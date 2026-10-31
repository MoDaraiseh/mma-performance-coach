"""Queryable metadata only; original aggregate payloads remain unchanged."""

from datetime import date, datetime, timezone


def metadata(row):
    when = (
        row.payload.get("date")
        if row.kind in {"checkin", "technical_achievement"}
        else row.payload.get("completed_on")
        if row.kind == "workout"
        else None
    )
    if row.kind == "workout" and not when:
        when = (row.created_at or datetime.now(timezone.utc)).date().isoformat()
    try:
        when = date.fromisoformat(when).isoformat() if when else None
    except (ValueError, TypeError):
        when = None
    parent = (
        row.payload.get("plan_id")
        if row.kind == "workout"
        else row.payload.get("lineage_id", row.id)
        if row.kind == "plan"
        else None
    )
    return {"event_date": when, "parent_ref": parent}
