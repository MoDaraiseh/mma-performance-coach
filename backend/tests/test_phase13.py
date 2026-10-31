import sqlite3
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException
from joserfc import jwt
from joserfc.jwk import RSAKey
from pydantic import ValidationError
from sqlalchemy import select, text
from test_api import account
from test_api import client as api_client

from app import identity
from app.access import digest
from app.db import ExternalIdentity, LoginSession, OIDCFlow, RateBucket, Session, User
from app.identity import bind_identity
from app.mma_agent import bounded_request
from app.operations import expected_head, reserve_ai
from app.settings import Settings, settings
from tools.sqlite_backup import backup

client = api_client


@pytest.fixture(scope="session", autouse=True)
def close_focused_database():
    yield
    from app.db import engine

    engine.dispose()


@pytest.fixture
def provider(monkeypatch):
    key = RSAKey.generate_key(2048, parameters={"kid": "test-key"})
    state = {"nonce": "", "override": {}, "exchanges": 0, "insecure": False}
    monkeypatch.setattr(settings, "identity_mode", "oidc")
    monkeypatch.setattr(settings, "oidc_issuer", "https://id.example")
    monkeypatch.setattr(settings, "oidc_client_id", "mma-client")
    monkeypatch.setattr(settings, "oidc_client_secret", "not-a-real-secret")

    def handler(request):
        if request.url.path == "/.well-known/openid-configuration":
            return httpx.Response(
                200,
                json={
                    "issuer": settings.oidc_issuer,
                    "authorization_endpoint": "https://id.example/authorize",
                    "token_endpoint": "http://id.example/token"
                    if state["insecure"]
                    else "https://id.example/token",
                    "jwks_uri": "https://id.example/jwks",
                    "id_token_signing_alg_values_supported": ["RS256"],
                    "response_types_supported": ["code"],
                },
            )
        if request.url.path == "/jwks":
            return httpx.Response(200, json={"keys": [key.as_dict(private=False)]})
        if request.url.path == "/token":
            state["exchanges"] += 1
            assert "code_verifier=" in request.content.decode()
            claims = {
                "iss": "https://id.example",
                "sub": "subject-one",
                "aud": "mma-client",
                "exp": int(time.time()) + 300,
                "iat": int(time.time()),
                "auth_time": int(time.time()),
                "nonce": state["nonce"],
                **state["override"],
            }
            return httpx.Response(
                200,
                json={
                    "access_token": "synthetic-unused-token",
                    "token_type": "Bearer",
                    "id_token": jwt.encode({"alg": "RS256", "kid": "test-key"}, claims, key),
                },
            )
        raise AssertionError("Unexpected provider URL")

    oauth = OAuth()
    remote = oauth.register(
        "managed",
        client_id="mma-client",
        client_secret="not-a-real-secret",
        server_metadata_url="https://id.example/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid",
            "code_challenge_method": "S256",
            "transport": httpx.MockTransport(handler),
        },
    )
    monkeypatch.setattr(identity, "_client", remote)
    return state


def start(client, provider, link=False):
    response = (
        client.post("/api/auth/oidc/link", follow_redirects=False)
        if link
        else client.get("/api/auth/oidc/login", follow_redirects=False)
    )
    assert response.status_code == (200 if link else 302), response.text
    url = response.json()["authorization_url"] if link else response.headers["location"]
    query = parse_qs(urlsplit(url).query)
    assert query["code_challenge_method"] == ["S256"] and query["nonce"]
    provider["nonce"] = query["nonce"][0]
    return "/api/auth/oidc/callback?code=synthetic&state=" + query["state"][0]


def test_real_authlib_signed_oidc_nonce_pkce_login_and_replay(client, provider):
    callback = start(client, provider)
    response = client.get(callback, follow_redirects=False)
    assert response.status_code == 303 and response.headers["location"] == "/"
    assert client.get("/api/auth/session").status_code == 200
    with Session() as db:
        assert db.scalar(select(ExternalIdentity.subject)) == "subject-one"
    assert client.get(callback).status_code == 400 and provider["exchanges"] == 1
    assert client.get("/api/auth/oidc/login").status_code == 409


@pytest.mark.parametrize(
    "claims",
    [
        {"nonce": "wrong"},
        {"aud": "other-client"},
        {"iss": "https://evil.example"},
        {"exp": 1},
        {"auth_time": None},
        {"auth_time": 1},
        {"auth_time": 9999999999},
    ],
)
def test_oidc_bad_signed_claims_never_create_accounts(client, provider, claims):
    provider["override"] = claims
    response = client.get(start(client, provider), follow_redirects=False)
    assert response.status_code == 400
    with Session() as db:
        assert not list(db.scalars(select(User)))


def test_expired_oidc_state_and_insecure_discovery(client, provider):
    callback = start(client, provider)
    with Session.begin() as db:
        for row in db.scalars(select(OIDCFlow)):
            row.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    assert client.get(callback).status_code == 400 and provider["exchanges"] == 0


