"""Interpretation is untrusted; only these bounded edits can be proposed."""

import re
from copy import deepcopy

from . import nutrition_integrity as ni
from .athletics import athletic_assessment
from .exercises import CATALOG, alternatives
from .ingredients import CATALOG as FOODS
from .nutrition_models import CoachIntent, NutritionChange
from .plan_integrity import make_plan, plan_status
from .progression import adapt_future, progression_review
from .schemas import Profile
from .training import TrainingPlanService

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def interpret(message, active=None):
    q = message.lower()
    if any(t in q for t in ("do not change", "don't change", "do not modify", "never modify")):
        return None
    if any(t in q for t in ("fighter", "matches")) and any(
        t in q for t in ("why", "explain", "differences", "similarities")
    ):
        return CoachIntent(kind="explain_matches")
    if not re.match(
        r"^(?:please\s+|can you\s+|could you\s+)?(?:make|shorten|reschedule|move|replace|substitute|suggest|propose|change|set|fit|add|schedule|request|update|reassess|progress|reduce|increase|give|what is a substitute|how can i fit|how do i adjust)\b",
        q.strip(),
    ):
        return None
    if any(s in q for s in ("why", "explain")) and not any(
        s in q for s in ("change", "shorter", "replace", "substitute")
    ):
        return None
    week = (
        int(m.group(1))
        if (m := re.search(r"week\s+(\d+)", q))
        else max(1, (active.payload.get("review_week", 0) + 1) if active else 1)
    )
    day = next((d for d in DAYS if d.lower() in q), None)
    if any(t in q for t in ("reassess", "updated assessment", "update my assessment")):
        return CoachIntent(kind="request_assessment")
    if "reschedule" in q or re.search(r"\bmove\b", q):
        named = re.findall("|".join(d.lower() for d in DAYS), q)
        if len(named) != 2:
            raise ValueError("Specify source and destination weekdays")
        return CoachIntent(
            kind="reschedule_workout", week=week, day=named[0].title(), target_day=named[1].title()
        )
    if any(t in q for t in ("frequency", "days per week", "days a week")):
        count = re.search(r"\b([1-6])\s*(?:days|sessions)", q)
        return CoachIntent(
            kind="change_frequency", week=week, days=int(count.group(1)) if count else None
        )
    if "progress" in q and any(t in q for t in ("training", "workout", "plan")):
        return CoachIntent(kind="progress_training", week=week)
    if any(s in q for s in ("lunch", "breakfast", "dinner", "snack")) and any(
        s in q for s in ("different", "substitut", "replace", "alternative", "change")
    ):
        match = re.search(r"day\s+(\d+)", q)
        food = next(
            (
                key
                for key, item in sorted(FOODS.items(), key=lambda r: -len(r[1]["name"]))
                if any(
                    re.search(r"\b" + re.escape(term) + r"\b", q)
                    for term in (key.replace("-", " "), item["name"].split(" (")[0].lower())
                )
            ),
            None,
        )
        if not food and re.search(r"\bwith\s+(?!similar\b|comparable\b|equivalent\b)", q):
            raise ValueError(
                "Requested food is not recognized in the verified catalog; choose a catalog ingredient"
            )
        return CoachIntent(
            kind="meal_swap",
            food_id=food,
            meal_day=int(match.group(1)) if match else 1,
            meal=next(
                (
                    m
                    for m in ("Breakfast", "Lunch", "Dinner", "Recovery snack")
                    if m.split()[-1].lower() in q
                ),
                "Lunch",
            ),
        )
    if "shorter" in q or "shorten" in q:
        minutes = re.search(r"(\d+)\s*(?:minutes|mins|minute|min)\b", q)
        return CoachIntent(
            kind="shorten_session",
            week=week,
            day=day,
            minutes=int(minutes.group(1)) if minutes else None,
        )
    if "boxing" in q and any(s in q for s in ("fit", "add", "schedule")):
        return CoachIntent(kind="schedule_boxing", week=week, day=day)
    if any(s in q for s in ("substitut", "replace", "alternative")):
        key = next(
            (key for key, item in CATALOG.items() if item["name"].lower() in q or key in q), None
        )
        if key:
            return CoachIntent(kind="exercise_substitution", week=week, day=day, exercise_id=key)
    return None


