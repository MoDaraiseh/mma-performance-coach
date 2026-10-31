# Phase 13 — production infrastructure and security readiness

Date: 2026-10-31. **Implemented and locally verified; production deployment remains blocked on external verification.** No public deployment, paid account, infrastructure purchase, live identity-provider sign-in or live AI request was performed. Normal athlete databases, recovery hashes, approved plans and tracker files were not changed by QA.

## Delivery and evidence

| Area | Delivered / actually verified | Outstanding boundary |
| --- | --- | --- |
| PostgreSQL | Existing isolated `mma_test*`/random-schema tool expanded with ownership checks, approved plan versioning and opt-in native archive restore/table-count verification. PostgreSQL offline migration compilation remains in the passing suite. | **Not executed against PostgreSQL:** `docker`, `postgres`, `pg_ctl`, `psql`, `pg_dump` and `pg_restore` are unavailable on PATH and no `MMA_TEST_DATABASE_URL` is configured. Standard PostgreSQL/Docker install directories were also absent. [Runtime inventory](evidence/phase13/runtime.json). SQL compilation is not runtime compatibility. |
| Authentication | Authlib1.9.1 OIDC authorization-code flow, S256 PKCE, nonce, signed ID-token validation, exact issuer/subject binding, no email merges, single-use expiring server flow, shared signed state-cookie secret. Real locally signed RSA token exchanges through mocked discovery/token/JWKS HTTP transports passed. | No real tenant/client/domain, provider recovery, optional MFA, key rotation, disabled-user policy or IdP browser handoff was validated. Provider configuration is a staging gate. |
| Compatibility | Explicit authenticated linking retains account UID, all athlete records and existing recovery hash. No automatic credential replacement. Managed-only sign-in creates a separate account if no binding exists. Production disables local registration. | `ALLOW_LEGACY_RECOVERY=true` intentionally preserves existing access and bypasses provider MFA. Disable only after authorized linking/recovery migration; no automatic bulk identity migration is provided. |
| Session controls | Settings lists up to100 active sessions, creation/expiry, method label/current marker and revocation controls. Individual/other-session revocation, cross-account denial, original-link-session revocation and unchanged recovery access tested. | No verified device fingerprint, session renaming, administrative console, IdP back-channel logout or automatic propagation of provider account suspension. Local logout/revocation does not terminate IdP sessions. |
| Security | Production config requires managed identity/secure cookies/HTTPS origin/explicit hosts; production startup also requires PostgreSQL and exact migration head. Rejection responses now carry no-store/frame/MIME/CSP headers; Permissions-Policy added. Existing same-origin write checks, body limits, ownership and proxy boundaries preserved. | External TLS/proxy trust, edge abuse control, penetration review and real production infrastructure remain unverified. CSP still permits inline styles for charts. |
| AI controls | Shared atomic UTC-day/calendar-month outbound-attempt reservations (two per logical AI request), existing per-account quota, model allowlist, configurable output/context limits, full-request ASCII-size cap, configured-rate cost estimates. Parallel and month-boundary tests pass. Offline coaching stays available after429. | Reservations are conservative capacity accounting, not actual billing. No spend reconciliation or live provider pricing measured; operator must enforce independent provider project limits. |
| Monitoring | Privacy-minimized route/status/duration logs including rejections, shared HTTP-error/AI-outcome/OIDC counters, migration-aware `/api/ready`, operator-only CLI report showing budget reservations and configured estimates. | No monitoring service, paging, log collector, dashboard or incident-response team installed. Aggregate counters are not a full observability platform. |
| Backup/restore | Online SQLite backup, integrity/FK/count checks, SHA-256 manifest verification, new-file-only restore rehearsal, restored-session/flow invalidation. Synthetic user and two plan versions preserved; source file unchanged. [Evidence](evidence/phase13/backup-restore.json). | Not an encrypted off-host production backup; SHA is not authenticity/signature protection. PostgreSQL archive restore and deletion-ledger reconciliation remain staging gates. |
| Retention | Audited dry-run/apply output; expired OIDC flows included. Timer/service templates default to dry run; destructive scheduled invocation also requires `RETENTION_ENABLED=true`. Protected athlete/history/identity categories stay out of age-based pruning. | No timer/task installed or enabled. Operators must approve retention, log/backup expiry, secure storage and account-deletion governance separately. |
| Deployment | Docker build recipe, private-only compose port, nginx HTTPS example, separate-role SQL example, disabled retention templates and updated environment/runbook instructions. | Docker/nginx/systemd not executed here. Base-image digest pinning, secret manager, TLS certificates, least-privilege grants and rollout rehearsals need staging verification. |

