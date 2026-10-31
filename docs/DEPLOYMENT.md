# Deployment and operations - Phase 13

**Phase 16 policy supersedes historical cutover instructions:** see [current operations and release gates](PHASE16_OPERATIONS.md). Production requires explicit identity cutover and fighter distribution review. No staging deployment was performed.

**Public production deployment is not authorized or verified.** Read [Phase 13 evidence and blockers](PHASE13_INFRASTRUCTURE.md) and [security boundaries](SECURITY.md). Local SQLite validation and mocked OIDC protocol tests do not establish PostgreSQL, real IdP, proxy/TLS, container or production readiness.

## Existing local installation

Keep this application's configuration/database separate from the original tracker. From `backend/`, after updating dependencies and building the frontend:

```powershell
..\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
..\.venv\Scripts\python.exe -m alembic current
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m alembic check
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

Current migration head: **0008**. Take a verified backup before any real migration. Normal athlete data was not migrated during Phase13 QA. Migration preserves existing recovery/session hashes and aggregate payloads; new identity metadata is additive. Legacy session creation timestamps are backfilled with migration time, not verified historical sign-in time. Keep `IDENTITY_MODE=local` for the existing local workflow. From frontend run `npm.cmd ci` only when installing dependencies, then `npm.cmd run build`.

## Production prerequisites and configuration

Provision only after explicit authorization. Use a dedicated PostgreSQL database, a secret manager, approved managed OIDC provider, private backend network and an established HTTPS reverse proxy. No third-party account or domain is created by these files. Copy `.env.production.example` to this project's protected `.env` or inject equivalent service environment variables. Do not commit populated secrets or reuse tracker settings.

| Setting | Contract |
| --- | --- |
| `APP_ENV=production` | Requires managed OIDC configuration, secure cookies, exact HTTPS origin/hosts; startup additionally requires PostgreSQL and current migration head |
| `DATABASE_URL` | `postgresql+psycopg://...`; least-privilege runtime role, remote `sslmode=verify-full` and appropriate CA/hostname verification |
| `PUBLIC_ORIGIN`, `ALLOWED_HOSTS`, `COOKIE_SECURE` | Exact HTTPS origin without path/trailing slash/credentials; explicit matching host, no wildcard; secure cookies true |
| `IDENTITY_MODE=oidc` | Mandatory in production; disables anonymous local registration |
| `OIDC_ISSUER`, `OIDC_CLIENT_ID`, `OIDC_CLIENT_SECRET` | Approved HTTPS issuer and confidential authorization-code client; never frontend values |
| `OIDC_STATE_SECRET` | Random private >=32-character secret, shared by all workers; state cookie is signed, HttpOnly, Lax and secure in production; rotate only with an approved plan for in-flight sign-ins |
| `ALLOW_LEGACY_RECOVERY` | Default true preserves original credentials. This path bypasses IdP MFA. Disable only after users explicitly link and operator recovery governance is approved |
| `SESSION_HOURS` | Fixed app session TTL, default24 (1-720). Local sessions are independent of ID-token lifetime; no back-channel logout |
| `API_PER_MINUTE`, `AUTH_PER_MINUTE` | Default600/10 atomic fixed-window counters per trusted observed peer; correct proxy trust and edge protection are essential |
| `AI_PER_DAY` | Default20 logical `use_ai=true` coach requests/account/UTC day, including fallbacks/failures |
| `AI_GLOBAL_DAILY`, `AI_GLOBAL_MONTHLY` | Default1000/10000 outbound-attempt reservation ceilings. Reserve2 per logical request for retry capacity. Zero disables provider-mode requests; odd ceiling remainder is unused |
| `AI_ALLOWED_MODELS` | Default `gpt-4o-mini`; configured `OPENAI_MODEL` must be allowed, otherwise labeled local fallback; no user-selected model |
| `AI_MAX_OUTPUT_TOKENS`, `AI_MAX_CONTEXT_CHARS` | Default1100 /16000; bounded settings. Entire serialized provider request <=40000 ASCII characters; no uncontrolled tool calls |
| `AI_INPUT_USD_PER_MILLION`, `AI_OUTPUT_USD_PER_MILLION` | Optional operator rates, default0/unconfigured. CLI estimates are conservative estimates, not exact billing/current pricing |
| `OPENAI_API_KEY`, `OPENAI_MODEL` | Optional server-side provider secret/model; no live provider call is required for offline features |
| `MAX_BODY_BYTES` | Default131072 for write bodies, including streamed chunks; proxy limit must be no greater |
| `RETENTION_ENABLED` | Default false; additional gate for scheduled destructive maintenance, not automatic permission to enable a job |
| `CONVERSATION_RETENTION_DAYS`, `DRAFT_RETENTION_DAYS` | Default30, used only by explicit maintenance |
| `LOG_LEVEL` | DefaultINFO; redact/disable raw proxy/server access logs and query strings |

