from copy import deepcopy
from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.athletics import athletic_assessment, discipline_priorities
from app.exercises import CATALOG, alternatives, available_equipment
from app.progression import adapt_future, progression_review, recovery_state
from app.schemas import ExerciseSet, Profile, WorkoutLog
from app.training import TrainingPlanService


def fixture():
    p = Profile(days=3, minutes=60, current_frequency=3, gym_years=2)
    plan = TrainingPlanService.generate(p)
    check = {
        "date": date.today().isoformat(),
        "sleep": 8,
        "fatigue": 3,
        "soreness": 2,
        "readiness": 4,
    }
    ex = plan["weeks"][0]["sessions"][0]["exercises"][0]
    logs = [
        {
            "record_id": str(i),
            "recorded_at": f"{date.today()}T1{i}:00:00",
            "completed_on": (date.today() - timedelta(days=2 if i == 0 else 0)).isoformat(),
            "session_id": f"w{i + 1}-d0",
            "minutes": 40,
            "effort": 5,
            "status": "completed",
            "performances": [
                {
                    "exercise_name": ex["name"],
                    "sets": [
                        {"reps": ex["rep_range"][1], "weight_kg": 20, "rpe": 5}
                        for _ in range(ex["sets"])
                    ],
                }
            ],
        }
        for i in range(2)
    ]
    return p, plan, check, ex, logs


def test_catalog_integrity_and_coverage():
    assert len(CATALOG) >= 35
    assert len({e["name"] for e in CATALOG.values()}) == len(CATALOG)
    assert {e["category"] for e in CATALOG.values()} == {
        "Strength",
        "Conditioning",
        "Athleticism",
        "Martial arts",
        "Mobility",
    }
    required = {
        "name",
        "movement_pattern",
        "muscles",
        "difficulty",
        "technique",
        "sets_guidance",
        "repetition_guidance",
        "common_mistakes",
        "modification_notes",
        "alternatives",
        "source_ids",
        "evidence_note",
    }
    for key, item in CATALOG.items():
        assert all(item[field] for field in required)
        assert all(alt in CATALOG and alt != key for alt in item["alternatives"])
    assert {
        "Squat",
        "Hip hinge",
        "Horizontal press",
        "Vertical press",
        "Horizontal pull",
        "Vertical pull",
        "Single leg",
        "Carry",
        "Trunk stabilization",
    } <= {e["movement_pattern"] for e in CATALOG.values()}
    assert CATALOG["mma"]["requires_coach"] and CATALOG["sprint"]["requires_coach"]


@pytest.mark.parametrize("days", range(1, 7))
@pytest.mark.parametrize("minutes", [20, 45, 90])
@pytest.mark.parametrize("equipment", [[], ["dumbbells", "bench", "bike"]])
def test_catalog_program_budget_and_equipment(days, minutes, equipment):
    p = Profile(days=days, minutes=minutes, equipment=equipment)
    plan = TrainingPlanService.generate(p)
    for week in plan["weeks"]:
        assert len(week["sessions"]) <= days
        for s in week["sessions"]:
            assert 0 < s["minutes"] <= minutes
            assert sum(e["block_minutes"] for e in s["exercises"]) == pytest.approx(
                s["minutes"] - 10, abs=0.01
            )
            for ex in s["exercises"]:
                item = CATALOG[ex["catalog_id"]]
                assert set(item["equipment"]) <= available_equipment(p)
                assert ex["rpe"] <= 6 and ex["progression_rule"] and ex["rest"]
                assert not item["requires_coach"]
    assert plan["weeks"][4]["sessions"][0]["minutes"] <= plan["weeks"][0]["sessions"][0]["minutes"]
    assert plan["weeks"][3]["sessions"][0]["minutes"] < plan["weeks"][0]["sessions"][0]["minutes"]


def test_equipment_filter_and_non_equivalent_alternative_notes():
    p = Profile(equipment=[])
    assert [e["id"] for e in alternatives("goblet-squat", p)] == ["chair-squat"]
    assert not alternatives("walk", p)
    assert "not equivalent" in CATALOG["prone-y"]["modification_notes"]
    plan = TrainingPlanService.generate(p.model_copy(update={"conditioning_mode": "rowing"}))
    assert all(
        ex["catalog_id"] != "row-erg"
        for w in plan["weeks"]
        for s in w["sessions"]
        for ex in s["exercises"]
    )


