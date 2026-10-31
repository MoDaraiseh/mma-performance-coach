import csv
import io
import json
import os
import sqlite3
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest
from sqlalchemy import event, select, text
from test_api import account
from test_api import client as api_client

from app.analytics import normalize, trend, window
from app.db import Record, Session, User, engine

client = api_client


@pytest.fixture(scope="session", autouse=True)
def close_focused_database():
    yield
    engine.dispose()


def seed(client):
    account(client)
    client.post("/api/demo")
    with Session() as db:
        return db.scalar(select(User.id))


def check(client, days_ago, load=40, run=500, weight=80):
    when = (date.today() - timedelta(days=days_ago)).isoformat()
    response = client.post(
        "/api/progress",
        json={
            "date": when,
            "weight_kg": weight,
            "sleep": 8,
            "fatigue": 3,
            "benchmarks": [
                {
                    "name": "Bench press",
                    "value": load,
                    "unit": "kg",
                    "reps": 5,
                    "effort": 7,
                    "provenance": "measured",
                },
                {
                    "name": "1km",
                    "value": run,
                    "unit": "seconds",
                    "reps": 1,
                    "effort": 7,
                    "provenance": "measured",
                },
            ],
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_trend_samples_span_direction_and_unchanged():
    def points(values, spacing=14):
        return [
            {
                "date": (
                    date.today() - timedelta(days=(len(values) - 1 - i) * spacing)
                ).isoformat(),
                "value": v,
            }
            for i, v in enumerate(values)
        ]

    assert trend([])["status"] == "missing"
    assert trend(points([40]))["status"] == "limited"
    assert trend(points([40, 50]))["status"] == "limited"
    assert trend(points([40, 45, 50]))["status"] == "improved"
    assert trend(points([500, 480, 450]), "lower")["status"] == "improved"
    assert trend(points([40, 40, 40]))["status"] == "unchanged"
    assert trend(points([40, 45, 40]))["status"] == "variable"
    assert trend(points([7, 8, 9]), "neutral")["status"] == "increased"


def test_unit_conversion_and_time_window_bounds():
    assert normalize(100, "lb")[0] == pytest.approx(45.359237)
    assert normalize(2, "minutes") == (120, "seconds")
    assert normalize(1, "m") == (100, "cm")
    with pytest.raises(ValueError):
        normalize(1, "cups")
    for a, b in [
        (date.today(), date.today() + timedelta(days=1)),
        (date.today(), date.today() - timedelta(days=1)),
        (date.today() - timedelta(days=3651), date.today()),
    ]:
        with pytest.raises(ValueError):
            window(a, b)


def test_empty_single_and_real_benchmark_comparisons(client):
    seed(client)
    empty = client.get("/api/analytics").json()
    assert empty["series"] == [] and empty["adherence"]["percent"] is None
    assert empty["profile_summary"]["weight_kg"] == 78
    check(client, 35, 40, 500)
    one = client.get("/api/analytics").json()
    assert all(s["trend"]["status"] == "limited" for s in one["series"])
    check(client, 21, 45, 480)
    check(client, 7, 50, 450)
    data = client.get("/api/analytics").json()
    strength = next(s for s in data["series"] if s["label"] == "Bench press")
    aerobic = next(s for s in data["series"] if s["label"] == "1km")
    relative = next(s for s in data["series"] if s["label"] == "Bench press relative load")
    assert strength["best"]["value"] == 50 and strength["trend"]["delta"] == 10
    assert aerobic["best"]["value"] == 450 and aerobic["trend"]["status"] == "improved"
    assert relative["best"]["value"] == 0.625
    assert data["nutrition_summary"]["usable"]  # only two weight check-ins are recent
    # A selected-period baseline never silently incorporates earlier profile data.
    filtered = client.get(
        f"/api/analytics?start={(date.today() - timedelta(days=22)).isoformat()}"
    ).json()
    assert (
        next(s for s in filtered["series"] if s["label"] == "Bench press")["trend"]["baseline"][
            "value"
        ]
        == 45
    )
    check(client, 0, 55, 430)
    stale = client.get("/api/analytics").json()["nutrition_summary"]
    assert not stale["usable"] and stale["target_calories"] is None


def test_protocol_evidence_and_deleted_corrected_records(client):
    seed(client)
    first = check(client, 28)
    second = check(client, 14, 50)
    with Session.begin() as db:
        row = db.get(Record, second["id"])
        row.payload = {
            **row.payload,
            "benchmarks": [
                {**row.payload["benchmarks"][0], "value": 55, "provenance": "estimated"}
            ],
        }
    data = client.get("/api/analytics").json()
    estimates = [s for s in data["series"] if s["kind"] == "estimate"]
    assert estimates and estimates[0]["best"]["value"] == 55
    actual = next(
        s for s in data["series"] if s["label"] == "Bench press" and s["kind"] == "benchmark"
    )
    assert actual["best"]["value"] == 40
    with Session.begin() as db:
        db.delete(db.get(Record, first["id"]))
    assert not any(s["kind"] == "benchmark" for s in client.get("/api/analytics").json()["series"])


def test_actual_sets_practice_and_calendar_adherence(client):
    seed(client)
    plan = client.get("/api/training-plans").json()
    monday = date.today() - timedelta(days=date.today().weekday() + 14)
    assert (
        client.post(
            "/api/analytics/schedule",
            json={"plan_id": plan["id"], "start_date": monday.isoformat()},
        ).status_code
        == 200
    )
    first = plan["data"]["weeks"][0]["sessions"][0]
    payload = {
        "plan_id": plan["id"],
        "session_id": first["id"],
        "completed_on": monday.isoformat(),
        "minutes": 30,
        "effort": 5,
        "practices": [{"discipline": "Boxing", "minutes": 15}],
        "performances": [
            {
                "exercise_name": first["exercises"][0]["name"],
                "sets": [{"reps": 8, "weight_kg": 40, "rpe": 5}],
            }
        ],
    }
    assert client.post("/api/training-sessions", json=payload).status_code == 200
    data = client.get("/api/analytics").json()
    assert data["adherence"]["planned"] > 1 and data["adherence"]["completed"] == 1
    assert data["martial_arts"]["minutes"] == [{"discipline": "Boxing", "minutes": 15}]
    records = [s for s in data["series"] if s["kind"] == "actual_set" and s["unit"] == "kg"]
    assert records[0]["best"]["value"] == 40
    assert not any(s["kind"] == "derived" for s in data["series"])  # no same-date weight
    invalid = {**payload, "practices": [{"discipline": "Boxing", "minutes": 31}]}
    assert client.post("/api/training-sessions", json=invalid).status_code == 422
    assert client.get("/api/training-plans").json()["id"] == plan["id"]


def test_export_pagination_privacy_and_technical_achievements(client):
    seed(client)
    check(client, 10)
    assert (
        client.post(
            "/api/analytics/achievements",
            json={
                "date": date.today().isoformat(),
                "discipline": "BJJ",
                "title": "Positional escape with coach",
                "notes": "private note",
            },
        ).status_code
        == 200
    )
    report = client.get("/api/analytics").json()
    assert report["achievements"][0]["evidence"].startswith("self-reported")
    export = client.get("/api/analytics/export.csv")
    assert export.status_code == 200 and export.headers["cache-control"] == "no-store"
    parsed = list(csv.DictReader(io.StringIO(export.text)))
    assert any(r["metric"] == "weight_kg" and r["value"] == "80.0" for r in parsed)
    assert "private note" not in export.text and "Alex Morgan" not in export.text
    assert client.get("/api/analytics/history?page_size=1").json()["total"] == 1
    assert client.get("/api/analytics/history?page=2&page_size=1").json()["items"] == []
    client.cookies.clear()
    assert client.get("/api/analytics/export.csv").status_code == 401
    account(client)
    assert client.get("/api/analytics").json()["coverage"]["total_events"] == 0
    assert client.get("/api/analytics/history").json()["total"] == 0


def test_large_history_is_bounded_indexed_and_full_export_streams(client):
    uid = seed(client)
    with Session.begin() as db:
        db.add_all(
            [
                Record(
                    id=f"history-{i}",
                    user_id=uid,
                    kind="checkin",
                    version=i + 1,
                    payload={
                        "date": (date.today() - timedelta(days=i)).isoformat(),
                        "weight_kg": 80,
                        "sleep": 8,
                        "fatigue": 3,
                        "benchmarks": [],
                    },
                )
                for i in range(2100)
            ]
        )
    start = (date.today() - timedelta(days=2200)).isoformat()
    statements = []

    def capture(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", capture)
    try:
        data = client.get(f"/api/analytics?start={start}").json()
    finally:
        event.remove(engine, "before_cursor_execute", capture)
    assert (
        data["coverage"]["loaded_events"] == 2000
        and data["coverage"]["total_events"] == 2100
        and data["coverage"]["truncated"]
    )
    assert max(len(s["points"]) for s in data["series"]) == 120
    assert len(statements) < 16
    with Session() as db:
        plan = db.execute(
            text(
                "EXPLAIN QUERY PLAN SELECT id FROM records WHERE user_id=:uid AND kind='checkin' AND event_date>=:start ORDER BY event_date DESC LIMIT 25"
            ),
            {"uid": uid, "start": start},
        ).all()
        assert "ix_record_history" in str(plan)
    raw = client.get(f"/api/analytics/export.csv?start={start}")
    assert len(list(csv.DictReader(io.StringIO(raw.text)))) == 2100 * 3


def test_history_migration_preserves_old_payloads(tmp_path):
    path = tmp_path / "legacy.db"
    env = {**os.environ, "DATABASE_URL": "sqlite:///" + str(path)}

    def migrate(*args):
        subprocess.run(
            [sys.executable, "-m", "alembic", *args],
            cwd=Path(__file__).resolve().parents[1],
            env=env,
            check=True,
            capture_output=True,
        )

    migrate("upgrade", "0006")
    payload = json.dumps({"date": "2024-01-02", "weight_kg": 80, "sleep": 8, "fatigue": 3})
    with sqlite3.connect(path) as db:
        db.execute("INSERT INTO users (id,token_hash,write_revision) VALUES ('old','hash',0)")
        db.execute(
            "INSERT INTO records (id,user_id,kind,version,payload,created_at) VALUES ('check','old','checkin',1,?,'2024-01-03 00:00:00')",
            (payload,),
        )
    migrate("upgrade", "head")
    migrate("check")
    with sqlite3.connect(path) as db:
        row = db.execute("SELECT payload,event_date FROM records WHERE id='check'").fetchone()
        assert row == (payload, "2024-01-02")
    migrate("downgrade", "0006")
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT payload FROM records WHERE id='check'").fetchone()[0] == payload
