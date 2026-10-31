import math

import pytest
from pydantic import ValidationError

from app.analysis import (
    LB_PER_KG,
    AthleticAssessmentService,
    FighterMatchingService,
    PhysicalProfileService,
    WeightClassService,
    weight_classes,
)
from app.fighters import SeededFighterProvider
from app.programs import NutritionPlanService, TrainingPlanService
from app.schemas import Benchmark, MatchWeights, Profile


def test_physical_math_and_missing():
    p = Profile(height_cm=180, weight_kg=81, wingspan_cm=185, body_fat=20)
    result = PhysicalProfileService.assess(p)
    assert result["bmi"] == 25
    assert result["ape_index_cm"] == 5
    assert result["lean_mass_kg"] == 64.8
    assert result["reach_ratio"] == 1.028
    assert PhysicalProfileService.assess(Profile())["ape_index_cm"] is None
    assert 100 / LB_PER_KG == pytest.approx(45.359237)


@pytest.mark.parametrize(
    "name,limit",
    [
        ("Flyweight", 125),
        ("Bantamweight", 135),
        ("Featherweight", 145),
        ("Lightweight", 155),
        ("Welterweight", 170),
        ("Middleweight", 185),
        ("Light Heavyweight", 205),
        ("Heavyweight", 265),
    ],
)
def test_division_boundaries(name, limit):
    p = Profile(weight_kg=limit / LB_PER_KG)
    assert WeightClassService.assess(p)["scale_reference"] == name
    p.weight_kg += 0.001
    assert WeightClassService.assess(p)["scale_reference"] != name


def test_women_history_allowance_and_minor():
    rows = weight_classes("Women")["rows"]
    assert [r["title_lb"] for r in rows if r["active"]] == [115, 125, 135]
    assert not rows[-1]["active"]
    assert all(r["non_title_lb"] == r["title_lb"] + 1 for r in rows)
    result = WeightClassService.assess(Profile(age=17))
    assert result["minor"]
    assert "under-18" in result["guidance"]
    assert "Insufficient" in result["target"]


def test_identical_physical_match_and_missing_renormalization():
    f = SeededFighterProvider().all()[0]
    p = Profile(height_cm=f["height_cm"], wingspan_cm=f["reach_cm"])
    ranking = FighterMatchingService().rank(
        p, MatchWeights(physical=100, background=0, style=0, stance=0, weight_class=0)
    )
    assert ranking["matches"][0]["score"] == 100
    assert ranking["matches"][0]["fighter"]["id"] == f["id"]
    p.wingspan_cm = None
    result = FighterMatchingService().rank(p, MatchWeights())
    assert result["matches"][0]["breakdown"]["physical"] == 100
    assert "stance" in result["matches"][0]["excluded"]
    assert sum(result["weights"].values()) == 100
    assert result == FighterMatchingService().rank(p, MatchWeights())


def test_weights_missing_style_and_empty_data():
    with pytest.raises(ValidationError):
        MatchWeights(physical=0, background=0, style=0, stance=0, weight_class=0)
    assert not FighterMatchingService().rank(
        Profile(), MatchWeights(physical=0, background=0, style=100, stance=0, weight_class=0)
    )["matches"]
    assert (
        len(FighterMatchingService().rank(Profile(division="Women"), MatchWeights())["matches"])
        == 3
    )
    for f in SeededFighterProvider().all():
        assert f["source"].startswith(("https://www.ufc.com/", "https://en.wikipedia.org/wiki/"))
        assert f["verified_at"]
        assert f["record"] is None


@pytest.mark.parametrize("days", range(1, 7))
@pytest.mark.parametrize("minutes", [20, 45, 90])
def test_training_constraints(days, minutes):
    plan = TrainingPlanService.generate(Profile(days=days, minutes=minutes))
    assert len(plan["weeks"]) == 12
    for w in plan["weeks"]:
        assert len(w["sessions"]) == min(days, 4)
        assert len(w["sessions"]) < 7
        assert all(s["minutes"] <= minutes for s in w["sessions"])
        strength_days = [s["id"].split("-d")[1] for s in w["sessions"] if s["type"] == "Strength"]
        assert all(int(b) - int(a) >= 2 for a, b in zip(strength_days, strength_days[1:]))
        assert w["deload"] == (w["week"] in (4, 8, 12))
    assert plan["inputs"]["days"] == days


