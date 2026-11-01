# Phase 24 - container triage and isolated candidate verification

Date: 2026-11-01. Branch `phase18-isolated-staging`; starting HEAD `43f5eadf05af909ec2c3ca6df4cf19624f0ebeac`. Existing uncommitted Phase 23 work was preserved. Original tag `v1.0.0-rc.17` still resolves to `2f43e4d66e76e921bc40d3840611c347ab9824c8`.

**Candidate verification passed; security clearance remains blocked. No existing staging container was replaced, no database cutover occurred, and no public deployment is authorized.** Original staging remains on port 18018. The final patched candidate is separately accessible at `http://127.0.0.1:18026`.

## Remediation and actual scan comparison

The current official Debian Python/PostgreSQL tags were pulled and resolve to the same baseline digests. Merely pulling those tags supplies no remediation. Supported official Alpine variants were evaluated instead, with immutable base digests. Locked Python dependencies install as binary wheels; no compiler/source dependency upgrade was introduced.

| Image | Before findings | Final findings | Critical | High | Other final findings |
| --- | ---: | ---: | ---: | ---: | --- |
| Application | 56 | 1 | 0 | 0 | 1 unspecified musl discrepancy |
| PostgreSQL | 124 | 12 | 0 | 1 | 5 medium, 5 low, 1 unspecified |

[Machine-readable comparison](evidence/phase24/scan-comparison.json). Counts are scanner findings, not independently confirmed exploits. Original staging still has its original findings: these results belong to new candidate artifacts only.

The application recipe `deploy/Dockerfile.candidate` changes only the candidate base to Python 3.14 Alpine 3.24, uses supported Alpine account creation, retains UID 10001 and pip/ensurepip removal, installs the existing lock without source builds, and includes third-party notices. Runtime inventory is 86 packages. No application feature/calculation was rewritten.

The PostgreSQL recipe `deploy/Dockerfile.postgres-candidate` uses the official PostgreSQL 18.6 Alpine 3.24 binary and entrypoint **byte-for-byte**, confirmed against the vendor image. Only libcurl 8.22.0-r0 -> 8.23.0-r0 and brotli-libs 1.2.0-r1 -> 1.2.1-r0 were upgraded from the official Alpine 3.24 repository. No broad package upgrade, server recompilation or entrypoint patch was used.

