"""Evidence-gated suggestions only. Logging never changes a prescription."""

from copy import deepcopy
from datetime import date, timedelta

from .exercises import CATALOG
from .schemas import Profile


def recovery_state(p, check=None):
    flags = []
    if min(p.sleep, check.get("sleep", p.sleep) if check else p.sleep) < 6:
        flags.append("Sleep below six reported hours")
    if p.recovery.strip():
        flags.append("Saved recovery concern")
    if check:
        for key, threshold, label in (
            ("fatigue", 7, "High reported fatigue"),
            ("soreness", 7, "High reported muscle soreness"),
        ):
            if check.get(key) is not None and check[key] >= threshold:
                flags.append(label)
        if check.get("readiness") is not None and check["readiness"] <= 2:
            flags.append("Low reported readiness")
    fresh = bool(check and date.fromisoformat(check["date"]) >= date.today() - timedelta(days=14))
    if p.limitations.strip():
        flags.append("Reported limitation: automated exercise prescriptions withheld")
    return {
        "status": "reduce" if flags else "stable" if fresh else "unknown",
        "flags": flags,
        "fresh_checkin": fresh,
        "note": "Subjective signals, not a diagnosis or validated readiness score. Missing/stale recovery data prevent progression suggestions. The 14-day freshness window and thresholds are conservative app rules.",
    }


def workload_summary(logs):
    cutoff = date.today() - timedelta(days=6)
    previous = cutoff - timedelta(days=7)

    def within(log, start, end):
        when = date.fromisoformat(
            log.get("completed_on") or log.get("recorded_at", date.today().isoformat())[:10]
        )
        return start <= when < end

    recent = [log for log in logs if within(log, cutoff, date.today() + timedelta(days=1))]
    prior = [log for log in logs if within(log, previous, cutoff)]
    performed = [log for log in recent if log.get("status", "completed") != "missed"]
    return {
        "last_7_days_minutes": sum(log["minutes"] for log in performed),
        "previous_7_days_minutes": sum(log["minutes"] for log in prior),
        "session_rpe_load_au": round(
            sum(
                log["minutes"] * log["effort"] for log in performed if log.get("effort") is not None
            ),
            1,
        ),
        "sessions_missing_rpe": sum(log.get("effort") is None for log in performed),
        "completed": sum(log.get("status", "completed") == "completed" for log in logs),
        "missed": sum(log.get("status") == "missed" for log in logs),
        "failed": sum(log.get("status") == "failed" for log in logs),
        "logged_completion_percent": round(
            100 * sum(log.get("status", "completed") == "completed" for log in logs) / len(logs)
        )
        if logs
        else None,
        "note": "Completion denominator is logged sessions only, not due-session attendance. Session-RPE load is minutes x reported RPE, excludes missing RPE and is not an injury-risk model. Unlogged outside training is unknown.",
    }


