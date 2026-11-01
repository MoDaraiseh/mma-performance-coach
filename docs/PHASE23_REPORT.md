# Phase 23 ? local staging reliability and security verification

Date: 2026-11-01. Branch: `phase18-isolated-staging`; starting HEAD `43f5eadf05af909ec2c3ca6df4cf19624f0ebeac`. Original annotated tag `v1.0.0-rc.17` still resolves to commit `2f43e4d66e76e921bc40d3840611c347ab9824c8`.

**Local reliability checks passed. Container vulnerability clearance remains blocked. This is not production readiness or public deployment approval.** Staging remains at `http://127.0.0.1:18018` using synthetic PostgreSQL data. No production access, paid AI calls, new system software, ACL changes, host services, public endpoints or purchases were used.

## Readiness root cause and correction

Readiness used the shared SQLAlchemy engine without an end-to-end deadline. Socket waits, pool pre-ping and queries could stall while PostgreSQL was paused. Even health handlers could finish and then wait on database-backed HTTP telemetry middleware. Monitoring also attempted database aggregates before reporting availability.

`backend/app/health_probe.py` now runs a lean SQLAlchemy-only worker with NullPool, connection/statement timeouts and migration verification. The parent imposes a three-second subprocess deadline and kills/reaps a stalled child. Per-process singleflight prevents concurrent health requests spawning unlimited probes; joining callers have a bounded wait. Heavy application/provider imports were removed after concurrent probing exposed false timeouts. No secrets enter command arguments or exception responses.

`/api/health` remains independent of database connectivity. Health/readiness paths, including trailing-slash variants, bypass database telemetry and quotas. `/api/ready` returns generic HTTP 503 with Retry-After when unavailable. Unsupported slash variants retain their existing 404 behavior without database writes. Application operations collect counters/reservations only inside the bounded worker and represent unavailable metrics as unknown rather than zero.

## Monitoring and real outage

The collector has sequential bounded probes, literal loopback-only HTTP targets, redirects/proxies disabled, bounded response reads, fixed-label structured signals, and a rolling 60-second trend window. It detects application/database failure and recovery, local/OIDC authentication failure trends and denied AI quotas. Split-sample authentication failures and expired history have regression coverage. Invalid local recovery attempts now emit the fixed authentication failure counter. No notes, credentials or external notifications are collected.

A final ten-sample real pause/unpause test targeted only PostgreSQL ID `96ae890980a38c79ecbae27389cae84d0374b117e9772a5362072cf4cbdb8a05`, with unpause in a finally block:

| Check | Actual result |
| --- | --- |
| Liveness during outage | HTTP 200, 0.033 seconds |
| Readiness during outage | HTTP 503, 2.68 seconds; generic dependency error |
| Alert signals | application_not_ready, database_not_ready, authentication_failures, ai_quota_denials |
| Recovery | HTTP 200; database_recovered and application_readiness_recovered |
| Collector | 10 samples, exit 0; no external notifications |
| Database | Same ID/start time/image; running and unpaused afterward |

[Outage evidence](evidence/phase23/outage-result.json), [collector snapshots](evidence/phase23/collector.jsonl).

A continuous collector was started inside the existing candidate container using `python -m app.monitoring --watch --url http://127.0.0.1:8000 --output /app/.qa-runtime/continuous.jsonl --interval 5`; two initial successful samples were verified. It uses private tmpfs, exclusive new output files, bounded history and an 8 MiB output guard. Output is volatile and requires manual rotation/restart when capped; this is not durable hosted monitoring or external paging. No Windows service was installed.

## Preservation and runtime

[Before](evidence/phase23/before.json) and [after](evidence/phase23/after.json) capture exact labels, IDs, storage, hashes and network evidence. All four original Phase18 containers retain their IDs, images and start times, including the completed migration container. PostgreSQL was never stopped, restarted or recreated. Original app/restore containers remain running. PostgreSQL PID1 runs as UID 999 and retains its original writable storage/capabilities; the stronger application restrictions below must not be attributed to the database container.

Users (4), records (26), fighter snapshots (8) and reference snapshots (2) have identical before/after content hashes. Both existing synthetic dump SHA256 hashes match. All 89 original prepared context hashes match. Operational counters intentionally changed during synthetic alert tests; no claim of byte-identical database storage is made. No new backup/restore rehearsal was performed in Phase23; archive preservation supplements the earlier successful separate-database restore.

A parallel candidate was built from a new sanitized 90-file context, preserving original preparation and credentials. Final image for both candidate and relay is `sha256:36dc7e726f059284027e41c779917e08ae87977938a51c35fa1ccad30e4b35a8`. Exact final IDs are in the after snapshot. The candidate uses a distinct DNS alias to avoid collision with the original Compose `app` alias. The prior Phase22 relay is stopped and retained for ingress-only rollback, as is an earlier stopped candidate. No broad cleanup occurred. An early cutover guard rolled back safely; final cutover waited for three successful readiness responses and browser acceptance passed afterward.

## Container security, SBOM and findings

Both active application/relay containers run as UID 10001, read-only, all capabilities dropped, no-new-privileges, with memory/PID limits. Application networking is the existing internal isolated network, with no default route or published app port. Only the relay publishes `127.0.0.1:18018`; its upstream is fixed, and it has no database/AI secret environment. Application temporary writes use restricted tmpfs. Runtime database CREATE SCHEMA/TABLE attempts are rejected. Invalid Host returns 400 and untrusted/cross-site POST returns 403; security headers are present. AI key is blank and global daily/monthly budgets are zero. [Actual security probe](evidence/phase23/security-result.json).

The actual final image contains an empty excluded-original-fighter catalog and eight sanitized supplemental records; .git, .env and backend tests are absent and the font notice is present. Technical exclusion is not fighter-data licensing approval.