## Changes and root causes

1. Token-only identity was unsuitable as the sole production path. Managed OIDC is now mandatory in production configuration, with explicit issuer/subject linking rather than guessed email ownership. Local profiles/recovery credentials remain compatible and unchanged.
2. Session expiry existed without visibility/revocation UI. Owned derived session handles now support scoped revocation; handles are not session credentials. Link initiation is a same-origin authenticated POST returning a validated authorization URL, followed by top-level navigation. This avoids external form redirects conflicting with strict `form-action 'self'` CSP.
3. Account quotas alone could not cap aggregate provider traffic. Two-period atomic reservations now prevent parallel callers from oversubscribing the configured global ceilings, including retry capacity. Both increments commit together; denied requests do not partially update another period. Reservations are never refunded, even if a call fails or no call is needed.
4. Readiness only proved a simple DB query and error responses bypassed headers/logging. Readiness now compares Alembic head; an outer response layer records redacted timing/status and adds security headers to rejections too. Settings validation hides input values in startup errors to avoid secret disclosure.
5. Backup guidance lacked an executable local rehearsal. New tools refuse overwrites, verify the source and backup manifest, preserve versioned records and invalidate restored sessions. The first rehearsal exposed Python SQLite context managers leaving Windows handles open: explicit connection closing fixes the issue; the final rehearsal exits successfully.
6. The first session browser run found five axe failures because “Revoke session” was not a contiguous part of the “Revoke current session” accessible name. “Revoke session (current)” fixes the label while preserving its meaning. Final scans pass.

Migration **0008** adds external identities, short-lived OIDC flows, session creation/method metadata and aggregate operator counters. Legacy recovery/session hashes and aggregate payloads are preserved. A dedicated up/down/up regression verifies this. Downgrading deletes new identity bindings/counters and is not the preferred production rollback; keep a verified backup and follow the runbook. No normal database was migrated during this task.

7. The inherited PostgreSQL verifier protected its normal entry point but exposed an internal `--probe` shortcut without the same disposable database/schema check. The child mode now requires the generated `mma_test*` database, exact random-schema search path and internal schema marker before importing the API or opening a connection. Negative tests verify refusal of normal SQLite and production PostgreSQL URLs.
8. SQLite session timestamps lost their UTC offset on serialization and could be interpreted as local wall time. Session metadata now serializes explicit UTC offsets; the final focused identity regression verifies both timestamps.

## Automated results

- Baseline: **308 backend tests passed**.
- Full updated backend: **328 passed**. Twenty new cases cover signed OIDC claims/PKCE/state/replay, insecure discovery rejection, explicit linking/conflicts/revoked source sessions, session ownership, production mode, legacy recovery switch, atomic parallel/calendar-month budgets, readiness, headers, migration preservation and disposable backup/restore. Existing plan approval/version, security, analytics and nutrition tests remain passing.
- Frontend: **12 passed**. App/browser TypeScript, Vite, Prettier, Ruff lint/format and `pip check` pass. New runtime dependencies are pinned in the lock file. Two upstream deprecation warnings remain: Starlette and Authlib currently use the installed `httpx` compatibility path. No new dependency advisory scan or independent security review is claimed.
- Final focused Edge: **25 passed, zero failed/skipped**, all five widths1440/1920/768/390/375. Fifteen new cases cover sessions, mocked configured-link navigation and the managed-login migration explanation; ten existing security cases cover expiry, exports, canceled deletion, deletion and invalidated sessions. Five Settings axe scans returned zero violations; document overflow checks passed. [Browser results](evidence/phase13/browser-results.json), [mobile screenshot](evidence/phase13/mobile-375-phase13-sessions.png), [desktop screenshot](evidence/phase13/desktop-1440-phase13-sessions.png). The browser identity-provider pages are explicitly mocked; it is not live SSO validation.
- Synthetic SQLite restore rehearsal: passed, exact plan versions preserved, source unchanged, sessions removed. No real athlete backup or restore was performed.
- PostgreSQL runtime/native restore, container build, nginx/systemd activation, real HTTPS, provider MFA/recovery and public deployment: **not performed**.

