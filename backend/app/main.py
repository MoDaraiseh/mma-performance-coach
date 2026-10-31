import hashlib
import json
import logging
import os
import secrets
import time
import uuid
from contextlib import asynccontextmanager
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import Cookie, Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.concurrency import run_in_threadpool
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from . import analytics as an
from . import coach_actions as ca
from . import coach_context as cc
from . import coach_security as cs
from . import identity
from . import nutrition_integrity as ni
from .access import digest, issue_session, quota
from .analysis import (
    AthleticAssessmentService,
    FighterMatchingService,
    FightingStyleAnalysisService,
    PhysicalProfileService,
    WeightClassService,
    weight_classes,
)
from .athletics import athletic_assessment
from .db import (
    ExternalIdentity,
    FighterSnapshot,
    LoginSession,
    OIDCFlow,
    RateBucket,
    Record,
    ReferenceSnapshot,
    Session,
    User,
    engine,
)
from .dietary import eligible as eligible_ingredients
from .divisions import bundled_reference
from .exercises import CATALOG, alternatives, catalog_payload
from .fighter_refresh import refresh as refresh_fighters
from .fighter_refresh import revisions as fighter_revisions
from .fighters import DatabaseFighterProvider, LicensedFileFighterProvider, SeededFighterProvider
from .ingredients import catalog_payload as nutrition_catalog_payload
from .meal_composition import validate_plan as validate_meal_plan
from .mma_agent import MMAAgentService
from .nutrition_models import CoachIntent, NutritionChange, NutritionPreferences
from .operations import increment, readiness, record_http, reserve_ai
from .plan_integrity import make_plan, newest_checkin, plan_status
from .progression import adapt_future, progression_review
from .release_policy import require_release
from .repository import account_records, account_write, append_record, latest_checkin, latest_record
from .schemas import (
    AnalyticsSchedule,
    CheckIn,
    CoachRequest,
    MatchWeights,
    Profile,
    ReassessmentRequest,
    RevisionRequest,
    SubstitutionRequest,
    TechnicalAchievement,
    WorkoutLog,
)
from .settings import settings

logging.basicConfig(level=settings.log_level, format="%(message)s")
logger = logging.getLogger("mma")


@asynccontextmanager
async def lifespan(app):
    if settings.app_env == "production":
        if engine.dialect.name != "postgresql" or not readiness()["ready"]:
            raise RuntimeError("Production requires PostgreSQL and the expected migration head")
    # Migrations are run explicitly with Alembic; fail clearly on uninitialized DB.
    with engine.connect() as conn:
        conn.execute(select(User).limit(1))
        conn.execute(select(LoginSession).limit(1))
        conn.execute(select(RateBucket).limit(1))
    with Session() as db:
        if settings.app_env == "production":
            require_release(db, settings)
        for f in [] if settings.app_env == "production" else SeededFighterProvider().all():
            if not db.get(FighterSnapshot, f["id"]):
                db.add(FighterSnapshot(id=f["id"], payload=f, verified_at=f["verified_at"]))
        for division in ("Men", "Women"):
            if not db.get(ReferenceSnapshot, division):
                db.add(ReferenceSnapshot(id=division, payload=bundled_reference(division)))
        db.commit()
    yield


app = FastAPI(
    title="MMA Performance Coach",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if settings.app_env == "production" else "/docs",
    redoc_url=None if settings.app_env == "production" else "/redoc",
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts.split(","))
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.oidc_state_secret or secrets.token_urlsafe(48),
    session_cookie="mma_oidc",
    max_age=600,
    same_site="lax",
    https_only=settings.cookie_secure,
)


@app.middleware("http")
async def security(request: Request, call_next):
    if settings.app_env == "production" and request.url.scheme != "https":
        return JSONResponse({"error": "HTTPS required"}, status_code=400)
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        origin = request.headers.get("origin")
        expected = settings.public_origin or str(request.base_url).rstrip("/")
        if request.headers.get("sec-fetch-site") == "cross-site":
            return JSONResponse({"error": "Cross-site write rejected"}, status_code=403)
        if origin and origin != expected:
            # Vite development proxy uses the frontend origin.
            if (
                settings.app_env == "production"
                or origin
                not in {
                    "http://127.0.0.1:5173",
                    "http://localhost:5173",
                }
                or request.url.hostname not in {"localhost", "127.0.0.1", "testserver"}
            ):
                return JSONResponse({"error": "Untrusted request origin"}, status_code=403)
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > settings.max_body_bytes:
                return JSONResponse({"error": "Request body too large"}, status_code=413)
        request._body = bytes(body)
    if request.url.path.startswith("/api/") and request.url.path not in {
        "/api/health",
        "/api/ready",
    }:
        try:
            peer = request.client.host if request.client else "unknown"
            await run_in_threadpool(quota, peer, "api", settings.api_per_minute)
            if request.url.path in {
                "/api/auth/register",
                "/api/auth/restore",
                "/api/auth/oidc/login",
                "/api/auth/oidc/link",
                "/api/auth/oidc/callback",
            }:
                await run_in_threadpool(quota, peer, "auth", settings.auth_per_minute)
        except HTTPException as exc:
            return JSONResponse(
                {"error": exc.detail}, status_code=exc.status_code, headers=exc.headers
            )
        except SQLAlchemyError:
            return JSONResponse(
                {"error": "Service temporarily unavailable. Please retry."}, status_code=503
            )
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; font-src 'self'; connect-src 'self'; "
        "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
    )
    response.headers["X-Frame-Options"] = "DENY"
    if settings.app_env != "production" and request.url.path in {"/docs", "/redoc"}:
        # FastAPI's development documentation loads its own inline/CDN assets.
        del response.headers["Content-Security-Policy"]
    if settings.app_env == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response


