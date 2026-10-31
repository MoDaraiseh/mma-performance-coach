# Phase 3: training and athletic performance intelligence

Scope: `mma-performance-coach/` only. The original tracker, normal athlete database and external configuration were not changed. Phase 2's 55 backend and 8 frontend tests formed the baseline. This is a functional expansion, not a claim of clinical validation or a complete competition-preparation system.

## Delivered functionality

| Area | Implementation | User workflow |
| --- | --- | --- |
| Curated catalog | `backend/app/exercises.py`: 37 versioned entries, 16 strength, 7 conditioning, 7 athleticism, 7 martial arts. Names, patterns, muscle involvement, equipment, difficulty, technique, set/rep guidance, mistakes, modification notes, alternative IDs, coach requirements and general sources. | Training → Exercise catalog: filter by category, search and expand technique/modification guidance. |
| Athletic evidence | `athletics.py`: relative external load/body mass at the entered repetition count; endurance repetitions/holds; running pace; jump results; mobility and training experience. | Training or Progress → Athletic performance evidence. Recorded observations retain measured/self-reported labels; estimates are a separate section. Missing domains remain explicit. |
| Training generation | `training.py`: catalog-linked prescriptions, movement variation, time-budgeted strength/technical/aerobic/mobility blocks; equipment, goals, intensity, strength experience, access and preferred conditioning modes. | Generate a first plan or explicitly preview a revision. Existing saved plans remain unchanged until approval. |
| Progression review | `progression.py`: repeated comparable exposures, actual sets, effort, separate dates and fresh recovery context gate suggestions. No log operation changes a plan. | Recovery and progression review → Exercise progression decisions; Progress → Run reassessment → Preview recommended adjustment → AI coach → full proposed prescription → Approve or Reject. |
| Recovery/load | Optional muscle soreness 0–10, readiness 1–5, session RPE and set RPE; existing sleep/fatigue; logged completion and actual minutes; session-RPE load proxy. | Weekly check-in and workout logging. Missing signals are labeled unknown; high adverse signals produce conservative holds/reductions. |
| Exercise performance | Actual sets, reps, load, set RPE, seconds, metres, session date, exercise notes, session notes, completed/failed/missed outcome. | Session detail → Add actual set. Training/Progress → Exercise performance over time: select exercise/metric, inspect chronological actual-set chart and table. |
| Substitutions | Equipment-filtered catalog alternatives, category validation, duplicate-exercise prevention and current-input/recorded-session checks. | Session → Exercise substitution → choose an alternative → review proposal in AI coach. Alternatives can change training focus; modification notes disclose this. |
| Periodization/reassessment | Foundation/development/consolidation organize technique; weeks 4/8/12 include deload/reassessment. Approved adaptive changes preserve weeks through the selected checkpoint and modify only later weeks. | Checkpoint selector accepts weeks 4, 8 or 12. At week 12 the report closes the cycle and directs next-cycle planning to the coach; it cannot mutate nonexistent later weeks. |
| Plan/version integrity | Proposals bind exact profile, recovery check-in, base plan and performance-record IDs. Adaptive/substitution versions retain a cycle lineage and earlier logs; explicit new-cycle frequency revisions restart at week 1. | New activity after preview produces a 409 and requires a fresh proposal. History/export preserve earlier plan payloads. Performance charts retain previous-cycle logs, while progression decisions use only the active cycle. |

The existing JSON aggregate architecture stores the additional optional fields. No new database migration is required beyond the existing `0003` schema. Old profiles receive validated defaults; old logs remain readable. Legacy plans without catalog IDs can be reviewed through a fresh reassessment or explicit current-input revision; they are not silently regenerated. Existing installations still need the README's normal `alembic upgrade head` step.

## Prescription rules and limits

Availability is a total weekly budget. Declared instructor-led classes consume technical slots within it, rather than being added on top. Exact outside class dates/durations remain unknown; a coach must align the roadmap with the actual timetable. Short one/two-day schedules combine fundamentals. A full rest day remains available, and generated strength days are separated. Requested modalities fall back to comfortable walking when equipment, experience or recovery do not support them. Sprint, jump, throw, agility and advanced contact entries are educational catalog options, not automatic unsupervised prescriptions.

All work and rest fit timed blocks inside the daily cap, including five minutes each for preparation and cool-down. Plans specify sets, repetitions or timed work, exercise RPE, rests, cues, technique focus, alternatives and progression rules. Basic phases no longer add minutes/sets merely because a calendar week passes. Deloads reduce duration, effort and/or sets; a 20-minute availability cap can have a 15-minute deload prescription. Neither availability nor a phase label obliges the athlete to complete all time.

Progression is deliberately conservative:

