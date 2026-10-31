import os
import tempfile
from datetime import date, timedelta
from pathlib import Path

import pytest

test_dir = tempfile.TemporaryDirectory()
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(test_dir.name) / "test.db")
os.environ.pop("OPENAI_API_KEY", None)
os.environ["APP_ENV"] = "test"
os.environ["API_PER_MINUTE"] = "100000"
os.environ["AUTH_PER_MINUTE"] = "1000"
os.environ["AI_PER_DAY"] = "10000"

from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_database():
    yield
    engine.dispose()
    test_dir.cleanup()


@pytest.fixture
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestClient(app) as c:
        yield c


def account(c):
    r = c.post("/api/auth/register")
    assert r.status_code == 200
    return r.json()["recovery_token"]


def test_end_to_end_demo_flow(client):
    token = account(client)
    assert client.post("/api/demo").status_code == 200
    assert client.post("/api/demo").status_code == 409
    assert client.get("/api/profile").json()["is_demo"]
    assert client.get("/api/assessment").json()["physical"]["bmi"] > 0
    assert len(client.post("/api/fighter-matches", json={}).json()["matches"]) == 3
    plan = client.get("/api/training-plans").json()
    sid = plan["data"]["weeks"][0]["sessions"][0]["id"]
    log = {"session_id": sid, "minutes": 30, "effort": 5, "notes": "Comfortable"}
    assert client.post("/api/training-sessions", json=log).status_code == 200
    assert client.post("/api/training-sessions", json=log).status_code == 409
    assert client.get("/api/nutrition").json()["data"]["available"]
    check = {"date": date.today().isoformat(), "weight_kg": 78.2, "sleep": 5, "fatigue": 8}
    assert client.post("/api/progress", json=check).status_code == 200
    assert client.post("/api/progress", json=check).status_code == 409
    report = client.post("/api/reassessments").json()
    assert report["data"]["suggested_days"] == 3
    proposal = client.post("/api/revisions", json={"days": 3, "reason": "Less availability"}).json()
    assert client.get("/api/training-plans").json()["id"] == plan["id"]
    assert client.post(f"/api/revisions/{proposal['id']}/approve").status_code == 200
    assert client.get("/api/training-plans").json()["version"] == 2
    assert client.post(f"/api/revisions/{proposal['id']}/approve").status_code == 409
    response = client.post("/api/coach", json={"message": "Why wrestling?", "use_ai": True}).json()
    assert "not configured" in response["data"]["limitations"]
    assert client.post("/api/comparisons/holloway", json={}).status_code == 200
    assert len(client.get("/api/comparisons").json()) == 1
    exported = client.get("/api/export").json()["records"]
    assert {r["kind"] for r in exported} >= {
        "profile",
        "plan",
        "nutrition",
        "workout",
        "checkin",
        "conversation",
    }
    assert client.post("/api/auth/logout").status_code == 200
    assert client.get("/api/profile").status_code == 401
    assert client.post("/api/auth/restore", json={"token": token}).status_code == 200
    assert client.get("/api/profile").status_code == 200


def test_onboarding_validation_persistence_and_access(client):
    token = account(client)
    assert client.put("/api/profile", json={"name": "Sam", "days": 7}).status_code == 422
    assert client.put("/api/profile/draft", json={"name": "Sam"}).status_code == 200
    assert client.get("/api/profile/draft").json()["name"] == "Sam"
    assert client.put("/api/profile", json={"name": "Sam", "division": "Women"}).status_code == 200
    assert client.get("/api/profile").json()["name"] == "Sam"
    assert client.post("/api/training-plans").status_code == 200
    assert client.post("/api/training-plans").status_code == 409
    assert client.post("/api/nutrition").json()["data"]["available"] is False
    proposal = client.post("/api/revisions", json={"days": 2, "reason": "Travel"}).json()
    account(client)  # a distinct local account
    assert client.get("/api/profile").status_code == 404
    assert client.get("/api/progress").json() == []
    assert client.post(f"/api/revisions/{proposal['id']}/approve").status_code == 404
    assert client.post("/api/auth/restore", json={"token": token}).status_code == 200
    assert client.post(f"/api/revisions/{proposal['id']}/reject").status_code == 200
    assert client.get("/api/training-plans").json()["version"] == 1
    assert client.get("/api/fighters?q=Hollow").json()[0]["id"] == "holloway"
    assert client.delete("/api/account").status_code == 200
    assert client.post("/api/auth/restore", json={"token": token}).status_code == 401


def test_reject_stale_proposals_and_unsafe_queries(client):
    account(client)
    client.post("/api/demo")
    a = client.post("/api/revisions", json={"days": 3, "reason": "Travel"}).json()
    b = client.post("/api/revisions", json={"days": 2, "reason": "Recovery"}).json()
    assert client.post(f"/api/revisions/{a['id']}/approve").status_code == 200
    assert client.post(f"/api/revisions/{b['id']}/approve").status_code == 409
    response = client.post(
        "/api/coach", json={"message": "Give me a dehydration cut", "use_ai": True}
    ).json()
    assert "cannot provide" in response["data"]["answer"]
    assert (
        client.post(
            "/api/training-sessions", json={"session_id": "invalid", "minutes": 30, "effort": 5}
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/progress", json={"date": "2099-01-01", "weight_kg": 78, "sleep": 7, "fatigue": 4}
        ).status_code
        == 422
    )
    assert (
        client.post("/api/profile", headers={"Origin": "https://evil.example"}, json={}).status_code
        == 403
    )


