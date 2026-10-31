"""Personalized offline explanations render validated analytics, not invented facts."""


def explain(message, context):
    q = message.lower()
    if any(
        t in q for t in ("discipline", "skill gap", "technical", "training balance", "martial arts")
    ):
        rows = context.get("discipline_priorities", [])
        return (
            "Development priorities from your reported experience, preferences and coaching access: "
            + " ".join(
                f"{r['discipline']}: priority {r['priority']}. {r['evidence']}" for r in rows
            )
            + " Priorities allocate study time; they are not proficiency ratings. Discuss technical gaps and coached practice schedules with your instructor. Anthropometry does not determine your optimal style or fighting ability."
        )
    if any(t in q for t in ("fighter", "match", "similar")):
        matches = context.get("fighter_matches", [])
        if not matches:
            return "No supported fighter comparison is available in this context. Missing fighter attributes and professional records are unknown; use the Comparison Lab sources before drawing conclusions."
        return (
            "Current default-weight heuristic comparisons: "
            + " ".join(
                f"{m['name']}: {m['score']} points, {m['coverage']}% evidence coverage; {m['basis']}. Differences: {' '.join(m['differences'][:2])} Missing dimensions: {', '.join(m['missing']) or 'none among requested dimensions'}. {'Source observation is stale.' if m['stale'] else ''}"
                for m in matches
            )
            + " Study distance, movement and technical transitions with a qualified coach. These source snapshots do not establish current professional statistics, comparable proficiency or fighting potential. Custom lab weights may rank differently."
        )
    if any(
        t in q
        for t in (
            "progress",
            "plateau",
            "consisten",
            "endurance",
            "strength",
            "fatigue",
            "recover",
            "conditioning",
            "reassess",
        )
    ):
        workload = context.get("workload", {})
        recovery = context.get("recovery", {})
        text = f"Logged training: {workload.get('completed', 0)} completed, {workload.get('missed', 0)} missed and {workload.get('failed', 0)} failed sessions; {workload.get('last_7_days_minutes', 0)} minutes in the last seven days. This measures logged activity, not attendance or unlogged practice. Recovery status: {recovery.get('status', 'unknown')}; subjective reports are not a diagnosis. "
        changes = context.get("progress_changes", [])
        text += " ".join(
            f"Comparable {c['name']}: {c['before']} to {c['after']} {c['unit']} (change {c['delta']})."
            for c in changes[:3]
        )
        if not changes:
            text += "No comparable benchmark change is established; strength or endurance improvement cannot be inferred from attendance. "
        decisions = context.get("progression", {}).get("decisions", [])
        text += " ".join(f"{d['exercise']}: {d['action']}; {d['reason']}" for d in decisions[:3])
        if "reassess" in q:
            reports = context.get("reassessments", [])
            text += f" {len(reports)} recent checkpoint reports are available; historical reports do not authorize changes to the current plan. Request an updated assessment to review current observations and missing domains."
        return text
    if any(
        t in q
        for t in (
            "nutrition",
            "food",
            "meal",
            "protein",
            "macro",
            "calori",
            "lunch",
            "dinner",
            "breakfast",
            "snack",
        )
    ):
        n = context.get("nutrition")
        if not n or not n.get("usable"):
            return "No current usable nutrition plan is available. Missing food composition is unknown. Review changed inputs, dietary restrictions and Nutrition before requesting a substitution."
        return f"Your current approved nutrition plan uses an estimated {n['target_calories']} kcal, not measured expenditure. Macro targets: {n['targets']}. Source-backed portions are recalculated by deterministic services; USDA source energy and 4P+4C+9F energy remain separate. Changes require a validated preview and approval. Verify actual product allergens and halal certification. Training/recovery explanations are in Nutrition; high-volume and medical needs require a qualified sports dietitian."
    return None
