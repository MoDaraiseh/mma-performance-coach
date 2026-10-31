from copy import deepcopy
from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.coach_actions import interpret
from app.dietary import eligible
from app.ingredients import CATALOG, portion
from app.meal_composition import validate_plan
from app.nutrition import NutritionPlanService, substitute
from app.nutrition_calculations import calculate
from app.nutrition_integrity import weight_review
from app.nutrition_models import AdaptiveCoachOutput, CoachIntent, NutritionPreferences
from app.schemas import Profile


def profile(**kwargs):
    return Profile(metabolic_sex="male", **kwargs)


def test_catalog_provenance_original_energy_and_unit_scaling():
    assert len(CATALOG) == 40
    for food in CATALOG.values():
        assert food["source"]["license"] == "CC0-1.0"
        assert food["source"]["fdc_id"] and food["source"]["archive_sha256"]
        assert food["serving_g"] == 100
        assert sum(food["per_100g"][k] for k in ("protein", "carbs", "fat")) <= 100.1
        base, double = portion(food["id"], 100), portion(food["id"], 200)
        for k in base:
            assert double[k] == pytest.approx(base[k] * 2)
    rice = portion("rice", 100)
    assert rice["source_calories"] == 130
    assert rice["calories"] != rice["source_calories"]
    assert CATALOG["rice"]["per_100g"]["protein"] == 2.69
    for grams in (-1, 0, 1001, float("nan")):
        with pytest.raises(ValueError):
            portion("rice", grams)


@pytest.mark.parametrize(
    "diet",
    [
        [],
        ["Halal"],
        ["Vegetarian"],
        ["Vegan"],
        ["Dairy-free"],
        ["Gluten-free"],
        ["Vegan", "Gluten-free"],
    ],
)
def test_restrictions_macros_portions_and_groceries(diet):
    p = profile(diet=diet)
    prefs = NutritionPreferences()
    plan = NutritionPlanService.generate(p, prefs)
    assert plan["available"], plan.get("reason")
    allowed = eligible(p, prefs)
    validate_plan(plan, allowed)
    assert plan["days"][0]["totals"]["protein"] == pytest.approx(1.6 * p.weight_kg, abs=1)
    grocery = {}
    for day in plan["days"]:
        assert abs(day["totals"]["calories"] - plan["target_calories"]) < 3
        for meal in day["meals"]:
            assert (
                abs(meal["calories"] - 4 * meal["protein"] - 4 * meal["carbs"] - 9 * meal["fat"])
                < 0.1
            )
            for part in meal["ingredients"]:
                assert part["id"] in allowed
                grocery[part["id"]] = grocery.get(part["id"], 0) + part["grams"]
    assert {i["id"]: i["grams"] for i in plan["grocery"]} == {
        k: round(v, 1) for k, v in sorted(grocery.items())
    }


@pytest.mark.parametrize(
    "allergy,excluded",
    [
        ("soy", {"tofu"}),
        ("dairy", {"yogurt"}),
        ("egg", {"egg"}),
        ("fish", {"salmon"}),
        ("wheat", {"oats", "bulgur", "couscous"}),
        ("legumes", {"tofu", "lentils", "chickpeas", "black-beans"}),
    ],
)
def test_common_allergy_aliases(allergy, excluded):
    assert not set(eligible(profile(allergies=[allergy]), NutritionPreferences())) & excluded


def test_additions_cannot_relax_profile_restrictions_and_dislikes_are_real():
    p = profile(diet=["Vegan"], allergies=["soy"])
    prefs = NutritionPreferences(
        add_diet=[], add_allergies=[], dislikes=["rice"], unavailable=["potato"]
    )
    allowed = eligible(p, prefs)
    assert not set(allowed) & {"chicken", "yogurt", "egg", "salmon", "tofu", "rice", "potato"}
    with pytest.raises(ValueError, match="Unrecognized"):
        eligible(profile(allergies=["unknown allergen"]), prefs)
    with pytest.raises(ValueError, match="catalog"):
        eligible(profile(), NutritionPreferences(dislikes=["invented"]))


def test_goal_adjustments_are_explicit_bounded_and_withheld_conservatively():
    p = profile(weight_kg=90)
    baseline = calculate(p, NutritionPreferences())
    lower = calculate(p, NutritionPreferences(objective="Sustainable reduction"))
    assert 0 < baseline["target_calories"] - lower["target_calories"] <= 150
    assert lower["target_calories"] >= baseline["estimated_maintenance"] * 0.95 - 1
    for change in (
        {"competitive": True},
        {"goal": "Prepare for amateur competition under qualified supervision"},
        {"recovery": "Poor recovery"},
        {"sleep": 5},
        {"weight_kg": 70},
    ):
        r = calculate(
            p.model_copy(update=change), NutritionPreferences(objective="Sustainable reduction")
        )
        assert r["adjustment"] == 0
    assert (
        calculate(p, NutritionPreferences(objective="Sustainable reduction", hunger=5))[
            "adjustment"
        ]
        == 0
    )
    assert 0 < calculate(p, NutritionPreferences(objective="Build gradually"))["adjustment"] <= 150


