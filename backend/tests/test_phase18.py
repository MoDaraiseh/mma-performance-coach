import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from app.monitoring import evaluate_alerts
from tools.prepare_staging import ROOT, build_context, prepare


@pytest.fixture
def staging_folder():
    runtime = ROOT / ".qa-runtime"
    runtime.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="phase18-test-", dir=runtime) as folder:
        yield Path(folder)


def test_staging_context_excludes_originals_and_private_runtime(staging_folder):
    source = ROOT / "backend/app/fighter_catalog.py"
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    result = build_context(staging_folder / "context")
    files = result["files"]
    assert result["original_fighter_records_excluded"] == 11
    assert not any(".test." in p or "/tests/" in p or p.endswith(".db") for p in files)
    assert not any(p.startswith((".env", ".git/", "docs/evidence/")) for p in files)
    assert "return []" in (staging_folder / "context/backend/app/fighter_catalog.py").read_text()
    assert "docs/FIGHTER_SUPPLEMENT_LICENSE.md" in files
    assert "third_party_notices/dm-sans.txt" in files
    assert "COPY third_party_notices/" in (staging_folder / "context/deploy/Dockerfile").read_text()
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before


def test_preparation_separates_secrets_and_never_overwrites(staging_folder):
    destination = staging_folder / "prepared"
    result = prepare(destination)
    values = {p.stem: p.read_text() for p in (destination / "secrets").glob("*.txt")}
    assert len(set(values.values())) == 3
    app = (destination / "app.env").read_text()
    migration = (destination / "migration.env").read_text()
    assert values["runtime"] in app and values["migrator"] not in app and values["admin"] not in app
    assert values["migrator"] in migration and values["runtime"] not in migration
    assert "OPENAI_API_KEY=\n" in app and "AI_GLOBAL_DAILY=0" in app
    assert not result["services_started"] and not result["legal_approval"]
    with pytest.raises(ValueError, match="new destination"):
        prepare(destination)
    assert (destination / "app.env").read_text() == app


def test_context_rejects_outside_workspace_without_writes(tmp_path):
    with pytest.raises(ValueError, match="inside"):
        build_context(Path(tempfile.gettempdir()) / "mma-phase18-outside-context")


def test_sanitized_context_migration_and_actual_app_workflow(staging_folder):
    destination = staging_folder / "context"
    build_context(destination)
    env = {
        **os.environ,
        "DATABASE_URL": "sqlite:///" + str(staging_folder / "synthetic.db"),
        "APP_ENV": "test",
        "IDENTITY_MODE": "local",
        "ALLOW_LEGACY_RECOVERY": "true",
        "COOKIE_SECURE": "false",
        "OPENAI_API_KEY": "",
        "API_PER_MINUTE": "100000",
        "AUTH_PER_MINUTE": "1000",
        "AI_GLOBAL_DAILY": "0",
        "AI_GLOBAL_MONTHLY": "0",
    }
    cwd = destination / "backend"
    for args in (["-m", "alembic", "upgrade", "head"], ["-m", "alembic", "check"]):
        subprocess.run([sys.executable, *args], cwd=cwd, env=env, capture_output=True, check=True)
    code = """
from fastapi.testclient import TestClient
from app.main import app
from app.db import engine
from app.operations import report
with TestClient(app) as c:
    assert c.get('/api/ready').status_code == 200
    assert report()['database']['ready'] and 'local_alerts' in report()
    recovery = c.post('/api/auth/register').json()['recovery_token']
    assert c.post('/api/demo').status_code == 200
    fighters = c.get('/api/fighters/search').json()
    assert fighters['total'] == 8
    assert all(s['rights'] == 'licensed' for f in fighters['items'] for s in f['sources'])
    assert c.post('/api/fighter-matches', json={}).status_code == 200
    assert c.get('/api/training-plans').json()['id']
    assert c.get('/api/nutrition').json()['id']
    assert c.post('/api/coach', json={'message':'Why prioritize wrestling?', 'use_ai':True}).status_code == 429
    assert c.post('/api/coach', json={'message':'Why prioritize wrestling?', 'use_ai':False}).status_code == 200
    assert c.delete('/api/account').status_code == 200
    assert c.post('/api/auth/restore', json={'token':recovery}).status_code == 401
engine.dispose()
"""
    completed = subprocess.run([sys.executable, "-c", code], cwd=cwd, env=env, capture_output=True)
    assert completed.returncode == 0, completed.stderr.decode(errors="replace")


def test_staging_compose_is_loopback_internal_and_least_privilege():
    data = json.loads((ROOT / "deploy/compose.staging.json").read_text())
    assert data["networks"]["isolated"]["internal"]
    services = data["services"]
    assert "ports" not in services["database"]
    assert services["app"]["ports"] == ["127.0.0.1:18018:8000"]
    assert services["app"]["env_file"] != services["migrate"]["env_file"]
    assert services["app"]["read_only"] and services["app"]["cap_drop"] == ["ALL"]
    assert all(
        services[name]["pull_policy"] == "never" for name in ("app", "migrate", "restore-app")
    )
    assert "volumes" not in data


def snapshot(**counters):
    return {"database": {"ready": True}, "counters": counters}


def test_local_alerts_outage_errors_auth_and_no_private_labels():
    current = snapshot(**{"http.total": 100, "http.503": 10, "auth.oidc_failure": 5})
    current["database"]["ready"] = False
    current["untrusted_note"] = "private token must never appear"
    signals = evaluate_alerts(current, snapshot(**{"http.total": 0}))
    assert {s["code"] for s in signals} == {
        "database_not_ready",
        "http_error_rate",
        "authentication_failures",
    }
    assert "private token" not in json.dumps(signals)


def test_counter_restart_and_small_sample_do_not_invent_error_rate():
    assert not evaluate_alerts(
        snapshot(**{"http.total": 5, "http.503": 5}), snapshot(**{"http.total": 100})
    )
    assert not evaluate_alerts(
        snapshot(**{"http.total": 19, "http.503": 19}), snapshot(**{"http.total": 0})
    )


def test_ai_budget_alerts_are_reservations_not_billing():
    current = snapshot()
    current["ai"] = {
        "daily_outbound_ceiling": 10,
        "monthly_outbound_ceiling": 100,
        "reserved_outbound_attempts": {"day:synthetic": 8, "month:synthetic": 80},
    }
    assert len(evaluate_alerts(current)) == 2
    current["ai"]["daily_outbound_ceiling"] = 0
    current["ai"]["monthly_outbound_ceiling"] = 0
    assert not evaluate_alerts(current)


@pytest.mark.parametrize(
    "value",
    [
        None,
        {},
        {"database": {"ready": "yes"}},
        {"database": {"ready": True}, "counters": {"http.total": -1}},
    ],
)
def test_malformed_monitoring_is_explicit(value):
    assert evaluate_alerts(value)[0]["code"] == "invalid_snapshot"
