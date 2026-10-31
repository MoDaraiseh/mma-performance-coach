"""Windowed descriptive analytics. No synthetic baselines, diagnosis or plan writes."""

import csv
import hashlib
import io
import math
from collections import Counter, defaultdict
from datetime import date, timedelta

from sqlalchemy import func, select

from . import nutrition_integrity as ni
from .db import Record
from .repository import latest_record

KINDS = ("checkin", "workout", "technical_achievement")
MAX_EVENTS = 2000
DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
LIMITATIONS = [
    "All observations are user-entered, including those labeled measured; none is independently verified.",
    "Window baselines and personal records use only the selected interval and disclosed loaded coverage, never an invented profile starting date.",
    "Compare the same exercise/test, units, repetition count, evidence label and testing conditions. Effort and technique still affect comparability.",
    "Body mass ratios use only a measurement on the same date. No 1RM, VO2max, wattage, fighting proficiency or medical diagnosis is inferred.",
    "Trends describe observations; they establish neither causation nor a predicted rate of improvement. Unlogged practice is unknown.",
]


def normalize(value, unit):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError("A finite nonnegative observation is required")
    factors = {
        "kg": (1, "kg"),
        "lb": (0.45359237, "kg"),
        "seconds": (1, "seconds"),
        "minutes": (60, "seconds"),
        "cm": (1, "cm"),
        "m": (100, "cm"),
        "reps": (1, "reps"),
    }
    if unit not in factors:
        raise ValueError("Unsupported measurement unit")
    factor, target = factors[unit]
    return value * factor, target


def window(start=None, end=None):
    end = end or date.today()
    start = start or end - timedelta(days=89)
    if end > date.today() or start > end or (end - start).days > 3650:
        raise ValueError("Choose an ordered interval up to 3651 days ending no later than today")
    return start, end


def history_query(uid, kind, start, end):
    return select(Record).where(
        Record.user_id == uid,
        Record.kind == kind,
        Record.event_date >= start.isoformat(),
        Record.event_date <= end.isoformat(),
    )


