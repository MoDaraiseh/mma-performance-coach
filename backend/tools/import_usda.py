"""Extract a curated factual subset from the official USDA SR Legacy CSV ZIP.

Usage: python tools/import_usda.py path/to/official.zip
No network access. Food names, restrictions, roles and cost tiers are app editorial
metadata, not USDA allergy certifications, current prices or cultural claims.
"""

import csv
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

SELECTION = [
    (168878, "rice", "rice (cooked)", "carb", ["rice"], 1),
    (172421, "lentils", "lentils (cooked)", "protein", ["legumes", "lentils"], 1),
    (173757, "chickpeas", "chickpeas (cooked)", "protein", ["legumes", "chickpeas"], 1),
    (170440, "potato", "potato (cooked)", "carb", [], 1),
    (170379, "broccoli", "broccoli (raw)", "vegetable", [], 1),
    (173944, "banana", "banana (raw)", "fruit", [], 1),
    (171413, "olive-oil", "olive oil", "fat", [], 2),
    (171477, "chicken", "chicken breast (cooked)", "protein", ["poultry"], 2),
    (172475, "tofu", "tofu (firm, raw)", "protein", ["soy"], 2),
    (173904, "oats", "oats (dry)", "carb", ["oats", "gluten", "wheat"], 1),
    (168917, "quinoa", "quinoa (cooked)", "carb", [], 3),
    (173735, "black-beans", "black beans (cooked)", "protein", ["legumes", "beans"], 1),
    (170894, "yogurt", "Greek yogurt (plain, nonfat)", "protein", ["milk"], 2),
    (173424, "egg", "egg (hard-boiled)", "protein", ["egg"], 1),
    (170393, "carrot", "carrot (raw)", "vegetable", [], 1),
    (170457, "tomato", "tomato (raw)", "vegetable", [], 1),
    (171688, "apple", "apple (raw, with skin)", "fruit", [], 1),
    (169097, "orange", "orange (raw)", "fruit", [], 1),
    (170287, "bulgur", "bulgur (cooked)", "carb", ["wheat", "gluten"], 1),
    (169700, "couscous", "couscous (cooked)", "carb", ["wheat", "gluten"], 1),
    (168462, "spinach", "spinach (raw)", "vegetable", [], 1),
    (175168, "salmon", "salmon (cooked)", "protein", ["fish"], 3),
    (167762, "strawberry", "strawberries (raw)", "fruit", [], 2),
    (171711, "blueberry", "blueberries (raw)", "fruit", [], 3),
    (169118, "pear", "pear (raw)", "fruit", [], 1),
    (169928, "peach", "peach (raw)", "fruit", [], 2),
    (169124, "pineapple", "pineapple (raw)", "fruit", [], 2),
    (174683, "grape", "grapes (raw)", "fruit", [], 2),
    (168409, "cucumber", "cucumber (raw, with peel)", "vegetable", [], 1),
    (170108, "red-pepper", "red pepper (raw)", "vegetable", [], 2),
    (169975, "cabbage", "cabbage (raw)", "vegetable", [], 1),
    (169986, "cauliflower", "cauliflower (raw)", "vegetable", [], 2),
    (169247, "romaine", "romaine lettuce (raw)", "vegetable", [], 1),
    (168484, "sweet-potato", "sweet potato (boiled, without skin)", "carb", [], 1),
    (169704, "brown-rice", "brown rice (cooked)", "carb", ["rice"], 1),
    (169737, "pasta", "pasta (cooked, enriched)", "carb", ["wheat", "gluten"], 1),
    (170285, "barley", "barley (cooked)", "carb", ["gluten"], 1),
    (172429, "split-peas", "split peas (cooked)", "protein", ["legumes"], 1),
    (175194, "kidney-beans", "kidney beans (cooked)", "protein", ["legumes", "beans"], 1),
    (175200, "pinto-beans", "pinto beans (cooked)", "protein", ["legumes", "beans"], 1),
]

