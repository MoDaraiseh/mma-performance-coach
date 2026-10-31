"""Generate synthetic review examples without opening an athlete database or provider."""

import json
import os
import sys
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite://"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.analysis import PhysicalProfileService, WeightClassService  # noqa: E402
from app.athletics import athletic_assessment, discipline_priorities  # noqa: E402
from app.nutrition import NutritionPlanService  # noqa: E402
from app.schemas import Profile  # noqa: E402
from app.training import TrainingPlanService  # noqa: E402

CASES = {
    "adult_beginner": {"metabolic_sex": "male", "days": 6, "minutes": 60},
    "trained_supervised": {
        "metabolic_sex": "female",
        "days": 6,
        "gym_years": 4,
        "current_frequency": 5,
        "mobility": "Comfortable",
        "power_practice": True,
        "strength_coach": True,
        "equipment": ["bike", "medicine_ball", "dumbbells"],
        "conditioning_mode": "interval_cycling",
    },
    "minor": {"age": 16, "days": 6, "metabolic_sex": "male"},
    "injury_conflict": {
        "limitations": "Knee pain; wants jump practice",
        "power_practice": True,
        "strength_coach": True,
        "metabolic_sex": "male",
    },
    "rapid_cut_request": {"goal": "Lose 10 kg in 3 days", "metabolic_sex": "male"},
    "unknown_allergy": {"allergies": ["unmapped rare allergen"], "metabolic_sex": "male"},
    "low_recovery": {
        "sleep": 3,
        "recovery": "Persistent exhaustion reported",
        "days": 6,
        "metabolic_sex": "male",
    },
}


def build():
    rows = []
    for name, values in CASES.items():
        p = Profile(**values)
        training = TrainingPlanService.generate(p)
        nutrition = NutritionPlanService.generate(p, training=training)
        rows.append(
            {
                "case": name,
                "profile": p.model_dump(),
                "physical": PhysicalProfileService.assess(p),
                "division": WeightClassService.assess(p),
                "athletics": athletic_assessment(p),
                "technical_priorities": discipline_priorities(p),
                "training": {
                    **{
                        k: v
                        for k, v in training.items()
                        if k not in {"weeks", "inputs", "discipline_priorities"}
                    },
                    "example_weeks": [w for w in training["weeks"] if w["week"] in (1, 4)],
                },
                "nutrition": {
                    k: ([v[0]] if k == "days" and v else v)
                    for k, v in nutrition.items()
                    if k not in {"inputs", "grocery"}
                },
            }
        )
    return {
        "synthetic": True,
        "independent_review": "pending",
        "nutrition_days_shown": "first day only; engine generates seven",
        "examples": rows,
    }


if __name__ == "__main__":
    destination = Path(__file__).resolve().parents[2] / "docs" / "review" / "examples.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(build(), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Generated {len(CASES)} synthetic examples: {destination}")