def test_strength_requires_actual_repeat_success_and_stable_load():
    p, plan, check, ex, logs = fixture()
    decision = progression_review(plan, logs, p, check)["decisions"][0]
    assert decision["action"] == "increase_load" and decision["target"] == 20.5
    changed = deepcopy(logs)
    changed[-1]["performances"][0]["sets"][0]["weight_kg"] = 22
    assert progression_review(plan, changed, p, check)["decisions"][0]["action"] == "hold"
    for log in logs:
        for actual in log["performances"][0]["sets"]:
            actual["reps"] = ex["rep_range"][0]
    decision = progression_review(plan, logs, p, check)["decisions"][0]
    assert decision["action"] == "increase_reps" and decision["target"] == ex["rep_range"][0] + 1


@pytest.mark.parametrize("status", ["failed", "missed"])
def test_failed_or_missed_exposure_prevents_progression(status):
    p, plan, check, _, logs = fixture()
    logs[-1]["status"] = status
    assert progression_review(plan, logs, p, check)["decisions"][0]["action"] == "hold"
    assert progression_review(plan, logs, p, check)["workload"][status] == 1


@pytest.mark.parametrize(
    "change", [{"fatigue": 8}, {"sleep": 5}, {"soreness": 8}, {"readiness": 1}]
)
def test_subjective_recovery_holds_progression(change):
    p, plan, check, _, logs = fixture()
    review = progression_review(plan, logs, p, {**check, **change})
    assert review["recovery"]["status"] == "reduce"
    assert all(d["action"] == "reduce" for d in review["decisions"])


def test_missing_effort_stale_context_and_no_actual_sets_are_not_success():
    p, plan, check, _, logs = fixture()
    assert progression_review(plan, logs[:1], p, check)["decisions"][0]["action"] == "hold"
    assert progression_review(plan, logs, p, None)["decisions"][0]["action"] == "hold"
    assert (
        recovery_state(p, {**check, "date": (date.today() - timedelta(days=15)).isoformat()})[
            "status"
        ]
        == "unknown"
    )
    for log in logs:
        log["effort"] = None
        for s in log["performances"][0]["sets"]:
            s["rpe"] = None
    assert progression_review(plan, logs, p, check)["decisions"][0]["action"] == "hold"
    assert progression_review(plan, logs, p, check)["workload"]["sessions_missing_rpe"] == 2


def test_conditioning_conservative_progression_and_future_only_changes():
    p, plan, check, _, _ = fixture()
    session = plan["weeks"][0]["sessions"][2]
    ex = next(e for e in session["exercises"] if e["category"] == "Conditioning")
    logs = [
        {
            "session_id": f"w{i + 1}-d4",
            "record_id": str(i),
            "recorded_at": f"{date.today()}T1{i}:00:00",
            "completed_on": (date.today() - timedelta(days=2 if i == 0 else 0)).isoformat(),
            "minutes": 40,
            "effort": 5,
            "status": "completed",
            "performances": [
                {
                    "exercise_name": ex["name"],
                    "sets": [{"duration_seconds": ex["block_minutes"] * 60, "rpe": 5}],
                }
            ],
        }
        for i in range(2)
    ]
    review = progression_review(plan, logs, p, check)
    assert (
        next(d for d in review["decisions"] if d["exercise"] == ex["name"])["action"]
        == "increase_duration"
    )
    result = adapt_future(plan, plan, review, 4)
    assert result["weeks"][:4] == plan["weeks"][:4]
    for old, new in zip(plan["weeks"][4:], result["weeks"][4:]):
        assert (
            sum(s["minutes"] for s in new["sessions"])
            <= sum(s["minutes"] for s in old["sessions"]) * 1.05 + 0.001
        )
        for s in new["sessions"]:
            assert s["minutes"] <= p.minutes
            assert sum(e["block_minutes"] for e in s["exercises"]) == pytest.approx(
                s["minutes"] - 10, abs=0.02
            )
    assert plan["weeks"][4]["sessions"][2]["minutes"] == 40  # input remains immutable


def test_assessment_separates_estimates_and_no_power_or_pro_norms():
    p = Profile(
        weight_kg=80,
        benchmarks=[
            {"name": "Squat", "unit": "kg", "value": 60, "reps": 5, "provenance": "measured"},
            {"name": "Vertical jump", "unit": "cm", "value": 30, "provenance": "estimated"},
        ],
    )
    assessment = athletic_assessment(p)
    assert len(assessment["observations"]) == len(assessment["estimates"]) == 1
    assert "0.75 x" in assessment["observations"][0]["derived"]
    assert "Explosive performance" in assessment["missing_domains"]
    assert "not a power measurement" in assessment["note"]