The standard entrypoint invokes gosu only when started as root. The candidate always starts as the existing PostgreSQL UID 70 with correctly owned tmpfs. [Official PostgreSQL documentation supports nonroot operation, including Alpine](https://github.com/docker-library/docs/blob/master/postgres/README.md#arbitrary---user-notes). Gosu was removed, and the merged filesystem copied into a final image so the executable is absent from distributable layers as well. An initial delete-only derivative still produced Go findings from inherited layer content; this was investigated rather than suppressed. The final SPDX inventory has 73 packages and no Go/gosu packages. The original gosu was 1.19 built with Go 1.24.6 on Linux/amd64.

The first Alpine PostgreSQL candidate introduced curl/Brotli findings (8 critical/18 high overall), despite removing Go. Exact vendor package updates removed 25 findings. This is why a smaller base alone was not treated as a clean result. Intermediate candidates and their databases were preserved in separate projects; none was substituted for original staging.

## Provenance and digests

| Artifact | Immutable image digest |
| --- | --- |
| Node build input | `sha256:c86ecead9e55a5210ac1727de38a4ca840bf03dcaf34dc9749addbf383b1920c` |
| Official Python Alpine input | `sha256:eb2c62658b8d51bff0acc408504b76521d02030de56a8a3c1e830083e89b89d2` |
| Official PostgreSQL Alpine input | `sha256:10a5c69a83035ab5239f5620d708520e8b28f5aa1f2b20143e6024532edadfb5` |
| Final application `mma-phase24-app:local` | `sha256:059e833cf07c5d45b1d95bb478a5732454be380271068c357b3a19c09f038a2b` |
| Final PostgreSQL `mma-phase24-postgres-patched:local` | `sha256:2e802d1c8a48db443edd5045891003f45cae05f7fc3204622bd5f8158c4badf8` |

Server executable SHA256 is `51b088c1df230893fc90182ce286d5e7caa5020ce9c01158dab462e1ec4b619a`; unchanged official entrypoint SHA256 is `9c440299ae04a0a79d55b8bf03307036d890a40979d2fb698073c9050d4b20a5`. Registry digest verification and byte comparisons establish the observed inputs; they do not constitute independent signature or vendor approval of this custom derivative. [Runtime IDs/controls](evidence/phase24/runtime-security.json), [component evidence](evidence/phase24/component-evidence.json).

## Triage and unresolved security gates

[The triage matrix](PHASE24_TRIAGE.md) covers 72 image/finding rows and 69 distinct high/critical CVEs, including every baseline high/critical finding and new high/critical findings encountered in the Alpine evaluation. [JSON](evidence/phase24/triage-matrix.json) and [CSV](evidence/phase24/triage-matrix.csv) include installed versions, runtime locations, CNA version boundaries, vendor status, reachability, remediation, compensating controls and approval requirements. All 69 high/critical CNA records were actually retrieved from the authoritative CVE API; official Debian tracker pages, Alpine security data and vendor source were also reviewed.

The four original critical Go findings were not dismissed as speculation. The executable was identified and removed from the final candidate. CVE-2026-56857 is explicitly Windows-specific in the Go CNA record, while the original executable is Linux; other Go network/TLS reachability in a privilege helper was not assumed merely from package version metadata. The original application Perl finding matches the source package while the affected Pod::Text module is absent from a complete standard /usr module search: a likely package-level false positive pending security confirmation, not an approved exception.

Two issues still block candidate clearance:

- **CVE-2026-86140, HIGH:** libxml2 2.13.9-r2 remains in PostgreSQL. The authoritative advisory identifies an overflow before upstream 2.15.4. Current Alpine 3.24 provides no newer libxml2 package; replacing it with an arbitrary upstream build or removing a linked server dependency was rejected. SQL XML parsing works, so XML functionality is present. No application XML endpoint/arbitrary SQL tool was found, but vulnerable code reachability has not been disproven. Require a supported vendor fix/new image and retest, or explicit independent security assessment and owner-approved risk acceptance. Neither exception nor approval was granted. [Authoritative advisory](https://cveawg.mitre.org/api/cve/CVE-2026-86140).
- **CVE-2026-107891, UNSPECIFIED:** the scanner requires musl 1.2.6-r6, but current [Alpine 3.24 security data](https://secdb.alpinelinux.org/v3.24/main.json) lists the fix at the installed 1.2.6-r3; the repository's latest version is r3. The authoritative CVE API returned 404. This affects both candidates and remains an unresolved scanner/vendor-data discrepancy. It is not silently suppressed or declared a confirmed false positive.

The remaining five medium/five low PostgreSQL libxml2 findings remain in SARIF. No vulnerability exception was added. Existing staging remains unremediated by design and cannot be called secure because a parallel candidate improved.

Docker Scout 1.27.0 generated fresh local artifact SPDX/SARIF files in offline mode with a closed loopback outbound proxy; no scanner installation or paid service was used. Advisory-cache freshness is not established. Fresh CNA/vendor retrieval improves triage but does not turn the cached scanner into a comprehensive current scan. [Docker Scout offline configuration](https://docs.docker.com/scout/how-tos/configure-cli/). Fresh npm audit reported zero advisories; CycloneDX frontend SBOM contains 155 components. [Application SPDX](evidence/phase24/app.sbom.spdx.json), [PostgreSQL SPDX](evidence/phase24/postgres-patched.sbom.spdx.json), [application SARIF](evidence/phase24/app-cves.sarif), [PostgreSQL SARIF](evidence/phase24/postgres-patched-cves.sarif), [frontend SBOM](evidence/phase24/frontend.sbom.cdx.json).

## Isolation, preservation and secret handling

Final Compose project is `mma-phase24-patched`, defined in `deploy/compose.candidate.json`. Database storage is a new 512MiB tmpfs owned by UID 70, with separate socket/tmp mounts and **no shared writable source storage**. Database/application use only the new internal backend network, disjoint from Phase 18/23 networks. Only the secret-free relay also joins the new loopback bridge, publishing `127.0.0.1:18026`. PostgreSQL has no published host port.

All three final containers run nonroot (database 70, app/relay 10001), read-only, cap-drop ALL and no-new-privileges, with bounded resources and healthy readiness checks. Runtime CREATE SCHEMA/TABLE is rejected. Migrator/runtime roles have no superuser/createdb/createrole powers. Invalid Host, Origin and cross-site requests are rejected; security headers remain present. No default application egress route exists. AI key is blank and daily/monthly paid-provider budgets are zero.

New candidate credentials differ from the original; no values were printed. The new host-account preparation's protected secret directory grants only OWNER RIGHTS, SYSTEM and Administrators; app environment ACLs inherit those principals. No Everyone/Users grant or existing ACL change occurred. A first sandbox-owned preparation was unreadable by Docker; it was left untouched, and host-account files were created in a new directory. A process-only Git safe.directory setting handled differing sandbox ownership without changing global Git configuration. Original credentials and preparation files were not regenerated.

Final source checks show all four original Phase18 container IDs, images and start times unchanged; the database is running/unpaused. Original Phase 23 app/relay IDs/images remain running at 18018. Original users 4 / records 26 / fighters 8 / references 2 have identical canonical hashes; both original archive SHA256 hashes match; all 89 original context hashes and the release tag match. Operational counters may advance through existing monitoring; no claim of database byte identity is made. [Preservation evidence](evidence/phase24/preservation-final.json). Parent tracker Git diff is unchanged.

Intermediate projects `mma-phase24-candidate` (18024) and `mma-phase24-verified` (18025) remain separately preserved. No broad cleanup, original Compose reconciliation, source database stop/restart/pause, host service change or firewall change occurred. The final candidate is not a durable production database: all candidate PGDATA is disposable tmpfs.

The sanitized application artifact excludes the 11 disputed original fighter records, retains the 8 supplemental records/notices, and has no .git/.env/test source. Actual runtime assertions verified these properties. This is technical exclusion, not redistribution/licensing approval.

## Native restore, migrations and application recovery

The existing authorized synthetic `/tmp/phase21b.dump` was read from the original container without modifying it. Its SHA256 matched `5eb49d4f74d1397028ef639e956adf1768af0567b4b77b50218b1303161f57d3` (110,318 bytes). Native archive listing/restore into the final initially empty candidate succeeded in 0.413 seconds. Source and destination agree on all four canonical table counts/hashes. PostgreSQL 18.6 -> 18.6 logical restore, head 0008 verification and Alembic check passed. Four archived sessions were invalidated in the candidate only. [Final restore evidence](evidence/phase24/restore-patched-result.json).

Old Phase 21 raw fixture tokens were no longer present in the source app tmpfs; they were not invented or recovered from credentials. To exercise actual sign-in semantics, a **new candidate-only** rehearsal created two synthetic accounts with plan versions and logs, then natively backed up `mma_test_stage` and restored into the separate initially empty `mma_test_restore`. Six users/39 records/eight fighters/two reference snapshots matched by canonical hashes. Two active synthetic sessions were invalidated in the destination, old cookies returned 401, recovery sign-in worked, two plan versions per fixture remained available, and exports matched the source exactly. Source candidate record hashes remained unchanged across the rehearsal. Backup -> restore -> verified application interval was 11.285 seconds; downloads/setup are excluded. [Round-trip evidence](evidence/phase24/roundtrip-result.json). Original staging was not involved in this rehearsal. Candidate synthetic fixtures and native round-trip archive remain private; no raw cookies/recovery tokens are in evidence.

The guarded PostgreSQL verifier ran against the final patched database in its own generated disposable schema. Upgrade/downgrade/upgrade to 0008, FK constraints, transaction rollback, concurrent writes, account ownership, approved plan version history, exports, account deletion and rejected recovery after deletion passed. This was actual PostgreSQL execution, not SQLite substitution.

## Regression and browser acceptance

| Check | Actual Phase 24 result |
| --- | --- |
| Backend Pytest | **388 passed**, two upstream deprecation warnings, 92.16s |
| Frontend Vitest | **12 passed** |
| TypeScript app/browser checks | Passed |
| Ruff / changed Python format check / Prettier | Passed |
| Vite production build | Passed |
| Guarded PostgreSQL verifier | Passed on final patched candidate |
| Real Edge -> patched PostgreSQL | **10 passed**, five widths 1440/1920/768/390/375 |
| Container security assertions | Passed; vulnerability clearance remains blocked |
| npm audit | Zero advisories |

The full backend suite ran in the Windows project virtual environment. The actual Alpine artifacts were exercised by the PostgreSQL verifier, native recovery, readiness/security assertions and real Edge workflows; a full Pytest run inside the sanitized artifact was not performed.

The initial full backend invocation from project root yielded 386 passes/two migration subprocess failures because those tests require backend working directory. Corrected invocation from `backend/` passed all 388; no application change concealed the harness error. A reused fixture script also initially failed BOM decoding before making requests; explicit UTF-8 decoding fixed the candidate-only harness.

`frontend/playwright.candidate.config.ts` fixes the final endpoint at 18026 and starts no SQLite server. Journey persistence assertions explicitly select `mma-phase24-patched-database-1`; an endpoint allowlist prevents an unknown target silently selecting the original database. Security tests derive the configured base URL rather than hard-coding 18018. The complete synthetic journey covers onboarding/measurements, comparisons, training, exercise logging, nutrition, progress, revisions/approval, exports, account deletion, ownership and Host/Origin protections. [Final browser results](evidence/phase24/browser-results.json), [five viewport screenshots](evidence/phase24/final), [regression summary](evidence/phase24/regression-summary.json). Earlier intermediate candidate browser results also passed but are not substituted for final artifact acceptance.

## Proposed cutover and rollback - NOT EXECUTED

1. Resolve libxml2 and musl advisory discrepancies; obtain independent security review and any explicit owner risk decision. Verify data licensing, professional review, private TLS/identity, durable monitoring/backups and other existing external gates. No blanket exception is proposed.
2. Keep original staging running. Verify a newly approved immutable app/PG image pair and separate storage/secrets/network. Rehearse a fresh logical backup/restore using the exact migration/schema and native tooling. Validate representative collations, encodings, extensions and larger histories: glibc -> musl changes can affect sorting/locale behavior and need more coverage than this small synthetic archive. Do not attach an old writable PGDATA directory to the candidate.
3. Define an owner-approved write-freeze/read-only window, take a final backup, restore to a new target, compare canonical counts/hashes/versions and invalidate restored sessions. Run isolated smoke/browser/security checks, then seek explicit approval for the specific ingress/application/database cutover. No existing container is replaced as part of this report.
4. After approval only, change the intended local route/configuration to the verified target and monitor errors/readiness. Preserve original containers and archives. Before any new writes, rollback can restore the original route; after new writes, freeze and reconcile/export those writes before rollback to avoid losing data. Do not simply point users at a stale database.
5. Document the acceptance window, data reconciliation, backup retention and exact owner-approved retirement procedure. Do not run Compose down/prune/remove-orphans or delete original tmpfs/archive containers. Future production work needs separate authorization.

## Decision

Phase 24 delivered verified isolated candidate images, a complete high/critical triage matrix, SBOM/scans, native recovery evidence, real PostgreSQL/browser acceptance and a proposed controlled transition plan. **No cutover, automatic exception, production readiness declaration or public launch occurred.** Outstanding candidate gates are libxml2 remediation, the musl advisory discrepancy and current comprehensive security review, plus the unchanged external licensing/professional/identity/TLS/monitoring/owner launch requirements.