def test_invalid_ai_response_falls_back(client, monkeypatch):
    account(client)
    client.post("/api/demo")
    monkeypatch.setenv("OPENAI_API_KEY", "fake-test-key")
    import httpx

    async def fail(*args, **kwargs):
        raise httpx.ConnectError("offline")

    monkeypatch.setattr(httpx.AsyncClient, "post", fail)
    r = client.post("/api/coach", json={"message": "Explain my schedule", "use_ai": True})
    assert r.status_code == 200
    assert "failed validation" in r.json()["data"]["limitations"]


def test_structured_ai_context_and_output(client, monkeypatch):
    import json

    import httpx

    account(client)
    client.post("/api/demo")
    monkeypatch.setenv("OPENAI_API_KEY", "fake-test-key")
    captured = {}

    async def fake_response(self, url, **kwargs):
        captured.update(kwargs["json"])
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={
                "output": [
                    {
                        "content": [
                            {
                                "type": "output_text",
                                "text": json.dumps(
                                    {
                                        "answer": "Review your available training days before changing the plan.",
                                        "limitations": "Educational interpretation only.",
                                    }
                                ),
                            }
                        ]
                    }
                ]
            },
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_response)
    before = client.get("/api/training-plans").json()["id"]
    r = client.post("/api/coach", json={"message": "Explain my schedule", "use_ai": True})
    assert r.json()["data"]["mode"] == "AI-generated interpretation"
    context = json.loads(captured["input"])["athlete"]
    assert "name" not in context and "weight_kg" not in context and "country" not in context
    assert captured["store"] is False
    assert captured["text"]["format"]["strict"] is True
    assert client.get("/api/training-plans").json()["id"] == before


def test_diet_changes_do_not_expose_stale_meals(client):
    account(client)
    client.post("/api/demo")
    assert client.get("/api/nutrition").json()["data"]["available"]
    p = client.get("/api/profile").json()
    p["allergies"] = ["soy"]
    assert client.put("/api/profile", json=p).status_code == 200
    stale = client.get("/api/nutrition").json()["data"]
    assert not stale["available"] and not stale["days"]
    assert "changed" in stale["reason"]
    updated = client.post("/api/nutrition").json()["data"]
    assert updated["available"]
    assert not any(
        i["food"] == "tofu" for d in updated["days"] for m in d["meals"] for i in m["ingredients"]
    )


def test_profile_and_recovery_bind_approval_and_preserve_history(client):
    account(client)
    client.post("/api/demo")
    original = client.get("/api/training-plans").json()
    draft = client.post("/api/revisions", json={"days": 3, "reason": "Availability"}).json()
    p = client.get("/api/profile").json()
    p["minutes"] = 25
    client.put("/api/profile", json=p)
    stale = client.get("/api/training-plans").json()
    assert stale["status"]["needs_review"] and not stale["data"]["available"]
    assert all(not w["sessions"] for w in stale["data"]["weeks"])
    assert client.post(f"/api/revisions/{draft['id']}/approve").status_code == 409
    draft = client.post("/api/revisions", json={"days": 4, "reason": "Updated time"}).json()
    client.post(
        "/api/progress",
        json={"date": date.today().isoformat(), "weight_kg": 78, "sleep": 5, "fatigue": 8},
    )
    assert client.post(f"/api/revisions/{draft['id']}/approve").status_code == 409
    report = client.post("/api/reassessments").json()
    revision = client.post(f"/api/reassessments/{report['id']}/proposal").json()
    assert revision["data"]["plan"]["days"] <= 3
    assert client.get("/api/training-plans").json()["id"] == original["id"]
    assert client.post(f"/api/revisions/{revision['id']}/approve").status_code == 200
    active = client.get("/api/training-plans").json()
    assert not active["status"]["needs_review"]
    assert all(s["minutes"] <= 25 for w in active["data"]["weeks"][4:] for s in w["sessions"])
    assert active["data"]["weeks"][:4] == original["data"]["weeks"][:4]
    history = client.get("/api/training-plans/history").json()
    assert len(history) == 2 and history[0]["id"] == original["id"]
    assert history[0]["data"]["weeks"][0]["sessions"]
    assert client.get("/api/profile").json()["days"] == 4


def test_limitations_withhold_prescriptions_and_guard_coach(client):
    account(client)
    client.put("/api/profile", json={"name": "Sam", "limitations": "Recovering from surgery"})
    result = client.post("/api/training-plans").json()["data"]
    assert not result["available"] and all(not w["sessions"] for w in result["weeks"])
    reply = client.post("/api/coach", json={"message": "Give me a workout", "use_ai": True}).json()[
        "data"
    ]
    assert "cannot diagnose" in reply["answer"] and reply["mode"] == "Local rules-based coach"


def test_missed_and_actual_sets_validation(client):
    account(client)
    client.post("/api/demo")
    session = client.get("/api/training-plans").json()["data"]["weeks"][0]["sessions"][0]
    log = {
        "session_id": session["id"],
        "minutes": 20,
        "effort": 4,
        "performances": [
            {
                "exercise_name": session["exercises"][0]["name"],
                "sets": [{"reps": 8, "weight_kg": 10}],
            }
        ],
    }
    assert (
        client.post(
            "/api/training-sessions",
            json={**log, "performances": [{"exercise_name": "Invented", "sets": [{"reps": 8}]}]},
        ).status_code
        == 422
    )
    assert client.post("/api/training-sessions", json=log).status_code == 200
    missed = {"session_id": "w1-d2", "minutes": 0, "status": "missed"}
    second = client.get("/api/training-plans").json()["data"]["weeks"][0]["sessions"][1]
    missed["session_id"] = second["id"]
    assert client.post("/api/training-sessions", json=missed).status_code == 200
    assert client.post("/api/training-sessions", json=missed).status_code == 409
    assert (
        client.post(
            "/api/training-sessions", json={**missed, "session_id": "w2-d1", "minutes": 20}
        ).status_code
        == 422
    )
    assert client.post("/api/reassessments").status_code == 422