@app.middleware("http")
async def operational_response(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if "Content-Security-Policy" not in response.headers and request.url.path not in {
        "/docs",
        "/redoc",
    }:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        )
    if settings.app_env == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
    logger.info(
        json.dumps(
            {
                "method": request.method,
                "route": getattr(request.scope.get("route"), "path", "unmatched"),
                "status": response.status_code,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            }
        )
    )
    try:
        await run_in_threadpool(
            record_http, response.status_code, (time.perf_counter() - started) * 1000
        )
    except SQLAlchemyError:
        logger.error(json.dumps({"event": "operational_counter_unavailable"}))
    return response


@app.exception_handler(HTTPException)
async def http_error(request, exc):
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code, headers=exc.headers)


@app.exception_handler(SQLAlchemyError)
async def database_error(request, exc):
    logger.error(json.dumps({"event": "database_error", "type": type(exc).__name__}))
    return JSONResponse(
        {"error": "Database temporarily unavailable. Reload and retry."}, status_code=503
    )


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return JSONResponse(
        {
            "error": "Invalid input",
            "details": [
                {"field": ".".join(map(str, e["loc"])), "message": e["msg"]} for e in exc.errors()
            ],
        },
        status_code=422,
    )


@app.exception_handler(IntegrityError)
async def version_conflict(request, exc):
    return JSONResponse(
        {"error": "A concurrent update changed this record. Reload and try again."}, status_code=409
    )


def auth(mma_session: str | None = Cookie(None)):
    if not mma_session or len(mma_session) > 200:
        raise HTTPException(401, "Create a local account or restore your account token.")
    with Session() as db:
        user = db.scalar(
            select(LoginSession.user_id)
            .join(User, User.id == LoginSession.user_id)
            .where(
                LoginSession.token_hash == digest(mma_session),
                LoginSession.expires_at > datetime.now(timezone.utc),
            )
        )
        if not user:
            raise HTTPException(401, "Session expired or account deleted.")
        return user


def records(uid, kind):
    with Session() as db:
        return list(
            db.scalars(
                select(Record)
                .where(Record.user_id == uid, Record.kind == kind)
                .order_by(Record.created_at, Record.id)
            )
        )


def latest(uid, kind):
    with Session() as db:
        return latest_record(db, uid, kind)


def save(uid, kind, payload):
    with account_write(uid) as db:
        r = append_record(db, uid, kind, payload)
    return r


def profile(uid):
    r = latest(uid, "profile")
    if not r:
        raise HTTPException(404, "Complete your athlete assessment first.")
    return Profile.model_validate(r.payload)


def record_json(r):
    return {
        "id": r.id,
        "version": r.version,
        "created_at": r.created_at.isoformat(),
        "data": r.payload,
    }


def plan(uid):
    r = latest(uid, "plan")
    if not r:
        raise HTTPException(404, "Generate a training plan first.")
    return r


def lineage_logs(db, uid, active):
    lineage = active.payload.get("lineage_id", active.id)
    ids = set(
        db.scalars(
            select(Record.id).where(
                Record.user_id == uid,
                Record.kind == "plan",
                (Record.id == lineage) | (Record.parent_ref == lineage),
            )
        )
    ) | {active.id}
    return [
        {**r.payload, "record_id": r.id, "recorded_at": r.created_at.isoformat()}
        for r in db.scalars(
            select(Record)
            .where(Record.user_id == uid, Record.kind == "workout", Record.parent_ref.in_(ids))
            .order_by(Record.version)
        )
    ]


@app.get("/api/exercise-catalog")
def exercise_catalog(uid=Depends(auth)):
    return catalog_payload()


@app.get("/api/training-intelligence")
def training_intelligence(uid=Depends(auth)):
    with Session() as db:
        source = latest_record(db, uid, "profile")
        active = latest_record(db, uid, "plan")
        if not source:
            raise HTTPException(404, "Complete your athlete assessment first.")
        p = Profile.model_validate(source.payload)
        check = latest_checkin(db, uid)
        logs = lineage_logs(db, uid, active) if active else []
        return {
            "assessment": athletic_assessment(p, check.payload if check else None),
            "review": progression_review(
                active.payload if active else {"weeks": []},
                logs,
                p,
                check.payload if check else None,
            ),
            "logs": [
                {**row.payload, "record_id": row.id, "recorded_at": row.created_at.isoformat()}
                for row in account_records(db, uid, "workout")
            ],
            "plan_id": active.id if active else None,
        }


def set_cookie(response, token):
    response.set_cookie(
        "mma_session",
        token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
        max_age=60 * 60 * settings.session_hours,
    )


@app.get("/api/health")
def health():
    return {"status": "ok", "ai_configured": bool(os.getenv("OPENAI_API_KEY"))}


@app.get("/api/ready")
def ready():
    if not readiness()["ready"]:
        raise HTTPException(503, "Database migration review required")
    return {"status": "ready"}


@app.post("/api/auth/register")
def register(response: Response):
    if settings.identity_mode != "local":
        raise HTTPException(403, "Use managed sign-in; local account creation is disabled")
    token = secrets.token_urlsafe(48)
    uid = str(uuid.uuid4())
    with Session() as db:
        db.add(User(id=uid, token_hash=hashlib.sha256(token.encode()).hexdigest()))
        db.flush()
        session_token = issue_session(db, uid)
        db.commit()
    set_cookie(response, session_token)
    return {
        "recovery_token": token,
        "note": "Local account token. Save privately; it grants full account access and is shown only now.",
    }


