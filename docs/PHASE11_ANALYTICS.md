# Phase 11 — athlete analytics verification

Implemented 2026-10-31, exclusively inside `mma-performance-coach/`. Existing athlete JSON records, approved plans and workout history are preserved. Normal athlete databases were not migrated or replaced during QA.

## Delivered behavior

| Area | Implementation and evidence |
| --- | --- |
| Longitudinal dashboard | Progress now has an inclusive date-filtered development dashboard, current profile summary, measured window baseline/current values, daily charts and accessible tables. Empty histories produce no invented baseline. |
| Performance | Comparable benchmark and completed-set series cover loads, repetitions, timed/distance conditioning, jumps and same-day body-mass ratios. Different repetition/effort/evidence protocols stay separate. Actual observations, self-reports and estimates are labeled. No estimated 1RM or professional proficiency is generated. |
| Personal records | Selected-window records use supported comparable performances; failed workouts do not create set records. Fixed-distance times favor lower values; duration-only endurance favors longer values. These are window records, not an unsupported lifetime claim. |
| Workload and recovery | Weekly actual minutes, completed/failed/missed sessions and session-RPE × minutes load are shown with missing-RPE and partial-week qualifications. Weight, sleep, fatigue, soreness and readiness use actual check-ins. |
| Adherence | An explicit Monday cycle start is saved separately from approved prescriptions. Only due session identifiers from the active plan lineage enter the denominator. Missing logs do not prove nonattendance. Without a calendar anchor or with truncated coverage, attendance percentages are withheld. |
| Martial arts | Optional actual discipline/minutes logging and self-reported dated technical achievements. Prescribed practice and profile experience are not treated as completed attendance. Backend accepts multiple disciplines; the workout form currently captures one per log. |
| Interpretation | Deterministic observations require at least three dates spanning 14 days for directional trends; unchanged observations need 28 days. Sparse samples are qualified. No causation or medical diagnosis is inferred. |
| Reassessment | Latest three saved checkpoint findings and review priorities are included. Existing week 4/8/12 reassessment and explicit approval remain the mechanism for plan changes; analytics never revises an approved plan. |
| Reports | Downloadable bounded JSON development report, streamed source CSV, and print-friendly development view include profile, history, performance, adherence, martial participation, available current nutrition targets and saved checkpoint findings. Stale nutrition numbers are withheld using existing validity rules. |
| Ownership | All analytics, history, schedule, achievement and export requests are authenticated and scoped to the current account. CSV omits account identity and raw notes, and escapes spreadsheet formula prefixes. |

## Implementation and integrity

`backend/app/analytics.py` implements calculations and reporting. `history_index.py` maintains indexed date/parent metadata on new or corrected records; `db.py`, migration `0007_history_metadata.py` and `repository.py` support bounded retrieval. `main.py` exposes the endpoints. `AthleteAnalytics.tsx` integrates them into Progress; Training captures actual discipline participation. A refresh counter prevents stale analytics when capped recent-history arrays retain the same length.

Migration **0007 is required before running an existing database**. From `backend/`:

```powershell
..\.venv\Scripts\python.exe -m alembic upgrade head
```

The migration backfills nullable event dates and parent references, adds composite history/lineage indexes and leaves payload JSON intact. Roundtrip tests verify payload preservation. Workout records lacking an explicit completion date use their recorded creation date; this is a historical fallback, not a measured completion timestamp. Corrected/deleted source rows are reflected on fresh queries without a stale materialized summary. No destructive correction UI was added.

The app initially loads only 100 recent check-ins/workouts. Analytics uses indexed account/kind/date filters and a 2,000-event summary cap, 60 displayed series, 120 chart points per series and 64 referenced source plans. Coverage is disclosed; narrow the interval for complete summary comparisons. Latest three reassessments are snapshots. CSV keyset-pages 100 source records at a time through the entire selected interval, independently of the summary cap. History views use count plus SQL pagination. Dates default to 90 days and support up to 3,651 inclusive days. Existing legacy API calls without a limit retain backward compatibility; full account JSON export still materializes history.

The 2,100-check-in fixture checks bounded results, history-index use and fewer than 16 summary SQL statements. This is local regression evidence, not production-scale performance certification. Referenced plan payloads remain whole JSON documents; profiles with more than 64 source plans can lose lineage deduplication coverage and should use narrower intervals.

## Verification

Baseline: **278 backend / 12 frontend tests passed** before implementation. Final backend: **286 passed**, including eight new regression tests. Frontend: **12 passed**. One existing Starlette/httpx deprecation warning remains. TypeScript, production Vite build, Ruff lint/format and frontend Prettier passed.

