# Phase 17 local performance and reliability report

2026-11-01. These are actual local measurements, not production SLAs, capacity certification or live-provider latency. Hardware: AMD Ryzen 7 7730U, eight cores/16 logical processors, 14,879,617,024 bytes installed RAM (about 13.86 GiB). OS: Windows 11 build 26300. Python 3.14.7, Node 24.20.0, npm 11.19.0; installed Edge/Blink 155.0.4283.45. [CPU](evidence/phase17/cpu.json), [RAM](evidence/phase17/memory.json), [runtime](evidence/phase17/runtime.json).

API measurements use FastAPI TestClient in-process HTTP transport, disposable local SQLite, synthetic demo profile, 1,000 extra 1-KB aggregate versions plus 1,000 dated check-ins. Middleware/auth/quota/monitoring/database work is included; no WAN, TLS or production PostgreSQL. API and fighter benchmark commands ran sequentially while the separate browser acceptance process was active; background host contention is uncontrolled. No benchmark accesses the athlete database. Twenty sequential samples per operation; reported p95 is nearest-rank sample 19/20, not a stable population tail estimate. Offline coach requests persist synthetic conversations; nutrition generation appends synthetic plan versions.

| Operation | Median ms | Sample p95 ms |
| --- | ---: | ---: |
| Full-history latest (comparison baseline, 1,000 versions) | 14.18 | 19.82 |
| Indexed latest (1,000 versions) | 0.58 | 1.00 |
| Athlete assessment | 25.01 | 28.56 |
| Fighter matching (19 snapshots) | 29.57 | 37.00 |
| Fighter search | 23.14 | 26.73 |
| Saved nutrition read/validation | 50.31 | 64.46 |
| Seven-day nutrition generation/persistence | 73.13 | 81.62 |
| Offline coach/context/conversation persistence | 91.05 | 134.70 |
| Analytics over 1,000 check-ins | 79.87 | 114.66 |
| Paginated history | 29.22 | 35.62 |

[Native API results](evidence/phase17/api-performance.json), [command log](evidence/phase17/api-performance.log). The old-latest comparison is a benchmark of a former full-materialization approach, not a claim that the current endpoint still uses it.

Concurrency: 32 authenticated session requests with eight workers all returned 200; median 115.47ms, max 1,034.73ms. A separate 32-request profile-read workload across four independently authenticated synthetic users/four workers all returned 200; median 71.50ms, max343.70ms. Independent account cookies were used; cross-account denial is separately asserted by the security suite. These small read workloads do not validate multiworker startup, PostgreSQL approval races, prolonged write load, connection exhaustion or failover. SQLite shared quota/counter writes can serialize requests; the one-second tail warrants staging workload/queueing measurements before setting limits.

Fighter scale fixture: **1,000 synthetic clones, not verified fighter coverage**. Ten samples per operation: paginated search median16.97ms/two SQL queries; direct lookup0.70ms/one query; full ranking199.11ms/two queries. Query count is bounded, but ranking still validates/scores the full candidate set and is not a claim of arbitrary-scale constant-time matching. [Native fighter benchmark](evidence/phase17/fighter-performance.json).

Long histories: the full backend regression executes 2,100-event behavior, checks the 2,000-event/120-point caps and truncation warning, bounded query count, paginated histories, streaming CSV, corrected/deleted records, empty/single histories and owned exports. The 1,000-check-in benchmark measures summary/page timing; full account JSON still materializes history and remains a P2 large-account limitation.

Frontend readiness is measured by `phase14.spec.ts` in the final suite at all five widths: three warm reloads per viewport, local HTTP, synthetic demo, no network/CPU throttling. Timings include Playwright polling and dashboard data/title readiness, not cold-load LCP, first-input responsiveness or a production UX budget. Native viewport sample files are in `docs/evidence/phase17/*-load-performance.json`; the final summary table below is generated after all viewports finish.

AI handling: offline timings above and mocked provider success/schema/error/deadline/retry/permission/quota cases passed in Pytest. Eighteen synthetic offline evaluation cases made zero live provider calls and zero plan writes. Live-model latency, actual usage/cost, semantic quality and deployed provider limits are **unverified**, not extrapolated from offline or mocks.

Next reliability acceptance requires owner-authorized private PostgreSQL/TLS/IdP staging, representative reads/writes and approval races, load duration/sample/percentile budgets agreed before measurement, restart and backup recovery, and actual monitoring alerts. No production SLA or achieved RPO/RTO is inferred here.


## Final five-viewport browser timing summary

Three warm samples per row; median milliseconds, including local test polling.

| Viewport | Overview ready | Progress dashboard ready |
| --- | ---: | ---: |
| desktop-1440 | 458.81 | 580.9 |
| desktop-1920 | 937.85 | 576.21 |
| tablet-768 | 447.37 | 573.62 |
| mobile-390 | 470.9 | 842.39 |
| mobile-375 | 462.6 | 895.57 |

[Native aggregate](evidence/phase17/frontend-performance-summary.json); raw samples retain navigation/load timing and exact browser version. These are not cold-load or WAN measurements.
