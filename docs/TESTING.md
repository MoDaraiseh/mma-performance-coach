# Testing and reproducibility

Current final acceptance and exact results: [Phase 17](PHASE17_ACCEPTANCE.md). Historical sections below retain their phase-specific totals. Phase 17 evidence is isolated in ignored `docs/evidence/phase17/`; no normal athlete database is used.

## Phase 17 commands and environment

Windows PowerShell, app-local Python 3.14.7 environment, Node 24.20.0/npm11.19.0, Edge155.0.4283.45. From backend, actual commands used:

```powershell
..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=../.qa-runtime/pytest-phase17
..\..\.venv\Scripts\ruff.exe check app tests tools migrations
..\..\.venv\Scripts\ruff.exe format --check app tests tools migrations
..\.venv\Scripts\python.exe -m pip check
..\.venv\Scripts\python.exe -m pip_audit -r requirements.lock.txt --format json --output ../docs/evidence/phase17/python-audit.json
$env:MMA_QA_PHASE='phase17'
..\.venv\Scripts\python.exe tools/release_inventory.py
..\.venv\Scripts\python.exe tools/verify_sqlite_restore.py
..\.venv\Scripts\python.exe tools/evaluate_coach.py --limit 18
..\.venv\Scripts\python.exe tools/benchmark_api.py
..\.venv\Scripts\python.exe tools/benchmark_fighters.py
# After browser PDFs are available:
..\.venv\Scripts\python.exe tests/check_prints.py
# After final source commit/tag (refuses dirty source):
..\.venv\Scripts\python.exe tools/build_release_manifest.py
```

Ruff is available in the parent virtual environment but commands inspect only this project. No parent code/configuration is modified. From frontend:

```powershell
npm.cmd test
npm.cmd run build
npm.cmd run typecheck:browser
npx.cmd prettier --check src e2e
npm.cmd audit --json
$env:PW_REPORT_FILE='../docs/evidence/phase17/browser-results.json'
$env:PW_EVIDENCE_DIR='../docs/evidence/phase17'
npm.cmd run test:browser
```

The build command includes app TypeScript (`tsc -b`); the browser command repeats production build and browser TypeScript before the full suite. Outputs were redirected into named Phase 17 logs; PowerShell text logs can be UTF-16 while native JSON files are UTF-8. Browser channel is installed Edge/Blink, one worker, local isolated HTTP at8123, five configured viewports and synthetic fixtures. Live provider keys are cleared by test server. Automated accessibility checks, screen-reader/manual-device testing and mocked/live identity/provider tests are distinct in the final report.

Real PostgreSQL verification was not executed: no Docker/PostgreSQL/native tools or authorized disposable test URL. When available, explicitly configure `MMA_TEST_DATABASE_URL` naming `mma_test*`, optionally `MMA_TEST_RESTORE=1`, then run `python tools/verify_postgres.py`; preserve output and inspect failures. Never substitute a normal DATABASE_URL or athlete database. Live-model evaluation likewise remains unexecuted and requires separate explicit configuration/cost authorization. [Controlled procedures and remaining gates](PHASE17_LAUNCH_RUNBOOK.md).

Run commands from the stated MMA project directories. Never point tests at personal or production data. The original tracker has independent tooling and is outside this task.

From `backend/`:

```powershell
..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=../.qa-runtime/pytest-local
ruff check app tests tools migrations
ruff format --check app tests tools migrations
```

