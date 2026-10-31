# Phase 12 — safety audit and independent review readiness

Date: 2026-10-31. **Automated validation completed; independent professional approval is pending.** No qualified MMA coach, strength specialist, dietitian or medical professional supplied signed feedback in the inspected repository or during this task. No opinions, credentials, signatures or approvals have been fabricated. Existing features, approved plans and athlete data are preserved; schema remains 0007 and this phase requires no new migration.

## Review deliverables

- [31-method inventory](review/METHODOLOGY_INVENTORY.md): inputs, outputs, equations/heuristics, assumptions/rationale, sources, limitations, safety controls and pending review status.
- [A — MMA technical coach](review/A_MMA_TECHNICAL_COACH.md).
- [B — strength and conditioning specialist](review/B_STRENGTH_CONDITIONING.md).
- [C — sports dietitian](review/C_SPORTS_DIETITIAN.md).
- [D — medical/safety reviewer](review/D_MEDICAL_SAFETY.md).
- [Seven reproducible synthetic profiles and generated recommendations](review/examples.json). `backend/tools/build_review_examples.py` uses an in-memory reference fallback, no athlete database writes and no provider calls. The artifact includes full profiles, generated weeks1/4 and the first generated nutrition day; the actual engine still produces 12weeks/seven days.

Every pack includes relevant algorithms, actual generated examples, questions, acceptance criteria, limitations, feedback tables and blank name/credentials/date/approval fields. A pending workflow label is not a filled approval. Reviewers must record the precise code/catalog version, population and approved scope.

## Findings and implemented corrections

| Priority / finding | Root cause | Correction / regression evidence |
| --- | --- | --- |
| P1: potentially misleading reassessment improvement | `AthleticAssessmentService.compare` matched name/unit/repetitions/evidence but omitted recorded effort. A higher-effort test could be presented as a comparable change. | Include effort in the match key. Different effort/evidence produces no comparison; equal effort retains arithmetic delta. Unknown effort is only matched to equally unknown legacy effort; technique/testing conditions still require review. |
| P2: deload prescription disagreement | Trained deload strength text said6–8reps while `rep_range` stayed8–12, allowing logging/progression expectations to disagree. | Deload human/machine ranges now both6–8; non-deload trained8–12 remains. Regression traverses generated weeks/exercises. Saved approved plans are not silently rewritten. |
| P1: unsupported rapid-cut goals reached generic meal generation | Structured nutrition objectives were conservative, but profile goal/objective/food-preference text was not screened for rapid-cut intent before energy estimation. | Deterministic lexical screen withholds numerical targets/meals for recognized rapid-cut/extreme-restriction patterns. Existing general cut refusal shares the screen. No rapid-loss target, dehydration steps or replacement extreme diet is generated. Previously saved numerical targets under a recognized rapid-cut profile are hidden on current reads and cannot support substitutions; the original snapshot remains unchanged. |
| P1: minor coaching boundary incomplete | Nutrition calculations already withheld minor targets, but coach text could route ordinary calorie/weight requests to a provider explanation. | Explicit minor weight-management/calorie/macro/fasting requests receive qualified youth-nutrition referral before provider invocation. Workout shortening and weight-training explanations are not mistaken for dieting requests. This is a conservative text rule, not comprehensive intent detection. |
| P1: unsupported professional/medical assurances | Structured output alone cannot establish truth or specialist approval. Existing prose screen did not reject several explicit positive endorsement claims. | Reject specified affirmative UFC-readiness/professional-skill, clinically validated/medically approved-plan and allergen-free-meal claims; preserve existing schema/permissions/source validation. Lexical checks do not guarantee semantic safety. |
| P2: insufficient interpretation caveats | Physical ratios could be read using adult BMI categories for minors; lean-mass precision could mask bodyfat uncertainty. Nutrition floors/macro matching could imply adequacy. | Physical explanation now separates BMI, pediatric interpretation and uncertain lean mass. Nutrition explanation states calorie floors/macros do not establish energy availability/completeness or diagnose REDs; independent dietitian review pending. Overview labels automated checks separately from professional approval. |

These are engineering corrections from code inspection and source review, **not implementation of actual expert feedback**. No clinician was asked to clear an individual athlete. No stored approved plan, historical benchmark, meal snapshot or log is rewritten by this phase.

## Safety audit by area