def test_discovery_http_token_endpoint_rejected(client, provider):
    provider["insecure"] = True
    assert client.get("/api/auth/oidc/login").status_code == 503
    assert provider["exchanges"] == 0


def test_live_identity_collision_cannot_reassign_account(client, monkeypatch):
    account(client)
    with Session() as db:
        uid = db.scalar(select(User.id))
        source = db.scalar(select(LoginSession.token_hash))
        original = db.get(User, uid).token_hash
    monkeypatch.setattr(settings, "oidc_issuer", "https://id.example")
    bind_identity({"iss": settings.oidc_issuer, "sub": "owned-by-another"}, {})
    with pytest.raises(HTTPException) as error:
        bind_identity(
            {"iss": settings.oidc_issuer, "sub": "owned-by-another"},
            {"user_id": uid, "session_hash": source},
        )
    assert error.value.status_code == 409
    with Session() as db:
        assert db.get(User, uid).token_hash == original


def test_operator_identity_mode_and_legacy_recovery_switch(client, monkeypatch):
    token = account(client)
    monkeypatch.setattr(settings, "identity_mode", "oidc")
    assert client.post("/api/auth/register").status_code == 403
    monkeypatch.setattr(settings, "allow_legacy_recovery", False)
    assert client.post("/api/auth/restore", json={"token": token}).status_code == 403
    assert client.get("/api/auth/config").json()["managed_sign_in"]


def test_identity_migration_preserves_legacy_credentials_and_payload(tmp_path):
    import json
    import os

    source = tmp_path / "legacy.db"
    env = {
        **os.environ,
        "DATABASE_URL": "sqlite:///" + str(source),
        "APP_ENV": "test",
        "IDENTITY_MODE": "local",
    }

    def migrate(*args):
        subprocess.run(
            [sys.executable, "-m", "alembic", *args], env=env, check=True, capture_output=True
        )

    migrate("upgrade", "0007")
    payload = json.dumps({"synthetic": True, "version": 1})
    with sqlite3.connect(source) as db:
        db.execute(
            "INSERT INTO users(id,token_hash,write_revision) VALUES ('original','unchanged-recovery-hash',0)"
        )
        db.execute(
            "INSERT INTO login_sessions(token_hash,user_id,expires_at) VALUES ('unchanged-session-hash','original','2099-01-01')"
        )
        db.execute(
            "INSERT INTO records(id,user_id,kind,version,payload,created_at) VALUES ('plan','original','plan',1,?,CURRENT_TIMESTAMP)",
            (payload,),
        )
    migrate("upgrade", "head")
    migrate("check")
    with sqlite3.connect(source) as db:
        assert db.execute("SELECT token_hash FROM users").fetchone()[0] == "unchanged-recovery-hash"
        assert db.execute("SELECT token_hash,created_at,label FROM login_sessions").fetchone()[
            :2
        ] != (None, None)
        assert (
            db.execute("SELECT token_hash FROM login_sessions").fetchone()[0]
            == "unchanged-session-hash"
        )
        assert db.execute("SELECT payload FROM records").fetchone()[0] == payload
    migrate("downgrade", "0007")
    migrate("upgrade", "head")
    with sqlite3.connect(source) as db:
        assert db.execute("SELECT payload FROM records").fetchone()[0] == payload


def test_explicit_link_preserves_recovery_and_account_id(client, monkeypatch, provider):
    monkeypatch.setattr(settings, "identity_mode", "local")
    token = account(client)
    with Session() as db:
        uid = db.scalar(select(User.id))
        previous_hash = db.get(User, uid).token_hash
    monkeypatch.setattr(settings, "identity_mode", "oidc")
    callback = start(client, provider, link=True)
    assert client.get(callback, follow_redirects=False).status_code == 303
    with Session() as db:
        assert db.scalar(select(ExternalIdentity.user_id)) == uid
        assert db.get(User, uid).token_hash == previous_hash
    client.post("/api/auth/logout")
    assert client.post("/api/auth/restore", json={"token": token}).status_code == 200
    assert client.delete("/api/account").status_code == 200
    with Session() as db:
        assert not list(db.scalars(select(ExternalIdentity)))


def test_linking_requires_original_live_session_and_no_email_merge(client, provider, monkeypatch):
    monkeypatch.setattr(settings, "identity_mode", "local")
    account(client)
    with Session() as db:
        uid = db.scalar(select(User.id))
        session_hash = db.scalar(select(LoginSession.token_hash))
    monkeypatch.setattr(settings, "identity_mode", "oidc")
    callback = start(client, provider, link=True)
    client.post("/api/auth/logout")
    assert client.get(callback, follow_redirects=False).status_code == 401
    first = bind_identity(
        {"iss": settings.oidc_issuer, "sub": "one", "email": "same@example.test"}, {}
    )
    second = bind_identity(
        {"iss": settings.oidc_issuer, "sub": "two", "email": "same@example.test"}, {}
    )
    with Session() as db:
        assert (
            db.get(LoginSession, digest(first)).user_id
            != db.get(LoginSession, digest(second)).user_id
        )
    with pytest.raises(HTTPException):
        bind_identity(
            {"iss": settings.oidc_issuer, "sub": "one"},
            {"user_id": uid, "session_hash": session_hash},
        )


