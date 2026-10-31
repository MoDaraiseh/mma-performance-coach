"""Synthetic migration/backup/restore evidence; no normal athlete database access."""

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from contextlib import closing
from pathlib import Path

from sqlite_backup import backup

root = Path(__file__).resolve().parents[2]
runtime = root / ".qa-runtime"
runtime.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix="restore-check-", dir=runtime) as folder:
    source = Path(folder) / "source.db"
    env = {
        **os.environ,
        "DATABASE_URL": "sqlite:///" + str(source),
        "APP_ENV": "test",
        "IDENTITY_MODE": "local",
    }
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=root / "backend",
        env=env,
        check=True,
        capture_output=True,
    )
    with closing(sqlite3.connect(source)) as db, db:
        db.execute(
            "INSERT INTO users(id,token_hash,write_revision) VALUES ('synthetic','synthetic-hash',0)"
        )
        for version in (1, 2):
            db.execute(
                "INSERT INTO records(id,user_id,kind,version,payload,created_at) VALUES (?, 'synthetic','plan',?,?,CURRENT_TIMESTAMP)",
                (f"plan-{version}", version, json.dumps({"version": version, "synthetic": True})),
            )
        db.execute(
            "INSERT INTO login_sessions(token_hash,user_id,expires_at,label) VALUES ('synthetic-session','synthetic','2099-01-01','synthetic')"
        )
    fingerprint = hashlib.sha256(source.read_bytes()).hexdigest()
    archive = Path(folder) / "backup.db"
    backup_report = backup(source, archive)
    restored = Path(folder) / "mma_restore_verified.db"
    restore_report = backup(archive, restored, restore=True)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == fingerprint
    with closing(sqlite3.connect(restored)) as db:
        assert [
            json.loads(r[0])["version"]
            for r in db.execute("SELECT payload FROM records ORDER BY version")
        ] == [1, 2]
        assert db.execute("SELECT count(*) FROM login_sessions").fetchone()[0] == 0
    result = {
        "fixture": "One synthetic user, two versioned plans, one session; no athlete data",
        "backup": backup_report,
        "restore": restore_report,
        "source_unchanged": True,
        "plan_payloads_preserved": True,
        "sessions_invalidated": True,
    }
    phase = os.getenv("MMA_QA_PHASE", "phase13")
    if phase not in {"phase13", "phase14", "phase16"}:
        raise ValueError("Unsupported evidence phase")
    output = root / f"docs/evidence/{phase}/backup-restore.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
