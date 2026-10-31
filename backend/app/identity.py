"""Managed OIDC via Authlib; issuer/subject identity, never email-based merging."""

import secrets
import uuid
from datetime import datetime, timedelta, timezone

import httpx
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from joserfc.errors import JoseError
from sqlalchemy import delete, select

from .access import digest, issue_session
from .db import ExternalIdentity, LoginSession, OIDCFlow, Session, User
from .operations import increment
from .settings import settings

_client = None


def utc_stamp(value):
    # SQLite drops timezone metadata from UTC columns; never let the browser
    # reinterpret those stored values as local wall-clock time.
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def oidc_client():
    global _client
    if _client is None:
        oauth = OAuth()
        _client = oauth.register(
            "managed",
            client_id=settings.oidc_client_id,
            client_secret=settings.oidc_client_secret,
            server_metadata_url=settings.oidc_issuer.rstrip("/")
            + "/.well-known/openid-configuration",
            client_kwargs={
                "scope": "openid",
                "code_challenge_method": "S256",
                "timeout": 10,
                "follow_redirects": False,
            },
        )
    return _client


def enabled():
    if settings.identity_mode != "oidc":
        raise HTTPException(404, "Managed sign-in is not configured")


async def begin(request, uid=None):
    enabled()
    state = secrets.token_urlsafe(32)
    with Session.begin() as db:
        db.add(
            OIDCFlow(
                state_hash=digest(state),
                payload={
                    "user_id": uid,
                    "session_hash": digest(request.cookies.get("mma_session", "")) if uid else None,
                },
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
            )
        )
    request.session.clear()
    origin = settings.public_origin or str(request.base_url).rstrip("/")
    try:
        client = oidc_client()
        metadata = await client.load_server_metadata()
        if metadata.get("issuer") != settings.oidc_issuer or any(
            not str(metadata.get(k, "")).startswith("https://")
            for k in ("authorization_endpoint", "token_endpoint", "jwks_uri")
        ):
            raise ValueError("Untrusted discovery configuration")
        return await client.authorize_redirect(
            request,
            origin + "/api/auth/oidc/callback",
            state=state,
            nonce=secrets.token_urlsafe(32),
            prompt="login",
            max_age=0,
        )
    except (httpx.HTTPError, OAuthError, JoseError, ValueError):
        raise HTTPException(
            503, "Managed identity provider unavailable; no account was changed"
        ) from None


def bind_identity(claims, flow):
    issuer, subject = claims.get("iss"), claims.get("sub")
    if (
        issuer != settings.oidc_issuer
        or not isinstance(subject, str)
        or not 1 <= len(subject) <= 255
    ):
        raise HTTPException(400, "Invalid managed identity claims")
    with Session.begin() as db:
        existing = db.scalar(
            select(ExternalIdentity).where(
                ExternalIdentity.issuer == issuer, ExternalIdentity.subject == subject
            )
        )
        uid = flow.get("user_id")
        if uid:
            # The explicit link request's original session must still be valid.
            session = db.scalar(
                select(LoginSession).where(
                    LoginSession.token_hash == flow["session_hash"],
                    LoginSession.user_id == uid,
                    LoginSession.expires_at > datetime.now(timezone.utc),
                )
            )
            if not session or not db.get(User, uid):
                raise HTTPException(401, "Original linking session expired or was revoked")
            if existing and existing.user_id != uid:
                raise HTTPException(
                    409, "This managed identity is already linked to another account"
                )
        elif existing:
            uid = existing.user_id
        else:
            uid = str(uuid.uuid4())
            # Managed-only accounts have no issued local recovery credential.
            db.add(User(id=uid, token_hash=digest(secrets.token_urlsafe(48))))
            db.flush()
        if not existing:
            db.add(
                ExternalIdentity(id=str(uuid.uuid4()), user_id=uid, issuer=issuer, subject=subject)
            )
        return issue_session(db, uid, "Managed OIDC sign-in")


