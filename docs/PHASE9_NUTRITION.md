# Phase 9 — sports nutrition and meal planning

Work is confined to `mma-performance-coach/`. QA uses disposable databases. Athlete data and saved plan snapshots are preserved. Catalog v2 makes old targets stale until users preview/approve regeneration; history/export remains available. Schema head remains 0006.

## Baseline and changes

Baseline: **239 backend / 12 frontend tests passed**. The 22-food engine already separated deterministic estimates, USDA composition, exclusion rules, portion solving, AI explanations and version persistence. No LLM supplies nutrient numbers. Existing safety, approval/rejection, stale-proposal and provider-failure tests remain.

Fixed limitations: unconditional yogurt/oat breakfast preference, limited automatic protein swaps, absent assembly/meal-count controls, absent sodium/mineral data, missing allergy metadata treated as clearance, and calendar staleness that missed weekday moves with unchanged weekly minutes.

## Actual food coverage

**40 USDA foods**: 11 protein-role, 10 carbohydrate-role, nine vegetables, nine fruits, one oil. Roles are solver categories, not exclusive nutritional properties. All 40 contain source calories, protein, carbohydrate, fat, fiber, sodium, calcium, iron and potassium. Daily dashboard totals for fiber and minerals are recalculated from edible portions; if any contributing value is missing, the total is unknown. Added salt/unlisted foods and dietary adequacy are not inferred. See [machine-readable coverage](evidence/phase9/nutrition-quality.json). Vitamins and many other nutrients are outside the catalog; composition completeness does not establish dietary adequacy.

