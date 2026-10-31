"""Privacy-minimized shared counters and migration-aware readiness."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import HTTPException
from sqlalchemy import select, text, update
from sqlalchemy.exc import IntegrityError

from .access import digest
from .db import OperatorCounter, RateBucket, Session, engine
from .settings import settings


def increment(key):
    increment_many([key])


def record_http(status, duration_ms):
    bucket = next((n for n in (100, 500, 1000, 5000) if duration_ms <= n), "inf")
    keys = ["http.total", f"http.latency_ms.le_{bucket}"]
    if status >= 400:
        keys.append("http." + str(status))
    increment_many(keys)


def increment_many(keys):
    for _ in range(2):
        try:
            with Session.begin() as db:
                for key in keys:
                    result = db.execute(
                        update(OperatorCounter)
                        .where(OperatorCounter.key == key)
                        .values(count=OperatorCounter.count + 1)
                    )
                    if not result.rowcount:
                        db.add(OperatorCounter(key=key, count=1))
            return
        except IntegrityError:
            continue


def reserve_ai(now=None):
    # Reserve two possible outbound attempts per logical request, including retries/failures.
    # Never refund: this favors a hard conservative ceiling over best-effort capacity.
    now = now or datetime.now(timezone.utc)
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    next_month = (now.replace(day=28) + timedelta(days=4)).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    budgets = [
        ("day:" + now.date().isoformat(), settings.ai_global_daily, tomorrow),
        ("month:" + now.strftime("%Y-%m"), settings.ai_global_monthly, next_month),
    ]
    for _ in range(3):
        try:
            with Session.begin() as db:
                for period, limit, expiry in budgets:
                    key = digest("operator-ai:" + period)
                    result = db.execute(
                        update(RateBucket)
                        .where(RateBucket.key == key, RateBucket.count <= limit - 2)
                        .values(count=RateBucket.count + 2)
                    )
                    if not result.rowcount:
                        if limit < 2 or db.get(RateBucket, key):
                            raise HTTPException(
                                429,
                                "Operator AI budget exhausted; offline coaching remains available",
                                headers={
                                    "Retry-After": str(max(1, int((expiry - now).total_seconds())))
                                },
                            )
                        db.add(RateBucket(key=key, count=2, expires_at=expiry))
                        db.flush()
            return
        except IntegrityError:
            continue
    raise HTTPException(503, "AI budget temporarily unavailable; use offline coaching")


def expected_head():
    cfg = Config()
    cfg.set_main_option("script_location", str(Path(__file__).resolve().parents[1] / "migrations"))
    return ScriptDirectory.from_config(cfg).get_current_head()


def readiness():
    with engine.connect() as db:
        current = db.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        db.execute(text("SELECT 1"))
    return {
        "ready": current == expected_head(),
        "migration_current": current,
        "migration_expected": expected_head(),
    }


def report():
    with Session() as db:
        counts = dict(db.execute(select(OperatorCounter.key, OperatorCounter.count)).all())
        now = datetime.now(timezone.utc)
        reservations = {}
        for period in ("day:" + now.date().isoformat(), "month:" + now.strftime("%Y-%m")):
            row = db.get(RateBucket, digest("operator-ai:" + period))
            reservations[period] = row.count if row else 0
    ceiling_input = 40000
    estimated = (
        2
        * (
            ceiling_input * settings.ai_input_usd_per_million
            + settings.ai_max_output_tokens * settings.ai_output_usd_per_million
        )
        / 1000000
    )
    return {
        "database": readiness(),
        "counters": counts,
        "latency_note": "Disjoint response-header latency buckets in milliseconds; excludes streaming body delivery. Lifetime counters, not windowed percentiles.",
        "identity_mode": settings.identity_mode,
        "ai": {
            "daily_outbound_ceiling": settings.ai_global_daily,
            "monthly_outbound_ceiling": settings.ai_global_monthly,
            "max_attempts": 2,
            "reserved_outbound_attempts": reservations,
            "output_token_cap": settings.ai_max_output_tokens,
            "allowed_models": settings.ai_allowed_models.split(","),
            "configured_rate_reservation_estimate_usd": round(estimated, 6),
            "pricing_configured": settings.ai_input_usd_per_million > 0
            or settings.ai_output_usd_per_million > 0,
            "note": "Conservative two-attempt reservation, not measured billing. Provider dashboards must enforce independent spending limits.",
        },
    }


if __name__ == "__main__":
    import json

    print(json.dumps(report(), indent=2))
