# Security review and operating boundaries

**Phase 13 supersedes the historical Phase6 control matrix below.** See [current evidence and blockers](PHASE13_INFRASTRUCTURE.md). Production now requires configured Authlib OIDC, PostgreSQL and current migrations. Explicit issuer/subject linking preserves local account/recovery ownership; no email merging. Session list/revocation, single-use flows, aggregate AI budgets and error-response headers are implemented. Legacy recovery deliberately remains available by default and bypasses IdP MFA; disable only after an authorized migration. No live-provider/TLS/proxy/penetration or production security certification is claimed.

Reviewed 2026-10-31. This is an implementation review and automated regression exercise, **not** a penetration test, compliance certification or approval for unrestricted public use.

| Area | Implemented protection | Remaining boundary |
| --- | --- | --- |
| Identity | High-entropy `secrets.token_urlsafe(48)` recovery credential, SHA-256 hash at rest; independent random HttpOnly/SameSite Strict session, fixed server expiry and revocation on logout | Local recovery remains a bearer credential; managed OIDC and session controls exist, with live provider/MFA policy unverified. No recovery-token rotation UI; stolen recovery credential grants access while legacy recovery is enabled |
| Authorization | Every athlete endpoint authenticates; owned record lookups and account write locks; stale source bindings and deterministic candidate checks | Review new endpoints with ownership-negative tests; global reference data is public study data, not per-user |
| Session lifecycle | Migration 0005 creates hashed session rows; restoration issues a distinct session; expired/deleted/logged-out sessions rejected; deletion removes all sessions | Existing pre-0005 cookies require recovery restore; session listing/revocation UI is implemented; no physical device attestation |
| Production config | Explicit HTTPS origin/hosts, secure cookies, HSTS, HTTPS rejection, TrustedHost; development-only Vite exception | Actual TLS/reverse proxy and forwarded-header trust not exercised externally |
| Browser security | Same-origin deployment, cross-site write rejection, CSP with self scripts/fonts, frame denial, MIME sniffing protection, no-store | CSP allows inline styles needed by current chart/UI library. Development API docs use FastAPI CDN/inline assets and are exempt; disabled in production |
| Abuse/cost | Shared DB atomic fixed-window per-IP API/auth limits, per-account AI request quota, Retry-After; body cap including streamed chunks | Global daily/monthly attempt reservations exist; no edge DoS defense, exact dollar billing enforcement, CAPTCHA or bot detection; boundary bursts and NAT sharing documented |
| AI | Server-only key, fixed provider HTTPS endpoint, model syntax checks, bounded context/output/deadline/retries, strict schemas and validated intents; no model write tools | Semantic explanations can still be wrong; live provider account permissions, billing and quality unverified |
| Data | Account-scoped versioned aggregates, atomic plan approvals, history preservation, FK enforcement; account export and transactional deletion | No application field encryption. Operator must provide encrypted disks/backups, database transport/access controls and retention governance |
| Retention | Explicit dry-run/apply job for expired sessions/quotas, old conversations/drafts | Not auto-scheduled. Plan/progress/history retention lasts until account deletion; backups/logs/exports need separate policies |
| Logging | Route-template/status/duration, exception type only, hidden SQL parameters; usage metadata excludes personal content | Operator must configure proxy/server logs, access controls, rotation and retention; deliberate account conversations store user text |
| Dependencies | Pinned runtime dependencies; npm audit and pip-audit reports; pip check | Advisory absence is not proof of safety; Python lock has versions without artifact hashes; reproducible OS/container supply-chain scanning remains future work |

## Bugs and root causes addressed

1. **Non-revocable sessions:** recovery tokens were the cookie credential and server checked no expiry. Separate hashed session rows now expire server-side; logout deletes that session, account deletion removes all. Recovery hashes and account data remain unchanged.
2. **SQLite referential integrity:** declaring SQLAlchemy foreign keys did not enable SQLite enforcement. Every SQLite connection now executes `PRAGMA foreign_keys=ON`; orphan-insertion regression checks this. PostgreSQL uses native constraints but awaits real execution.
3. **Unbounded repeated requests/provider attempts:** no API/auth/provider quotas existed. Atomic conditional DB counters work across connections; insert races retry once. AI quota is account-bound and checked before provider interpretation. Failed or fallback AI requests still consume quota.
4. **Production browser trust inherited development defaults:** development origin handling, cookie settings and host checks lacked a deployment gate. Settings now reject insecure production startup; HTTPS, host, origin, cookie and header tests cover the code path. Shared fighter refresh is denied to ordinary production accounts, pending an operator administration workflow.
5. **Oversized write payloads:** schemas bounded individual values but request body parsing could allocate an arbitrarily large document. Write bodies are capped before downstream JSON parsing, including chunked bodies; proxy/header/slow-client limits remain operator responsibilities.
6. **Database errors and transaction recovery:** unexpected DB failures lacked a clean client contract. SQLAlchemy failures return 503 without query/connection details; rollback tests prove partial records are absent. Existing integrity conflicts still return 409.
7. **Stale athlete panels after expired sessions:** action failures displayed an error while keeping workspace data mounted. The UI now clears athlete state and returns to account recovery on 401. Browser tests exercise deletion in another request followed by a failed export.
8. **Configuration inconsistency:** CLI/Alembic imported `db.py` without the API's `.env` loader. Database configuration now loads only this project's `.env` centrally without overriding explicit environment variables. CLI/migrations and API use the same URL.

## Review evidence and priorities

The release report links exact tests and advisory results. Session replay, expiry, account deletion, other-user denial, concurrent quotas, production TLS/cookies/origin, body size, retention dry run, rollback and hidden errors have automated checks. Existing tests cover stale/concurrent plan approvals, invalid AI output/timeouts, schema validation, nutrition arithmetic and missing fighter data.

Before public deployment: execute PostgreSQL/proxy/restore gates, decide whether bearer-token identity is suitable, add managed identity if needed, configure edge controls and incident response, and obtain independent security review. Do not claim the application is hardened against all attacks. No public deployment or paid API call was performed.

Implementation references: [Starlette middleware](https://www.starlette.io/middleware/), [SQLAlchemy SQLite constraints](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html), [SQLite FK documentation](https://www.sqlite.org/foreignkeys.html). These describe underlying mechanics, not validation of this application.


## Phase 10 coach boundaries

See [the Phase 10 report](PHASE10_COACH.md). Only the primary authenticated user request can authorize a typed capability. Stored canonical permission, account ownership, context/reassessment/workout bindings and candidate equality are checked before append-only approval. Model output cannot supply identity, approval or writes. Imported prose and user notes are untrusted; raw log/check-in notes and external biographies are not forwarded. Provider function/computer/web calls are rejected, not executed. Safety and premature-persistence claims are checked in both output text fields. Tests cover malicious output, argument tampering, other accounts, stale/rejected changes and recovery gates. These checks do not prove semantic truth or prompt-injection immunity; no independent security or live-model quality validation is claimed.


## Phase14 acceptance

328 backend tests passed, including security regressions; point-in-time npm/Python advisory scans found no known vulnerabilities. See [release evidence and gates](PHASE14_ACCEPTANCE.md). This is not external penetration testing or production security approval. Never expose this local candidate publicly before the documented infrastructure, identity, licensing and review gates.
