from copy import deepcopy
from datetime import date, timedelta

import pytest
from test_training_intelligence import fixture

from app.athletics import DISCIPLINES, athletic_assessment, discipline_priorities
from app.progression import adapt_future, progression_review
from app.schemas import Profile, WorkoutLog
from app.training import TrainingPlanService


def exercises(plan):
    return [e for w in plan["weeks"] for s in w["sessions"] for e in s["exercises"]]


def trained(**overrides):
    return Profile(
        **{
            **dict(
                days=6,
                minutes=60,
                gym_years=4,
                current_frequency=5,
                mobility="Comfortable",
                equipment=["dumbbells", "bike", "medicine_ball"],
                strength_coach=True,
                power_practice=True,
                conditioning_mode="interval_cycling",
            ),
            **overrides,
        }
    )


def test_ten_dimensions_estimates_missing_anaerobic_and_no_anthropometric_skill_inference():
    p = Profile(
        benchmarks=[
            {"name": "Squat", "value": 60, "unit": "kg", "reps": 5},
            {"name": "Vertical jump", "value": 35, "unit": "cm", "provenance": "estimated"},
        ]
    )
    result = athletic_assessment(p)["development"]
    assert len(result["dimensions"]) == 10
    axes = {r["dimension"]: r for r in result["dimensions"]}
    assert axes["General strength"]["status"] == "Recorded observation"
    assert axes["Relative strength"]["evidence"]
    assert axes["Anaerobic conditioning"]["status"] == "Missing objective data"
    assert axes["Explosive performance"]["status"] == "Missing objective data"
    changed = p.model_copy(update={"height_cm": 220, "wingspan_cm": 240})
    assert discipline_priorities(changed) == discipline_priorities(p)


def test_profile_benchmark_fallback_keeps_checkin_recovery_and_uses_original_benchmark_mass():
    p = Profile(weight_kg=80, benchmarks=[{"name": "Squat", "value": 60, "unit": "kg"}])
    assessment = athletic_assessment(
        p, {"benchmarks": [], "weight_kg": 100, "sleep": 5, "fatigue": 8, "mobility": "Limited"}
    )
    assert "0.75 x" in assessment["observations"][0]["derived"]
    assert assessment["mobility"] == "Limited"
    assert any(
        "5 hours" in text for r in assessment["development"]["dimensions"] for text in r["evidence"]
    )


@pytest.mark.parametrize("discipline", DISCIPLINES)
def test_independent_technical_goals_stage_and_no_calendar_based_complexity(discipline):
    p = Profile(
        days=3,
        current_frequency=3,
        experience=[
            dict(
                discipline=discipline,
                months=48,
                level="Advanced",
                instructor=True,
                sessions=1,
                technical_goals="Defensive exits",
            )
        ],
    )
    row = next(r for r in discipline_priorities(p) if r["discipline"] == discipline)
    assert row["stage"] == "Coach-led technical refinement"
    assert row["technical_goals"] == "Defensive exits"
    assert "Defensive exits" in row["development_reason"]
    plan = TrainingPlanService.generate(p)
    first = [
        e for e in plan["weeks"][0]["sessions"][1]["exercises"] if e["category"] == "Martial arts"
    ][0]
    later = [
        e for e in plan["weeks"][8]["sessions"][1]["exercises"] if e["category"] == "Martial arts"
    ][0]
    assert first["technique_focus"] == later["technique_focus"]
    assert "refinement" in first["technique_focus"]


def test_unentered_discipline_is_unknown_not_assumed_beginner():
    rows = athletic_assessment(Profile())["development"]["technical"]
    assert {r["discipline"] for r in rows} == set(DISCIPLINES)
    assert all(r["months"] is None and not r["recorded"] for r in rows)


def test_beginner_limit_and_exact_weekdays_recovery():
    p = Profile(days=6, available_days=["Tuesday", "Thursday", "Sunday"])
    plan = TrainingPlanService.generate(p)
    assert plan["days"] == 3
    assert {s["day"] for s in plan["weeks"][0]["sessions"]} == set(p.available_days)
    assert len(plan["recovery_days"]) == 4
    assert TrainingPlanService.generate(Profile(days=6))["days"] == 4


@pytest.mark.parametrize("years,frequency", [(2, 3), (6, 6)])
def test_intermediate_advanced_budget_deload_and_no_calendar_overload(years, frequency):
    p = trained(gym_years=years, current_frequency=frequency)
    plan = TrainingPlanService.generate(p)
    for week in plan["weeks"]:
        assert len(week["sessions"]) <= p.days
        assert 7 - len(week["sessions"]) >= 1
        for s in week["sessions"]:
            assert sum(e["block_minutes"] for e in s["exercises"]) == pytest.approx(
                s["minutes"] - 10, abs=0.02
            )
            assert s["minutes"] <= p.minutes
    assert plan["weekly_minutes"][0] == plan["weekly_minutes"][4] == plan["weekly_minutes"][8]
    assert plan["weekly_minutes"][3] < plan["weekly_minutes"][0]


@pytest.mark.parametrize(
    "override",
    [
        dict(age=17),
        dict(age=70),
        dict(strength_coach=False),
        dict(gym_years=0),
        dict(mobility="Limited"),
        dict(sleep=5),
    ],
)
def test_explosive_practice_withheld_without_supported_context(override):
    assert not any(
        e["category"] == "Explosive practice"
        for e in exercises(TrainingPlanService.generate(trained(**override)))
    )