@app.post("/api/auth/restore")
def restore(response: Response, request: dict):
    if not settings.allow_legacy_recovery:
        raise HTTPException(403, "Legacy recovery is disabled by the operator; use managed sign-in")
    token = request.get("token", "")
    if not isinstance(token, str) or len(token) > 200:
        raise HTTPException(422, "Invalid token")
    with Session() as db:
        exists = db.scalar(
            select(User).where(User.token_hash == hashlib.sha256(token.encode()).hexdigest())
        )
    if not exists:
        raise HTTPException(401, "Invalid recovery token")
    with Session.begin() as db:
        # Check the account again inside the transaction to handle concurrent deletion.
        if not db.get(User, exists.id):
            raise HTTPException(401, "Account no longer exists")
        session_token = issue_session(db, exists.id)
    set_cookie(response, session_token)
    return {"restored": True}


@app.get("/api/auth/session")
def session(uid=Depends(auth)):
    return {"authenticated": True, "has_profile": latest(uid, "profile") is not None}


@app.post("/api/auth/logout")
def logout(response: Response, mma_session: str | None = Cookie(None)):
    if mma_session:
        with Session.begin() as db:
            db.execute(delete(LoginSession).where(LoginSession.token_hash == digest(mma_session)))
    response.delete_cookie("mma_session")
    return {"logged_out": True}


identity.install(app, auth, set_cookie)


@app.delete("/api/account")
def delete_account(response: Response, uid=Depends(auth)):
    with account_write(uid) as db:
        db.execute(delete(ExternalIdentity).where(ExternalIdentity.user_id == uid))
        db.execute(delete(OIDCFlow).where(OIDCFlow.payload["user_id"].as_string() == uid))
        db.execute(delete(LoginSession).where(LoginSession.user_id == uid))
        db.execute(delete(Record).where(Record.user_id == uid))
        db.execute(delete(User).where(User.id == uid))
    response.delete_cookie("mma_session")
    return {"deleted": True}


@app.get("/api/profile")
def get_profile(uid=Depends(auth)):
    return profile(uid)


@app.put("/api/profile")
def update_profile(p: Profile, uid=Depends(auth)):
    r = save(uid, "profile", p.model_dump())
    return record_json(r)


@app.get("/api/profile/draft")
def get_draft(uid=Depends(auth)):
    r = latest(uid, "draft")
    saved = latest(uid, "profile")
    return r.payload if r and (not saved or r.created_at > saved.created_at) else None


@app.put("/api/profile/draft")
def save_draft(p: Profile, uid=Depends(auth)):
    return record_json(save(uid, "draft", p.model_dump()))


@app.post("/api/demo")
def demo(uid=Depends(auth)):
    if latest(uid, "profile"):
        raise HTTPException(409, "A profile already exists. Demo does not overwrite athlete data.")
    p = Profile(
        name="Alex Morgan",
        age=26,
        metabolic_sex="male",
        height_cm=180,
        weight_kg=78,
        wingspan_cm=185,
        days=4,
        minutes=60,
        is_demo=True,
        stance="Orthodox",
        experience=[
            {"discipline": "Boxing", "months": 18, "sessions": 2, "instructor": True},
            {"discipline": "BJJ", "months": 6, "sessions": 1, "instructor": True},
        ],
    )
    with account_write(uid) as db:
        if latest_record(db, uid, "profile"):
            raise HTTPException(
                409, "A profile already exists. Demo does not overwrite athlete data."
            )
        source = append_record(db, uid, "profile", p.model_dump())
        append_record(db, uid, "plan", make_plan(source))
        append_record(db, uid, "nutrition", ni.build(ni.context_rows(db, uid)))
    return {"created": True}


@app.get("/api/assessment")
def assessment(uid=Depends(auth)):
    p = profile(uid)
    return {
        "physical": PhysicalProfileService.assess(p),
        "weight": WeightClassService.assess(p),
        "style": FightingStyleAnalysisService.assess(p),
    }


@app.get("/api/weight-classes")
def divisions(division: str = "Men"):
    if division not in {"Men", "Women"}:
        raise HTTPException(422, "Division must be Men or Women")
    return weight_classes(division)


@app.get("/api/fighters")
def fighters(response: Response, q: str = Query("", max_length=100)):
    response.headers["X-Result-Limit"] = "50"
    return DatabaseFighterProvider().search(q, page_size=50)["items"]


@app.get("/api/fighters/search")
def fighter_search(
    q: str = Query("", max_length=100),
    category: Literal["Men", "Women"] | None = None,
    division: str | None = Query(None, max_length=80),
    stance: Literal["Orthodox", "Southpaw", "Switch", "Unknown"] | None = None,
    status: Literal["Active", "Retired", "Not fighting", "Unknown"] | None = None,
    page: int = Query(1, ge=1, le=100000),
    page_size: int = Query(20, ge=1, le=50),
):
    return DatabaseFighterProvider().search(q, category, division, stance, status, page, page_size)


@app.post("/api/fighter-matches")
def matches(weights: MatchWeights, uid=Depends(auth)):
    return FighterMatchingService(DatabaseFighterProvider()).rank(profile(uid), weights)


@app.post("/api/fighter-comparisons/{fighter_id}")
def manual_comparison(fighter_id: str, weights: MatchWeights, uid=Depends(auth)):
    match = FighterMatchingService(DatabaseFighterProvider()).compare(
        profile(uid), weights, fighter_id
    )
    if match is None:
        raise HTTPException(404, "Fighter unavailable or requires provenance refresh")
    return match


@app.get("/api/fighter-data")
def fighter_data(uid=Depends(auth)):
    provider = DatabaseFighterProvider()
    available = provider.all()
    from .fighter_governance import quality

    return {
        "quality": quality(available),
        "count": len(available),
        "unavailable_records": provider.issues,
        "providers": [
            {
                "id": "local",
                "available": True,
                "description": "Reimport reviewed bundle; no new web verification.",
            },
            {
                "id": "licensed",
                "available": bool(
                    os.getenv("FIGHTER_LICENSED_EXPORT") and os.getenv("FIGHTER_LICENSE_REFERENCE")
                ),
                "description": "Operator-configured licensed JSON export; no provider bundled.",
            },
        ],
        "revisions": fighter_revisions(),
    }


