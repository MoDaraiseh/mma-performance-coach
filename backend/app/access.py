"""Opaque random sessions and database-backed fixed-window quotas."""

import hashlib
import secrets
import time
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from .db import LoginSession, RateBucket, Session
from .settings import settings


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def issue_session(db, uid, label="Local recovery session"):
    token = secrets.token_urlsafe(48)
    db.add(
        LoginSession(
            token_hash=digest(token),
            user_id=uid,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=settings.session_hours),
            label=label,
        )
    )
    return token


def quota(subject, scope, limit, seconds=60):
    now = int(time.time())
    window = now // seconds
    key = digest(f"{scope}:{subject}:{window}")
    expiry = datetime.fromtimestamp((window + 1) * seconds, timezone.utc)
    # A conditional UPDATE is atomic across workers; an insert collision retries once.
    for _ in range(2):
        try:
            with Session.begin() as db:
                changed = db.execute(
                    update(RateBucket)
                    .where(RateBucket.key == key, RateBucket.count < limit)
                    .values(count=RateBucket.count + 1)
                )
                if changed.rowcount:
                    return
                if db.get(RateBucket, key):
                    raise HTTPException(
                        429,
                        "Request limit reached. Please retry later.",
                        headers={"Retry-After": str((window + 1) * seconds - now)},
                    )
                db.add(RateBucket(key=key, count=1, expires_at=expiry))
            return
        except IntegrityError:
            continue
    raise HTTPException(503, "Request quota temporarily unavailable. Please retry.")
