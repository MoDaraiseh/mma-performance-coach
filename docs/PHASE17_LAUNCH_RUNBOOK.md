# Phase 17 launch checklist, deployment and rollback runbooks

2026-11-01. **Do not deploy from this checklist alone.** Current category is **A: local release candidate** under Phase 17's scale. Earlier B-local labels used a different scale. A private staging verification exercise is the next appropriate activity once an owner-selected isolated environment and access are authorized; this artifact is not yet accepted as staging-ready.

## Launch checklist

| Item | Actual status | Closure evidence required |
| --- | --- | --- |
| Domain/hosting | Unverified, no target selected | Owner-approved account, region, domain, operator access and budget |
| HTTPS certificate/reverse proxy | Unverified template | Real certificate/renewal test, host rejection, TLS and forwarded-header trust results |
| PostgreSQL/least-privilege roles | Blocked locally | Disposable runtime suite plus runtime/migration role separation, TLS and connection limits |
| Database migration | Verified SQLite/offline SQL only | Real PostgreSQL upgrade/rollback rehearsal and approved migration job; head 0008 |
| Backup/restore | Synthetic SQLite passed | Encrypted offhost backup, separately controlled key, PostgreSQL restore/deletion reconciliation, timed and approved RPO/RTO |
| IdP/MFA/recovery | Mocked only | Real tenant configuration, fresh login, linking, MFA/lost-device/recovery tests, explicit cutover |
| Secrets | Configuration validation tested | Secret-manager/injection audit, rotation, no credentials in logs/image/client |
| Monitoring | Aggregate code tested | Private collector, alert routing and actual readiness/error/budget/backup failure exercise |
| Rate/body/origin/ownership controls | Local regression verified | Proxy/edge and deployment multiuser/abuse tests with approved synthetic users |
| AI budgets/quality | Mocked plus offline verified | If enabled: explicit bounded live-call/cost authorization, project budget/rate controls, model evaluation; otherwise keep provider disabled |
| Privacy policy | Missing owner-approved publication | Data controller/contact, hosting/processors/regions, retention/backup erasure/export and incident procedures reviewed for intended users |
| Terms of service | Missing owner-approved publication | Jurisdiction/audience, acceptable use, safety/competition boundaries, complaints and legal review |
| User-data deletion | Verified local workflow | Deployed ownership test and restored-backup erasure reconciliation |
| Licensed fighters/attribution | Blocked | Original 11 cleared or excluded from distribution; eight adaptations reviewed for attribution/share-alike; approved release data artifact |
| Nutrition provenance | USDA CC0/source/version verified | Preserve attribution and uncertainty; no false allergy/certification claims |
| Images/logos/fonts/dependencies | Source uses icons/fonts, no copied fighter photos/logos | Installed dependency/font notices and SBOM review for built artifact; no UFC endorsement/brand-rights claim |
| Training/nutrition explanations | Local safety wording tested | Specialist review of actual scopes; publish responsible limits/referrals without professional-approval claims |
| Specialist review | Pending all four packs | Signed dated scope/revision-specific findings, corrections and retests; no invented sign-offs |
| Independent security review | Pending | Scoped pentest and remediation/retest; owner acceptance of remaining risks |
| Incident response/rollback | Written, not rehearsed | Named operator and alternate, notification channel, credential revocation and timed rollback exercise |
| Release artifact | Local commit/tag/manifest planned | Verify clean tagged revision, lock/source/build/evidence hashes; pin images and scan built artifact |
| Owner authorization | **Not granted for public launch** | Subsequent explicit approval of named target, release revision/digests, audience, cost ceiling and deployment scope |

## Configuration inventory

Use `.env.production.example` as a names-only template. Keep actual secret values outside Git and reviewed evidence. App settings are validated in `backend/app/settings.py`; production defaults deliberately block startup.

| Group | Names / required decision |
| --- | --- |
| Environment/origin | APP_ENV, COOKIE_SECURE, PUBLIC_ORIGIN, ALLOWED_HOSTS, LOG_LEVEL; exact HTTPS origin/host, no wildcard |
| Database | DATABASE_URL (secret-bearing), migration head 0008; separate migration/runtime credentials and read-only backup access |
| Identity | IDENTITY_MODE, OIDC_ISSUER, OIDC_CLIENT_ID, OIDC_CLIENT_SECRET (secret), OIDC_STATE_SECRET (secret), SESSION_HOURS; authorize exact callback URI |
| Cutover | ALLOW_LEGACY_RECOVERY=false, IDENTITY_CUTOVER_ACKNOWLEDGED=true only after verified explicit linking; no automatic credential changes |
| Fighter governance | FIGHTER_DISTRIBUTION_REVIEWED, FIGHTER_LICENSED_EXPORT, FIGHTER_LICENSE_REFERENCE; validate actual rights and intended distribution |
| Abuse controls | API_PER_MINUTE, AUTH_PER_MINUTE, AI_PER_DAY, MAX_BODY_BYTES; tune against measured private workload |
| AI | OPENAI_API_KEY (secret, server only), OPENAI_MODEL, AI_ALLOWED_MODELS, AI_MAX_OUTPUT_TOKENS, AI_MAX_CONTEXT_CHARS, AI_GLOBAL_DAILY, AI_GLOBAL_MONTHLY, AI_INPUT_USD_PER_MILLION, AI_OUTPUT_USD_PER_MILLION; no live calls without additional authorization |
| Retention | RETENTION_ENABLED, CONVERSATION_RETENTION_DAYS, DRAFT_RETENTION_DAYS; dry-run/owner approval before scheduled deletion |
| Container/proxy | NODE_IMAGE, PYTHON_IMAGE, POSTGRES_IMAGE (verified digest references), POSTGRES_PASSWORD (secret bootstrap), FORWARDED_ALLOW_IPS (exact proxy peers plus loopback if using local healthcheck) |
| QA only | MMA_TEST_DATABASE_URL (disposable mma_test* only), MMA_TEST_RESTORE, MMA_QA_PHASE, PW_REPORT_FILE, PW_EVIDENCE_DIR, PW_CHANNEL; never expose test flags as a production service |

