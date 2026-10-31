# Changelog

## 1.0.0-rc.17 — 2026-11-01

Internal local release candidate; tag `v1.0.0-rc.17`. Not an authorization to publish source, images or a service. Public distribution remains blocked by rights and external acceptance gates.

- Consolidated Phases 1–16 into an evidence-linked feature matrix, launch checklist, security/licensing assessment and controlled deployment/rollback runbooks.
- Ran final local backend/frontend/security/mocked-AI/migration/browser acceptance; actual totals and limitations are in [Phase 17 acceptance](docs/PHASE17_ACCEPTANCE.md).
- Corrected a calendar test fixture that mixed Dubai-local weekday arithmetic with UTC ISO dates, producing Sunday instead of Monday before 04:00. Initial failures and the fresh five-viewport Phase 11 recheck are retained separately.
- Added reproducible clean-source/frontend/evidence hashing for the local release manifest. Manifest generation refuses uncommitted source and sensitive/generated tracked paths.
- Extended existing performance, source-inventory, synthetic restore and print QA tools to write Phase 17 evidence without overwriting prior phase reports. Corrected a stale six-versus-eight fighter supplement count.
- Added local nutrition-generation/offline-coach timing and four-account concurrent profile-read measurements. No production capacity or live-model SLA is inferred.
- Preserved working application behavior, athlete data, approved history, offline coach and optional provider configuration. No schema change beyond head 0008; no automatic migration of an athlete database.

Release limitations: 19 dated fighter snapshots (11 unresolved original redistribution rights/eight CC-BY-SA adaptations), 55 historical USDA foods, 49 curated exercises. No live PostgreSQL/IdP/TLS/container/staging acceptance or independent professional/security approval. No public deployment or paid provider request occurred.

Prior source releases: `95651d9` (Phase 16 release policy/authentication freshness/monitoring/review handoff), `1943020` (Phase 15 curated catalog and feature refinements), `d8839ce` (independent MMA project preservation checkpoint). Historical reports retain their original evidence and terminology; Phase 17 uses category **A = local release candidate**.