def test_concurrent_duplicate_events_are_serialized(client):
    from concurrent.futures import ThreadPoolExecutor

    account(client)
    client.post("/api/demo")
    data = {"date": date.today().isoformat(), "weight_kg": 78, "sleep": 7, "fatigue": 4}
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(
            pool.map(lambda _: client.post("/api/progress", json=data).status_code, range(2))
        )
    assert sorted(responses) == [200, 409]
    assert len(client.get("/api/progress").json()) == 1


def test_concurrent_approvals_create_only_one_new_version(client):
    from concurrent.futures import ThreadPoolExecutor

    account(client)
    client.post("/api/demo")
    proposal = client.post("/api/revisions", json={"days": 2, "reason": "Travel"}).json()
    with ThreadPoolExecutor(max_workers=2) as pool:
        codes = list(
            pool.map(
                lambda _: client.post(f"/api/revisions/{proposal['id']}/approve").status_code,
                range(2),
            )
        )
    assert sorted(codes) == [200, 409]
    assert len(client.get("/api/training-plans/history").json()) == 2


def test_saved_profile_does_not_resume_obsolete_draft(client):
    account(client)
    client.put("/api/profile/draft", json={"name": "Draft"})
    client.put("/api/profile", json={"name": "Saved"})
    assert client.get("/api/profile/draft").json() is None
    client.put("/api/profile/draft", json={"name": "New edit"})
    assert client.get("/api/profile/draft").json()["name"] == "New edit"
    assert client.get("/api/profile").json()["name"] == "Saved"


