"""Synthetic isolated query benchmark, never a real-roster coverage count."""

import json
import os
import statistics
import sys
import tempfile
import time
from copy import deepcopy
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "backend"))
runtime = root / ".qa-runtime"
runtime.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=runtime, prefix="fighter-perf-") as folder:
    os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(folder) / "qa.db")
    from sqlalchemy import event

    from app.db import Base, FighterSnapshot, Session, engine
    from app.fighters import DatabaseFighterProvider, SeededFighterProvider
    from app.matching import FighterMatchingService
    from app.schemas import MatchWeights, Profile

    Base.metadata.create_all(engine)
    f = SeededFighterProvider().all()[-1]
    with Session.begin() as db:
        for n in range(1000):
            item = deepcopy(f)
            item.update(id=f"qa-{n:04}", name=f"Synthetic {n:04}")
            db.add(FighterSnapshot(id=item["id"], payload=item, verified_at=item["verified_at"]))
    output = {"fixture": "1000 synthetic records, not verified fighters", "measurements": {}}
    for name, operation in {
        "search_page": lambda: DatabaseFighterProvider().search("Synthetic", page=20, page_size=25),
        "manual_lookup": lambda: DatabaseFighterProvider().get("qa-0475"),
        "rank": lambda: FighterMatchingService(DatabaseFighterProvider()).rank(
            Profile(division="Women"), MatchWeights()
        ),
    }.items():
        queries = []
        durations = []

        def capture(*args):
            queries.append(args[2])

        event.listen(engine, "before_cursor_execute", capture)
        for _ in range(10):
            started = time.perf_counter()
            operation()
            durations.append(1000 * (time.perf_counter() - started))
        event.remove(engine, "before_cursor_execute", capture)
        output["measurements"][name] = {
            "samples": 10,
            "median_ms": round(statistics.median(durations), 2),
            "queries_per_operation": len(queries) / 10,
        }
    engine.dispose()
    phase = os.getenv("MMA_QA_PHASE", "phase8")
    if phase not in {"phase8", "phase13", "phase14"}:
        raise ValueError("Unsupported evidence phase")
    path = root / (
        f"docs/evidence/{phase}/fighter-performance.json"
        if phase in {"phase13", "phase14"}
        else "docs/evidence/phase8/performance.json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
