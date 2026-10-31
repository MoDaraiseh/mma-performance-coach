"""Operator-only, offline imports with explicit conflict review and guarded rollback."""

import json
import uuid
from collections import Counter
from datetime import date

from sqlalchemy import select

from .db import FighterImportBatch, FighterSnapshot, Session
from .fighter_index import name_key
from .fighter_refresh import fingerprint
from .fighters import validated


def quality(records):
    fields = [
        "height_cm",
        "reach_cm",
        "listed_weight_kg",
        "stance",
        "background",
        "current_division",
        "record",
        "statistics",
    ]
    history = Counter(
        (r["competition_division"], d["name"]) for r in records for d in r["division_history"]
    )
    return {
        "validated_count": len(records),
        "categories": dict(Counter(r["competition_division"] for r in records)),
        "history_divisions": [
            {"category": c, "division": d, "fighters": n} for (c, d), n in sorted(history.items())
        ],
        "current_divisions": [
            {"category": c, "division": d, "fighters": n}
            for (c, d), n in sorted(
                Counter(
                    (r["competition_division"], r["current_division"])
                    for r in records
                    if r["current_division"]
                ).items()
            )
        ],
        "supported_fields": {f: sum(bool(r.get(f)) for r in records) for f in fields},
        "statuses": dict(Counter(r["career_status"] for r in records)),
        "stale_count": sum(
            (date.today() - date.fromisoformat(r["verified_at"])).days > 365 for r in records
        ),
        "unestablished_rights": sum(
            any(s["rights"] == "not_established" for s in r["sources"]) for r in records
        ),
        "note": "Historical division counts overlap; verification is source-snapshot review, not independent athlete measurement. No comprehensive roster claim.",
    }


def preview(items, db):
    if not isinstance(items, list) or not 1 <= len(items) <= 10000:
        raise ValueError("Provide 1–10000 records")
    records = [validated(r) for r in items]
    keys = [(name_key(r["name"]), r["competition_division"]) for r in records]
    if len({r["id"] for r in records}) != len(records) or len(set(keys)) != len(keys):
        raise ValueError("Duplicate fighter ID or normalized identity in import")
    existing = list(db.scalars(select(FighterSnapshot).with_for_update()))
    by_id = {r.id: r for r in existing}
    identities = {
        (name_key(r.payload.get("name", "")), r.payload.get("competition_division")): r.id
        for r in existing
    }
    changes = []
    external = {
        (key, value): r.id
        for r in existing
        for key, value in r.payload.get("external_ids", {}).items()
    }
    for f, key in zip(records, keys):
        for namespace, value in f["external_ids"].items():
            identity = (namespace, value)
            if identity in external and external[identity] != f["id"]:
                raise ValueError(
                    "Duplicate external identifier; reconcile the canonical fighter ID"
                )
            external[identity] = f["id"]
        if any(s["rights"] != "licensed" or not s["license_reference"] for s in f["sources"]):
            raise ValueError(
                "Operator imports require explicit reuse/license references on every source"
            )
        if key in identities and identities[key] != f["id"]:
            raise ValueError(
                "Existing identity under another ID; reconcile explicitly before import"
            )
        old = by_id.get(f["id"])
        if old and old.payload.get("provider_id") != f["provider_id"]:
            raise ValueError("Provider takeover rejected; review identity/source reconciliation")
        if old and old.verified_at > f["verified_at"]:
            raise ValueError("Older source snapshot cannot replace newer data")
        if old and old.payload == f:
            continue
        differences = [k for k in f if old and old.payload.get(k) != f[k]]
        changes.append(
            {
                "id": f["id"],
                "before": old.payload if old else None,
                "after": f,
                "changed_fields": differences,
            }
        )
    token = fingerprint("import-preview", changes)
    return {
        "preview_token": token,
        "changes": changes,
        "conflicts": sum(c["before"] is not None for c in changes),
        "quality": quality(records),
    }


def import_records(items, expected_token=None, accept_conflicts=False):
    with Session.begin() as db:
        if db.bind.dialect.name == "sqlite":
            db.connection().exec_driver_sql("BEGIN IMMEDIATE")
        report = preview(items, db)
        if expected_token is None:
            return report
        if expected_token != report["preview_token"]:
            raise ValueError("Preview changed; review again")
        if report["conflicts"] and not accept_conflicts:
            raise ValueError(
                "Conflicts require explicit operator acceptance after reviewing changed fields"
            )
        batch_id = uuid.uuid4().hex
        for c in report["changes"]:
            row = db.get(FighterSnapshot, c["id"])
            if row:
                row.payload = c["after"]
                row.verified_at = c["after"]["verified_at"]
            else:
                db.add(
                    FighterSnapshot(
                        id=c["id"], payload=c["after"], verified_at=c["after"]["verified_at"]
                    )
                )
        db.add(FighterImportBatch(id=batch_id, payload={"status": "applied", "report": report}))
    return {"batch_id": batch_id, "changed": len(report["changes"]), "status": "applied"}


def rollback(batch_id, apply=False):
    with Session.begin() as db:
        if db.bind.dialect.name == "sqlite":
            db.connection().exec_driver_sql("BEGIN IMMEDIATE")
        batch = db.get(FighterImportBatch, batch_id, with_for_update=True)
        if not batch or batch.payload["status"] != "applied":
            raise ValueError("Unknown or resolved import")
        for c in batch.payload["report"]["changes"]:
            row = db.get(FighterSnapshot, c["id"], with_for_update=True)
            if not row or row.payload != c["after"]:
                raise ValueError("Later changes prevent rollback; review a new reconciliation")
        if apply:
            for c in batch.payload["report"]["changes"]:
                row = db.get(FighterSnapshot, c["id"])
                if c["before"] is None:
                    db.delete(row)
                else:
                    row.payload = c["before"]
                    row.verified_at = c["before"]["verified_at"]
            batch.payload = {**batch.payload, "status": "rolled_back"}
        return {
            "batch_id": batch_id,
            "status": "rolled_back" if apply else "rollback_preview",
            "changed": len(batch.payload["report"]["changes"]),
        }


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("file", nargs="?")
    p.add_argument("--apply-token")
    p.add_argument("--accept-conflicts", action="store_true")
    p.add_argument("--rollback")
    p.add_argument("--apply-rollback", action="store_true")
    args = p.parse_args()
    if args.rollback:
        result = rollback(args.rollback, args.apply_rollback)
    else:
        path = Path(args.file)
        if path.stat().st_size > 25_000_000:
            raise ValueError("Import exceeds 25 MB")
        result = import_records(
            json.loads(path.read_text(encoding="utf-8")), args.apply_token, args.accept_conflicts
        )
    print(json.dumps(result, indent=2))
