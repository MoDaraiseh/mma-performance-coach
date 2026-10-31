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