## Performance observations

Windows/Python3.14 local disposable SQLite databases; in-process FastAPI test client, not HTTP network or production PostgreSQL. API measurements use20 sequential samples per operation plus32 session requests across8 threads. History fixture:1,000 dated check-ins plus1,000 generic versioned records. Separate fighter fixture:1,000 explicitly synthetic records, **not verified fighter coverage**. These are local observations, not capacity/SLA commitments.

| Operation | Actual result |
| --- | --- |
| Indexed latest aggregate | median0.50ms, p95 0.62ms |
| 1,000-event analytics summary | median59.28ms, p95 92.52ms |
| Paginated history | median17.61ms, p95 19.29ms |
| 32 concurrent session requests /8 threads | All200; median60.81ms, maximum385.60ms |
| Synthetic1,000-fighter search page | median15.77ms;2 queries/operation |
| Synthetic manual lookup | median0.96ms;1 query/operation |
| Synthetic ranking | median205.70ms;2 queries/operation |
| Concurrent AI reservations | 20 parallel requests /8 threads, configured daily ceiling6 outbound attempts: exactly3 reservations accepted and17 denied |

[API measurements](evidence/phase13/api-performance.json), [fighter measurements](evidence/phase13/fighter-performance.json). No application-level athlete-data cache was added; requests requery current rows and existing source/version signatures still reject stale plans. Authlib caches trusted provider metadata/keys through its integration; real key-rotation behavior requires provider staging tests. Provider concurrency tests use mocks/reservations, not paid API load.

## Mandatory production gates

1. Execute the disposable PostgreSQL migration/FK/rollback/ownership/concurrency/plan-version/deletion probe and optional native archive restore with compatible native tools; test the actual supported PostgreSQL version.
2. Register/configure an approved managed IdP client, exact callback, PKCE/JWKS/signing, account recovery, tenant/signup policy and optional MFA. Verify live linking, sign-in, errors, key rotation and revocation. Approve the legacy-recovery migration policy; it bypasses IdP MFA while enabled.
3. Build/scan/pin the release image and dependencies, provision least-privilege migration/runtime roles, verify remote DB TLS and secret storage, and externally exercise proxy trust/HTTPS/hosts/origin/cookies/headers. No reverse-proxy wildcard trust.
4. Establish encrypted off-host backup retention, access controls, restoration/deletion reconciliation and measured RPO/RTO; rehearse before any live recovery. Old backups can contain deleted accounts and credentials.
5. Configure provider project spend controls, operator quotas/rates, monitoring/alerts/incident response and edge abuse controls. Review subjective/medical/scientific review gates retained from Phase12.
6. Re-run full release/browser/security tests in staging, then obtain explicit authorization before public exposure or paid infrastructure use.

Source references: [Authlib web-client flow](https://docs.authlib.org/en/latest/oauth2/client/web/), [Starlette signed sessions](https://www.starlette.io/middleware/#sessionmiddleware), [OpenAI token limits/usage](https://developers.openai.com/api/docs/guides/token-counting), existing SQLAlchemy/PostgreSQL references in the deployment/security documents. The large Responses reference failed retrieval; the fetched official token-counting guide establishes that output caps include non-visible generated tokens. No model or pricing migration was introduced.
