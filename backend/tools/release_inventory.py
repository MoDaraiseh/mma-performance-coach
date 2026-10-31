"""Validate bundled data and record runtime availability without opening athlete data."""

import json
import os
import platform
import shutil
import sys
from collections import Counter
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root / "backend"))

    from app.exercises import CATALOG as exercises
    from app.fighters import SeededFighterProvider
    from app.ingredients import CATALOG as foods
    from app.ingredients import validate_catalog

    fighters = SeededFighterProvider().all()
    validate_catalog(list(foods.values()))
    history = Counter(
        (r["competition_division"], d["name"]) for r in fighters for d in r["division_history"]
    )
    report = {
        "validated_fighter_snapshots": len(fighters),
        "categories": dict(Counter(r["competition_division"] for r in fighters)),
        "historical_divisions": [
            {"category": c, "division": d, "count": n} for (c, d), n in sorted(history.items())
        ],
        "career_status_snapshots": dict(Counter(r["career_status"] for r in fighters)),
        "field_coverage": {
            k: sum(bool(r.get(k)) for r in fighters)
            for k in (
                "height_cm",
                "reach_cm",
                "listed_weight_kg",
                "stance",
                "background",
                "statistics",
                "record",
                "style_traits",
            )
        },
        "sources_reverified_online_this_phase": False,
        "food_count": len(foods),
        "food_nutrients_present": {
            k: sum(r["per_100g"].get(k) is not None for r in foods.values())
            for k in next(iter(foods.values()))["per_100g"]
        },
        "exercise_count": len(exercises),
        "licensing_limit": "Original 11 fighter source snapshots have unestablished redistribution rights; eight attributed CC BY-SA adaptations. Foods USDA SR Legacy April 2018; editorial allergen metadata is not certification.",
    }
    runtime = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "executables": {
            k: shutil.which(k)
            for k in ("docker", "psql", "postgres", "pg_ctl", "pg_dump", "pg_restore")
        },
        "test_database_url_configured": bool(os.getenv("MMA_TEST_DATABASE_URL")),
        "live_provider_calls": 0,
        "public_deployment": False,
        "independent_expert_approval": False,
    }
    phase = os.getenv("MMA_QA_PHASE", "phase14")
    if phase not in {"phase14", "phase17", "phase18"}:
        raise ValueError("Unsupported evidence phase")
    directory = root / f"docs/evidence/{phase}"
    directory.mkdir(parents=True, exist_ok=True)
    for name, value in (("data-quality", report), ("runtime", runtime)):
        (directory / f"{name}.json").write_text(json.dumps(value, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