def test_recovery_and_equipment_adaptation():
    p = Profile(days=6, sleep=5, gym=False, mma_gym=False)
    result = TrainingPlanService.generate(p)
    assert result["days"] == 3
    assert result["weeks"][0]["sessions"][0]["exercises"][0]["name"] == "Chair squat"
    assert "Solo" in result["weeks"][0]["sessions"][1]["exercises"][0]["name"]
    assert result["weeks"][0]["sessions"][0]["exercises"][0]["substitution"]


def test_nutrition_arithmetic_and_energy():
    p = Profile(metabolic_sex="male", weight_kg=80, height_cm=180, age=30, activity="moderate")
    n = NutritionPlanService.generate(p)
    assert n["rmr"] == 1780
    assert n["estimated_maintenance"] == 2848
    assert len(n["days"]) == 7
    for d in n["days"]:
        t = d["totals"]
        assert abs(t["calories"] - 4 * t["protein"] - 4 * t["carbs"] - 9 * t["fat"]) < 1
        assert abs(t["calories"] - n["estimated_maintenance"]) < 3
        assert sum(m["calories"] for m in d["meals"]) == pytest.approx(t["calories"], abs=0.1)


@pytest.mark.parametrize(
    "changes",
    [
        {"age": 17},
        {"clinical_nutrition": True},
        {"metabolic_sex": "unspecified"},
        {"allergies": ["unknown allergen"]},
        {"body_fat": 5},
    ],
)
def test_nutrition_withholds_unsafe_or_unknown(changes):
    p = Profile(metabolic_sex="male")
    n = NutritionPlanService.generate(p.model_copy(update=changes))
    assert not n["available"]
    assert not n["days"]


def test_vegan_gluten_allergy_exclusion():
    n = NutritionPlanService.generate(
        Profile(metabolic_sex="female", diet=["Vegan", "Gluten-free"], allergies=["soy"])
    )
    assert n["available"]
    foods = {i["food"] for d in n["days"] for m in d["meals"] for i in m["ingredients"]}
    assert not foods & {"chicken breast (cooked)", "tofu", "oats (dry)"}


def test_validation_and_benchmark_comparison():
    for change in [{"weight_kg": 0}, {"days": 7}, {"wingspan_cm": 0}, {"weight_kg": math.nan}]:
        with pytest.raises(ValidationError):
            Profile(**change)
    with pytest.raises(ValidationError):
        Benchmark(name="Squat", value=60, unit="seconds")
    before = Benchmark(name="Squat", value=40, unit="kg", reps=5).model_dump()
    after = {**before, "value": 45}
    assert AthleticAssessmentService.compare([before], [after])[0]["delta"] == 5
    assert not AthleticAssessmentService.compare([before], [{**after, "reps": 1}])


def test_benchmark_evidence_not_compared_as_improvement():
    from app.analysis import AthleticAssessmentService

    b = {"name": "Squat", "value": 80, "unit": "kg", "reps": 5, "provenance": "Estimated"}
    assert (
        AthleticAssessmentService.compare([b], [{**b, "value": 90, "provenance": "Measured"}]) == []
    )
    assert AthleticAssessmentService.compare([b], [{**b, "value": 85}])[0]["delta"] == 5


def test_program_time_budget_mixed_days_and_intensity():
    from app.programs import TrainingPlanService
    from app.schemas import Profile

    for days in (1, 2, 3, 6):
        p = Profile(name="Sam", days=days, minutes=20, intensity="Gentle")
        plan = TrainingPlanService.generate(p)
        for week in plan["weeks"]:
            for session in week["sessions"]:
                assert session["minutes"] <= 20
                assert session["effort"] <= 4
                assert (
                    sum(ex["block_minutes"] for ex in session["exercises"])
                    <= session["minutes"] - 10 + 0.01
                )
        if days <= 2:
            assert plan["weeks"][0]["sessions"][0]["type"] == "Mixed fundamentals"
