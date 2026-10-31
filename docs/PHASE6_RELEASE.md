# Phase 6 final delivery and release assessment

Review date: **2026-10-31**. Scope is confined to `mma-performance-coach/`; original tracker source/config/data and normal MMA athlete data were not used for destructive QA. No public deployment, hosted database or paid provider call occurred.

**Readiness: verified local release candidate; not approved as public production-ready.** Real PostgreSQL, deployed TLS/proxy behavior, backup restoration, production monitoring/cost controls and independent specialist review remain gates. A working browser application and passing automated checks do not close those gaps.

## A. Implemented features

Existing onboarding, unit-aware profile persistence, deterministic assessments/weight-class references, 11-fighter explainable comparison lab, training catalog/12-week planning/per-exercise logs, fatigue/progression/reassessment, 22-ingredient seven-day nutrition/substitutions, context-aware offline/optional structured coaching, explicit approve/reject/version workflows, progress, print/export and account deletion are preserved.

Phase 6 adds independent expiring/revocable sessions, production configuration validation, trusted hosts/HTTPS/origin/cookie/header controls, shared DB API/auth quotas and per-account AI daily attempt quota, write-body limits, hidden recoverable DB errors, DB-backed readiness, SQLite FK enforcement, explicit retention tooling, PostgreSQL driver/offline SQL and disposable runtime verifier. Expired sessions clear the UI workspace. Old workout modals cannot remain attached to a newly approved plan. Indexed latest-record lookup replaces full-history deserialization.

## B. Partially implemented features

- Token-only accounts provide possession-based identity and owned data isolation; managed identity, MFA, recovery rotation and device-session management are absent.
- Production controls exist and their code paths are tested, but domain/TLS/proxy/monitoring and multiworker PostgreSQL behavior are not staged.
- Per-account AI attempts limit frequency, not money spent; no global monetary budget or production billing verification.
- Retention has tested dry-run/apply behavior but is not scheduled automatically; backups/logs/offline exports require operator policy.
- Food/fighter coverage is deliberately narrow and historical; no complete nutrition optimization or current comprehensive UFC roster.

## C. Unavailable or blocked verification

No PostgreSQL server, Docker executable or psql was available. The included opt-in schema-isolated verifier and Compose test service were not executed. PostgreSQL SQL generation and driver installation are verified; runtime compatibility is **unverified**. Other browser engines, physical devices, manual screen-reader review, real paid AI responses, public deployment, external penetration testing and actual backup restore are also unverified.

## D. Automated quality results

| Check | Result / evidence |
| --- | --- |
| Backend Pytest | **187 passed**, one existing Starlette/httpx deprecation warning; [output](evidence/phase6/pytest.txt) |
| Frontend Vitest | **10 passed**, including deferred preference refresh and stale workout modal regression |
| App/browser TypeScript | Passed |
| Vite production build | Passed; entry about 94 KB gzip, chart chunk about 99 KB gzip, analytics code split retained |
| Ruff lint / formatting | Passed for app/tests/tools/migrations |
| Prettier | Passed for frontend source, browser tests, tools and configuration |
| npm audit | **Zero known vulnerabilities** reported; [JSON](evidence/phase6/npm-audit.json) |
| Python pinned dependency audit | **Zero known vulnerabilities** across the enumerated runtime lock including PostgreSQL driver; [JSON](evidence/phase6/python-audit.json) |
| pip check | Passed, no broken requirements |
| SQLite migrations | Upgrade/check/downgrade/re-upgrade passed; pre-existing recovery hash preserved; head **0005** |
| PostgreSQL offline SQL | All migrations compile without connecting; not a runtime test |

Advisory results are a dated lookup, not proof of dependency safety. The Python audit warns that versions are pinned without artifact hashes. Initial sandbox advisory requests were blocked; authenticated tool execution then completed both lookups. No dependency was updated merely to hide an audit failure.

## E. Browser verification

The [final report](evidence/phase6/browser-results.json) records actual Edge execution at **1440, 1920, 768, 390 and 375 CSS pixels**. **88 passed, zero failed, seven intentional viewport-specific skips** in the final full rerun (5.6 minutes). All ten new Phase 6 cases and all prior workflows passed. Existing complete journeys cover account creation/onboarding/profile/assessment/divisions/matches/lab, training generation and exercise logging, nutrition/substitutions/coaching actions, preview/approval/rejection, progress/reassessment and export. Phase 6 adds expired/deleted-session recovery plus canceled and confirmed deletion through the actual UI at all five widths. Local and configured-interface provider tests are clearly labeled; configured transport is mocked.

The [initial full matrix](evidence/phase6/browser-initial.json) recorded **85 passes, three failures, seven intentional skips**. All three failures exposed one training race at desktop/tablet widths: approval persisted while a user could open the pre-refresh session; the session modal retained the old exercise object even after the calendar showed the new version. The fix disables session opening while tasks are pending and closes modal state on plan-ID change. Pending task counting also prevents nested requests from clearing busy state early. A component regression covers disabled opening and invalidation, and the existing cross-viewport substitution journey is rerun. The earlier [two-case focused run](evidence/phase6/browser-focused.json) passed export/deletion on desktop and mobile; it was not treated as a replacement for the full suite.

