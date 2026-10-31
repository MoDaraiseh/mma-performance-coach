"""Migration round trip preserves an account created before serialized writes."""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path


def test_serialized_write_migration_round_trip(tmp_path):
    path = tmp_path / "migration.db"
    env = {**os.environ, "DATABASE_URL": "sqlite:///" + str(path)}

    def migrate(*args):
        subprocess.run(
            [sys.executable, "-m", "alembic", *args],
            cwd=Path(__file__).resolve().parents[1],
            env=env,
            check=True,
            capture_output=True,
        )

    migrate("upgrade", "0002")
    with sqlite3.connect(path) as db:
        db.execute("INSERT INTO users(id, token_hash) VALUES (?, ?)", ("existing", "hash"))
    migrate("upgrade", "head")
    migrate("check")
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT write_revision FROM users WHERE id='existing'").fetchone() == (0,)
    migrate("downgrade", "0002")
    migrate("upgrade", "head")
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT token_hash FROM users WHERE id='existing'").fetchone() == (
            "hash",
        )


def test_postgres_offline_migration_sql_compiles_without_connecting():
    env = {
        **os.environ,
        "DATABASE_URL": "postgresql+psycopg://unused:unused@127.0.0.1:1/mma_test_offline",
    }
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "CREATE TABLE login_sessions" in result.stdout
    assert "CREATE TABLE rate_buckets" in result.stdout
    assert "FOREIGN KEY(user_id) REFERENCES users" in result.stdout
    assert "CREATE UNIQUE INDEX uq_record_version" in result.stdout