SELECTION.extend(
    [
        (170567, "almonds", "almonds (raw)", "fat", ["tree nuts", "almonds"], 3),
        (170187, "walnuts", "walnuts (English)", "fat", ["tree nuts", "walnuts"], 3),
        (170554, "chia", "chia seeds (dried)", "fat", ["seeds"], 3),
        (170556, "pumpkin-seeds", "pumpkin seed kernels (dried)", "fat", ["seeds"], 2),
        (
            172470,
            "peanut-butter",
            "peanut butter (smooth, unsalted)",
            "fat",
            ["peanuts", "legumes"],
            2,
        ),
        (173432, "skim-milk", "skim milk (fluid, unfortified)", "protein", ["milk"], 1),
        (175215, "soy-milk", "soy milk (unsweetened, fortified)", "protein", ["soy"], 2),
        (171496, "turkey", "turkey breast (roasted, meat only)", "protein", ["poultry"], 2),
        (174028, "lean-beef", "lean beef (95 percent, cooked crumbles)", "protein", ["beef"], 3),
        (171705, "avocado", "avocado (raw)", "fat", [], 3),
        (169910, "mango", "mango (raw)", "fruit", [], 2),
        (169291, "zucchini", "zucchini (raw, with skin)", "vegetable", [], 1),
        (
            170420,
            "green-peas",
            "green peas (boiled, unsalted)",
            "vegetable",
            ["legumes", "peas"],
            1,
        ),
        (169999, "sweetcorn", "sweetcorn (boiled, unsalted)", "vegetable", [], 1),
        (168914, "rice-noodles", "rice noodles (cooked)", "carb", ["rice"], 2),
    ]
)


def main(archive):
    archive = Path(archive)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != "b80817294b8850530aaedf2e515c02593b1824f763a0ff356e5c2081643e6fd0":
        raise ValueError(
            "Archive differs from reviewed USDA April 2018 source; review before import"
        )
    with zipfile.ZipFile(archive) as z:

        def rows(name):
            path = next(n for n in z.namelist() if n.endswith("/" + name))
            return csv.DictReader(io.StringIO(z.read(path).decode("utf-8-sig")))

        foods = {int(r["fdc_id"]): r for r in rows("food.csv")}
        selected = {r[0] for r in SELECTION}
        nutrients = {fid: {} for fid in selected}
        keys = {
            "1003": "protein",
            "1004": "fat",
            "1005": "carbs",
            "1008": "source_calories",
            "1079": "fiber",
            "1093": "sodium_mg",
            "1087": "calcium_mg",
            "1089": "iron_mg",
            "1092": "potassium_mg",
        }
        for row in rows("food_nutrient.csv"):
            fid, nid = int(row["fdc_id"]), row["nutrient_id"]
            if fid in selected and nid in keys:
                nutrients[fid][keys[nid]] = float(row["amount"])
        output = []
        for fid, key, name, role, allergens, tier in SELECTION:
            values = nutrients[fid]
            assert {"protein", "fat", "carbs", "source_calories"} <= values.keys(), (
                f"Missing nutrients for {fid}"
            )
            for nutrient in keys.values():
                values.setdefault(nutrient, None)
            output.append(
                {
                    "id": key,
                    "name": name,
                    "role": role,
                    "serving_g": 100,
                    "data_version": "SR-Legacy-2018-04 / curated-v3",
                    "allergen_review": "generic-ingredient-screened; product and cross-contact unknown",
                    "certification": {"halal": "unknown"},
                    "units": {"mass": "g", "energy": "kcal", "macros": "g"},
                    "per_100g": values,
                    "allergens": allergens,
                    "vegan": key
                    not in {
                        "chicken",
                        "yogurt",
                        "egg",
                        "salmon",
                        "skim-milk",
                        "turkey",
                        "lean-beef",
                    },
                    "vegetarian": key not in {"chicken", "salmon", "turkey", "lean-beef"},
                    "cost_tier": tier,
                    "halal_note": "Choose appropriately certified halal meat; nutrient record is not halal certification."
                    if key in {"chicken", "turkey", "lean-beef"}
                    else "Check product ingredients, processing and certification requirements.",
                    "source": {
                        "publisher": "USDA FoodData Central",
                        "fdc_id": fid,
                        "description": foods[fid]["description"],
                        "url": f"https://fdc.nal.usda.gov/food-details/{fid}/nutrients",
                        "dataset": "SR Legacy April 2018",
                        "publication_date": foods[fid]["publication_date"],
                        "reviewed_at": "2026-10-31",
                        "license": "CC0-1.0",
                        "license_url": "https://fdc.nal.usda.gov/api-guide/",
                        "download_url": "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip",
                        "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                    },
                }
            )
        target = Path(__file__).resolve().parents[1] / "app/data/ingredients.json"
        sys.path.insert(0, str(target.parents[2]))
        from app.ingredients import validate_catalog

        validate_catalog(output)
        target.parent.mkdir(exist_ok=True)
        pending = target.with_suffix(".pending")
        pending.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
        pending.replace(target)
        print(f"Extracted {len(output)} ingredient records")


if __name__ == "__main__":
    main(sys.argv[1])