Browser checks include requested-viewport overflow, automated WCAG rules, keyboard/modal/focus behavior, error/retry/loading states and reduced motion. Seven intentional skips are the drawer test at three non-mobile widths and duplicate print runs at four widths. Browser results do not establish manual screen-reader accessibility or physical-device behavior. Screenshots include settings [1440](evidence/phase6/desktop-1440-phase6-settings.png), [1920](evidence/phase6/desktop-1920-phase6-settings.png), [768](evidence/phase6/tablet-768-phase6-settings.png), [390](evidence/phase6/mobile-390-phase6-settings.png), [375](evidence/phase6/mobile-375-phase6-settings.png), plus regenerated training/comparison/nutrition/coaching evidence in the same folder. Synthetic recovery credentials are dismissed before screenshots.

Four A4 reports (12 total pages) passed nonblank-text and safe-margin checks; [print results](evidence/phase6/print-checks.json) and rendered pages are retained under [evidence](evidence/phase6/): nutrition, overview, training and comparison. The mobile settings screenshot and a rendered nutrition page were visually inspected. Full histories/seven-day plans are exported as JSON; printing shows the selected day/week and opens relevant details. Margin/text checks supplement visual inspection; neither establishes scientific validity.

## F. Security findings

[Security review](SECURITY.md) records controls, root causes and remaining risks. Nine new API/security tests plus the PostgreSQL offline migration test extend the baseline 177 backend cases to 187. New cases cover distinct sessions, expiry/logout replay, deleted accounts/all sessions, FK violations, concurrent quotas, rate Retry-After, host/origin/body limits, production TLS/secure cookies/HSTS/shared-refresh authorization, AI quota, retention dry-run/preservation and failed-write rollback/error privacy. Existing ownership-negative/stale/conflicting approval tests remain passing.

No passwords are accepted or stored, so password hashing is not claimed. Recovery-token hashing protects high-entropy random credentials, not human passwords; no custom cryptographic protocol was introduced. Production shared fighter refresh is denied pending an operator administration workflow. Server API keys never enter frontend configuration. Quota counters persist across workers/restarts but need edge limits and periodic expiry cleanup. See [deployment checklist](DEPLOYMENT.md#deployment-gate-checklist).

## G. Database compatibility

SQLite runtime behavior, referential integrity, rollback, concurrent account writes/quotas, plan versioning/export/deletion and migrations are exercised on disposable data. Migration **0005** adds `login_sessions` and `rate_buckets` without rewriting profiles/plans/recovery hashes. Sessions from old cookies are intentionally not migrated: users restore with their original recovery token. Do not lose that token.

The `psycopg` driver is pinned and PostgreSQL migration SQL compiles. `tools/verify_postgres.py` provides actual future up/check/down/up, FK, rollback, concurrent monotonic versions, API demo/nutrition/export and deletion checks in a randomly named disposable schema. It refuses ordinary database names and never reads the user's normal `DATABASE_URL`. That infrastructure is not evidence of an executed PostgreSQL service. No production database, real account deletion or personal migration was performed.

## H. Sports-science and nutrition limits

[Specialist checklist](SPECIALIST_REVIEW.md) is ready for qualified MMA coaches, strength/conditioning professionals and sports dietitians. It explicitly covers exercise technique/supervision/contact, workload/progression/recovery heuristics, measured versus estimated assessments, energy/macros/portion/micronutrient adequacy, allergy/halal/product screening and clinical/competition referral. No expert has signed it off in this task. No automated result represents professional or clinical validation.

Anthropometric resemblance does not imply professional fighting ability. Subjective readiness is not diagnosis. Energy expenditure and review thresholds are estimates/heuristics. Macro-balanced bowls can be repetitive and are not a complete diet or weight-cut service. Medical and competition-specific needs require qualified professionals.

## I. Known issues and maintainability

- One existing Starlette/httpx test-client deprecation remains; tests pass with current pinned versions.
- `main.py` and `App.tsx` remain large. [Architecture review](ARCHITECTURE.md) identifies incremental router/context/page extraction; no unjustified rewrite was attempted.
- Full-history/export queries are not paginated/streamed. Startup seeding has not been tested under simultaneous multiple workers; deployment example uses one worker.
- Rate windows allow boundary bursts, IP buckets can group NAT users, and SQL quota writes add contention. No production load/capacity claim is made.
- Model text checks are defense in depth; explanations can still be wrong. No live provider efficacy/cost claim.
- No verified PostgreSQL service, external TLS/proxy, backup restore, physical devices or human specialist/security/accessibility review.

## J. Deployment readiness and operation

**Local release candidate; public production remains gated.** [Deployment guide](DEPLOYMENT.md) provides production `.env` example, same-origin HTTPS/proxy requirements, PostgreSQL setup and migration commands, local build/start commands, liveness/readiness, logs, explicit retention, backup/recovery guidance and release checklist. The original tracker is outside this deployment. No service was published or external spend incurred.

The [local benchmark](evidence/phase6/performance.json) measures 20 samples per operation. Indexed latest-version reads are materially cheaper than loading 1,000 aggregate versions. Assessment, matching/search and nutrition timings include the current rate/auth middleware. These are local single-client values, not a capacity target; no cache was added that could stale an athlete report.

## K. Recommended next enhancements

1. Execute the disposable PostgreSQL verifier and representative staging concurrency/load/restore tests.
2. Validate external TLS/host/origin/proxy trust, establish monitoring/incident response and token-identity suitability; add managed identity/MFA where needed.
3. Obtain independent security and qualified MMA/strength/dietitian review; broaden device and assistive-technology checks.
4. Add operator budget controls, retention scheduling and restore/deletion governance.
5. Expand verified licensed food/fighter coverage and nutrition adequacy/palatability, then paginate history/export and extract orchestration modules as scale warrants.

Exact local startup is in [deployment](DEPLOYMENT.md#local-startup-powershell); current automated commands are in [testing](TESTING.md). No arbitrary completion percentage is assigned.