@app.post("/api/fighter-data/refresh")
def refresh_fighter_data(provider: str = "local", uid=Depends(auth)):
    if settings.app_env == "production":
        raise HTTPException(
            403, "Shared fighter data refresh is an operator-only maintenance task in production."
        )
    if provider not in ("local", "licensed"):
        raise HTTPException(422, "Choose local or licensed provider")
    selected = SeededFighterProvider()
    if provider == "licensed":
        path, license_ref = (
            os.getenv("FIGHTER_LICENSED_EXPORT"),
            os.getenv("FIGHTER_LICENSE_REFERENCE"),
        )
        if not path or not license_ref:
            raise HTTPException(503, "Licensed provider not configured by operator")
        selected = LicensedFileFighterProvider(path, license_ref)
    try:
        return refresh_fighters(selected, refresh_reference=provider == "local")
    except (ValueError, OSError):
        raise HTTPException(
            422,
            "Provider export rejected; no changes applied. Check schema, license references, dates and identity collisions.",
        ) from None
    except IntegrityError:
        raise HTTPException(
            409, "Concurrent refresh; retry to read the committed snapshots"
        ) from None


@app.get("/api/comparisons")
def comparisons(uid=Depends(auth)):
    return [record_json(r) for r in records(uid, "comparison")]


@app.post("/api/comparisons/{fighter_id}")
def favorite(fighter_id: str, weights: MatchWeights, uid=Depends(auth)):
    athlete = profile(uid)
    match = FighterMatchingService(DatabaseFighterProvider()).compare(athlete, weights, fighter_id)
    if match is None:
        raise HTTPException(404, "No defensible comparison for this fighter")
    return record_json(
        save(
            uid,
            "comparison",
            {"match": match, "weights": weights.model_dump(), "profile": athlete.model_dump()},
        )
    )


@app.delete("/api/comparisons/{comparison_id}")
def remove_favorite(comparison_id: str, uid=Depends(auth)):
    with account_write(uid) as db:
        r = db.get(Record, comparison_id)
        if not r or r.user_id != uid or r.kind != "comparison":
            raise HTTPException(404, "Comparison not found")
        db.delete(r)
    return {"deleted": True}


@app.get("/api/training-plans")
def get_plan(uid=Depends(auth)):
    current = plan(uid)
    status = plan_status(current, latest(uid, "profile"), newest_checkin(records(uid, "checkin")))
    result = {**record_json(current), "status": status}
    if status["needs_review"]:
        result["data"] = {
            **current.payload,
            "available": False,
            "reason": status["reason"],
            "weeks": [{**w, "sessions": []} for w in current.payload["weeks"]],
        }
    return result


@app.post("/api/training-plans")
def generate_plan(uid=Depends(auth)):
    with account_write(uid) as db:
        if latest_record(db, uid, "plan"):
            raise HTTPException(409, "Use a proposed revision to replace an active plan.")
        source = latest_record(db, uid, "profile")
        if not source:
            raise HTTPException(404, "Complete your athlete assessment first.")
        r = append_record(db, uid, "plan", make_plan(source, latest_checkin(db, uid)))
    return record_json(r)


@app.get("/api/training-plans/history")
def plan_history(uid=Depends(auth)):
    return [record_json(r) for r in records(uid, "plan")]


@app.post("/api/training-sessions")
def log_workout(data: WorkoutLog, uid=Depends(auth)):
    with account_write(uid) as db:
        current = latest_record(db, uid, "plan")
        if not current:
            raise HTTPException(404, "Generate a training plan first.")
        valid = {s["id"]: s for w in current.payload["weeks"] for s in w["sessions"]}
        if data.session_id not in valid:
            raise HTTPException(422, "Session not found in active plan")
        if (
            current.payload.get("review_week")
            and int(data.session_id.split("-")[0][1:]) <= current.payload["review_week"]
        ):
            raise HTTPException(
                409, "This week is a historical checkpoint; log a future prescribed session"
            )
        if data.plan_id is not None and data.plan_id != current.id:
            raise HTTPException(409, "Plan changed; reopen the session before logging")
        if data.completed_on and data.completed_on > date.today():
            raise HTTPException(422, "Session dates cannot be in the future")
        if (
            sum(s.duration_seconds or 0 for e in data.performances for s in e.sets)
            > data.minutes * 60
        ):
            raise HTTPException(422, "Recorded set durations exceed actual session time")
        names = {ex["name"] for ex in valid[data.session_id]["exercises"]}
        if any(ex.exercise_name not in names for ex in data.performances):
            raise HTTPException(422, "Exercise not found in this session")
        if any(r["session_id"] == data.session_id for r in lineage_logs(db, uid, current)):
            raise HTTPException(409, "Session already logged")
        r = append_record(
            db,
            uid,
            "workout",
            {
                **data.model_dump(mode="json"),
                "completed_on": (data.completed_on or date.today()).isoformat(),
                "plan_id": current.id,
            },
        )
    return record_json(r)


@app.get("/api/training-sessions")
def workouts(limit: int | None = Query(None, ge=1, le=500), uid=Depends(auth)):
    if limit is None:
        return [record_json(r) for r in records(uid, "workout")]
    with Session() as db:
        return [
            record_json(r)
            for r in reversed(
                list(
                    db.scalars(
                        select(Record)
                        .where(Record.user_id == uid, Record.kind == "workout")
                        .order_by(Record.version.desc())
                        .limit(limit)
                    )
                )
            )
        ]


@app.get("/api/nutrition")
def nutrition(uid=Depends(auth)):
    with Session() as db:
        ctx = ni.context_rows(db, uid)
        if not ctx["nutrition"]:
            return None
        return {**record_json(ctx["nutrition"]), "data": ni.visible(ctx)}


