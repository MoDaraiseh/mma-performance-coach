from copy import deepcopy
from types import SimpleNamespace

import pytest
from test_api import account
from test_api import client as api_client

from app.db import engine
from app.dietary import eligible
from app.exercises import CATALOG as exercises
from app.fighter_governance import quality
from app.fighters import SeededFighterProvider
from app.ingredients import CATALOG, MACROS
from app.matching import FighterMatchingService, background_terms
from app.meal_composition import measure, solve_portions, validate_plan
from app.nutrition import NutritionPlanService, substitute
from app.nutrition_models import NutritionPreferences
from app.plan_integrity import make_plan, plan_status
from app.schemas import MatchWeights, Profile
from app.training import TrainingPlanService

client = api_client


@pytest.fixture(scope="session", autouse=True)
def close_focused_database():
    yield
    engine.dispose()


def test_expanded_catalogs_have_source_coverage_and_resolvable_alternatives():
    records = SeededFighterProvider().all()
    report = quality(records)
    assert report["validated_count"] == 19
    assert report["unestablished_rights"] == 11
    assert report["providers"]["wikimedia-reviewed"] == 8
    for key in ("volkov", "antonina-shevchenko"):
        r = next(r for r in records if r["id"] == key)
        assert r["current_division"] is None and r["record"] is None
        assert r["career_status"] == "Unknown" and not r["style_traits"]
        assert key in report["field_gaps"]["record"]
        assert r["sources"][0]["license_reference"] == "CC-BY-SA-4.0"
    assert len(CATALOG) == 55 and len(exercises) == 49
    assert len({r["source"]["fdc_id"] for r in CATALOG.values()}) == 55
    for r in CATALOG.values():
        assert r["source"]["archive_sha256"] and r["source"]["license"] == "CC0-1.0"
        assert r["certification"]["halal"] == "unknown"
    for r in exercises.values():
        assert r["objective"] and r["technique"] and r["modification_notes"]
        assert set(r["alternatives"]) <= exercises.keys()
    assert exercises["chest-pass"]["requires_coach"]
    assert exercises["coached-pummel"]["requires_coach"]


@pytest.mark.parametrize("allergy", ["peanut", "peanuts", "nuts"])
def test_plural_peanut_and_legume_allergies_exclude_new_foods(allergy):
    assert "peanut-butter" not in eligible(Profile(allergies=[allergy]), NutritionPreferences())
    if allergy == "nuts":
        assert not {"almonds", "walnuts"} & set(
            eligible(Profile(allergies=[allergy]), NutritionPreferences())
        )
    allowed = eligible(Profile(allergies=["legumes"]), NutritionPreferences())
    assert not {"peanut-butter", "soy-milk", "tofu", "green-peas"} & set(allowed)


def test_expanded_animal_foods_are_not_mislabeled_vegan():
    vegan = eligible(Profile(diet=["Vegan"]), NutritionPreferences())
    assert not {"skim-milk", "turkey", "lean-beef"} & set(vegan)
    assert "soy-milk" in vegan
    dairy_free = eligible(Profile(diet=["Dairy-free"]), NutritionPreferences())
    assert "skim-milk" not in dairy_free


def test_rice_allergy_excludes_related_rice_foods_not_only_exact_identifier():
    allowed = set(eligible(Profile(allergies=["rice"]), NutritionPreferences()))
    assert not {"rice", "brown-rice", "rice-noodles"} & allowed
    assert "potato" in allowed


@pytest.mark.parametrize(
    "allergy,excluded", [("beef", {"lean-beef"}), ("seed", {"chia", "pumpkin-seeds"})]
)
def test_new_reviewed_allergen_tags_are_recognized_without_global_withholding(allergy, excluded):
    allowed = set(eligible(Profile(allergies=[allergy]), NutritionPreferences()))
    assert "rice" in allowed and not allowed & excluded


@pytest.mark.parametrize("replacement", ["almonds", "peanut-butter", "avocado"])
def test_fat_substitution_accounts_for_all_macros_and_preserves_source(replacement):
    p, prefs = Profile(metabolic_sex="male"), NutritionPreferences()
    plan = NutritionPlanService.generate(p, prefs)
    before = deepcopy(plan)
    changed = substitute(plan, p, prefs, 1, "Lunch", food_id=replacement)
    meal = changed["days"][0]["meals"][1]
    assert replacement in {i["id"] for i in meal["ingredients"]}
    assert "olive-oil" not in {i["id"] for i in meal["ingredients"]}
    assert plan == before
    assert measure(meal)["calories"] == meal["calories"]
    validate_plan(changed, eligible(p, prefs))
    for k in MACROS:
        assert abs(changed["substitution_comparison"]["delta"][k]) <= 0.1
    assert solve_portions(["rice", "rice", "rice"], dict(protein=10, carbs=50, fat=10)) is None


