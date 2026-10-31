"""Transparent observations and preference/access allocation; no professional norms."""

DISCIPLINES = ("Boxing", "Muay Thai", "Kickboxing", "BJJ", "Wrestling", "Judo", "MMA")
TECHNICAL_FOCUS = {
    "Boxing": "striking stance, guard recovery and defensive exits",
    "Muay Thai": "balanced striking and coached clinch positioning",
    "Kickboxing": "balanced punching/kicking combinations and defensive exits",
    "BJJ": "positional awareness, escapes and positional grappling",
    "Wrestling": "stance, level changes and coached takedown defense",
    "Judo": "instructor-led balance and breakfall preparation; no solo throws",
    "MMA": "coached transitions between striking and positional grappling",
    "Clinch": "coached posture and positional clinch control",
}


def discipline_stage(p, ex):
    if not ex:
        return "Unknown: experience not entered"
    if ex.months < 12 or ex.level in {"None", "Beginner", "Novice"}:
        return "Fundamental skill acquisition"
    if ex.months >= 36 and ex.level in {"Advanced", "Competitive"} and p.mma_gym and ex.instructor:
        return "Coach-led technical refinement"
    return "Coached consolidation"


def discipline_priorities(p):
    known = {e.discipline: e for e in p.experience}
    candidates = list(dict.fromkeys([*p.preferred, *known, *DISCIPLINES, "Clinch"]))
    rows = []
    for d in candidates:
        ex = known.get(d)
        interested = ex.interested if ex else d in p.preferred
        access = bool(p.mma_gym and ex and ex.instructor)
        score = (
            4 * interested
            + 3 * (d in p.preferred)
            + 2 * access
            + bool(ex and ex.weaknesses.strip())
            + 2 * bool(ex and ex.technical_goals.strip())
        )
        # Existing sessions are already training load, not a reason to add more classes.
        score -= min(ex.sessions, 3) if ex else 0
        if d.lower() in " ".join([p.goal, *p.objectives]).lower():
            score += 8
        if ex and ex.enjoyment is not None:
            score += 2 if ex.enjoyment >= 4 else -2 if ex.enjoyment <= 2 else 0
        rows.append(
            {
                "discipline": d,
                "score": score,
                "purpose": f"Support {p.goal}. "
                + (
                    "Discuss the recorded skill gap with your instructor."
                    if ex and ex.weaknesses.strip()
                    else "Build coached fundamentals and defensive awareness."
                ),
                "frequency": "Use existing classes within the weekly availability cap; rotate optional practice rather than adding sessions.",
                "access": "Recorded instructor access"
                if access
                else "Arrange qualified instruction before contact or partner drills",
                "evidence": f"Interest: {'yes' if interested else 'not selected'}; preferred: {'yes' if d in p.preferred else 'no'}; existing weekly classes: {ex.sessions if ex else 0}. Skill gaps are self-reported.",
                "interested": interested,
                "enjoyment": ex.enjoyment if ex else None,
                "stage": discipline_stage(p, ex),
                "technical_goals": ex.technical_goals if ex else "",
                "focus": TECHNICAL_FOCUS.get(
                    d, "Discuss discipline-specific goals with a qualified instructor"
                ),
                "recorded": ex is not None,
                "months": ex.months if ex else None,
                "sessions": ex.sessions if ex else None,
                "proficiency": ex.level if ex else "Not entered",
                "development_reason": (
                    f"Recorded goals: {ex.technical_goals}. "
                    if ex and ex.technical_goals
                    else "No discipline-specific goal entered. "
                )
                + (f"Self-reported gap: {ex.weaknesses}. " if ex and ex.weaknesses else "")
                + (
                    "Use the existing coached slot; instructor decides progression."
                    if access
                    else "No verified coaching access; use solo movement only while arranging instruction."
                ),
            }
        )
    rows.sort(key=lambda r: (-r["score"], r["discipline"]))
    return [{**r, "priority": i + 1} for i, r in enumerate(rows)]


