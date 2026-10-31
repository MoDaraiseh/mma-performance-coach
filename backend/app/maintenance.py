"""Explicit retention job; plan, profile and performance history are never aged out."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select

from .db import LoginSession, OIDCFlow, RateBucket, Record, Session
from .settings import settings


def retention(apply=False, now=None):
    now = now or datetime.now(timezone.utc)
    rules = [
        (LoginSession, LoginSession.expires_at < now),
        (RateBucket, RateBucket.expires_at < now),
        (
            Record,
            (Record.kind == "conversation")
            & (Record.created_at < now - timedelta(days=settings.conversation_retention_days)),
        ),
        (
            Record,
            (Record.kind == "draft")
            & (Record.created_at < now - timedelta(days=settings.draft_retention_days)),
        ),
        (OIDCFlow, OIDCFlow.expires_at < now),
    ]
    counts = {}
    with Session.begin() as db:
        for index, (model, condition) in enumerate(rules):
            counts[str(index)] = db.scalar(select(func.count()).select_from(model).where(condition))
            if apply:
                db.execute(delete(model).where(condition))
    result = {
        "applied": apply,
        "counts": counts,
        "order": [
            "expired_sessions",
            "expired_quotas",
            "old_conversations",
            "old_drafts",
            "expired_identity_flows",
        ],
        "protected": [
            "profiles",
            "approved/historical plans",
            "nutrition",
            "workouts",
            "check-ins",
            "proposals",
            "external identity bindings",
        ],
    }
    import json
    import logging

    logging.getLogger("mma.retention").info(json.dumps({"event": "retention", **result}))
    return result


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="Delete eligible records; default is dry run"
    )
    parser.add_argument(
        "--scheduled",
        action="store_true",
        help="Requires explicit RETENTION_ENABLED for scheduled destructive runs",
    )
    args = parser.parse_args()
    if args.scheduled and args.apply and not settings.retention_enabled:
        parser.error(
            "Scheduled deletion is disabled; operator must approve and configure RETENTION_ENABLED"
        )
    print(json.dumps(retention(args.apply)))