Pytest creates disposable SQLite data; migration tests create a separate database beneath `--basetemp`. That directory is pytest-owned and may be cleared by pytest: use only a dedicated QA path. Tests override provider key and test quotas; specific tests lower quotas to verify enforcement. They do not upgrade the normal athlete DB. The PostgreSQL SQL compilation test connects to no server; real PostgreSQL verification is a separate opt-in [deployment procedure](DEPLOYMENT.md#database-setup-and-migration).

From `frontend/`:

```powershell
npm.cmd test
npm.cmd run typecheck
npm.cmd run typecheck:browser
npm.cmd exec prettier -- --check src e2e tools vite.config.ts playwright.config.ts
npm.cmd run build
$env:PW_REPORT_FILE='../docs/evidence/phase6/browser-results.json'
$env:PW_EVIDENCE_DIR='../docs/evidence/phase6'
npm.cmd run test:browser
```

Playwright uses installed Edge, one worker and an isolated API on port 8123. It refuses to reuse a server, clears provider credentials and overrides the environment to test mode. Widths: 1440, 1920, 768, 390 and 375 CSS pixels. The suite covers prior Phase 1–5 journeys plus 401 workspace reset and canceled/confirmed account deletion. New accounts are synthetic; screenshots dismiss recovery credentials. Traces may contain synthetic credentials; keep test-result folders ignored. Missing browser executables are a failed prerequisite, not a successful run. For Playwright Chromium set `PW_CHANNEL=chromium` after installing its browser; no other engine/device coverage is implied by Edge results.

Optional print QA from `backend/`:

```powershell
..\.venv\Scripts\python.exe -m pip install -r requirements-qa.txt
$env:MMA_QA_PHASE='phase6'
..\.venv\Scripts\python.exe tests/check_prints.py
```

From project root, dependency checks and local disposable benchmark:

```powershell
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe -m pip install -r backend/requirements-security.txt
.venv\Scripts\python.exe -m pip_audit -r backend/requirements.lock.txt --no-deps --disable-pip
.venv\Scripts\python.exe backend/tools/benchmark_api.py
cd frontend
npm.cmd audit
```

Audit commands need advisory-network access. Python `--no-deps --disable-pip` audits every entry in the fully enumerated lock; it does not resolve a new environment. The lock is version-pinned but lacks artifact hashes. Record query date/results and distinguish advisory lookup failure from a clean audit. Performance numbers are local, 20 samples per operation and 1,000 synthetic history versions; do not extrapolate to production throughput or real-user latency.

Migration release checks include SQLite upgrade/check/downgrade/re-upgrade with preservation of a pre-existing account hash and offline PostgreSQL SQL compilation through 0005. Runtime PostgreSQL, external TLS/proxy, backup restoration, paid AI, production quotas/costs, physical devices and manual screen-reader/specialist review remain separate release gates.


## Phase 10 AI evaluation

`backend/tests/fixtures/coach_evaluations.json` defines 18 reproducible scenarios; `tests/test_phase10.py` uses mock responses/transports plus real transactional API checks. Run `..\.venv\Scripts\python.exe -m pytest tests/test_phase10.py -q` from backend. `tools/evaluate_coach.py --limit 3` is a synthetic offline smoke report. Optional live runs require `--live`, `MMA_LIVE_COACH_EVAL=1`, an explicit `OPENAI_MODEL` and server-side `OPENAI_API_KEY`; calls may incur charges. Live evaluation has not been run. Browser cases in `frontend/e2e/phase10.spec.ts` verify preview/approval/history, rescheduling and stale nutrition, frequency rejection, evidence-gated progression and context disclosure. See [full report and limitations](PHASE10_COACH.md).


## Phase 11 analytics

Run `python -m pytest tests/test_phase11.py` from backend with the project virtualenv. Eight regression tests cover trends, records, dates/units, ownership, exports, correction/deletion, calendar adherence, 2,100-event histories and migration 0007. Full backend: 286 passed; frontend: 12 passed.

`npm run test:browser -- phase11.spec.ts` exercises measured/empty dashboards, technical milestone persistence without plan mutation, CSV download, responsive overflow and targeted axe checks at five viewport widths. Full suite also prints the Progress report. Set `PW_REPORT_FILE=../docs/evidence/phase11/browser-results.json` and `PW_EVIDENCE_DIR=../docs/evidence/phase11` before browser execution. `MMA_QA_PHASE=phase11` selects the five-report print inspector. Consult the [final report](PHASE11_ANALYTICS.md) for actual execution results and limitations.


## Phase 12 safety regression

`python -m pytest tests/test_phase12.py` covers 22 safety cases; full backend suite:308 passed, frontend:12 passed. `python tools/build_review_examples.py` regenerates seven synthetic review examples with no athlete database writes or provider requests. Browser scenarios in `e2e/phase12.spec.ts` verify honest review status and visible rapid-cut withholding; actual results are in [Phase 12](PHASE12_SAFETY.md). Automated testing does not satisfy independent expert-review gates.


## Phase 13 security/infrastructure

Full backend:328 passed (20 new Phase13 cases), frontend:12 passed. `python -m pytest tests/test_phase13.py` exercises real Authlib signed-token verification through mocked HTTP discovery/token/JWKS, identity/link ownership, replay/expiry/claims, session revocation, shared calendar budgets, readiness and legacy-preserving migration/backup behavior. `python tools/verify_sqlite_restore.py` emits synthetic backup/restore evidence without normal athlete data.

Final focused Edge:25 passed at five widths, covering sessions, revocation, recovery, mocked managed login/link navigation and existing account-deletion/privacy flows. Provider browser pages are mocked; no real SSO/MFA validation. Five Settings axe scans passed. `MMA_QA_PHASE=phase13` selects isolated API/fighter performance evidence destinations. PostgreSQL native runtime/restore and container/proxy infrastructure remain unexecuted; use the dedicated test tools/runbook on an authorized disposable host. [Evidence and limitations](PHASE13_INFRASTRUCTURE.md).


## Phase14 release acceptance

The [current acceptance report](PHASE14_ACCEPTANCE.md), [feature matrix](PHASE14_FEATURE_MATRIX.md), [known limitations](KNOWN_LIMITATIONS.md), [user guide](USER_GUIDE.md) and [AI configuration guide](AI_CONFIGURATION.md) consolidate the release. Current schema head is0008. Historical results above retain their phase-specific context; Phase14 evidence supersedes release totals. No public deployment, live AI, real IdP or PostgreSQL runtime verification is claimed. Source validation rechecks bundled schemas/provenance and nutrient completeness; it does not reverify current fighter facts online.


Phase14 reproduction (project root; use only the dedicated evidence/QA paths):

```powershell
.venv\Scripts\python.exe backend/tools/release_inventory.py
$env:MMA_QA_PHASE='phase14'
.venv\Scripts\python.exe backend/tools/benchmark_api.py
.venv\Scripts\python.exe backend/tools/benchmark_fighters.py
.venv\Scripts\python.exe backend/tools/verify_sqlite_restore.py
.venv\Scripts\python.exe backend/tools/evaluate_coach.py --limit 18
cd frontend
$env:PW_REPORT_FILE='../docs/evidence/phase14/browser-results.json'
$env:PW_EVIDENCE_DIR='../docs/evidence/phase14'
npm.cmd run test:browser
cd ..\backend
..\.venv\Scripts\python.exe tests/check_prints.py
```

Use the backend/frontend/static/advisory commands above as well. The native Phase14 full report predates addition of the five timing cases; the separate release-check report verifies those plus ten repeated responsive/keyboard cases. Do not add repeated test executions together as unique coverage. Advisory results are dated point-in-time checks. Re-running against the same evidence directory intentionally replaces that run's artifacts; archive them first if immutable evidence is required.


## Phase15 regression and catalog reproduction

Baseline328backend/12frontend passed. Updated344backend/12frontend passed;16new cases are in backend/tests/test_phase15.py. Existing fixed coverage expectations now match19fighters/55foods and the additional Mobility category; no validation assertions were removed. Full/current browser evidence and final follow-up results are in PHASE15_DELIVERY.md.

From backend: `..\.venv\Scripts\python.exe tools/phase15_quality.py` produces the operator report using public bundled data, without athlete DB reads/writes or network. Reproduce foods using `..\.venv\Scripts\python.exe tools/import_usda.py ../.qa-runtime/usda-sr-2018.zip` after obtaining the exact official hash-pinned archive. This intentionally updates the source catalog, not athlete data. Keep source changes in the independent MMA repository; do not add runtime data/evidence.

From frontend set PW_REPORT_FILE=../docs/evidence/phase15/browser-results.json and PW_EVIDENCE_DIR=../docs/evidence/phase15 before npm.cmd run test:browser. The dedicated phase15.spec.ts tests a new sourced fighter, explicit training context, selected fat-food preview/approval/history, and final Mobility filter/objective behavior. Final follow-up uses a new API process and rebuilt assets so stale static modules do not stand in for final code. MMA_QA_PHASE=phase15 selects the optional print inspector. No physical-device/live-AI/real-IdP/PostgreSQL runtime pass is implied.


Phase17 full Edge initially returned163passed/5fixture failures/7intentional skips. Corrected UTC calendar fixtures; final `npm.cmd run test:browser -- phase11.spec.ts` passed15cases across five widths with explicit native exit0. Reports/logs use edge-phase11-final names and separate evidence directory. `PW_CHANNEL=chromium` with `journey.spec.ts --project=desktop-1440 --project=mobile-375` additionally passed4cases. All commands were sequential against isolated servers; the original full report remains unchanged. [Failure analysis and precise accounting](PHASE17_BROWSER_QA.md).
