# Delivery status · 2026-10-31

**Current delivery: Phase 15.** [Delivery report and actual evidence](PHASE15_DELIVERY.md), [updated feature matrix](PHASE15_FEATURE_MATRIX.md).344backend tests/12frontend tests passed. Source-backed catalogs now19fighters/55foods/49exercises; normalization, allergy validation, macro-balanced food replacement, exercise filtering and competition-context review are integrated. No athlete database reset/migration or tracker change. Public release gates remain open.


**Current release: Phase14 - verified local release candidate (category B).** [Acceptance report, feature matrix, evidence and launch gates](PHASE14_ACCEPTANCE.md). 328 backend / 12 frontend tests passed; full Edge 158 passed, 0 failed, 7 intentional skips across five widths; final focused checks 15 passed. Current schema0008. No public deployment, live AI/IdP, PostgreSQL runtime or independent professional approval. Earlier phase statements below are historical snapshots.


**Latest delivery: Phase 13 (2026-10-31).** [Infrastructure/security report](PHASE13_INFRASTRUCTURE.md). **328 backend / 12 frontend tests passed; final focused Edge25 passed, zero failed/skipped.** Signed-token OIDC mocks, account linking/session controls, atomic global AI budgets, migration0008 preservation and a disposable SQLite backup/restore rehearsal passed. PostgreSQL/Docker/native tools are unavailable; no live IdP, proxy/TLS, container or public deployment was verified. Production readiness remains blocked on the explicit external gates. Normal athlete data and original tracker remain unchanged.

**Latest delivery: Phase 12 (2026-10-31).** [Full safety report and expert review packs](PHASE12_SAFETY.md). **308 backend / 12 frontend tests passed**. Thirty-one methods inventoried, seven synthetic examples generated, four review packs prepared. Focused Edge verification: **20 passed, zero failed**, including five safety scenarios with no targeted axe violations at five viewport sizes. Independent expert approval remains pending; no actual expert feedback was supplied or invented. Schema remains 0007 and approved plan/history data is preserved.

**Latest delivery: Phase 11 (2026-10-31).** [Analytics methodology, verification and limitations](PHASE11_ANALYTICS.md). Added date-filtered measured trends, comparable window records, weekly workload, explicit calendar adherence, actual martial arts minutes, technical achievements, indexed/paginated history and private CSV/JSON/print reporting. **286 backend / 12 frontend tests passed**. Migration **0007** is required for existing databases; QA used disposable databases and preserved normal athlete data and the original tracker. Final focused Edge: **43 passed, zero failed, seven intentional skips**, including all 15 Phase 11 cases at five widths. Five A4 reports (18 pages) passed print checks. The prior full run had one ambiguous test selector failure, corrected and reverified in the focused run; details and limitations are recorded in the linked report.

**Phase 10 (2026-10-31).** [Full coach report](PHASE10_COACH.md): current bounded context, deterministic offline explanations, typed controlled actions, canonical request permission checks, retained approval/version history and 18 mocked evaluation scenarios. **278 backend / 12 frontend tests passed**. Full Edge: **123 passed, seven intentional skips**; final coach/journey confirmation after chat scrolling improvements: **35 passed** across five viewports. TypeScript, Vite, Ruff, Prettier and four A4 reports passed. No live AI quality, professional approval or new production-runtime validation is claimed. Existing data and schema head 0006 are preserved.

**Latest: Phase 9 (2026-10-31).** See [nutrition implementation, provenance, QA and limitations](PHASE9_NUTRITION.md). Forty source-backed USDA foods replace the 22-food subset; daily mineral/fiber totals, chosen food substitutions, assembly/meal-count preferences and day-specific training explanations integrate with retained approval/version history. Old targets require reviewed regeneration under catalog v2; normal athlete data is preserved. Full recipe-level cooking, monetary budgets, complete micronutrient adequacy and individualized workload-based calorie cycling remain outside coverage.