The locked dependency installation passed `pip check` during build. Unneeded pip and ensurepip were then removed from the runtime image; absence was verified in the final container. Compared with the first build, this removed 19 packages and 9 scanner findings, including 6 high findings. No host tooling was removed.

Installed Docker Scout 1.27.0 produced local SPDX SBOMs and SARIF scans using offline mode and a closed loopback outbound proxy. No scanner installation or paid service was used. [Docker documents offline configuration](https://docs.docker.com/scout/how-tos/configure-cli/), [SBOM generation](https://docs.docker.com/scout/how-tos/view-create-sboms/) and [local artifact selection](https://docs.docker.com/scout/how-tos/artifact-types/). Advisory-cache freshness was not established; results are not a current comprehensive vulnerability clearance.

| Artifact | Packages/components | Critical | High | Medium | Low |
| --- | ---: | ---: | ---: | ---: | ---: |
| Final application/relay image | 187 | 0 | 8 | 4 | 44 |
| Preserved PostgreSQL image | 210 | 4 | 34 | 31 | 55 |
| Frontend CycloneDX SBOM | 180 | ? | ? | ? | ? |

Fresh npm audit reported zero advisories. Remaining application high findings concern OS packages including util-linux, glibc, perl and zlib; the cached report marks these not fixed. PostgreSQL's four critical findings identify Go 1.24.6 in `/usr/local/bin/gosu`: CVE-2026-78663, CVE-2026-39821, CVE-2026-56857 and CVE-2025-68121. These are scanner findings, not proof of four exploitable PostgreSQL server vulnerabilities. They nevertheless require vendor/reachability triage and remediation. The database image was deliberately not upgraded or restarted under the preservation constraint. A future patched candidate database should be validated by separate restore before an authorized cutover.

[Scan summary](evidence/phase23/scan-summary.json), [application SARIF](evidence/phase23/offline-cves.sarif), [PostgreSQL SARIF](evidence/phase23/postgres-cves.sarif), [application SPDX](evidence/phase23/app.sbom.spdx.json), [PostgreSQL SPDX](evidence/phase23/postgres.sbom.spdx.json), [frontend CycloneDX](evidence/phase23/frontend.sbom.cdx.json). Counts are scanner advisory findings, not independently verified unique exploits. Scan exit 0 means completion, not a clean security gate.

## Ingress review

The Phase22 relay already bounds connections and upstream/idle waits, supports streaming and half-close, uses a fixed internal upstream, and avoids request-content logging. No relay implementation defect was established, so its code was preserved. Added regression tests verify excess-connection rejection/capacity recovery and upstream failure without private logging, alongside existing large-payload/half-close coverage. The failure test allows the relay's existing five-second connection deadline on Windows. Host validation remains enforced by the application. No arbitrary destination proxy or external exposure was added.

## Executed regression

| Check | Final actual result |
| --- | --- |
| Backend Pytest | 388 passed, 2 upstream warnings, 94.31 seconds |
| Frontend Vitest | 12 passed |
| Real Edge to PostgreSQL | 10 passed at 1440/1920/768/390/375px |
| TypeScript / Ruff / changed Python formatting / Prettier | Passed |
| Vite production build | Passed |
| Guarded PostgreSQL verifier, final image | Passed: migration head 0008, down/up, FK, rollback, concurrent writes, ownership, plan versions, exports, deletion and recovery denial |
| Real outage / recovery / local alerts | Passed |
| Final image security assertions | Passed; vulnerability clearance separately blocked |

Browser execution used the live staging endpoint and PostgreSQL, not SQLite or mocked APIs. [Browser results](evidence/phase23/browser-results.json) and five viewport screenshots are in [the evidence directory](evidence/phase23). Focused tests cover process deadlines/singleflight, malformed worker output, outage-safe metrics, health middleware, rolling trends, local URL validation and ingress behavior. [Regression summary](evidence/phase23/regression-summary.json). No earlier-phase result is counted as a newly executed backup/TLS/live-provider test.

## Staging runbook and gate matrix

`deploy/compose.reliability.json` is a separate project with candidate/ingress only and no database service. Its default port 18020 is for canary testing; the active cutover uses process environment `PHASE23_INGRESS_PORT=18018`. Preserve that value for any approved reconciliation. Do not run broad Compose down, remove-orphans, prune or recreate database commands. Rollback is ingress-only: stop the specific Phase23 ingress, then start the retained Phase22 relay ID; do not touch PostgreSQL. The current candidate remains healthy and active.

| Gate | Phase23 status |
| --- | --- |
| Bounded readiness and independent liveness | Passed locally |
| Continuous collector and real outage/recovery | Passed locally; bounded volatile retention/manual rotation |
| PostgreSQL integrity, migration and browser workflows | Passed locally |
| Original containers, records, archives, context and tag preserved | Passed |
| Nonroot application/relay, network/secret controls | Passed locally |
| SBOM and installed local scanner execution | Completed; cached-data limitation |
| Vulnerability remediation/clearance | **Blocked: app 8 high; PostgreSQL 4 critical/34 high** |
| Private TLS/reverse-proxy secure-cookie acceptance | Not executed in this phase; separate scope/gate remains |
| Live IdP/account recovery, independent expert/security review | External gates remain pending |
| Fighter-data redistribution/licensing | Not approved by technical exclusion |
| Production monitoring/incident infrastructure and owner release approval | Pending; local collector is not a substitute |
| Public deployment | Unauthorized; not performed |

Next priorities are vendor-reviewed vulnerability remediation with a separately restored database candidate, durable approved monitoring/rotation, private TLS acceptance, and the existing independent licensing/professional/security/identity release reviews. Automated local tests do not constitute independent expert approval.