- Strength requires two completed, comparable exposures on separate dates with actual sets, matching prescribed dose, sufficient repetitions and reported effort no higher than 7. Below the top of the range, a proposal may add one repetition. At the top, consistent positive external loads can support a 2.5% load suggestion. Suitable small increments and technique must be confirmed; no 1RM is inferred and no load is automatically applied.
- Conditioning requires two comparable timed exposures at reported effort no higher than 6. A proposal may extend that same block up to 5% at unchanged intensity, subject to available session time and a 5% weekly **time** ceiling. This ceiling is not a guarantee about total mechanical stress, tonnage or injury risk. Rest/strength time is not silently replaced to make room.
- Technical phases describe coach-reviewed learning from fundamentals toward linked skills. Experience and recorded instruction access limit the focus. Repeated coached exposure can suggest a coach review; the engine does not escalate contact, sparring, takedowns or submissions. Unsupported disciplines fall back to generic non-contact movement rather than invented technical expertise.
- Missed/failed exposures, missing actual sets/effort, changed dose, missing/stale recovery, or adverse recovery flags prevent automatic progression. No missed-session catch-up volume is added. Repeated missed/failed sessions can support a proposed smaller weekly schedule.
- Under-18 progression is referred to a qualified youth coach. Adult evidence is not presented as validation of youth programming. Reported injury/training limitations continue to withhold automatic exercise prescriptions.

Sleep below six reported hours, fatigue/soreness at least 7, readiness at most 2, or saved recovery concerns are conservative review flags. A check-in older than 14 days cannot support progression. These cutoffs, the two-exposure rule, RPE ceilings, 2.5%/5% steps and checkpoint schedule are **app heuristics**, not medically validated diagnoses, individualized readiness scores or injury predictions.

## Assessments and history interpretation

Relative strength means recorded external load divided by the body mass recorded with the input, retaining repetitions and evidence label. It is not a normative strength grade. Running pace derives from the entered distance-test duration; no VO2max is invented. Jump height/distance remains a result rather than a power measurement. Mobility is a self-assessment. Physiological recovery capacity and fighting ability cannot be established by these inputs.

Set charts display actual entered values, with gaps for missing metrics. Higher loads are not automatically better: compare repetitions, effort, technique, exercise variant and conditions. Failed attempts remain labeled in the table. Historical results survive adaptive versions and new cycles; only the active cycle is used to justify its progression. Workout dates are user-entered, not independently verified. Logged completion uses **logged sessions** as its denominator; unlogged or outside training is unknown.

The new intelligence/catalog panels are excluded from current-view printing to avoid opening the entire catalog in a report. All workout fields, reports and proposal/plan versions remain included in Settings → Download all data. A dedicated consolidated athletic-performance PDF remains future work.

## Scientific basis

Sources were checked on 2026-10-30. They support general principles, not validation of this exact MMA engine, catalog cues or every numerical cutoff:

