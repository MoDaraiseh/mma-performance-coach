# Phase 16 operational and independent-review handoff

Prepared 2026-11-01. Automated inspection is not professional approval or a penetration test.

## Identity cutover

Local development keeps recovery credentials unchanged. Production startup now refuses legacy recovery, unacknowledged cutover, and accounts not explicitly linked to the configured issuer. Merely having an identity at another issuer does not satisfy the gate. No credential is automatically deleted, replaced or disabled.

1. Back up the database and verify a disposable restore. Inventory account access without exporting bearer credentials.
2. In an isolated migration environment, retain recovery temporarily; users explicitly sign in and link from Settings. Verify ownership with each user; never merge by email. This migration environment is not public-production approved because recovery can bypass provider MFA.
3. Verify provider MFA, recovery, lost-device handling, compromised-account response and two independent administrator recovery paths with the actual IdP. App acknowledgement does not prove these policies.
4. Run `python -m tools.release_preflight` from backend using the intended database/configuration. It reports aggregate counts only and never migrates or updates data. All users must link to the configured issuer; unresolved accounts require a separately reviewed migration decision, not silent deletion.
5. Set `ALLOW_LEGACY_RECOVERY=false` and `IDENTITY_CUTOVER_ACKNOWLEDGED=true` only after access verification. Revoke pre-cutover sessions using the established incident procedure. A production rollback must not re-enable recovery without a documented security decision.

OIDC callback now requires numeric `auth_time` within the flow's start time and current time, allowing 30 seconds clock skew. Missing, stale, future and invalid values fail before binding an identity. Existing in-flight flows lacking start time must restart. Signature, issuer, audience, expiry, nonce and PKCE remain Authlib responsibilities. Fresh authentication does not establish MFA assurance. See [OIDC Core](https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest).

## PostgreSQL gate and rehearsal

This machine has no Docker, PostgreSQL server/client executables or `MMA_TEST_DATABASE_URL`. No PostgreSQL runtime verification occurred. Existing guarded `backend/tools/verify_postgres.py` requires a disposable PostgreSQL+psycopg database named `mma_test*`, creates a random `qa_*` schema and removes only that schema. Run it before staging acceptance; retain migration upgrade/downgrade, FK, rollback, concurrent writes, isolation, plan versions, export and deletion evidence. Configure `MMA_TEST_RESTORE=1` with matching native tools to additionally exercise backup/restore. Never point it at athlete databases.

For staging, separately verify runtime-role least privilege (no superuser/CREATEDB/CREATEROLE), migration-role separation, concurrent approvals, connection exhaustion, TLS, restart recovery and full application lifecycle. The sample compose database role is bootstrap infrastructure, not evidence of least privilege. A schema-scoped test is not full-cluster recovery validation.

## Backup, retention and incident recovery

The executed SQLite rehearsal uses a disposable synthetic database, two plan versions and one login session. Integrity/FKs/head and payload counts are checked; original source bytes remain unchanged and restored sessions are invalidated. This does not establish PostgreSQL or staging recoverability.

