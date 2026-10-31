# Calculation and recommendation methodology

## Evidence categories

All athlete measurements and experiences are user-reported unless a benchmark is explicitly labeled measured or estimated by the user. These labels are not independent verification. Fighter attributes are dated official-source snapshots. Calculations, heuristic recommendations, local coaching and AI-generated interpretations have distinct UI explanations. Unknown values remain null, never zero.

## Units and physical calculations

Canonical database units are centimeters, kilograms and seconds. One inch = 2.54 cm and one pound = 0.45359237 kg. Imperial form conversions round canonical values to four decimal places. BMI = kg / meters²; ape index = wingspan − height; reach ratio = wingspan / height; lean mass estimate = kg × (1 − body-fat percentage / 100). Waist/hip ratio is calculated only when both exist. Standing reach is separate and never substituted for wingspan. BMI is not body composition or skill.

## Divisions

The simplified scale reference is the first active championship limit at or above everyday weight, using exact pound conversions. It is not eligibility or a recommended competition class. Non-title allowances are separate reference values, subject to regulator/event rules. Men's limits are 125/135/145/155/170/185/205/265 lb. Active women's reference limits are 115/125/135 lb; 145 lb is labeled historical and excluded. Above the largest active limit returns no active reference. Target-weight guidance returns insufficient information rather than an invented target. Minors receive no weight-cut advice.

## Fighter matching (Phase 4)

The deterministic `resemblance-v2` engine scores each height/reach difference as `100 * exp(-0.5 * (difference_cm / 15)^2)`. It combines these scores using physical subweights (height/reach defaults 50/50), renormalized over measurements available on both sides. An optional reach/height-ratio score uses scale 0.05 and defaults to zero to avoid double counting derived reach. These scales and weights are product heuristics, not scientifically fitted predictors.

Background and supported shared style traits use Jaccard overlap; stance uses exact agreement. Source-listed style labels are descriptive, separate from the shared controlled taxonomy. Local records have no verified stance or controlled style traits, so those dimensions are excluded. Unknown background is not treated as no experience. No skill, professional proficiency or outcome comparison is made.

Division compatibility uses the nearest active title-limit difference across documented UFC history, or only the profile-listed current division if selected: `100 * exp(-abs(limit_difference_lb) / 30)`. Both assessment and matching read the same validated stored reference. Everyday weight maps to the first active reference title limit above it. It is not a target or competition eligibility decision. Listed fighter weight has no effect on ranking. Retired/not-fighting records do not acquire a current division, and historical women's featherweight remains inactive.

Group weights default to physical/background/style/stance/division = 60/15/10/5/10 and are renormalized over supported dimensions. Requested-weight coverage separately accounts for absent groups and absent physical subdimensions. A high resemblance with low coverage is not stronger evidence than a lower score with better coverage. Filters can require minimum coverage, same reference division, active source status or observations within 365 days. Fresh observation does not imply a newly taken measurement. An old published statistic remains historical even if its page was recently observed.

All-zero group weights, and all-zero physical subweights when physical is enabled, are invalid. No supported positive-weight components produces an unscored manual comparison and no ranked match. Category mismatches are unscored manual references. Full-precision score sorts descending, exact ties by fighter ID; display is rounded to whole points. Top three are returned. Manual comparisons use the same engine without the top-three restriction. Source snapshots, reference version, algorithm, weights and athlete inputs are frozen in favorites; loading a favorite uses those inputs. Re-evaluation is explicit.

Full audit, coverage limits and source review method: [PHASE4_COMPARISON.md](PHASE4_COMPARISON.md).

## Training

Twelve weeks use foundation (1–4), development (5–8) and consolidation (9–12), with reduced volume in weeks 4/8/12. Availability is capped at six days and at three for minors, low sleep or reported recovery/limitation flags. Fixed day patterns separate strength sessions. Session caps never exceed reported daily minutes; short strength sessions reduce sets and exercise count. RPE is conservative and contact training is never prescribed without qualified supervision. Basic experience, equipment and recovery influence the template. The plan is not rehabilitation or an advanced competition camp.

Profiles and plans are independently versioned. Editing a profile does not mutate the active plan. Approved proposals create new plan versions with input snapshots and restart the roadmap; stale or already-resolved proposals cannot replace the current version. Reassessment compares current check-ins against active-plan baseline and reduces suggested frequency only for significant fatigue/low sleep flags. Daily weight changes do not regenerate plans.

## Nutrition (Phase 5)

Calculations, ingredients, dietary screening, meal composition, validation, integrity/versioning and AI explanations are separate modules. [Phase 5 design and coverage](PHASE5_NUTRITION_COACH.md) supersede the former illustrative-food template.

