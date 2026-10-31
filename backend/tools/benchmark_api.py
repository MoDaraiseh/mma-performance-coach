"""Local disposable-DB timings, not a production load/capacity claim."""

import json
import os
import statistics
import sys
import tempfile
import time
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "backend"))
runtime = root / ".qa-runtime"
runtime.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=runtime, prefix="perf-") as folder:
    os.environ.update(
        DATABASE_URL="sqlite:///" + str(Path(folder) / "perf.db"),
        APP_ENV="test",
        OPENAI_API_KEY="",
        COOKIE_SECURE="false",
        API_PER_MINUTE="100000",
        AUTH_PER_MINUTE="1000",
    )
    from fastapi.testclient import TestClient
    from sqlalchemy import select

    from app.db import Base, Session, User, engine
    from app.main import app, latest, records
    from app.repository import account_write, append_record

    Base.metadata.create_all(engine)
    results = {}
    phase = os.getenv("MMA_QA_PHASE", "phase6")
    if phase not in {"phase6", "phase13", "phase14"}:
        raise ValueError("Unsupported evidence phase")
    with TestClient(app) as client:
        client.post("/api/auth/register")
        client.post("/api/demo")
        with Session() as db:
            uid = db.scalar(select(User.id))
        with account_write(uid) as db:
            for i in range(1000):
                append_record(db, uid, "benchmark", {"index": i, "padding": "x" * 1024})
        if phase in {"phase13", "phase14"}:
            from datetime import date, timedelta

            with account_write(uid) as db:
                for i in range(1000):
                    append_record(
                        db,
                        uid,
                        "checkin",
                        {
                            "date": (date.today() - timedelta(days=i)).isoformat(),
                            "weight_kg": 78,
                            "sleep": 8,
                            "fatigue": 3,
                        },
                    )
        for name, operation in {
            "old_latest_1000_versions": lambda: max(
                records(uid, "benchmark"), key=lambda r: r.version
            ),
            "indexed_latest_1000_versions": lambda: latest(uid, "benchmark"),
            "assessment": lambda: client.get("/api/assessment"),
            "fighter_matching": lambda: client.post("/api/fighter-matches", json={}),
            "fighter_search": lambda: client.get("/api/fighters?q=alex"),
            "nutrition": lambda: client.get("/api/nutrition"),
            **(
                {
                    "analytics_1000_events": lambda: client.get("/api/analytics?start=2020-01-01"),
                    "history_page": lambda: client.get("/api/analytics/history?page_size=25"),
                }
                if phase in {"phase13", "phase14"}
                else {}
            ),
        }.items():
            values = []
            for _ in range(20):
                start = time.perf_counter()
                value = operation()
                if hasattr(value, "status_code"):
                    assert value.status_code == 200, (name, value.status_code)
                values.append((time.perf_counter() - start) * 1000)
            results[name] = {
                "samples": len(values),
                "median_ms": round(statistics.median(values), 2),
                "p95_ms": round(sorted(values)[18], 2),
            }
        if phase in {"phase13", "phase14"}:
            from concurrent.futures import ThreadPoolExecutor

            def request(_):
                start = time.perf_counter()
                response = client.get("/api/auth/session")
                return response.status_code, (time.perf_counter() - start) * 1000

            with ThreadPoolExecutor(max_workers=8) as pool:
                samples = list(pool.map(request, range(32)))
            assert all(status == 200 for status, _ in samples)
            results["concurrent_sessions"] = {
                "requests": 32,
                "workers": 8,
                "all_status_200": True,
                "median_ms": round(statistics.median(t for _, t in samples), 2),
                "max_ms": round(max(t for _, t in samples), 2),
            }
    engine.dispose()
    output = root / (
        f"docs/evidence/{phase}/api-performance.json"
        if phase in {"phase13", "phase14"}
        else "docs/evidence/phase6/performance.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