def progression_review(plan, logs, p, check=None):
    recovery = recovery_state(p, check)
    if any(
        log.get("fatigue") is not None
        and log["fatigue"] >= 7
        and date.today() - timedelta(days=6)
        <= date.fromisoformat(log.get("completed_on") or log.get("recorded_at", "1900-01-01")[:10])
        <= date.today()
        and log.get("status", "completed") != "missed"
        for log in logs
    ):
        recovery["status"] = "reduce"
        recovery["flags"].append("High fatigue recorded with a recent performed session")
    prescriptions = {}
    by_session = {}
    for week in plan["weeks"]:
        for session in week["sessions"]:
            by_session[session["id"]] = session
            for ex in session["exercises"]:
                prescriptions.setdefault(ex["name"], ex)
    exposures = {name: [] for name in prescriptions}
    for log in sorted(
        logs,
        key=lambda log: (
            log.get("completed_on") or log.get("recorded_at", "")[:10],
            log.get("recorded_at", ""),
            log.get("record_id", ""),
        ),
    ):
        actual = {e["exercise_name"]: e for e in log.get("performances", [])}
        for ex in by_session.get(log["session_id"], {}).get("exercises", []):
            performance = actual.get(ex["name"])
            # Missing records are evidence gaps, never assumed successful sets.
            exposures[ex["name"]].append(
                {"log": log, "performance": performance, "prescription": ex}
            )
    decisions = []
    for name, ex in prescriptions.items():
        last = exposures[name][-2:]
        if last:
            ex = last[-1]["prescription"]
        decision = {
            "exercise": name,
            "catalog_id": ex.get("catalog_id"),
            "action": "hold",
            "reason": "Two comparable completed exposures with actual performance and effort are required.",
            "target": None,
            "baseline_block_minutes": ex.get("block_minutes"),
            "baseline_rep_range": ex.get("rep_range"),
            "baseline_sets": ex.get("sets"),
        }
        if p.age < 18:
            decision["reason"] = (
                "A qualified youth coach must individualize progression; adult resistance-training evidence does not establish a youth prescription."
            )
        elif recovery["status"] == "reduce":
            decision.update(
                action="reduce",
                reason="Recovery flags: reduce effort/volume and review with your coach.",
            )
        elif recovery["status"] != "stable":
            decision["reason"] = "Fresh recovery context is missing; retain the prescription."
        elif last and any(
            date.fromisoformat(
                e["log"].get("completed_on") or e["log"].get("recorded_at", "1900-01-01")[:10]
            )
            < date.today() - timedelta(days=28)
            for e in last
        ):
            decision["reason"] = (
                "Comparable performance is older than 28 days; repeat manageable work before progression."
            )
        elif len(last) == 2 and (
            last[0]["log"].get("completed_on") or last[0]["log"].get("recorded_at", "")[:10]
        ) == (last[1]["log"].get("completed_on") or last[1]["log"].get("recorded_at", "")[:10]):
            decision["reason"] = (
                "Repeat comparable completed work on separate dates before considering progression."
            )
        elif len(last) == 2 and any(
            last[0]["prescription"].get(key) != last[1]["prescription"].get(key)
            for key in (
                ("sets", "rep_range", "target_reps")
                if ex.get("category") == "Strength"
                else ("block_minutes", "catalog_id")
            )
        ):
            decision["reason"] = (
                "Prescribed dose changed between exposures; repeat comparable work before progression."
            )
        elif len(last) == 2 and all(
            e["log"].get("status", "completed") == "completed" and e["performance"] for e in last
        ):
            sets = [e["performance"]["sets"] for e in last]
            efforts = [
                [
                    s.get("rpe") if s.get("rpe") is not None else e["log"].get("effort")
                    for s in e["performance"]["sets"]
                ]
                for e in last
            ]
            if any(v is None or v > 7 for group in efforts for v in group) or any(
                e["log"].get("effort") is not None and e["log"]["effort"] > 7 for e in last
            ):
                decision["reason"] = (
                    "Effort is missing or above the conservative progression ceiling."
                )
            elif ex.get("category") == "Strength" and ex.get("rep_range"):
                low, high = ex["rep_range"]
                low = max(low, ex.get("target_reps", low))
                if all(
                    len(group) >= ex["sets"] and all(s.get("reps", 0) >= low for s in group)
                    for group in sets
                ):
                    at_top = all(all(s["reps"] >= high for s in group) for group in sets)
                    loads = [s.get("weight_kg") for group in sets for s in group]
                    if (
                        at_top
                        and all(v is not None and v > 0 for v in loads)
                        and len(set(loads)) == 1
                    ):
                        decision.update(
                            action="increase_load",
                            target=round(loads[-1] * 1.025, 2),
                            reason="Two completed exposures at the top of the rep range with consistent load and reported effort <=7. Suggest 2.5% only if a suitable small increment is available; otherwise retain load.",
                        )
                    elif not at_top:
                        decision.update(
                            action="increase_reps",
                            target=min(high, min(s["reps"] for s in sets[-1]) + 1),
                            reason="Two comfortable completed exposures support one additional repetition per set, within the range and time cap.",
                        )
                    else:
                        decision["reason"] = (
                            "Top range reached, but a comparable external load is absent. Maintain or discuss a harder variant with your coach."
                        )
            elif ex.get("category") == "Conditioning":
                if all(
                    sum(s.get("duration_seconds") or 0 for s in group)
                    >= ex.get("block_minutes", 0) * 60
                    for group in sets
                ) and all(v <= 6 for group in efforts for v in group):
                    decision.update(
                        action="increase_duration",
                        target=round(ex["block_minutes"] * 1.05, 2),
                        reason="Two completed timed exposures at reported effort <=6 permit considering up to 5% longer at the same intensity, within session and weekly caps.",
                    )
            elif ex.get("category") == "Martial arts":
                if ex.get("coached"):
                    decision.update(
                        action="coach_review",
                        reason="Two completed coached exposures support discussing linked skills. Instructor approval and observation remain necessary; no automatic contact progression.",
                    )
        if (
            last
            and any(e["log"].get("status") in {"missed", "failed"} for e in last)
            and recovery["status"] == "stable"
        ):
            decision.update(
                action="hold",
                target=None,
                reason="A recent exposure was missed or failed. Repeat manageable work; do not make up missed volume or progress automatically.",
            )
        recent = exposures[name][-3:]
        if recovery["status"] == "stable" and len(recent) == 3:
            signatures, dates = [], set()
            for exposure in recent:
                log, perf = exposure["log"], exposure["performance"]
                dates.add(log.get("completed_on") or log.get("recorded_at", "")[:10])
                if log.get("status", "completed") != "completed" or not perf:
                    break
                signatures.append(
                    (
                        exposure["prescription"].get("sets"),
                        tuple(exposure["prescription"].get("rep_range", [])),
                        tuple(
                            (
                                s.get("reps"),
                                s.get("weight_kg"),
                                s.get("duration_seconds"),
                                s.get("distance_m"),
                            )
                            for s in perf["sets"]
                        ),
                    )
                )
            if (
                len(signatures) == 3
                and len(dates) == 3
                and min(dates) >= (date.today() - timedelta(days=28)).isoformat()
                and len(set(signatures)) == 1
            ):
                decision.update(
                    action="hold",
                    target=None,
                    reason="Three comparable recorded exposures show unchanged output. Possible plateau, not a diagnosis: review technique, effort, recovery and goals with your coach before adding work.",
                )
        decisions.append(decision)
    return {
        "recovery": recovery,
        "workload": workload_summary(logs),
        "decisions": decisions,
        "note": "Suggestions require a preview and explicit approval. RPE thresholds, two-exposure gating, 2.5% load and 5% time steps are conservative product heuristics, not a validated individualized MMA protocol.",
    }