The simplified [Mifflin?St Jeor equation](https://pubmed.ncbi.nlm.nih.gov/2305711/) estimates resting expenditure: `10*kg + 6.25*cm - 5*age + s` (+5 male, -161 female equation constant). It is an estimated resting/BMR proxy, not measured BMR. Equation input is independent of competition division; unspecified input withholds targets. Self-reported activity factors 1.4/1.6/1.8 and the ?15% maintenance band are product heuristics, not measured TDEE or a confidence interval.

Default is maintenance. An explicit optional build/reduction goal permits at most the smaller of 5% or 150 kcal. Reduction is withheld for BMI below 25, competitive users, poor sleep, recovery concerns or high reported hunger; competitive gain adjustments are also withheld. Minors, clinical needs/pregnancy/breastfeeding/eating-disorder concerns, BMI below 18.5, very low reported body fat and maintenance estimates outside 1500?4500 kcal receive no numerical plan. These are conservative product exclusions, not diagnostic criteria or a validated weight-management protocol. No pace of weight change or target division is predicted.

Guidance: [ISSN protein position](https://pmc.ncbi.nlm.nih.gov/articles/PMC5477153/) supports 1.4?2.0 g/kg/day for most exercising adults. The [ISSN review](https://pmc.ncbi.nlm.nih.gov/articles/PMC6090881/) provides lower-volume carbohydrate context of 3?5 g/kg/day and 25?35% energy from fat. The composer uses protein 1.6 g/kg, fat 27% energy and carbohydrate as the remainder. It flags carbohydrate outside the general reference rather than silently clipping it; higher-volume MMA training can need individualized fueling beyond this template. These references do not validate the app's exact targets or meal compositions.

Twenty-two ingredients are extracted from USDA FoodData Central SR Legacy April 2018, with source FDC IDs, preparation descriptions, publication dates, CC0 attribution and archive SHA-256. Values are per 100 g in the named edible raw/dry/cooked state; portions scale linearly. Source kcal are preserved separately from macro-derived `4P + 4C + 9F` energy. Fiber and specific Atwater factors can explain differences; source energy is not rewritten to make it match. Meals use rounded macro-derived energy, daily totals sum meals, and groceries sum all seven days' ingredient weights. Source values are historical reference composition, not a freshly analyzed product or allergen certification.

The deterministic composer solves protein/carbohydrate portions against the macro targets, then balances measured oil within portion bounds. Three meals and optional recovery snack use bounded ingredient combinations. Every plan is validated for exact day/meal structure, allowed ingredients, finite totals, catalog version, meal arithmetic, daily target tolerances and groceries. Substitutions preserve the meal's macro context, recalculate seven-day totals and groceries, and are proposed rather than applied automatically. This is not a complete micronutrient, fiber or dietary-quality optimizer; larger legume portions and GI tolerance require review.

Vegan/vegetarian, dairy-free, gluten-free, halal ingredient sourcing, common allergy aliases, explicit dislikes and unavailable catalog ingredients affect eligibility. Unrecognized allergies withhold meals. Dietary additions cannot relax profile restrictions. Uncertified oats are conservatively excluded for gluten/wheat restrictions. Halal poultry must be sourced with appropriate certification; generic USDA entries do not certify products or preparation. Package labeling, intolerances, cross-contact and clinical needs require qualified review. Cuisine settings alter ingredient preferences and are labeled inspired patterns, not authentic recipes. Budget tiers are editorial relative categories, not local prices or a monetary guarantee. Legacy food-preference prose is retained with an explicit warning; structured controls provide reliable exclusions.

Nutrition is withheld after relevant profile, preference/restriction or approved training-volume changes. Three recent check-ins spanning at least 14 days, all at least 2% in one direction from the calculation baseline, trigger a review. A median can be used only in an approved new calculation; the user profile remains unchanged. Isolated fluctuations do not regenerate meals. These thresholds are product rules, not clinical judgments. Current calories are never increased automatically because one workout is logged. Reassessment includes nutrition review status. Pending approvals bind the exact profile, training/nutrition/preferences IDs and progress; later context changes require a fresh preview. Histories remain recoverable through read-only history and account export.

## Progress and AI

Trend charts use actual logs without synthetic demo history. Recorded bests group matching test/unit/repetition/evidence labels; faster timed runs and larger loads/repetitions/jumps are favorable within that group. Effort and measurement protocols still matter. Reassessment only compares same units and repetitions; values are not a validated composite athlete rating.

OpenAI receives a reduced current context: goal/availability/discipline background, usable approved session/meal summaries, diet/allergy additions, recent recovery and training summaries, plus the user's question. Name, country, raw body measurements, recovery free text and full history are not automatically sent. Goal/question prose may itself contain personal information. The frontend explains transmission and requires the provider toggle. No API key is exposed.

Structured explanations and nullable action intents are schema-validated. Only whitelisted session shortening, exercise substitution, solo boxing focus and meal substitution can reach deterministic validation; the model has no write tools. Backend previews store source bindings and exact before/after data. Approval revalidates in a serialized account transaction, saves a new version and marks the proposal resolved together; rejection leaves plans unchanged. Unsupported requests, unavailable providers and failed validation use deterministic local behavior. Plain-language explanations still need judgment; numeric/prohibited-claim checks are defense in depth, not a guarantee of semantic accuracy.

Provider calls use a fixed HTTPS endpoint, validated model setting, 16,000-character input cap, 1,100 output-token cap, a 20-second overall deadline and short per-operation timeouts. Maximum two attempts: retry connection failure or 429/503 only, with at most one second of indicated retry delay. Read timeouts, invalid JSON/schema, refusal, incomplete output, credentials/configuration problems and unknown numerical claims fall back; no uncontrolled retry loop. Numeric grounding uses typed context/intent facts, not numbers embedded in user prose. Sanitized usage records contain attempts, duration, bounded token counts and outcome; logs omit keys, questions, names, measurements and raw responses. Paid live-provider behavior and production rate limiting remain unverified.


## Training template v2 and approval integrity

The conservative 12-week generator uses timed work blocks, with five-minute warm-up and cool-down allowances included in the daily cap. One/two-day availability combines strength, technical practice and easy conditioning. Strength experience/equipment alter movement choices and volume; intensity affects the RPE cap, priority alters block allocation, and weeks 4/8/12 reduce workload. These are product heuristics, not a validated clinical or sport-performance protocol. Reported training limitations withhold automated exercise prescriptions rather than interpreting an injury. A coach must individualize advanced competition and partner practice.

Generated plans include both the unchanged source profile snapshot and effective recovery-adjusted inputs. Pending revisions bind to the exact source profile, latest dated check-in and active plan. Approval checks those IDs in a serialized account transaction. A new version does not modify the athlete profile or historical records. Revision restarts at week 1 are disclosed in the preview. Benchmark deltas require equal test, unit, repetitions and evidence label; matching those does not prove equal effort or testing conditions.


## Phase 3 catalog and evidence-gated adaptation

The current engine is catalog template v3; [Phase 3 rules and source boundaries](PHASE3_TRAINING.md) supersede the older template description above. Calendar phase labels do not themselves increase volume. All work/rest remains inside timed blocks. Progression is proposed only from comparable actual performance on separate dates, with explicit effort and current recovery context. Repetition/load/time targets do not compound without new actual evidence. Set RPE is not inferred from the prescribed RPE; the session-effort input starts blank.

Relative external load uses the body mass accompanying the entered profile/check-in and retains its repetition count and evidence label. This is not a one-repetition maximum estimate or a professional norm. Running pace is a deterministic duration/distance calculation. Jump results are not converted to power; mobility/recovery remain subjective signals.

Adaptive revisions retain checkpoint and earlier weeks, bind the exact source profile/check-in/workout set, and preserve cycle lineage. Only later weeks may change; target sets, load, reps, RPE and timed budgets remain reviewable before approval. New profile preferences cannot silently raise held time/effort. Performance charts keep previous-cycle logs, while the current cycle alone supports its progression decisions. Current implementation remains informational and requires qualified coaching for contact, advanced and injury-sensitive decisions.


## Phase 7 development model and programming

[Detailed Phase 7 methodology](PHASE7_TRAINING.md) supersedes calendar-based technical complexity and unconditionally regenerated future prescriptions. General strength, relative strength, aerobic conditioning, anaerobic conditioning, explosive performance, mobility, training age, technical experience, recovery/fatigue and availability are separate evidence dimensions, with observations/estimates/missing data identified. No composite or professional norm is calculated. Anaerobic capacity has no validated input protocol and remains missing.

Selected weekdays constrain the template; low-training beginners have a four-day cap and cautious/youth contexts retain the three-day cap. Explicit supervised power and cycling-interval requests have bounded suitability gates, fit existing time blocks and are omitted on deloads/unsupported recovery. Technical stages depend on recorded discipline history/goals/access, never height/reach or calendar phase alone. Current actual sets/effort and conservative recovery/performance freshness gates support proposals; possible plateaus hold rather than automatically add volume. Compatible approved sessions survive reassessment, while shorter budgets replace hard blocks that no longer fit. All modifications still require approval and preserve history. These rules are transparent app heuristics, not an independently validated MMA protocol.


## Fighter matching Phase 8

`resemblance-v3` keeps the deterministic Gaussian/Jaccard/reference model but scales the physical group's contribution by the fraction of requested physical subweights actually supported. Thus incomplete physical evidence no longer retains the entire requested physical influence when other groups exist. Missing values remain excluded rather than zero. Coverage and source/freshness warnings are separate from the whole-point resemblance score. Configured/effective percentages use largest-remainder allocation at two-decimal precision so each nonempty weight set sums to 100%. No calibration, professional proficiency or competitive-outcome inference is claimed.

Search pagination is independent from top-three scoring. Manual lookup uses the primary key; a ranking request shares one division-reference read across all candidates. Saved comparisons retain their original algorithm/input/source snapshots. [Phase 8 report](PHASE8_FIGHTERS.md) documents equations, sources, duplicates/conflict/rollback rules, query evidence and coverage limits.


## Phase 12 consolidated inventory

The [current method-by-method inventory](review/METHODOLOGY_INVENTORY.md) records 31 methods, assumptions, source scope, limitations, controls and pending expert-review status. The [safety report](PHASE12_SAFETY.md) records automated corrections and four unfilled specialist review packs. Reassessment now requires matching recorded effort; trained deload rep text/ranges agree. Numerical nutrition is withheld for recognized extreme-cut goals. Automated tests are not professional approval.
