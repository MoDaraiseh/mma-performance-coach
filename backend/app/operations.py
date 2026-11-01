"""Privacy-minimized shared counters and migration-aware readiness."""

import json
import os
import subprocess
import sys
import threading
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from .access import digest
from .db import OperatorCounter, RateBucket, Session, engine
from .monitoring import evaluate_alerts
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
        except HTTPException as exc:
            if exc.status_code == 429:
                increment("ai.quota_denied")
            raise
    raise HTTPException(503, "AI budget temporarily unavailable; use offline coaching")


def expected_head():
    cfg = Config()
    cfg.set_main_option("script_location", str(Path(__file__).resolve().parents[1] / "migrations"))
    return ScriptDirectory.from_config(cfg).get_current_head()


# One bounded child at a time per application process: no accumulating timeout threads.
PROBE_TIMEOUT_SECONDS = 3
_probe_condition = threading.Condition()
_probe_running = False
_probe_last = None


def _unavailable(reason):
    return {
        "database": {
            "ready": False,
            "migration_current": None,
            "migration_expected": expected_head(),
            "reason": reason,
        },
        "counters": {},
        "reservations": {},
        "metrics_available": False,
    }


def _bounded_probe(aggregate=False):
    global _probe_running, _probe_last
    with _probe_condition:
        if _probe_running:
            completed = _probe_condition.wait_for(
                lambda: not _probe_running, PROBE_TIMEOUT_SECONDS + 0.25
            )
            if not completed:
                return _unavailable("probe_busy")
            return deepcopy(_probe_last)
        _probe_running = True
    result = _unavailable("probe_failed")
    try:
        # Credentials stay in the child environment, never argv or error output.
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "app.health_probe",
                "aggregate" if aggregate else "readiness",
                expected_head(),
            ],
            cwd=Path(__file__).resolve().parents[1],
            env={**os.environ, "DATABASE_URL": engine.url.render_as_string(hide_password=False)},
            capture_output=True,
            timeout=PROBE_TIMEOUT_SECONDS,
        )
        if completed.returncode or len(completed.stdout) > 65536:
            result = _unavailable("probe_failed")
            return result
        result = json.loads(completed.stdout)
        if (
            not isinstance(result, dict)
            or not isinstance(result.get("database"), dict)
            or type(result["database"].get("ready")) is not bool
        ):
            result = _unavailable("probe_failed")
        return result
    except subprocess.TimeoutExpired:
        # subprocess.run kills and reaps the child; no hung pooled DB connection survives.
        result = _unavailable("probe_timeout")
        return result
    except (OSError, ValueError, TypeError):
        result = _unavailable("probe_failed")
        return result
    finally:
        with _probe_condition:
            _probe_last = result
            _probe_running = False
            _probe_condition.notify_all()


def readiness():
    return _bounded_probe()["database"]


def report():
    collected = _bounded_probe(aggregate=True)
    counts = collected["counters"]
    reservations = collected["reservations"]
    ceiling_input = 40000
    estimated = (
        2
        * (
            ceiling_input * settings.ai_input_usd_per_million
            + settings.ai_max_output_tokens * settings.ai_output_usd_per_million
        )
        / 1000000
    )
    snapshot = {
        "database": collected["database"],
        "metrics_available": collected["metrics_available"],
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "counters": counts,
        "latency_note": "Disjoint response-header latency buckets in milliseconds; excludes streaming body delivery. Lifetime counters, not windowed percentiles.",
        "identity_mode": settings.identity_mode,
        "ai": {
            "daily_outbound_ceiling": settings.ai_global_daily,
            "monthly_outbound_ceiling": settings.ai_global_monthly,
            "max_attempts": 2,
            "reserved_outbound_attempts": reservations,
            "metrics_available": collected["metrics_available"],
            "output_token_cap": settings.ai_max_output_tokens,
            "allowed_models": settings.ai_allowed_models.split(","),
            "configured_rate_reservation_estimate_usd": round(estimated, 6),
            "pricing_configured": settings.ai_input_usd_per_million > 0
            or settings.ai_output_usd_per_million > 0,
            "note": "Conservative two-attempt reservation, not measured billing. Provider dashboards must enforce independent spending limits.",
        },
    }
    snapshot["local_alerts"] = evaluate_alerts(snapshot)
    return snapshot


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
