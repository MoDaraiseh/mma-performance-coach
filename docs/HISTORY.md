# Project history

This project was built in numbered phases, each with its own report in this folder. This page collects the release status and the per-phase upgrade notes that used to live in the README. Statements in each phase report describe that report's own date, not current availability or clearance.

Phase reports link to raw evidence files (test logs, browser results, screenshots, scans) under `docs/evidence/`. Those files were kept locally and are not published in this repository.

## Release status (as of 11 November 2026)

**Authoritative record:** [Final delivery, acceptance, operations and owner decisions](FINAL_DELIVERY.md) (4 November 2026). Local candidate acceptance passed; security clearance and launch remain blocked. Staging replacement and public deployment are not authorized.

- **Post-handoff review (11 November 2026):** [defects fixed, open findings and re-verification](POST_HANDOFF_REVIEW.md). These source fixes postdate the accepted Phase 24 candidate images, so the candidate must be rebuilt and re-accepted before they apply to staging.
- **Release:** 1.0.0-rc.17, category **A - local release candidate** on the [Phase 17 scale](PHASE17_ACCEPTANCE.md). No final tag.
- **Candidate environment:** original staging preserved at `127.0.0.1:18018`; isolated patched candidate at `127.0.0.1:18026` ([Phase 24](PHASE24_REPORT.md)).
- **Open security gates:** libxml2 CVE-2026-86140 (no supported Alpine fix); no current trusted image scan. The musl CVE-2026-107891 scanner discrepancy has vendor-backed fixed-status evidence but still awaits independent review.
- **Other launch blockers:** content-rights, professional (medical/nutrition/coaching) and security review; live identity provider, TLS, durable backups and monitoring. See [known limitations](KNOWN_LIMITATIONS.md).

## Phase history

Historical snapshots, newest first. Statements in these reports describe their own date, not current availability or clearance.

- **Phase 24 - container triage.** [Report](PHASE24_REPORT.md), [triage matrix](PHASE24_TRIAGE.md). Candidate scans: application 0 high/critical; PostgreSQL 0 critical/1 high. 388 backend / 12 frontend / 10 real Edge-to-PostgreSQL passed, plus native restore/session recovery.
- **Phases 18-23 - isolated staging.** [Phase 18 staging](PHASE18_STAGING.md), [launch gates](PHASE18_LAUNCH_GATES.md), [Phase 19](PHASE19_REPORT.md), [Phase 20](PHASE20_REPORT.md), [Phase 21](PHASE21_REPORT.md), [Phase 22](PHASE22_REPORT.md), [Phase 23](PHASE23_REPORT.md).
- **Phase 17 - release acceptance (1.0.0-rc.17).** [Acceptance](PHASE17_ACCEPTANCE.md), [feature matrix](PHASE17_FEATURE_MATRIX.md), [launch/deployment/rollback runbooks](PHASE17_LAUNCH_RUNBOOK.md). Earlier B-local labels used a different scale.
- **Phase 15 - catalog and feature refinement.** [Delivery](PHASE15_DELIVERY.md), [acceptance matrix](PHASE15_FEATURE_MATRIX.md). 19 source-backed fighter snapshots, 55 USDA foods and 49 exercises; macro-balanced fat-food substitutions, explicit amateur-training context and stronger allergy/source validation. 344 backend / 12 frontend tests; full Edge verification 168 passed, 0 failed, 7 intentional skips. Nutrition catalog v3 requires reviewed regeneration of older meal plans. Independent baseline checkpoint d8839ce.
- **Phase 14 - verified local release candidate (category B).** [Acceptance, feature matrix, evidence and launch gates](PHASE14_ACCEPTANCE.md). 328 backend / 12 frontend; full Edge 158 passed, 0 failed, 7 intentional skips across five widths. Schema 0008.
- **Phase 13 - infrastructure and identity.** [Verification and production blockers](PHASE13_INFRASTRUCTURE.md). Authlib OIDC with explicit local-account linking, session visibility/revocation, shared AI budgets, migration-aware readiness, private deployment templates and backup/restore tooling. Existing databases require migration 0008.
- **Phase 12 - review readiness.** [Safety audit, methodology inventory and four specialist review packs](PHASE12_SAFETY.md). Automated safety checks are separate from independent professional approval, which remains pending.
- **Phase 11 - analytics.** [Implementation, methodology and limitations](PHASE11_ANALYTICS.md). Longitudinal measurements, comparable records, weekly workload, calendar adherence, martial arts participation, technical achievements and private CSV/JSON/print reports (schema 0007).
- **Phase 10 - coach.** [Context, actions, evaluations and cost limits](PHASE10_COACH.md). Rescheduling, frequency changes, exercise/food replacements, assessment snapshots and evidence-gated progression use validated previews and explicit approval. Providers cannot authorize capabilities or write records. Live OpenAI quality remains unverified.
- **Phase 9 - nutrition.** [Report, coverage and limitations](PHASE9_NUTRITION.md). Forty USDA source-backed foods with fiber, sodium, calcium, iron and potassium; cooking/meal-count preferences and food replacements with preview and approval.
- **Phases 1-8.** See the sections below and the `PHASE*` reports in this folder.

