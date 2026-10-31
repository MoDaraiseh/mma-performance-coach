# C — sports dietitian review pack

Workflow: **independent review pending**. Macro arithmetic and exclusion tests are not nutritional adequacy, allergy clearance or clinical approval.

## Scope and algorithms

Review P4–P6, N1–N9 and C1 in [the inventory](METHODOLOGY_INVENTORY.md), including sources R1/R2/R5/R6/R8/R9. Inspect `nutrition_calculations.py`, `ingredients.py`, `dietary.py`, `meal_composition.py`, `nutrition.py`, `nutrition_integrity.py`, `nutrition_models.py` and USDA source metadata.

Mifflin–St Jeor resting estimate is multiplied by reported activity1.4/1.6/1.8. The ±15% band is heuristic, not a confidence interval. Explicit gain/reduction is limited to the smaller of5%/150kcal; reduction has conservative withholding gates. Protein target1.6g/kg, fat27%energy and carbohydrate remainder are a deterministic template. The contextual P1.4–2g/kg/C3–5g/kg/F25–35% ranges are not adequate for every MMA workload. The1500kcal floor is not evidence of adequate energy availability.

The40-food USDA historical catalog scales edible grams and preserves source kcal separately from macro-derived4P+4C+9F display energy. Linear macro portion solving and meal rotation produce seven days; micronutrient coverage is limited. Generic-food editorial allergen/diet tags cannot certify real products or cross-contact/halal status. Food replacements recompute portions/totals and require preview/approval/new versions.

## Actual generated examples

[examples.json](examples.json) supplies full synthetic profiles, calculated numbers, a generated first day (seven-day generation is truncated only in this review artifact) and training context. Regenerate with `python tools/build_review_examples.py` from backend.

| Case | Actual generated result | Review concern |
| --- | --- | --- |
| `adult_beginner` | 26y,180cm,78kg, male equation input/moderate activity: RMR1780, maintenance2848kcal, P124.8/C395.0/F85.4g | Whether activity/macro assumptions and feasible food portions suit the stated intended population |
| `trained_supervised` | Same age/size, female equation input/moderate activity:2582kcal, P124.8/C346.4/F77.5g | Six40min template sessions do not establish true energy expenditure; outside activity/intensity may underfuel |
| `minor` | No numbers, meals or grocery list | Youth nutrition requires appropriate individualized oversight |
| `rapid_cut_request` | No numbers/meals; referral for unsupported10kg/3day request | No dehydration or restriction instructions |
| `unknown_allergy` | Meals withheld for unmapped allergy | False certainty must not be substituted for missing allergen data |
| `injury_conflict` / `low_recovery` | Maintenance template remains available because clinical-nutrition screening was not selected | Does injury/recovery context require a stronger nutrition gate or activity reassessment? This is not a treatment diet. |

## Questions and acceptance criteria

1. Define appropriate age, health and training populations for the equation, activity factors, estimation band and withholding criteria. Current clinical flag combines medical needs, pregnancy/breastfeeding and eating-disorder concerns; it does not establish the absence of these conditions.
2. Review1500–4500maintenance limits,1500target floor, BMI/bodyfat and hunger/recovery gates. Acceptance must never imply these thresholds establish safe energy availability or medical suitability.
3. Review energy availability, low-energy-availability concerns and referral wording. The app lacks reliable measured intake/exercise expenditure/FFM and must not calculate a REDs diagnosis or “safe” EA threshold.
4. Assess carbohydrate adequacy for MMA/strength/endurance, protein distribution, fat assumptions, fiber/sodium/mineral balance and missing nutrients. Acceptance requires explicit limits; seven days of matching macros cannot establish complete nutrition.
5. Evaluate portions, fruit/vegetable variety, three/four meals, meal assembly instructions, ingredient affordability and cultural preferences. Cost tiers are not monetary budgets; cooking estimates exclude batch prep.
6. Confirm allergies, gluten/dairy restrictions, vegan/vegetarian and halal sourcing remain conservative and uncertain classifications visible. No allergen-free or halal-certified claim without product evidence.
7. Confirm substitutions respect exclusions, recompute all totals and preserve prior versions; sustained changes prompt review, not continuous autonomous replanning.
8. Define competition-specific referrals and boundaries without introducing dehydration guidance or automated minor targets.

## Feedback and reviewer record

Reviewer name: ____________________  Dietitian credential / regulator: ____________________

Sports-nutrition qualification and relevant populations: ____________________

Review date: ____________________  Code/catalog version/hash reviewed: ____________________

Approval status: ____________________  Approved scope and exclusions: ____________________

| Method ID / example / meal | Finding / correction | Evidence / calculation | Severity | Acceptance test | Decision / implementation reference |
| --- | --- | --- | --- | --- | --- |
| | | | | | |
| | | | | | |

Reviewer signature/original feedback reference: ____________________
