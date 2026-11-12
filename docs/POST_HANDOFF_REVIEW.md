# Post-handoff review — 11 November 2026

Branch `review/post-handoff-fixes`, based on the final handoff commit `7e43a1f` (`phase18-isolated-staging`). Scope: application source (backend, frontend), tests, configuration examples, deployment recipes and documentation consistency across Phases 1–24 and the final handoff.

**These are source changes made after the accepted Phase 24 candidate.** The candidate images at `127.0.0.1:18026`, their digests and [FINAL_BUILD_MANIFEST.json](FINAL_BUILD_MANIFEST.json) describe the earlier tested revision `d89b8d1`. The fixes reach staging only after a sanitized rebuild and fresh acceptance, as the [final handoff](FINAL_DELIVERY.md) requires for any rebuild. No container, database, staging environment or release tag was touched.

## Defects fixed

| # | Area | Defect | Effect before the fix | Regression test |
| --- | --- | --- | --- | --- |
| 1 | Backend dates | Check-ins, workout logs, technical achievements and the analytics window were validated against the server's `date.today()`, while the browser submits the athlete's local date. | In UTC containers, an athlete east of UTC (e.g. Dubai 00:00–04:00) was told that today's entry was in the future (HTTP 422). A just-logged session was also briefly excluded from the 7-day workload and recent-fatigue checks. | `tests/test_review_fixes.py` (fails on the old code) |
| 2 | Training UI | Overview "Sessions logged" and the Training status label used only the newest plan id, ignoring `history_plan_ids`. | After every approved continuation revision, the logged-session count dropped. A session logged as missed under the earlier version showed "Logged". | `src/Training.test.tsx` (fails on the old code) |
| 3 | AI coach | `use_ai=true` reserved the per-athlete quota and two operator budget attempts even when no `OPENAI_API_KEY` was configured. | Local installs silently consumed the shared budget. Staging (blank key, zero budgets) returned 429 "budget exhausted" instead of the offline answer. | `tests/test_hardening.py` (new test fails on the old code; existing quota test now uses a mocked provider and asserts no call after denial) |
| 4 | Database | `sqlite:///./mma.db` resolved against the launch directory. | Starting the server from anywhere other than `backend/` silently created a second empty database, and startup then failed with "no such table". Relative SQLite paths now always mean `backend/…`. | `tests/test_review_fixes.py` |
| 5 | Profile wizard | Imperial input min/max were rounded to the nearest 0.01. | A bound could convert back outside the metric limit (240 cm → 94.49 in → 240.005 cm), so the browser accepted values the API rejected. | Bounds verified numerically for every converted field |
| 6 | Middleware | `TrustedHostMiddleware` was registered first, so it ran innermost. | A request with `Host: evil.example` was rejected (400) only after writing a rate-limit row and three telemetry counters. Unexpected hosts are now rejected before any other processing. | `tests/test_review_fixes.py` (fails on the old code) |
| 7 | Shared data | `POST /api/fighter-data/refresh` was blocked only when `APP_ENV=production`. Generated staging uses `APP_ENV=test` with open self-registration. | Any visitor could create an account and reimport the shared fighter dataset (reproduced: 200 for a fresh account). New `ALLOW_USER_FIGHTER_REFRESH` setting: unset or blank means development only, and production is always blocked. The UI disables the button with an explanation, and operators run `python -m app.fighter_refresh`. | `tests/test_review_fixes.py` |
| 8 | Readiness | `/api/ready` is unauthenticated, quota-exempt and starts a database probe per call. | A public client could keep a probe running continuously. The nginx template now limits the route to loopback and private monitoring networks. A cache was rejected because it would delay the immediate 503/200 transitions the outage drill relies on. | Template change; existing readiness tests unchanged |
| 9 | Security headers | Headers and two copies of the CSP string were set in two middlewares. | A policy edit could silently diverge. There is now one `CONTENT_SECURITY_POLICY`, applied once by the outer middleware; behaviour is unchanged. | New header test passes on both the old and new code |
| 10 | Build recipe | `deploy/Dockerfile` (original staging, `compose.production.yml`) used floating base tags. | Rebuilds could silently change base images. It is now pinned to the exact digests recorded for original staging in Phase 21. | Deployment tests (`test_phase18`) pass |

