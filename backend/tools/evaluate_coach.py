"""Synthetic offline/live smoke evaluation. Never loads athlete records or edits plans."""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.mma_agent import MMAAgentService
from app.schemas import CoachRequest, Profile


async def run(args):
    if args.live and not (
        os.getenv("MMA_LIVE_COACH_EVAL") == "1"
        and os.getenv("OPENAI_API_KEY")
        and os.getenv("OPENAI_MODEL")
    ):
        raise SystemExit(
            "Live evaluation requires explicit MMA_LIVE_COACH_EVAL=1, OPENAI_API_KEY and OPENAI_MODEL. Calls may incur charges."
        )
    cases = json.loads(
        (Path(__file__).resolve().parents[1] / "tests/fixtures/coach_evaluations.json").read_text()
    )
    results = []
    for case in cases[: args.limit]:
        p = Profile(metabolic_sex="male", **case.get("profile", {}))
        response = await MMAAgentService.respond(
            CoachRequest(message=case["question"], use_ai=args.live),
            p,
            None,
            [],
            context={
                "goal": p.goal,
                "age_group": "adult",
                "approved_plan": None,
                "nutrition": None,
                "fighter_matches": [],
                "evidence_policy": "Synthetic incomplete context, all athlete inputs self-reported. No real athlete information.",
            },
        )
        results.append(
            {
                "case": case["id"],
                "mode": response["mode"],
                "answer": response["answer"],
                "limitations": response["limitations"],
                "usage": response["usage"],
            }
        )
    print(
        json.dumps(
            {
                "live_requested": args.live,
                "model": os.getenv("OPENAI_MODEL") if args.live else None,
                "manual_quality_review_required": True,
                "plan_writes": 0,
                "results": results,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--limit", type=int, choices=range(1, 19), default=3)
    asyncio.run(run(parser.parse_args()))