## Phase 2 feature audit

See [the 17-module feature matrix and fix report](PHASE2_AUDIT.md) for verified scope, priorities and remaining work. This iteration adds current-input approval checks, recovery-aware reassessment proposals, serialized account writes, conservative limitation-based withholding, time-budgeted mixed training, read-only program history, actual-set/missed logging, body-fat/mobility check-ins and edit-draft resume.

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

See [Phase 3 delivery, rules, evidence and scientific boundaries](PHASE3_TRAINING.md).

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

See [Phase 4 delivery and coverage](PHASE4_COMPARISON.md) for the audit, mathematics, source register, browser evidence and limitations. Upgrade existing databases through Alembic **0004**. Startup adds missing reviewed records without overwriting existing snapshots; use **Comparison lab > Refresh reviewed fighter data** to explicitly replace legacy snapshots with the reviewed bundle. This reimports data, preserves revisions and does not fetch websites or advance verification dates.

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

[Phase 5 implementation, sources, tests and limitations](PHASE5_NUTRITION_COACH.md) documents the current nutrition/coaching system. Nutrition now uses a bundled **22-ingredient USDA SR Legacy subset (CC0)**, separate source versus macro-derived energy, bounded portions, macro guidance, additive dietary settings and feedback, substitutions, groceries and reviewed plan versions. The historical generic catalog does not certify allergens/halal products, guarantee local prices or establish complete micronutrient adequacy.

In **Nutrition**, save feedback if needed, choose **Preview updated meal plan** or a meal substitution, review the full candidate, then approve or reject. Old input assumptions are withheld after relevant changes. An approved sustained-weight review may use a check-in median without overwriting the profile. In **AI coach**, requests such as “Make my Monday workout shorter to 20 minutes” or “Suggest a different halal lunch” can prepare a real validated preview. An existing unlogged session/current usable nutrition plan is required. Approval saves a new version; the model has no write tools. Refer medical/competition-specific nutrition and contact training to qualified professionals.

Phase 5 itself added no schema migration; Phase 6 now requires **0005** before startup. Existing illustrative nutrition snapshots remain in history and require explicit reviewed regeneration. `POST /api/nutrition` remains an explicit authenticated manual generation/regeneration API for existing integrations; the application uses preview/approval for changes to existing meals. No nutrition API key or live USDA connection is required. Optional OpenAI settings remain server-only; provider calls have context/output limits, short timeouts, bounded retries and sanitized usage metadata. Paid live AI quality and global spend enforcement remain unverified; Phase 6 adds a tested per-account daily attempt quota.

To reproduce the food subset from an independently downloaded official archive:

```powershell
cd backend
..\.venv\Scripts\python.exe tools/import_usda.py ..\.qa-runtime\usda-sr-2018.zip
```