| Primary source | What it supports / boundary |
| --- | --- |
| [ACSM 2026 position stand](https://pmc.ncbi.nlm.nih.gov/articles/PMC12965823/) | Individualized progressive resistance training for healthy adults. It does not establish that a particular phase structure is necessary or optimal for this application. Enjoyment, access and consistency inform choices; the engine is not claimed to reproduce every recommended adult dose. |
| [ACSM 2009 progression position stand](https://pubmed.ncbi.nlm.nih.gov/19204579/) | Historical context for small load changes after demonstrated capacity. The app's 2.5% step and evidence gate are its own conservative implementation, not a validated MMA rule or a claim that the older paper is the latest guidance. |
| [IOC load consensus](https://bjsm.bmj.com/content/50/17/1030) | Monitoring training, recovery and non-training burden together. This does not provide validated injury-risk thresholds for the app's subjective scores. |
| [Foster et al., 2001](https://pubmed.ncbi.nlm.nih.gov/11708692/) | Session-RPE monitoring research. The displayed minutes × RPE measure is a load proxy with missing-data limitations, not a diagnostic tool. |
| [Saw et al., systematic review](https://pmc.ncbi.nlm.nih.gov/articles/PMC4789708/) | Subjective well-being can inform athlete monitoring. Single self-reported values do not establish a medical diagnosis or complete recovery capacity. |
| [CDC intensity guidance](https://www.cdc.gov/physical-activity-basics/measuring/) | Talk-test description for aerobic intensity. Exercise selection, short blocks and exact progression increments remain product choices. |

Muscle lists describe broad involvement, not activation rankings or causal claims about fighting performance. Technique cues and common mistakes are original editorial summaries requiring practical coach review. No professional-athlete performance norms, fabricated fighter statistics, talent scores, automatic contact escalation or rehabilitation diagnosis were added.

## Verification

Automated checks cannot establish clinical or coaching effectiveness. Practitioner review, physical devices, manual assistive-technology review, other browser engines, PostgreSQL and real paid AI remain outside this verification.

| Check | Result |
| --- | --- |
| Backend | **115 Pytest tests passed**, versus 55 at baseline; one existing upstream Starlette HTTPX deprecation warning. Covers catalog integrity, equipment/time budgets across availability combinations, comparable progression, separate dates, effort gaps, youth boundaries, missed/failed work, fatigue/soreness/readiness, future-only changes, current availability, stale proposals, substitutions, dates/duration validation, cycle lineage and cross-cycle history. |
| Frontend | **8 Vitest tests passed**; app and browser-test TypeScript checks, production Vite build and Prettier passed. Recharts intelligence is loaded as a separate chunk rather than adding its full size to the initial application bundle. |
| Backend quality | Ruff lint and formatting passed for app, tests and migrations. Existing migration round-trip test remains passing; Phase 3 adds no schema migration. |
| Full Edge matrix | **53 passed / 7 intentional skips / 0 failures** in the final full matrix. [Final full results](evidence/phase3/browser-results-final.json). Skips are the mobile-drawer checks on three non-mobile viewports and PDF generation on four non-primary projects. The final focused UI/class-allocation/print rerun passed **11 cases / 4 intentional print-project skips / 0 failures**: [final focused results](evidence/phase3/final-targeted-results.json). Widths: 1440, 1920, 768, 390, 375 CSS pixels. Disposable database/accounts and mocked configured-AI transport; no normal athlete data or paid provider call. |
| Print regression | Four A4 PDFs passed text/margin checks: overview 2 pages, comparisons 2, nutrition 2, training 3. [Print checks](evidence/phase3/print-checks.json). New catalog/intelligence panels are intentionally not included in current-view print. |

Commands: from backend, `..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=../.qa-runtime/pytest-phase3-final`; from frontend, `npm.cmd run test`, `npm.cmd run typecheck`, `npm.cmd run typecheck:browser`, and `npm.cmd run test:browser` with the README's Phase 3 evidence variables. Ruff ran from the backend directory; Prettier covered `src`, `e2e` and `playwright.config.ts`.

The initial two-scenario smoke run passed the progression journey and stopped on an ambiguous heading selector in the substitution test; the selector was scoped to the prescription heading. An intermediate full run was interrupted after an existing test caught altered recovery wording; the original applicable wording was preserved. A later targeted run found a genuine active-tooltip contrast defect (red tooltip text on charcoal, approximately 4.27:1). The tooltip now uses high-contrast text, and the regression explicitly activates it before axe checks. [Initial smoke](evidence/phase3/smoke-initial-results.json) and [tooltip failure](evidence/phase3/tooltip-failure-results.json) are retained rather than represented as passes. The interrupted run produced no completed JSON report and is not counted as verification. An intermediate full matrix also passed 53 cases/7 intentional skips; use the final report below for current evidence.

Visual inspection of the desktop and mobile performance panels caught an overly compressed mobile set table. It now retains readable column widths inside a keyboard-focusable scroll region, without making the page wider. Recorded class slots also preserve distinct disciplines (for example, two boxing classes and one BJJ class), with a dedicated regression test. These final changes are covered by a focused cross-viewport/print run in addition to the full matrix.

Evidence: [desktop actual-set panel](evidence/phase3/desktop-1440-phase3-performance-panel.png), [mobile actual-set panel](evidence/phase3/mobile-390-phase3-performance-panel.png), [mobile recovery journey](evidence/phase3/mobile-375-phase3-recovery.png). Screenshots and generated PDFs are synthetic QA accounts. Final print renders were checked for text/margins; training page 2 and performance panels were visually inspected. Automated axe covers the original workspace/onboarding states and the new populated chart with an activated tooltip; it is not full WCAG certification.

## API and storage map

- `GET /api/exercise-catalog`: authenticated, versioned read-only catalog and general source URLs.
- `GET /api/training-intelligence`: athletic evidence, current-cycle recovery/progression decisions and all-cycle actual workout history.
- `POST /api/training-sessions`: validated richer actual performance, optional effort, completion date and outcome. New UI sends the active plan ID; mismatched IDs are rejected. Legacy clients can still omit it for compatibility.
- `POST /api/reassessments` with `{ "week": 4 | 8 | 12 }`: immutable source-bound report; omitted body retains the week-4 default for older clients.
- `POST /api/reassessments/{id}/proposal`: validated future-only preview; week 12 has no future weeks to modify.
- `POST /api/training-plans/substitution-preview`: validated alternative proposal; historical checkpoint or already logged sessions cannot be rewritten.
- Existing `/api/revisions/{id}/approve|reject`, history and export endpoints preserve the approval boundary and account isolation.

Versioned JSON aggregates retain input snapshots and actual logs. Profile fields are not overwritten by recommendations. Pending proposals become stale when their supporting profile/check-in/base plan/workout set changes. Previously saved prescriptions remain in history/export even when the active schedule is withheld for safety or changed inputs.

## Remaining work

- Qualified MMA/strength-and-conditioning review of technique cues, exercise variants, volume, rest and progression choices; clinical review of limitation handling. More catalog entries alone do not establish program effectiveness.
- A dated external-class calendar and exact outside workload, coach-approved technical competencies, mobility protocols, and advanced competition peaking.
- Workout correction history and richer protocol filters for cross-cycle performance comparisons; production-scale history pagination.
- A complete next-cycle planning workflow after week 12, with expert-guided goals, and consolidated athletic-performance reports.
- Optional device integrations and independently verified testing; no fabricated measurements should fill these gaps.