## Documentation and configuration corrected

- README: one current-status section plus a dated phase history, replacing five competing "Current"/"Latest" paragraphs. It also updates the musl status to match FINAL_DELIVERY, states the database location, and explains how to run Ruff, which is not in the locked requirements.
- KNOWN_LIMITATIONS: removed the stale claims that PostgreSQL runtime and native restore were never exercised, and that no base image was digest-pinned.
- AI_CONFIGURATION: invalid model id `gpt-4 o-mini` → `gpt-4o-mini`; documented when the quota and budget apply.
- Encoding damage repaired where en dashes had become `?` (e.g. `1?500`, `1.4?2.0 g/kg`), and missing spaces restored (e.g. `original11`, `Default90-day`).
- `.env.example` now lists every setting the code reads (OIDC, release gates, AI rate estimates), as `.env.production.example` already did.

## Remaining items

| # | Status | Finding | Notes |
| --- | --- | --- | --- |
| B | Staging only | Rate limits key on the client address. The production template already passes it correctly: nginx replaces `X-Forwarded-For`, and uvicorn runs with `--proxy-headers` and a pinned `FORWARDED_ALLOW_IPS`. The loopback staging relay forwards raw TCP and cannot pass the client address, so staging users share one bucket. | Acceptable for the single-operator loopback staging. Verify forwarded-address handling on the real proxy before multi-user use. |
| F | Upstream | Starlette's test client and Authlib emit `httpx` → `httpx2` deprecation warnings from inside their own code. | Fixing it means changing locked dependencies, which would invalidate the tested set. Address it in the next reviewed dependency refresh. |
| G | Done locally | The local development database `backend/mma.db` was at Alembic revision `0002`. | It contained no users or records. It was backed up byte-for-byte to the git-ignored `backend/mma.db-backup-2026-11-11-rev0002`, migrated to `0008`, and readiness now reports ready. |

The external gates in FINAL_DELIVERY are unchanged: libxml2 CVE-2026-86140, a current trusted image scan, content rights, professional review, identity/TLS/backup operations, and staging/public approvals.

## Verification (11 November 2026, Windows, project virtual environment)

| Check | Before fixes | After fixes |
| --- | --- | --- |
| Backend pytest (cwd `backend/`) | 388 passed in one uninterrupted run | 396 passed in one uninterrupted run (8 new tests) |
| Ruff 0.17.4 check / format | Passed | Passed |
| Frontend Vitest | 12 passed | 13 passed |
| TypeScript (app and browser configs) / Prettier | Passed | Passed |
| Production build | — | Passed |

Browser, PostgreSQL and container checks were run afterwards on a rebuilt candidate; see the next section. Each new regression test was confirmed to fail on the old code and pass with the fix. Two existing assertions were updated because they encoded defects 1 and 3: `test_phase11` treated server-date + 1 as always future, and `test_phase18` expected staging to answer AI requests with 429 rather than the offline coach (it now also asserts zero provider attempts).

## Rebuilt review candidate acceptance (12 November 2026, owner-authorized)

Source: `phase18-isolated-staging` at `a86f429`, after this review was merged in PR #1.

**Build context.** A new sanitized context was generated with `tools.prepare_candidate_build`. It differs from [FINAL_BUILD_MANIFEST.json](FINAL_BUILD_MANIFEST.json) only in the 13 files this review changed: 12 modified, plus the new `backend/app/clock.py`. The rights exclusion, notices and candidate recipes are unchanged.

**Images.** Built under new names from the unchanged candidate recipes:
- `mma-review-app:local` (`sha256:2e99240dc5ef4e136e332f093b79831a2c1ef03337c40ad0ecb5c1d2e258f1f6`).
- `mma-review-postgres:local` (`sha256:d8dd9b00077c87c250760bc351bb5f6cb997fe6594a3af35b2ec9eee730629ec`). Its filesystem layers are identical to `mma-phase24-postgres-patched:local`; only the attestation wrapper differs. Packages are unchanged: libxml2 2.13.9-r2, musl 1.2.6-r3, libcurl 8.23.0-r0, brotli-libs 1.2.1-r0.

