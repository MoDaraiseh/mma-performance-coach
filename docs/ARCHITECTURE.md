# Architecture review — Phase 6

## Boundaries and contracts

The React/TypeScript client uses a same-origin typed JSON API. FastAPI validates Pydantic inputs; deterministic physical, division, training, progression, fighter-matching and nutrition modules produce calculations. The provider interprets bounded coaching intents and explanations only. SQLAlchemy stores owned versioned JSON aggregates with immutable plan/input snapshots; Alembic controls schema changes. Public fighter/reference snapshots and revision archives are separate from athlete data. Source-backed exercise/food catalogs remain bundled data.

`access.py` owns random session issuance and DB quotas; `settings.py` validates deployment configuration; `maintenance.py` implements explicit retention. `repository.account_write` locks the owning user row through an UPDATE before reading/writing dependent versions; the unique `(user_id, kind, version)` index is the final collision guard. Stale proposals bind exact source IDs and are revalidated before commit. No provider can invoke arbitrary writes. SQLAlchemy context managers roll back failed transactions.

Frontend analytics are already lazy-loaded: comparison, progress, training insights and chart chunks stay separate. Phase 6 preserves that structure and avoids introducing athlete-response caching. Initial entry is about 94 KB gzip; the chart chunk is about 99 KB gzip when needed. Local fonts do not require a third-party font request. These build sizes are not a measured network/LCP score.

## Reviewed modules

| Area | Evidence / conclusion |
| --- | --- |
| Onboarding/profile | Six-step strict inputs, drafts, unit conversion and persisted input versions; optional measurements remain missing rather than invented |
| Physical/divisions | Deterministic calculations and verified reference model; everyday weight is distinct from divisional limit and prospective target |
| Fighter data/matching | Provider abstraction, provenance, deterministic configurable weights, coverage/missing/stale rules; only 11 dated study snapshots, no broad live roster |
| Training/progression | Catalog, bounded availability/equipment/recovery prescription, logs and future-only adaptation; effectiveness and injury suitability require expert review |
| Nutrition | Separate calculations/data/exclusions/composition/validation/integrity; 22 historical USDA generic records; macros do not establish micronutrient completeness |
| AI | Reduced approved context, strict nullable intent, bounded transport and fallback; per-account daily attempt quota added; no global spend guarantee |
| Data | SQLite FK enforcement and atomic owned writes; PostgreSQL driver and disposable verification tool supplied, runtime still unverified |
| Auth/security | Expiring independent sessions, revocation/deletion, shared quotas, origin/host/body controls, safe errors and production configuration gate |
| Errors/UI | Loading/error states retained, 401 clears athlete workspace; workout selection blocked during pending actions and old modal closes on version replacement |

## Focused simplification and measurable change

`main.latest` previously loaded and deserialized every record version, then chose the maximum in Python. It now delegates to the existing indexed `repository.latest_record` query with descending version and `LIMIT 1`. The disposable benchmark compares both approaches with 1,000 1-KB payload versions and reports 20-sample medians/p95 in [performance.json](evidence/phase6/performance.json). It also times assessment, fighter search/matching and nutrition including TestClient/middleware overhead. These are local single-client timings, not production capacity results.

API orchestration and frontend refresh still overlap some context reads. A broad dashboard refresh concurrently reloads several independent views; it is explicit and uncached, which avoids serving stale approved plans. Busy state now counts nested/concurrent tasks rather than allowing one completed task to mark another pending action idle. Training modals are invalidated by plan ID changes. The compatibility `programs.py` reexports remain because callers/tests rely on them; replacing working modules has no clear Phase 6 benefit.

## Maintainability risks and future boundaries

`main.py` and `App.tsx` remain large orchestration files. A later refactor should extract FastAPI routers/context loaders and smaller page controllers while preserving current authorization/transaction boundaries. JSON aggregates reduce schema churn but limit relational reporting, SQL-level payload constraints and selective queries. Full history/export queries are unpaginated; benchmark sizes do not justify a caching layer, but larger accounts will need pagination/streaming and retention design. Fighter search scans 11 validated records; database search indexing is premature at this coverage.

Public-data startup seeding is idempotent for serial startup, not validated under simultaneous multiworker initialization. Use one worker until PostgreSQL/staging validation. Quota writes add DB work to reads; future high-scale deployments may use a proven shared limiter/edge service with explicit failure and privacy policies. Do not substitute an in-process-only cache/limiter that breaks cross-worker consistency.

The deployed API contract is generated from FastAPI (`/openapi.json`). [API notes](API.md), [testing](TESTING.md), [security](SECURITY.md) and [deployment](DEPLOYMENT.md) document current behavior and unverified operations.


## Phase 10 coaching additions

`coach_context.py` builds bounded, provenance-labeled current summaries; `coach_guidance.py` renders deterministic offline explanations. `coach_security.py` checks primary-request permissions independently of provider interpretations. `coach_actions.py` proposes bounded edits through existing training/nutrition/progression services. `main.py` serializes and revalidates approved writes. A `coach_assessment` record is a separate versioned snapshot, not a checkpoint or profile mutation. No migration beyond 0006 is needed. New typed intents and UI differences are detailed in [Phase 10](PHASE10_COACH.md). Fighter context reads the current validated database; free-text source biographies are omitted.


## Phase 11 analytics additions

`analytics.py` reads account-scoped indexed events and deterministic summaries; it never changes approved plans. Nullable event-date/parent metadata are maintained by `history_index.py` on writes and backfilled by migration 0007, preserving source payloads. History is SQL-paginated; CSV uses keyset pages. The dashboard explicitly reports bounded coverage and keeps current profile inputs separate from actual window baselines. See [Phase 11](PHASE11_ANALYTICS.md) for comparison rules, caps and caveats.


## Phase 13 identity and operations

`identity.py` integrates Authlib OIDC, exact issuer/subject bindings, single-use server flows and explicit authenticated linking. No provider tokens are persisted. `ExternalIdentity`, `OIDCFlow`, `OperatorCounter` and session metadata arrive in migration0008. Existing recovery credentials and athlete aggregates are not migrated to another UID automatically. `SessionSecurity.tsx` exposes owned session handles and revocation; provider navigation follows a same-origin POST initiation response.

`operations.py` supplies migration-aware readiness, aggregate counters and two-period atomic outbound-attempt reservations. Request budgets span workers; token/context/model limits remain server-side. The CLI report exposes no athlete facts or credentials. Maintenance includes expired identity flows and a disabled-by-default destructive scheduling gate. Backup/restore tools use new destinations/disposable fixtures; production restoration and deletion governance remain external operational controls. [Full Phase13 report](PHASE13_INFRASTRUCTURE.md).


## Phase14 release acceptance

The [current acceptance report](PHASE14_ACCEPTANCE.md), [feature matrix](PHASE14_FEATURE_MATRIX.md), [known limitations](KNOWN_LIMITATIONS.md), [user guide](USER_GUIDE.md) and [AI configuration guide](AI_CONFIGURATION.md) consolidate the release. Current schema head is0008. Historical results above retain their phase-specific context; Phase14 evidence supersedes release totals. No public deployment, live AI, real IdP or PostgreSQL runtime verification is claimed. Source validation rechecks bundled schemas/provenance and nutrient completeness; it does not reverify current fighter facts online.