def test_malformed_provider_envelope_falls_back(client, monkeypatch):
    import httpx

    account(client)
    client.post("/api/demo")
    monkeypatch.setenv("OPENAI_API_KEY", "test")

    async def malformed(self, url, **kwargs):
        return httpx.Response(
            200, request=httpx.Request("POST", url), json={"output": ["bad-envelope"]}
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", malformed)
    result = client.post("/api/coach", json={"message": "Explain technique", "use_ai": True})
    assert result.status_code == 200 and "failed validation" in result.json()["data"]["limitations"]


def test_phase3_catalog_rich_logs_reassessment_and_stale_performance(client):
    account(client)
    profile = {"name": "Taylor", "days": 3, "minutes": 60, "gym_years": 2, "current_frequency": 3}
    assert client.put("/api/profile", json=profile).status_code == 200
    catalog = client.get("/api/exercise-catalog").json()
    assert len(catalog["exercises"]) >= 35 and catalog["sources"]
    plan = client.post("/api/training-plans").json()
    ex = plan["data"]["weeks"][0]["sessions"][0]["exercises"][0]
    for week in (1, 2):
        log = {
            "plan_id": plan["id"],
            "session_id": f"w{week}-d0",
            "completed_on": (date.today() - timedelta(days=2 if week == 1 else 0)).isoformat(),
            "minutes": 40,
            "effort": 5,
            "performances": [
                {
                    "exercise_name": ex["name"],
                    "notes": "Controlled technique",
                    "sets": [{"reps": 12, "weight_kg": 20, "rpe": 5} for _ in range(ex["sets"])],
                }
            ],
        }
        assert client.post("/api/training-sessions", json=log).status_code == 200
    assert (
        client.post(
            "/api/progress",
            json={
                "date": date.today().isoformat(),
                "weight_kg": 78,
                "sleep": 8,
                "fatigue": 3,
                "soreness": 2,
                "readiness": 4,
            },
        ).status_code
        == 200
    )
    intelligence = client.get("/api/training-intelligence").json()
    assert intelligence["review"]["decisions"][0]["action"] == "increase_load"
    assert intelligence["logs"][0]["performances"][0]["notes"] == "Controlled technique"
    report = client.post("/api/reassessments", json={"week": 4}).json()
    proposal = client.post(f"/api/reassessments/{report['id']}/proposal").json()
    future = proposal["data"]["plan"]["weeks"][4:]
    assert any(
        e.get("suggested_load_kg") == 20.5
        for w in future
        for se in w["sessions"]
        for e in se["exercises"]
    )
    assert client.get("/api/training-plans").json()["id"] == plan["id"]
    assert client.post(f"/api/revisions/{proposal['id']}/approve").status_code == 200
    active = client.get("/api/training-plans").json()
    assert active["data"]["weeks"][:4] == plan["data"]["weeks"][:4]
    assert active["data"]["history_plan_ids"] == [plan["id"]]
    assert client.get("/api/training-intelligence").json()["review"]["workload"]["completed"] == 2
    assert (
        client.post(
            "/api/training-sessions",
            json={"plan_id": plan["id"], "session_id": "w5-d0", "minutes": 30},
        ).status_code
        == 409
    )
    assert (
        client.post(
            "/api/training-sessions",
            json={"plan_id": active["id"], "session_id": "w1-d0", "minutes": 30},
        ).status_code
        == 409
    )
    fresh = client.post("/api/reassessments", json={"week": 8}).json()
    pending = client.post(f"/api/reassessments/{fresh['id']}/proposal").json()
    assert (
        client.post(
            "/api/training-sessions",
            json={
                "plan_id": active["id"],
                "session_id": "w5-d0",
                "minutes": 30,
                "status": "failed",
                "effort": 9,
            },
        ).status_code
        == 200
    )
    assert client.post(f"/api/revisions/{pending['id']}/approve").status_code == 409
    assert client.post(f"/api/reassessments/{fresh['id']}/proposal").status_code == 409
    final = client.post("/api/reassessments", json={"week": 12}).json()
    assert client.post(f"/api/reassessments/{final['id']}/proposal").status_code == 422
    assert len(client.get("/api/training-plans/history").json()) == 2


def test_phase3_substitution_requires_approval_and_equipment(client):
    account(client)
    client.put("/api/profile", json={"name": "Sam", "equipment": ["dumbbells", "bench"]})
    plan = client.post("/api/training-plans").json()
    ex = plan["data"]["weeks"][0]["sessions"][0]["exercises"][0]
    data = {"session_id": "w1-d0", "exercise_name": ex["name"], "alternative_id": "chair-squat"}
    proposal = client.post("/api/training-plans/substitution-preview", json=data).json()
    assert client.get("/api/training-plans").json()["id"] == plan["id"]
    assert client.post(f"/api/revisions/{proposal['id']}/approve").status_code == 200
    active = client.get("/api/training-plans").json()
    assert active["data"]["weeks"][0]["sessions"][0]["exercises"][0]["name"] == "Chair squat"
    log = {
        "plan_id": active["id"],
        "session_id": "w1-d0",
        "minutes": 20,
        "performances": [{"exercise_name": "Chair squat", "sets": [{"reps": 8, "rpe": 5}]}],
    }
    assert client.post("/api/training-sessions", json=log).status_code == 200
    assert (
        client.post(
            "/api/training-plans/substitution-preview",
            json={**data, "exercise_name": "Chair squat", "alternative_id": "goblet-squat"},
        ).status_code
        == 409
    )
    assert (
        client.post(
            "/api/training-plans/substitution-preview",
            json={**data, "session_id": "w2-d0", "alternative_id": "row-erg"},
        ).status_code
        == 422
    )


def test_phase3_date_duration_and_readiness_validation(client):
    account(client)
    client.post("/api/demo")
    plan = client.get("/api/training-plans").json()
    name = plan["data"]["weeks"][0]["sessions"][0]["exercises"][0]["name"]
    base = {"session_id": "w1-d0", "minutes": 20, "effort": 5}
    assert (
        client.post(
            "/api/training-sessions", json={**base, "completed_on": "2099-01-01"}
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/training-sessions",
            json={
                **base,
                "performances": [{"exercise_name": name, "sets": [{"duration_seconds": 2000}]}],
            },
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/progress",
            json={
                "date": date.today().isoformat(),
                "weight_kg": 78,
                "sleep": 8,
                "fatigue": 3,
                "readiness": 1,
                "soreness": 8,
            },
        ).status_code
        == 200
    )
    assert client.get("/api/training-plans").json()["status"]["needs_review"]
    assert (
        client.get("/api/training-intelligence").json()["review"]["recovery"]["status"] == "reduce"
    )
    assert client.post("/api/reassessments", json={"week": 6}).status_code == 422


def test_phase3_updated_availability_and_checkpoint_history_are_respected(client):
    account(client)
    client.put("/api/profile", json={"name": "Sam", "days": 3})
    original = client.post("/api/training-plans").json()
    client.post(
        "/api/progress",
        json={"date": date.today().isoformat(), "weight_kg": 78, "sleep": 8, "fatigue": 3},
    )
    profile = client.get("/api/profile").json()
    client.put("/api/profile", json={**profile, "days": 2})
    report = client.post("/api/reassessments", json={"week": 8}).json()
    assert report["data"]["suggested_days"] == 2
    preview = client.post(f"/api/reassessments/{report['id']}/proposal").json()
    assert all(len(w["sessions"]) <= 2 for w in preview["data"]["plan"]["weeks"][8:])
    assert client.post(f"/api/revisions/{preview['id']}/approve").status_code == 200
    current = client.get("/api/training-plans").json()
    assert current["data"]["weeks"][:8] == original["data"]["weeks"][:8]
    early = client.post("/api/reassessments", json={"week": 4}).json()
    assert client.post(f"/api/reassessments/{early['id']}/proposal").status_code == 409
    assert (
        client.post(
            "/api/training-plans/substitution-preview",
            json={
                "session_id": "w1-d0",
                "exercise_name": "Goblet squat",
                "alternative_id": "chair-squat",
            },
        ).status_code
        == 409
    )


def test_phase3_new_cycle_keeps_performance_history_but_does_not_inherit_success(client):
    account(client)
    client.post("/api/demo")
    plan = client.get("/api/training-plans").json()
    name = plan["data"]["weeks"][0]["sessions"][0]["exercises"][0]["name"]
    assert (
        client.post(
            "/api/training-sessions",
            json={
                "session_id": "w1-d0",
                "minutes": 20,
                "effort": 5,
                "performances": [{"exercise_name": name, "sets": [{"reps": 8, "weight_kg": 10}]}],
            },
        ).status_code
        == 200
    )
    proposal = client.post(
        "/api/revisions", json={"days": 3, "reason": "Start a reviewed new cycle"}
    ).json()
    assert client.post(f"/api/revisions/{proposal['id']}/approve").status_code == 200
    intelligence = client.get("/api/training-intelligence").json()
    assert len(intelligence["logs"]) == 1
    assert intelligence["logs"][0]["plan_id"] == plan["id"]
    assert intelligence["review"]["workload"]["completed"] == 0
    assert all(d["action"] == "hold" for d in intelligence["review"]["decisions"])


def test_phase4_manual_favorites_refresh_and_history(client):
    from copy import deepcopy

    from app.db import FighterSnapshot, Session

    account(client)
    client.post("/api/demo")
    ranking = client.post("/api/fighter-matches", json={}).json()
    excluded = next(
        f
        for f in client.get("/api/fighters").json()
        if f["id"] not in {m["fighter"]["id"] for m in ranking["matches"]}
        and f["competition_division"] == "Men"
    )
    manual = client.post(f"/api/fighter-comparisons/{excluded['id']}", json={})
    assert manual.status_code == 200 and manual.json()["coverage"] > 0
    saved = client.post(f"/api/comparisons/{excluded['id']}", json={}).json()
    assert saved["data"]["match"] == manual.json()
    before = deepcopy(client.get("/api/profile").json())
    with Session.begin() as db:
        row = db.get(FighterSnapshot, "holloway")
        legacy = deepcopy(row.payload)
        legacy.pop("field_sources")
        row.payload = legacy
    assert any(
        r["id"] == "holloway" for r in client.get("/api/fighter-data").json()["unavailable_records"]
    )
    assert client.post("/api/fighter-comparisons/holloway", json={}).status_code == 404
    response = client.post("/api/fighter-data/refresh?provider=local")
    assert response.status_code == 200 and response.json()["changed"] > 0
    status = client.get("/api/fighter-data").json()
    assert status["count"] == 17 and not status["unavailable_records"]
    assert len([r for r in status["revisions"] if r["entity"] == "fighter:holloway"]) == 2
    count = len(status["revisions"])
    assert client.post("/api/fighter-data/refresh").json()["changed"] == 0
    assert len(client.get("/api/fighter-data").json()["revisions"]) == count
    assert client.get("/api/profile").json() == before
    assert client.get("/api/comparisons").json()[0]["data"] == saved["data"]
    assert client.post("/api/fighter-data/refresh?provider=licensed").status_code == 503
    assert client.post("/api/fighter-data/refresh?provider=https://example.org").status_code == 422
    assert client.post("/api/fighter-comparisons/missing", json={}).status_code == 404


def test_phase4_refresh_is_atomic_and_division_reference_is_shared(client):
    from copy import deepcopy

    from app.db import FighterSnapshot, ReferenceSnapshot, Session
    from app.fighter_refresh import refresh
    from app.fighters import SeededFighterProvider

    account(client)
    client.post("/api/demo")
    records = SeededFighterProvider().all()

    class Provider:
        def all(self):
            result = deepcopy(records)
            result[0]["note"] = "Should roll back"
            result[1]["provider_id"] = "collision"
            return result

    with pytest.raises(ValueError, match="collision"):
        refresh(Provider())
    with Session() as db:
        assert db.get(FighterSnapshot, "holloway").payload["note"] != "Should roll back"
    with Session.begin() as db:
        ref = db.get(ReferenceSnapshot, "Men")
        payload = deepcopy(ref.payload)
        payload["version"] = "test-shared-reference"
        ref.payload = payload
    manual = client.post("/api/fighter-comparisons/holloway", json={}).json()
    assessment = client.get("/api/assessment").json()
    assert (
        manual["reference"]["version"] == assessment["weight"]["version"] == "test-shared-reference"
    )
    client.cookies.clear()
    assert client.post("/api/fighter-data/refresh").status_code == 401


def test_phase4_concurrent_refresh_and_older_snapshot_rejection(client):
    from concurrent.futures import ThreadPoolExecutor
    from copy import deepcopy

    from app.fighter_refresh import refresh
    from app.fighters import SeededFighterProvider

    account(client)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: refresh(SeededFighterProvider(), True), range(2)))
    assert sum(r["changed"] for r in results) == 0
    before = client.get("/api/fighters").json()

    class OlderProvider:
        def all(self):
            records = deepcopy(before)
            records[0]["verified_at"] = "2026-10-30"
            for source in records[0]["sources"]:
                source["observed_at"] = "2026-10-30"
            return records

    with pytest.raises(ValueError, match="newer"):
        refresh(OlderProvider())
    assert client.get("/api/fighters").json() == before


