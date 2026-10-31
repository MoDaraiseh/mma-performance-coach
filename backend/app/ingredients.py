"""USDA values and editorial safety metadata; independent of any LLM."""

import json
import math
from pathlib import Path

CATALOG = {
    r["id"]: r
    for r in json.loads(
        (Path(__file__).parent / "data/ingredients.json").read_text(encoding="utf-8")
    )
}
VERSION = "usda-sr-curated-v2"
MACROS = ("protein", "carbs", "fat")


def serving_grams(quantity, unit):
    """Mass-only conversions: household volume needs food-specific density."""
    factors = {"g": 1, "kg": 1000, "oz": 28.349523125}
    if unit not in factors or not math.isfinite(quantity) or quantity <= 0:
        raise ValueError("Use a positive mass in g, kg or oz; volume conversions are unsupported")
    return quantity * factors[unit]


def validate_catalog(records):
    ids, sources = set(), set()
    for r in records:
        if r["id"] in ids or r["source"]["fdc_id"] in sources:
            raise ValueError("Duplicate food identifier or USDA record")
        ids.add(r["id"])
        sources.add(r["source"]["fdc_id"])
        for k in (*MACROS, "source_calories"):
            v = r["per_100g"].get(k)
            if v is None or not math.isfinite(v) or v < 0:
                raise ValueError("Missing or invalid required composition")
        if sum(r["per_100g"][k] for k in MACROS) > 100.1:
            raise ValueError("Macronutrients exceed edible mass")
        for v in r["per_100g"].values():
            if v is not None and (not math.isfinite(v) or v < 0):
                raise ValueError("Invalid optional nutrient; use null for missing")


validate_catalog(list(CATALOG.values()))


def portion(key, grams):
    if key not in CATALOG or not 0 < grams <= 1000:
        raise ValueError("Unsupported ingredient or portion")
    food = CATALOG[key]
    result = {k: food["per_100g"][k] * grams / 100 for k in MACROS}
    result["calories"] = 4 * result["protein"] + 4 * result["carbs"] + 9 * result["fat"]
    result["source_calories"] = food["per_100g"]["source_calories"] * grams / 100
    return result


def catalog_payload():
    return {
        "version": VERSION,
        "items": list(CATALOG.values()),
        "coverage": {
            "foods": len(CATALOG),
            "nutrients": {
                k: sum(r["per_100g"].get(k) is not None for r in CATALOG.values())
                for k in (
                    "protein",
                    "carbs",
                    "fat",
                    "source_calories",
                    "fiber",
                    "sodium_mg",
                    "calcium_mg",
                    "iron_mg",
                    "potassium_mg",
                )
            },
        },
        "method": "USDA SR Legacy April 2018 factual subset, CC0. Source kcal and 4P+4C+9F macro-derived energy are distinct; fiber and food-specific factors can explain differences. Allergen, cost-tier and dietary metadata are conservative editorial screening, not certification or cross-contact guarantees.",
    }
