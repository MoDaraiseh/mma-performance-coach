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

## Documentation and configuration corrected

- README: one current-status section plus a dated phase history, replacing five competing "Current"/"Latest" paragraphs. It also updates the musl status to match FINAL_DELIVERY, states the database location, and explains how to run Ruff, which is not in the locked requirements.
- KNOWN_LIMITATIONS: removed the stale claims that PostgreSQL runtime and native restore were never exercised, and that no base image was digest-pinned.
- AI_CONFIGURATION: invalid model id `gpt-4 o-mini` → `gpt-4o-mini`; documented when the quota and budget apply.
- Encoding damage repaired where en dashes had become `?` (e.g. `1?500`, `1.4?2.0 g/kg`), and missing spaces restored (e.g. `original11`, `Default90-day`).
- `.env.example` now lists every setting the code reads (OIDC, release gates, AI rate estimates), as `.env.production.example` already did.

## Open findings (not changed; need an owner decision)

| # | Severity | Finding | Recommendation |
| --- | --- | --- | --- |
| A | Medium (staging) | `POST /api/fighter-data/refresh` is blocked only when `APP_ENV=production`. Generated staging uses `APP_ENV=test` with open local registration, so any visitor who creates an account can trigger a reimport of the shared fighter dataset. Reproduced: a freshly self-registered account received 200 under the generated staging settings. | Make refresh an operator-only command or add an explicit setting, default off outside development. Changing it alters staging behaviour, so it was left for decision. |
| B | Medium (pre-launch) | Rate limits key on the TCP peer address. Behind the staging relay or any reverse proxy, all users share one bucket. The auth limit (10/min) then applies to everyone together, and one client can exhaust it for all. | Configure trusted forwarded-header handling for the chosen proxy before multi-user use. This is already listed as unexercised in KNOWN_LIMITATIONS. |
| C | Low | `/api/ready` is unauthenticated, exempt from rate limiting, and starts a Python subprocess per probe. Probes are serialized per process, so concurrent callers wait for the running one. | Cache the last result for a few seconds, or restrict readiness to the internal network at the proxy. |
| D | Low | Security headers are set in two middlewares (`security` and `operational_response`) with duplicated CSP strings. | Keep one definition to avoid drift. |
| E | Info | The original `deploy/Dockerfile` still uses floating base tags. Only the candidate recipes pin digests. | Retire it or pin it like the candidate. |
| F | Info | Starlette's test client and Authlib emit `httpx` → `httpx2` deprecation warnings. | Track upstream before the next dependency refresh. |
| G | Info | The local development database `backend/mma.db` is at Alembic revision `0002`; the code expects `0008`. | Back it up, then run `alembic upgrade head` from `backend/` before using `run-local.cmd`. Not done automatically because it is the owner's data. |

The external gates in FINAL_DELIVERY are unchanged: libxml2 CVE-2026-86140, a current trusted image scan, content rights, professional review, identity/TLS/backup operations, and staging/public approvals.

## Verification (11 November 2026, Windows, project virtual environment)

| Check | Before fixes | After fixes |
| --- | --- | --- |
| Backend pytest (cwd `backend/`) | 388 passed in one uninterrupted run | 393 passed in one uninterrupted run (5 new tests) |
| Ruff 0.17.4 check / format | Passed | Passed |
| Frontend Vitest | 12 passed | 13 passed |
| TypeScript (app and browser configs) / Prettier | Passed | Passed |
| Production build | — | Passed |

Browser (Playwright/Edge), PostgreSQL verifier and container checks were not re-run: they need the Docker/staging environment and owner authorization. Each new regression test was confirmed to fail on the old code and pass with the fix. Two existing assertions were updated because they encoded defects 1 and 3: `test_phase11` treated server-date + 1 as always future, and `test_phase18` expected staging to answer AI requests with 429 rather than the offline coach (it now also asserts zero provider attempts).
