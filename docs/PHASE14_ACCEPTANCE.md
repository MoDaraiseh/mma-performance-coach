# Phase14 final system acceptance

Date:2026-10-31. Scope: mma-performance-coach only. Release decision: **B - verified local release candidate**. No public deployment or paid provider call occurred. The original tracker has no tracked diff; application files are untracked in the parent Git repository, so application commits/tags could not be reviewed. Personal athlete databases were not migrated, reset or used for QA.

## Audit and changes

Reviewed the React route/component structure, FastAPI route/auth boundaries, schema0008/models, deterministic assessment/training/nutrition/matching/progression/analytics services, provider context/intent checks, data catalogs, test suites and phase reports1-13. [Complete feature matrix](PHASE14_FEATURE_MATRIX.md) records implementation, status, user impact, priority, source and coverage. [31-method inventory](review/METHODOLOGY_INVENTORY.md) separates formulas from template/product heuristics and optional LLM explanations.

This phase changes QA tooling and release documentation, preserving working domain behavior. Fixed a hard-coded Phase1 accessibility-summary destination; new runs honor PW_EVIDENCE_DIR. The initial full run may have overwritten legacy Phase1 summaries before the fix; those files are not claimed as immutable historical evidence. Extended phase-safe print/benchmark/restore evidence routing and expanded the evaluation CLI to all18 fixtures. Added actual browser load/dashboard observations and user/AI/release guides. No P0 or newly discovered P1 local workflow defect required a product rewrite. Remaining P1 launch gates below are material.

## Automated verification

| Check | Actual result / scope |
| --- | --- |
| Backend |328 passed,2 upstream deprecation warnings,67.54 seconds |
| Frontend Vitest |12 passed across4 files |
| App TypeScript / Vite |Passed through browser command production build |
| Browser TypeScript |Passed, including new release timing test |
| Ruff lint/format |Passed;74 files formatted |
| Prettier |Passed after formatting the new timing test |
| pip check |No broken requirements |
| npm advisory audit |0 known vulnerabilities;180 total dependency entries in audit metadata |
| Python advisory audit |38 pinned packages;0 known vulnerabilities |
| Migrations |Disposable SQLite upgrade/check/down/up and pre-existing hash/payload preservation passed in backend tests; currenthead0008 |
| PostgreSQL |Offline SQL compilation passed; runtime/native restore NOT RUN |
| Security |Ownership, deletion/expiry/replay, origin/host/body/config, concurrent version/quotas and proposal permission regressions included in328 |
| Backup/restore |Synthetic SQLite fixture passed;2 versioned synthetic payloads preserved; source unchanged; restored sessions invalidated |
| Offline evaluation |18 scenarios executed; zero provider attempts; smoke output requires human quality review |
| Configured AI |Mocked structured-success/error/schema/retry/deadline/quota/context/security cases passed; no live-model evaluation |

[Advisory evidence](evidence/phase14/npm-audit.json), [Python audit](evidence/phase14/python-audit.json), [restore](evidence/phase14/backup-restore.json), [offline coach](evidence/phase14/offline-coach.json), [runtime availability](evidence/phase14/runtime.json). Audits initially hit restricted cache/network access; reruns with authorized access succeeded. An initial npm output path was missing; it was created and the actual audit rerun. No failed lookup was counted as clean. Warnings are Starlette/Authlib httpx compatibility deprecations, not suppressed failures.

## Browser acceptance and UX

Installed Edge/Blink on Windows, isolated HTTP API and synthetic accounts, five widths1440/1920/768/390/375 CSS pixels. No physical device or other engine was available in the installed browser inventory (only Chromium-family runtimes). Real IdP pages are mocked; live SSO is unverified. Browser totals are recorded in the final evidence summary below.