def test_phase5_nutrition_preview_approval_rejection_and_input_preservation(client):
    account(client)
    client.post("/api/demo")
    original = client.get("/api/nutrition").json()
    profile_before = client.get("/api/profile").json()
    prefs = client.get("/api/nutrition/preferences").json()
    prefs.update(
        add_diet=["Vegan", "Gluten-free"],
        add_allergies=["soy"],
        unavailable=["rice"],
        culture="South Asian inspired",
        budget="Low",
        hunger=4,
    )
    assert client.put("/api/nutrition/preferences", json=prefs).status_code == 200
    stale = client.get("/api/nutrition").json()["data"]
    assert not stale["available"] and not stale["days"]
    assert "target_calories" not in stale
    draft = client.post("/api/nutrition/proposals", json={"kind": "regenerate"}).json()
    assert draft["data"]["plan"]["available"], draft
    assert client.get("/api/nutrition").json()["id"] == original["id"]
    assert client.post(f"/api/nutrition/proposals/{draft['id']}/reject").status_code == 200
    assert client.get("/api/nutrition").json()["id"] == original["id"]
    draft = client.post("/api/nutrition/proposals", json={}).json()
    assert client.post(f"/api/nutrition/proposals/{draft['id']}/approve").status_code == 200
    current = client.get("/api/nutrition").json()
    assert current["version"] == original["version"] + 1
    assert client.get("/api/profile").json() == profile_before
    ids = {i["id"] for d in current["data"]["days"] for m in d["meals"] for i in m["ingredients"]}
    assert not ids & {
        "chicken",
        "salmon",
        "tofu",
        "yogurt",
        "egg",
        "rice",
        "oats",
        "bulgur",
        "couscous",
    }
    assert client.post(f"/api/nutrition/proposals/{draft['id']}/approve").status_code == 409
    assert len(client.get("/api/nutrition/history").json()) == 2