### Managed identity setup and compatibility

Register exact callback `<PUBLIC_ORIGIN>/api/auth/oidc/callback`, authorization-code response using **GET/query mode**, S256 PKCE, signed ID tokens/JWKS, issuer/subject/audience/expiry/nonce validation and confidential client authentication. The app requests `openid`; it does not merge users by email or persist provider access/refresh tokens. Configure verified-email policy, tenant/signup restrictions, recovery and optional MFA in the IdP. Actual provider settings and sign-in must be verified in staging.

Sign-in starts at `/api/auth/oidc/login`. Existing signed-in accounts must use the explicit Settings link action: POST `/api/auth/oidc/link`, then navigate to its returned authorization URL. The callback consumes an expiring single-use DB flow, validates Authlib's state/PKCE/ID token, verifies the original linking session is still valid and binds issuer/subject to the same account. A binding owned by another account is rejected. No automatic email migration, credential rotation or record reassignment occurs.

Keep local recovery enabled during an approved migration. Do not disable it before users have linked or lose their only recovery route. Provider-only new accounts have no issued local recovery credential. Settings exposes session method/current/expiry and scoped revocation; labels do not independently identify physical devices. Local logout does not log out the IdP, and provider account suspension is not pushed into active app sessions. Verify TTL/revocation policy before any MFA-dependent deployment.

### Database and migrations

Use distinct migration/runtime roles. `deploy/roles.sql.example` illustrates grants for a fresh dedicated database; review names, passwords, ownership and existing tables before use. Set passwords interactively or through secret-managed provisioning, not committed SQL/command arguments. Apply migrations using the migration role, then switch the service URL to the restricted runtime role. Startup does not migrate automatically.

From backend with the approved migration-role URL injected:

```powershell
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m alembic check
```

Schema0008 adds identity/flow/counter tables and session metadata. A downgrade removes managed identity bindings/counters; it is not a data-neutral rollback. Prefer a rehearsed backup restore with a compatible previous artifact. Do not run destructive migrations against athlete data during testing.

## Disposable PostgreSQL gate

Docker/native PostgreSQL tools are absent here. These are **ready-to-run, unexecuted PostgreSQL instructions**, not compatibility evidence. On an authorized test host, from project root:

```powershell
docker compose -f compose.postgres-test.yml up -d --wait
$env:MMA_TEST_DATABASE_URL='postgresql+psycopg://mma_test:disposable-test-only@127.0.0.1:55432/mma_test'
.venv\Scripts\python.exe backend\tools\verify_postgres.py
docker compose -f compose.postgres-test.yml down
```

The URL must name a disposable `mma_test*` database. The tool ignores normal `DATABASE_URL`, creates a random `qa_<hex>` schema, forces test/local identity/no provider key, and removes only its own schema. It exercises migrations/check/down/up, native FK enforcement, rollback, concurrent version writes, ownership denial, approved training-plan history, export and account deletion. On a host with matching `pg_dump`/`pg_restore`, set `MMA_TEST_RESTORE=1` to add native custom-archive restore and per-table count/version checks inside the disposable schema. Passwords are passed through the child environment, not command arguments. Never set this URL to a real athlete database. Restore is opt-in and remains unverified here.

## Build, reverse proxy and HTTPS

The primary local build uses the locked frontend/backend dependencies. `deploy/Dockerfile` and `deploy/compose.production.yml` are staging recipes, not images already built here. Pin reviewed base-image digests and scan the release image in staging. Compose binds the app only to host loopback; PostgreSQL is not publicly published. Supply a private database secret, service `.env`, explicit trusted proxy peers, TLS and roles before startup. Do not run compose against a live data volume without a rollout/backup plan. The database initialization role is not the intended runtime role. Inside compose, use the `database` service hostname in the runtime connection URL; the loopback example is for a host installation.

For an authorized host deployment, from backend:

```powershell
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1 --proxy-headers --forwarded-allow-ips 127.0.0.1 --no-access-log --limit-concurrency 100 --timeout-keep-alive 5
```

`deploy/nginx.conf.example` supplies an HTTPS server block with body/time limits, no raw access logging and replaced forwarding headers. Supply real certificates/domain, validate `nginx -t`, configure renewal and verify externally. Never trust `*` forwarded peers. Container NAT may change the observed proxy peer: set the exact `FORWARDED_ALLOW_IPS`, test spoofed headers from untrusted peers and keep the listener private. A mismatch should fail HTTPS checks, not be bypassed. No CORS policy is needed for the single-origin frontend/API; cross-site writes are rejected. Strict session cookies complement origin checks, not replace authorization.