def test_requested_power_is_supervised_and_not_in_deloads():
    plan = TrainingPlanService.generate(trained())
    assert any(e["category"] == "Explosive practice" for e in exercises(plan))
    for w in plan["weeks"]:
        for s in w["sessions"]:
            for e in s["exercises"]:
                if e["category"] == "Explosive practice":
                    assert e["coached"] and e["sets"] == 2 and not w["deload"]


@pytest.mark.parametrize(
    "override",
    [
        dict(sleep=5),
        dict(current_frequency=1),
        dict(age=17),
        dict(experience=[dict(discipline="Boxing", sessions=4)]),
    ],
)
def test_high_intensity_not_added_to_unsupported_or_busy_profiles(override):
    assert not any(
        e["catalog_id"] == "cycle-interval"
        for e in exercises(TrainingPlanService.generate(trained(**override)))
    )


def test_high_intensity_at_most_one_block_per_week_and_deload_omits_it():
    plan = TrainingPlanService.generate(trained())
    assert any(e["catalog_id"] == "cycle-interval" for e in exercises(plan))
    for w in plan["weeks"]:
        intervals = [
            e for s in w["sessions"] for e in s["exercises"] if e["catalog_id"] == "cycle-interval"
        ]
        assert len(intervals) <= 1
        if w["deload"]:
            assert not intervals
        assert all(e["block_minutes"] >= 9 and e["rpe"] == 7 for e in intervals)


def test_recent_session_fatigue_blocks_progression_with_fresh_good_checkin():
    p, plan, check, ex, logs = fixture()
    logs[-1]["fatigue"] = 8
    review = progression_review(plan, logs, p, check)
    assert review["recovery"]["status"] == "reduce"
    assert all(
        d["action"] not in {"increase_load", "increase_reps", "increase_duration"}
        for d in review["decisions"]
    )


def test_old_actual_performance_does_not_support_increase():
    p, plan, check, ex, logs = fixture()
    logs[0]["completed_on"] = (date.today() - timedelta(days=60)).isoformat()
    row = next(
        r
        for r in progression_review(plan, logs, p, check)["decisions"]
        if r["exercise"] == ex["name"]
    )
    assert row["action"] == "hold" and "28 days" in row["reason"]


def test_possible_plateau_holds_instead_of_mechanically_adding_volume():
    p, plan, check, ex, logs = fixture()
    third = deepcopy(logs[-1])
    third.update(session_id="w3-d0", completed_on=(date.today() - timedelta(days=1)).isoformat())
    row = next(
        r
        for r in progression_review(plan, [*logs, third], p, check)["decisions"]
        if r["exercise"] == ex["name"]
    )
    assert row["action"] == "hold" and "Possible plateau" in row["reason"]


def test_reassessment_keeps_approved_substitution_and_past_weeks():
    p, plan, check, _, _ = fixture()
    active = deepcopy(plan)
    for w in active["weeks"]:
        ex = w["sessions"][0]["exercises"][0]
        ex.update(name="Chair squat", catalog_id="chair-squat", suggested_load_kg=12)
    before = deepcopy(active)
    review = progression_review(active, [], p, check)
    result = adapt_future(plan, active, review, 4)
    assert result["weeks"][:4] == active["weeks"][:4]
    assert result["weeks"][4]["sessions"][0]["exercises"][0]["catalog_id"] == "chair-squat"
    assert result["weeks"][4]["sessions"][0]["exercises"][0]["suggested_load_kg"] == 12
    assert active == before


def test_reduced_availability_and_fatigue_remove_hard_blocks_without_changing_history():
    p = trained()
    active = TrainingPlanService.generate(p)
    revised = p.model_copy(update={"days": 2, "minutes": 20})
    candidate = TrainingPlanService.generate(revised)
    review = progression_review(active, [], revised, {"date": date.today().isoformat(), "sleep": 5})
    result = adapt_future(candidate, active, review, 4)
    assert result["weeks"][:4] == active["weeks"][:4]
    for w in result["weeks"][4:]:
        assert len(w["sessions"]) <= 2
        for s in w["sessions"]:
            assert s["effort"] <= 4 and s["minutes"] <= 20
            assert all(
                e["catalog_id"] != "cycle-interval" and e["category"] != "Explosive practice"
                for e in s["exercises"]
            )


def test_fatigue_logging_is_optional_and_bounded():
    assert WorkoutLog(session_id="w1-d0", minutes=30).fatigue is None
    assert WorkoutLog(session_id="w1-d0", minutes=30, fatigue=8).fatigue == 8
    with pytest.raises(ValueError):
        WorkoutLog(session_id="w1-d0", minutes=30, fatigue=11)


def test_shorter_availability_removes_blocks_that_no_longer_fit_even_with_good_recovery():
    p = trained()
    active = TrainingPlanService.generate(p)
    revised = p.model_copy(update={"minutes": 20})
    candidate = TrainingPlanService.generate(revised)
    review = progression_review(active, [], revised, {"date": date.today().isoformat(), "sleep": 8})
    result = adapt_future(candidate, active, review, 4)
    for w in result["weeks"][4:]:
        for s in w["sessions"]:
            assert sum(e["block_minutes"] for e in s["exercises"]) == pytest.approx(
                s["minutes"] - 10, abs=0.02
            )
            assert all(
                e["catalog_id"] != "cycle-interval" and e["category"] != "Explosive practice"
                for e in s["exercises"]
            )
            assert s["effort"] <= 6