The suite exercises all eight main workspace views plus Settings, chart data tables, keyboard navigation, focus restoration/trapping, Escape, reduced motion, onboarding validation, responsive drawer/touch targets, document overflow, loading/error/retry states, permissions, session expiry/deletion, stale proposals and persisted approval/rejection. Forty core-view axe scans plus targeted dialog/phase scans check WCAG2 A/AA/2.1 AA rules; absence of automated violations is not full accessibility conformance or manual screen-reader testing. Dark charcoal/red styling and legibility were retained; no redesign was necessary.

Five fresh A4 reports total18 pages: overview2, training3, nutrition4, comparison5, progress4. All pages contain text and no detected text outside20 pt margins. Representative rendered pages were visually inspected, including charts/tables, nutrition portions and long comparison details. Long reports span pages and the progress history ends on a short final page; pagination polish is P3, not hidden clipping. PDFs and rendered page PNGs are in evidence/phase14; [print checks](evidence/phase14/print-checks.json). Print produces the current detailed view, not a complete book of every week/day.

## User acceptance mapping

Every row maps to exercised browser test source; backend tests additionally verify invalid inputs, ownership and versioning. Fixtures are realistic synthetic adults/beginners/trained users, including sparse measurements, dietary changes, fatigue and unsafe-goal cases. This is automated acceptance, not external user-study approval.

| Step | Workflow | Browser evidence source |
| --- | --- | --- |
|1|Create/access account|journey;phase6;phase13|
|2|Complete onboarding|journey;states-and-print|
|3|Enter measurements|journey;phase2|
|4|Enter martial arts experience|journey;phase7|
|5|Enter athletic performance|journey;phase3;phase7|
|6|Set availability|journey;phase7|
|7|Set dietary preferences|journey;phase9|
|8|Save profile/draft|journey;phase2|
|9|Receive assessment|journey;responsive;phase7|
|10|Review division guidance|journey;responsive|
|11|Fighting-style recommendations|responsive;phase7|
|12|Martial arts priorities|phase7;responsive|
|13|Compare sourced fighters|journey;phase4;phase8|
|14|Adjust weights|journey;phase4|
|15|Save comparisons|journey;phase4|
|16|Generate twelve-week plan|journey;phase3;phase7|
|17|Review sessions|journey;phase3|
|18|Log actual exercise sets|phase3;phase7|
|19|View progression|phase3;phase7;phase11|
|20|Nutrition generation|journey;phase5;phase9|
|21|Meal/food substitution|phase5;phase9;phase10|
|22|Track progress|journey;phase11|
|23|Reassessment|journey;phase3;phase7|
|24|Coach questions|journey;phase5;phase10|
|25|Preview modifications|phase3;phase5;phase10|
|26|Approve/reject|journey;phase5;phase10|
|27|Export reports|journey;phase6;phase11;states-and-print|
|28|Delete account|phase6|

Failures tested include invalid forms, failed saves/retry, failed/missed sessions, unavailable/stale nutrition, unsupported actions, approval conflicts, expired sessions, canceled deletion, inaccessible other-user records and unavailable provider responses. Mocked backend provider tests cover failures beyond browser UI fixtures.

## Data and recommendation findings

[Fresh local catalog validation](evidence/phase14/data-quality.json):17 fighter snapshots (10 men/7 women),40 foods,39 exercises. Historical division counts overlap: men Flyweight2/Bantamweight1/Featherweight2/Lightweight2/Welterweight2/Middleweight3/Light Heavyweight3/Heavyweight3; women Strawweight3/Flyweight5/Bantamweight3/historicalFeatherweight1. These are historical participants, not a current roster. Career labels are dated snapshots:8 Active,2 Retired,1 Not fighting,6 Unknown. Height/reach/listedweight17 each; stance2/background11/statistics2/currentprofessionalrecord0/styletraits0. Missing dimensions are excluded with reported coverage; deterministic weights/scales remain heuristic. No professional proficiency prediction is supported.