@app.post("/api/nutrition")
def generate_nutrition(uid=Depends(auth)):
    # Explicit manual generation remains available for existing API clients.
    # AI has no write tools; UI changes to existing plans use preview/approval.
    with account_write(uid) as db:
        ctx = ni.context_rows(db, uid)
        if not ctx["profile"]:
            raise HTTPException(404, "Save a profile first")
        row = append_record(db, uid, "nutrition", ni.build(ctx))
    return record_json(row)


@app.get("/api/nutrition/catalog")
def nutrition_catalog(uid=Depends(auth)):
    return nutrition_catalog_payload()


@app.get("/api/nutrition/preferences")
def nutrition_preferences(uid=Depends(auth)):
    with Session() as db:
        return ni.preferences(ni.context_rows(db, uid)).model_dump()


@app.put("/api/nutrition/preferences")
def save_nutrition_preferences(data: NutritionPreferences, uid=Depends(auth)):
    with account_write(uid) as db:
        ctx = ni.context_rows(db, uid)
        if not ctx["profile"]:
            raise HTTPException(404, "Save a profile first")
        try:
            eligible_ingredients(Profile.model_validate(ctx["profile"].payload), data)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from None
        previous = ctx["preferences"]
        if previous and previous.payload == data.model_dump():
            return record_json(previous)
        row = append_record(db, uid, "nutrition_preferences", data.model_dump())
    return record_json(row)


@app.get("/api/nutrition/history")
def nutrition_history(uid=Depends(auth)):
    return [record_json(r) for r in records(uid, "nutrition")]


@app.get("/api/nutrition/proposals")
def nutrition_proposals(uid=Depends(auth)):
    return [record_json(r) for r in records(uid, "nutrition_proposal")]


@app.post("/api/nutrition/proposals")
def propose_nutrition(data: NutritionChange, uid=Depends(auth)):
    with account_write(uid) as db:
        ctx = ni.context_rows(db, uid)
        try:
            candidate = ni.proposed(ctx, data)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from None
        row = append_record(
            db,
            uid,
            "nutrition_proposal",
            {
                "binding": ni.binding(ctx),
                "status": "pending",
                "plan": candidate,
                "change": data.model_dump(),
            },
        )
    return record_json(row)


@app.post("/api/nutrition/proposals/{proposal_id}/{action}")
def decide_nutrition(proposal_id: str, action: str, uid=Depends(auth)):
    if action not in ("approve", "reject"):
        raise HTTPException(422, "Choose approve or reject")
    with account_write(uid) as db:
        row = db.get(Record, proposal_id)
        if not row or row.user_id != uid or row.kind != "nutrition_proposal":
            raise HTTPException(404, "Proposal not found")
        if row.payload["status"] != "pending":
            raise HTTPException(409, "Proposal already resolved")
        if action == "approve":
            ctx = ni.context_rows(db, uid)
            if row.payload["binding"] != ni.binding(ctx):
                raise HTTPException(
                    409,
                    "Nutrition, profile, preferences, training or progress changed; request a fresh proposal",
                )
            candidate = row.payload["plan"]
            # Recompute using current deterministic services; never trust a stored generated total.
            try:
                expected = ni.proposed(ctx, NutritionChange.model_validate(row.payload["change"]))
            except ValueError as exc:
                raise HTTPException(409, str(exc)) from None
            if candidate != expected:
                raise HTTPException(409, "Proposal no longer validates against current catalog")
            if candidate.get("available"):
                validate_meal_plan(
                    candidate,
                    eligible_ingredients(
                        Profile.model_validate(candidate["inputs"]), ni.preferences(ctx)
                    ),
                )
            saved = append_record(db, uid, "nutrition", candidate)
            row.payload = {**row.payload, "status": "approved", "saved_plan_id": saved.id}
        else:
            row.payload = {**row.payload, "status": "rejected"}
    return {"status": row.payload["status"], "saved_plan_id": row.payload.get("saved_plan_id")}


@app.get("/api/progress")
def progress(limit: int | None = Query(None, ge=1, le=500), uid=Depends(auth)):
    if limit is None:
        return [record_json(r) for r in records(uid, "checkin")]
    with Session() as db:
        return [
            record_json(r)
            for r in reversed(
                list(
                    db.scalars(
                        select(Record)
                        .where(Record.user_id == uid, Record.kind == "checkin")
                        .order_by(Record.event_date.desc(), Record.version.desc())
                        .limit(limit)
                    )
                )
            )
        ]


@app.post("/api/progress")
def checkin(data: CheckIn, uid=Depends(auth)):
    if data.date > date.today():
        raise HTTPException(422, "Check-in dates cannot be in the future")
    with account_write(uid) as db:
        if db.scalar(
            select(Record.id)
            .where(
                Record.user_id == uid,
                Record.kind == "checkin",
                Record.event_date == data.date.isoformat(),
            )
            .limit(1)
        ):
            raise HTTPException(409, "A check-in already exists for this date")
        r = append_record(db, uid, "checkin", data.model_dump(mode="json"))
    return record_json(r)


@app.post("/api/revisions")
def propose(data: RevisionRequest, uid=Depends(auth)):
    with account_write(uid) as db:
        active = latest_record(db, uid, "plan")
        source = latest_record(db, uid, "profile")
        if not active or not source:
            raise HTTPException(404, "Generate a training plan first.")
        check = latest_checkin(db, uid)
        proposed = make_plan(source, check, data.days)
        r = append_record(
            db,
            uid,
            "proposal",
            {
                "base_plan_id": active.id,
                "source_workout_ids": sorted(
                    log["record_id"] for log in lineage_logs(db, uid, active)
                ),
                "source_profile_id": source.id,
                "source_checkin_id": check.id if check else None,
                "before_days": active.payload["days"],
                "after_days": proposed["days"],
                "reason": data.reason,
                "plan": proposed,
                "status": "pending",
            },
        )
    return record_json(r)