@pytest.mark.parametrize(
    "changes",
    [
        {"age": 17},
        {"clinical_nutrition": True},
        {"metabolic_sex": "unspecified"},
        {"weight_kg": 45},
        {"body_fat": 5},
    ],
)
def test_exclusions_do_not_expose_numeric_targets(changes):
    plan = NutritionPlanService.generate(profile().model_copy(update=changes))
    assert not plan["available"] and not plan["days"]
    assert "target_calories" not in plan and "macro_targets" not in plan


def test_preferences_snacks_culture_budget_and_substitution():
    p = profile(diet=["Halal"])
    prefs = NutritionPreferences(
        culture="South Asian inspired", budget="Low", snacks=False, dislikes=["tofu"]
    )
    plan = NutritionPlanService.generate(p, prefs)
    assert plan["available"]
    assert all(len(d["meals"]) == 3 for d in plan["days"])
    foods = {i["id"] for d in plan["days"] for m in d["meals"] for i in m["ingredients"]}
    assert not foods & {"tofu", "salmon", "quinoa"}
    changed = substitute(plan, p, prefs, 1, "Lunch")
    assert changed["days"][0]["meals"][1]["recipe_id"] != plan["days"][0]["meals"][1]["recipe_id"]
    for k in ("calories", "protein", "carbs", "fat"):
        assert changed["days"][0]["totals"][k] == pytest.approx(plan["days"][0]["totals"][k], abs=1)
    validate_plan(changed, eligible(p, prefs))
    with pytest.raises(ValueError):
        substitute(plan, p, prefs, 1, "Lunch", "tofu")
    broken = deepcopy(plan)
    broken["days"][0]["meals"][0]["protein"] += 10
    with pytest.raises(ValueError):
        validate_plan(broken, eligible(p, prefs))


def test_weight_trend_requires_sustained_direction_and_span():
    p = profile(weight_kg=80)

    def rows(values, days):
        return [
            SimpleNamespace(
                payload={"date": (date.today() - timedelta(days=d)).isoformat(), "weight_kg": v}
            )
            for v, d in zip(values, days)
        ]

    assert not weight_review(p, rows([82], [0]))["needs_review"]
    assert not weight_review(p, rows([82, 82, 82], [2, 1, 0]))["needs_review"]
    assert not weight_review(p, rows([82, 79, 82], [14, 7, 0]))["needs_review"]
    assert weight_review(p, rows([82, 82.5, 82], [14, 7, 0]))["needs_review"]
    assert not weight_review(p, rows([82, 82.5, 82], [14, 7, 0]), 82)["needs_review"]


def test_intent_schema_and_offline_interpretation():
    assert interpret("Make my Wednesday workout shorter to 30 minutes").minutes == 30
    assert interpret("Suggest a different halal lunch").kind == "meal_swap"
    assert interpret("How can I fit boxing into my schedule?").kind == "schedule_boxing"
    assert interpret("Why did you prioritize wrestling?") is None
    assert interpret("What is a substitute for Goblet squat?").kind == "exercise_substitution"
    with pytest.raises(ValidationError):
        CoachIntent(kind="write_database")
    with pytest.raises(ValidationError):
        AdaptiveCoachOutput(
            answer="ok", limitations="ok", intent={"kind": "meal_swap", "calories": 500}
        )


def test_validation_rejects_nonfinite_targets_and_totals():
    p, prefs = profile(), NutritionPreferences()
    plan = NutritionPlanService.generate(p, prefs)
    plan["days"][0]["meals"][0]["calories"] = float("nan")
    with pytest.raises(ValueError):
        validate_plan(plan, eligible(p, prefs))


def test_boxing_focus_uses_existing_uncoached_time_block():
    from types import SimpleNamespace

    from app.coach_actions import candidate
    from app.plan_integrity import make_plan

    p = profile()
    source = SimpleNamespace(id="p", payload=p.model_dump())
    active = SimpleNamespace(id="a", payload=make_plan(source))
    result = candidate(
        {"profile": source, "training": active, "checks": []},
        [],
        CoachIntent(kind="schedule_boxing"),
    )
    assert result["target"] == "training"
    assert result["after_session"]["minutes"] == result["before_session"]["minutes"]
    assert any(
        "Solo boxing" in e.get("technique_focus", "") for e in result["after_session"]["exercises"]
    )
    assert result["plan"]["weekly_minutes"] == active.payload["weekly_minutes"]


def test_ambiguous_exercise_question_requests_clarification():
    import asyncio

    from app.mma_agent import MMAAgentService
    from app.schemas import CoachRequest

    result = asyncio.run(
        MMAAgentService.respond(
            CoachRequest(message="What is a substitute for this exercise?"), profile(), None, []
        )
    )
    assert result["intent"] is None
    assert "Which exercise or meal" in result["answer"]
