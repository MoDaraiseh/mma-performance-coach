"""Primary user text authorizes a capability; model output and context never do."""

from .coach_actions import interpret
from .safety import unsafe_weight_goal


def safety_reason(message, p):
    q = message.lower()
    if unsafe_weight_goal(message) or any(
        t in q
        for t in (
            "weight cut",
            "cut weight",
            "water cut",
            "dehydrat",
            "water load",
            "starv",
            "rapid weight",
            "sauna",
            "diuretic",
            "laxative",
            "lose weight fast",
            "kg overnight",
        )
    ):
        return "I cannot provide rapid weight cutting, dehydration or extreme restriction instructions. Consult a qualified sports dietitian and medical team for competition-specific needs."
    if p.age < 18 and any(
        t in q
        for t in (
            "calorie",
            "macro",
            "fasting",
            "weight loss",
            "target weight",
            "goal weight",
            "lose weight",
            "gain weight",
            "should i weigh",
        )
    ):
        return "Numerical weight-management and nutrition targets are withheld for minors. A qualified youth sports dietitian and pediatric clinician should individualize needs with a parent or guardian as appropriate."
    if p.limitations or any(
        t in q
        for t in (
            "pain",
            "injur",
            "concussion",
            "dizzy",
            "diagnos",
            "medication",
            "insulin",
            "eating disorder",
            "chest pressure",
        )
    ):
        return "I cannot diagnose medical conditions, prescribe medication or rehabilitation. Stop symptom-provoking activity and seek qualified medical assessment."
    return None


def authorize_intent(message, active, intent):
    if not intent or intent.kind in {"explain", "explain_matches"}:
        return
    requested = interpret(message, active)
    authorize_permission(requested, intent)


def authorize_permission(requested, intent):
    if not requested or requested.kind != intent.kind:
        raise ValueError("Provider action was not authorized by the user's explicit request")
    for key in (
        "week",
        "day",
        "target_day",
        "days",
        "minutes",
        "meal_day",
        "meal",
        "exercise_id",
        "alternative_id",
        "protein_id",
        "food_id",
    ):
        expected = getattr(requested, key)
        if expected is not None and getattr(intent, key) != expected:
            raise ValueError("Provider arguments conflict with the user's request")


def validate_prose(answer, limitations):
    text = (answer + " " + limitations).lower()
    if any(
        t in text
        for t in (
            "water load",
            "dehydrate",
            "sauna",
            "calorie deficit",
            "cut water",
            "i updated",
            "i have updated",
            "i changed",
            "i saved",
            "i have saved",
            "i applied",
            "has been applied",
            "i rescheduled",
            "i increased",
            "i approved",
            "i deleted",
            "change is saved",
            "you are ufc-ready",
            "you have professional-level fighting skill",
            "this plan is clinically validated",
            "this plan is medically approved",
            "this meal is allergen-free",
        )
    ):
        raise ValueError("Unsupported persistence or safety claim")