No new online fighter source verification or ingestion occurred. Source references and schema/field provenance were revalidated, not current claims of roster accuracy. Original11 records retain unresolved redistribution rights; six attributed secondary-source adaptations have CC BY-SA obligations. No access-control bypass/scraper is included. Forty USDA SR Legacy April2018 records contain macros/source energy/fiber/sodium/calcium/iron/potassium; editorial allergen/cost/diet labels are not certification. Nutrition estimates use Mifflin-St Jeor and documented conservative heuristics; no measured TDEE or clinical adequacy claim. Training progression uses actual comparable exposures and recovery gates; technical stages/fatigue thresholds/deloads are product heuristics. Analytics requires comparable protocols and sample windows; it does not fabricate historical baseline or infer causation.

## AI and security findings

Offline explanations and deterministic actions remain useful without a provider. Context is bounded/current/authorized and separates estimates/self-reports. Configured provider mocks verify schemas, malformed output, timeouts, maximum2 attempts/20 seconddeadline, canonical-request/ownership validation, no direct tools/writes, stale-state checks, approve/reject and persistence. Shared budget tests reserve2 attempts per logical request; daily6 attemptceiling accepted3 of20 parallel reservations with17 denied, using8 threads. This tests reservations, not paid provider concurrency or actual bill limits. Local default20 logical/account/day,1000 globalattempt/day,10000/month; actual pricing defaults unconfigured. External provider billing/quality/security remains unverified.

Session/account isolation, recoverable local access, signed OIDC claims through mock HTTP, replay prevention, expired/revoked session rejection, cross-account denial, export ownership and complete application-account deletion passed regression tests. Backups/exports and the external IdP account remain outside application deletion. There is no independent penetration test. Legacy recovery can bypass IdP MFA while enabled. HTTPS/proxy/remote DB security, recovery policy, encrypted backup controls and monitoring require operational validation.

## Local performance

Windows11/Python3.14.7/Node24.20.0. API benchmarks use disposable SQLite and in-process FastAPI TestClient,20 samples each; concurrent32 requests across8 threads share one synthetic account, NOT32 independent users. Fighter benchmark uses1000 syntheticrecords and10 samples; none are counted as verified fighters. Browser benchmarks use local HTTP,3 warmreloads per viewport, no network/CPU throttling and include polling. They establish no cold-load score, production capacity or SLA.

| Operation | Measured result |
| --- | --- |
|Indexed latest /1000 versions|median0.55 ms,p950.77 ms|
|Analytics /1000 datedevents|median60.85 ms,p9582.23 ms|
|History page|median16.01 ms,p9518.99 ms|
|Assessment|median16.99 ms,p9529.43 ms|
|Matching /bundled17|median20.77 ms,p9522.03 ms|
|Concurrent sessions32/8 threads|all200;median47.67 ms,max498.03 ms|
|Synthetic1000 fighter search|median15.00 ms,2 queries|
|Synthetic manual lookup|median0.59 ms,1 query|
|Synthetic1000 fighter ranking|median196.34 ms,2 queries|

[API timings](evidence/phase14/api-performance.json), [fighter timings](evidence/phase14/fighter-performance.json). Vite production build: mainJS319.44 kB(96.79 gzip), chartchunk337.61 kB(98.85 gzip), CSS44.63 kB(9.82 gzip); split progress/comparison/training modules. These are build sizes, not measured network transfer totals. Browser timing details are in the viewport load-performance JSON files.

## Launch gates and owner checklist

