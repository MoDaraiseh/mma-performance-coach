"""Regression tests for defects found in the post-handoff review."""

from datetime import date, datetime, timedelta, timezone

from test_api import account
from test_api import client as client

from app import analytics, main
from app.clock import latest_user_date
from app.db import BACKEND_DIR, OperatorCounter, RateBucket, Session, resolve_database_url


def test_latest_user_date_covers_furthest_ahead_time_zone():
    # 11:00 UTC is already the next calendar day in UTC+14 (Kiribati), not in UTC+13.
    assert latest_user_date(datetime(2026, 11, 1, 10, 59, tzinfo=timezone.utc)).isoformat() == (
        "2026-11-02"
    )
    assert latest_user_date(datetime(2026, 11, 1, 9, 59, tzinfo=timezone.utc)).isoformat() == (
        "2026-11-01"
    )
    dubai = timezone(timedelta(hours=4))
    # 01:30 in Dubai is still the previous UTC date; the athlete's "today" must be accepted.
    assert latest_user_date(datetime(2026, 11, 2, 1, 30, tzinfo=dubai)).isoformat() == "2026-11-02"


def test_dates_ahead_of_server_utc_are_accepted_until_truly_future(client, monkeypatch):
    # Simulate an athlete east of UTC whose calendar is already one day ahead of the server.
    local_today = date.today() + timedelta(days=1)
    future = local_today + timedelta(days=1)
    for module in (main, analytics):
        monkeypatch.setattr(module, "latest_user_date", lambda: local_today)
    account(client)
    assert client.post("/api/demo").status_code == 200

    check = {"weight_kg": 78, "sleep": 7.5, "fatigue": 3}
    assert client.post("/api/progress", json={**check, "date": future.isoformat()}).status_code == (
        422
    )
    assert (
        client.post("/api/progress", json={**check, "date": local_today.isoformat()}).status_code
        == 200
    )

    achievement = {"discipline": "Boxing", "title": "Clean jab return"}
    assert (
        client.post(
            "/api/analytics/achievements", json={**achievement, "date": future.isoformat()}
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/analytics/achievements", json={**achievement, "date": local_today.isoformat()}
        ).status_code
        == 200
    )

    plan = client.get("/api/training-plans").json()
    sid = plan["data"]["weeks"][0]["sessions"][0]["id"]
    log = {"session_id": sid, "minutes": 30, "effort": 5}
    assert (
        client.post(
            "/api/training-sessions", json={**log, "completed_on": future.isoformat()}
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/training-sessions", json={**log, "completed_on": local_today.isoformat()}
        ).status_code
        == 200
    )

    window = f"start={(local_today - timedelta(days=30)).isoformat()}"
    assert client.get(f"/api/analytics?{window}&end={local_today.isoformat()}").status_code == 200
    assert client.get(f"/api/analytics?{window}&end={future.isoformat()}").status_code == 422


def test_relative_sqlite_path_is_anchored_to_backend_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # launching from another directory must not matter
    resolved = resolve_database_url("sqlite:///./mma.db")
    assert resolved.database == str((BACKEND_DIR / "mma.db").resolve())
    absolute = tmp_path / "explicit.db"
    assert resolve_database_url(f"sqlite:///{absolute}").database == str(absolute)
    assert resolve_database_url("sqlite://").database in (None, "")
    assert resolve_database_url("sqlite:///:memory:").database == ":memory:"
    pg = "postgresql+psycopg://user:secret@db:5432/mma"
    assert resolve_database_url(pg).render_as_string(hide_password=False) == pg


def test_unexpected_host_is_rejected_before_quota_and_telemetry_writes(client):
    from sqlalchemy import func, select

    def rows():
        with Session() as db:
            return (
                db.scalar(select(func.count()).select_from(RateBucket)),
                db.scalar(select(func.count()).select_from(OperatorCounter)),
            )

    before = rows()
    assert client.get("/api/fighters", headers={"host": "evil.example"}).status_code == 400
    assert rows() == before