Phase 9 validation: **251 backend / 12 frontend tests passed**. Real Edge full report: **113 passed, zero failed, seven intentional skips** at 1440/1920/768/390/375 px. Four A4 reports (14 pages) passed text/margin checks. Ruff, Prettier, app/browser TypeScript and Vite passed. The report discloses the initial fixture failure and inconsistent redirected PowerShell wrapper exit, with corrected full and focused browser evidence.

The app is isolated in `mma-performance-coach/`. The original tracker source, configuration and data are unchanged.

**Phase 1 update:** Real-browser QA is now complete for the requested Edge viewport matrix. See [the comprehensive QA report and evidence](PHASE1_QA.md). The previous browser-access blocker is superseded by direct Playwright execution.

## Verified

| Check | Result |
| --- | --- |
| Backend Pytest | **45 passed** |
| Frontend Vitest / React Testing Library | **8 passed** |
| Playwright / installed Edge | **38 passed, 7 intentional skips** across 1440/1920/768/390/375 widths |
| Automated axe accessibility | Zero targeted violations in 40 workspace and five assessment-dialog scans |
| A4 print reports | Four reports rendered and inspected; text/margin checks passed |
| TypeScript project check | Passed |
| Vite production build | Passed; lazy analytics bundles, no oversized-chunk warning |
| Backend Ruff lint | Passed |
| Backend Ruff formatting | Passed, 15 files |
| Frontend Prettier | Formatted; final check recorded during handoff |
| npm dependency audit | **0 vulnerabilities** after updating test tooling |
| Alembic | Fresh upgrade → downgrade → upgrade and table inspection passed |
| Running HTTP server | Production HTML and referenced assets, API docs, persisted demo profile, training, nutrition, matches, local coaching, export and account deletion passed |

Tested runtime: Windows, Python **3.14.7**, Node **24.20.0**. Compatible minimum versions are documented, but other OS/Python/PostgreSQL combinations were not exercised. Exact frontend versions are in `package-lock.json`; backend versions are in `requirements.lock.txt`.

The backend test client emits one upstream Starlette deprecation warning about its HTTPX transport. All tests pass. No paid AI requests are made by the tests. AI success, reduced-context payload, unavailable provider behavior and schema validation are exercised using mocked responses.

## Verification limits

The initial delivery's browser connector was unavailable. Phase 1 subsequently exercised the real application using Playwright and installed headless Microsoft Edge 155.0.4283.45. Desktop, tablet/mobile viewport emulation, workflows, keyboard behavior, screenshots and A4 PDF output are now verified within that environment. Physical devices, Safari/Firefox, manual screen-reader use, printer drivers and real paid AI behavior remain unverified. Automated axe results are not full WCAG certification.

OpenAI is optional and not configured in the delivered local environment. Actual model availability, key permissions and paid response quality require a user-provided server-side key. Live ingestion/licensed fighter redistribution, production authentication and database deployment are not represented as complete.

## Working scope and known limits

All eight main navigation modules have functioning backend interactions. No fabricated progress history or invented fight statistics are shown. The demo has intentionally empty training and check-in history. Nutrition is withheld after relevant profile changes, preventing stale allergy/clinical inputs from being presented as usable meals. Plan revisions require explicit approval and retain original inputs.

This first local version uses compact versioned aggregate storage and conservative program templates. It does not fulfill every production expansion in the original brief: inclusive licensed fighter coverage, independently verified athletic testing, a comprehensive exercise/food catalog, per-exercise performance logging, automated reminders, advanced sport-specific periodization, sports macro optimization, comprehensive cultural/budget meal customization and arbitrary natural-language plan editing need further development and expert review. Existing source snapshots and heuristics are explicitly labeled.

## Recommended next work