1. Preserve a verified backup of the intended athlete database and private recovery credentials. Review migration0008 and run Alembic explicitly before starting this release. QA used only disposable databases; real data migration remains your operational step.
2. Freeze/commit/tag the app, retain evidence and lock files, add artifact hashes/digest-pinned container builds as appropriate. Resolve fighter redistribution rights before any wider distribution.
3. Provision an authorized disposable PostgreSQL mma_test database and execute tools/verify_postgres.py plus optional native restore. Build/scan container artifacts, initialize reference data with one worker, then exercise the actual least-privilege DB/proxy/TLS/secret/retention setup.
4. Configure a real managed IdP; verify live linking, recovery, MFA policy, key rotation and session lifecycle. Decide legacy recovery migration policy explicitly before disabling it. Complete security/pentesting, edge rate controls and monitoring/incident response.
5. Establish encrypted off-host backups, access/deletion reconciliation, tested restore procedures and realistic RPO/RTO. The local synthetic rehearsal is not this production gate.
6. Obtain qualified MMA/strength/dietitian/medical review using the blank packs in docs/review. All31 methods remain pending independent review. No sign-offs or reviewer opinions were supplied/invented.
7. If provider use is desired, explicitly authorize a bounded live evaluation and configure project spending controls/current costs. No live paid evaluation was performed here.
8. Rerun staging acceptance on the actual stack and supported engines/devices. Obtain explicit owner authorization before public deployment or spending. CategoryC/D/E is not supported by current evidence.

## Exact local startup

From mma-performance-coach, after backing up an existing database:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend\requirements.lock.txt
cd frontend
npm.cmd ci
npm.cmd run build
cd ..\backend
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. For an existing installed environment, run the build/migration/server commands only. run-local.cmd automates those steps but does not replace backup/review. Use only this app's .env. See USER_GUIDE.md, AI_CONFIGURATION.md, DEPLOYMENT.md and KNOWN_LIMITATIONS.md.

## Executive decision

The local application integrates onboarding, explainable assessments/comparisons, template training, actual logging/progression, bounded source-backed nutrition, controlled coach changes, longitudinal analytics and private exports/account management. Automated verification supports local candidate use. Public launch remains blocked by real infrastructure/identity/PostgreSQL validation, licensing, operational security/recovery and independent professional review. The owner should retain evidence, back up/migrate deliberately, and complete those gates before authorizing external deployment.


## Final full-browser result

[Native full-suite report](evidence/phase14/browser-results.json):158 passed,0 failed,0 flaky,7 intentional skips in568.99 seconds (9.5 minutes). Thirty-three cases were scheduled per viewport. Four print skips apply outside desktop1440; three drawer skips apply outside the mobile viewports. No skip masks a missing browser prerequisite. The full UAT and prior-phase integration cases passed with an isolated server and no provider key. [Desktop screenshot](evidence/phase14/desktop-1440-overview.png), [mobile progress screenshot](evidence/phase14/mobile-375-progress.png), and the other per-view PNGs/PDFs are retained.


## Final release-check result and browser performance

[Focused report](evidence/phase14/browser-release-checks.json): 15 passed, 0 failed, 0 skipped in87.83seconds (five new timing cases plus ten repeated responsive/keyboard cases). The full report preceded adding the timing test; these are separate runs, not173unique tests. All40fresh core-view axe summaries report zero violations and no runtime errors; evidence routing now targets Phase14 for all five viewports. Final Ruff lint/format passed for74files.

| Width (CSS px) | Overview ready median (ms) | Progress dashboard ready median (ms) | DOMContentLoaded median (ms) |
| --- | ---: | ---: | ---: |
| 1440 | 328.61 | 509.6 | 45.9 |
| 1920 | 348.4 | 550.65 | 44.4 |
| 375 | 328.63 | 852.19 | 56.2 |
| 390 | 334.94 | 794.69 | 54 |
| 768 | 322.9 | 532.31 | 41.5 |

Three warm reloads per width, Edge155.0.4283.45, local HTTP, no throttling, synthetic demo with empty history; dashboard waits for the actual analytics response and rendered event summary. These numbers include automation polling. Long-history API performance is measured separately. [Raw viewport summaries](evidence/phase14/browser-performance-summary.json). No physical-device, cold-network or production-latency claim.


[Source integrity manifest](evidence/phase14/source-manifest.json) fingerprints the inspected application/test/config files and locks; it is not a signed release or commit.
