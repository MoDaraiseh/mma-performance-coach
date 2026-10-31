from .ingredients import CATALOG

ALIASES = {
    "dairy": "milk",
    "eggs": "egg",
    "soya": "soy",
    "tofu": "soy",
    "chicken": "poultry",
    "peanuts": "peanut",
    "nuts": "tree nuts",
    "lentil": "lentils",
    "chickpea": "chickpeas",
    "legume": "legumes",
    "oat": "oats",
}
COMMON = {
    "milk",
    "egg",
    "soy",
    "fish",
    "shellfish",
    "peanut",
    "tree nuts",
    "sesame",
    "wheat",
    "gluten",
    "legumes",
    "beans",
    "lentils",
    "chickpeas",
    "poultry",
    "oats",
    "rice",
    "potato",
    "broccoli",
    "banana",
    "olive",
    "olive oil",
    "carrot",
    "tomato",
    "apple",
    "orange",
    "spinach",
    "quinoa",
    "couscous",
    "bulgur",
    "salmon",
}


def eligible(p, prefs):
    unknown_ids = set(prefs.dislikes + prefs.unavailable) - CATALOG.keys()
    if unknown_ids:
        raise ValueError("Choose dislikes and unavailable ingredients from the catalog")
    allergies = {
        ALIASES.get(a.strip().lower(), a.strip().lower())
        for a in [*p.allergies, *prefs.add_allergies]
        if a.strip()
    }
    known = COMMON | set(CATALOG) | {i["name"].split(" (")[0] for i in CATALOG.values()}
    if allergies - known:
        raise ValueError("Unrecognized allergy; automated meals withheld")
    diet = set(p.diet) | set(prefs.add_diet)
    result = []
    for key, item in CATALOG.items():
        if (allergies or diet & {"Dairy-free", "Gluten-free"}) and not item.get("allergen_review"):
            continue
        tags = set(item["allergens"]) | {key, item["name"].split(" (")[0]}
        if key == "tofu":
            tags.add("legumes")
        if key == "olive-oil":
            tags |= {"olive", "olive oil"}
        if set(prefs.dislikes + prefs.unavailable) & {key} or allergies & tags:
            continue
        if "Vegan" in diet and not item["vegan"]:
            continue
        if "Vegetarian" in diet and not item["vegetarian"]:
            continue
        if "Dairy-free" in diet and "milk" in tags:
            continue
        if "Gluten-free" in diet and tags & {"wheat", "gluten", "oats"}:
            continue
        if (prefs.budget or p.budget) == "Low" and item["cost_tier"] > 2:
            continue
        result.append(key)
    return result
