"""Reproducible operator coverage report; no athlete reads/writes or network requests."""

import json
import sys
from collections import Counter
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root / "backend"))
    from app.exercises import CATALOG as exercises
    from app.fighter_governance import quality
    from app.fighters import SeededFighterProvider
    from app.ingredients import CATALOG as foods
    from app.ingredients import VERSION, validate_catalog
    from app.nutrition import NutritionPlanService
    from app.nutrition_models import NutritionPreferences
    from app.schemas import Profile

    records = SeededFighterProvider().all()
    validate_catalog(list(foods.values()))
    meals = NutritionPlanService.generate(Profile(metabolic_sex="male"), NutritionPreferences())
    assert meals["available"]
    result = {
        "fighter_sources": quality(records),
        "food_catalog": {
            "version": VERSION,
            "foods": len(foods),
            "roles": dict(Counter(f["role"] for f in foods.values())),
            "nutrient_coverage": {
                k: sum(f["per_100g"].get(k) is not None for f in foods.values())
                for k in next(iter(foods.values()))["per_100g"]
            },
            "certified_halal": 0,
            "current_price_records": 0,
            "source": "USDA SR Legacy April 2018; CC0; editorial screening is not certification",
        },
        "exercise_catalog": {
            "exercises": len(exercises),
            "categories": dict(Counter(e["category"] for e in exercises.values())),
            "requires_coach": sum(e["requires_coach"] for e in exercises.values()),
            "independent_expert_approval": False,
        },
        "synthetic_default_meal_plan": {
            "meals": sum(len(d["meals"]) for d in meals["days"]),
            "distinct_compositions": len(
                {m["recipe_id"] for d in meals["days"] for m in d["meals"]}
            ),
            "maximum_calorie_target_difference": max(
                abs(d["totals"]["calories"] - meals["target_calories"]) for d in meals["days"]
            ),
            "note": "One synthetic profile, not clinical adequacy, independent taste testing or population validation",
        },
        "athlete_data_accessed": False,
        "network_requests": 0,
    }
    directory = root / "docs/evidence/phase15"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "data-quality.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
