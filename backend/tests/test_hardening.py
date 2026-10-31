"""Security and failure checks use the same disposable DB fixture as API tests."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from test_api import account
from test_api import client as api_client

from app.access import digest, quota
from app.db import LoginSession, Record, Session, User
from app.main import settings
from app.maintenance import retention
from app.repository import account_write, append_record
from app.settings import Settings

client = api_client


def test_session_is_separate_expires_and_logout_revokes(client):
    recovery = account(client)
    cookie = client.cookies.get("mma_session")
    assert cookie != recovery
    client.post("/api/auth/logout")
    client.cookies.set("mma_session", cookie)
    assert client.get("/api/auth/session").status_code == 401
    client.cookies.clear()
    assert client.post("/api/auth/restore", json={"token": recovery}).status_code == 200
    with Session.begin() as db:
        row = db.get(LoginSession, digest(client.cookies.get("mma_session")))
        row.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    assert client.get("/api/auth/session").status_code == 401
    assert client.post("/api/auth/restore", json={"token": recovery}).status_code == 200


def test_deleted_account_revokes_every_session_and_foreign_key(client):
    token = account(client)
    cookie = client.cookies.get("mma_session")
    client.post("/api/auth/restore", json={"token": token})
    assert client.delete("/api/account").status_code == 200
    client.cookies.set("mma_session", cookie)
    assert client.get("/api/auth/session").status_code == 401
    assert client.post("/api/auth/restore", json={"token": token}).status_code == 401
    with Session.begin() as db:
        assert not list(db.scalars(select(LoginSession)))
    with pytest.raises(IntegrityError), Session.begin() as db:
        db.add(Record(id="orphan", user_id="absent", kind="profile", version=1, payload={}))


def test_quota_atomic_across_concurrent_connections(client):
    def attempt(_):
        try:
            quota("same-client", "concurrent-test", 3)
            return 200
        except HTTPException as exc:
            return exc.status_code

    with ThreadPoolExecutor(max_workers=8) as pool:
        result = list(pool.map(attempt, range(12)))
    assert result.count(200) == 3
    assert result.count(429) == 9


def test_rate_response_and_host_origin_body_limits(client, monkeypatch):
    monkeypatch.setattr(settings, "auth_per_minute", 1)
    assert client.post("/api/auth/register").status_code == 200
    denied = client.post("/api/auth/register")
    assert denied.status_code == 429 and int(denied.headers["retry-after"]) > 0
    assert client.get("/api/health", headers={"host": "evil.example"}).status_code == 400
    assert (
        client.post("/api/auth/logout", headers={"origin": "https://evil.example"}).status_code
        == 403
    )
    assert (
        client.post("/api/auth/logout", headers={"sec-fetch-site": "cross-site"}).status_code == 403
    )
    assert (
        client.post("/api/auth/logout", content="x" * (settings.max_body_bytes + 1)).status_code
        == 413
    )
    assert "frame-ancestors 'none'" in client.get("/api/health").headers["content-security-policy"]


def test_production_configuration_fails_closed():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, app_env="production", cookie_secure=False)
    configured = Settings(
        _env_file=None,
        app_env="production",
        cookie_secure=True,
        public_origin="https://mma.example",
        allowed_hosts="mma.example",
        identity_mode="oidc",
        oidc_issuer="https://identity.example",
        oidc_client_id="test-client",
        oidc_client_secret="test-secret",
        oidc_state_secret="x" * 48,
    )
    assert configured.session_hours == 24


def test_production_tls_cookie_headers_and_shared_refresh_authorization(client, monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")
    monkeypatch.setattr(settings, "cookie_secure", True)
    monkeypatch.setattr(settings, "public_origin", "https://testserver")
    assert client.get("/api/health").status_code == 400
    response = client.post("https://testserver/api/auth/register")
    assert response.status_code == 200
    assert "Secure" in response.headers["set-cookie"]
    assert response.headers["strict-transport-security"] == "max-age=31536000"
    assert client.post("https://testserver/api/fighter-data/refresh").status_code == 403
    assert (
        client.post(
            "https://testserver/api/auth/logout", headers={"origin": "http://localhost:5173"}
        ).status_code
        == 403
    )


def test_ai_quota_prevents_provider_call_and_plan_mutation(client, monkeypatch):
    account(client)
    client.post("/api/demo")
    original = client.get("/api/training-plans").json()["id"]
    monkeypatch.setattr(settings, "ai_per_day", 1)
    request = {"message": "Explain recovery", "use_ai": True}
    assert client.post("/api/coach", json=request).status_code == 200
    assert client.post("/api/coach", json=request).status_code == 429
    assert client.get("/api/training-plans").json()["id"] == original
    assert client.post("/api/coach", json={**request, "use_ai": False}).status_code == 200


def test_retention_dry_run_preserves_plans_and_logs(client):
    account(client)
    with Session() as db:
        uid = db.scalar(select(User.id))
    old = datetime.now(timezone.utc) - timedelta(days=4000)
    with account_write(uid) as db:
        for kind in ["conversation", "draft", "profile", "plan", "nutrition", "workout", "checkin"]:
            row = append_record(db, uid, kind, {})
            row.created_at = old
    assert retention()["counts"]["2"] == 1
    with Session() as db:
        assert len(list(db.scalars(select(Record)))) == 7
    retention(apply=True)
    with Session() as db:
        assert {r.kind for r in db.scalars(select(Record))} == {
            "profile",
            "plan",
            "nutrition",
            "workout",
            "checkin",
        }


def test_failed_transaction_rolls_back_and_response_hides_database_details(client, monkeypatch):
    account(client)
    with Session() as db:
        uid = db.scalar(select(User.id))
    with pytest.raises(RuntimeError), account_write(uid) as db:
        append_record(db, uid, "profile", {"name": "rollback"})
        raise RuntimeError("simulated write failure")
    assert client.get("/api/profile").status_code == 404

    def fail(*args, **kwargs):
        raise OperationalError("secret query", {}, Exception("private database URL"))

    monkeypatch.setattr("app.main.save", fail)
    response = client.put("/api/profile", json={"name": "Sam"})
    assert response.status_code == 503
    assert "secret" not in response.text and "private" not in response.text
