from .programs import TrainingPlanService
from .progression import recovery_state
from .schemas import Profile

TRAINING_FIELDS = (
    "age",
    "days",
    "available_days",
    "strength_coach",
    "power_practice",
    "minutes",
    "sleep",
    "recovery",
    "limitations",
    "gym",
    "mma_gym",
    "partners",
    "boxing_equipment",
    "gym_years",
    "current_frequency",
    "workout_minutes",
    "goal",
    "preferred",
    "experience",
    "priority",
    "intensity",
    "mobility",
    "equipment",
    "objectives",
    "conditioning_mode",
    "competitive",
)


def newest_checkin(rows):
    return max(rows, key=lambda r: (r.payload["date"], r.version)) if rows else None


def make_plan(profile_row, checkin=None, days=None):
    original = Profile.model_validate(profile_row.payload)
    values = original.model_dump()
    if days is not None:
        values["days"] = days
    if checkin:
        values["sleep"] = min(values["sleep"], checkin.payload["sleep"])
        if recovery_state(original, checkin.payload)["status"] == "reduce":
            values["recovery"] = values["recovery"] or "Recent check-in reports elevated fatigue."
    effective = Profile.model_validate(values)
    return {
        **TrainingPlanService.generate(effective),
        "profile_snapshot": original.model_dump(),
        "source_profile_id": profile_row.id,
        "source_checkin_id": checkin.id if checkin else None,
    }


def plan_status(row, profile_row, checkin):
    current = profile_row.payload
    original = row.payload.get("profile_snapshot", row.payload["inputs"])
    original = Profile.model_validate(original).model_dump()
    current = Profile.model_validate(current).model_dump()
    changed = [key for key in TRAINING_FIELDS if original.get(key) != current.get(key)]
    recovery = bool(
        checkin
        and checkin.id != row.payload.get("source_checkin_id")
        and recovery_state(Profile.model_validate(current), checkin.payload)["status"] == "reduce"
    )
    hold = bool(changed) or recovery or bool(current.get("limitations"))
    return {
        "profile_changed": bool(changed),
        "changed_fields": changed,
        "recovery_changed": recovery,
        "needs_review": hold,
        "reason": "Training inputs or recovery changed. Preview and approve a current-input revision before using this program."
        if hold
        else "Saved program matches current training inputs.",
    }
