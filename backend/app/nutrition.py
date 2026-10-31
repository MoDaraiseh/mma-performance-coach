from copy import deepcopy

from .dietary import eligible
from .ingredients import CATALOG, VERSION
from .meal_composition import MEALS, compose, recompute, validate_plan
from .nutrition_calculations import calculate
from .nutrition_models import NutritionPreferences

GENERAL = "Educational estimates, not measured energy expenditure or medical nutrition therapy. Independent sports-dietitian review is pending. A calorie floor and matching macros do not establish adequate energy availability or a nutritionally complete diet; this app cannot diagnose REDs. Review clinical needs and competition-specific fueling with a qualified sports dietitian. No dehydration, rapid weight cuts or extreme diets. Check labels, halal certification and cross-contact; ingredient screening is not an allergy safety guarantee."


class NutritionPlanService:
    @staticmethod
    def generate(p, preferences=None, training=None):
        prefs = preferences or NutritionPreferences()
        try:
            numbers = calculate(p, prefs)
            allowed = eligible(p, prefs)
            days = []
            snacks = prefs.meals_per_day == 4 if prefs.meals_per_day else prefs.snacks
            slots = MEALS if snacks else MEALS[:3]
            fractions = [0.25, 0.3, 0.3, 0.15] if snacks else [0.3, 0.35, 0.35]
            for day in range(7):
                meals = [
                    compose(
                        name,
                        {k: v * fraction for k, v in numbers["macro_targets"].items()},
                        allowed,
                        prefs,
                        day + i,
                    )
                    for i, (name, fraction) in enumerate(zip(slots, fractions))
                ]
                days.append({"day": day + 1, "meals": meals})
            weeks = (training or {}).get("weeks") or [{}]
            sessions = weeks[0].get("sessions", [])
            weekdays = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            for day, weekday in zip(days, weekdays):
                minutes = sum(s.get("minutes", 0) for s in sessions if s.get("day") == weekday)
                selected = (
                    weekday in prefs.training_days
                    if prefs.training_days is not None
                    else minutes > 0
                )
                day["training_context"] = {
                    "weekday": weekday,
                    "approved_minutes": minutes,
                    "note": "Higher-volume day: prioritize carbohydrate-containing meals around practice; this template may underfuel prolonged training. Seek individualized sports-dietitian review."
                    if minutes > 90
                    else "Training day: distribute carbohydrate around practice and protein across meals; adjust timing to gastrointestinal comfort."
                    if selected
                    else "Recovery day: retain regular meals and protein. Recovery still requires energy; no automatic calorie reduction.",
                }
                if not sessions and prefs.training_days is None:
                    day["training_context"]["note"] = (
                        "No approved training schedule is available. Meal targets use reported activity only; set timing preferences or save a training plan for day-specific guidance."
                    )
                types = {s.get("type") for s in sessions if s.get("day") == weekday}
                if "Strength" in types:
                    day["training_context"]["note"] += (
                        " Strength practice: retain regular protein-containing meals and adequate carbohydrate; a lifting session does not establish a need for a calorie surplus."
                    )
                if "Conditioning" in types:
                    day["training_context"]["note"] += (
                        " Conditioning practice: carbohydrate availability matters for sustained work. Duration alone cannot establish intensity, sweat losses or precise fueling needs."
                    )
            plan = recompute(
                {
                    "available": True,
                    **numbers,
                    "days": days,
                    "catalog_version": VERSION,
                    "preferences": prefs.model_dump(),
                    "inputs": p.model_dump(),
                    "guidance": GENERAL,
                    "method": "Mifflin–St Jeor estimated resting expenditure (not measured BMR) × self-reported activity factor. Macro targets and bounded ingredient portions are deterministic. Meal calories use 4P+4C+9F from rounded macros, distinct from USDA source kcal (fiber and food-specific factors differ). No LLM generates nutrient values. Maintenance uncertainty band and optional 5%/150-kcal adjustments are product heuristics, not weight-change predictions.",
                    "substitutions": "Preview a catalog-backed alternative, compare portions and totals, then approve a new version. Dietary additions take effect before suggestions. Remove profile restrictions only through profile editing. Choose certified halal poultry; no record certifies a product.",
                    "training_days": prefs.training_days
                    if prefs.training_days is not None
                    else [s["day"] for s in sessions],
                    "training_note": "Distribute carbohydrate-containing meals around training according to comfort; keep regular protein across the day. Recovery days still need fuel. No automatic extra calories are added for a session. Reported timing preferences do not edit the approved training calendar.",
                    "budget_note": "Editorial cost tiers guide ingredient choices; no live local prices or monetary budget guarantee.",
                    "changes": [],
                }
            )
            warnings = [
                "This macronutrient template is not validated as nutritionally complete. Micronutrient adequacy and gastrointestinal tolerance, including larger legume portions, require dietary review."
            ]
            carbs_per_kg = plan["macro_targets"]["carbs"] / p.weight_kg
            if not 3 <= carbs_per_kg <= 5:
                warnings.append(
                    "Carbohydrate remainder falls outside the general 3–5 g/kg reference. This is not a performance prescription; review workload and fueling with a sports dietitian."
                )
            if p.activity == "high" or p.minutes > 90:
                warnings.append(
                    "High training volume may exceed this general template; individualized carbohydrate and energy planning is recommended."
                )
            if p.food_preferences:
                warnings.append(
                    "Legacy free-text food preferences are retained for discussion. Use explicit cuisine/exclusion controls for reliable filtering; prose is not silently interpreted as an allergy rule."
                )
            plan["warnings"] = warnings
            validate_plan(plan, allowed)
            return plan
        except ValueError as exc:
            return {
                "available": False,
                "reason": str(exc),
                "guidance": GENERAL,
                "days": [],
                "grocery": [],
                "catalog_version": VERSION,
                "preferences": prefs.model_dump(),
                "inputs": p.model_dump(),
            }


