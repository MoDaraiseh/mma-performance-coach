# MMA Performance Coach

Current development: [Phase 18 isolated staging](docs/PHASE18_DELIVERY.md) on `phase18-isolated-staging`. The existing release tag below is preserved. [Private staging procedure](docs/PHASE18_STAGING.md) and [launch gates](docs/PHASE18_LAUNCH_GATES.md) distinguish local preparation from unexecuted PostgreSQL/container/live-identity verification. No public deployment is authorized.

Current release: **1.0.0-rc.17**, [Phase 17 acceptance](docs/PHASE17_ACCEPTANCE.md), [feature matrix](docs/PHASE17_FEATURE_MATRIX.md), [launch/deployment/rollback runbooks](docs/PHASE17_LAUNCH_RUNBOOK.md). Readiness is **A - local release candidate** on the Phase 17 scale. Public launch is blocked; no public deployment is authorized. Earlier B-local labels used a different scale. See the current report for actual verification and remaining infrastructure, licensing and independent-review gates.

**Current delivery: Phase 15.** [Changes, source coverage, tests and limitations](docs/PHASE15_DELIVERY.md) ? [Updated acceptance matrix](docs/PHASE15_FEATURE_MATRIX.md).19source-backed fighter snapshots,55USDA foods and49exercises; macro-balanced fat-food substitutions, explicit amateur-training context and stronger allergy/source validation.344backend/12frontend tests pass; full Edge verification: 168 passed, 0 failed, 7 intentional skips; final safety checks: 5 passed. Existing data/schema0008 are preserved; nutrition catalog v3 requires reviewed regeneration of older meal plans. Independent baseline checkpoint d8839ce excludes secrets/runtime/evidence. No public deployment or expert approval. Earlier phase notes below are historical.


**Current release: Phase14 - verified local release candidate (category B).** [Acceptance report, feature matrix, evidence and launch gates](docs/PHASE14_ACCEPTANCE.md). 328 backend / 12 frontend tests passed; full Edge 158 passed, 0 failed, 7 intentional skips across five widths; final focused checks 15 passed. Current schema0008. No public deployment, live AI/IdP, PostgreSQL runtime or independent professional approval. Earlier phase statements below are historical snapshots.


**Latest: Phase 13 infrastructure and identity.** [Verification, evidence and production blockers](docs/PHASE13_INFRASTRUCTURE.md). Added Authlib OIDC with explicit local-account linking, session visibility/revocation, shared AI budgets, migration-aware readiness, private deployment templates and backup/restore tooling. **328 backend / 12 frontend tests passed; 25 focused Edge checks passed.** Existing databases require migration0008. PostgreSQL runtime, real IdP/MFA, TLS/proxy and production infrastructure remain unverified; no public deployment occurred.

**Latest: Phase 12 review readiness.** [Safety audit, methodology inventory and four specialist review packs](docs/PHASE12_SAFETY.md). Automated safety checks are separate from independent professional approval, which remains pending. Reassessment effort matching, deload rep consistency, rapid-cut withholding and minor/unsupported-claim coach safeguards were improved. No new migration; existing athlete data and plans are preserved.

**Latest: Phase 11 analytics.** [Implementation, methodology, verification and limitations](docs/PHASE11_ANALYTICS.md). Progress now provides actual longitudinal measurements, comparable records, weekly workload, explicit calendar adherence, martial arts participation, technical achievements and private CSV/JSON/print reports. Existing databases require `alembic upgrade head` from `backend/` (schema 0007); payload history and approved plans are preserved.

**Phase 10 coach.** [Context, actions, evaluations, cost limits and verification](docs/PHASE10_COACH.md). Offline coaching now uses bounded history and deterministic analytics. Rescheduling, frequency changes, exercise/food replacements, updated assessment snapshots and evidence-gated progression use validated previews and explicit approval. Providers cannot authorize capabilities or write records. Live OpenAI quality remains unverified. Schema head remains 0006 and existing data is preserved.

