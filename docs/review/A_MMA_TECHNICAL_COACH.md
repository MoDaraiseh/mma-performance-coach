# A — MMA technical coach review pack

Workflow: **independent review pending**. This document is prepared by automated code inspection, not a coach's approval. Review the exact code/examples supplied, not the product in general.

## Scope and algorithms

Review inventory methods P3, P5–P7, A3–A4, T1, T4, T8 and C1 in [the methodology inventory](METHODOLOGY_INVENTORY.md). Implementation: `backend/app/analysis.py`, `athletics.py`, `training.py`, `matching.py`, `coach_actions.py`, `coach_security.py`. Technical priorities score preferences/access/goals and subtract existing practice load; technical stage uses experience/level/access. Neither height nor reach rates fighting skill. Source-backed fighter measurements feed heuristic resemblance, not potential. Contact drills require reported instructor access; unsupported practice falls back to non-contact footwork. There is no hard-sparring progression or unsupervised submission/throw prescription.

## Generated examples to inspect

Open [examples.json](examples.json); this contains actual deterministic outputs, not reviewer opinions. Full synthetic input profiles, technical priorities, physical results and generated weeks 1/4 accompany each case.

| Case | Profile and actual generated behavior | Review concern |
| --- | --- | --- |
| `adult_beginner` | 26y, no recorded technical history, 6 requested days; four 30min sessions/week; fundamentals/solo footwork | Does missing experience/coaching access remain clear? Is the selected mix useful rather than a false curriculum? |
| `trained_supervised` | Four gym years, five current sessions, comfortable mobility, strength-coach access; six 40min sessions; **no entered martial arts history** | Strength experience must not establish technical refinement or instructor access. |
| `minor` | 16y; three 30min sessions; no numerical nutrition target or cut | Which youth-specific content should be withheld until a qualified youth coach reviews it? |
| `injury_conflict` | Knee-pain limitation despite requested jumps; no automatic sessions | Confirm limitation cannot be overridden by a goal or instruction in free text. |
| `rapid_cut_request` | Wants 10kg loss in three days; nutrition withheld; ordinary skill template remains informational | No competition readiness or division-change promise should arise. |

Also inspect seven independent discipline rows: Boxing, Muay Thai, Kickboxing, BJJ, Wrestling, Judo and integrated MMA (stored as `MMA`). Clinch is an additional development topic. Athlete participation minutes are explicit logs, not inferred proficiency.

## Questions and acceptance criteria

1. Are the priority weights, stage cutoffs (<12 / ≥36 months), curriculum cues and fallback solo movements appropriate? Accept only with documented population and supervision limits; these are unvalidated heuristics.
2. How should exact class dates, class durations and technical contact load be collected before advanced scheduling? Existing classes are notionally part of the day budget; the app cannot prove all outside practice fits.
3. Is any cue reasonably interpretable as permission for unsupervised contact, takedowns, sparring or submissions? Acceptance requires no such instruction and explicit qualified supervision for partner work.
4. Do fighter similarities use only supported fields and distinguish current/historical divisions, everyday weight and weigh-in limits? Acceptance requires no equal-proficiency, optimal-style or professional-potential claim.
5. Which recommendations require video/in-person observation rather than questionnaire data? Record them as explicit review gates; do not approve them solely from self-reported months.

Known limits: sparse 17-fighter subset; source styles/background may be missing; no technical observation, contact-load accounting, coaching credential verification or competition clearance. Specialist approval must name the versions and populations reviewed.

## Feedback and reviewer record — leave blank until actually reviewed

Reviewer name: ____________________  Credentials/issuing organization: ____________________

Relevant MMA/youth coaching experience: ____________________

Review date: ____________________  Code version/hash reviewed: ____________________

Approval status: ____________________  Approved scope/populations/conditions: ____________________

| Method ID / example | Finding or requested correction | Evidence / rationale | Severity | Acceptance test | Decision / implementation reference |
| --- | --- | --- | --- | --- | --- |
| | | | | | |
| | | | | | |

Reviewer signature/reference to original feedback: ____________________

No signature or automated test result in this repository substitutes for this review.


## Phase 16 review refresh (2026-11-01)

Source baseline: 1943020 (Phase 15); review the Phase 16 diff and regenerated `examples.json` together. All seven examples were regenerated from the current deterministic engine, not an LLM or clinician. Coverage is 19 fighters, 55 USDA ingredients and 49 exercises (15 requiring coach access). These counts describe curated coverage, not completeness. All 31 inventory methods remain independently unvalidated. No actual expert feedback or signed approval was supplied/found; all reviewer, credentials, date and approval fields remain unfilled.

Record each finding with method ID, example ID, severity, proposed correction, rationale/source, acceptance test and disposition. Acceptance requires the qualified reviewer to assess exact outputs and population limits; passing software tests is insufficient. See [operational/security handoff](../PHASE16_OPERATIONS.md) for identity, privacy and licensing gates.

Specialist questions and acceptance gate: Review the explicit general-development versus amateur-preparation context (no automatic dose increase), coaching-required partner drills, seven independent discipline assessments and lack of professional-proficiency inference. Confirm no implicit competition readiness or unsupervised contact progression. Accept only after reviewing novice/youth/injury examples and documenting supervision requirements.


## Phase 18 isolated-staging review handoff (2026-11-01)

Baseline release v1.0.0-rc.17 / 2f43e4d is preserved; fixes live on phase18-isolated-staging. Seven synthetic examples.json outputs were regenerated from unchanged training/nutrition equations. Internal catalog:19fighters/55foods/49exercises; sanitized staging candidate:8attributed CC-BY-SA fighter snapshots (4men/4women), with the11unresolved original records excluded before the Docker context is built. This is technical exclusion, not legal or specialist approval. PostgreSQL/containers/live IdP remain unexecuted.

Reviewer must record exact revision/output hash, credentials, date, scope, population/exclusions, findings by method/case, severity, correction rationale and retest outcome. Name/date/approval/signature fields above remain blank; no genuine external feedback was supplied or invented. Review all31methodology entries and seven generated examples. See [Phase18 gates](../PHASE18_DELIVERY.md) and [staging procedures](../PHASE18_STAGING.md).

Specific review request: Compare technical-priority explanations with the smaller staged fighter set; no ranking implies professional skill. Confirm beginner/coached-contact boundaries and realistic integration with existing practice.

Full current12-week training and seven-day nutrition outputs (including withheld/unsupported safety cases) are available as [seven synthetic full examples](../evidence/phase18/specialist-full-examples.json). Regenerate using `python tools/build_staging_review.py` from backend. They are software outputs, not expert-approved programs; reviewer fields remain blank.