1. Extend the passing Edge viewport matrix to physical devices, other browser engines and manual assistive-technology review.
2. Review programming and nutrition with qualified MMA coaches and sports dietitians.
3. Obtain licensed fighter/nutrition feeds and expand inclusive source coverage.
4. Add production identity, rate limiting, retention controls and PostgreSQL deployment tests.
5. Expand catalogs, per-exercise logs, dietary optimization and supervised AI action proposals.


## Phase 2 audit update

The original-specification feature matrix, resolved integrity defects, module statuses and Phase 3 priorities are in [PHASE2_AUDIT.md](PHASE2_AUDIT.md). Read it as the current completion assessment; the initial-delivery limitations above describe the earlier baseline. Actual-set logging now has frontend/API integration; reassessment can create an explicitly approved proposal; program schedules have a read-only history view.

Run Alembic through revision **0003** before starting an existing database. Existing records remain in place. Source-bound proposals reject later profile/recovery edits, and unsafe/stale active training is withheld rather than silently replaced. Tests use disposable accounts/databases; the normal local athlete database and original tracker were not migrated or modified during QA.

Phase 2 validation: **55 backend tests, 8 frontend tests, 43 browser cases passed with 7 intentional viewport skips**; app/browser TypeScript, Vite, Ruff and Prettier passed. Four A4 reports passed text/margin checks. Current results and failed-initial-run disclosure are linked in the audit report. Real paid AI, PostgreSQL, physical devices and production deployment remain unverified.


## Phase 3 delivery

Current training delivery is documented in [PHASE3_TRAINING.md](PHASE3_TRAINING.md): 37 structured catalog entries, catalog-linked prescriptions, richer actual-set logging/history, measured-versus-estimated assessment, goal/access/enjoyment-aware discipline priorities, fatigue-aware holds/reductions, evidence-gated progression and future-only approved reassessment/substitution versions.

Phase 3 supersedes the earlier training-template and per-exercise-log limitations. It remains an informational local system, not clinically validated individualized or advanced competition programming. No extra migration beyond `0003` is needed; existing plans/data are retained. Contact training and injury-sensitive programming require qualified coaches. Exact current tests, browser evidence and unresolved limits are in the Phase 3 report.

Phase 3 verification: **115 backend tests, 8 frontend tests and 53 full-matrix Edge cases passed** (7 intentional viewport-specific skips). Ruff, Prettier, app/browser TypeScript and Vite passed. Four A4 PDF reports passed text/margin checks. See the Phase 3 report for the final focused checks, screenshots, intermediate failure disclosures and explicit scientific/operational limits.

The final focused cross-viewport/print rerun passed **11 cases with 4 intentional print-project skips**, including the readable history table and distinct class allocation. Final full and focused machine-readable reports and screenshots are linked in `PHASE3_TRAINING.md`.


## Phase 4 fighter comparison delivery

[Phase 4 audit, feature status, source boundaries and QA evidence](PHASE4_COMPARISON.md) supersede the earlier three-fighter comparison limitation. The local bundle now contains 11 reviewed snapshots (seven men, four women), field-level provenance, separate current/history divisions and career status, and sparse dated historical statistics. Current stance and shared style traits remain unavailable rather than inferred.

The deterministic resemblance engine includes configurable physical subweights and optional reach/height ratio, separate coverage, missing/stale handling, full-precision ordering and component explanations. Manual selections outside the top three receive a real breakdown and can be saved. Favorites retain profile/fighter/reference/algorithm snapshots and load the original athlete measurements; re-evaluation is explicit. The lab has source/quality tables, charts, filters, responsive controls and an explicit reviewed-data refresh.

Run Alembic through **0004** before starting an existing database. Startup preserves existing snapshots; the lab's local refresh explicitly imports reviewed versions, archives old/new public-data payloads and does not perform fresh web verification or advance dates. The optional licensed JSON-file adapter requires operator settings and matching source license references; no commercial feed or redistribution agreement is bundled. The normal local athlete database and original tracker were not modified during QA.

