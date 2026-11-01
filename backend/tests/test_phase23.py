import json
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

import pytest
from test_api import client as api_client

from app import main, monitoring, operations

client = api_client


@pytest.fixture(scope="session", autouse=True)
def close_borrowed_test_engine():
    yield
    from app.db import engine

    engine.dispose()


def test_health_and_readiness_never_wait_on_counter_writes(client, monkeypatch):
    def blocked_counter(*args):
        raise AssertionError("Health must not call database telemetry")

    monkeypatch.setattr(main, "record_http", blocked_counter)
    monkeypatch.setattr(main, "quota", blocked_counter)
    monkeypatch.setattr(main, "readiness", lambda: {"ready": False})
    assert client.get("/api/health").status_code == 200
    response = client.get("/api/ready")
    assert response.status_code == 503
    assert response.headers["retry-after"] == "3"
    assert "password" not in response.text.lower()
    assert client.get("/api/health/").status_code == 404
    assert client.get("/api/ready/").status_code == 404


def test_real_blocked_child_is_killed_and_next_probe_can_run(monkeypatch):
    real_run = subprocess.run

    def stalled(*args, **kwargs):
        return real_run([sys.executable, "-c", "import time;time.sleep(30)"], **kwargs)

    monkeypatch.setattr(operations.subprocess, "run", stalled)
    monkeypatch.setattr(operations, "PROBE_TIMEOUT_SECONDS", 0.2)
    started = time.monotonic()
    assert operations.readiness()["reason"] == "probe_timeout"
    assert time.monotonic() - started < 3
    assert not operations._probe_running


def test_concurrent_probes_share_one_child(monkeypatch):
    calls = []
    barrier = threading.Barrier(6)

    def run(*args, **kwargs):
        calls.append(1)
        time.sleep(0.2)
        result = operations._unavailable("ready")
        result["database"]["ready"] = True
        return subprocess.CompletedProcess([], 0, json.dumps(result).encode(), b"")

    monkeypatch.setattr(operations.subprocess, "run", run)

    def probe(_):
        barrier.wait()
        return operations.readiness()["ready"]

    with ThreadPoolExecutor(max_workers=6) as pool:
        assert all(pool.map(probe, range(6)))
    assert len(calls) == 1


@pytest.mark.parametrize("stdout", [b"secret exception", b"[]", b'{"database":null}'])
def test_probe_output_failure_never_leaks_errors(monkeypatch, stdout):
    monkeypatch.setattr(
        operations.subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess([], 0, stdout, b"private-password"),
    )
    result = operations.report()
    assert result["database"]["ready"] is False
    assert result["metrics_available"] is False
    assert "private-password" not in json.dumps(result)


def test_report_emits_outage_without_aggregate_query(monkeypatch):
    monkeypatch.setattr(
        operations, "_bounded_probe", lambda **k: operations._unavailable("probe_timeout")
    )
    snapshot = operations.report()
    assert snapshot["counters"] == {} and not snapshot["metrics_available"]
    assert snapshot["local_alerts"][0]["code"] == "database_not_ready"


def test_monitor_recovery_auth_and_quota_trends_are_explicit():
    before = {
        "database": {"ready": False},
        "metrics_available": False,
        "application": {"available": False, "ready": False},
        "counters": {},
    }
    current = {
        "database": {"ready": True},
        "metrics_available": True,
        "application": {"available": True, "ready": True},
        "counters": {"http.total": 10, "auth.local_failure": 5, "ai.quota_denied": 1},
    }
    codes = {s["code"] for s in monitoring.evaluate_alerts(current, before)}
    assert "database_recovered" in codes and "application_recovered" in codes
    assert "authentication_failures" not in codes  # Unknown prior metrics aren't zero.
    before = {**current, "counters": {"http.total": 0}}
    codes = {s["code"] for s in monitoring.evaluate_alerts(current, before)}
    assert {"authentication_failures", "ai_quota_denials"} <= codes


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "http://localhost",
        "https://127.0.0.1",
        "http://user:secret@127.0.0.1",
        "http://127.0.0.1/path",
    ],
)
def test_collector_rejects_nonliteral_or_credentialed_origins(url):
    with pytest.raises(ValueError, match="loopback"):
        monitoring._application_status(url)


def test_auth_failures_split_between_samples_use_rolling_baseline():
    baseline = {"database": {"ready": True}, "counters": {"http.total": 0}}
    prior = {"database": {"ready": True}, "counters": {"http.total": 3, "auth.local_failure": 3}}
    current = {"database": {"ready": True}, "counters": {"http.total": 5, "auth.local_failure": 5}}
    assert "authentication_failures" not in {
        s["code"] for s in monitoring.evaluate_alerts(current, prior)
    }
    assert "authentication_failures" in {
        s["code"] for s in monitoring.evaluate_alerts(current, prior, baseline)
    }


def test_watch_does_not_compare_expired_trend_history(monkeypatch):
    ticks = iter([0, 0, 61, 61])
    monkeypatch.setattr(
        monitoring, "time", SimpleNamespace(monotonic=lambda: next(ticks), sleep=lambda _: None)
    )
    baselines = []

    def collect(url, previous, baseline):
        baselines.append(baseline)
        return {"database": {"ready": True}, "metrics_available": True, "counters": {}}

    monkeypatch.setattr(monitoring, "collect", collect)
    runtime = Path(__file__).resolve().parents[2] / ".qa-runtime"
    with tempfile.TemporaryDirectory(dir=runtime, prefix="phase23-watch-test-") as folder:
        monitoring.watch(
            "http://127.0.0.1:8000", Path(folder) / "new.jsonl", samples=2, interval=61
        )
    assert all(baseline.get("metrics_available") is False for baseline in baselines)
