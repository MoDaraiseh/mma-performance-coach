# Phase 7 — individual development and MMA programming

Review date: **2026-10-31**. All implementation and evidence remain within `mma-performance-coach/`. The original tracker and normal athlete database were not modified for QA. No live paid AI call or public deployment occurred. This is an informational local release candidate, **not independently validated sports-science or clinical programming**.

## Baseline and implementation audit

Before edits, **187 backend tests and ten frontend tests passed**. Reviewed Phase 6 release/security/architecture notes, strict schemas, exercise catalog, athletic/style services, planner, progression, plan integrity, approvals, logging and their UI/tests. Existing features were extended, not rebuilt. Schema head remains **0005**: additional profile/log fields live in existing versioned JSON aggregates and have defaults for older profiles.

| Recommendation | Existing basis | Phase 7 basis / boundary |
| --- | --- | --- |
| Absolute/relative strength | Recorded external load and load/body-mass ratio | Separate development dimensions; original repetitions/evidence labels retained; no 1RM or professional strength rating |
| Aerobic assessment | Entered run duration converted to pace | Recorded result remains distinct from expenditure/VO2max estimates; no MMA-specific capacity inference |
| Anaerobic assessment | No validated repeated-effort protocol | Explicit missing objective-data dimension; sprint time or interval completion does not become an anaerobic capacity score |
| Explosive assessment | Entered jump distance/height | Observation or estimate kept separate; no inferred power output |
| Technical priorities | Interest/preference/coaching/access/gaps/enjoyment heuristic | Seven independent discipline histories plus goals, evidence gaps and acquisition/consolidation/refinement; no body-measurement input to proficiency |
| Weekly plan | Timed catalog template, day-count slots, weeks 4/8/12 deload | Template v4 also respects selected weekdays, caps low-training beginners, gates optional supervised explosive practice and a single controlled interval block, keeps recovery days visible |
| Progression | Two comparable completed exposures, effort/recovery gates | Same basis plus recent session fatigue, 28-day performance freshness, possible-plateau hold and preservation of compatible approved exercises |
| AI | Optional explanation/whitelisted intent | Unchanged: no LLM-generated physiological score, nutrient value, exercise prescription or automatic plan mutation |

Numerical ratios, pace, minutes and version/source checks are deterministic calculations. Domain grouping, technical stages, workload caps, timing, deloads and progression thresholds are **explicit product heuristics/templates**, not validated individualized prediction models. Optional AI interprets bounded requests; deterministic services validate previews and existing approval persists changes.

## Delivered athlete development model

`athletics.athletic_assessment` now exposes `development` through `GET /api/training-intelligence`:

1. General strength: original external loads and repetitions.
2. Relative strength: load divided by accompanying recorded body mass, never an inferred 1RM.
3. Aerobic conditioning: comparable entered run results/pace.
4. Anaerobic conditioning: missing objective protocol, explicitly unscored.
5. Explosive performance: jump results, with estimated inputs excluded from observed evidence.
6. Mobility: self-assessed context; unknown remains missing.
7. Training experience: reported gym years/current frequency.
8. Technical martial arts experience: independent self-reported discipline histories.
9. Recovery/fatigue: reported sleep/check-in context; not physiological capacity.
10. Availability: reported day/time cap and selected weekdays or visible template assumption.

Each dimension carries evidence/status/limits. No composite athlete score, professional percentile or optimal fighting style is generated. Estimated benchmark inputs remain in their own existing list. A fallback bug was corrected: when a check-in contained no benchmarks, using profile benchmarks previously discarded the check-in's mobility/recovery context. The assessment now preserves that context while using the profile body mass for the original profile benchmark ratio.

## Independent technical development

Boxing, Muay Thai, Kickboxing, BJJ, Wrestling, Judo and MMA each show entered/missing experience, months, weekly frequency, self-reported proficiency, technical goals, access and a stated development reason. Existing strength/gap/enjoyment fields remain. New `Experience.technical_goals` is optional, bounded to 300 characters and editable in onboarding/profile step 3.

Stages are coaching-allocation heuristics: under 12 months or a None/Beginner/Novice self-report retains fundamental acquisition; at least 36 months plus Advanced/Competitive self-report and recorded instructor/gym access permits **coach-led refinement**; other recorded histories use consolidation. Missing histories are unknown rather than assumed beginner. These conditions never verify proficiency. Technical complexity no longer advances merely because the calendar reaches week 5 or 9; instructors observe and decide progression.

Kickboxing and Judo now have distinct catalog entries (catalog total **39**), with non-contact combinations/defensive exits and instructor-selected balance/breakfall preparation respectively. Judo requires recorded mats and instruction; no unsupervised throws or submissions. Other grappling/transition drills retain equipment/coaching gates. Missing access falls back to comfortable solo footwork. No hard sparring prescription exists.