Proposed staging objectives, pending owner approval and timed rehearsal: RPO 24 hours and RTO 4 hours. No achieved RPO/RTO is claimed. For PostgreSQL select a reviewed managed backup/PITR strategy; logical dumps alone are not an operational backup policy. See [PostgreSQL backup documentation](https://www.postgresql.org/docs/current/backup.html) and [pg_dump limitations](https://www.postgresql.org/docs/current/app-pgdump.html).

Before offhost backup: encrypt with authenticated encryption using separately controlled keys, TLS transport, access-limited storage, object versioning/retention, separate restore credentials and audit records. Approve region, processor, retention and cost first. Manifests provide corruption checks, not an authenticity signature. Store signed manifests separately if required. Reconcile deletion requests after restoring an older backup; invalidate sessions/OIDC flows before serving restored data. Do not log URLs containing database credentials. No cloud storage or encryption service was configured here.

Retention remains opt-in and dry-run first. Review counts, authorise scheduling, monitor failures and preserve approved plans/progress. Backup expiry and erasure reconciliation remain operator responsibilities. Rehearse recovery into a new isolated destination; never overwrite the live database to test recovery.

## Containers, TLS and release rollback

No container engine or staging target is available; no image build, scanner, TLS or deploy was executed. Dockerfile now accepts `NODE_IMAGE` and `PYTHON_IMAGE` build arguments: release owners must supply verified `name@sha256:...` references and record both digests, the PostgreSQL digest, source revision, SBOM and scan results. Defaults remain mutable development tags and do not satisfy the release gate. Never invent digests. Read-only filesystem, UID 10001 and capability restrictions remain in the templates.

Healthcheck polls readiness without credentials; secure production requires the trusted forwarded HTTPS header. Confirm proxy addresses, header replacement and private backend connectivity in staging. Validate certificates, host rejection, timeouts, body limits, secret injection, DB connectivity and readiness failure on schema mismatch. Run migrations once with a separate role before workers. Test rolling restart and rollback against a restored backup; destructive downgrades are not a production rollback plan. Original bundled fighter files still exist in build context: review/remove unlicensed content from distribution packaging before publishing images.

## Monitoring and alerts

HTTP monitoring now records total responses, HTTP error statuses and five fixed disjoint latency buckets (<=100/500/1000/5000ms or above). No user IDs, raw URLs, queries, bodies or tokens are counter labels. Latency ends at response headers, excludes streamed delivery and is lifetime aggregate data; it is not p95 or an SLO. A single transaction updates each response's counters; database failure logs a fixed event and does not replace the response. High traffic needs measured overhead and an external metrics collector.

Operator-only `python -m app.operations` exposes DB/migration readiness, aggregate counters, conservative AI reservations and configured rate estimates. Prices are operator supplied, not measured billing. Suggested alerts pending tuning: readiness failure immediately; 5xx >1% over 5 minutes with >=100 requests; sustained >1s latency via windowed collector; AI reservation >=80% budget; failed retention/backup job or backup age >24h. Do not claim alert delivery until configured and exercised. Provider consoles must independently cap spend. Do not expose the operator report publicly or add personal-data labels.

## Independent penetration test package

Scope: isolated staging only, synthetic accounts A/B, no paid provider calls, no production users. Reviewer must receive revision, architecture, OpenAPI schema, role matrix, migration history, safe test credentials via a separate channel and these boundaries. Test OIDC token/nonce/state/PKCE replay, issuer/audience/signature/expiry/auth_time failures, explicit linking conflicts, recovery/MFA bypass, session fixation/revocation, CSRF/origin, object ownership on all reads/exports/approvals/deletes, stale proposal races, prompt injection/tool permission, rate/body limits, log leakage, proxy spoofing and security headers. Validate dependency/image findings and backup access. Stop on cross-account data access, persistence corruption or unexpected external calls; preserve redacted reproduction evidence and notify the owner.

Report fields: reviewer name/credentials, date, exact deployed revision, scope, finding ID/severity, reproduction, impact, remediation and independent retest. Acceptance: no unresolved critical/high findings; medium risks explicitly accepted by owner; evidence of isolation and rollback. Reviewer, date, signatures and approval remain blank/pending. Automated regression tests do not satisfy this gate.

## Data distribution inventory

19 fighter records: 11 original snapshots with unresolved redistribution rights, eight attributed Wikipedia adaptations under CC-BY-SA 4.0. No comprehensive/current roster claim. Production no longer seeds bundled records; startup validates all existing fighter rows and blocks missing/unlicensed source rights or absent license references. `FIGHTER_DISTRIBUTION_REVIEWED=true` additionally requires operator review of attribution, share-alike and actual intended distribution. A metadata flag is not a legal determination. Use the existing preview/import/conflict/rollback workflow for an approved dataset; preserve internal original data and do not change rights labels without evidence. Empty fighter datasets are allowed but provide no comparisons.

55 USDA SR Legacy ingredients: CC0/public domain composition with source/version attribution; no halal certification, allergen guarantee or current market prices. [USDA licensing](https://fdc.nal.usda.gov/api-guide/#bkmk-6). 49 curated exercise entries: application guidance, qualified review pending; no imported professional approval. Maintain notices for software dependencies/fonts using their installed license texts and a generated SBOM before distributing a built image. No third-party logo, portrait or licensed paid feed has been added.
