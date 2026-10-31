from datetime import date, timedelta
from statistics import median

from .ingredients import VERSION
from .nutrition import GENERAL, NutritionPlanService, substitute
from .nutrition_models import NutritionPreferences
from .repository import account_records, latest_record
from .schemas import Profile

FIELDS = (
    "age",
    "metabolic_sex",
    "height_cm",
    "weight_kg",
    "body_fat",
    "clinical_nutrition",
    "diet",
    "allergies",
    "activity",
    "budget",
    "food_preferences",
    "goal",
    "objectives",
    "days",
    "minutes",
    "competitive",
    "sleep",
    "recovery",
)


def training_signature(plan):
    return (
        [
            [[s["day"], s["minutes"], s.get("type")] for s in w["sessions"]]
            for w in plan.payload.get("weeks", [])
        ]
        if plan
        else []
    )


def weight_review(profile, checks, baseline=None):
    recent = sorted(
        [
            r.payload
            for r in checks
            if date.fromisoformat(r.payload["date"]) >= date.today() - timedelta(days=28)
        ],
        key=lambda r: r["date"],
    )[-3:]
    base = baseline or profile.weight_kg
    if (
        len(recent) < 3
        or (date.fromisoformat(recent[-1]["date"]) - date.fromisoformat(recent[0]["date"])).days
        < 14
    ):
        return {
            "needs_review": False,
            "reason": "Three recent check-ins spanning at least 14 days are needed; isolated fluctuations do not replan.",
        }
    values = [r["weight_kg"] for r in recent]
    sustained = all(v >= base * 1.02 for v in values) or all(v <= base * 0.98 for v in values)
    return {
        "needs_review": sustained,
        "weight_kg": median(values) if sustained else base,
        "checkin_dates": [r["date"] for r in recent],
        "reason": "Sustained ≥2% directional change over three recent measurements spanning ≥14 days; review, do not automatically replan."
        if sustained
        else "No sustained threshold met; retain existing targets.",
    }


def context_rows(db, uid):
    return {
        "profile": latest_record(db, uid, "profile"),
        "training": latest_record(db, uid, "plan"),
        "nutrition": latest_record(db, uid, "nutrition"),
        "preferences": latest_record(db, uid, "nutrition_preferences"),
        "checks": account_records(db, uid, "checkin"),
    }


def preferences(ctx):
    return (
        NutritionPreferences.model_validate(ctx["preferences"].payload)
        if ctx["preferences"]
        else NutritionPreferences()
    )


def build(ctx):
    if not ctx["profile"]:
        raise ValueError("Save a profile first")
    original = Profile.model_validate(ctx["profile"].payload)
    effective = original.model_copy(deep=True)
    review = weight_review(original, ctx["checks"])
    if review["needs_review"]:
        effective.weight_kg = review["weight_kg"]
    result = NutritionPlanService.generate(
        effective, preferences(ctx), ctx["training"].payload if ctx["training"] else None
    )
    return {
        **result,
        "profile_snapshot": original.model_dump(),
        "source_profile_id": ctx["profile"].id,
        "source_training_id": ctx["training"].id if ctx["training"] else None,
        "source_training_signature": training_signature(ctx["training"]),
        "source_preferences_id": ctx["preferences"].id if ctx["preferences"] else None,
        "weight_review": review,
        "effective_weight_kg": effective.weight_kg,
    }


def status(ctx):
    row = ctx["nutrition"]
    if not row:
        return {"needs_review": True, "reason": "No saved nutrition plan"}
    p = Profile.model_validate(ctx["profile"].payload)
    old = Profile.model_validate(
        row.payload.get("profile_snapshot", row.payload.get("inputs", {}))
    ).model_dump()
    changed = [k for k in FIELDS if old[k] != p.model_dump()[k]]
    reasons = []
    from .safety import unsafe_weight_goal

    if row.payload.get("available") and unsafe_weight_goal(
        " ".join([p.goal, *p.objectives, p.food_preferences])
    ):
        reasons.append(
            "Rapid-cutting or extreme-restriction request: legacy numerical targets are withheld; seek qualified sports-dietitian review"
        )
    if changed:
        reasons.append("Nutrition profile inputs changed: " + ", ".join(changed))
    if row.payload.get("catalog_version") != VERSION:
        reasons.append("Legacy illustrative catalog requires reviewed regeneration")
    if row.payload.get("source_preferences_id") != (
        ctx["preferences"].id if ctx["preferences"] else None
    ):
        reasons.append("Nutrition preferences or dietary feedback changed")
    if row.payload.get("source_training_signature", []) != training_signature(ctx["training"]):
        reasons.append("Approved training volume changed")
    review = weight_review(p, ctx["checks"], row.payload.get("effective_weight_kg", p.weight_kg))
    if review["needs_review"]:
        reasons.append(review["reason"])
    return {
        "needs_review": bool(reasons),
        "reason": "; ".join(reasons) or "Saved nutrition matches current inputs",
        "changed_fields": changed,
        "weight_review": review,
    }


def visible(ctx):
    if not ctx["nutrition"]:
        return None
    state = status(ctx)
    if state["needs_review"]:
        return {
            "available": False,
            "reason": state["reason"]
            + ". Preview and approve a current-input meal plan before using targets.",
            "guidance": GENERAL,
            "days": [],
            "grocery": [],
            "status": state,
        }
    return {**ctx["nutrition"].payload, "guidance": GENERAL, "status": state}


def proposed(ctx, change):
    if change.kind == "regenerate":
        result = build(ctx)
        result["changes"] = [
            "Rebuild seven days from current profile, dietary feedback, approved training volume and sustained weight-review context; retain previous versions."
        ]
        return result
    if not ctx["nutrition"] or status(ctx)["needs_review"]:
        raise ValueError(
            "Nutrition inputs changed; preview a regenerated plan before substitutions"
        )
    p = Profile.model_validate(ctx["nutrition"].payload["inputs"])
    return substitute(
        ctx["nutrition"].payload,
        p,
        preferences(ctx),
        change.day,
        change.meal,
        change.protein_id,
        change.food_id,
    )


def binding(ctx):
    return {
        k: ctx[k].id if ctx[k] else None
        for k in ("profile", "training", "nutrition", "preferences")
    } | {"check_ids": sorted(r.id for r in ctx["checks"])}
