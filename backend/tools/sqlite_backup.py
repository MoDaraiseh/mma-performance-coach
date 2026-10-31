"""Online SQLite backup and disposable-only restore; never overwrite a destination."""

import argparse
import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


def validate(path):
    with closing(sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)) as db:
        if (
            db.execute("PRAGMA integrity_check").fetchone()[0] != "ok"
            or db.execute("PRAGMA foreign_key_check").fetchall()
        ):
            raise ValueError("Database integrity validation failed")
        names = [
            r[0]
            for r in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        ]
        counts = {
            name: db.execute('SELECT count(*) FROM "' + name.replace('"', '""') + '"').fetchone()[0]
            for name in names
        }
        version = db.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    return {"migration": version, "counts": counts}


def backup(source, destination, restore=False):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if destination.exists() or source == destination:
        raise ValueError("Destination must be a new file; overwrite is forbidden")
    if restore and not destination.name.startswith("mma_restore_"):
        raise ValueError("Restore tests require an explicitly disposable mma_restore_ destination")
    before = validate(source)
    if restore:
        manifest = source.with_suffix(source.suffix + ".manifest.json")
        if (
            not manifest.exists()
            or json.loads(manifest.read_text(encoding="utf-8")).get("sha256")
            != hashlib.sha256(source.read_bytes()).hexdigest()
        ):
            raise ValueError("Backup manifest missing or checksum mismatch")
    # Exclusive creation prevents races replacing a preexisting database.
    with destination.open("xb"):
        pass
    with (
        closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as src,
        closing(sqlite3.connect(destination)) as dst,
    ):
        src.backup(dst)
    after = validate(destination)
    if before != after:
        raise ValueError("Source changed during backup; retry during a controlled quiet window")
    if restore:
        # A rehearsal must not resurrect active sessions or unfinished sign-in flows.
        with closing(sqlite3.connect(destination)) as db, db:
            db.execute("DELETE FROM login_sessions")
            db.execute("DELETE FROM oidc_flows")
        after = validate(destination)
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "restore_rehearsal": restore,
        **after,
        "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        "note": "Sensitive backup: operator must encrypt, restrict access, set retention and reconcile account deletions before any recovery goes online.",
    }
    destination.with_suffix(destination.suffix + ".manifest.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("--restore-rehearsal", action="store_true")
    args = parser.parse_args()
    print(json.dumps(backup(args.source, args.destination, args.restore_rehearsal), indent=2))