Useful directions explain striking fundamentals, defensive exits, clinch positioning, takedown defense, positional grappling and striking/grappling transitions using recorded goals/gaps and access. Height/reach/weight are not inputs to technical priority or stage. The existing fighter-style view and comparison lab remain exploratory, not measures of fighting ability.

## Planner v4 and scheduling rules

New optional profile fields: `available_days`, `strength_coach`, `power_practice`. Defaults preserve old profile parsing; exact days remain unknown until entered. Selected weekdays are sorted in calendar order, capped by the requested/recovery/beginner day count and never supplemented with unavailable days. More selected days than the cap become recovery days; fewer selected days reduce the scheduled count without overwriting the requested count. At least one non-training day remains. Reported outside classes count toward the budget, but their actual dates/durations are still unknown: this is not a guaranteed timetable for every existing class.

Low-training beginners (`gym_years < 1` and current frequency under 3) have at most four planned days, still within existing short timed sessions. Poor sleep/recovery concerns, youth and Gentle preference retain the three-day cautious cap. One/two-day plans use mixed fundamentals. Higher experience does not automatically prescribe maximal loads, more weekly volume or competition-camp intensities. General strength, aerobic work, technical practice and comfortable mobility remain inside daily time blocks.

**Optional explosive practice:** explicitly requested, recorded qualified strength/conditioning coach access, age 18–64, at least one gym year, comfortable mobility, supported recovery, non-deload week and at least 12 minutes in the strength block. Four minutes are reassigned from that block, not added outside the cap. Light supervised chest passes with suitable equipment or low coached jumps use two sets of three controlled repetitions, full comfortable recovery inside the block, and immediate stopping when quality deteriorates. This is low-volume practice, not a prescribed power outcome or clearance for ballistic training.

**Optional controlled cycling intervals:** explicit existing interval-mode preference, bike, age 18–64, at least one gym year, current frequency at least three, comfortable mobility, supported recovery, no more than two reported technical sessions, non-deload week and a conditioning block of at least nine minutes. At most one dedicated conditioning session per week includes three rounds of one minute at reported RPE 7 plus two minutes easy; remaining block time stays easy. Intervals are not added to strength/power blocks, never all-out, and omitted in deloads or unsupported contexts. This is mixed-system exposure, not an anaerobic test or camp prescription. Missing suitability falls back to easy movement.

Every session exposes objective, time cap, exercises/practice, sets/repetitions or timed task, RPE, rest, technique cue, progression condition and available alternatives. The UI now displays the objective and recovery-day/availability notes. All work/rest plus ten minutes of warm-up/cool-down must fit. Weeks 4/8/12 retain reduced-duration deload/review; no calendar-only escalation of load/sets/time is introduced.

## Adaptation, logging and history

Optional bounded `WorkoutLog.fatigue` (1–10) is captured in the session form and persists/export alongside existing sets, reps, load, effort, duration/distance and notes. High fatigue (at least 7) in a performed session within seven days blocks progression even if a fresh check-in otherwise appears favorable. Missed sessions are not performed fatigue exposures. Existing missing/stale recovery gates and high-effort holds remain.

Two comparable completed exposures on separate dates with actual performance and effort are still required for suggestions. Performance older than 28 days cannot support an increase. Three comparable completed exposures on separate dates within 28 days with unchanged output produce a **possible plateau** hold and coach-review explanation; this does not diagnose stagnation or automatically add work. Existing small rep/load/time suggestions and all approval/source-binding checks remain. No missed-session catch-up workload is generated.

Reassessment still proposes only after a selected week 4/8 checkpoint; week 12 closes the cycle for coach review. Prior weeks and logged history remain intact. Compatible unchanged sessions now start from the **approved** prescription, preserving manual substitutions and reviewed loads instead of replacing them with a fresh template. Changed goals/equipment/technical constraints can justify new future prescriptions; reduced day/time availability is respected. When a hard block is no longer permitted or cannot fit, it becomes easy cycling/coordination. Strength set reduction applies only when the time budget actually shrinks. Fatigue/deload adjustments never increase intensity.

Snapshots and all prior plan versions stay recoverable through existing history/export; candidate previews require approve/reject. Logging/assessment does not mutate saved plans. No normal athlete database was migrated or deleted during QA.

## Tests and actual results

