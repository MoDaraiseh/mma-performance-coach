"""Small child-only DB probe: no application/provider imports or private error output."""

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool


def probe(url, expected, aggregate=False):
    result = {
        "database": {
            "ready": False,
            "migration_current": None,
            "migration_expected": expected,
            "reason": "database_unavailable",
        },
        "counters": {},
        "reservations": {},
        "metrics_available": False,
    }
    parsed = make_url(url)
    if parsed.drivername.startswith("postgresql"):
        args = {
            "connect_timeout": 1,
            "options": parsed.query.get("options", "") + " -c statement_timeout=1000",
        }
    else:
        args = {"timeout": 1}
    engine = create_engine(parsed, connect_args=args, poolclass=NullPool, hide_parameters=True)
    try:
        with engine.connect() as db:
            current = db.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
            db.execute(text("SELECT 1"))
            result["database"].update(
                ready=current == expected,
                migration_current=current,
                reason="ready" if current == expected else "migration_mismatch",
            )
            if aggregate and current == expected:
                rows = db.execute(text("SELECT key,count FROM operator_counters LIMIT 257")).all()
                if len(rows) > 256:
                    return result
                result["counters"] = {
                    key: count
                    for key, count in rows
                    if re.fullmatch(r"(?:http|auth|ai)\.[a-z0-9_.]+", key)
                    and type(count) is int
                    and count >= 0
                }
                now = datetime.now(timezone.utc)
                for period in ("day:" + now.date().isoformat(), "month:" + now.strftime("%Y-%m")):
                    key = hashlib.sha256(("operator-ai:" + period).encode()).hexdigest()
                    count = db.execute(
                        text("SELECT count FROM rate_buckets WHERE key=:key"), {"key": key}
                    ).scalar()
                    if count is not None:
                        result["reservations"][period] = count
                result["metrics_available"] = True
    except SQLAlchemyError:
        result["database"]["ready"] = False
        result["database"]["reason"] = "database_unavailable"
        result["counters"] = {}
        result["reservations"] = {}
        result["metrics_available"] = False
    finally:
        engine.dispose()
    return result


if __name__ == "__main__":
    print(json.dumps(probe(os.environ["DATABASE_URL"], sys.argv[2], sys.argv[1] == "aggregate")))
