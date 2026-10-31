"""Educational estimates, not measured expenditure or competition nutrition."""

from .safety import unsafe_weight_goal


def calculate(p, prefs):
    if unsafe_weight_goal(" ".join([p.goal, *p.objectives, p.food_preferences])):
        raise ValueError(
            "Automated numerical nutrition withheld for a rapid-cutting or extreme-restriction request. No dehydration or rapid weight-loss plan is provided; consult a qualified sports dietitian and medical team."
        )
    competition = p.competitive or "competit" in " ".join([p.goal, *p.objectives]).lower()
    if p.age < 18 or p.clinical_nutrition or p.metabolic_sex == "unspecified":
        raise ValueError(
            "No numerical targets for minors, clinical needs, pregnancy/breastfeeding, eating-disorder concerns or unspecified metabolic equation input."
        )
    rmr = (
        10 * p.weight_kg
        + 6.25 * p.height_cm
        - 5 * p.age
        + (5 if p.metabolic_sex == "male" else -161)
    )
    factor = {"low": 1.4, "moderate": 1.6, "high": 1.8}[p.activity]
    maintenance = round(rmr * factor)
    bmi = p.weight_kg / (p.height_cm / 100) ** 2
    if not 1500 <= maintenance <= 4500 or p.body_fat is not None and p.body_fat < 10 or bmi < 18.5:
        raise ValueError(
            "Profile outside conservative template coverage; consult a qualified dietitian"
        )
    adjustment, note = 0, "Maintenance estimate; no automatic weight-loss recommendation."
    if prefs.objective == "Build gradually" and not competition:
        adjustment = min(150, round(maintenance * 0.05))
        note = "Optional modest surplus: smaller of 5% or 150 kcal. A product heuristic, not a predicted gain rate."
    elif prefs.objective == "Sustainable reduction":
        if (
            competition
            or bmi < 25
            or p.sleep < 6
            or p.recovery
            or prefs.hunger
            and prefs.hunger >= 4
        ):
            note = "Requested reduction withheld; maintenance shown. Competition, lower BMI, recovery concerns or high hunger need individualized professional review."
        else:
            adjustment = -min(150, round(maintenance * 0.05))
            note = "Explicit optional modest reduction: smaller of 5% or 150 kcal. No rapid weight-loss rate or target division is prescribed."
    if competition and prefs.objective != "Maintain":
        note = "Competition-specific energy changes require a qualified sports dietitian; maintenance shown."
    target = max(1500, maintenance + adjustment)
    protein, fat = 1.6 * p.weight_kg, 0.27 * target / 9
    carbs = (target - 4 * protein - 9 * fat) / 4
    if carbs <= 0:
        raise ValueError("Unsupported macro balance; individualized assessment needed")
    return {
        "rmr": round(rmr),
        "bmr_estimate": round(rmr),
        "activity_factor": factor,
        "estimated_maintenance": maintenance,
        "range": [round(maintenance * 0.85), round(maintenance * 1.15)],
        "target_calories": target,
        "adjustment": target - maintenance,
        "goal_note": note,
        "macro_targets": {
            "protein": round(protein, 1),
            "carbs": round(carbs, 1),
            "fat": round(fat, 1),
        },
        "macro_guidance": {
            "protein_g": [round(1.4 * p.weight_kg), round(2 * p.weight_kg)],
            "carbs_g": [round(3 * p.weight_kg), round(5 * p.weight_kg)],
            "fat_g": [round(0.25 * target / 9), round(0.35 * target / 9)],
            "note": "Protein 1.4–2.0 g/kg/day (ISSN); carbohydrate 3–5 g/kg/day is general lower-volume exercise context, not a ceiling for MMA camps. Fat 25–35% energy. Composition targets use protein 1.6 g/kg, fat 27%, carbohydrate as remainder; flag deviations rather than hiding them. Activity multipliers and ±15% maintenance band are heuristics, not measured expenditure or validated confidence intervals.",
        },
        "equation_source": "https://pubmed.ncbi.nlm.nih.gov/2305711/",
        "guidance_sources": [
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC5477153/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC6090881/",
        ],
    }
