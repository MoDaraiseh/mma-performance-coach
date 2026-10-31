"""Account-scoped atomic writes; no model or LLM has unrestricted write access."""

import uuid
from contextlib import contextmanager

from fastapi import HTTPException
from sqlalchemy import select, update

from .db import Record, Session, User


def latest_record(db, uid, kind):
    return db.scalar(
        select(Record)
        .where(Record.user_id == uid, Record.kind == kind)
        .order_by(Record.version.desc())
        .limit(1)
    )


def latest_checkin(db, uid):
    return db.scalar(
        select(Record)
        .where(Record.user_id == uid, Record.kind == "checkin")
        .order_by(Record.event_date.desc().nullslast(), Record.version.desc())
        .limit(1)
    )


def account_records(db, uid, kind):
    return list(
        db.scalars(
            select(Record)
            .where(Record.user_id == uid, Record.kind == kind)
            .order_by(Record.version)
        )
    )


def append_record(db, uid, kind, payload):
    prior = latest_record(db, uid, kind)
    row = Record(
        id=str(uuid.uuid4()),
        user_id=uid,
        kind=kind,
        version=prior.version + 1 if prior else 1,
        payload=payload,
    )
    db.add(row)
    db.flush()
    return row


@contextmanager
def account_write(uid):
    with Session.begin() as db:
        # First acquire a write lock on the account. This serializes reads/decisions/writes
        # in SQLite and takes a row lock on PostgreSQL, without in-process-only mutexes.
        result = db.execute(
            update(User).where(User.id == uid).values(write_revision=User.write_revision + 1)
        )
        if result.rowcount != 1:
            raise HTTPException(401, "Account no longer exists")
        yield db