The importer has no network behavior. The included JSON is sufficient to run the application; downloading the source archive is optional for audit/reproduction. Sources, original IDs/descriptions and the checked archive hash are in [SOURCES.md](SOURCES.md#phase-5-nutrition-and-coaching-sources-reviewed-2026-10-31).

Phase 5 browser evidence uses `$env:PW_REPORT_FILE='../docs/evidence/phase5/browser-results.json'` and `$env:PW_EVIDENCE_DIR='../docs/evidence/phase5'` before `npm.cmd run test:browser` in `frontend/`. Optional A4 inspection uses `$env:MMA_QA_PHASE='phase5'` with `tests/check_prints.py` from `backend/`.

## Phase 6 release and operations

[Final readiness report](PHASE6_RELEASE.md), [deployment](DEPLOYMENT.md), [security review](SECURITY.md), [architecture](ARCHITECTURE.md), [API notes](API.md), [testing](TESTING.md) and [qualified specialist checklist](SPECIALIST_REVIEW.md) describe the release candidate. **Public production readiness is not claimed**: live PostgreSQL, deployed HTTPS/proxy, backup restoration, production operations and independent specialist review remain gates.

Migration **0005** adds independent expiring/revocable sessions and shared quota counters, preserving existing profiles/plans and recovery hashes. Old cookies require restoration with the existing private recovery token. Production configuration requires HTTPS `PUBLIC_ORIGIN`, explicit `ALLOWED_HOSTS` and secure cookies. See `.env.production.example` for all settings. New settings include session lifetime, API/auth limits, daily AI attempts, body size and explicit conversation/draft retention. `GET /api/ready` checks database connectivity; `/api/health` is process liveness. No passwords or managed identity are implied by token accounts.

Only this project's `.env` is loaded, centrally for API, migrations and maintenance. From `backend/`, `..\.venv\Scripts\python.exe -m app.maintenance` previews retention; add `--apply` only after reviewing policy and scheduling it appropriately. Historical plans/progress remain until account deletion. The PostgreSQL driver is included; `compose.postgres-test.yml` and `backend/tools/verify_postgres.py` provide opt-in disposable verification when PostgreSQL/Docker is available. No personal database was migrated or deleted for QA.

## Phase 7 training intelligence

[Phase 7 methodology, changes, tests and review decisions](PHASE7_TRAINING.md) documents the new ten-dimension athlete development view, independent histories/goals for Boxing, Muay Thai, Kickboxing, BJJ, Wrestling, Judo and integrated MMA, exact optional weekdays, optional supervised explosive practice, and bounded controlled cycling intervals. The catalog now has **39 exercises**, with separate Kickboxing and Judo entries. No anaerobic capacity or technical skill is invented from body measurements.

Edit discipline goals in assessment step 3, coaching/power preferences in step 4, and exact weekdays in step 5. In Training, inspect **Athlete development model** and open independent discipline details. Optional post-session fatigue is logged with the workout; recent high fatigue blocks progression suggestions. Current plans are not replaced by assessment/logging. Preview and approve a current-input change when training inputs change. Compatible reassessments preserve approved substitutions and reviewed loads; previous checkpoints/versions and workout history remain intact.

The new windows/caps/stages are explicit product heuristics and need qualified coaching review. There is no maximal testing, unsupervised contact, validated anaerobic assessment, competition-camp programming or independent professional sign-off. No schema migration beyond **0005** is required; old JSON profiles/logs have safe defaults. Local startup and the Phase 6 production gates remain unchanged.

## Phase 8 fighter data and matching

[Phase 8 report](PHASE8_FIGHTERS.md) gives actual division coverage, source/rights limitations, data quality, deterministic mathematics, tests and the offline import/rollback procedure. The bundle now has **17 source-snapshot records: 10 men, seven women**, including six attributed Wikipedia adaptations under [CC BY-SA 4.0](FIGHTER_SUPPLEMENT_LICENSE.md). Historical study coverage includes all eight men's and three active women's reference divisions; this is not a current comprehensive roster. Original 11 redistribution rights remain unestablished.

**Existing databases require migration 0006** before starting: run `..\.venv\Scripts\python.exe -m alembic upgrade head` from `backend/`. This backfills searchable fighter metadata and adds operator import-batch history, preserving athlete aggregates/favorites. The Comparison Lab now uses paginated server search with category, historical division, stance and career-status filters. Matching v3 reduces a partial physical group's contribution in proportion to its supported evidence; scores remain heuristic and independent from professional skill. Current status/division for the six additions remain unknown. No new web scraping or network startup dependency exists.