- Baseline: **187 backend**, **10 frontend** passed.
- Final backend: **221 passed**, one existing Starlette/httpx deprecation warning; [output](evidence/phase7/pytest.txt).
- Frontend: **11 passed**, including saving discipline goals, coach access and selected weekdays.
- Ruff lint/format, Prettier, app/browser TypeScript and Vite production build are checked. Full Edge matrix: **98 passed, zero failed, seven intentional viewport-specific skips** in 6.3 minutes. All ten new Phase 7 cases passed across five widths.
- New unit/API coverage includes all seven discipline stages/goals, unknown histories, ten dimensions, observation/estimate separation, anthropometric independence, benchmark fallback, novice/intermediate/advanced budgets, weekdays/recovery, power/interval exclusions, one-interval limit, deloads, recent fatigue, stale performance, plateaus, substitutions, shortened availability, version approval/history and fatigue persistence.

The new four-case focused desktop/mobile rerun [passed](evidence/phase7/browser-focused-fixed.json). The [first focused attempt](evidence/phase7/browser-focused.json) had one pass/three failures: two exact implicit-label textarea locators and one mobile navigation attempt before initial workspace readiness. Correct role-based selection and an explicit loaded-heading wait fixed those test problems; they are not represented as passing UI evidence. Desktop power/interval content already passed that first attempt.

Regression testing also caught an implementation error introduced during this phase: a set-count reduction applied to unchanged short strength blocks, preventing an existing evidence-supported load increase. Restricting that reduction to actual duration shrinkage restored the prior progression contract. A separate time-budget regression proves that reduced availability does not retain unsupported power/interval prescriptions. Earlier six day-count assertions were intentionally updated to the new four-day low-training beginner cap; timing/equipment tests still run across all requested day/time combinations.

The inspected [full Edge report](evidence/phase7/browser-results.json) records **98 passed, zero failed, seven intentional skips** and covers all prior phases plus ten new Phase 7 cases across 1440/1920/768/390/375 px. It checks real frontend/backend approval, selected weekdays, development details, fatigue logging, supervised practice, controlled intervals, overflow and automated accessibility. Screenshots include development [1440](evidence/phase7/desktop-1440-phase7-development.png), [1920](evidence/phase7/desktop-1920-phase7-development.png), [768](evidence/phase7/tablet-768-phase7-development.png), [390](evidence/phase7/mobile-390-phase7-development.png), [375](evidence/phase7/mobile-375-phase7-development.png), with interval/session evidence in the same folder. Four A4 reports (12 total pages) passed [text/margin checks](evidence/phase7/print-checks.json); interval-session and rendered-training layouts were visually inspected. Manual screen-reader or physical-device coverage is not implied.

## Decisions requiring qualified review

1. Whether a user's self-reported technical stage is accurate, which skills to prioritize and when to link skills or introduce contact.
2. Outside class integration, actual session durations and weekly load, especially experienced/competitive schedules and constrained consecutive weekdays.
3. Exercise technique, equipment/surface suitability, safe jump/throw load/height, appropriateness of power/interval exposure and age-specific programming.
4. Injury-sensitive exercise selection, pain/return-to-sport, youth/older-adult/clinical needs; reported limitations continue to withhold automated prescriptions.
5. Interpretation of fatigue, effort, possible plateaus and benchmark protocol/measurement quality; the numeric thresholds are product rules, not diagnostic tests.
6. Individual load increments, deload timing, extended absence/reacclimation and week-12 next-cycle design. No fixed periodization or percent increase guarantees adaptation or injury prevention.
7. Medical/competition-specific fueling and weight-class preparation remain dietitian/medical decisions; Phase 7 changes no nutrition equations or fighter data.

Use the existing [specialist review checklist](SPECIALIST_REVIEW.md), now supplemented by these phase-specific decisions. No qualified specialist signed off this delivery.

## Sources and limitations

The 2026 [ACSM healthy-adult resistance-training position stand](https://pmc.ncbi.nlm.nih.gov/articles/PMC12965823/) supports individualized progressive resistance/power principles; it does not validate this MMA template, prescribe these gates or cover youth/clinical clearance. The [IOC load consensus](https://pubmed.ncbi.nlm.nih.gov/27535989/) supports individualized load monitoring with contextual/subjective information; this application does not calculate an injury-risk ratio or infer a safe load from a universal percentage. Exercise teaching cues and technical drills are editorial suggestions requiring observed coaching.

Remaining limits: no validated anaerobic/repeated-effort assessment; no professional norms/composite skill score; no dated club-class calendar or fully optimized concurrent-training schedule; no competition camp, maximal testing, hard sparring, injury rehabilitation or guaranteed adaptation. Technique stages, plateau/recovery windows and prescription caps need independent expert validation. Exact weekdays cannot guarantee adequate spacing when the user's only days are consecutive; review with a coach. Other browser engines, physical devices, manual assistive-technology, paid AI, real PostgreSQL and deployment/backup gates from Phase 6 remain unverified.


The seven intentional skips are the mobile drawer test on three non-mobile projects and repeated print execution on four projects; print ran at desktop 1440. No retries or flaky passes were used in the final matrix. All original tracker tracked files remain unchanged.