def history_page(db, uid, kind, start, end, page=1, page_size=25):
    query = history_query(uid, kind, start, end)
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    rows = list(
        db.scalars(
            query.order_by(Record.event_date.desc(), Record.version.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {"id": r.id, "version": r.version, "date": r.event_date, "data": r.payload}
            for r in rows
        ],
    }


def trend(points, direction="higher"):
    # One last observation per date avoids treating repeated same-day entries as independent evidence.
    by_date = {p["date"]: p for p in points}
    ordered = [by_date[k] for k in sorted(by_date)]
    if not ordered:
        return {
            "samples": 0,
            "status": "missing",
            "note": "No observations; no baseline or trend inferred.",
        }
    first, last = ordered[0], ordered[-1]
    delta = round(last["value"] - first["value"], 4)
    span = (date.fromisoformat(last["date"]) - date.fromisoformat(first["date"])).days
    result = {
        "samples": len(ordered),
        "span_days": span,
        "baseline": first,
        "current": last,
        "delta": delta,
        "direction": direction,
    }
    if len(ordered) < 3 or span < 14:
        result.update(
            status="limited",
            note="Limited evidence: at least three distinct dates spanning 14 days are required for a trend observation.",
        )
    elif delta == 0:
        stagnant = span >= 28 and all(p["value"] == first["value"] for p in ordered)
        result.update(
            status="unchanged" if stagnant else "variable",
            note="Unchanged recorded output over at least 28 days; review protocol, effort and consistency before calling this a plateau."
            if stagnant
            else "Baseline and latest match, but this is not sufficient evidence of stagnation.",
        )
    else:
        improved = (delta > 0) if direction == "higher" else (delta < 0)
        result.update(
            status=("increased" if delta > 0 else "decreased")
            if direction == "neutral"
            else "improved"
            if improved
            else "lower_result",
            note="Descriptive change in comparable recorded values, not evidence of cause, a diagnosis or a forecast.",
        )
    return result


def summarize(db, uid, start, end):
    query = select(Record).where(
        Record.user_id == uid,
        Record.kind.in_(KINDS),
        Record.event_date >= start.isoformat(),
        Record.event_date <= end.isoformat(),
    )
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    rows = list(
        db.scalars(
            query.order_by(
                Record.event_date.desc(), Record.created_at.desc(), Record.version.desc()
            ).limit(MAX_EVENTS)
        )
    )
    rows.sort(key=lambda r: (r.event_date, r.created_at, r.version, r.id))
    checks = [r for r in rows if r.kind == "checkin"]
    workouts = [r for r in rows if r.kind == "workout"]
    achievements = [r for r in rows if r.kind == "technical_achievement"]
    by_date = {r.event_date: r for r in checks}
    # Read only referenced plan components, at a bounded number of source versions.
    plan_ids = list(
        dict.fromkeys(
            r.payload.get("plan_id") for r in reversed(workouts) if r.payload.get("plan_id")
        )
    )[:64]
    plans = (
        {
            r.id: r.payload
            for r in db.scalars(
                select(Record).where(
                    Record.user_id == uid, Record.kind == "plan", Record.id.in_(plan_ids)
                )
            )
        }
        if plan_ids
        else {}
    )
    active = latest_record(db, uid, "plan")
    source = latest_record(db, uid, "profile")
    nutrition = latest_record(db, uid, "nutrition")
    nutrition_summary = None
    if nutrition and source:
        recent = list(
            db.scalars(
                select(Record)
                .where(
                    Record.user_id == uid,
                    Record.kind == "checkin",
                    Record.event_date >= (date.today() - timedelta(days=28)).isoformat(),
                )
                .order_by(Record.event_date.desc(), Record.version.desc())
                .limit(3)
            )
        )
        current = ni.visible(
            {
                "profile": source,
                "training": active,
                "nutrition": nutrition,
                "preferences": latest_record(db, uid, "nutrition_preferences"),
                "checks": recent,
            }
        )
        nutrition_summary = {
            "version": nutrition.version,
            "usable": current["available"],
            "as_of": date.today().isoformat(),
            "target_calories": current.get("target_calories"),
            "macro_targets": current.get("macro_targets"),
            "note": current.get(
                "reason",
                "Current approved estimate; not measured expenditure. Allergens, halal certification and clinical needs require appropriate review.",
            ),
        }
    reassessments = list(
        db.scalars(
            select(Record)
            .where(Record.user_id == uid, Record.kind == "reassessment")
            .order_by(Record.version.desc())
            .limit(3)
        )
    )
    series = {}
    invalid_entries = 0

    def add(
        label,
        unit,
        value,
        r,
        *,
        protocol="",
        evidence="self-reported",
        direction="higher",
        kind="observation",
        effort=None,
    ):
        if value is None:
            return
        raw = f"{label}|{unit}|{protocol}|{evidence}"
        key = hashlib.sha256(raw.encode()).hexdigest()[:20]
        item = series.setdefault(
            key,
            {
                "id": key,
                "label": label,
                "unit": unit,
                "protocol": protocol,
                "evidence": evidence,
                "kind": kind,
                "direction": direction,
                "points": [],
            },
        )
        item["points"].append(
            {"date": r.event_date, "value": round(value, 4), "record_id": r.id, "effort": effort}
        )

    for r in checks:
        p = r.payload
        for key, label, unit in [
            ("weight_kg", "Body weight", "kg"),
            ("sleep", "Sleep", "hours"),
            ("fatigue", "Fatigue", "1–10"),
            ("soreness", "Muscle soreness", "0–10"),
            ("readiness", "Recovery readiness", "1–5"),
            ("body_fat", "Body fat (reported)", "%"),
        ]:
            add(label, unit, p.get(key), r, direction="neutral")
        for b in p.get("benchmarks", []):
            try:
                value, unit = normalize(b.get("value"), b.get("unit"))
                if not b.get("name") or not b.get("reps"):
                    raise ValueError("Missing benchmark protocol")
            except ValueError:
                invalid_entries += 1
                continue
            protocol = f"{b['reps']} reps; effort {b.get('effort', 'unknown')}/10; check-in test"
            direction = "lower" if b["name"] in {"100m", "1km", "5km"} else "higher"
            add(
                b["name"],
                unit,
                value,
                r,
                protocol=protocol,
                evidence=b.get("provenance", "self-reported"),
                direction=direction,
                kind="estimate" if b.get("provenance") == "estimated" else "benchmark",
                effort=b.get("effort"),
            )
            if unit == "kg" and p.get("weight_kg"):
                add(
                    b["name"] + " relative load",
                    "× body mass",
                    value / p["weight_kg"],
                    r,
                    protocol=protocol,
                    evidence=b.get("provenance", "self-reported"),
                    kind="derived",
                )
    weeks = defaultdict(
        lambda: {
            "minutes": 0,
            "completed": 0,
            "failed": 0,
            "missed": 0,
            "load_au": 0,
            "missing_rpe": 0,
        }
    )
    practices = Counter()
    practice_records = 0
    seen = {}
    for r in workouts:
        p = r.payload
        plan = plans.get(p.get("plan_id"), {})
        identity = (plan.get("lineage_id", p.get("plan_id")), p.get("session_id"))
        seen[identity] = r
    for r in seen.values():
        p = r.payload
        when = date.fromisoformat(r.event_date)
        week = (when - timedelta(days=when.weekday())).isoformat()
        status = p.get("status", "completed")
        weeks[week][status] += 1
        if status == "missed":
            continue
        weeks[week]["minutes"] += p["minutes"]
        if p.get("effort") is None:
            weeks[week]["missing_rpe"] += 1
        else:
            weeks[week]["load_au"] += p["minutes"] * p["effort"]
        if p.get("practices"):
            practice_records += 1
        for practice in p.get("practices", []):
            practices[practice["discipline"]] += practice["minutes"]
        add("Session fatigue", "1–10", p.get("fatigue"), r, direction="neutral")
        if status != "completed":
            continue  # failed sets never become a completed personal record
        for performance in p.get("performances", []):
            name = performance["exercise_name"]
            for s in performance["sets"]:
                reps = s.get("reps")
                load = s.get("weight_kg")
                if load is not None and reps is not None:
                    protocol = f"{reps} reps; completed logged sets; conditions/RPE may differ"
                    add(
                        name,
                        "kg",
                        load,
                        r,
                        protocol=protocol,
                        kind="actual_set",
                        effort=s.get("rpe"),
                    )
                    weight = by_date.get(r.event_date)
                    if weight:
                        add(
                            name + " relative load",
                            "× body mass",
                            load / weight.payload["weight_kg"],
                            r,
                            protocol=protocol,
                            kind="derived",
                        )
                if reps is not None:
                    add(
                        name + " repetitions",
                        "reps",
                        reps,
                        r,
                        protocol=f"Load {load if load is not None else 'unknown'} kg; completed sets",
                        kind="actual_set",
                        effort=s.get("rpe"),
                    )
                if s.get("duration_seconds") is not None:
                    add(
                        name + " duration",
                        "seconds",
                        s["duration_seconds"],
                        r,
                        protocol=f"Distance {s.get('distance_m', 'unknown')} m; completed sets",
                        kind="actual_set",
                        direction="lower" if s.get("distance_m") else "higher",
                    )
                if s.get("distance_m") is not None:
                    add(
                        name + " distance",
                        "m",
                        s["distance_m"],
                        r,
                        protocol=f"Duration {s.get('duration_seconds', 'unknown')} seconds; completed sets",
                        kind="actual_set",
                    )
    items = []
    for s in series.values():
        # For multiple sets on one date use the supported daily best, not a fictitious mean test.
        daily = {}
        for point in s["points"]:
            old = daily.get(point["date"])
            if old is None or (
                point["value"] < old["value"]
                if s["direction"] == "lower"
                else point["value"] > old["value"]
            ):
                daily[point["date"]] = point
        points = [daily[k] for k in sorted(daily)]
        best = (min if s["direction"] == "lower" else max)(points, key=lambda p: p["value"])
        s.update(
            points=points[-120:],
            observations=len(points),
            chart_truncated=len(points) > 120,
            trend=trend(points, s["direction"]),
            best=best,
        )
        items.append(s)
    items.sort(
        key=lambda s: (
            0 if s["label"] in {"Body weight", "Sleep", "Fatigue"} else 1,
            s["label"],
            s["protocol"],
            s["evidence"],
        )
    )
    adherence = adherence_summary(
        db, uid, active, start, end, list(seen.values()), total > MAX_EVENTS
    )
    count = sum(r.payload.get("status", "completed") == "completed" for r in seen.values())
    observations = [
        f"{s['label']} ({s['protocol'] or s['unit']}): {s['trend']['status']}, change {s['trend'].get('delta')} {s['unit']} over {s['trend'].get('span_days', 0)} days. {s['trend']['note']}"
        for s in items
        if s["trend"]["status"] not in {"limited", "missing"}
    ][:12]
    complete = [
        (k, v)
        for k, v in sorted(weeks.items())
        if start <= date.fromisoformat(k) and date.fromisoformat(k) + timedelta(days=6) <= end
    ]
    if (
        len(complete) >= 2
        and (date.fromisoformat(complete[-1][0]) - date.fromisoformat(complete[-2][0])).days == 7
    ):
        a, b = complete[-2][1], complete[-1][1]
        observations.append(
            f"Logged volume changed from {a['minutes']} to {b['minutes']} minutes between two complete consecutive calendar weeks. This does not measure unlogged training or establish cause."
        )
    return {
        "period": {"start": start.isoformat(), "end": end.isoformat()},
        "coverage": {
            "total_events": total,
            "loaded_events": len(rows),
            "truncated": total > MAX_EVENTS,
            "event_limit": MAX_EVENTS,
            "series_total": len(items),
            "series_returned": min(60, len(items)),
            "chart_point_limit": 120,
            "source_plan_limit": 64,
            "source_plans_loaded": len(plans),
            "invalid_benchmark_entries": invalid_entries,
        },
        "observations": observations
        or [
            "Limited longitudinal evidence. Add repeated comparable measurements; no development trend is inferred from an empty or single-observation history."
        ],
        "series": items[:60],
        "weekly": [
            {
                "week": k,
                **v,
                "partial_week": date.fromisoformat(k) < start
                or date.fromisoformat(k) + timedelta(days=6) > end,
            }
            for k, v in sorted(weeks.items())
        ],
        "adherence": adherence,
        "martial_arts": {
            "minutes": [{"discipline": k, "minutes": v} for k, v in sorted(practices.items())],
            "workouts_with_practice": practice_records,
            "workouts_loaded": len(seen),
            "note": "Only explicitly logged discipline minutes; unrecorded participation and proficiency are unknown.",
        },
        "achievements": [
            {
                "id": r.id,
                **r.payload,
                "evidence": "self-reported technical achievement, not verified proficiency",
            }
            for r in achievements[-50:]
        ],
        "milestones": [
            f"{n} completed logged sessions within the loaded selected window"
            for n in (5, 10, 25, 50, 100)
            if count >= n
        ],
        "profile_summary": {
            k: source.payload.get(k)
            for k in ("goal", "age", "height_cm", "weight_kg", "experience")
        }
        if source
        else None,
        "nutrition_summary": nutrition_summary,
        "reassessments": [
            {
                "version": r.version,
                "checkpoint": r.payload.get("review_week"),
                "reason": r.payload.get("reason"),
                "benchmark_changes": r.payload.get("benchmark_changes", []),
                "historical": not active or r.payload.get("base_plan_id") != active.id,
            }
            for r in reassessments
        ],
        "limitations": LIMITATIONS,
        "priorities": [
            "Repeat comparable tests under consistent conditions; do not infer improvement from attendance alone.",
            "Review persistent fatigue or unchanged performance with qualified coaches. No approved plan was changed.",
            "Use weeks 4/8/12 reassessment and explicit proposal approval for programming changes.",
        ],
    }


def adherence_summary(db, uid, active, start, end, workouts, truncated):
    if not active:
        return {
            "planned": None,
            "completed": 0,
            "percent": None,
            "note": "No approved program; due-session attendance is unknown.",
        }
    lineage = active.payload.get("lineage_id", active.id)
    schedule = latest_record(db, uid, "analytics_schedule")
    sessions = [(w["week"], s) for w in active.payload.get("weeks", []) for s in w["sessions"]]
    if not schedule or schedule.payload.get("lineage_id") != lineage:
        return {
            "planned": None,
            "completed": None,
            "percent": None,
            "all_program_slots": len(sessions),
            "note": "No explicit cycle start date. Due-session adherence cannot be inferred from plan creation or future slots.",
        }
    anchor = date.fromisoformat(schedule.payload["start_date"])
    due = {
        s["id"]
        for w, s in sessions
        if start <= anchor + timedelta(days=7 * (w - 1) + DAYS.index(s["day"])) <= end
    }
    ids = set(
        db.scalars(
            select(Record.id).where(
                Record.user_id == uid, Record.kind == "plan", Record.parent_ref == lineage
            )
        )
    ) | {active.id}
    completed = {
        r.payload["session_id"]
        for r in workouts
        if r.parent_ref in ids
        and r.payload.get("status", "completed") == "completed"
        and r.payload["session_id"] in due
    }
    return {
        "planned": len(due),
        "completed": len(completed),
        "percent": round(100 * len(completed) / len(due), 1) if due and not truncated else None,
        "start_date": anchor.isoformat(),
        "all_program_slots": len(sessions),
        "note": "Explicit analytics calendar reference; numerator requires a completed logged session in this interval and a due slot. Early/late logs outside the interval are excluded. Missing logs do not prove nonattendance. Truncated coverage withholds percentages.",
    }


def csv_rows(db, uid, start, end):
    """Keyset pages avoid all-history materialization; no identity/notes columns."""
    fields = ["date", "kind", "record_id", "version", "metric", "value", "unit", "evidence"]

    def emit(values):
        stream = io.StringIO()
        csv.writer(stream).writerow(values)
        return stream.getvalue()

    def safe(v):
        text = str(v) if v is not None else ""
        return "'" + text if text.startswith(("=", "+", "-", "@", "\t", "\r")) else text

    yield emit(fields)
    cursor = 0
    # Versions are unique per account/kind, so page by kind/version rather than offsets.
    for kind in KINDS:
        cursor = 0
        while True:
            rows = list(
                db.scalars(
                    history_query(uid, kind, start, end)
                    .where(Record.version > cursor)
                    .order_by(Record.version)
                    .limit(100)
                )
            )
            if not rows:
                break
            for r in rows:
                p = r.payload
                if kind == "checkin":
                    for metric, unit in (
                        ("weight_kg", "kg"),
                        ("body_fat", "%"),
                        ("mobility", "self-reported category"),
                        ("sleep", "hours"),
                        ("fatigue", "1–10"),
                        ("soreness", "0–10"),
                        ("readiness", "1–5"),
                    ):
                        if p.get(metric) is not None:
                            yield emit(
                                [
                                    r.event_date,
                                    kind,
                                    r.id,
                                    r.version,
                                    metric,
                                    p[metric],
                                    unit,
                                    "self-reported",
                                ]
                            )
                    for b in p.get("benchmarks", []):
                        yield emit(
                            [
                                r.event_date,
                                kind,
                                r.id,
                                r.version,
                                safe(f"{b['name']} / {b['reps']} reps / effort {b.get('effort')}"),
                                b["value"],
                                b["unit"],
                                b.get("provenance", "self-reported"),
                            ]
                        )
                elif kind == "workout":
                    yield emit(
                        [
                            r.event_date,
                            kind,
                            r.id,
                            r.version,
                            "training_minutes",
                            p["minutes"],
                            "minutes",
                            p.get("status", "completed"),
                        ]
                    )
                    for ex in p.get("performances", []):
                        for s in ex["sets"]:
                            for metric, unit in (
                                ("weight_kg", "kg"),
                                ("reps", "reps"),
                                ("duration_seconds", "seconds"),
                                ("distance_m", "m"),
                                ("rpe", "1–10"),
                            ):
                                if s.get(metric) is not None:
                                    yield emit(
                                        [
                                            r.event_date,
                                            kind,
                                            r.id,
                                            r.version,
                                            safe(ex["exercise_name"] + " / " + metric),
                                            s[metric],
                                            unit,
                                            "self-reported set; " + p.get("status", "completed"),
                                        ]
                                    )
                    for practice in p.get("practices", []):
                        yield emit(
                            [
                                r.event_date,
                                kind,
                                r.id,
                                r.version,
                                safe(practice["discipline"]),
                                practice["minutes"],
                                "minutes",
                                "self-reported practice",
                            ]
                        )
                else:
                    yield emit(
                        [
                            r.event_date,
                            kind,
                            r.id,
                            r.version,
                            safe(p["discipline"] + " / " + p["title"]),
                            "",
                            "",
                            "self-reported technical achievement",
                        ]
                    )
            cursor = rows[-1].version