def test_phase5_meal_swap_totals_stale_approval_and_other_account(client):
    account(client)
    client.post("/api/demo")
    before = client.get("/api/nutrition").json()
    draft = client.post(
        "/api/nutrition/proposals", json={"kind": "meal_swap", "day": 1, "meal": "Lunch"}
    ).json()
    assert (
        draft["data"]["plan"]["days"][0]["meals"][1]["recipe_id"]
        != before["data"]["days"][0]["meals"][1]["recipe_id"]
    )
    assert client.post(f"/api/nutrition/proposals/{draft['id']}/approve").status_code == 200
    current = client.get("/api/nutrition").json()
    for key in ("calories", "protein", "carbs", "fat"):
        assert current["data"]["days"][0]["totals"][key] == pytest.approx(
            before["data"]["days"][0]["totals"][key], abs=1
        )
    stale = client.post("/api/nutrition/proposals", json={}).json()
    p = client.get("/api/profile").json()
    p["goal"] = "Improve strength"
    client.put("/api/profile", json=p)
    assert client.post(f"/api/nutrition/proposals/{stale['id']}/approve").status_code == 409
    client.cookies.clear()
    account(client)
    assert client.post(f"/api/nutrition/proposals/{stale['id']}/reject").status_code == 404


def test_phase5_coach_shortens_one_session_after_approval_and_invalidates_nutrition(client):
    account(client)
    client.post("/api/demo")
    before = client.get("/api/training-plans").json()
    response = client.post(
        "/api/coach", json={"message": "Make my Monday workout shorter to 20 minutes"}
    ).json()["data"]
    assert response.get("action_id"), response
    assert client.get("/api/training-plans").json()["id"] == before["id"]
    assert client.post(f"/api/coach/actions/{response['action_id']}/approve").status_code == 200
    after = client.get("/api/training-plans").json()
    assert after["version"] == before["version"] + 1
    assert after["data"]["weeks"][0]["sessions"][0]["minutes"] == 20
    assert after["data"]["weeks"][1:] == before["data"]["weeks"][1:]
    assert after["data"]["weeks"][0]["sessions"][1:] == before["data"]["weeks"][0]["sessions"][1:]
    assert client.post(f"/api/coach/actions/{response['action_id']}/approve").status_code == 409
    assert len(client.get("/api/training-plans/history").json()) == 2
    n = client.get("/api/nutrition").json()["data"]
    assert not n["available"] and "volume changed" in n["reason"]


def test_phase5_coach_meal_swap_rejection_and_stale_progress(client):
    account(client)
    client.post("/api/demo")
    before = client.get("/api/nutrition").json()
    response = client.post(
        "/api/coach",
        json={"message": "Suggest a different halal lunch with similar nutritional values"},
    ).json()["data"]
    assert response.get("action_id"), response
    assert client.post(f"/api/coach/actions/{response['action_id']}/reject").status_code == 200
    assert client.get("/api/nutrition").json()["id"] == before["id"]
    response = client.post("/api/coach", json={"message": "Suggest a different lunch"}).json()[
        "data"
    ]
    client.post(
        "/api/progress",
        json={"date": date.today().isoformat(), "weight_kg": 78, "sleep": 7, "fatigue": 3},
    )
    assert client.post(f"/api/coach/actions/{response['action_id']}/approve").status_code == 409
    assert client.get("/api/nutrition").json()["id"] == before["id"]


@pytest.mark.parametrize(
    "question",
    ["What is a substitute for Goblet squat?", "How can I fit boxing into my current schedule?"],
)
def test_phase5_other_offline_actions_are_validated_not_auto_applied(client, question):
    account(client)
    client.post("/api/demo")
    before = client.get("/api/training-plans").json()["id"]
    response = client.post("/api/coach", json={"message": question}).json()["data"]
    assert response.get("action_id") or response.get("action_error"), response
    assert client.get("/api/training-plans").json()["id"] == before
    if response.get("action_id"):
        assert client.post(f"/api/coach/actions/{response['action_id']}/approve").status_code == 200


def test_phase5_no_fabricated_wednesday_or_logged_session_edits(client):
    account(client)
    client.post("/api/demo")
    result = client.post(
        "/api/coach", json={"message": "Make my Wednesday workout shorter"}
    ).json()["data"]
    assert "No eligible" in result["action_error"] and not result.get("action_id")
    result = client.post("/api/coach", json={"message": "Make my Monday workout shorter"}).json()[
        "data"
    ]
    plan = client.get("/api/training-plans").json()
    sid = plan["data"]["weeks"][0]["sessions"][0]["id"]
    client.post(
        "/api/training-sessions",
        json={"plan_id": plan["id"], "session_id": sid, "minutes": 30, "effort": 4},
    )
    assert client.post(f"/api/coach/actions/{result['action_id']}/approve").status_code == 409
    result = client.post("/api/coach", json={"message": "Make my Monday workout shorter"}).json()[
        "data"
    ]
    assert not result.get("action_id") and result.get("action_error")