def candidate(ctx, logs, intent):
    if intent.kind == "request_assessment":
        p = Profile.model_validate(ctx["profile"].payload)
        check = (
            max(ctx["checks"], key=lambda r: (r.payload["date"], r.version))
            if ctx["checks"]
            else None
        )
        report = athletic_assessment(p, check.payload if check else None)
        return {
            "target": "assessment",
            "assessment": report,
            "changes": [
                "Recalculate athletic observations and estimates from current saved inputs. Approval saves an assessment snapshot; no measurements, plans or checkpoint are changed."
            ],
        }
    if intent.kind == "exercise_substitution" and intent.exercise_id not in CATALOG:
        raise ValueError("Specify an exercise in the current catalog")
    if intent.kind == "meal_swap":
        meal_plan = ni.proposed(
            ctx,
            NutritionChange(
                kind="meal_swap",
                day=intent.meal_day,
                meal=intent.meal,
                protein_id=intent.protein_id,
                food_id=intent.food_id,
            ),
        )
        return {
            "target": "nutrition",
            "nutrition_change": NutritionChange(
                kind="meal_swap",
                day=intent.meal_day,
                meal=intent.meal,
                protein_id=intent.protein_id,
                food_id=intent.food_id,
            ).model_dump(),
            "nutrition_plan": meal_plan,
            "changes": meal_plan["changes"],
        }
    active, source = ctx["training"], ctx["profile"]
    if not active:
        raise ValueError("Generate and approve a training plan first")
    check = (
        max(ctx["checks"], key=lambda r: (r.payload["date"], r.version)) if ctx["checks"] else None
    )
    if plan_status(active, source, check)["needs_review"]:
        raise ValueError("Training profile or recovery changed; approve a current-input plan first")
    p = Profile.model_validate(source.payload)
    if intent.week <= active.payload.get("review_week", 0):
        raise ValueError("Choose a future week after the reviewed checkpoint")
    result = deepcopy(active.payload)
    week = next(w for w in result["weeks"] if w["week"] == intent.week)
    if intent.kind in {"change_frequency", "progress_training"}:
        if any(int(r["session_id"].split("-")[0][1:]) >= intent.week for r in logs):
            raise ValueError("Choose a future week after all logged sessions")
        review = progression_review(active.payload, logs, p, check.payload if check else None)
        if intent.kind == "change_frequency":
            if intent.days is None or intent.days > p.days:
                raise ValueError(
                    "Specify a frequency within your saved availability; edit your profile to increase availability"
                )
            fresh = make_plan(source, check, intent.days)
            review["decisions"] = []  # frequency authorization never authorizes progression
        else:
            if review["recovery"]["status"] != "stable" or not any(
                d["action"] != "hold" for d in review["decisions"]
            ):
                raise ValueError(
                    "No evidence-supported progression with fresh stable recovery; log comparable completed performance and recovery first"
                )
            fresh = deepcopy(active.payload)
        proposed = adapt_future(fresh, active.payload, review, intent.week - 1)
        if proposed["weeks"] == active.payload["weeks"]:
            raise ValueError("No feasible distinct training change is supported")
        # A preview does not advance a completed reassessment checkpoint.
        proposed["review_week"] = active.payload.get("review_week", 0)
        changes = (
            proposed["changes"]
            if intent.kind == "progress_training"
            else [
                f"From week {intent.week}, requested {intent.days} training days; actual schedule remains subject to recovery and workload caps. Earlier weeks and logs remain unchanged."
            ]
        )
        proposed["changes"] = changes
        return {
            "target": "training",
            "plan": proposed,
            "changes": changes,
            "before_week": deepcopy(week),
            "after_week": deepcopy(proposed["weeks"][intent.week - 1]),
            "from_week": intent.week,
        }
    sessions = week["sessions"]
    if intent.day:
        sessions = [s for s in sessions if s["day"] == intent.day]
    if intent.kind == "exercise_substitution":
        sessions = [
            s
            for s in sessions
            if any(e.get("catalog_id") == intent.exercise_id for e in s["exercises"])
        ]
    if intent.kind == "schedule_boxing":
        sessions = [
            s for s in sessions if any(e.get("category") == "Martial arts" for e in s["exercises"])
        ]
    logged = {r["session_id"] for r in logs}
    sessions = [s for s in sessions if s["id"] not in logged]
    if not sessions:
        raise ValueError(
            "No eligible unlogged session on the requested day/week. Choose an existing future session; no extra session was added."
        )
    if intent.kind == "shorten_session" and not intent.day:
        raise ValueError("Specify the existing session day to shorten")
    session = sessions[0]
    before = deepcopy(session)
    if intent.kind == "reschedule_workout":
        if not intent.day or not intent.target_day or intent.target_day == intent.day:
            raise ValueError("Specify distinct source and destination weekdays")
        if p.available_days and intent.target_day not in p.available_days:
            raise ValueError("Destination is outside saved weekday availability")
        if any(s["day"] == intent.target_day for s in week["sessions"]):
            raise ValueError("Destination already has a session; no double sessions are added")
        if any(e.get("coached") for e in session["exercises"]):
            raise ValueError(
                "Coordinate coached class moves with your instructor; only uncoached sessions can be rescheduled"
            )
        destination = (intent.week - 1) * 7 + DAYS.index(intent.target_day)
        if session["effort"] >= 7 and any(
            s is not session
            and s["effort"] >= 7
            and abs((w["week"] - 1) * 7 + DAYS.index(s["day"]) - destination) <= 1
            for w in result["weeks"]
            for s in w["sessions"]
        ):
            raise ValueError("Move would cluster hard sessions; choose a recovery-separated day")
        session["day"] = intent.target_day
        week["sessions"].sort(key=lambda s: DAYS.index(s["day"]))
        explanation = f"Week {intent.week}: move {before['day']} to {intent.target_day}, preserving session identity, exercises and minutes. No class booking is claimed."
    elif intent.kind == "shorten_session":
        minutes = intent.minutes or max(20, session["minutes"] - 15)
        if not 20 <= minutes < session["minutes"] or minutes > p.minutes:
            raise ValueError(
                "New duration must be at least 20 minutes and shorter than the saved session"
            )
        effective = Profile.model_validate(active.payload["inputs"]).model_copy(
            update={"minutes": minutes}
        )
        generated = TrainingPlanService.generate(effective)
        replacement = next(
            (
                s
                for w in generated["weeks"]
                if w["week"] == intent.week
                for s in w["sessions"]
                if s["day"] == session["day"]
            ),
            None,
        )
        if not replacement:
            raise ValueError("Unable to preserve this session's day within the training template")
        session.clear()
        session.update(replacement)
        explanation = f"Week {intent.week} {session['day']}: {before['minutes']} → {session['minutes']} minutes. Rebuild only this session's timed prescription; no catch-up volume or extra days. Review changed exercises below."
    elif intent.kind == "exercise_substitution":
        ex = next(e for e in session["exercises"] if e.get("catalog_id") == intent.exercise_id)
        options = [
            e
            for e in alternatives(intent.exercise_id, p)
            if e["category"] == CATALOG[intent.exercise_id]["category"]
            and e["name"] not in {other["name"] for other in session["exercises"]}
        ]
        alternative = (
            next((e for e in options if e["id"] == intent.alternative_id), None)
            if intent.alternative_id
            else next(iter(options), None)
        )
        if not alternative:
            raise ValueError("No eligible equipment/category-compatible alternative")
        old_name = ex["name"]
        ex.update(
            name=alternative["name"],
            catalog_id=alternative["id"],
            cue=alternative["technique"],
            alternative_ids=[a["id"] for a in alternatives(alternative["id"], p)],
            substitution=alternative["modification_notes"],
        )
        ex.pop("suggested_load_kg", None)
        explanation = f"{session['id']}: {old_name} → {ex['name']}. Existing timed block and effort cap retained."
    elif intent.kind == "schedule_boxing":
        ex = next(e for e in session["exercises"] if e.get("category") == "Martial arts")
        # Preserve an existing solo block; new contact/coached work is not inferred.
        if ex.get("coached"):
            raise ValueError(
                "Coordinate changes to existing coached classes with your instructor; this app will not replace them with an inferred boxing class"
            )
        item = CATALOG["footwork"]
        ex.update(
            name=item["name"],
            catalog_id="footwork",
            coached=False,
            technique_focus="Solo boxing stance, jab-recovery footwork and defensive exits; no contact or partner drills.",
            cue="Discuss a coached boxing class with your instructor before replacing any class. Keep solo work comfortable within the existing time block.",
        )
        explanation = f"{session['id']}: focus the existing non-contact technical block on boxing footwork. No extra training time or coached class is claimed."
    else:
        raise ValueError("No supported action requested")
    if sum(e["block_minutes"] for e in session["exercises"]) > session["minutes"] - 10 + 0.1:
        raise ValueError("Prescription exceeds the session time budget")
    result.update(
        continuation=True,
        changes=[explanation],
        weekly_minutes=[sum(s["minutes"] for s in w["sessions"]) for w in result["weeks"]],
    )
    return {
        "target": "training",
        "plan": result,
        "changes": [explanation],
        "before_session": before,
        "after_session": deepcopy(session),
    }