The release manifest records hashes and runtime versions, not secret values. Lockfiles: frontend/package-lock.json and backend/requirements.lock.txt. Python pins currently lack artifact hashes; immutable build dependencies/SBOM remain release gates, not implied by a clean advisory scan.

## Controlled deployment procedure — execute only after subsequent approval

1. Record approver, target/account/region, audience (private synthetic staging or public), exact annotated tag/commit, artifact digests, approved cost ceiling and named rollback operator. Confirm all relevant checklist gates and risks; stop if critical evidence is absent. Do not reuse the original tracker's services or data.
2. Verify clean source/tag and `python tools/build_release_manifest.py` output hashes from backend. The generated manifest is under ignored `docs/evidence/phase17/`. Archive it and redacted acceptance evidence securely. This internal source checkout is **not** a distribution-cleared public artifact: resolve/exclude unlicensed fighter files and validate packaging first.
3. Build using reviewed digest inputs for both base images and PostgreSQL; generate SBOM, dependency/font notices and scan actual image. Record registry digest and signature verification if configured. Do not treat default mutable tags or a Dockerfile review as this evidence.
4. Prepare private PostgreSQL, migration/runtime roles, TLS, restricted network, secret injection and trusted OIDC tenant. Confirm identity cutover with `python -m tools.release_preflight` against the intended migrated database. Empty/approved fighter datasets only; no automatic original bundle import in production. Initialize reference data once, one worker until concurrency acceptance.
5. Take and validate an encrypted backup before migrations; record source revision/schema/checksum/storage/key reference and a successful isolated restore. Never test by overwriting live athlete data. Verify erasure reconciliation and restore-session invalidation.
6. Stop writes or use an approved compatible migration window. Run `python -m alembic upgrade head` and `python -m alembic check` once using migration credentials, then revoke those privileges from the runtime. Confirm head 0008; no new schema migration is introduced by Phases 16/17. Do not run test reset/create_all against live data.
7. Deploy exact reviewed artifact with nonroot/read-only/capability restrictions. Keep backend private; terminate TLS at approved proxy, replace forwarded headers and enforce exact trust. Poll `/api/health` and `/api/ready` through the real HTTPS origin; validate container loopback healthcheck and Host/forwarded scheme configuration. Do not log callback query strings or tokens.
8. Execute approved synthetic smoke tests: sign-in/link/fresh token rejection, profile save, approved training/nutrition, proposal approve/reject/stale conflict, log/progress, export, cross-account denial, logout/revocation and synthetic account deletion. Verify persistence with fresh reads, not success banners alone. Live AI remains off unless separately authorized.
9. Exercise alert delivery, quota/error/backup failures, monitoring access, restart and rollback. Record target URL (no credentials), revision/image/DB migration identifiers, timestamps, operator and smoke/alert evidence. Stop/rollback on unsafe output, cross-account access, failed persistence or readiness.
10. Obtain acceptance for the precise deployed scope. Only actual verified production deployment permits category D. Private staging completion alone cannot imply public readiness.

## Rollback and recovery procedure — rehearsal pending

1. Declare incident; restrict traffic/writes, preserve privacy-safe logs and record affected revision/time. Notify named owner/operator. Do not delete athlete records or silently re-enable recovery/disable MFA.
2. If schema is backward compatible and data intact, restore the previously accepted immutable application image/configuration, leaving approved data/history in place. Validate compatibility before switching traffic. Never roll back to an artifact with unresolved security or licensing failures.
3. If data integrity or schema prevents application rollback, restore the verified encrypted backup into a **new isolated** database using approved credentials. Validate checksums, schema, FKs, user/plan/version/log counts and representative payloads; replay permitted subsequent writes only through a reviewed recovery process. Record actual data-loss interval.
4. Invalidate restored login sessions and OIDC flows, rotate compromised secrets and reconcile deletions since backup. Confirm account linking/cutover policy and rights metadata remain correct. Do not run an automatic Alembic downgrade as a generic data recovery method.
5. Run health/readiness, ownership, approval/versioning, export and synthetic deletion checks. Verify monitoring, backup and spending controls. Switch traffic only after operator and owner approval, retain old environment for forensics under retention policy and document actual RTO/RPO.
6. Record incident findings, affected records, notification decisions, root cause and follow-up tests. Proposed RPO24h/RTO4h remain unmeasured until rehearsal. This runbook has not been executed in staging or production.

Next owner authorization should name an isolated private staging environment/access, allowed synthetic workload, infrastructure changes and cost ceiling. Separately arrange specialist, legal and security reviews. Public deployment requires a later explicit instruction after these gates close; this request provides no such authorization.