`backend/tests/test_phase11.py` covers empty/single/repeated measurements, trend thresholds, units/date ranges, measured-versus-estimated protocols, same-day ratios, source correction/deletion, actual set records, martial participation, calendar adherence, plan preservation, private exports, pagination, long histories and migration preservation. Existing tests retain reassessment approval, access control and plan versioning coverage.

Browser results and print evidence are recorded in `docs/evidence/phase11/`; final counts are recorded below. Edge runs against a disposable QA database, not athlete data. Initial new browser run found five failures from identical accessible region names on the scrollable tables; distinct labels fix the root cause. Empty-state tests passed in that run. The first focused backend run also exposed an incorrect test assumption about sustained-weight staleness; the fixture was corrected to include three recent check-ins over 21 days, matching existing validity rules.

## Interpretation limitations and coach review

- Records describe the selected period and available logs. No missing history, technical mastery, attendance or baseline is fabricated.
- Benchmarks depend on consistent testing protocols, effort and accurate user entry. Same-day load/body-mass ratios are simple descriptive ratios, not validated strength classifications.
- Session-RPE load is an optional subjective workload indicator, not a diagnosis or proof that workload caused performance changes. Missing complete weeks are not silently converted to zero workload.
- Jump height is not a direct power measurement. Sprint, endurance and strength values are not comparisons with professional fighters.
- A qualified coach should review test protocols, fatigue-related workload changes, plateau interpretation, technique milestones and return-to-training decisions. Injury or medical concerns require an appropriate qualified professional.
- No independent sports-science or clinical review, live AI validation, multi-browser certification or production-scale load validation is claimed.


## Browser execution audit

Final fresh focused verification: **43 passed, zero failed, seven intentional skips**, with no flaky results, in [final-browser-results.json](evidence/phase11/final-browser-results.json). This run covers all three Phase 11 scenarios, the full athlete journey, configured-provider UI with mocked transport, loading/error states, modal accessibility, mobile navigation and print exports. All **15 Phase 11 cases passed** across 1440, 1920, 768, 390 and 375 px. Five targeted analytics axe scans returned zero violations. Skips are desktop-only mobile-drawer tests (three) and duplicate fixed-paper print runs (four).

Final screenshots: [desktop](evidence/phase11/desktop-1440-phase11-development.png), [tablet](evidence/phase11/tablet-768-phase11-development.png), [mobile](evidence/phase11/mobile-375-phase11-development.png). Additional widths and empty states are in the same directory. [Development PDF](evidence/phase11/progress-a4.pdf), [print checks](evidence/phase11/print-checks.json).

| Final checklist | Result |
| --- | --- |
| Actual baselines and comparable records | Passed backend and browser fixtures; no synthetic history |
| Date filters, pagination, calendar save, CSV/JSON downloads | Passed at all five widths |
| Saved plans unchanged by analytics actions | Passed backend and browser checks |
| Private exports and account isolation | Passed backend checks |
| Corrections/deletions and long histories | Passed backend fixtures; no normal athlete data touched |
| Responsive layout and targeted accessibility | No document overflow or targeted axe violations in executed checks |
| Print output | Five PDFs, 18 pages; safe-margin/text checks passed; development pages visually inspected |
| Build and static checks | App/browser TypeScript, Vite, Ruff and Prettier passed |
| Outstanding deployment step | Upgrade existing database to schema 0007 before starting the new code |

The complete cross-phase Edge run recorded **132 passed, one failed, seven intentional skips** in `evidence/phase11/browser-results.json`. Its sole failure was a strict test selector matching the same recovery explanation in both the new summary and existing reassessment panel. The assertion now targets the reassessment panel. All five viewport runs of the responsive workspace/axe test passed.

An intermediate focused run was interrupted after two mobile fixture timeouts: its fixture reloaded the page and attempted navigation before session restoration completed. The fixture now explicitly waits for the loaded overview. This was a test readiness issue; it is not counted as a successful browser run.

Print inspection found a premature loading-state capture and duplicate quick panels spilling a row to another page. The test now waits for three real fixture observations; print CSS includes the bounded development report once and keeps its cards together when possible. Five final A4 PDFs total **18 pages**, with no blank pages or text outside the checked safe margins. All four development-report pages were visually reviewed; charts, units, records, limitations and history remain readable. The report spans four pages and can use more paper for longer tables; full raw histories belong in CSV.
