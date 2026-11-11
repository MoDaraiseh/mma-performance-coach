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

Browser (Playwright/Edge), PostgreSQL verifier and container checks were not re-run: they need the Docker/staging environment and owner authorization. Each new regression test was confirmed to fail on the old code and pass with the fix. Two existing assertions were updated because they encoded defects 1 and 3: `test_phase11` treated server-date + 1 as always future, and `test_phase18` expected staging to answer AI requests with 429 rather than the offline coach (it now also asserts zero provider attempts).
