from copy import deepcopy
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.dietary import eligible
from app.ingredients import CATALOG, catalog_payload, serving_grams, validate_catalog
from app.meal_composition import recompute, validate_plan
from app.nutrition import NutritionPlanService, substitute
from app.nutrition_integrity import build, status, training_signature
from app.nutrition_models import NutritionPreferences
from app.schemas import Profile


def profile(**values):
    return Profile(metabolic_sex="male", **values)


def test_mass_conversion_and_no_invented_volume():
    assert serving_grams(0.1, "kg") == 100
    assert serving_grams(1, "oz") == pytest.approx(28.349523125)
    for value, unit in [(1, "cup"), (float("nan"), "g"), (-1, "g")]:
        with pytest.raises(ValueError):
            serving_grams(value, unit)


def test_catalog_duplicate_invalid_and_missing_optional_nutrients():
    records = deepcopy(list(CATALOG.values()))
    records[0]["per_100g"]["sodium_mg"] = None
    validate_catalog(records)
    with pytest.raises(ValueError, match="Duplicate"):
        validate_catalog([*records, records[0]])
    records[0]["per_100g"]["protein"] = None
    with pytest.raises(ValueError, match="required"):
        validate_catalog(records)
    assert catalog_payload()["coverage"]["foods"] == 55
    assert all(r["certification"]["halal"] == "unknown" for r in CATALOG.values())


def test_unknown_allergen_metadata_is_not_clearance(monkeypatch):
    food = deepcopy(CATALOG["rice"])
    food.pop("allergen_review")
    monkeypatch.setitem(CATALOG, "rice", food)
    assert "rice" not in eligible(profile(allergies=["milk"]), NutritionPreferences())
    assert "rice" not in eligible(profile(diet=["Gluten-free"]), NutritionPreferences())


@pytest.mark.parametrize("count", [3, 4])
def test_customization_variety_budget_and_preparation(count):
    p = profile(diet=["Vegan"], budget="Low")
    prefs = NutritionPreferences(meals_per_day=count, cooking_minutes=10)
    plan = NutritionPlanService.generate(p, prefs)
    assert plan["available"], plan.get("reason")
    validate_plan(plan, eligible(p, prefs))
    assert all(len(d["meals"]) == count for d in plan["days"])
    recipes = set()
    for d in plan["days"]:
        for m in d["meals"]:
            recipes.add(m["recipe_id"])
            assert m["preparation_minutes"] <= 10
            assert len(m["preparation_steps"]) == 4
            assert all(CATALOG[i["id"]]["cost_tier"] <= 2 for i in m["ingredients"])
    assert len(recipes) >= 7
    with pytest.raises(ValidationError):
        NutritionPreferences(cooking_minutes=5)


def test_food_swap_rebalances_and_preserves_original():
    p, prefs = profile(), NutritionPreferences()
    plan = NutritionPlanService.generate(p, prefs)
    old = deepcopy(plan)
    new = substitute(plan, p, prefs, 1, "Lunch", food_id="pasta")
    assert plan == old
    assert "pasta" in {i["id"] for i in new["days"][0]["meals"][1]["ingredients"]}
    validate_plan(new, eligible(p, prefs))
    assert new["substitution_comparison"]["before"] != new["substitution_comparison"]["after"]
    assert new["grocery"] != old["grocery"]
    with pytest.raises(ValueError):
        substitute(
            plan, p, NutritionPreferences(add_diet=["Gluten-free"]), 1, "Lunch", food_id="pasta"
        )


def test_training_timing_and_recovery_no_automatic_restriction():
    p, prefs = profile(), NutritionPreferences()
    training = {"weeks": [{"sessions": [{"day": "Monday", "minutes": 120}]}]}
    plan = NutritionPlanService.generate(p, prefs, training)
    assert "Higher-volume" in plan["days"][0]["training_context"]["note"]
    assert "Recovery day" in plan["days"][1]["training_context"]["note"]
    assert plan["days"][0]["totals"]["calories"] == pytest.approx(
        plan["days"][1]["totals"]["calories"], abs=3
    )
    before = training_signature(SimpleNamespace(payload=training))
    training["weeks"][0]["sessions"][0]["day"] = "Tuesday"
    assert training_signature(SimpleNamespace(payload=training)) != before


def test_same_volume_calendar_move_invalidates_saved_nutrition():
    ctx = {
        "profile": SimpleNamespace(id="profile", payload=profile().model_dump()),
        "training": SimpleNamespace(
            id="training", payload={"weeks": [{"sessions": [{"day": "Monday", "minutes": 60}]}]}
        ),
        "nutrition": None,
        "preferences": None,
        "checks": [],
    }
    ctx["nutrition"] = SimpleNamespace(id="nutrition", payload=build(ctx))
    assert not status(ctx)["needs_review"]
    ctx["training"].payload["weeks"][0]["sessions"][0]["day"] = "Tuesday"
    assert status(ctx)["needs_review"]


def test_catalog_validation_supports_large_curated_imports():
    # Synthetic IDs exercise capacity; these are never distributed as real foods.
    rows = []
    for i in range(1000):
        row = deepcopy(CATALOG["rice"])
        row["id"], row["source"]["fdc_id"] = f"synthetic-{i}", i + 1000000
        rows.append(row)
    validate_catalog(rows)


def test_optional_nutrient_totals_propagate_unknown_and_reject_tampering(monkeypatch):
    p, prefs = profile(), NutritionPreferences()
    plan = NutritionPlanService.generate(p, prefs)
    item = plan["days"][0]["meals"][0]["ingredients"][0]["id"]
    food = deepcopy(CATALOG[item])
    food["per_100g"]["sodium_mg"] = None
    monkeypatch.setitem(CATALOG, item, food)
    updated = recompute(plan)
    assert updated["days"][0]["nutrients"]["sodium_mg"] is None
    validate_plan(updated, eligible(p, prefs))
    updated["days"][0]["nutrients"]["sodium_mg"] = 0
    with pytest.raises(ValueError, match="totals"):
        validate_plan(updated, eligible(p, prefs))


def test_strength_and_conditioning_guidance_uses_approved_session_type():
    training = {
        "weeks": [
            {
                "sessions": [
                    {"day": "Monday", "minutes": 60, "type": "Strength"},
                    {"day": "Tuesday", "minutes": 60, "type": "Conditioning"},
                ]
            }
        ]
    }
    plan = NutritionPlanService.generate(profile(), NutritionPreferences(), training)
    assert "Strength practice" in plan["days"][0]["training_context"]["note"]
    assert "Conditioning practice" in plan["days"][1]["training_context"]["note"]


def test_missing_calendar_is_unknown_not_assumed_recovery():
    plan = NutritionPlanService.generate(profile(), NutritionPreferences(), {"weeks": []})
    assert plan["available"]
    assert "No approved training schedule" in plan["days"][0]["training_context"]["note"]
