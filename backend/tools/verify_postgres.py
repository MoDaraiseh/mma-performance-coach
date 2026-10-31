"""Opt-in real PostgreSQL migration/transaction/API verification in a throwaway schema.

Requires MMA_TEST_DATABASE_URL naming an mma_test database. Never uses DATABASE_URL.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


def probe():
    # --probe is an internal child mode, not a shortcut around the disposable URL guard.
    url = make_url(os.environ.get("DATABASE_URL", "sqlite://"))
    schema = os.environ.get("MMA_TEST_SCHEMA", "")
    if (
        url.drivername != "postgresql+psycopg"
        or not (url.database or "").startswith("mma_test")
        or not re.fullmatch(r"qa_[0-9a-f]{32}", schema)
        or url.query.get("options") != "-csearch_path=" + schema
    ):
        raise ValueError(
            "Internal probe requires the generated disposable mma_test schema; normal DATABASE_URL is never accepted"
        )
    from concurrent.futures import ThreadPoolExecutor

    from fastapi.testclient import TestClient
    from sqlalchemy import select
    from sqlalchemy.exc import IntegrityError

    from app.db import Record, Session, User, engine
    from app.main import app
    from app.repository import account_write, append_record

    with TestClient(app) as client:
        recovery = client.post("/api/auth/register").json()["recovery_token"]
        assert client.post("/api/demo").status_code == 200
        with Session() as db:
            uid = db.scalar(select(User.id))
        try:
            with account_write(uid) as db:
                append_record(db, uid, "rollback_probe", {})
                raise ValueError("rollback")
        except ValueError:
            pass
        with Session() as db:
            assert not db.scalar(select(Record).where(Record.kind == "rollback_probe"))

        def write(_):
            with account_write(uid) as db:
                return append_record(db, uid, "concurrency_probe", {}).version

        with ThreadPoolExecutor(max_workers=4) as pool:
            assert sorted(pool.map(write, range(8))) == list(range(1, 9))
        try:
            with Session.begin() as db:
                db.add(
                    Record(id="orphan", user_id="missing", kind="profile", version=1, payload={})
                )
            raise AssertionError("Foreign key not enforced")
        except IntegrityError:
            pass
        assert len(client.get("/api/export").json()["records"]) > 8
        assert client.get("/api/nutrition").json()["data"]["available"]
        active = client.get("/api/training-plans").json()
        other = TestClient(app)
        with other:
            other.post("/api/auth/register")
            assert other.post(
                "/api/training-sessions",
                json={
                    "plan_id": active["id"],
                    "session_id": active["data"]["weeks"][0]["sessions"][0]["id"],
                    "minutes": 20,
                    "effort": 3,
                },
            ).status_code in (404, 409)
            assert other.get("/api/profile").status_code == 404
            other.delete("/api/account")
        assert client.get("/api/training-plans/history").json()[0]["id"] == active["id"]
        proposal = client.post(
            "/api/revisions",
            json={"days": 2, "reason": "Disposable PostgreSQL versioning verification"},
        )
        assert proposal.status_code == 200, proposal.text
        proposed_id = proposal.json()["id"]
        assert client.post(f"/api/revisions/{proposed_id}/approve").status_code == 200
        history = client.get("/api/training-plans/history").json()
        assert len(history) == 2 and any(r["id"] == active["id"] for r in history)
        assert client.delete("/api/account").status_code == 200
        assert client.post("/api/auth/restore", json={"token": recovery}).status_code == 401
    engine.dispose()
    print("PostgreSQL API, FK, rollback, concurrency, versioning, export and deletion passed")


def run():
    url = make_url(os.environ["MMA_TEST_DATABASE_URL"])
    if url.drivername != "postgresql+psycopg" or not (url.database or "").startswith("mma_test"):
        raise ValueError("Use postgresql+psycopg and an explicitly disposable mma_test database")
    schema = "qa_" + uuid.uuid4().hex
    engine = create_engine(url, hide_parameters=True)
    backend = Path(__file__).resolve().parents[1]
    with engine.begin() as db:
        db.execute(text(f'CREATE SCHEMA "{schema}"'))
    env = {
        **os.environ,
        "DATABASE_URL": url.update_query_dict(
            {"options": f"-csearch_path={schema}"}
        ).render_as_string(hide_password=False),
        "APP_ENV": "test",
        "COOKIE_SECURE": "false",
        "OPENAI_API_KEY": "",
        "API_PER_MINUTE": "100000",
        "AUTH_PER_MINUTE": "1000",
        "IDENTITY_MODE": "local",
        "MMA_TEST_SCHEMA": schema,
    }
    try:
        for command in [
            ["-m", "alembic", "upgrade", "head"],
            ["-m", "alembic", "check"],
            [str(Path(__file__).resolve()), "--probe"],
        ]:
            subprocess.run([sys.executable, *command], cwd=backend, env=env, check=True)
        if os.getenv("MMA_TEST_RESTORE") == "1":
            if not shutil.which("pg_dump") or not shutil.which("pg_restore"):
                raise RuntimeError(
                    "Restore gate requested but native pg_dump/pg_restore are unavailable"
                )
            pg_env = {
                **env,
                "PGHOST": url.host or "localhost",
                "PGPORT": str(url.port or 5432),
                "PGUSER": url.username or "",
                "PGPASSWORD": url.password or "",
                "PGDATABASE": url.database,
            }
            with tempfile.TemporaryDirectory(prefix="mma-pg-restore-") as folder:
                archive = str(Path(folder) / "qa.dump")
                with engine.begin() as db:
                    db.execute(
                        text(
                            f'INSERT INTO "{schema}".users (id,token_hash,write_revision) VALUES (:id,:hash,0)'
                        ),
                        {"id": str(uuid.uuid4()), "hash": "synthetic-restore-marker"},
                    )
                    names = list(
                        db.execute(
                            text(
                                "SELECT table_name FROM information_schema.tables WHERE table_schema=:schema"
                            ),
                            {"schema": schema},
                        ).scalars()
                    )
                    counts = {
                        name: db.execute(
                            text(f'SELECT count(*) FROM "{schema}"."{name}"')
                        ).scalar_one()
                        for name in names
                    }
                subprocess.run(
                    ["pg_dump", "--format=custom", "--schema=" + schema, "--file=" + archive],
                    env=pg_env,
                    check=True,
                )
                with engine.begin() as db:
                    before = db.execute(
                        text(f'SELECT version_num FROM "{schema}".alembic_version')
                    ).scalar_one()
                    # Only the randomly generated disposable schema is replaced.
                    db.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
                subprocess.run(
                    [
                        "pg_restore",
                        "--exit-on-error",
                        "--no-owner",
                        "--no-privileges",
                        "--dbname=" + url.database,
                        archive,
                    ],
                    env=pg_env,
                    check=True,
                )
                with engine.connect() as db:
                    assert (
                        db.execute(
                            text(f'SELECT version_num FROM "{schema}".alembic_version')
                        ).scalar_one()
                        == before
                    )
                    assert all(
                        db.execute(text(f'SELECT count(*) FROM "{schema}"."{name}"')).scalar_one()
                        == count
                        for name, count in counts.items()
                    )
                print("Disposable PostgreSQL native archive restore and table counts passed")
        for command in [
            ["-m", "alembic", "downgrade", "base"],
            ["-m", "alembic", "upgrade", "head"],
        ]:
            subprocess.run([sys.executable, *command], cwd=backend, env=env, check=True)
    finally:
        # Only this generated, hex-named schema is removed, never the database/public schema.
        with engine.begin() as db:
            db.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        engine.dispose()


if __name__ == "__main__":
    if "--probe" in sys.argv:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        probe()
    else:
        run()
