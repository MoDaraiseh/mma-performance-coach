"""Read-only production gates; operator acknowledgements are not legal approval."""

from sqlalchemy import exists, func, select

from .db import ExternalIdentity, FighterSnapshot, User
from .fighters import validated


def inspect_release(db, settings):
    linked = exists().where(
        ExternalIdentity.user_id == User.id,
        ExternalIdentity.issuer == settings.oidc_issuer,
    )
    unlinked = db.scalar(select(func.count()).select_from(User).where(~linked))
    blocked_fighters = 0
    total = 0
    for payload in db.scalars(select(FighterSnapshot.payload)):
        total += 1
        try:
            fighter = validated(payload)
            if any(
                s["rights"] != "licensed" or not s.get("license_reference")
                for s in fighter["sources"]
            ):
                blocked_fighters += 1
        except ValueError:
            blocked_fighters += 1
    blockers = []
    if settings.allow_legacy_recovery:
        blockers.append("Legacy recovery bypasses managed-provider MFA")
    if not settings.identity_cutover_acknowledged:
        blockers.append("Identity cutover requires explicit operator acknowledgement")
    if unlinked:
        blockers.append("Existing accounts require linking to the configured issuer before cutover")
    if not settings.fighter_distribution_reviewed or blocked_fighters:
        blockers.append(
            "Fighter distribution rights require operator review and licensed provenance"
        )
    return {
        "ready": not blockers,
        "unlinked_accounts": unlinked,
        "fighter_records": total,
        "fighter_records_blocking_distribution": blocked_fighters,
        "blockers": blockers,
        "note": "Configuration checks only; independent identity, legal and security review remain required.",
    }


def require_release(db, settings):
    result = inspect_release(db, settings)
    if not result["ready"]:
        raise RuntimeError("Production release policy blocked: " + "; ".join(result["blockers"]))
