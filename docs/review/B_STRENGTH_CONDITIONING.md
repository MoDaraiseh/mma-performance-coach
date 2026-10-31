# B — strength and conditioning specialist review pack

Workflow: **independent review pending**. Automated checks verify implementation behavior, not physiological effectiveness or individual safety.

## Scope and algorithms

Review A1–A2 and T1–T10 in [the inventory](METHODOLOGY_INVENTORY.md). Sources R3/R4 support broad principles only. Inspect `athletics.py`, `training.py`, `exercises.py`, `progression.py`, `plan_integrity.py`, `analytics.py`. Exact workload, RPE, exposure, freshness and percentage thresholds are product heuristics.

The planner has 12 weeks, 30/40min base sessions within availability, capped days, timed blocks, low set counts, weeks4/8/12 deloads and no mechanical weekly escalation. Progression requires two recent separate-date comparable actual completed exposures, recorded effort and current recovery. It proposes +1rep, +2.5%load or up to+5%conditioning duration; failed/missed work holds. Three unchanged comparable exposures prompt a possible-plateau review. Approved plans remain intact until explicit approval of a bound proposal.

## Generated examples

[examples.json](examples.json) contains full synthetic inputs, athletic domain evidence and actual weeks1/4; weekly minute vectors show the whole cycle.

| Case | Actual output | Inspect |
| --- | --- | --- |
| `adult_beginner` | Four days, 120min/week initially, novice single sets and 6–8rep range | Newcomer tolerance, recovery spacing, achievable exercises and rest within blocks |
| `trained_supervised` | Six days, 240min/week initially; requested eligible power and controlled cycling intervals; deload removes those blocks | Whether experience/access gates are sufficient, especially for jumps/throws; no assumed technical expertise |
| `low_recovery` | Sleep3h plus persistent exhaustion; three days/90min, low effort, no hard intervals/power | Whether even this template should be withheld pending professional assessment; no physiological readiness inference is justified |
| `injury_conflict` | Zero sessions, automatic prescription unavailable | Limitations override requests; no automated rehabilitation substitution |
| `minor` | Three days/90min, no automatic adult progression or power | Youth-specific suitability is not established by adult literature |

Exercise descriptions/muscle lists are editorial summaries, not verified individual biomechanics. Alternatives are equipment/non-coach filtered; medical contraindications require individualized assessment.

## Questions and acceptance criteria

1. Review frequency caps, 30/40min budgets, 45–60s strength rest, RPE4–6 and rep ranges. Acceptance requires a defensible intended population and explicit cases needing longer rest, fewer sessions or withholding.
2. Validate that the warmup+blocks+cooldown arithmetic fits and prioritizes fewer quality sets over rushing. Deload displayed/machine rep ranges must agree.
3. Review power2×3 within4min and interval3×(1minRPE7+2min easy), the age/experience/mobility/access gates and recovery spacing. Are these inappropriate for any screened population despite the gates?
4. Review two-exposure, ≤7 strength effort / ≤6 conditioning effort, 14/28day freshness, 2.5%/5% steps and 3-exposure plateau rule. Acceptance requires these remain provisional unless independently supported for the intended context.
5. Which fatigue signals need withholding rather than a lighter session? The app does not diagnose from sleep/soreness/readiness or treat session-RPE load as injury risk.
6. Verify missed-session behavior never adds catch-up work, old plans/history remain recoverable and reassessment changes only future weeks after approval.
7. Evaluate comparable record rules: same repetitions/evidence, reassessment effort matched, same-day body mass, jump height not power, no inferred VO2max/1RM or professional comparison.

Known limits: subjective competence/coaching access, missing external workload, no graded exercise test, no medical clearance, rigid template day patterns and no individual load-tolerance validation. Four/three/six-day caps are not universally safe limits.

## Feedback and reviewer record

Reviewer name: ____________________  Credentials/issuing organization: ____________________

Relevant athlete populations: ____________________

Review date: ____________________  Code version/hash reviewed: ____________________

Approval status: ____________________  Approved scope and conditions: ____________________

| Method ID / example | Finding / correction | Supporting rationale | Severity | Acceptance test | Decision / implementation reference |
| --- | --- | --- | --- | --- | --- |
| | | | | | |
| | | | | | |

Reviewer signature/original feedback reference: ____________________


## Phase 16 review refresh (2026-11-01)

Source baseline: 1943020 (Phase 15); review the Phase 16 diff and regenerated `examples.json` together. All seven examples were regenerated from the current deterministic engine, not an LLM or clinician. Coverage is 19 fighters, 55 USDA ingredients and 49 exercises (15 requiring coach access). These counts describe curated coverage, not completeness. All 31 inventory methods remain independently unvalidated. No actual expert feedback or signed approval was supplied/found; all reviewer, credentials, date and approval fields remain unfilled.

Record each finding with method ID, example ID, severity, proposed correction, rationale/source, acceptance test and disposition. Acceptance requires the qualified reviewer to assess exact outputs and population limits; passing software tests is insufficient. See [operational/security handoff](../PHASE16_OPERATIONS.md) for identity, privacy and licensing gates.

Specialist questions and acceptance gate: Review 49-exercise coverage, bench-free trained floor press, availability caps, fatigue/missed-session holds, plateau rules and approval-only future plan adaptation. Confirm measured and estimated benchmarks remain separate. Accept only after documenting acceptable workload/progression by training age and contraindication referral boundaries.


## Phase 18 isolated-staging review handoff (2026-11-01)

Baseline release v1.0.0-rc.17 / 2f43e4d is preserved; fixes live on phase18-isolated-staging. Seven synthetic examples.json outputs were regenerated from unchanged training/nutrition equations. Internal catalog:19fighters/55foods/49exercises; sanitized staging candidate:8attributed CC-BY-SA fighter snapshots (4men/4women), with the11unresolved original records excluded before the Docker context is built. This is technical exclusion, not legal or specialist approval. PostgreSQL/containers/live IdP remain unexecuted.

Reviewer must record exact revision/output hash, credentials, date, scope, population/exclusions, findings by method/case, severity, correction rationale and retest outcome. Name/date/approval/signature fields above remain blank; no genuine external feedback was supplied or invented. Review all31methodology entries and seven generated examples. See [Phase18 gates](../PHASE18_DELIVERY.md) and [staging procedures](../PHASE18_STAGING.md).

Specific review request: Review availability/fatigue/deload/plateau rules, the49exercise catalog and15coaching-required entries, alternatives and injury limitations; operator alert thresholds are unrelated to athlete physiology.

Full current12-week training and seven-day nutrition outputs (including withheld/unsupported safety cases) are available as [seven synthetic full examples](../evidence/phase18/specialist-full-examples.json). Regenerate using `python tools/build_staging_review.py` from backend. They are software outputs, not expert-approved programs; reviewer fields remain blank.