def install(app, auth, set_cookie):
    @app.get("/api/auth/config")
    def config():
        return {
            "managed_sign_in": settings.identity_mode == "oidc",
            "local_registration": settings.identity_mode == "local",
            "legacy_recovery": settings.allow_legacy_recovery,
            "note": "Provider manages email verification, recovery and optional MFA. Linking requires an explicit signed-in action; existing recovery credentials remain unchanged.",
        }

    @app.get("/api/auth/oidc/login")
    async def login(request: Request):
        if request.cookies.get("mma_session"):
            try:
                auth(request.cookies["mma_session"])
            except HTTPException:
                pass
            else:
                raise HTTPException(
                    409, "Sign out before switching accounts, or explicitly link from Settings"
                )
        return await begin(request)

    @app.post("/api/auth/oidc/link")
    async def link(request: Request, uid=Depends(auth)):
        response = await begin(request, uid)
        # Fetch this same-origin POST, then navigate. A native form redirect to
        # an external IdP would conflict with the app's strict form-action CSP.
        return {"authorization_url": response.headers["location"]}

    @app.get("/api/auth/oidc/callback")
    async def callback(request: Request):
        enabled()
        state = request.query_params.get("state", "")
        with Session.begin() as db:
            flow = db.execute(
                delete(OIDCFlow)
                .where(
                    OIDCFlow.state_hash == digest(state),
                    OIDCFlow.expires_at > datetime.now(timezone.utc),
                )
                .returning(OIDCFlow.payload)
            ).scalar_one_or_none()
        if not flow:
            increment("auth.oidc_failure")
            raise HTTPException(400, "Sign-in state expired or already used; restart sign-in")
        try:
            token = await oidc_client().authorize_access_token(
                request,
                claims_options={"iss": {"essential": True, "value": settings.oidc_issuer}},
                leeway=30,
            )
            claims = token.get("userinfo")
            if not token.get("id_token") or not claims:
                raise ValueError("Missing validated ID token")
            session_token = bind_identity(claims, flow)
        except HTTPException:
            raise
        except (httpx.HTTPError, OAuthError, JoseError, ValueError):
            increment("auth.oidc_failure")
            raise HTTPException(
                400, "Managed sign-in could not be verified; restart sign-in"
            ) from None
        finally:
            request.session.clear()
        response = RedirectResponse("/", status_code=303)
        set_cookie(response, session_token)
        increment("auth.oidc_success")
        return response

    @app.get("/api/auth/sessions")
    def sessions(request: Request, uid=Depends(auth)):
        with Session() as db:
            rows = db.scalars(
                select(LoginSession)
                .where(
                    LoginSession.user_id == uid,
                    LoginSession.expires_at > datetime.now(timezone.utc),
                )
                .order_by(LoginSession.created_at.desc())
                .limit(100)
            )
            # Derived public handles cannot be used as bearer credentials.
            current = digest(request.cookies.get("mma_session", ""))
            return [
                {
                    "id": digest("session-handle:" + r.token_hash),
                    "label": r.label,
                    "created_at": utc_stamp(r.created_at),
                    "expires_at": utc_stamp(r.expires_at),
                    "current": r.token_hash == current,
                }
                for r in rows
            ]

    @app.delete("/api/auth/sessions/{handle}")
    def revoke(handle: str, uid=Depends(auth)):
        with Session.begin() as db:
            rows = db.scalars(select(LoginSession).where(LoginSession.user_id == uid))
            row = next(
                (r for r in rows if digest("session-handle:" + r.token_hash) == handle), None
            )
            if not row:
                raise HTTPException(404, "Session not found")
            db.delete(row)
        return {"revoked": True}

    @app.post("/api/auth/sessions/revoke-others")
    def revoke_others(request: Request, uid=Depends(auth)):
        with Session.begin() as db:
            result = db.execute(
                delete(LoginSession).where(
                    LoginSession.user_id == uid,
                    LoginSession.token_hash != digest(request.cookies.get("mma_session", "")),
                )
            )
        return {"revoked": result.rowcount}