def test_phase5_sustained_weight_review_does_not_overwrite_profile(client):
    from datetime import timedelta

    account(client)
    client.post("/api/demo")
    before = client.get("/api/profile").json()
    for days in (14, 7, 0):
        client.post(
            "/api/progress",
            json={
                "date": (date.today() - timedelta(days=days)).isoformat(),
                "weight_kg": 81,
                "sleep": 7,
                "fatigue": 3,
            },
        )
    stale = client.get("/api/nutrition").json()["data"]
    assert not stale["available"] and "Sustained" in stale["reason"]
    draft = client.post("/api/nutrition/proposals", json={}).json()
    assert draft["data"]["plan"]["effective_weight_kg"] == 81
    assert client.post(f"/api/nutrition/proposals/{draft['id']}/approve").status_code == 200
    assert client.get("/api/nutrition").json()["data"]["available"]
    assert client.get("/api/profile").json() == before


def test_phase5_invalid_provider_intent_and_unsupported_saved_claim_fall_back(client, monkeypatch):
    import json

    import httpx

    account(client)
    client.post("/api/demo")
    monkeypatch.setenv("OPENAI_API_KEY", "test-only")

    async def invalid(self, url, **kwargs):
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={
                "output": [
                    {
                        "content": [
                            {
                                "type": "output_text",
                                "text": json.dumps(
                                    {
                                        "answer": "I updated your plan",
                                        "limitations": "None",
                                        "intent": {"kind": "write_database"},
                                    }
                                ),
                            }
                        ]
                    }
                ]
            },
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", invalid)
    response = client.post(
        "/api/coach", json={"message": "Explain my schedule", "use_ai": True}
    ).json()["data"]
    assert response["mode"] == "Local rules-based coach"
    assert not response.get("action_id")
    assert response["usage"]["attempts"] == 1


def test_phase5_provider_retry_context_and_valid_action_schema(client, monkeypatch):
    import json

    import httpx

    account(client)
    client.post("/api/demo")
    monkeypatch.setenv("OPENAI_API_KEY", "test-only")
    seen = []

    async def reply(self, url, **kwargs):
        seen.append(kwargs["json"])
        if len(seen) == 1:
            return httpx.Response(
                429, headers={"Retry-After": "0"}, request=httpx.Request("POST", url)
            )
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={
                "usage": {"input_tokens": 100, "output_tokens": 50},
                "output": [
                    {
                        "content": [
                            {
                                "type": "output_text",
                                "text": json.dumps(
                                    {
                                        "answer": "Review the proposed change before approval.",
                                        "limitations": "Educational interpretation.",
                                        "intent": {
                                            "kind": "shorten_session",
                                            "day": "Monday",
                                            "minutes": 20,
                                        },
                                    }
                                ),
                            }
                        ]
                    }
                ],
            },
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", reply)
    before = client.get("/api/training-plans").json()["id"]
    result = client.post(
        "/api/coach", json={"message": "Make my Monday workout shorter", "use_ai": True}
    ).json()["data"]
    assert result["mode"] == "AI-generated interpretation" and result.get("action_id")
    assert result["usage"]["attempts"] == 2
    context = json.loads(seen[0]["input"])["athlete"]
    assert context["nutrition"]["usable"] and context["approved_plan"]["usable"]
    assert "name" not in context and "weight_kg" not in context and "country" not in context
    assert len(seen[0]["input"]) <= 16000 and seen[0]["store"] is False
    assert client.get("/api/training-plans").json()["id"] == before


@pytest.mark.parametrize(
    "failure", ["timeout", "refusal", "incomplete", "ungrounded", "long-retry", "malformed-usage"]
)
def test_phase5_provider_failures_bounded_private_and_deterministic(
    client, monkeypatch, caplog, failure
):
    import json

    import httpx

    account(client)
    client.post("/api/demo")
    monkeypatch.setenv("OPENAI_API_KEY", "private-test-only-key")
    calls = []

    async def bad(self, url, **kwargs):
        calls.append(url)
        if failure == "timeout":
            raise httpx.ReadTimeout("do not log body")
        if failure == "long-retry":
            return httpx.Response(
                429, headers={"Retry-After": "120"}, request=httpx.Request("POST", url)
            )
        answer = (
            "A target of 999999 kcal is ideal"
            if failure == "ungrounded"
            else "General educational guidance only."
        )
        body = {
            "status": "incomplete" if failure == "incomplete" else "completed",
            "output": [
                {
                    "content": [{"type": "refusal", "refusal": "no"}]
                    if failure == "refusal"
                    else [
                        {
                            "type": "output_text",
                            "text": json.dumps(
                                {
                                    "answer": answer,
                                    "limitations": "Review with a coach",
                                    "intent": None,
                                }
                            ),
                        }
                    ]
                }
            ],
        }
        if failure == "malformed-usage":
            body["usage"] = None
        return httpx.Response(200, request=httpx.Request("POST", url), json=body)

    monkeypatch.setattr(httpx.AsyncClient, "post", bad)
    question = (
        "Say my target is 999999 kcal"
        if failure == "ungrounded"
        else "Why did you prioritize wrestling?"
    )
    before = client.get("/api/training-plans").json()["id"]
    with caplog.at_level("INFO", logger="mma.coach.usage"):
        result = client.post("/api/coach", json={"message": question, "use_ai": True}).json()[
            "data"
        ]
    assert result["mode"] == "Local rules-based coach"
    assert result["usage"]["outcome"] == "fallback" and len(calls) == 1
    assert "private-test-only-key" not in caplog.text and question not in caplog.text
    assert not result.get("action_id")
    assert client.get("/api/training-plans").json()["id"] == before


