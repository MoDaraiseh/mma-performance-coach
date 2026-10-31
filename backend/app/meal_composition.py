import math
from collections import Counter
from copy import deepcopy

from .ingredients import CATALOG, MACROS, VERSION, portion

MEALS = ["Breakfast", "Lunch", "Dinner", "Recovery snack"]


def measure(meal):
    values = {k: 0.0 for k in (*MACROS, "source_calories")}
    for ingredient in meal["ingredients"]:
        amounts = portion(ingredient["id"], ingredient["grams"])
        for k in values:
            values[k] += amounts[k]
    result = {k: round(v, 1) for k, v in values.items()}
    result["calories"] = round(4 * result["protein"] + 4 * result["carbs"] + 9 * result["fat"], 1)
    return result


def compose(name, targets, allowed, prefs, rotation=0, protein_id=None, food_id=None):
    proteins = [k for k in allowed if CATALOG[k]["role"] == "protein"]
    carbs = [k for k in allowed if CATALOG[k]["role"] == "carb"]
    vegetables = [k for k in allowed if CATALOG[k]["role"] == "vegetable"]
    fruits = [k for k in allowed if CATALOG[k]["role"] == "fruit"]
    if not proteins or not carbs or not vegetables or not fruits or "olive-oil" not in allowed:
        raise ValueError("Safe meal coverage unavailable; review exclusions with a dietitian")
    if protein_id:
        if protein_id not in proteins:
            raise ValueError("Requested protein is excluded or unavailable")
        proteins = [protein_id]
    else:
        proteins = proteins[rotation % len(proteins) :] + proteins[: rotation % len(proteins)]
        if name in ("Breakfast", "Recovery snack") and "yogurt" in proteins and rotation % 3 == 0:
            proteins = ["yogurt", *[k for k in proteins if k != "yogurt"]]
    preferred = {
        "Middle Eastern inspired": ["rice", "bulgur", "couscous"],
        "South Asian inspired": ["rice", "potato"],
        "Mediterranean inspired": ["bulgur", "potato", "couscous"],
    }.get(prefs.culture, [])
    carbs = sorted(
        carbs,
        key=lambda k: (
            0
            if name in ("Breakfast", "Recovery snack") and k == "oats" and rotation % 3 == 0
            else 1
            if k in preferred
            else 2,
            (carbs.index(k) - rotation) % len(carbs),
        ),
    )
    veg, fruit = vegetables[rotation % len(vegetables)], fruits[rotation % len(fruits)]
    fixed = (
        [(fruit, 50 if name == "Breakfast" else 25)]
        if name in ("Breakfast", "Recovery snack")
        else [(veg, 100)]
    )
    if food_id:
        if food_id not in allowed:
            raise ValueError("Requested food is excluded or unavailable")
        role = CATALOG[food_id]["role"]
        if role == "protein":
            proteins = [food_id]
        elif role == "carb":
            carbs = [food_id]
        elif role in ("fruit", "vegetable"):
            if CATALOG[fixed[0][0]]["role"] != role:
                raise ValueError("Choose fruit for breakfast/snack or vegetables for lunch/dinner")
            fixed = [(food_id, fixed[0][1])]
        else:
            raise ValueError("Fat-only substitutions are outside current recipe coverage")
    fixed_values = {k: sum(portion(f, grams)[k] for f, grams in fixed) for k in MACROS}
    for pro in proteins:
        for carb in carbs:
            a, b = CATALOG[pro]["per_100g"], CATALOG[carb]["per_100g"]
            determinant = a["protein"] * b["carbs"] - b["protein"] * a["carbs"]
            if abs(determinant) < 0.001:
                continue
            p, c = (
                targets["protein"] - fixed_values["protein"],
                targets["carbs"] - fixed_values["carbs"],
            )
            pro_g = 100 * (p * b["carbs"] - c * b["protein"]) / determinant
            carb_g = 100 * (a["protein"] * c - a["carbs"] * p) / determinant
            fat_g = (
                targets["fat"]
                - fixed_values["fat"]
                - a["fat"] * pro_g / 100
                - b["fat"] * carb_g / 100
            ) / (CATALOG["olive-oil"]["per_100g"]["fat"] / 100)
            carb_cap = 140 if carb == "oats" else 500
            if not (20 <= pro_g <= 500 and 15 <= carb_g <= carb_cap and 0 <= fat_g <= 40):
                continue
            parts = [(pro, pro_g), (carb, carb_g), *fixed]
            if fat_g >= 0.1:
                parts.append(("olive-oil", fat_g))
            ingredients = [
                {
                    "id": k,
                    "food": CATALOG[k]["name"],
                    "grams": round(g, 1),
                    "source": CATALOG[k]["source"],
                }
                for k, g in parts
            ]
            meal = {
                "name": name,
                "title": f"{CATALOG[pro]['name']} & {CATALOG[carb]['name']}",
                "ingredients": ingredients,
                "recipe_id": f"{pro}-{carb}-{fixed[0][0]}",
                "preparation": "Use the specified raw/dry/cooked edible weights. Prepare separately as appropriate; combine as a bowl, with fruit on the side. Oil is a measured ingredient, not an additional uncounted dressing.",
                "culture_note": prefs.culture
                + ": ingredient preference only, not an authentic regional recipe.",
                "preparation_minutes": 10,
                "preparation_steps": [
                    "Use batch-cooked grains, legumes and meat, or ready-cooked equivalents matching the named preparation state. Batch cooking time is additional.",
                    "Weigh the listed edible portions. Wash raw produce; keep raw and cooked foods separate.",
                    "Reheat cooked components safely according to local food-safety guidance. Serve with the listed produce and measured oil.",
                ],
                "cooking_note": f"{prefs.cooking_skill}: assembly estimate 10 minutes, within your {prefs.cooking_minutes}-minute limit; batch preparation and shopping are excluded.",
            }
            return {**meal, **measure(meal)}
    raise ValueError(
        "No feasible portions within template limits for these ingredients and targets"
    )