@app.post("/api/training-plans/substitution-preview")
def substitute(data: SubstitutionRequest, uid=Depends(auth)):
    with account_write(uid) as db:
        active = latest_record(db, uid, "plan")
        source = latest_record(db, uid, "profile")
        if not active or not source:
            raise HTTPException(404, "Generate a training plan first")
        p = Profile.model_validate(source.payload)
        check = latest_checkin(db, uid)
        if plan_status(active, source, check)["needs_review"]:
            raise HTTPException(
                409, "Review changed profile/recovery inputs before choosing substitutions"
            )
        logs = lineage_logs(db, uid, active)
        if (
            int(data.session_id.split("-")[0][1:]) <= active.payload.get("review_week", 0)
            if data.session_id.split("-")[0][1:].isdigit()
            else False
        ):
            raise HTTPException(409, "Historical checkpoint sessions cannot be substituted")
        if any(log["session_id"] == data.session_id for log in logs):
            raise HTTPException(409, "This session is already logged")
        proposed = deepcopy(active.payload)
        session = next(
            (s for w in proposed["weeks"] for s in w["sessions"] if s["id"] == data.session_id),
            None,
        )
        ex = (
            next((e for e in session["exercises"] if e["name"] == data.exercise_name), None)
            if session
            else None
        )
        if not ex or not ex.get("catalog_id"):
            raise HTTPException(
                422,
                "Exercise has no current catalog prescription; review a current-input plan first",
            )
        eligible = alternatives(ex["catalog_id"], p)
        item = next((e for e in eligible if e["id"] == data.alternative_id), None)
        if not item or item["category"] != CATALOG[ex["catalog_id"]]["category"]:
            raise HTTPException(
                422, "Alternative is unavailable or changes the prescription category"
            )
        if any(other is not ex and other["name"] == item["name"] for other in session["exercises"]):
            raise HTTPException(422, "Alternative already exists in this session")
        ex.update(
            name=item["name"],
            catalog_id=item["id"],
            cue=item["technique"],
            alternative_ids=[e["id"] for e in alternatives(item["id"], p)],
            substitution=item["modification_notes"],
        )
        ex.pop("suggested_load_kg", None)
        proposed.update(
            continuation=True,
            changes=[
                f"{data.session_id}: replace {data.exercise_name} with {item['name']}. Alternative focus may differ; review technique and modification notes."
            ],
        )
        row = append_record(
            db,
            uid,
            "proposal",
            {
                "base_plan_id": active.id,
                "source_profile_id": source.id,
                "source_checkin_id": check.id if check else None,
                "source_workout_ids": sorted(log["record_id"] for log in logs),
                "before_days": active.payload["days"],
                "after_days": proposed["days"],
                "reason": proposed["changes"][0],
                "plan": proposed,
                "status": "pending",
            },
        )
    return record_json(row)


@app.get("/api/revisions")
def proposals(uid=Depends(auth)):
    return [record_json(r) for r in records(uid, "proposal")]


@app.post("/api/revisions/{proposal_id}/{action}")
def decide(proposal_id: str, action: str, uid=Depends(auth)):
    if action not in {"approve", "reject"}:
        raise HTTPException(422, "Choose approve or reject")
    with account_write(uid) as db:
        r = db.get(Record, proposal_id)
        if not r or r.user_id != uid or r.kind != "proposal":
            raise HTTPException(404, "Proposal not found")
        if r.payload["status"] != "pending":
            raise HTTPException(409, "Proposal already resolved")
        current = latest_record(db, uid, "plan")
        source = latest_record(db, uid, "profile")
        check = latest_checkin(db, uid)
        if action == "approve" and (
            r.payload.get("source_profile_id") != source.id
            or r.payload.get("source_checkin_id") != (check.id if check else None)
        ):
            raise HTTPException(409, "Profile or recovery changed; request a new proposal")
        if (
            action == "approve"
            and r.payload.get("source_workout_ids") is not None
            and r.payload["source_workout_ids"]
            != sorted(log["record_id"] for log in lineage_logs(db, uid, current))
        ):
            raise HTTPException(409, "Performance history changed; request a new proposal")
        if action == "approve" and current.id != r.payload["base_plan_id"]:
            raise HTTPException(409, "Active plan changed; request a new proposal")
        if action == "approve":
            db.add(
                Record(
                    id=str(uuid.uuid4()),
                    user_id=uid,
                    kind="plan",
                    version=current.version + 1,
                    payload={
                        **r.payload["plan"],
                        "version": current.version + 1,
                        **(
                            {
                                "lineage_id": current.payload.get("lineage_id", current.id),
                                "history_plan_ids": sorted(
                                    {current.id, *current.payload.get("history_plan_ids", [])}
                                ),
                            }
                            if r.payload["plan"].get("continuation")
                            else {}
                        ),
                    },
                )
            )
        r.payload = {**r.payload, "status": "approved" if action == "approve" else "rejected"}
    return {"status": r.payload["status"]}