def test_weight_priorities_change_ranking_without_source_style_inference():
    p = Profile(wingspan_cm=185, experience=[dict(discipline="Boxing", months=12)])
    base = SeededFighterProvider().all()[0]
    rows = []
    for key, height, reach, background, division in [
        ("build", 180, 185, ["Wrestling"], "Heavyweight"),
        ("skill", 200, 205, ["Boxing"], "Heavyweight"),
        ("division", 160, 165, ["BJJ"], "Middleweight"),
    ]:
        r = deepcopy(base)
        r.update(
            id=key,
            height_cm=height,
            reach_cm=reach,
            background=background,
            division_history=[dict(name=division)],
        )
        rows.append(r)
    service = FighterMatchingService(SimpleNamespace(all=lambda: rows))
    for factor, expected in [
        ("physical", "build"),
        ("background", "skill"),
        ("weight_class", "division"),
    ]:
        weights = {k: 0 for k in ("physical", "background", "weight_class", "style", "stance")}
        weights[factor] = 100
        first = service.rank(p, MatchWeights(**weights))
        assert first == service.rank(p, MatchWeights(**weights))
        assert first["matches"][0]["fighter"]["id"] == expected
    assert background_terms(["Brazilian Jiu-Jitsu", "BJJ"]) == {"bjj"}
    assert background_terms(["Muay Thai", "Kickboxing"]) == {"muay thai", "kickboxing"}
    assert (
        service.evaluate(
            Profile(experience=[dict(discipline="BJJ", months=12)]),
            MatchWeights(),
            {**rows[0], "background": ["Brazilian Jiu-Jitsu"]},
        )["breakdown"]["background"]
        == 100
    )


def test_competition_intent_requires_review_without_increasing_workload():
    p = Profile(gym_years=2, current_frequency=3, equipment=["dumbbells"], days=4)
    ordinary = TrainingPlanService.generate(p)
    competitive = TrainingPlanService.generate(p.model_copy(update={"competitive": True}))
    assert competitive["weekly_minutes"] == ordinary["weekly_minutes"]
    assert competitive["development_context"]["coach_review_required"]
    assert ordinary["weeks"][0]["sessions"][0]["exercises"] != []
    row = SimpleNamespace(id="profile", payload=p.model_dump())
    approved = SimpleNamespace(payload=make_plan(row))
    snapshot = deepcopy(approved.payload)
    row.payload["competitive"] = True
    assert "competitive" in plan_status(approved, row, None)["changed_fields"]
    assert approved.payload == snapshot


def test_new_fat_food_requires_owned_approval_and_allergy_invalidates_preview(client):
    account(client)
    assert client.post("/api/demo").status_code == 200
    original = client.get("/api/nutrition").json()
    history_before = client.get("/api/nutrition/history").json()
    response = client.post(
        "/api/nutrition/proposals", json=dict(kind="meal_swap", food_id="almonds")
    )
    assert response.status_code == 200, response.text
    proposal = response.json()["id"]
    assert client.get("/api/nutrition").json()["id"] == original["id"]
    profile = client.get("/api/profile").json()
    profile["allergies"] = ["tree nuts"]
    assert client.put("/api/profile", json=profile).status_code == 200
    assert client.post(f"/api/nutrition/proposals/{proposal}/approve").status_code == 409
    assert client.get("/api/nutrition/history").json() == history_before


def test_bundled_duplicate_identity_is_rejected_before_seeding(monkeypatch):
    from app import fighters

    original = fighters.reviewed_records()
    monkeypatch.setattr(fighters, "reviewed_records", lambda: [*original, original[0]])
    with pytest.raises(ValueError, match="Duplicate bundled"):
        SeededFighterProvider().all()


def test_competition_context_is_persisted_only_after_approved_revision(client):
    account(client)
    client.post("/api/demo")
    original = client.get("/api/training-plans").json()
    history_before = client.get("/api/training-plans/history").json()
    p = client.get("/api/profile").json()
    p["competitive"] = True
    assert client.put("/api/profile", json=p).status_code == 200
    assert client.get("/api/training-plans").json()["id"] == original["id"]
    proposal = client.post(
        "/api/revisions",
        json={"days": p["days"], "reason": "Review supervised amateur preparation"},
    )
    assert proposal.status_code == 200, proposal.text
    assert client.get("/api/training-plans/history").json() == history_before
    response = client.post(f"/api/revisions/{proposal.json()['id']}/approve")
    assert response.status_code == 200, response.text
    current = client.get("/api/training-plans").json()
    assert current["version"] == original["version"] + 1
    assert current["data"]["development_context"]["mode"] == "Supervised amateur preparation"
    history = client.get("/api/training-plans/history").json()
    assert next(r for r in history if r["id"] == original["id"]) == history_before[0]
