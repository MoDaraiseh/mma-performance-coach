import hashlib
import json

from sqlalchemy import select

from .db import FighterDataRevision, FighterSnapshot, ReferenceSnapshot, Session
from .divisions import DivisionReference, bundled_reference


def fingerprint(entity, payload):
    return hashlib.sha256(
        (entity + json.dumps(payload, sort_keys=True, separators=(",", ":"))).encode()
    ).hexdigest()


def refresh(provider, refresh_reference=False):
    """Validate entire export before a single atomic write; archive old and new.

    Same-date corrections are allowed; older observations and provider takeover
    are rejected. Removing a record from an export never deletes stored history.
    """
    from .fighter_index import name_key
    from .fighters import validated

    fighters = [validated(r) for r in provider.all()]
    if len({r["id"] for r in fighters}) != len(fighters) or len(
        {(name_key(r["name"]), r["competition_division"]) for r in fighters}
    ) != len(fighters):
        raise ValueError("Duplicate fighter IDs or normalized identities")
    changes = 0
    with Session.begin() as db:
        if db.bind.dialect.name == "sqlite":
            # Acquire the writer lock before reading dates/hashes, preventing a
            # concurrent refresh from committing between validation and update.
            db.connection().exec_driver_sql("BEGIN IMMEDIATE")

        def archive(entity, payload):
            digest = fingerprint(entity, payload)
            if not db.get(FighterDataRevision, digest):
                db.add(FighterDataRevision(id=digest, entity=entity, payload=payload))

        for f in fighters:
            old = db.get(FighterSnapshot, f["id"], with_for_update=True)
            if old:
                if old.verified_at > f["verified_at"]:
                    raise ValueError("Refresh would replace a newer observation")
                if old.payload.get("provider_id", "reviewed-local") != f["provider_id"]:
                    raise ValueError("Provider identity collision; use distinct fighter IDs")
                archive("fighter:" + f["id"], old.payload)
                if old.payload != f:
                    old.payload, old.verified_at = f, f["verified_at"]
                    changes += 1
            else:
                db.add(FighterSnapshot(id=f["id"], payload=f, verified_at=f["verified_at"]))
                changes += 1
            archive("fighter:" + f["id"], f)
        if refresh_reference:
            for category in ("Men", "Women"):
                payload = DivisionReference.model_validate(bundled_reference(category)).model_dump(
                    exclude_none=True
                )
                old = db.get(ReferenceSnapshot, category, with_for_update=True)
                if old:
                    if old.payload["verified_at"] > payload["verified_at"]:
                        raise ValueError("Reference refresh would replace a newer observation")
                    archive("reference:" + category, old.payload)
                    if old.payload != payload:
                        old.payload = payload
                        changes += 1
                else:
                    db.add(ReferenceSnapshot(id=category, payload=payload))
                    changes += 1
                archive("reference:" + category, payload)
    return {
        "changed": changes,
        "reviewed": len(fighters),
        "message": "Reviewed snapshots reimported. Verification dates have not been advanced; no website was fetched.",
    }


def revisions():
    with Session() as db:
        return [
            {
                "digest": r.id,
                "entity": r.entity,
                "payload": r.payload,
                "archived_at": r.archived_at.isoformat(),
            }
            for r in db.scalars(
                select(FighterDataRevision).order_by(
                    FighterDataRevision.entity,
                    FighterDataRevision.archived_at,
                    FighterDataRevision.id,
                )
            )
        ]