| Area | Existing/current controls verified | Outstanding gate |
| --- | --- | --- |
| Weight classes and targets | Everyday weight, source-listed fighter weight, active/historical division limit and typical non-title allowance remain distinct. Target guidance reports insufficient information; no individualized target or cut rate. Minors receive no cut/numerical nutrition plan. Event/regulator rules determine competition eligibility. | G-MMA/G-DIET/G-MED: current event-specific eligibility, responsible long-term bodyweight goals and any competition preparation require individual professionals. |
| Training workload | Beginner/cautious day caps, time-budget arithmetic, rest days, no automatic catch-up/escalation, recovery/missed/failed progression holds, future-only approved revisions. Limitations withhold automatic sessions even when text requests jumps. | G-SC: exact day/dose/rest/RPE/percentage/freshness thresholds remain heuristics. External class dates/durations/contact load unknown. No universally safe workload limit is claimed. |
| Power/conditioning/contact | Optional adult/experience/recovery/coach/equipment gates; controlled nonmaximal work; deload withholding; no unsupervised hard sparring, throws or submissions. | G-MMA/G-SC/G-MED: self-reported coach access does not verify supervision, technical competence, contact eligibility or medical clearance. |
| Severe recovery and injury | Subjective symptoms never produce diagnoses; no automatic progression with high fatigue/low readiness. Injury limitations override exercise requests. | G-MED/G-SC: determine when a gentle template is still inappropriate and should be withheld. Current low-recovery example intentionally exposes this unresolved question. Free-text screening is not medical triage. |
| Nutrition estimation | Adult/nonclinical/known-input scope; conservative template coverage; explicit optional modest adjustments; competition reduction withheld; unsupported cut goals withheld. | G-DIET/G-MED: estimation bias, athlete-specific activity, metabolic context, calorie floors and underfueling need qualified review. No energy-availability sufficiency or clinical validation. |
| Meals/restrictions | Source-backed arithmetic, bounded portions, seven-day validation, catalog exclusions, unknown-allergy withholding, missing nutrients null, no cross-contact/halal certification assurance, validated substitutions and retained versions. | G-DIET: limited40-food variety, complete micronutrient adequacy, actual product labels, medical/religious requirements, practical portions/budgets and cooking feasibility. |
| AI/professional comparisons | Deterministic numerical services, factual provenance/coverage, no anthropometric skill inference, typed request permissions and explicit approval; unsupported affirmative claims rejected. | All gates: semantic safety and provider quality remain unproven; lexical rules can miss paraphrases or overblock benign mentions. No live provider or expert quality evaluation occurred. |

## Automated verification

Baseline before changes: **286 backend tests passed**. Final full backend suite: **308 passed**, including **22 Phase 12 cases**, with one existing Starlette/httpx deprecation warning. Tests cover extreme goals, minors, excessive availability/workload, conflicting injury requests, low recovery, deload consistency, effort-matched comparisons, unsafe/infeasible restrictions, food allergies, missing clinical/equation context, malformed meal totals and unverified affirmative skill/approval claims. Existing approval/version/access-control suites remain passing.

Frontend: **12 tests passed**. App TypeScript/Vite build, frontend Prettier, backend Ruff lint/format passed. An initial focused test used the wrong existing fixture tuple length; it was corrected before the final full run. This was a test setup error, not an application failure.

Focused real-browser verification: **20 passed, zero failed, zero skips** across Edge widths1440/1920/768/390/375. Five new safety scenarios verified honest review status, persisted unavailable rapid-cut meal plans, visible reasons, no document overflow and zero targeted axe violations. Fifteen existing nutrition/coaching cases verified substitution previews, rejection/approval and stale-source refusal. [Machine results](evidence/phase12/browser-results.json), [mobile evidence](evidence/phase12/mobile-375-phase12-withheld-nutrition.png), [desktop evidence](evidence/phase12/desktop-1440-phase12-withheld-nutrition.png). This is focused regression coverage, not a new all-phase browser certification. Browser QA uses the existing disposable Edge QA environment; it does not modify normal athlete data, contact reviewers or invoke a live AI provider. No new print/PDF validation is claimed for Phase12; the user-facing explanatory text changed and should be part of professional review.

## Outstanding expert-review gates and feedback process

1. **G-MMA — pending:** technical priorities/stages, partner/contact language, fighter-study interpretation, integration with actual coached classes.
2. **G-SC — pending:** workload/rest/dose suitability, youth/trained/older populations, power/interval entry criteria, progression/fatigue/plateau rules, test protocols.
3. **G-DIET — pending:** energy/macro assumptions, meal feasibility/variety/completeness, exclusions, training fueling, energy-availability boundaries and competition referrals.
4. **G-MED — pending:** pediatric/sensitive-population scope, clinical screening/referral, symptom-related withholding, injury/return-to-training and risks of false reassurance.

Store actual submitted feedback separately with provenance and the original wording. Map it to inventory IDs and fixtures; record accept/adapt/reject/defer decisions with rationale and regression evidence. Update only the reviewed scope and retain historical plans. Approval fields must remain blank until the named qualified reviewer actually completes them. Pending specialist review is not a reason to label this product scientifically or professionally validated.


Legacy trained plans with the earlier deload range mismatch remain historical snapshots; preview/approve a current-input revision to obtain corrected prescriptions. No historical plan was silently rewritten. New safety explanations are applied when current nutrition is read, without altering stored payloads.