def recompute(plan):
    plan = deepcopy(plan)
    grocery = Counter()
    for day in plan["days"]:
        for meal in day["meals"]:
            meal.update(measure(meal))
            for i in meal["ingredients"]:
                grocery[i["id"]] += i["grams"]
        day["totals"] = {
            k: round(sum(m[k] for m in day["meals"]), 1)
            for k in (*MACROS, "calories", "source_calories")
        }
        parts = [i for meal in day["meals"] for i in meal["ingredients"]]
        day["nutrients"] = {}
        for nutrient in ("fiber", "sodium_mg", "calcium_mg", "iron_mg", "potassium_mg"):
            values = [CATALOG[i["id"]]["per_100g"].get(nutrient) for i in parts]
            day["nutrients"][nutrient] = (
                None
                if any(v is None for v in values)
                else round(sum(v * i["grams"] / 100 for v, i in zip(values, parts)), 1)
            )
    plan["grocery"] = [
        {
            "id": k,
            "food": CATALOG[k]["name"],
            "grams": round(g, 1),
            "preparation_state": CATALOG[k]["source"]["description"],
        }
        for k, g in sorted(grocery.items())
    ]
    return plan


def validate_plan(plan, allowed):
    if not plan.get("available"):
        if plan.get("days") or plan.get("grocery"):
            raise ValueError("Unavailable plan must not expose meals")
        return
    if plan.get("catalog_version") != VERSION or len(plan["days"]) != 7:
        raise ValueError("Invalid catalog version or seven-day structure")
    if not math.isfinite(plan["target_calories"]) or not 1500 <= plan["target_calories"] <= 4650:
        raise ValueError("Invalid energy target")
    if any(not math.isfinite(v) or v <= 0 for v in plan["macro_targets"].values()):
        raise ValueError("Invalid macro target")
    if [d["day"] for d in plan["days"]] != list(range(1, 8)):
        raise ValueError("Invalid meal days")
    for day in plan["days"]:
        if [m["name"] for m in day["meals"]] not in (MEALS, MEALS[:3]):
            raise ValueError("Missing or duplicated meals")
        for meal in day["meals"]:
            if any(
                not math.isfinite(meal[k]) or meal[k] < 0
                for k in (*MACROS, "calories", "source_calories")
            ):
                raise ValueError("Invalid meal total")
            if any(i["id"] not in allowed for i in meal["ingredients"]):
                raise ValueError("Excluded ingredient in plan")
            if len({i["id"] for i in meal["ingredients"]}) != len(meal["ingredients"]):
                raise ValueError("Duplicate ingredient")
            measured = measure(meal)
            if any(
                abs(measured[k] - meal[k]) > 0.11 for k in (*MACROS, "calories", "source_calories")
            ):
                raise ValueError("Meal totals do not match catalog portions")
        if abs(day["totals"]["calories"] - plan["target_calories"]) > 10:
            raise ValueError("Day outside energy tolerance")
        for k in MACROS:
            if abs(day["totals"][k] - plan["macro_targets"][k]) > 1:
                raise ValueError("Day outside macro tolerance")
    recalculated = recompute(plan)
    if recalculated["grocery"] != plan["grocery"] or any(
        a["totals"] != b["totals"] or a.get("nutrients") != b.get("nutrients")
        for a, b in zip(plan["days"], recalculated["days"])
    ):
        raise ValueError("Day or grocery totals invalid")