**Phase 9 nutrition.** [Report, coverage and limitations](docs/PHASE9_NUTRITION.md). Forty USDA source-backed foods now include fiber, sodium, calcium, iron and potassium. Cooking/meal-count preferences and selected food replacements integrate with preview, approval and retained history. Catalog v2 requires reviewed regeneration of old targets without erasing snapshots. No migration beyond 0006 is required.

A functional local MMA development workspace built with React, TypeScript, Vite, Recharts, FastAPI, Pydantic, SQLAlchemy, SQLite and Alembic. The existing Saudi law tracker is untouched.

## Run on Windows

From this directory, with Python 3.12+ and Node 22.12+ installed:

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

Open **http://127.0.0.1:8000**. API documentation: **http://127.0.0.1:8000/docs**. Choose **Explore the demo** or create your athlete profile. Keep the one-time local recovery token private. It restores access after signing out or clearing cookies.

After dependencies are installed, `run-local.cmd` builds the frontend, applies migrations and starts the complete app. `requirements.lock.txt` and `package-lock.json` pin the verified dependency set; `requirements.txt` expresses supported package ranges.

For frontend development, keep the backend running and use a second terminal:

```powershell
cd frontend
npm.cmd run dev
```

Open the URL printed by Vite (normally http://127.0.0.1:5173). Its `/api` proxy connects to port 8000. Restart the backend after building the frontend for the first time: static serving is configured at backend import time.

On macOS/Linux replace `.venv\Scripts\python.exe` with `.venv/bin/python` and `npm.cmd` with `npm`.

## Configuration

Copy `.env.example` to `.env` in **this app directory** if configuration is needed. Do not reuse the parent project's `.env`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./mma.db` | Relative to backend working directory. PostgreSQL driver is pinned; offline migration SQL compiles, but real PostgreSQL integration remains unverified. |
| `OPENAI_API_KEY` | empty | Optional, server-only. All calculations and local coaching work without it. |
| `OPENAI_MODEL` | `gpt-4o-mini` | Configurable Responses API model with structured output support. |
| `COOKIE_SECURE` | `false` | Set `true` behind HTTPS for deployment. |
| `FIGHTER_LICENSED_EXPORT` | empty | Optional server-local licensed fighter JSON export path; no feed bundled. |
| `FIGHTER_LICENSE_REFERENCE` | empty | Operator license reference; must match each export source. |

Alembic imports the same database configuration as the API. Migrations are explicit; startup fails on an uninitialized database. Public deployment remains gated on PostgreSQL, external HTTPS/proxy, identity-policy and operational review; see docs/DEPLOYMENT.md.

## Implemented workflows

- Six-step editable athlete assessment, backend draft saving, optional measurements, metric/imperial input, independent discipline history and benchmark evidence labels.
- Persistent local accounts with hashed high-entropy recovery tokens, HttpOnly SameSite cookies, user-scoped records, data download and complete account deletion.
- Physical calculations, explainable scale-weight division references, historical women's featherweight distinction, conservative target-weight uncertainty, and exploratory style priorities.
- Seventeen source-reviewed UFC fighter study snapshots (10 men, seven women; 11 original official-source and six attributed secondary-source records), field-level provenance, current/history division contexts, manual comparisons, configurable deterministic ranking and coverage, height/reach charts, immutable favorites, and explicit provider refresh with archived data revisions.
- A 12-week conservative training roadmap with phases, deloads, recovery constraints, equipment substitutions, session details and duplicate-safe workout logging.
- Estimated resting/TDEE/maintenance ranges, optional bounded goal adjustments, macro guidance, seven-day source-backed portions, dietary exclusions, meal feedback, substitution previews and approved nutrition versions.
- Weekly check-ins, weight/sleep/fatigue and benchmark charts, recorded personal bests, plan completion, comparable benchmark changes and reassessment reports.
- Contextual local coaching and optional structured OpenAI explanations/intents, using current usable plan/meal and recent progress summaries. Validated training/meal edits require explicit approval; provider failures fall back locally.
- Preview/approve/reject plan revisions, retained plan versions and original inputs, stale proposal protection. No chat text directly mutates a saved plan.
- Responsive charcoal/red UI, local font assets, accessible labels and print views. JSON export includes all user records and plan versions.

## Architecture

```text
frontend/src/
  App.tsx                  workspace shell, overview and assessment views
  api.ts, types.ts         API client and typed contracts
  components/              onboarding, comparison, training, meals, progress, coach
  components/ui.tsx        reusable presentation components
backend/app/
  main.py                  authenticated REST services and AI orchestration
  schemas.py               strict validated input contracts
  db.py                    SQLAlchemy persistence
  analysis.py              physical, division, style, matching, benchmark services
  programs.py              compatibility exports for training/nutrition services
  nutrition*.py            calculations, composition/integrity and strict contracts
  ingredients.py           source-backed USDA catalog; dietary.py screens exclusions
  coach_actions.py         bounded coaching intents and validated candidates
  fighters.py              replaceable provider interface and sourced seed adapter
backend/migrations/        explicit versioned schema migrations
backend/tests/             mathematical and API integration tests
docs/                      methodology, provenance, delivery status
```

The local schema uses users, versioned typed JSON athlete aggregates, public fighter snapshots and reference snapshots. It intentionally does **not** create a separate relational table for every conceptual entity in the brief. Profile experiences, goals and measurements are captured in profile versions; meals and exercises live in immutable plan input/output aggregates. This keeps the local implementation compact while preserving ownership and history. Structured exercise and USDA food catalogs, per-exercise performance logs and nutrition/coaching proposal aggregates now extend this storage model; no relational table is added for every food or exercise.

## Tests and checks

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest -q
cd ..\frontend
npm.cmd run test
npm.cmd run typecheck
npm.cmd run build
npm.cmd audit
```

## Phase 1 browser QA

Real-browser coverage, fixes and evidence are documented in [the Phase 1 QA report](docs/PHASE1_QA.md). The browser suite uses installed Microsoft Edge in headless mode and builds the production frontend first:

```powershell
cd frontend
npm.cmd run test:browser
npm.cmd run test:browser:report
```

Tests cover 1440, 1920, 768, 390 and 375 CSS-pixel widths. They start an isolated API on port **8123**, create a disposable database under this application's ignored `.qa-runtime/`, and force the AI key to empty. They refuse to reuse a server already on that port. Normal `backend/mma.db` and the parent tracker are not used. A configured AI interface is tested with a labeled mocked transport; no paid provider call is made.

If Edge is unavailable, install Playwright Chromium with `npm.cmd exec playwright -- install chromium`, then set `$env:PW_CHANNEL='chromium'` before running the suite. Missing browser executables are a failed prerequisite, not a passing or silently skipped browser run. Reports and traces are local; avoid committing test artifacts containing recovery credentials. Saved screenshot evidence dismisses the synthetic account's recovery token first.

For optional print-page text/margin checks and PNG renders:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pip install -r requirements-qa.txt
..\.venv\Scripts\python.exe tests\check_prints.py
```

The app's **Print report** button prints the current view (including the selected training week or nutrition day), with ingredient/method disclosures expanded temporarily. **Settings & data → Download all data** exports all saved versions and includes record types.

Core tests require no paid APIs. Optional backend lint/format uses Ruff (`ruff check backend`, `ruff format --check backend`). Frontend formatting: `npm.cmd exec prettier -- --check src tools vite.config.ts`.

See [delivery status](docs/DELIVERY.md) for exact results and verification limits, [methodology](docs/METHODOLOGY.md) for formulas, and [sources](docs/SOURCES.md) for provenance and data permissions.

## Remaining limits and next improvements

This is a working local first version, not the entire production specification. The fighter library is intentionally small (17 dated snapshots, including seven women), and omits unverified current records, most stance data and imagery. Two explicitly historical statistics are descriptive only. Style similarity is excluded without a shared source-backed taxonomy. No live scraping, licensed feed, professional ability score or automated weight cut is implemented.

Training uses conservative templates, not clinically reviewed individualized programming or a full exercise library. Food values come from a 22-record public-domain USDA subset; meals target general macro guidance, with no complete micronutrient or competition-specific optimization. Structured exclusions and inspired ingredient patterns are supported; budget tiers do not represent real prices, and legacy preference prose is not automatically interpreted. The coach supports whitelisted language-driven previews plus the existing frequency form, rather than arbitrary plan rewriting. Reassessments are user-triggered, with week 4/8/12 prompts in the plan rather than scheduled notifications. Adherence is reported as recorded plan completion, not automatically inferred attendance. Exercise performance logging supports optional actual sets, repetitions, load and timed duration, alongside session duration/effort and separate check-in benchmarks.

Before public deployment: validate the implemented session/rate/production controls under the actual HTTPS proxy and PostgreSQL deployment, decide token-identity suitability, schedule retention and review consent/backup governance, obtain rights for expanded datasets, review training/nutrition with qualified practitioners, and complete real-device, manual assistive-technology and cross-browser QA. The requested responsive browser matrix now runs in headless Edge; a real paid AI response has not been exercised.


## Phase 2 feature audit

See [the 17-module feature matrix and fix report](docs/PHASE2_AUDIT.md) for verified scope, priorities and remaining work. This iteration adds current-input approval checks, recovery-aware reassessment proposals, serialized account writes, conservative limitation-based withholding, time-budgeted mixed training, read-only program history, actual-set/missed logging, body-fat/mobility check-ins and edit-draft resume.

**Existing databases require migration before starting the updated backend:**

```powershell
cd backend
..\.venv\Scripts\python.exe -m alembic upgrade head
```

Migration `0003` adds the per-account write serialization counter; it preserves existing records. Legacy pending proposals without source bindings must be previewed again before approval. Explicit frequency revisions retain prior versions and restart week 1; Phase 3 adaptive revisions continue the cycle after the selected checkpoint. New adverse recovery or training-profile changes withhold the active schedule until a fresh revision is approved. Historical prescriptions remain historical references, not current clearance.

To keep Phase 2 browser evidence separate:

```powershell
cd frontend
$env:PW_REPORT_FILE='../docs/evidence/phase2/browser-results.json'
$env:PW_EVIDENCE_DIR='../docs/evidence/phase2'
npm.cmd run test:browser
```


## Phase 3 training intelligence

See [Phase 3 delivery, rules, evidence and scientific boundaries](docs/PHASE3_TRAINING.md).

- **37-entry structured exercise catalog** with technique, movement patterns, muscle involvement, equipment, guidance, mistakes, modification notes and alternatives.
- Catalog-linked timed workouts, equipment and conditioning preferences, strength/conditioning goal emphasis, technical-access checks, mobility blocks and phase/deload structure. Existing instructor-led classes count inside the weekly availability budget.
- Actual exercise sets, repetitions, load, RPE, duration, distance, session date and notes; completed/failed/missed outcomes; per-exercise history tables/charts. Session effort starts blank and missing effort is not fabricated.
- Separate recorded versus estimated athletic evidence, relative-load and pace calculations, missing-domain disclosure and subjective recovery review.
- Evidence-gated repetition/load/duration proposals; no automatic progression after missing, failed or missed work. Recovery, prescribed dose, separate completion dates and effort matter.
- Week 4/8 adaptive proposals preserve earlier weeks and cycle logs; week 12 reviews the completed cycle. Substitutions are equipment-filtered proposals requiring approval. Full proposed prescriptions are reviewable in AI coach.

No extra database migration is required beyond `0003`; optional JSON fields have backward-compatible defaults. Existing plans are not silently regenerated. To use the new catalog engine, generate a first plan or explicitly preview and approve a current-input revision. Historical performance remains accessible across cycles; progression decisions use the current cycle only. Review age/health/access limitations with qualified professionals; contact training and injury-sensitive programming require qualified coaches.

Phase 3 browser evidence uses a separate directory:

```powershell
cd frontend
$env:PW_REPORT_FILE='../docs/evidence/phase3/browser-results.json'
$env:PW_EVIDENCE_DIR='../docs/evidence/phase3'
npm.cmd run test:browser
```

Optional print inspection: from `backend`, set `$env:MMA_QA_PHASE='phase3'` and run `..\.venv\Scripts\python.exe tests/check_prints.py`. The catalog/intelligence panels are excluded from current-view print to avoid printing the whole library; JSON export includes all recorded fields.


## Phase 4 comparison system

See [Phase 4 delivery and coverage](docs/PHASE4_COMPARISON.md) for the audit, mathematics, source register, browser evidence and limitations. Upgrade existing databases through Alembic **0004**. Startup adds missing reviewed records without overwriting existing snapshots; use **Comparison lab > Refresh reviewed fighter data** to explicitly replace legacy snapshots with the reviewed bundle. This reimports data, preserves revisions and does not fetch websites or advance verification dates.

Optional operator settings `FIGHTER_LICENSED_EXPORT` (server-local JSON file) and `FIGHTER_LICENSE_REFERENCE` enable a validated licensed-export adapter. No commercial provider or redistribution license is included. Do not put these settings in frontend configuration. Schema: `backend/app/fighter_models.py`; canonical units cm/kg, per-field source IDs, source dates/method/rights and division-history context required.


Phase 4 QA uses an isolated temporary database and these evidence settings:

```powershell
cd frontend
$env:PW_REPORT_FILE='../docs/evidence/phase4/browser-results.json'
$env:PW_EVIDENCE_DIR='../docs/evidence/phase4'
npm.cmd run test:browser
```

For the four A4 reports, from `backend/` set `$env:MMA_QA_PHASE='phase4'` and run `..\.venv\Scripts\python.exe tests/check_prints.py` with the optional PDF QA dependencies described above. Current test results, intermediate failures and limitations are in the Phase 4 report.


## Phase 5 nutrition and adaptive coach

[Phase 5 implementation, sources, tests and limitations](docs/PHASE5_NUTRITION_COACH.md) documents the current nutrition/coaching system. Nutrition now uses a bundled **22-ingredient USDA SR Legacy subset (CC0)**, separate source versus macro-derived energy, bounded portions, macro guidance, additive dietary settings and feedback, substitutions, groceries and reviewed plan versions. The historical generic catalog does not certify allergens/halal products, guarantee local prices or establish complete micronutrient adequacy.

In **Nutrition**, save feedback if needed, choose **Preview updated meal plan** or a meal substitution, review the full candidate, then approve or reject. Old input assumptions are withheld after relevant changes. An approved sustained-weight review may use a check-in median without overwriting the profile. In **AI coach**, requests such as ?Make my Monday workout shorter to 20 minutes? or ?Suggest a different halal lunch? can prepare a real validated preview. An existing unlogged session/current usable nutrition plan is required. Approval saves a new version; the model has no write tools. Refer medical/competition-specific nutrition and contact training to qualified professionals.

Phase 5 itself added no schema migration; Phase 6 now requires **0005** before startup. Existing illustrative nutrition snapshots remain in history and require explicit reviewed regeneration. `POST /api/nutrition` remains an explicit authenticated manual generation/regeneration API for existing integrations; the application uses preview/approval for changes to existing meals. No nutrition API key or live USDA connection is required. Optional OpenAI settings remain server-only; provider calls have context/output limits, short timeouts, bounded retries and sanitized usage metadata. Paid live AI quality and global spend enforcement remain unverified; Phase 6 adds a tested per-account daily attempt quota.

To reproduce the food subset from an independently downloaded official archive:

```powershell
cd backend
..\.venv\Scripts\python.exe tools/import_usda.py ..\.qa-runtime\usda-sr-2018.zip
```

The importer has no network behavior. The included JSON is sufficient to run the application; downloading the source archive is optional for audit/reproduction. Sources, original IDs/descriptions and the checked archive hash are in [SOURCES.md](docs/SOURCES.md#phase-5-nutrition-and-coaching-sources-reviewed-2026-10-31).

Phase 5 browser evidence uses `$env:PW_REPORT_FILE='../docs/evidence/phase5/browser-results.json'` and `$env:PW_EVIDENCE_DIR='../docs/evidence/phase5'` before `npm.cmd run test:browser` in `frontend/`. Optional A4 inspection uses `$env:MMA_QA_PHASE='phase5'` with `tests/check_prints.py` from `backend/`.


## Phase 6 release and operations

[Final readiness report](docs/PHASE6_RELEASE.md), [deployment](docs/DEPLOYMENT.md), [security review](docs/SECURITY.md), [architecture](docs/ARCHITECTURE.md), [API notes](docs/API.md), [testing](docs/TESTING.md) and [qualified specialist checklist](docs/SPECIALIST_REVIEW.md) describe the release candidate. **Public production readiness is not claimed**: live PostgreSQL, deployed HTTPS/proxy, backup restoration, production operations and independent specialist review remain gates.

Migration **0005** adds independent expiring/revocable sessions and shared quota counters, preserving existing profiles/plans and recovery hashes. Old cookies require restoration with the existing private recovery token. Production configuration requires HTTPS `PUBLIC_ORIGIN`, explicit `ALLOWED_HOSTS` and secure cookies. See `.env.production.example` for all settings. New settings include session lifetime, API/auth limits, daily AI attempts, body size and explicit conversation/draft retention. `GET /api/ready` checks database connectivity; `/api/health` is process liveness. No passwords or managed identity are implied by token accounts.

Only this project's `.env` is loaded, centrally for API, migrations and maintenance. From `backend/`, `..\.venv\Scripts\python.exe -m app.maintenance` previews retention; add `--apply` only after reviewing policy and scheduling it appropriately. Historical plans/progress remain until account deletion. The PostgreSQL driver is included; `compose.postgres-test.yml` and `backend/tools/verify_postgres.py` provide opt-in disposable verification when PostgreSQL/Docker is available. No personal database was migrated or deleted for QA.


## Phase 7 training intelligence

[Phase 7 methodology, changes, tests and review decisions](docs/PHASE7_TRAINING.md) documents the new ten-dimension athlete development view, independent histories/goals for Boxing, Muay Thai, Kickboxing, BJJ, Wrestling, Judo and integrated MMA, exact optional weekdays, optional supervised explosive practice, and bounded controlled cycling intervals. The catalog now has **39 exercises**, with separate Kickboxing and Judo entries. No anaerobic capacity or technical skill is invented from body measurements.

Edit discipline goals in assessment step 3, coaching/power preferences in step 4, and exact weekdays in step 5. In Training, inspect **Athlete development model** and open independent discipline details. Optional post-session fatigue is logged with the workout; recent high fatigue blocks progression suggestions. Current plans are not replaced by assessment/logging. Preview and approve a current-input change when training inputs change. Compatible reassessments preserve approved substitutions and reviewed loads; previous checkpoints/versions and workout history remain intact.

The new windows/caps/stages are explicit product heuristics and need qualified coaching review. There is no maximal testing, unsupervised contact, validated anaerobic assessment, competition-camp programming or independent professional sign-off. No schema migration beyond **0005** is required; old JSON profiles/logs have safe defaults. Local startup and the Phase 6 production gates remain unchanged.


## Phase 8 fighter data and matching

[Phase 8 report](docs/PHASE8_FIGHTERS.md) gives actual division coverage, source/rights limitations, data quality, deterministic mathematics, tests and the offline import/rollback procedure. The bundle now has **17 source-snapshot records: 10 men, seven women**, including six attributed Wikipedia adaptations under [CC BY-SA 4.0](docs/FIGHTER_SUPPLEMENT_LICENSE.md). Historical study coverage includes all eight men's and three active women's reference divisions; this is not a current comprehensive roster. Original 11 redistribution rights remain unestablished.

**Existing databases require migration 0006** before starting: run `..\.venv\Scripts\python.exe -m alembic upgrade head` from `backend/`. This backfills searchable fighter metadata and adds operator import-batch history, preserving athlete aggregates/favorites. The Comparison Lab now uses paginated server search with category, historical division, stance and career-status filters. Matching v3 reduces a partial physical group's contribution in proportion to its supported evidence; scores remain heuristic and independent from professional skill. Current status/division for the six additions remain unknown. No new web scraping or network startup dependency exists.