def easy_block(ex):
    replacement = "cycle" if ex.get("catalog_id") == "cycle-interval" else "coordination"
    ex.update(
        catalog_id=replacement,
        name=CATALOG[replacement]["name"],
        category="Conditioning" if replacement == "cycle" else "Athleticism",
        sets=1,
        reps=f"{ex['block_minutes']} minutes comfortable movement",
        rpe=3,
        cue=CATALOG[replacement]["technique"],
        alternative_ids=[],
        coached=False,
        substitution="Comfortable easy movement",
    )


def adapt_future(candidate, active, review, week):
    """Keep completed/past checkpoint weeks intact; only propose changes after it."""
    result = deepcopy(candidate)
    changes = []
    lookup = {d["exercise"]: d for d in review["decisions"]}
    original_inputs = Profile.model_validate(active["inputs"]).model_dump()
    proposed_inputs = Profile.model_validate(result["inputs"]).model_dump()
    for old, new in zip(active["weeks"], result["weeks"]):
        if old["week"] <= week:
            new.clear()
            new.update(deepcopy(old))
            continue
        old_minutes = sum(s["minutes"] for s in old["sessions"])
        weekly_cap = old_minutes * (1 if review["recovery"]["status"] != "stable" else 1.05)
        for session in new["sessions"]:
            previous = next((s for s in old["sessions"] if s["id"] == session["id"]), None)
            compatible = all(
                original_inputs.get(key) == proposed_inputs.get(key)
                for key in (
                    "equipment",
                    "gym",
                    "mma_gym",
                    "experience",
                    "priority",
                    "goal",
                    "objectives",
                    "conditioning_mode",
                    "gym_years",
                    "strength_coach",
                    "power_practice",
                    "age",
                    "mobility",
                    "current_frequency",
                )
            )
            if previous and previous["type"] == session["type"] and compatible:
                permitted = {e.get("catalog_id") for e in session["exercises"]}
                duration_cap, effort_cap = session["minutes"], session["effort"]
                session.clear()
                session.update(deepcopy(previous))
                for ex in session["exercises"]:
                    if (
                        ex.get("catalog_id") in {"cycle-interval", "jump", "throw"}
                        and ex["catalog_id"] not in permitted
                    ):
                        easy_block(ex)
                session["effort"] = min(effort_cap, session["effort"])
                if duration_cap < session["minutes"]:
                    factor = (duration_cap - 10) / (session["minutes"] - 10)
                    for ex in session["exercises"]:
                        ex["block_minutes"] = round(ex["block_minutes"] * factor, 2)
                        if ex.get("category") == "Strength" and ex["block_minutes"] < 6:
                            ex["sets"] = 1
                    session["exercises"][-1]["block_minutes"] += round(
                        duration_cap - 10 - sum(e["block_minutes"] for e in session["exercises"]), 2
                    )
                    session["minutes"] = duration_cap
            prior_minutes = (
                previous["minutes"]
                if previous
                else min((s["minutes"] for s in old["sessions"]), default=session["minutes"])
            )
            prior_effort = (
                previous["effort"]
                if previous
                else min((s["effort"] for s in old["sessions"]), default=4)
            )
            session["effort"] = min(session["effort"], prior_effort)
            if session["minutes"] > prior_minutes:
                factor = (prior_minutes - 10) / (session["minutes"] - 10)
                for ex in session["exercises"]:
                    ex["block_minutes"] = round(ex["block_minutes"] * factor, 2)
                    if ex.get("category") != "Strength":
                        ex["reps"] = f"{ex['block_minutes']} minutes with comfortable breaks"
                    elif ex["block_minutes"] < 6:
                        ex["sets"] = 1
                difference = round(
                    prior_minutes - 10 - sum(ex["block_minutes"] for ex in session["exercises"]), 2
                )
                session["exercises"][-1]["block_minutes"] += difference
                session["minutes"] = prior_minutes
        # Candidate frequency must never make the weekly time budget grow >5%.
        while sum(s["minutes"] for s in new["sessions"]) > weekly_cap and new["sessions"]:
            new["sessions"].pop()
        for session in new["sessions"]:
            if review["recovery"]["status"] == "reduce":
                session["effort"] = min(session["effort"], 4)
            for ex in session["exercises"]:
                if (
                    ex.get("catalog_id") == "cycle-interval"
                    and ex["block_minutes"] < 9
                    or ex.get("category") == "Explosive practice"
                    and ex["block_minutes"] < 4
                ):
                    easy_block(ex)
                ex["rpe"] = min(ex.get("rpe", session["effort"]), session["effort"])
                decision = lookup.get(ex["name"], {})
                action = decision.get("action")
                applied = False
                if new["deload"] or review["recovery"]["status"] == "reduce":
                    ex["sets"] = 1
                    ex["rpe"] = min(ex.get("rpe", 4), 4)
                    if (
                        ex.get("catalog_id") == "cycle-interval"
                        or ex.get("category") == "Explosive practice"
                    ):
                        easy_block(ex)
                    continue
                if action in {"increase_load", "increase_reps"} and (
                    ex.get("rep_range") != decision.get("baseline_rep_range")
                    or ex.get("sets") != decision.get("baseline_sets")
                ):
                    continue
                if action == "increase_load":
                    ex["suggested_load_kg"] = decision["target"]
                    applied = True
                elif action == "increase_reps":
                    ex["reps"] = f"{decision['target']} per set; stop at time cap"
                    ex["target_reps"] = decision["target"]
                    applied = True
                elif action == "increase_duration" and ex["block_minutes"] == decision.get(
                    "baseline_block_minutes"
                ):
                    headroom = min(
                        result["inputs"]["minutes"] - session["minutes"],
                        weekly_cap - sum(s["minutes"] for s in new["sessions"]),
                    )
                    addition = max(0, min(decision["target"] - ex["block_minutes"], headroom))
                    if addition:
                        ex["block_minutes"] = round(ex["block_minutes"] + addition, 2)
                        session["minutes"] = round(session["minutes"] + addition, 2)
                        ex["reps"] = f"{ex['block_minutes']} minutes at conversational effort"
                        applied = True
                if applied:
                    changes.append(
                        f"Week {new['week']} {session['day']}: {ex['name']} - {decision['reason']}"
                    )
            session["time_note"] = (
                f"10 minutes warm-up/cool-down plus {round(sum(e['block_minutes'] for e in session['exercises']), 2)} minutes work, including rests. Session cap {session['minutes']} minutes."
            )
            session["effort"] = min(
                session["effort"], max((e.get("rpe", 4) for e in session["exercises"]), default=4)
            )
    result["review_week"] = week
    result["changes"] = list(dict.fromkeys(changes)) or [
        "Hold manageable prescriptions or reduce recovery load; no performance increase is supported."
    ]
    result["weekly_minutes"] = [
        round(sum(s["minutes"] for s in w["sessions"]), 2) for w in result["weeks"]
    ]
    result["continuation"] = True
    return result