@app.post("/api/reassessments")
def reassess(data: ReassessmentRequest | None = None, uid=Depends(auth)):
    checkpoint = data.week if data else 4
    with account_write(uid) as db:
        checks = account_records(db, uid, "checkin")
        active = latest_record(db, uid, "plan")
        source = latest_record(db, uid, "profile")
        if not checks or not active or not source:
            raise HTTPException(422, "Save a profile, plan and check-in before reassessment")
        check = newest_checkin(checks)
        old = active.payload["inputs"]
        logs = lineage_logs(db, uid, active)
        review = progression_review(
            active.payload, logs, Profile.model_validate(source.payload), check.payload
        )
        reduce = (
            review["recovery"]["status"] == "reduce"
            or sum(log.get("status") in {"missed", "failed"} for log in logs[-3:]) >= 2
        )
        report = {
            "review_week": checkpoint,
            "weight_change_kg": round(check.payload["weight_kg"] - old["weight_kg"], 2),
            "before_days": active.payload["days"],
            "suggested_days": min(
                source.payload["days"],
                max(1, active.payload["days"] - 1) if reduce else active.payload["days"],
            ),
            "sessions_logged": review["workload"]["completed"],
            "benchmark_changes": AthleticAssessmentService.compare(
                old["benchmarks"], check.payload["benchmarks"]
            ),
            "review": review,
            "nutrition_review": ni.status(ni.context_rows(db, uid)),
            "reason": (
                "Recovery flags support reducing workload."
                if review["recovery"]["status"] == "reduce"
                else "Repeated missed/failed sessions support reducing workload."
            )
            if reduce
            else "Hold or progress only where actual comparable performance supports it.",
            "note": f"Review checkpoint week {checkpoint}. Only later weeks may change; previous weeks and recorded history stay intact. At week 12 review the next training cycle with your coach. Weight fluctuation alone never triggers a replacement. No missed-session catch-up volume.",
            "checkin_id": check.id,
            "base_plan_id": active.id,
            "source_profile_id": source.id,
            "source_workout_ids": sorted(log["record_id"] for log in logs),
        }
        row = append_record(db, uid, "reassessment", report)
    return record_json(row)


@app.post("/api/reassessments/{report_id}/proposal")
def reassessment_proposal(report_id: str, uid=Depends(auth)):
    with account_write(uid) as db:
        report = db.get(Record, report_id)
        if not report or report.user_id != uid or report.kind != "reassessment":
            raise HTTPException(404, "Reassessment not found")
        active = latest_record(db, uid, "plan")
        source = latest_record(db, uid, "profile")
        check = latest_checkin(db, uid)
        if (
            not active
            or not source
            or not check
            or report.payload.get("base_plan_id") != active.id
            or report.payload.get("source_profile_id") != source.id
            or report.payload.get("checkin_id") != check.id
            or report.payload.get("source_workout_ids", [])
            != sorted(log["record_id"] for log in lineage_logs(db, uid, active))
        ):
            raise HTTPException(409, "Inputs changed; run a fresh reassessment")
        checkpoint = report.payload.get("review_week", 4)
        if checkpoint < active.payload.get("review_week", 0):
            raise HTTPException(
                409, "Checkpoint precedes the saved review; choose a current or later checkpoint"
            )
        if checkpoint == 12:
            raise HTTPException(
                422,
                "Week 12 closes this cycle. Review a new cycle with your coach; no remaining weeks can be changed.",
            )
        logs = lineage_logs(db, uid, active)
        if any(int(log["session_id"].split("-")[0][1:]) > checkpoint for log in logs):
            raise HTTPException(
                409, "Later weeks are already logged; choose a later reassessment checkpoint"
            )
        candidate = make_plan(source, check, report.payload["suggested_days"])
        review = progression_review(
            active.payload, logs, Profile.model_validate(source.payload), check.payload
        )
        proposed = adapt_future(candidate, active.payload, review, checkpoint)
        row = append_record(
            db,
            uid,
            "proposal",
            {
                "base_plan_id": active.id,
                "source_workout_ids": sorted(
                    log["record_id"] for log in lineage_logs(db, uid, active)
                ),
                "source_profile_id": source.id,
                "source_checkin_id": check.id,
                "reassessment_id": report.id,
                "before_days": active.payload["days"],
                "after_days": proposed["days"],
                "reason": report.payload["reason"],
                "plan": proposed,
                "status": "pending",
            },
        )
    return record_json(row)


@app.get("/api/reassessments")
def reassessments(uid=Depends(auth)):
    return [record_json(r) for r in records(uid, "reassessment")]


@app.post("/api/coach")
async def coach(data: CoachRequest, uid=Depends(auth)):
    if data.use_ai:
        await run_in_threadpool(quota, uid, "ai", settings.ai_per_day, 86400)
        await run_in_threadpool(reserve_ai)
    with Session() as db:
        ctx = cc.load(db, uid)
        if not ctx["profile"]:
            raise HTTPException(404, "Save a profile first")
        p = Profile.model_validate(ctx["profile"].payload)
        logs = lineage_logs(db, uid, ctx["training"]) if ctx["training"] else []
        source_binding = cc.binding(ctx)
        source_logs = sorted(log["record_id"] for log in logs)
        context = cc.assemble(p, ctx, logs, data.message)
    result = await MMAAgentService.respond(data, p, ctx["training"], ctx["checks"], context=context)
    await run_in_threadpool(increment, "ai." + result.get("usage", {}).get("outcome", "unknown"))
    with account_write(uid) as db:
        current = cc.load(db, uid)
        current_logs = lineage_logs(db, uid, current["training"]) if current["training"] else []
        intent = result.pop("intent", None)
        if intent:
            try:
                if source_binding != cc.binding(current) or source_logs != sorted(
                    log["record_id"] for log in current_logs
                ):
                    raise ValueError(
                        "Saved context changed during interpretation; request a fresh preview"
                    )
                intent = CoachIntent.model_validate(intent)
                if cs.safety_reason(
                    data.message, Profile.model_validate(current["profile"].payload)
                ):
                    raise ValueError("This request requires qualified professional assessment")
                cs.authorize_intent(data.message, current["training"], intent)
                candidate = ca.candidate(current, current_logs, intent)
                action = append_record(
                    db,
                    uid,
                    "coach_proposal",
                    {
                        "binding": source_binding,
                        "source_log_ids": source_logs,
                        "intent": intent.model_dump(),
                        "permission": ca.interpret(data.message, current["training"]).model_dump(),
                        "status": "pending",
                        **candidate,
                    },
                )
                result["action_id"] = action.id
                result["action_summary"] = "Preview saved; approval required. " + " ".join(
                    candidate["changes"]
                )
            except ValueError as exc:
                result["action_error"] = str(exc)
        saved = append_record(db, uid, "conversation", result)
    return record_json(saved)


