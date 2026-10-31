# Phase 17 release notes

Version: **1.0.0-rc.17**, annotated local tag `v1.0.0-rc.17`; package/API version remains 1.0.0. Date: 2026-11-01. Internal QA candidate only, not a production release. The tag identifies exact reviewed source; it is not a signed attestation or public publication.

Implemented scope: athlete onboarding/assessment, dated division references, transparent fighter comparisons, approved twelve-week plans and per-exercise logs, fatigue/progression/reassessment, seven-day nutrition and approved substitutions, deterministic offline coaching and optional schema-constrained provider, controlled proposed actions, bounded longitudinal analytics and owned exports/deletion. See [feature acceptance matrix](PHASE17_FEATURE_MATRIX.md) for each module's complete/partial/blocked status and actual tests.

This phase adds release tooling, evidence routing and final acceptance materials; it does not rebuild working features or alter training/nutrition equations. Existing credentials, approved plans and history remain intact. The original tracker is outside this release and unchanged.

## Upgrade and artifact handling

No new migration is introduced. Existing databases must still be backed up and explicitly migrated to Alembic head **0008** using the approved one-time migration procedure; never run test reset/create_all on real data. Production additionally requires Phase 16 identity cutover and distribution review gates. Local defaults retain recovery access; production cannot accept those compatibility defaults.

After final clean commit/tag, run `..\.venv\Scripts\python.exe tools/build_release_manifest.py` from backend. This writes ignored `docs/evidence/phase17/release-manifest.json`: source revision/tag, tracked-file hashes, built frontend hashes, evidence hashes and local runtime. It does not create a Docker image, approved redistributable package, signature or registry push. Archive it and private/redacted evidence securely. Do not commit databases, real `.env`, keys, tokens, user exports or browser traces.

Node/Python dependency locks remain unchanged. Release builders must separately pin verified base-image digests, generate software/font notices and scan actual built artifacts. No such image was built here. The source includes unresolved-rights fighter files; runtime licensing gates do not make this checkout publicly distributable.

## Readiness and next step

Current readiness is **A — local release candidate** under Phase 17's scale, replacing earlier phases' B-local label without upgrading actual readiness. Public launch is not appropriate. The next appropriate exercise is owner-authorized isolated synthetic staging, once an environment, access, workload and cost ceiling are specified. PostgreSQL/IdP/MFA/TLS/proxy/secrets/container/monitoring/backup acceptance and independent professional/security/legal reviews must close before any public-launch approval request.

Read [final acceptance](PHASE17_ACCEPTANCE.md), [security/licensing](PHASE17_SECURITY_LICENSING.md), [launch/deployment/rollback runbook](PHASE17_LAUNCH_RUNBOOK.md), [browser acceptance](PHASE17_BROWSER_QA.md) and [performance](PHASE17_PERFORMANCE.md). No public deployment, live AI call or external expenditure is authorized or performed by this release.
