"""Full synthetic training/nutrition outputs for Phase18 reviewers; never athlete data."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["DATABASE_URL"] = "sqlite://"

from app.nutrition import NutritionPlanService  # noqa: E402
from app.schemas import Profile  # noqa: E402
from app.training import TrainingPlanService  # noqa: E402
from tools.build_review_examples import CASES  # noqa: E402


def build():
    cases = []
    for name, values in CASES.items():
        profile = Profile(**values)
        training = TrainingPlanService.generate(profile)
        cases.append(
            {
                "case": name,
                "synthetic_profile": profile.model_dump(mode="json"),
                "full_training": training,
                "full_nutrition": NutritionPlanService.generate(profile, training=training),
            }
        )
    return {"synthetic": True, "professional_approval": "pending", "examples": cases}


if __name__ == "__main__":
    output = (
        Path(__file__).resolve().parents[2] / "docs/evidence/phase18/specialist-full-examples.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    result = build()
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"synthetic_cases": len(result["examples"]), "output": str(output)}))
