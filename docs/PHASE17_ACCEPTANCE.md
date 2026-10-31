# Phase 17 final release acceptance

Date: **2026-11-01**, Asia/Dubai. Baseline source `95651d9`; final source is identified by annotated local tag **v1.0.0-rc.17** and the generated clean-source manifest. Native logs preserve tool timestamps, including UTC dates. Scope is exclusively `mma-performance-coach/`; original tracker tracked files remain unchanged. No athlete data was deleted/reset/migrated and no existing credentials or approved history were replaced.

**Final readiness: A — local release candidate on the Phase 17 scale.** Earlier phases used B for the same local-candidate category; this is a label reconciliation, not a promotion. Staging readiness and production readiness remain blocked by missing external acceptance evidence. Public launch is not appropriate. No public deployment, registry publication, live AI call, external service purchase or paid provisioning occurred.

## Review and implementation

Reviewed Phase 14 acceptance, Phase 15 report/matrix, Phase 16 report/operations, architecture, testing, security, deployment, known limitations, data/source notices, the 31-method inventory and four specialist packs. Historical counts/labels remain in their dated reports; current entry points now link this acceptance. Current state is Alembic head **0008**, matching v4, 19 fighter snapshots (11 men/eight women), 55 USDA ingredients and 49 exercises. Professional records/style-trait coverage remain sparse/unknown, not invented.

The [final feature matrix](PHASE17_FEATURE_MATRIX.md) covers all 22 requested functional areas plus infrastructure/review gates with actual service/API/component and executed test mappings. Partial areas include individualized weight targets, style/scientific validation, sparse fighter coverage, meal variety/adequacy, live AI quality and very-large full-account exports. No overall completion percentage is assigned.

This phase preserves domain behavior. A calendar acceptance fixture mixed local weekday arithmetic and UTC ISO dates; before 04:00 Dubai it submitted Sunday instead of Monday and the backend correctly returned422. Corrected UTC fixture arithmetic; initial full-run failures and fresh focused rechecks are retained rather than relabeled as an all-green full run. [Fixed-time reproduction](evidence/phase17/utc-fixture-reproduction.json).

Changes: phase-safe source/benchmark/restore/print evidence routing; corrected obsolete six-versus-eight supplement wording; real nutrition generation/offline-coach/four-account timings; clean-source/artifact/evidence hashing tool; current feature/security/licensing/launch reports; release notes/changelog and controlled deployment/rollback procedures. No new database migration or recommendation equation was introduced. No P0 local workflow defect was found; existing external P1 launch blockers remain material.

## Automated acceptance

| Check | Actual result and evidence |
| --- | --- |
| Full backend Pytest | **358 passed**, zero failed, **88.42s**, two upstream Starlette/Authlib httpx deprecation warnings; [log](evidence/phase17/backend-tests.log) |
| Frontend Vitest | **12 passed**, four files, 3.14s; [log](evidence/phase17/frontend-tests.log) |
| App TypeScript / Vite build | Passed through `tsc -b && vite build`; [log](evidence/phase17/frontend-build.log) |
| Browser TypeScript | Passed, also repeated by browser command; [log](evidence/phase17/browser-types.log) |
| Ruff lint/format | Passed, **80 files** formatted; [lint](evidence/phase17/ruff-lint.log), [format](evidence/phase17/ruff-format.log) |
| Prettier / pip check | Passed; [Prettier](evidence/phase17/prettier.log), [pip](evidence/phase17/pip-check.log) |
| JavaScript advisory scan | Zero known vulnerabilities, 180 dependency entries in audit metadata; [native npm report](evidence/phase17/npm-audit.json) |
| Python advisory scan | 38 pinned dependencies, zero known vulnerabilities; [native report](evidence/phase17/python-audit.json). Audit-only temporary environment emitted a Windows path-redirection warning; scan succeeded |
| Migration/security/mocked AI | Executed within all358 tests: disposable upgrade/check/down/up, pre-existing hash/payload preservation, SQLite FK/rollback, ownership/quotas/concurrency/replay/CSRF/body/host/session and structured-provider/schema/failure/injection/version-conflict cases |
| SQLite backup/restore | Passed disposable head0008 fixture: one synthetic user, two plan versions retained, source hash unchanged, restored session removed; [report](evidence/phase17/backup-restore.json) |
| Offline coach evaluation | **18 scenarios executed**, zero live attempts, zero plan writes; [report](evidence/phase17/offline-coach.json). Human semantic-quality review remains required; no live quality claim |
| PostgreSQL | **Blocked/not executed**; no Docker/server/native client or backup tools/test URL; [runtime availability](evidence/phase17/runtime.json). Offline SQL compilation is not runtime acceptance |
| Full Edge matrix | 163 passed/five calendar-fixture failures/seven intentional skips; initial report preserved. All five failures resolved by UTC test-fixture correction; no application behavior change |
| Final Edge Phase11 recheck | **15 passed**, zero failed/skipped,68.38s, explicit native exit0; [report](evidence/phase17/edge-phase11-final.json). Combined original/focused evidence accepts168 of175 scheduled combinations, with seven intentional skips; no single green full rerun is claimed |
| Chromium journey smoke | **Four passed**, zero failed/skipped,36.83s, native exit0; [report](evidence/phase17/chromium-smoke-results.json). Two runtimes share Blink, not independent engine coverage |
| Release manifest | Dirty-source refusal exercised; final clean-source manifest generated after commit/tag and frontend build. Source/lock/build/evidence SHA256 hashes, revision and tag are recorded; no actual image or signed supply-chain attestation |