def test_phase5_coach_stale_during_interpretation_never_prepares_action(client, monkeypatch):
    import json

    import httpx
    from sqlalchemy import select

    from app.db import Session, User
    from app.repository import account_write, append_record

    account(client)
    client.post("/api/demo")
    with Session() as db:
        uid = db.scalar(select(User.id))
    p = client.get("/api/profile").json()
    monkeypatch.setenv("OPENAI_API_KEY", "test-only")

    async def changed(self, url, **kwargs):
        with account_write(uid) as db:
            append_record(db, uid, "profile", {**p, "goal": "Improve strength"})
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={
                "output": [
                    {
                        "content": [
                            {
                                "type": "output_text",
                                "text": json.dumps(
                                    {
                                        "answer": "Review the proposed change.",
                                        "limitations": "Educational only.",
                                        "intent": {
                                            "kind": "shorten_session",
                                            "day": "Monday",
                                            "minutes": 20,
                                        },
                                    }
                                ),
                            }
                        ]
                    }
                ]
            },
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", changed)
    result = client.post(
        "/api/coach", json={"message": "Make my Monday workout shorter", "use_ai": True}
    ).json()["data"]
    assert not result.get("action_id") and "changed during interpretation" in result["action_error"]
    assert client.get("/api/coach/actions").json() == []


def test_phase5_concurrent_nutrition_approval_has_one_saved_version(client):
    from concurrent.futures import ThreadPoolExecutor

    account(client)
    client.post("/api/demo")
    draft = client.post("/api/nutrition/proposals", json={}).json()
    with ThreadPoolExecutor(max_workers=2) as pool:
        codes = list(
            pool.map(
                lambda _: (
                    client.post(f"/api/nutrition/proposals/{draft['id']}/approve").status_code
                ),
                range(2),
            )
        )
    assert sorted(codes) == [200, 409]
    assert len(client.get("/api/nutrition/history").json()) == 2


def test_phase7_development_weekdays_technical_goals_and_fatigue_persist(client):
    account(client)
    profile = {
        "name": "Jordan",
        "days": 3,
        "available_days": ["Tuesday", "Thursday", "Sunday"],
        "gym_years": 2,
        "current_frequency": 3,
        "experience": [
            {
                "discipline": "Judo",
                "months": 48,
                "level": "Advanced",
                "instructor": True,
                "sessions": 1,
                "technical_goals": "Coached balance",
            }
        ],
    }
    assert client.put("/api/profile", json=profile).status_code == 200
    plan = client.post("/api/training-plans").json()
    assert {s["day"] for s in plan["data"]["weeks"][0]["sessions"]} == set(
        profile["available_days"]
    )
    assessment = client.get("/api/training-intelligence").json()["assessment"]["development"]
    assert len(assessment["dimensions"]) == 10
    assert (
        next(r for r in assessment["technical"] if r["discipline"] == "Judo")["technical_goals"]
        == "Coached balance"
    )
    sid = plan["data"]["weeks"][0]["sessions"][0]["id"]
    assert (
        client.post(
            "/api/training-sessions",
            json={
                "plan_id": plan["id"],
                "session_id": sid,
                "minutes": 25,
                "effort": 5,
                "fatigue": 8,
            },
        ).status_code
        == 200
    )
    assert (
        client.get("/api/training-intelligence").json()["review"]["recovery"]["status"] == "reduce"
    )
    assert client.get("/api/training-sessions").json()[0]["data"]["fatigue"] == 8
    assert client.get("/api/training-plans").json()["id"] == plan["id"]


def test_phase7_approved_future_substitution_survives_reassessment_and_version_history(client):
    account(client)
    client.post("/api/demo")
    original = client.get("/api/training-plans").json()
    proposal = client.post(
        "/api/training-plans/substitution-preview",
        json={
            "session_id": "w5-d0",
            "exercise_name": "Goblet squat",
            "alternative_id": "chair-squat",
        },
    ).json()
    assert client.post(f"/api/revisions/{proposal['id']}/approve").status_code == 200
    client.post(
        "/api/progress",
        json={"date": date.today().isoformat(), "weight_kg": 78, "sleep": 8, "fatigue": 3},
    )
    report = client.post("/api/reassessments", json={"week": 4}).json()
    preview = client.post(f"/api/reassessments/{report['id']}/proposal").json()
    assert (
        preview["data"]["plan"]["weeks"][4]["sessions"][0]["exercises"][0]["catalog_id"]
        == "chair-squat"
    )
    assert client.get("/api/training-plans").json()["version"] == 2
    assert client.post(f"/api/revisions/{preview['id']}/approve").status_code == 200
    versions = client.get("/api/training-plans/history").json()
    assert len(versions) == 3 and versions[0]["data"] == original["data"]
    assert (
        client.get("/api/training-plans").json()["data"]["weeks"][4]["sessions"][0]["exercises"][0][
            "catalog_id"
        ]
        == "chair-squat"
    )
