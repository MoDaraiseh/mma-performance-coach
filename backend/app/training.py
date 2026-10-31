"""Conservative, time-budgeted templates; not rehabilitation or competition clearance."""

from .athletics import TECHNICAL_FOCUS, discipline_priorities, discipline_stage
from .exercises import CATALOG, alternatives, available_equipment
from .schemas import Profile

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class TrainingPlanService:
    @staticmethod
    def generate(p: Profile):
        cautious = p.sleep < 6 or bool(p.recovery) or p.age < 18 or p.intensity == "Gentle"
        count = min(p.days, 3 if cautious else 6)
        if p.gym_years < 1 and p.current_frequency < 3:
            count = min(count, 4)
        slots = {
            1: [0],
            2: [0, 3],
            3: [0, 2, 4],
            4: [0, 1, 3, 5],
            5: [0, 1, 2, 4, 5],
            6: [0, 1, 2, 3, 4, 5],
        }[count]
        if p.available_days:
            chosen = [i for i, day in enumerate(DAYS) if day in p.available_days]
            slots = chosen[:count]
            count = len(slots)
        novice_strength = p.gym_years < 1
        goal_text = " ".join([p.goal, *p.objectives]).lower()
        priority = (
            p.priority
            if p.priority != "Balanced"
            else "Strength"
            if any(word in goal_text for word in ("strength", "stronger", "muscle"))
            else "Conditioning"
            if any(word in goal_text for word in ("conditioning", "aerobic", "endurance"))
            else "Balanced"
        )
        priorities = discipline_priorities(p)
        lead = next((r["discipline"] for r in priorities if r["interested"]), "Boxing")
        have = available_equipment(p)
        existing_classes = sum(e.sessions for e in p.experience if e.instructor and e.months > 0)
        class_pool = [
            e.discipline
            for e in p.experience
            if e.instructor and e.months > 0
            for _ in range(min(e.sessions, p.days))
        ]
        technical = {
            "Boxing": [
                "stance and jab recovery",
                "defensive exits and footwork",
                "jab-to-exit sequences",
            ],
            "Muay Thai": [
                "balanced stance and guard",
                "defensive footwork",
                "coached clinch positioning",
            ],
            "Wrestling": [
                "stance and level changes",
                "coached entries and defense",
                "coached transitions",
            ],
            "BJJ": [
                "positional awareness and safe movement",
                "coached positional escapes",
                "coached transitions",
            ],
        }
        weeks = []
        for week in range(1, 13):
            interval_used = False
            phase_index = (week - 1) // 4
            deload = week in (4, 8, 12)
            phase = ["Foundation", "Development", "Consolidation"][phase_index]
            base = min(p.minutes, 40 if p.current_frequency or p.gym_years >= 1 else 30)
            duration = min(p.minutes, base)
            if deload:
                duration = max(15, int(duration * 0.7))
            sessions = []
            for index, slot in enumerate(slots):
                kind = ["Strength", "Technique", "Conditioning"][index % 3]
                if count == 1 or count == 2 and index == 0:
                    kind = "Mixed fundamentals"
                elif count == 2:
                    kind = "Technique"
                if 0 < index <= min(existing_classes, max(0, count - 1)):
                    kind = "Technique"
                if priority == "Conditioning" and index == 3:
                    kind = "Conditioning"
                rpe = (
                    4
                    if cautious or deload
                    else min(6, {"Gentle": 4, "Balanced": 5, "Challenging": 6}[p.intensity])
                )
                total_work_budget = duration - 10
                mobility_minutes = min(3, total_work_budget // 4)
                work_budget = total_work_budget - mobility_minutes
                # All sessions explicitly include skill, strength or aerobic/mobility blocks;
                # short availability uses smaller blocks rather than impossible extra sessions.
                if kind == "Mixed fundamentals":
                    blocks = [
                        ("Strength", max(1, work_budget // 2)),
                        ("Technique", max(1, work_budget // 4)),
                    ]
                elif kind == "Strength":
                    share = 0.85 if priority == "Strength" else 0.7
                    blocks = [("Strength", max(4, int(work_budget * share)))]
                elif kind == "Technique":
                    blocks = [("Technique", max(4, int(work_budget * 0.7)))]
                else:
                    blocks = [("Conditioning", work_budget)]
                used = sum(minutes for _, minutes in blocks)
                if used < work_budget:
                    blocks.append(("Conditioning", work_budget - used))
                work = []
                for category, minutes in blocks:
                    if category == "Strength":
                        power = (
                            p.power_practice
                            and p.strength_coach
                            and 18 <= p.age < 65
                            and not cautious
                            and not deload
                            and p.gym_years >= 1
                            and p.mobility == "Comfortable"
                            and minutes >= 12
                        )
                        if power:
                            key = "throw" if "medicine_ball" in have else "jump"
                            work.append(
                                {
                                    "name": CATALOG[key]["name"],
                                    "catalog_id": key,
                                    "category": "Explosive practice",
                                    "sets": 2,
                                    "reps": "3 controlled repetitions",
                                    "rest": "60–90 seconds; all recovery inside the 4-minute block",
                                    "rpe": 5,
                                    "block_minutes": 4,
                                    "coached": True,
                                    "cue": CATALOG[key]["technique"]
                                    + " Stop as soon as movement quality drops; coach selects height/load. No maximal attempts.",
                                    "substitution": "Omit explosive work and use comfortable coordination practice.",
                                }
                            )
                            minutes -= 4
                        ids = [
                            "goblet-squat" if "dumbbells" in have else "chair-squat",
                            "row" if {"dumbbells", "bench"} <= have else "prone-y",
                            "incline-push" if "bench" in have else "wall-push",
                            "hip-hinge",
                            "dead-bug",
                        ]
                        if index >= 3:
                            ids = [
                                "romanian-deadlift"
                                if "dumbbells" in have and not novice_strength
                                else "bridge",
                                "split-squat",
                                "dead-bug",
                                "overhead-press"
                                if "dumbbells" in have and not novice_strength
                                else "wall-push",
                                "carry" if "dumbbells" in have else "bird-dog",
                            ]
                        ids = ids[: max(1, min(len(ids), minutes // 4))]
                        for key in ids:
                            item = CATALOG[key]
                            name = item["name"]
                            cue = item["technique"]
                            substitution = (
                                "; ".join(e["name"] for e in alternatives(key, p))
                                or "Ask your coach for a suitable alternative."
                            )
                            sets = 1 if minutes < 12 or deload or novice_strength else 2
                            work.append(
                                {
                                    "name": name,
                                    "catalog_id": key,
                                    "rep_range": [6, 8] if novice_strength or deload else [8, 12],
                                    "rpe": rpe,
                                    "category": category,
                                    "sets": sets,
                                    "reps": "6–8" if novice_strength or deload else "8–12",
                                    "rest": "45–60 seconds",
                                    "cue": cue
                                    + " Keep about three comfortable repetitions in reserve; never work through pain.",
                                    "substitution": substitution,
                                    "block_minutes": round(minutes / len(ids), 2)
                                    if key != ids[-1]
                                    else round(
                                        minutes - round(minutes / len(ids), 2) * (len(ids) - 1), 2
                                    ),
                                }
                            )
                    elif category == "Technique":
                        session_lead = (
                            class_pool[index - 1] if 0 < index <= len(class_pool) else lead
                        )
                        coached = p.mma_gym and any(
                            e.discipline == session_lead and e.instructor for e in p.experience
                        )
                        curriculum = technical.get(
                            session_lead,
                            [
                                "stance and defensive movement",
                                "coached fundamental transitions",
                                "coached skill integration",
                            ],
                        )
                        technical_key = {
                            "Boxing": "boxing",
                            "Muay Thai": "muay-thai",
                            "Wrestling": "wrestling",
                            "BJJ": "bjj",
                            "Clinch": "clinch",
                            "MMA": "mma",
                            "Kickboxing": "kickboxing",
                            "Judo": "judo",
                        }.get(session_lead, "footwork")
                        allowed = (
                            coached
                            and technical_key != "footwork"
                            and set(CATALOG[technical_key]["equipment"]) <= have
                        )
                        experience = next(
                            (e for e in p.experience if e.discipline == session_lead), None
                        )
                        key = technical_key if allowed else "footwork"
                        name = CATALOG[key]["name"]
                        focus = (
                            f"Coached {session_lead}: {discipline_stage(p, experience)}; {TECHNICAL_FOCUS.get(session_lead, curriculum[0])}. "
                            + (
                                f"Recorded technical goal: {experience.technical_goals}. "
                                if experience and experience.technical_goals
                                else ""
                            )
                            + "Instructor observes technique before changing task complexity."
                            if allowed
                            else "Solo footwork and non-contact movement"
                        )
                        work.append(
                            {
                                "name": name,
                                "catalog_id": key,
                                "coached": allowed,
                                "technique_focus": focus,
                                "rpe": min(rpe, 5),
                                "category": "Martial arts",
                                "sets": 1,
                                "reps": f"{minutes} minutes with easy breaks",
                                "rest": "As needed within the block",
                                "cue": "Instructor controls all partner practice; no unsupervised sparring, throws or submissions."
                                if allowed
                                else f"Practice comfortable balance and footwork. Arrange qualified {session_lead} instruction before partner technique; self-reported skill is unverified.",
                                "substitution": "Easy non-contact movement and a discussion with your instructor.",
                                "block_minutes": minutes,
                            }
                        )
                    else:
                        mode = {
                            "cycling": "cycle",
                            "rowing": "row-erg",
                            "run_walk": "run-walk",
                            "jump_rope": "rope",
                            "interval_cycling": "cycle-interval",
                            "walking": "walk",
                        }.get(p.conditioning_mode, "cycle" if "bike" in have else "walk")
                        item = CATALOG[mode]
                        interval_ok = (
                            kind == "Conditioning"
                            and not interval_used
                            and not deload
                            and not cautious
                            and 18 <= p.age < 65
                            and p.gym_years >= 1
                            and p.current_frequency >= 3
                            and p.mobility == "Comfortable"
                            and sum(e.sessions for e in p.experience) <= 2
                        )
                        if (
                            not set(item["equipment"]) <= have
                            or (
                                item["difficulty"] != "Beginner"
                                and (cautious or p.current_frequency < 3 or p.mobility == "Limited")
                            )
                            or (mode == "cycle-interval" and (minutes < 9 or not interval_ok))
                        ):
                            mode = "walk"
                        if mode == "cycle-interval":
                            interval_used = True
                            rpe = 7
                        work.append(
                            {
                                "name": CATALOG[mode]["name"],
                                "catalog_id": mode,
                                "rpe": 7 if mode == "cycle-interval" else min(rpe, 5),
                                "category": "Conditioning",
                                "sets": 1,
                                "reps": f"{minutes} minutes",
                                "rest": "As needed within the block",
                                "cue": (
                                    "Three rounds: 1 minute controlled work at RPE 7, 2 minutes easy. No all-out efforts; remaining block time is easy cycling."
                                    if mode == "cycle-interval"
                                    else CATALOG[mode]["technique"]
                                )
                                + " Stay within the time cap. Requested unavailable or unsuitable modes fall back to comfortable walking.",
                                "substitution": "Comfortable easy walking or seated cycling.",
                                "block_minutes": minutes,
                            }
                        )
                work.append(
                    {
                        "name": CATALOG["mobility"]["name"],
                        "catalog_id": "mobility",
                        "category": "Athleticism",
                        "sets": 1,
                        "reps": f"{mobility_minutes} minutes",
                        "rest": "As needed",
                        "cue": CATALOG["mobility"]["technique"],
                        "substitution": "Comfortable walking",
                        "block_minutes": mobility_minutes,
                        "rpe": 2,
                    }
                )
                for exercise in work:
                    exercise["progression_rule"] = (
                        "Progress only through a reviewed proposal after two comparable completed exposures with actual sets and effort; hold after missed/failed work or recovery flags. Keep all work and rest inside this block."
                    )
                    exercise["alternative_ids"] = [
                        e["id"] for e in alternatives(exercise["catalog_id"], p)
                    ]
                sessions.append(
                    {
                        "id": f"w{week}-d{slot}",
                        "day": DAYS[slot],
                        "type": kind,
                        "objective": f"{phase}: {kind.lower()}, {priority.lower()} emphasis. Technical focus follows recorded experience and instructor review; preserve recovery.",
                        "minutes": duration,
                        "effort": rpe,
                        "warmup": "5 minutes easy movement and joint preparation",
                        "exercises": work,
                        "cooldown": "5 minutes easy walking and comfortable mobility",
                        "time_note": f"10 minutes warm-up/cool-down + {total_work_budget} minutes of timed work blocks = {duration} minutes. Stop at each block's time cap; do fewer sets when needed.",
                        "recovery": "Keep at least one full rest day. Reduce effort if recovery deteriorates and seek qualified assessment for pain.",
                    }
                )
            if p.limitations.strip():
                sessions = []
            weeks.append(
                {
                    "week": week,
                    "phase": phase,
                    "deload": deload,
                    "sessions": sessions,
                    "focus": "Reduce work and reassess comparable benchmarks"
                    if deload
                    else "Learn comfortable, repeatable fundamentals"
                    if phase_index == 0
                    else "Within the time cap, add repetitions only after comfortable technique and recovery"
                    if phase_index == 1
                    else "Consolidate skill and compare consistent assessments",
                }
            )
        return {
            "available": not bool(p.limitations.strip()),
            "reason": "Automatic exercise prescriptions are withheld for reported training limitations. Obtain an individualized plan from a qualified professional; update the limitation only when appropriate."
            if p.limitations.strip()
            else None,
            "weeks": weeks,
            "days": count if not p.limitations.strip() else 0,
            "requested_days": p.days,
            "version": 1,
            "planning_priority": priority,
            "catalog_version": "2026-10-phase7",
            "existing_class_sessions": existing_classes,
            "recovery_days": DAYS[:]
            if p.limitations.strip()
            else [day for day in DAYS if day not in [DAYS[s] for s in slots]],
            "availability_note": "Exact selected weekdays are respected; days beyond the day-count cap are recovery."
            if p.available_days
            else "Weekdays use a template because exact availability was not entered.",
            "power_note": "Requested explosive practice requires an adult trained profile, comfortable mobility, suitable recovery and recorded strength-coach access; otherwise withheld. No injury clearance is inferred.",
            "scheduling_note": f"{existing_classes} recorded instructor-led classes are treated as part of, not additional to, the {count}-day budget. Exact class dates/durations are unknown; align this roadmap with your coach. Technical slots first reflect recorded class disciplines, then rotate the selected priority; this is not a dated timetable or a guarantee that every outside class fits.",
            "discipline_priorities": priorities,
            "weekly_minutes": [sum(s["minutes"] for s in w["sessions"]) for w in weeks],
            "inputs": p.model_dump(),
            "method": "Catalog template v4. Timed blocks respect selected weekdays and the daily cap; beginners with little current training are capped at four days, recovery-sensitive profiles at three. Technical goals and independently recorded histories guide coached acquisition/consolidation/refinement, never calendar-based complexity. Requested supervised explosive practice and one controlled cycling interval block/week have explicit adult/experience/recovery gates; otherwise withheld. Weeks 4/8/12 offer deload and review, not automatic overload. Actual comparable performance and explicit approval govern progression. Advanced competition programming requires individual coach review.",
            "limitations": "Not rehabilitation or competition clearance. Injury text is not interpreted as a diagnosis. No automatic exercise plan for reported limitations; no contact prescription without qualified supervision.",
        }
