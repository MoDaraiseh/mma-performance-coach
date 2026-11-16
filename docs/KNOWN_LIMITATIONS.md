# Known limitations and release gates

> **Current state (11 November 2026):** the authoritative gate list is the decision table in [FINAL_DELIVERY.md](FINAL_DELIVERY.md); post-handoff fixes and open findings are in [POST_HANDOFF_REVIEW.md](POST_HANDOFF_REVIEW.md). Items below were written at Phases 15-18 and have been corrected where later phases changed them.

Phase 18 technically excludes the original 11 fighter records from its generated staging context, preserving internal source/history; whole-repository distribution remains unapproved. Staging configuration and local alerts are tested, but Docker/PostgreSQL/separate-DB restore/live IdP/TLS/external reviews remain unavailable or pending. [Current gates](PHASE18_LAUNCH_GATES.md).

Highest supported category: **A - local release candidate** under [Phase 17 acceptance](PHASE17_ACCEPTANCE.md). Earlier B-local labels are historical and use a different scale. Not staging-ready or production-ready; no deployment or paid-service authorization.

## Public source repository

The source repository has been public since November 2026. The MIT license covers the application code only, not third-party data:

- The 11 official-source fighter records in `backend/app/fighter_catalog.py` are factual profile fields (height, reach, listed weight, division and activity status) recorded on 2026-10-31 from official ufc.com athlete profiles, with a source link for each field. They include no images, biographies or fight records. No permission or license from the UFC has been obtained for them.
- The eight Wikipedia-derived records are adapted under [CC BY-SA 4.0](FIGHTER_SUPPLEMENT_LICENSE.md).
- The USDA food data is public domain (CC0); see [sources](SOURCES.md).

The gate reviews in this folder were written before the repository was public. They concern running the application as a public service and distributing release builds, and every gate they list remains open.

## Public-launch blockers

- PostgreSQL runtime, guarded migration/FK/concurrency verification and native `pg_dump`/`pg_restore` round trips were executed on the isolated synthetic staging candidate in Phases 21-24. No production database, durable storage, PITR or approved RPO/RTO exists; candidate PGDATA is disposable tmpfs.
- Managed OIDC is validated with signed-token mocked transports and mocked browser provider pages only. Real tenant policy, MFA, recovery, key rotation, back-channel logout and live account linking need staging tests. Local legacy recovery remains enabled by default. Phase 16 production startup blocks recovery bypass, unacknowledged cutover and unlinked accounts; migrate/verify access explicitly without silently changing credentials.
- Docker images, nginx/TLS, remote database roles/TLS, forwarded-header trust, secrets storage, monitoring, edge abuse controls and retention services have not been deployed/exercised. Initialize reference data with one worker; concurrent first-start seeding is not hardened.
- Original 11 fighter source records have unestablished redistribution rights. Eight additions have attributed CC BY-SA terms; the whole database is not automatically licensed for commercial redistribution.
- No independent security penetration test or sports-science/clinical approval. Four specialist packs remain blank and pending. User safety/claims and contact or competition-specific use require qualified review.
- Encrypted off-host backup retention, deletion reconciliation, operational recovery ownership and RPO/RTO need implementation and rehearsal. SQLite synthetic restoration does not establish production disaster recovery.
- No live AI evaluation or actual provider billing validation. Configure provider project spend controls and current rates before authorized use. Do not treat lexical safety filters as complete semantic protection.

## Functional coverage boundaries

19 fighter snapshots (11 men/8 women), not comprehensive/current roster coverage; stance 3, background 13, historical statistics 2, current verified professional records 0 and controlled style traits 0. Observation/review dates are not new physical measurements. Two additional secondary-source articles were reviewed in Phase 15; no live roster/statistics refresh is implied.

55 USDA SR Legacy April 2018 foods, with macros/fiber/sodium/calcium/iron/potassium; no complete micronutrient adequacy, clinical plan or verified cross-contact/halal certification. Cooking steps are simple assembly, cuisine/cost labels editorial, no monetary budget optimizer, limited meal variety and no individualized training-day calorie cycling.

49 exercises and conservative template programming. Technical ability and supervision are self-reported. No optimal-style/pro-potential prediction, individualized target fight weight, injury rehabilitation or objective anaerobic-capacity inference. Thresholds/deload/progression rules are product heuristics requiring specialist review.

Analytics uses actual available data with explicit protocol/sample limitations. Default 90-day window, maximum 3651 inclusive days; summary caps 2000 events/60 series/120 points/64 source plans; latest 3 reassessments. Narrow windows when warned. CSV streams source rows; full account JSON still loads history into memory. Personal records are selected-window comparable records, not guaranteed lifetime records. The workout form captures one discipline per log, while the API supports multiple. No destructive measurement-correction UI was added.

Browser evidence is automated installed Edge/Blink at 1440/1920/768/390/375 CSS pixels on Windows. No physical devices, other browser engines, manual screen-reader testing or exhaustive WCAG conformance claim. Printed long reports can span several pages; only the current selected training week/meal day is the detailed print view, with program history and grocery summaries as available.

Python lock pins versions without artifact hashes. The Phase 24 candidate recipes (`deploy/Dockerfile.candidate`, `deploy/Dockerfile.postgres-candidate`) pin base images by digest; the original `deploy/Dockerfile` is pinned to the Debian digests recorded for original staging in Phase 21. Upstream Starlette/Authlib httpx deprecations remain. Dependency audit results are point-in-time advisory queries, not a supply-chain guarantee. The app now has an independent local source checkpoint (d8839ce). No signed tag, remote publication or publicly deployed artifact exists; generated evidence is intentionally ignored.


Phase 15 nutrition catalog v3 invalidates older meal plans for reviewed regeneration without deleting snapshots. Fat-food replacements solve all 3 macros and can fail when no bounded portion solution exists. Exercise categories/objectives and competition intent are now explicit. See PHASE15_DELIVERY.md for current coverage and verification.