Start with one worker. Database quotas are shared and atomic, but startup reference seeding uses check/insert and should not race multiple workers on a fresh deployment; initialize once and validate multiworker behavior in staging. No DoS, capacity or multiworker certification is implied.

## Monitoring and health

`GET /api/health` is liveness/key-configuration presence, never the key. `GET /api/ready` checks DB connectivity and exact migration head, returning503 otherwise. Neither proves provider availability or scientific validity. Restrict health probes appropriately at the proxy.

From backend, `python -m app.operations` provides an operator-only CLI JSON report: migration status, aggregate HTTP-error/OIDC/AI-outcome counters, current shared budget reservations, model/token settings and configured-rate estimates. There is no public administration/metrics endpoint. Logs include route templates/status/duration; no query strings, body measurements, prompts, provider text, keys or recovery tokens are intentionally logged. Configure redacted aggregation, rotation/retention, alerts for503/5xx/auth failures429/budget exhaustion and external liveness/readiness/latency. The app does not install a monitoring service or page responders.

## Backup, restore and deletion governance

Define approved RPO/RTO, encryption, key management, off-host storage, access control and retention before production. Backups contain sensitive athlete data and recovery/identity bindings. SHA manifests detect corruption, not malicious replacement of both backup and manifest. Do not store backups in the public asset tree.

For a controlled local SQLite backup, from backend (choose a new secured destination):

```powershell
..\.venv\Scripts\python.exe tools\sqlite_backup.py .\mma.db <new-secured-backup.db>
..\.venv\Scripts\python.exe tools\sqlite_backup.py <backup.db> <new-mma_restore_rehearsal.db> --restore-rehearsal
```

Use actual paths rather than literal angle-bracket placeholders. The source opens read-only and uses SQLite's online backup API. Integrity/FK/count checks and a SHA-256 manifest are produced; restore requires that manifest, a new destination named `mma_restore_*`, and invalidates restored sessions/unfinished OIDC flows. It never overwrites the existing database. Coordinate a quiet window for count consistency. `python tools/verify_sqlite_restore.py` runs a synthetic isolated rehearsal without any normal athlete data.

For PostgreSQL use native `pg_dump --format=custom` / `pg_restore` with secret-managed connection environment, authenticated encrypted storage and a fresh isolated restore target. Do not place credentials on command lines. The disposable verification tool's optional restore gate is not a backup service. Reconcile deleted accounts against a separately protected deletion ledger before restored data is reachable; old backups can resurrect deleted records and recovery credentials. Invalidate sessions, verify plans/ownership/counts/migrations and document restore duration before switching a service connection. No production restore, encryption policy or RPO/RTO has been verified here.

## Retention schedule

`python -m app.maintenance` defaults to dry run. `--apply` is an explicit manual delete; `--scheduled --apply` additionally refuses unless `RETENTION_ENABLED=true`. Counts/category audit logs contain no athlete IDs. Only expired sessions/quotas/OIDC flows and old conversations/drafts are eligible. Profiles, plans, nutrition, workout/check-in history, proposals and identity bindings are protected from age pruning; account deletion removes owned records/identity bindings/sessions transactionally.

`deploy/mma-retention.service` / `.timer` are not installed/enabled. They default to a daily randomized dry run under a restricted service account. Review working paths/service identity/environment and policy before installation. Do not add `--apply` or enable destructive retention without operator approval. Backups, exports, logs and deleted-account restoration require separate governance.

## Rollout and rollback gates

1. Confirm PostgreSQL runtime/restore, live IdP recovery/MFA/linking/key rotation, exact TLS/proxy/cookies/hosts/origin, least privilege and encrypted backup recovery in isolated staging.
2. Pin/scan the build, approve secrets/retention/deletion policies, set provider project spend controls and monitoring/incident response.
3. Take/verify a pre-migration backup; apply migrations with the separate role; check readiness and same-account/cross-account smoke tests on the approved artifact.
4. On failure, keep public traffic closed, preserve evidence and restore a verified backup into a separate target with a compatible artifact. Reconcile deletions and invalidate sessions before cutover. Do not blindly downgrade or overwrite production data.
5. Obtain explicit authorization before public exposure, new accounts/infrastructure costs or destructive scheduled jobs. This phase authorizes none of those operations.


## Phase14 release acceptance

The [current acceptance report](PHASE14_ACCEPTANCE.md), [feature matrix](PHASE14_FEATURE_MATRIX.md), [known limitations](KNOWN_LIMITATIONS.md), [user guide](USER_GUIDE.md) and [AI configuration guide](AI_CONFIGURATION.md) consolidate the release. Current schema head is0008. Historical results above retain their phase-specific context; Phase14 evidence supersedes release totals. No public deployment, live AI, real IdP or PostgreSQL runtime verification is claimed. Source validation rechecks bundled schemas/provenance and nutrient completeness; it does not reverify current fighter facts online.