def test_discipline_access_interests_goals_and_enjoyment():
    p = Profile(
        goal="Improve Wrestling",
        experience=[
            {
                "discipline": "Wrestling",
                "months": 12,
                "sessions": 2,
                "enjoyment": 5,
                "weaknesses": "Entries",
                "instructor": True,
            }
        ],
    )
    rows = discipline_priorities(p)
    assert rows[0]["discipline"] == "Wrestling"
    assert "Recorded instructor" in rows[0]["access"]
    no_access = TrainingPlanService.generate(
        p.model_copy(update={"mma_gym": False, "equipment": []})
    )
    assert all(
        not e.get("coached")
        for w in no_access["weeks"]
        for s in w["sessions"]
        for e in s["exercises"]
    )


def test_richer_log_validation():
    assert ExerciseSet(distance_m=100, rpe=6).distance_m == 100
    assert WorkoutLog(session_id="w1-d0", minutes=20).effort is None
    for bad in ({"reps": 8, "rpe": 11}, {"distance_m": -1}, {"weight_kg": 20}):
        with pytest.raises(ValidationError):
            ExerciseSet(**bad)


def test_same_day_duplicate_efforts_do_not_support_progression():
    p, plan, check, _, logs = fixture()
    logs[0]["completed_on"] = logs[1]["completed_on"]
    decision = progression_review(plan, logs, p, check)["decisions"][0]
    assert decision["action"] == "hold" and "separate dates" in decision["reason"]


def test_youth_progression_is_referred_to_qualified_coach():
    p, plan, check, _, logs = fixture()
    review = progression_review(plan, logs, p.model_copy(update={"age": 17}), check)
    assert all(d["action"] == "hold" for d in review["decisions"])
    assert "youth coach" in review["decisions"][0]["reason"]


def test_changed_strength_protocol_does_not_inherit_advanced_load():
    p, plan, check, _, logs = fixture()
    review = progression_review(plan, logs, p, check)
    beginner = TrainingPlanService.generate(p.model_copy(update={"gym_years": 0}))
    adapted = adapt_future(beginner, plan, review, 4)
    assert all(
        "suggested_load_kg" not in e
        for w in adapted["weeks"][4:]
        for se in w["sessions"]
        for e in se["exercises"]
    )


def test_held_progression_never_inherits_profile_time_or_effort_increase():
    p = Profile(days=3, minutes=60, current_frequency=0, gym_years=0)
    plan = TrainingPlanService.generate(p)
    requested = p.model_copy(update={"current_frequency": 3, "intensity": "Challenging"})
    check = {"date": date.today().isoformat(), "sleep": 8, "fatigue": 3}
    logs = [
        {
            "session_id": "w1-d0",
            "minutes": 20,
            "effort": 9,
            "status": "failed",
            "completed_on": date.today().isoformat(),
        }
    ]
    review = progression_review(plan, logs, requested, check)
    result = adapt_future(TrainingPlanService.generate(requested), plan, review, 4)
    for old, new in zip(plan["weeks"][4:], result["weeks"][4:]):
        assert len(old["sessions"]) == len(new["sessions"])
        for before, after in zip(old["sessions"], new["sessions"]):
            assert after["minutes"] <= before["minutes"]
            assert after["effort"] <= before["effort"]
            assert sum(e["block_minutes"] for e in after["exercises"]) == pytest.approx(
                after["minutes"] - 10, abs=0.02
            )
            assert all("suggested_load_kg" not in e for e in after["exercises"])


def test_existing_class_disciplines_are_allocated_separately():
    p = Profile(
        days=4,
        experience=[
            {"discipline": "Boxing", "months": 18, "sessions": 2, "instructor": True},
            {"discipline": "BJJ", "months": 6, "sessions": 1, "instructor": True},
        ],
    )
    plan = TrainingPlanService.generate(p)
    technical = [
        ex["catalog_id"]
        for session in plan["weeks"][0]["sessions"]
        for ex in session["exercises"]
        if ex["category"] == "Martial arts"
    ]
    assert technical == ["boxing", "boxing", "bjj"]
    assert len(plan["weeks"][0]["sessions"]) == 4
