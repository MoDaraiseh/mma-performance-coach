# API notes — Phase 6

All endpoints are under `/api`. The authoritative machine-readable contract is `/openapi.json`; development `/docs` is interactive. Production disables `/docs` and `/redoc`. Requests/responses are JSON except static frontend files; error objects contain `error` and optional validation `details`. Cookies are same-origin. No frontend API key or broad CORS policy is required.

| Contract | Endpoints / behavior |
| --- | --- |
| Liveness / readiness | `GET /health` process status and key-configured boolean; `GET /ready` DB probe, 503 if unavailable |
| Identity | `POST /auth/register` returns recovery credential once and separate session cookie; `POST /auth/restore` accepts `{token}` and issues a new expiring cookie; `GET /auth/session`; `POST /auth/logout` revokes current session |
| Profile | `GET/PUT /profile`, `GET/PUT /profile/draft`; strict inputs, owned versioned records |
| Analysis | `GET /assessment`, `GET /exercise-catalog`, `GET /training-intelligence`, public reference/fighter reads |
| Fighters | `GET /fighters?q=...`, `POST /fighter-matches`, `POST /fighter-comparisons/{fighter_id}`, owned comparison favorites, data provenance/revisions; shared refresh denied in production |
| Training | `GET/POST /training-plans`, `GET /training-plans/history`, `GET/POST /training-sessions`; source plan/session checks prevent logs against invalid prescriptions |
| Nutrition | Catalog/settings/current/history, regeneration/substitution previews and explicit decisions; exact Phase 5 contracts in [nutrition/coach report](PHASE5_NUTRITION_COACH.md#user-workflows-and-api-contracts) |
| Coaching/reassessment | Coach conversation and whitelisted action previews, review checkpoints, revisions and approve/reject; no response alone applies edits |
| Data | `GET /export` all owned aggregate versions; `DELETE /account` transactionally removes owned records, sessions and account; cannot erase prior external backups/exports |

Status codes: **401** absent/expired/revoked/deleted session, **403** prohibited origin or production shared refresh, **404** missing owned resource, **409** stale/version/decision conflict, **413** oversized write body, **422** invalid input, **429** shared API/auth/provider-attempt quota, **503** recoverable DB/quota failure. Quota responses include `Retry-After`; fixed-window limits are configured in [deployment](DEPLOYMENT.md). Successful generated changes append versions and resolve proposals atomically. Rejections do not replace active plans.

Legacy authenticated `POST /nutrition` remains explicit manual generation for compatibility. Existing-plan app UI and all AI edits use preview/approval; the provider is never given that route as a write tool. Recovery-token possession grants full account access: no password or managed-identity flow is implied.

OpenAI configuration/transport remains the Phase 5 server-only Responses adapter with bounded schema/context/output, retry and timeout rules. Daily per-account attempts are now enforced even when a provider falls back. Invalid/unavailable provider replies use local explanations and validated local intents; no paid provider was invoked in QA. See [source/methodology notes](SOURCES.md) and [AI boundaries](PHASE5_NUTRITION_COACH.md#ai-reliability-privacy-and-cost-controls).


## Phase 8 search and governance additions

`GET /api/fighters/search` accepts bounded `q`, `category` (Men/Women), `division` (historical), `stance`, `status`, `page` and `page_size` (1?50); returns `items`, `total`, `page`, `page_size`. Legacy `/api/fighters` keeps a list response with a 50-record cap and `X-Result-Limit`; use pagination for larger datasets. `GET /api/fighter-data` includes the current coverage/field/source-rights quality report. Manual comparison uses indexed ID lookup, and matching returns v3 evidence-scaled weights/support labels.

There is **no public import/rollback endpoint**. Operator CLI and migration **0006** are documented in [Phase 8](PHASE8_FIGHTERS.md). Ordinary production-user refresh remains denied. Optional typed professional-record fields require dated scope and provenance, but the current bundle has none verified; sparse historical statistic values remain outside similarity scoring.


## Phase 10 coaching contract

Existing authenticated endpoints remain: `POST /api/coach`, `GET /api/coach`, `GET /api/coach/actions`, `POST /api/coach/actions/{id}/approve` and `/reject`. Coach requests still accept only `message` and `use_ai`; no user ID, approval or arbitrary tool arguments come from the model. Responses include context-section/omission metadata and explicit action errors. Proposals now support training, nutrition or assessment targets, canonical request permission, optional before/after week and assessment previews, and persisted saved-version metadata. Assessment approval appends `coach_assessment` without changing a plan. Duplicate/stale/tampered approvals return 409; another account's action returns 404. See [typed capability behavior](PHASE10_COACH.md). Export/account deletion include all new aggregates.


## Phase 11 analytics contract

All endpoints require the current authenticated account; ownership is never accepted from request arguments.

- `GET /api/analytics?start=YYYY-MM-DD&end=YYYY-MM-DD`: bounded summary, coverage, comparable series, workload, adherence, participation, records and current/historical report context.
- `GET /api/analytics/history?kind=checkin&page=1&page_size=10&start=...&end=...`: account-scoped paginated events; kinds also include `workout` and `technical_achievement`.
- `GET /api/analytics/export.csv?start=...&end=...`: private, no-store, streamed full-interval source metrics.
- `POST /api/analytics/schedule`: `{plan_id,start_date}`; Monday anchor must reference the current approved plan. Stale plan returns 409. Does not alter workouts.
- `POST /api/analytics/achievements`: `{date,discipline,title,notes}`; dated self-reported technical milestone, no future dates.
- Workout logs optionally accept `practices:[{discipline,minutes}]`; unique disciplines, total practice minutes cannot exceed actual duration.
- Existing progress/workout GET routes accept optional `limit` (1?500), preserving legacy array responses.

See [methodology and limits](PHASE11_ANALYTICS.md). Migration 0007 is required.


## Phase 13 authentication and operations contract

- `GET /api/auth/config`: public boolean capabilities only, no credentials. Managed mode disables local registration; legacy recovery is an explicit operator switch.
- `GET /api/auth/oidc/login`: starts configured Authlib OIDC; already-authenticated users must sign out or explicitly link.
- `POST /api/auth/oidc/link`: authenticated same-origin initiation, returns `{authorization_url}`. Frontend navigates to this trusted configured-provider URL; no identity mutation until verified callback.
- `GET /api/auth/oidc/callback`: expiring single-use server state plus Authlib state/PKCE/nonce/signed ID-token validation; issuer/subject binding. Generic errors omit provider secrets/prose. New app session issued only after persistence.
- `GET /api/auth/sessions`: up to100 active owned sessions with derived non-bearer handle, method, current marker, creation/expiry.
- `DELETE /api/auth/sessions/{handle}`: only owned session; other-user handles return404.
- `POST /api/auth/sessions/revoke-others`: preserves current session, revokes other owned sessions.
- `GET /api/ready`:503 for missing/unreachable/outdated migration state; exact operational version details are available only through the operator CLI.
- Provider-mode coach requests reserve two possible outbound attempts against shared UTC-day and calendar-month limits before invocation. Exhaustion returns429/Retry-After; offline mode remains available. No refunds or exact-billing guarantee.

Account deletion now also removes owned external identity bindings and pending linked sign-in flows. It does not delete an external provider's account, backups or offline exports. [Operational runbook](DEPLOYMENT.md).