Source: [USDA SR Legacy April 2018 downloads](https://fdc.nal.usda.gov/download-datasets/), reused under [FoodData Central public-domain/CC0 terms](https://fdc.nal.usda.gov/api-guide/). These are historical generic foods, not a current branded-product feed. Records retain FDC ID, original preparation description, source URL, publication/review date, dataset version, license and archive SHA-256. Roles, relative cost tiers and diet/allergen screening are editorial, distinct from sourced composition.

**Zero halal-certified or cross-contact-verified products.** Unknown product safety is visible. Missing allergen screening excludes a food under allergy/gluten/dairy restrictions; unknown allergies withhold automated meals. Generic screening does not guarantee packaged-product safety. Halal preference requires users to verify actual products/certification.

The extensible importer rejects unexpected archives, duplicate IDs/FDC records, invalid mandatory composition and impossible macro mass before atomic replacement. Missing optional nutrients remain `null`, never zero. Tests validate 1,000 synthetic records solely for capacity; they are not distributed or counted as real foods.

## Calculation methodology

Existing [Mifflin–St Jeor](https://pubmed.ncbi.nlm.nih.gov/2305711/) resting estimates use weight, height, age and selected metabolic equation input. Activity factors 1.4/1.6/1.8 and ±15% maintenance band are product heuristics, not measured expenditure or confidence intervals. Explicit gain/reduction is capped at 5%/150 kcal. Reduction is withheld for competition, lower BMI, poor sleep/recovery or high hunger. Minors, clinical/eating-disorder/pregnancy concerns and unsupported profiles receive referral, not numerical plans.

Protein guidance 1.4–2.0 g/kg follows [ISSN](https://pmc.ncbi.nlm.nih.gov/articles/PMC5477153/). The solver uses protein 1.6 g/kg, fat 27% energy and carbohydrate remainder. General carbohydrate guidance 3–5 g/kg describes lower-volume exercise; [ISSN's review](https://pmc.ncbi.nlm.nih.gov/articles/PMC6090881/) identifies higher requirements under larger workloads. Departures/high volume are flagged. No rapid-cut, dehydration, body-fat target or clinical protocol was added.

Displayed meal kcal uses **4P+4C+9F** from rounded macros, with USDA source kcal separate. Fiber and food-specific factors cause legitimate differences. Mass conversion supports g/kg/oz; cups require food-specific densities and are rejected rather than guessed.

## Meals and customization

Seven days provide breakfast/lunch/dinner and optional snack. Explicit count supports **three or four meals**, with existing snack preferences retained. Cooking skill and 10–120 minute assembly limit are saved. All templates estimate ten minutes assembly using matching batch-cooked/ready-cooked components; batch cooking and shopping are additional. These controls do not claim full cooking-time accounting or advanced skill-specific recipes.

Rotating proteins/grains/produce replaces unconditional breakfast favoritism. The default fixture has **17 ingredient combinations across 28 meals**; restrictions can reduce variety. This remains a bowl/assembly template, not a chef-developed recipe library. Steps describe weighing preparation-state portions, separating foods and safe reheating. Cuisine settings prioritize ingredients without claiming authenticity. Budget filters editorial relative tiers, not local prices or monetary guarantees.

Chosen substitutions support protein, grain, fruit for breakfast/snack, or vegetables for lunch/dinner. Other portions may rebalance to preserve targets. Backend checks exclusions and feasibility. Fat-only swaps and arbitrary amounts are outside coverage. Preview shows before/after portions, nutrient deltas, seven-day totals and groceries. Approval revalidates bindings and deterministic output before appending a version. Rejection retains active plans/history.

High-volume (>90 minutes), ordinary training and recovery days show distinct guidance from the first approved training week and optional timing preferences. Recovery days retain meals without automatic calorie reduction. Weekday changes now invalidate stale timing even when weekly minutes match. **Automatic calorie cycling, intensity-based expenditure and separate strength/endurance macro prescriptions remain outside coverage. Session-specific strength/conditioning explanations use approved practice types; changes in those types also invalidate timing guidance.** More workload information and specialist review are needed.

## Validation and remaining limitations

New tests cover serving conversions, missing optional composition, invalid/duplicate imports, uncertain allergy metadata, synthetic capacity, three/four meals, vegan budgets, variety, assembly bounds, replacement arithmetic/immutability, recovery guidance and same-volume calendar staleness. Browser tests exercise saved preferences, selected substitutions, previews/approval/history, overflow and axe at five viewports. Actual execution results are appended below.

Remaining: more current foods/brands, volume densities, product certification, full recipes/cooking times, monetary budgets, additional meal counts, complete micronutrient adequacy, specialist-designed strength/endurance/day-specific fueling, and independent review. No professional approval is claimed. Medical, competition-specific and eating-disorder concerns require qualified assessment.

## Update and specialist review

From `backend/`: `..\.venv\Scripts\python.exe tools/import_usda.py ../.qa-runtime/usda-sr-2018.zip`. Expected SHA-256: `b80817294b8850530aaedf2e515c02593b1824f763a0ff356e5c2081643e6fd0`. The archive is not needed at startup. Extend reviewed `SELECTION`, check source preparation states and editorial restrictions, validate output, bump catalog version and rerun tests. New sources need permissions/units review. Use source control for catalog rollback; athlete history is independent.

See [specialist-review checklist](SPECIALIST_REVIEW.md). Review energy availability, metabolic-input limitations, GI tolerance/fiber/portion practicality, complete micronutrient adequacy, palatability/culture, preparation safety, allergy/halal uncertainty, prices and referral pathways. Automated tests establish software behavior, not sports-dietetic validation.

## Actual verification results

| Check | Result |
| --- | --- |
| Baseline | 239 backend, 12 frontend passed |
| Final backend | **251 passed**, one existing upstream Starlette/httpx deprecation; [output](evidence/phase9/pytest.txt) |
| Frontend | **12 passed** |
| Ruff lint / format | Passed; 48 Python files formatted |
| App/browser TypeScript and Vite | Passed |
| Prettier | Passed for frontend source and browser tests |
| USDA import reproduction | 40 records, pinned official archive accepted; nutrient IDs/units checked against its nutrient table |
| A4 reports | Four reports, **14 pages**, zero blank pages or margin violations; [checks](evidence/phase9/print-checks.json). Nutrition page and desktop preview visually inspected |
| Final real Edge matrix | **113 passed, zero failed, seven intentional skips**, zero flaky cases in 7.3 minutes; [full JSON](evidence/phase9/browser-results.json) |

The [initial full browser run](evidence/phase9/browser-initial.json) passed 108 existing cases, skipped seven intentional viewport duplicates and failed five new cases because the fixture requested pasta already present in the meal. The backend correctly rejected a non-distinct substitution. The test now selects a different grain; the corrected full rerun is recorded separately. No retry-based flaky pass is claimed.

Browser evidence uses installed headless Microsoft Edge at 1440/1920/768/390/375 px, disposable SQLite and no paid provider. Physical devices, Safari/Firefox, manual assistive technology, live regional prices/product labels and independent specialist review remain unverified. The original tracker has no tracked-file changes.

All five new cases passed the corrected full run, including saved cooking/meal-count inputs, selected grain replacement, preview deltas, approval/history, no horizontal overflow and zero targeted axe violations. Desktop 1440 and mobile 390 screenshots and a rendered nutrition print page were visually inspected. Evidence: [1440](evidence/phase9/desktop-1440-phase9-substitution.png), [1920](evidence/phase9/desktop-1920-phase9-substitution.png), [768](evidence/phase9/tablet-768-phase9-substitution.png), [390](evidence/phase9/mobile-390-phase9-substitution.png), [375](evidence/phase9/mobile-375-phase9-substitution.png). These are full-page captures; fixed header placement reflects scroll position during capture.

The redirected PowerShell logging wrapper returned exit 1 although Playwright's full report contains `113 expected`, `0 unexpected`, `0 flaky` and no suite-level errors, and its console summary says 113 passed. A focused five-viewport confirmation with explicit native exit handling **passed all five cases in 37.8 seconds and exited 0**, recorded in [confirmation JSON](evidence/phase9/browser-confirmation.json). The wrapper discrepancy is disclosed rather than silently reported as a successful shell exit. Seven intentional full-suite skips avoid redundant desktop drawer and multi-viewport PDF tests.

Rollback also requires a fresh catalog version: restore reviewed source records, assign a new version and rerun validation so previously generated targets cannot silently appear current against changed composition.