**Isolation.** The candidate ran as a separate Compose project, `mma-review`, at `http://127.0.0.1:18027`. It had an internal database network, a tmpfs database and newly generated credentials. No original staging or Phase 22–24 container, image, network or database was started, stopped or modified. All of those containers were already stopped, because Docker Desktop was not running at the start.

| Check | Result |
| --- | --- |
| Guarded PostgreSQL verifier, run in a temporary container on the review network | Passed: migrations, foreign keys, rollback, concurrency, versioning, exports, deletion |
| Runtime security assertions | Passed: non-root user, read-only filesystem, all capabilities dropped, no-new-privileges, internal database network with no published database port, Host/Origin/cross-site rejection, security headers, least-privilege database role, gosu absent, entrypoint hash matches |
| Fixes checked live through the ingress | Passed: bad Host returns 400; fighter refresh returns 403 and `refresh_allowed=false`; AI with no key answers offline (200, never 429); a date that is "today" at UTC+14 is accepted and the next day returns 422; security headers present, no HSTS over HTTP |
| Real Edge browser journey and security, 5 widths | 10 passed, 0 failed, in a single run |
| Bounded outage drill | Health 200 in 0.05 s; readiness 503 in 3.03 s while the database was paused; monitor samples passed; readiness recovered after unpause |
| SPDX SBOMs, app and PostgreSQL | Generated |
| Image vulnerability scan | Obtained after the owner logged in; see the next section |
| npm audit / pip-audit | 0 vulnerabilities / 0 known vulnerabilities (dependency lock files unchanged) |

Raw records are in the git-ignored `.qa-runtime/review-acceptance/` (including `acceptance-summary.json`). The browser specs were run from a temporary copy retargeted to port 18027, so the committed specs were not edited.

### Current image vulnerability scan (Docker Scout, 12 November 2026, authenticated)

Images were scanned against current advisory data. The installed packages are byte-identical to Phase 24; every additional finding comes from advisories published since the Phase 24 scan on 1 November.

| Image | Findings | New since Phase 24 |
| --- | --- | --- |
| `mma-review-app:local` | 3: zlib 1.3.2-r1 (CVE-2026-4738, critical 9.4), sqlite-libs 3.53.4-r0 (CVE-2026-119586, high 8.5), musl 1.2.6-r3 (CVE-2026-107891, high) | zlib, sqlite |
| `mma-review-postgres:local` | 38 across zlib (1, critical), krb5-libs (21: 7 high, 8 medium, 6 unscored), libxslt (4: 2 high), libxml2 (11, including CVE-2026-86140 high) and musl (1) | 26 (zlib, krb5, libxslt) |

Alpine 3.24 fix availability, checked against the live `v3.24/main` index:

| Package | Installed | Fix in Alpine 3.24 |
| --- | --- | --- |
| zlib | 1.3.2-r1 | **1.4-r0 available** |
| krb5-libs | 1.22.2-r1 | **1.22.3-r0 available** |
| libxslt | 1.1.43-r3 | **1.1.43-r4 available** |
| libxml2 | 2.13.9-r2 | None (unchanged; CVE-2026-86140 blocker stands) |
| sqlite-libs | 3.53.4-r0 | None |
| musl | 1.2.6-r3 | Scanner threshold r6; vendor-fixed in r3 per the existing FINAL_DELIVERY disposition |

The scanner-freshness gate now has a current trusted scan, and that scan is **not clean**. Clearing it requires pinning the three available Alpine fixes in the candidate recipes, rebuilding, rescanning and re-running acceptance. libxml2 and sqlite need either a vendor fix or an explicit owner risk decision. Raw SARIF is in `.qa-runtime/review-acceptance/`.

This acceptance covers functional behaviour only. It does not clear the security, rights, professional-review or operations gates. It also does not authorize replacing staging or deploying publicly.
