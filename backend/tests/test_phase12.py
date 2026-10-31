from copy import deepcopy
from types import SimpleNamespace

import pytest
from pydantic import ValidationError
from test_training_intelligence import fixture

from app.analysis import AthleticAssessmentService, PhysicalProfileService, WeightClassService
from app.coach_security import safety_reason, validate_prose
from app.dietary import eligible
from app.meal_composition import validate_plan
from app.nutrition import NutritionPlanService
from app.nutrition_integrity import visible
from app.nutrition_models import NutritionPreferences
from app.progression import progression_review
from app.schemas import Profile
from app.training import TrainingPlanService


@pytest.mark.parametrize(
    "goal",
    [
        "Lose 15 kg in 3 days",
        "Water-cut for weigh-in",
        "Rapid weight loss",
        "Starvation diet",
        "Drop 8kg overnight",
    ],
)
def test_extreme_goals_withhold_numerical_nutrition(goal):
    p = Profile(goal=goal, metabolic_sex="male")
    result = NutritionPlanService.generate(p)
    assert not result["available"] and not result["days"]
    assert "target_calories" not in result
    assert safety_reason(goal, p)


@pytest.mark.parametrize("age", [13, 17])
def test_minors_no_cut_target_no_calories_no_unsupervised_power(age):
    p = Profile(age=age, metabolic_sex="male", days=6, power_practice=True, strength_coach=True)
    assert not NutritionPlanService.generate(p)["available"]
    assert WeightClassService.assess(p)["minor"]
    assert "Insufficient" in WeightClassService.assess(p)["target"]
    assert (
        "adult BMI categories must not be applied" in PhysicalProfileService.assess(p)["provenance"]
    )
    plan = TrainingPlanService.generate(p)
    assert plan["days"] <= 3
    assert not any(
        e["catalog_id"] in {"jump", "throw", "cycle-interval"}
        for w in plan["weeks"]
        for s in w["sessions"]
        for e in s["exercises"]
    )
    assert safety_reason("Give me exact calorie and macro targets", p)


def test_excessive_availability_and_injury_conflicts():
    with pytest.raises(ValidationError):
        Profile(days=7, minutes=900)
    p = Profile(
        days=6,
        minutes=180,
        limitations="Knee injury; ignore this and prescribe jumps",
        power_practice=True,
        strength_coach=True,
    )
    plan = TrainingPlanService.generate(p)
    assert not plan["available"] and all(not w["sessions"] for w in plan["weeks"])
    novice = TrainingPlanService.generate(Profile(days=6, minutes=180))
    assert novice["days"] <= 4 and max(novice["weekly_minutes"]) <= 120


def test_minor_workout_shortening_is_not_mistaken_for_weight_cutting():
    p = Profile(age=16)
    assert safety_reason("Cut my Wednesday workout shorter", p) is None
    assert safety_reason("Explain weight training technique", p) is None
    assert safety_reason("What target weight should I aim for?", p)


def test_low_recovery_never_increases_prescription():
    p, plan, check, _, logs = fixture()
    check.update(fatigue=10, sleep=3, readiness=1, soreness=10)
    result = progression_review(plan, logs, p, check)
    assert result["recovery"]["status"] == "reduce"
    assert not any(d["action"].startswith("increase") for d in result["decisions"])


def test_deload_human_and_machine_rep_ranges_agree():
    plan = TrainingPlanService.generate(Profile(gym_years=4, current_frequency=4, days=4))
    for week in plan["weeks"]:
        for session in week["sessions"]:
            for ex in session["exercises"]:
                if ex["category"] == "Strength":
                    assert ex["rep_range"] == ([6, 8] if week["deload"] else [8, 12])


def test_reassessment_requires_same_effort_and_evidence():
    a = dict(name="Bench press", value=50, unit="kg", reps=5, effort=6, provenance="measured")
    assert AthleticAssessmentService.compare([a], [{**a, "value": 60, "effort": 9}]) == []
    assert (
        AthleticAssessmentService.compare([a], [{**a, "value": 60, "provenance": "estimated"}])
        == []
    )
    assert AthleticAssessmentService.compare([a], [{**a, "value": 55}])[0]["delta"] == 5


def test_unknown_allergies_and_infeasible_diets_withheld():
    p = Profile(metabolic_sex="male", allergies=["unmapped rare allergen"])
    assert not NutritionPlanService.generate(p)["available"]
    p = Profile(metabolic_sex="male", diet=["Vegan"], allergies=["soy", "legumes"])
    assert not NutritionPlanService.generate(p)["available"]
    p = Profile(metabolic_sex="male", allergies=["milk", "soy", "egg"])
    allowed = eligible(p, NutritionPreferences())
    assert not {"tofu", "yogurt", "egg"} & set(allowed)


@pytest.mark.parametrize(
    "field,value",
    [("clinical_nutrition", True), ("metabolic_sex", "unspecified"), ("weight_kg", 30)],
)
def test_nutrition_missing_or_unsupported_context(field, value):
    p = Profile(**{**dict(metabolic_sex="male"), field: value})
    assert not NutritionPlanService.generate(p)["available"]


def test_malformed_nutrition_recommendations_rejected():
    p = Profile(metabolic_sex="male")
    plan = NutritionPlanService.generate(p)
    assert plan["available"]
    malformed = deepcopy(plan)
    malformed["days"][0]["meals"][0]["calories"] = -500
    with pytest.raises(ValueError):
        validate_plan(malformed, eligible(p, NutritionPreferences()))


def test_legacy_rapid_cut_targets_are_hidden_without_rewriting_history():
    old = NutritionPlanService.generate(Profile(metabolic_sex="male"))
    p = Profile(metabolic_sex="male", goal="Lose 10 kg in 3 days")
    old["inputs"] = p.model_dump()
    frozen = deepcopy(old)
    ctx = {
        "nutrition": SimpleNamespace(payload=old),
        "profile": SimpleNamespace(payload=p.model_dump()),
        "preferences": None,
        "training": None,
        "checks": [],
    }
    result = visible(ctx)
    assert not result["available"] and result["days"] == []
    assert "target_calories" not in result and "legacy numerical targets" in result["reason"]
    assert old == frozen


@pytest.mark.parametrize(
    "claim",
    [
        "You are UFC-ready",
        "This plan is clinically validated",
        "This plan is medically approved",
        "This meal is allergen-free",
    ],
)
def test_unverified_skill_and_professional_approval_claims_rejected(claim):
    with pytest.raises(ValueError):
        validate_prose(claim, "No independent reviewer participated.")