def athletic_assessment(p, check=None):
    benchmark_check = check
    benchmarks = check.get("benchmarks", []) if check else [b.model_dump() for b in p.benchmarks]
    if not benchmarks:
        benchmarks = [b.model_dump() for b in p.benchmarks]
        benchmark_check = None
    weight = benchmark_check["weight_kg"] if benchmark_check else p.weight_kg
    observations, estimates = [], []
    for b in benchmarks:
        domain = (
            "Relative strength"
            if b["unit"] == "kg"
            else "Aerobic performance"
            if b["name"] in {"1km", "5km"}
            else "Explosive performance"
            if "jump" in b["name"].lower()
            else "Acceleration"
            if b["name"] == "100m"
            else "Muscular endurance"
        )
        row = {
            "name": b["name"],
            "domain": domain,
            "value": b["value"],
            "unit": b["unit"],
            "reps": b["reps"],
            "effort": b["effort"],
            "provenance": b["provenance"],
            "derived": None,
            "note": "User-entered observation; no professional-athlete comparison or normative rating.",
        }
        if b["unit"] == "kg":
            row["derived"] = (
                f"{b['value'] / weight:.2f} x recorded body mass for {b['reps']} reps; not an estimated 1RM."
            )
        elif b["name"] in {"1km", "5km"}:
            row["derived"] = (
                f"{round(b['value'] / (5 if b['name'] == '5km' else 1), 1)} seconds/km from the entered test; not a VO2max estimate."
            )
        (estimates if b["provenance"] == "estimated" else observations).append(row)
    return {
        "observations": observations,
        "estimates": estimates,
        "mobility": (check or {}).get("mobility", p.mobility),
        "experience": f"{p.gym_years} years strength training; technical experience remains self-reported.",
        "recovery": "Subjective recovery flags guide conservative suggestions; physiological recovery capacity is not measured.",
        "missing_domains": [
            d
            for d in (
                "Relative strength",
                "Muscular endurance",
                "Aerobic performance",
                "Explosive performance",
            )
            if not any(r["domain"] == d for r in observations)
        ],
        "note": "Measured labels are user-supplied, not independently verified. Compare the same protocol, units, repetitions and evidence label. Jump distance/height is a result, not a power measurement. No maximal testing is requested.",
        "development": development_model(p, observations, estimates, check),
    }


def development_model(p, observations, estimates, check):
    """Ten independent dimensions, no composite athlete/proficiency score."""

    def observed(domain):
        return [r for r in observations if r["domain"] == domain]

    strength = observed("Relative strength")
    technical = discipline_priorities(p)
    axes = []
    for name, rows, evidence, limits in [
        (
            "General strength",
            strength,
            [f"{r['name']}: {r['value']} kg for {r['reps']} reps" for r in strength],
            "Recorded external loads, not a maximum or strength rating.",
        ),
        (
            "Relative strength",
            strength,
            [r["derived"] for r in strength],
            "Load/body mass uses the accompanying recorded weight; no 1RM inferred.",
        ),
        (
            "Aerobic conditioning",
            observed("Aerobic performance"),
            [r["derived"] for r in observed("Aerobic performance")],
            "Run result/pace, not VO2max or MMA endurance.",
        ),
        (
            "Anaerobic conditioning",
            [],
            [],
            "No validated repeated-effort protocol is collected. Sprint time and interval attendance do not establish anaerobic capacity.",
        ),
        (
            "Explosive performance",
            observed("Explosive performance"),
            [f"{r['name']}: {r['value']} {r['unit']}" for r in observed("Explosive performance")],
            "Jump result, not measured power or fighting ability.",
        ),
        (
            "Mobility",
            [],
            [f"Self-assessed: {(check or {}).get('mobility', p.mobility)}"],
            "No joint-specific objective assessment.",
        ),
        (
            "Training experience",
            [],
            [f"{p.gym_years} gym years; {p.current_frequency} current sessions/week"],
            "Self-reported training age, not verified competence.",
        ),
        (
            "Technical martial arts experience",
            [],
            [f"{r['discipline']}: {r['proficiency']}" for r in technical if r["recorded"]],
            "Independent discipline histories; no anthropometric skill inference.",
        ),
        (
            "Recovery and fatigue",
            [],
            [
                f"Sleep: {(check or {}).get('sleep', p.sleep)} hours",
                f"Check-in fatigue: {(check or {}).get('fatigue', 'not entered')}",
            ],
            "Subjective and date-sensitive; not a physiological capacity test.",
        ),
        (
            "Training availability",
            [],
            [
                f"Up to {p.days} days, {p.minutes} minutes/day",
                ", ".join(p.available_days) if p.available_days else "Exact weekdays not entered",
            ],
            "Calendar assumptions remain visible; class dates/durations are unknown.",
        ),
    ]:
        status = (
            "Recorded observation"
            if rows
            else "Self-reported context"
            if name in {"Training experience", "Recovery and fatigue", "Training availability"}
            or evidence
            and name in {"Mobility", "Technical martial arts experience"}
            else "Missing objective data"
        )
        if name == "Mobility" and (check or {}).get("mobility", p.mobility) == "Unknown":
            status = "Missing objective data"
        axes.append({"dimension": name, "status": status, "evidence": evidence, "limits": limits})
    return {
        "dimensions": axes,
        "technical": [r for r in technical if r["discipline"] in DISCIPLINES],
        "directions": [
            {
                "direction": r["focus"],
                "reason": r["development_reason"],
                "discipline": r["discipline"],
            }
            for r in technical
            if r["interested"]
        ][:5],
        "estimate_count": len(estimates),
        "note": "No composite score, professional norm or optimal fighting style is inferred. Missing data are not a zero score. Technical stages and priorities are transparent coaching-allocation heuristics.",
    }