Phase 4 validation: **132 backend tests**, **eight frontend tests**, and **63 full-matrix Edge cases passed** with seven intentional viewport-specific skips. Alembic upgrade/downgrade/re-upgrade, legacy payload preservation, no-schema-difference check, Ruff, Prettier, app/browser TypeScript and Vite passed. The linked report records the final focused cross-viewport snapshot/error/print checks and earlier failures honestly. Four A4 reports have rendered evidence and margin/text checks.

Coverage remains explicitly limited: 11 indexed official-source study snapshots, no comprehensive/current roster, no current fighter records, no inferred professional skill and no live licensed-provider verification. Direct profile requests returned 403; the source register identifies indexed-excerpt review. Production refresh authorization, licensed coverage, expert review of heuristics, other browser engines/devices and manual assistive-technology testing remain next work.

Final Phase 4 focused Edge checks: **11 passed, four intentional print-project skips**, including actual saved-profile versus updated-profile rendering, explicit unscored favorites, error/retry behavior, expanded-source accessibility and corrected print contrast.


## Phase 5 nutrition and coaching delivery

[Phase 5 status, API contracts, sources and QA](PHASE5_NUTRITION_COACH.md) supersede the original illustrative-food and generic-chat limitations. The bundled 22-ingredient USDA CC0 subset has per-record provenance, units and separate source/macro-derived energy. Nutrition calculations, exclusions, composition, validation and explanations are separate. Seven-day macro-guided meals include bounded portions, optional snacks, substitutions and groceries, with structured dietary/availability/dislike/budget/pattern feedback.

Nutrition and coaching changes have explicit preview/approve/reject workflows. Approvals revalidate source IDs and exact candidate data in serialized transactions; previous versions, workout lineage and profile inputs remain intact. Local and structured-provider interpretations can propose supported training or meal changes, with useful errors/clarification for unavailable context. AI cannot write plans directly. Relevant approved workload/input changes and sustained check-in trends create review needs without automatically replanning for minor fluctuations. Reassessment exposes nutrition status.

Backend verification: **177 tests passed**, with an existing Starlette/httpx deprecation and a non-fatal pytest cache-write warning on the final rerun. Frontend **nine tests passed**; app/browser TypeScript, Vite, Ruff and Prettier passed. Final Edge matrix: **78 passed, zero failed, seven intentional viewport-specific skips**, across 1440, 1920, 768, 390 and 375 px. All 16 new nutrition/coaching browser cases passed; automated accessibility, requested-width overflow and four printed reports (12 pages) passed. Screenshots, print renders and intermediate failures are recorded in the Phase 5 report. Paid provider transport is mocked in QA; no paid call, production deployment or real device verification is claimed.

No schema migration beyond `0004` is required. The normal MMA database and original tracker were untouched during QA. Existing nutrition history remains stored; legacy illustrative current plans are withheld until explicit reviewed generation. Remaining boundaries include limited generic food coverage, no complete micronutrient/palatability optimizer, no product/cross-contact certification or real-price guarantees, heuristic energy adjustments, and unverified live AI/production quotas. Qualified dietitian/medical and MMA coaching review remains necessary for clinical or competition-specific requirements.


## Phase 6 release candidate

[Final structured release assessment](PHASE6_RELEASE.md) supersedes earlier session/rate/deployment limitations where implemented, while retaining explicit unverified gates. Phase 6 adds migration **0005**, independent expiring/revocable sessions, production HTTPS/origin/host/cookie/header validation, shared DB quotas, per-account AI daily attempt limits, bounded write bodies, safe DB failures, readiness, SQLite FK enforcement, explicit retention, a PostgreSQL driver and disposable integration tooling. Workout modals cannot retain a prior prescription through approved-plan refresh; expired sessions return to recovery. Indexed latest-version lookup removes full-history deserialization.