def substitute(plan, p, prefs, day, meal_name, protein_id=None, food_id=None):
    if not plan.get("available") or plan.get("catalog_version") != VERSION:
        raise ValueError("Use a current validated meal plan before substitution")
    result = deepcopy(plan)
    meal = next((m for m in result["days"][day - 1]["meals"] if m["name"] == meal_name), None)
    if not meal:
        raise ValueError("Meal not present in this plan")
    allowed = eligible(p, prefs)
    old_ids = {i["id"] for i in meal["ingredients"]}
    proteins = (
        [None]
        if food_id
        else (
            [protein_id]
            if protein_id
            else [k for k in allowed if CATALOG[k]["role"] == "protein" and k not in old_ids]
        )
    )
    for key in proteins:
        try:
            candidate = compose(
                meal_name,
                {k: meal[k] for k in ("protein", "carbs", "fat")},
                allowed,
                prefs,
                day,
                key,
                food_id,
            )
            if candidate["recipe_id"] == meal["recipe_id"]:
                continue
            result["days"][day - 1]["meals"][result["days"][day - 1]["meals"].index(meal)] = (
                candidate
            )
            result = recompute(result)
            result["changes"] = [
                f"Day {day} {meal_name}: {meal['title']} → {candidate['title']}; portions, macros and grocery list revalidated."
            ]
            result["substitution_comparison"] = {
                "before": {
                    k: meal[k] for k in ("calories", "protein", "carbs", "fat", "ingredients")
                },
                "after": {
                    k: candidate[k] for k in ("calories", "protein", "carbs", "fat", "ingredients")
                },
                "delta": {
                    k: round(candidate[k] - meal[k], 1)
                    for k in ("calories", "protein", "carbs", "fat")
                },
            }
            validate_plan(result, allowed)
            return result
        except ValueError:
            if protein_id or food_id:
                raise
    raise ValueError(
        "No suitable distinct substitution within current restrictions and portion limits"
    )