Commands, environment and safe reproduction instructions are in [TESTING](TESTING.md#phase-17-commands-and-environment). Full browser acceptance and its actual final totals are in [the browser report](PHASE17_BROWSER_QA.md) and native [results](evidence/phase17/browser-results.json). Viewport PDF inspection passed five reports/18 pages with nonblank text and no text outside20pt safe margins; desktop/mobile UI screenshots and one rendered nutrition page were visually inspected. This is not a physical printer/device or manual screen-reader test.

## Real infrastructure, AI, professional and rights gates

No authorized remote staging target was available. PostgreSQL/native restore, runtime least privilege, TLS/reverse proxy, actual IdP/MFA/recovery, secret injection, container build/scan/digests, external monitoring/alert delivery, encrypted offhost backup and measured RPO/RTO remain **unverified release blockers**. Local multiuser tests cannot close those gates. No bounded live-model test was authorized/configured for execution; actual model quality/latency/billing and deployed budgets remain unverified. Offline mode remains functional.

All four expert packs remain unsigned; no actual specialist feedback was supplied/found, so there is no professional approval. All31 recommendation methods remain independently unvalidated. Exact scope/population/contact/injury/nutrition claims need qualified review and documented correction/retest.

Eleven original fighter records lack established redistribution rights; eight attributed Wikipedia adaptations carry CC-BY-SA obligations. Public release packaging must resolve/exclude unresolved content without deleting internal data. Production runtime metadata gates do not clear the original files still in source/build context. USDA CC0 terms were reopened; food provenance/certification uncertainty stays explicit. Font license texts and icon package metadata were inspected; actual built-image SBOM/notices and legal acceptance remain pending. [Detailed security/professional/licensing assessment](PHASE17_SECURITY_LICENSING.md).

## Performance and limitations

Actual local measurements include API/readiness, nutrition generation, offline AI request handling, 1,000-check-in analytics, 1,000 synthetic fighter query/ranking and 32-request/four-account concurrency. All synthetic requests succeeded. Hardware, workload, transport, sample definitions, background contention, browser warm-load limitations and actual medians/tails are documented in [the performance report](PHASE17_PERFORMANCE.md). A roughly one-second max in the eight-worker session workload and shared SQLite counter writes require staging queueing/load investigation; no production SLA is inferred.

## Auditable release and exact next authorization

The local release commit/tag includes source, QA tools, unchanged dependency locks, reports/changelog, configuration inventory, migration/backup/deployment/rollback instructions. Generated evidence, browser artifacts, databases, exports, real `.env` and secrets remain ignored. The generated [release manifest](evidence/phase17/release-manifest.json) records clean tagged source and frontend/evidence hashes; archive it with redacted evidence privately. No remote push/public source archive/image distribution occurred. A local annotated tag is not a cryptographically signed release or owner deployment authorization.

[Launch checklist and runbooks](PHASE17_LAUNCH_RUNBOOK.md) state each verification gate, closure evidence, controlled deployment procedure and recovery sequence. Rollback is written but not staged/rehearsed: retain prior accepted immutable artifact, back up before migrations, validate compatibility, restore only to a new isolated destination when required, revoke restored sessions and reconcile deletions before traffic. Proposed RPO24h/RTO4h remain unmeasured objectives.

The next owner instruction should authorize a **named isolated private staging environment**, operator access, synthetic test scope, infrastructure changes and an explicit cost ceiling (or no-cost constraint). Arrange qualified specialist, independent security and licensing/privacy/terms reviews in parallel. After actual staging and review closure, request separate explicit authorization for the exact public target/revision/digests. Do not infer public-launch permission from Phase17, this report or the tag.