**187 backend tests and ten frontend tests passed.** App/browser TypeScript, Vite, Ruff, formatting, pip check and both dependency advisory audits passed; no known vulnerabilities were returned. SQLite migration round trip/schema checks and PostgreSQL offline SQL compile passed. Final full Edge matrix: **88 passed, zero failed, seven intentional skips** across five widths. Four A4 reports (12 pages) passed text/margin checks; screenshots/renders and the initial three training-race failures are recorded in the linked report. No real paid AI or public deployment was exercised.

**Local release candidate; public production remains gated.** PostgreSQL runtime, deployed TLS/proxy/host behavior, actual backup restoration, managed-identity suitability, production operations/cost governance and independent specialist/manual device review remain unverified. See [deployment](DEPLOYMENT.md), [security](SECURITY.md) and [specialist checklist](SPECIALIST_REVIEW.md). The original tracker and normal athlete database were not modified by QA.


## Phase 7 training delivery

[Phase 7 full report](PHASE7_TRAINING.md) records baseline, deterministic versus template/AI boundaries, ten separate development dimensions, independent seven-discipline goals/stages, a 39-entry catalog, exact optional weekdays, supervised explosive/controlled interval gates, fatigue/plateau/stale-performance holds and preservation of approved future prescriptions. New session objectives, recovery notes, development details and fatigue logging are integrated in the existing UI. Approvals, version history and original profile inputs remain protected.

Baseline **187 backend / ten frontend tests passed**. Current backend **221 passed**, with one existing Starlette/httpx deprecation; frontend **11 passed**. Lint/format/type/build passed. Full Edge matrix: **98 passed, zero failed, seven intentional skips**, including all ten new Phase 7 cases across five widths. Four printed reports (12 pages) passed text/margin checks. Screenshots, actual intermediate failures and final evidence are in the linked report. No paid AI or personal database was used. No migration beyond `0005` is required.

Anaerobic capacity, coaching competence and injury suitability are not inferred. Class dates/durations remain unknown, stage/plateau/load thresholds are heuristics, and competition/injury/clinical needs require specialists. Qualified-review decisions are listed explicitly. Phase 6 PostgreSQL/production/backup/manual-device/security review gates remain open; no public production readiness is claimed.


## Phase 8 fighter system delivery

[Phase 8 complete report](PHASE8_FIGHTERS.md) records actual coverage: **17 source-snapshot records (10 men, seven women)**, including six attributed secondary-source additions under CC BY-SA 4.0. Historical records span all eight men's active reference divisions and all three women's active reference divisions; no complete/current roster is claimed. Original 11 redistribution rights remain unestablished.

Migration **0006** adds normalized query metadata, duplicate-identity protection and reversible operator import batches, preserving athlete records/frozen favorites. Server pagination and filters replace whole-library downloads in the lab. Matching v3 gives partial physical evidence only its supported group contribution, normalizes weights exactly, retains deterministic ties and exposes sparse evidence. Offline preview/apply/conflict/rollback checks and source/license boundaries are documented.

Baseline **221 backend / 11 frontend** tests passed; current **239 backend / 12 frontend** passed. Full Edge matrix: **108 passed, zero failed, seven intentional skips** across five widths, including all ten new Phase 8 cases. Four A4 reports (13 pages) passed text/margin checks. Query benchmark, migration, source-quality and screenshot evidence is linked in the report. No public scraper, paid provider or normal personal-data migration/deletion was used for QA. Real PostgreSQL, live provider rights/quality, public-deployment/backup gates and independent domain review remain unverified.


## Phase 10 controlled coaching delivery

[Phase 10 report](PHASE10_COACH.md) describes bounded athlete context, deterministic offline explanations, request-permission gating, new reschedule/frequency/assessment/progression proposals, retained exercise/meal actions, explicit persistence confirmation and an 18-scenario mocked evaluation set. Existing data and approved-plan lineage remain intact; schema head stays 0006. No paid/live model calls or public deployment were performed. Actual tests and browser evidence are recorded in the report; model semantics, unsupported paraphrases and independent specialist/security review remain limitations.