@app.get("/api/coach/actions")
def coach_proposals(uid=Depends(auth)):
    return [record_json(r) for r in records(uid, "coach_proposal")]


@app.post("/api/coach/actions/{proposal_id}/{action}")
def decide_coach_action(proposal_id: str, action: str, uid=Depends(auth)):
    if action not in ("approve", "reject"):
        raise HTTPException(422, "Choose approve or reject")
    with account_write(uid) as db:
        row = db.get(Record, proposal_id)
        if not row or row.user_id != uid or row.kind != "coach_proposal":
            raise HTTPException(404, "Coaching proposal not found")
        if row.payload["status"] != "pending":
            raise HTTPException(409, "Coaching proposal already resolved")
        if action == "approve":
            ctx = cc.load(db, uid)
            logs = lineage_logs(db, uid, ctx["training"]) if ctx["training"] else []
            if row.payload["binding"] != (
                cc.binding(ctx) if "reassessment_ids" in row.payload["binding"] else ni.binding(ctx)
            ) or row.payload["source_log_ids"] != sorted(log["record_id"] for log in logs):
                raise HTTPException(
                    409, "Context or progress changed; request a fresh coaching proposal"
                )
            try:
                if row.payload.get("permission"):
                    cs.authorize_permission(
                        CoachIntent.model_validate(row.payload["permission"]),
                        CoachIntent.model_validate(row.payload["intent"]),
                    )
                expected = ca.candidate(
                    ctx, logs, CoachIntent.model_validate(row.payload["intent"])
                )
            except ValueError as exc:
                raise HTTPException(409, str(exc)) from None
            if any(row.payload[k] != v for k, v in expected.items()):
                raise HTTPException(409, "Proposed changes no longer validate")
            if row.payload["target"] == "assessment":
                saved = append_record(db, uid, "coach_assessment", expected["assessment"])
            elif row.payload["target"] == "nutrition":
                saved = append_record(db, uid, "nutrition", expected["nutrition_plan"])
            else:
                active = ctx["training"]
                payload = {
                    **expected["plan"],
                    "version": active.version + 1,
                    "lineage_id": active.payload.get("lineage_id", active.id),
                    "history_plan_ids": sorted(
                        {active.id, *active.payload.get("history_plan_ids", [])}
                    ),
                }
                saved = append_record(db, uid, "plan", payload)
            row.payload = {
                **row.payload,
                "status": "approved",
                "saved_plan_id": saved.id,
                "saved_version": saved.version,
            }
        else:
            row.payload = {**row.payload, "status": "rejected"}
    return {"status": row.payload["status"], "saved_plan_id": row.payload.get("saved_plan_id")}


@app.get("/api/coach")
def conversations(uid=Depends(auth)):
    return [record_json(r) for r in records(uid, "conversation")][-50:]


@app.get("/api/export")
def export(uid=Depends(auth)):
    with Session() as db:
        rows = list(db.scalars(select(Record).where(Record.user_id == uid)))
    return {
        "application": "MMA Performance Coach",
        "records": [{**record_json(r), "kind": r.kind} for r in rows],
    }


def analytics_window(start, end):
    try:
        return an.window(start, end)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None


@app.get("/api/analytics")
def athlete_analytics(start: date | None = None, end: date | None = None, uid=Depends(auth)):
    start, end = analytics_window(start, end)
    with Session() as db:
        return an.summarize(db, uid, start, end)


@app.get("/api/analytics/history")
def analytics_history(
    kind: Literal["checkin", "workout", "technical_achievement"] = "checkin",
    start: date | None = None,
    end: date | None = None,
    page: int = Query(1, ge=1, le=100000),
    page_size: int = Query(25, ge=1, le=100),
    uid=Depends(auth),
):
    start, end = analytics_window(start, end)
    with Session() as db:
        return an.history_page(db, uid, kind, start, end, page, page_size)


@app.get("/api/analytics/export.csv")
def analytics_export(start: date | None = None, end: date | None = None, uid=Depends(auth)):
    start, end = analytics_window(start, end)

    def stream():
        with Session() as db:
            yield from an.csv_rows(db, uid, start, end)

    return StreamingResponse(
        stream(),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=athlete-progress.csv",
            "Cache-Control": "no-store",
        },
    )


@app.post("/api/analytics/schedule")
def analytics_schedule(data: AnalyticsSchedule, uid=Depends(auth)):
    if data.start_date.weekday() != 0 or not date(
        2000, 1, 1
    ) <= data.start_date <= date.today() + timedelta(days=365):
        raise HTTPException(422, "Choose a Monday cycle start between 2000 and one year ahead")
    with account_write(uid) as db:
        active = latest_record(db, uid, "plan")
        if not active or active.id != data.plan_id:
            raise HTTPException(
                409, "Approved plan changed; reload before assigning its analytics calendar"
            )
        row = append_record(
            db,
            uid,
            "analytics_schedule",
            {
                **data.model_dump(mode="json"),
                "lineage_id": active.payload.get("lineage_id", active.id),
            },
        )
    return record_json(row)


@app.post("/api/analytics/achievements")
def technical_achievement(data: TechnicalAchievement, uid=Depends(auth)):
    if data.date > date.today():
        raise HTTPException(422, "Achievement date cannot be in the future")
    return record_json(save(uid, "technical_achievement", data.model_dump(mode="json")))


@app.get("/api/{unknown:path}")
def unknown_api(unknown: str):
    raise HTTPException(404, "Unknown API endpoint")


frontend = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if frontend.exists():
    app.mount("/", StaticFiles(directory=frontend, html=True), name="frontend")