def test_sessions_cross_account_revocation_and_restore(client):
    token = account(client)
    original = client.cookies.get("mma_session")
    client.post("/api/auth/restore", json={"token": token})
    rows = client.get("/api/auth/sessions").json()
    assert all(
        r["created_at"].endswith("+00:00") and r["expires_at"].endswith("+00:00") for r in rows
    )
    assert len(rows) == 2 and sum(r["current"] for r in rows) == 1
    assert all(r["id"] not in {original, digest(original)} for r in rows)
    handle = rows[0]["id"]
    client.cookies.clear()
    account(client)
    assert client.delete("/api/auth/sessions/" + handle).status_code == 404
    client.cookies.clear()
    client.cookies.set("mma_session", original)
    assert client.post("/api/auth/sessions/revoke-others").json()["revoked"] == 1


def test_ai_budget_concurrent_reservations_and_calendar_month(client, monkeypatch):
    monkeypatch.setattr(settings, "ai_global_daily", 6)
    monkeypatch.setattr(settings, "ai_global_monthly", 100)

    def attempt(_):
        try:
            reserve_ai()
            return 200
        except HTTPException as exc:
            return exc.status_code

    with ThreadPoolExecutor(max_workers=8) as pool:
        result = list(pool.map(attempt, range(20)))
    assert result.count(200) == 3 and result.count(429) == 17
    with Session.begin() as db:
        from sqlalchemy import delete

        db.execute(delete(RateBucket))
    monkeypatch.setattr(settings, "ai_global_daily", 100)
    monkeypatch.setattr(settings, "ai_global_monthly", 4)
    reserve_ai(datetime(2026, 10, 1, tzinfo=timezone.utc))
    reserve_ai(datetime(2026, 10, 16, tzinfo=timezone.utc))
    with pytest.raises(HTTPException):
        reserve_ai(datetime(2026, 10, 31, tzinfo=timezone.utc))
    reserve_ai(datetime(2026, 11, 1, tzinfo=timezone.utc))


def test_headers_on_rejection_and_input_cap(client):
    response = client.post("/api/auth/register", headers={"origin": "https://evil.example"})
    assert response.status_code == 403
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["cache-control"] == "no-store"
    with pytest.raises(ValueError):
        bounded_request({"input": "x" * 40001})


def test_production_requires_oidc_and_valid_shared_secrets():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            app_env="production",
            cookie_secure=True,
            public_origin="https://mma.example",
            allowed_hosts="mma.example",
        )


@pytest.mark.parametrize(
    "url", ["sqlite:///normal-athlete.db", "postgresql+psycopg://user:secret@localhost/production"]
)
def test_internal_postgres_probe_cannot_open_normal_database(monkeypatch, url):
    from tools.verify_postgres import probe

    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.delenv("MMA_TEST_SCHEMA", raising=False)
    with pytest.raises(ValueError, match="generated disposable"):
        probe()


def test_readiness_requires_migration_head(client):
    assert client.get("/api/ready").status_code == 503  # create_all fixture is not migrated
    from app.db import engine

    with engine.begin() as db:
        db.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))
        db.execute(text("INSERT INTO alembic_version VALUES (:v)"), {"v": expected_head()})
    try:
        assert client.get("/api/ready").status_code == 200
    finally:
        with engine.begin() as db:
            db.execute(text("DROP TABLE alembic_version"))


def test_disposable_backup_restore_and_no_overwrite(tmp_path):
    import os

    source = tmp_path / "source.db"
    env = {**os.environ, "APP_ENV": "test", "DATABASE_URL": "sqlite:///" + str(source)}
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        env=env,
        check=True,
        capture_output=True,
    )
    with sqlite3.connect(source) as db:
        db.execute("INSERT INTO users(id,token_hash,write_revision) VALUES ('synthetic','hash',0)")
        db.execute(
            "INSERT INTO login_sessions(token_hash,user_id,expires_at,label) VALUES ('session','synthetic','2099-01-01','test')"
        )
    destination = tmp_path / "backup.db"
    assert backup(source, destination)["counts"]["users"] == 1
    restored = tmp_path / "mma_restore_test.db"
    result = backup(destination, restored, restore=True)
    assert result["counts"]["users"] == 1 and result["counts"]["login_sessions"] == 0
    with pytest.raises(ValueError):
        backup(source, source)
    with pytest.raises(ValueError):
        backup(destination, tmp_path / "mma.db", restore=True)
