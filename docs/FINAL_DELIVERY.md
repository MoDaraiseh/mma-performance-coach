# Final delivery and owner handoff — 4 November 2026

**Handed off with explicit launch blockers. Local candidate acceptance passed; security clearance is blocked. Replacement of existing staging and public deployment are not authorized.** No risk exception, independent approval, final tag, cutover or publication was made. Earlier numbered reports are historical snapshots; this document is the authoritative delivery record.

## Delivered capabilities

Athlete onboarding and measurements; physical/style analysis and source-backed fighter comparisons; reviewed training and nutrition plans; exercise, workload, adherence and progress history; preview/approval of revisions; account ownership/deletion, recovery and session controls; private JSON/CSV/print exports; bounded optional AI budgets; migrations, readiness and local monitoring. Schema is `0008`. Qualified medical, nutrition, coaching, security, legal and content-rights reviews remain external requirements. AI provider access stays disabled in staging (blank key, zero budgets).

## Source, artifacts and preservation

Tested application source: branch `phase18-isolated-staging`, revision `d89b8d188803c8aa08238ac2c16d5c514cbafa10`. Working tree was clean at entry. Handoff changes are documentation, a sanitized build-context helper and a browser report-path override; no runtime application, dependency, database image or recovery implementation changed. They are committed as a handoff update without changing the tested application source revision.

Original tag `v1.0.0-rc.17` remains `2f43e4d66e76e921bc40d3840611c347ab9824c8`. No final tag was created.

| Artifact | Immutable input digest / local image ID |
| --- | --- |
| Node build input | `sha256:c86ecead9e55a5210ac1727de38a4ca840bf03dcaf34dc9749addbf383b1920c` |
| Python Alpine input | `sha256:eb2c62658b8d51bff0acc408504b76521d02030de56a8a3c1e830083e89b89d2` |
| PostgreSQL Alpine input | `sha256:10a5c69a83035ab5239f5620d708520e8b28f5aa1f2b20143e6024532edadfb5` |
| `mma-phase24-app:local` | `sha256:059e833cf07c5d45b1d95bb478a5732454be380271068c357b3a19c09f038a2b` |
| `mma-phase24-postgres-patched:local` | `sha256:2e802d1c8a48db443edd5045891003f45cae05f7fc3204622bd5f8158c4badf8` |

Local image IDs are content identities, not published registry manifests or signatures. Candidate packages remain PostgreSQL 18.6, libxml2 2.13.9-r2, musl 1.2.6-r3, libcurl 8.23.0-r0 and brotli-libs 1.2.1-r0. Server/entrypoint hashes still match Phase 24. No rebuild was justified by an available supported libxml2 fix.

Fresh preservation probes verified original container IDs/images/start times, unpaused database, disjoint candidate networks, all 89 original context hashes, both native archive hashes and canonical source counts/hashes (users 4, records 26, fighters 8, references 2). No original container was stopped, recreated, replaced or upgraded. Candidate database ID is `7e2d3b6c31f9136bed0a856d42c8793cd80af9beb821b4830785e48ab9d883c6`. Full sanitized identities, mounts, ports and controls are in [runtime evidence](evidence/phase25/runtime-security.json) and [preservation evidence](evidence/phase25/preservation-final.json).

## Actual final acceptance

| Check executed 4 November | Result / evidence |
| --- | --- |
| Backend Pytest, cwd `backend/` | 382 passed; six fixture setup errors from inaccessible pre-existing host temp directory. Only those six rerun with a new project-local `--basetemp`: 6 passed. All 388 cases passed across the two runs; two upstream deprecation warnings. Not a single uninterrupted 388-pass run. |
| Frontend Vitest | 12 passed |
| Application and browser TypeScript | Passed; browser check repeated after report-path edit |
| Ruff | Backend passed; new helper lint/format passed |
| Prettier | Existing source/tools/Vite config passed; changed browser config passed |
| Production build | Passed |
| Guarded real PostgreSQL verifier | Passed in separate temporary QA container on candidate network, generated disposable schema; migrations, FK, rollback, concurrency, versioning, exports, deletion |
| Real Edge to candidate PostgreSQL | Initial 9 passed/1 failed due to concurrent outage test; only interrupted tablet journey rerun: 1 passed. Ten unique cases passed across five widths; no SQLite server or browser traces. [Initial](evidence/phase25/browser-results.json), [retry](evidence/phase25/browser-retry.json) |
| Runtime security assertions | Passed: nonroot, read-only, drop ALL, no-new-privileges, internal database network/no published DB port, Host/Origin/cross-site rejection, headers, least-privilege application role |
| Bounded candidate outage and monitoring | Health 200 in 0.077s; readiness 503 in 3.044s; before/during/after monitor samples passed and readiness recovered. Only exact candidate DB paused; unpause in `finally`. [Evidence](evidence/phase25/outage.json) |
| Fresh image SPDX SBOMs | Both generated locally with Scout 1.27.0 |
| Image vulnerability scans | Both attempted offline; exit 1, login required, no new vulnerability result. Prior SARIF counts remain historical. Advisory-cache freshness unverified. |
| npm audit / CycloneDX | Zero advisories; fresh frontend SBOM |
| Python pip-audit | Zero known vulnerabilities in pinned lock; installed tool only, no installation |
| Native restore/session recovery | Reused unchanged Phase 24 evidence, not rerun: [round trip](evidence/phase24/roundtrip-result.json), [restore](evidence/phase24/restore-patched-result.json). Same DB image/configuration/recovery code; native restore, session invalidation, recovery sign-in, plan versions and exports passed historically. |

Raw local execution records are in `.qa-runtime/phase25/` (acceptance, PostgreSQL verifier, pytest retry, browser logs, scan diagnostics, advisory recipes/patch, audits). Sanitized shareable copies are in `docs/evidence/phase25/`; evidence is intentionally Git-ignored and must be transferred separately if needed. [Acceptance summary](evidence/phase25/acceptance-summary.json), [evidence checksums](evidence/phase25/checksums.json), and [post-acceptance preservation](evidence/phase25/preservation-after.json) consolidate the results. The final preservation comparison passed after browser/outage work. No credentials, database, dump, bearer token, private runtime file or trace is part of the source handoff. Initial sandbox Docker denial was resolved through approved host execution; candidate egress denial was preserved and vendor data retrieved on the host.

## Security dispositions and decision table

| Item | Current evidence and disposition | Effect / required action |
| --- | --- | --- |
| Local functional acceptance | Checks above passed on isolated synthetic candidate | Local evaluation verified; does not confer security clearance |
| CVE-2026-86140, libxml2 | Installed 2.13.9-r2. Current Alpine 3.24 recipe remains r2 and secdb supplies no fix for this CVE. Upstream fix is 2.15.4; XML functionality remains linked and reachable through SQL. No supported candidate fix established. | Blocks security clearance and candidate cutover/public launch. Obtain supported vendor backport/new image, rescan and regression-test, or independent assessment and explicit owner risk decision. No acceptance granted. |
| CVE-2026-107891, musl | Vendor-backed technical resolution: Alpine secdb names installed 1.2.6-r3 as fixed; current APKBUILD includes the CVE patch and its SHA512 exactly matches the downloaded patch. Upstream advisory confirms the regcomp overflow and patch. Scanner r6 threshold is not an Alpine revision boundary. No finding suppressed. | Retain scanner discrepancy for independent security review/data correction; no blanket clean-image claim. Vendor patch evidence supports fixed status for Alpine, not independent clearance. |
| Scanner freshness | Fresh local inventories succeeded; CVE commands require login; no comprehensive fresh image scan obtained | Blocks security clearance, cutover and public launch. Security operator must provide a current trusted scan with advisory timestamp/provenance. External scanner metadata transmission must be explained before use; no paid scanning authorized. |
| Existing staging | Preserved original images/findings, untouched by candidate improvements | Local use remains owner-controlled; candidate fixes do not clear original staging |
| Licensing/professional review | Disputed original 11 fighter records technically excluded from candidate; eight supplemental records/notices retained. Redistribution and professional safety approval absent | Blocks public distribution/launch; obtain qualified rights/legal and clinical/nutrition/coaching review |
| Operations/identity | Synthetic restore verified historically; tmpfs storage, private HTTP and local monitoring only. Live IdP/MFA, private TLS, durable backup/PITR, offhost recovery, alert ownership and incident response unverified | Blocks public launch; approve and validate target-specific operations, identity, retention and recovery policy |
| Staging replacement | Not authorized | Separate explicit owner approval of exact artifacts, target, write-freeze and rollback after gates close |
| Public deployment | Not authorized | Separate explicit target/operator/budget/deployment approval after all required gates close |

Compensating controls: loopback-only ingress, isolated internal app/database network, no arbitrary SQL/XML application endpoint identified, nonroot/read-only containers, removed gosu, bounded resources, restricted roles and disabled paid AI. These reduce exposure but do not prove vulnerable paths unreachable or authorize unresolved risks. Remaining historical PostgreSQL medium/low findings stay recorded in Phase 24 SARIF.

Authoritative sources retrieved/reviewed on 4 November: [Alpine secdb](https://secdb.alpinelinux.org/v3.24/main.json), [musl package recipe](https://gitlab.alpinelinux.org/alpine/aports/-/raw/3.24-stable/main/musl/APKBUILD), [Alpine patch](https://gitlab.alpinelinux.org/alpine/aports/-/raw/3.24-stable/main/musl/CVE-2026-107891.patch), [libxml2 recipe](https://gitlab.alpinelinux.org/alpine/aports/-/raw/3.24-stable/main/libxml2/APKBUILD), [upstream musl advisory](https://www.openwall.com/lists/musl/2026/10/21/1), [Debian libxml2 tracker and upstream fix](https://security-tracker.debian.org/tracker/CVE-2026-86140). Phase 24's CVE API 404 is historical, not evidence that musl has no CVE. Patch SHA512: `df73a35b9da531021ad5b1a6aad12b9d8d69de2bed7fc91b1156d9727476ab25c0d3c2341d60488152ee8ccbddb83786e91fff950cdb177b9b04673da98fdc4e`.

## Exact local access and operation

Open preserved staging at **http://127.0.0.1:18018** or isolated synthetic candidate at **http://127.0.0.1:18026**. Both readiness endpoints returned 200 in this acceptance. Use `/api/health` for process liveness and `/api/ready` for database/schema readiness; readiness must fail during DB outage. Local HTTP is not verified production TLS. Keep recovery credentials private; synthetic candidate state can disappear when its tmpfs DB container stops.

From project root in PowerShell, Docker is installed outside PATH:

```powershell
$docker = "$env:LOCALAPPDATA/Programs/DockerDesktop/resources/bin/docker.exe"
& $docker ps --format '{{.Names}}|{{.Status}}|{{.Ports}}'
Invoke-RestMethod http://127.0.0.1:18026/api/ready
```

For an already-created, stopped candidate only, verify identities and storage first. `docker start` of the three `mma-phase24-patched-*-1` containers is a candidate-only operation; stopping a tmpfs database loses its contents, so recovery/reinitialization may be needed. Do not blindly reconcile Compose or treat a restarted empty DB as recovered. Do not use `compose down`, `prune`, `--remove-orphans`, or run original staging Compose during handoff.

For source-only local development, use the existing `run-local.cmd` after installing locked prerequisites as documented in [README](../README.md). It builds frontend, migrates the project-local SQLite database and starts port 8000; this is separate from accepted PostgreSQL candidate operation. Do not run it against original staging or use it as evidence of PostgreSQL acceptance.

Runtime secret locations (values intentionally omitted): `.qa-runtime/phase24/runtime-host/secrets/{admin,migrator,runtime}.txt`, and that directory's `postgres.env`, `migration.env`, `app-patched.env`; original preparation remains `.qa-runtime/phase18/`. Preserve protected ACLs. `deploy/compose.candidate.json` maps the candidate paths and controls; never print `docker inspect` environment/config or resolved Compose secrets into public evidence. Do not regenerate existing credentials.

Monitoring: run `python -m app.operations` inside the candidate app for a bounded current aggregate report. For continuous local collection, create a new private writable `.qa-runtime` directory on tmpfs in a separately configured monitoring container and use `python -m app.monitoring --watch --url http://127.0.0.1:8000 --output <new-private-jsonl> --samples <bounded-count> --interval 5`. The shipping app root is read-only: do not relax it to create an output directory. Rotate before the 8 MiB collector limit, retain no account content, and assign an operator; local signals do not send external notifications.

Backup/recovery: use matching PostgreSQL 18 native `pg_dump --format=custom` from the selected source to restricted private storage; verify archive hash and listing. Never commit dumps. Restore with `pg_restore --exit-on-error --no-owner --no-privileges` to a separately named, initially empty authorized database; migrate/verify head 0008, compare canonical table counts/hashes, invalidate restored sessions and test old-cookie rejection, recovery sign-in, plan history and exports before serving it. Preserve source and archive throughout. Phase 24's 11.285-second synthetic rehearsal is not an approved RTO/RPO or durable backup policy. Encryption/offhost/PITR/retention/deletion reconciliation require owner-approved operations. See [operations review](PHASE16_OPERATIONS.md) and [executed recovery detail](PHASE24_REPORT.md).

## Reproduce the candidate build inputs

The new helper creates a new sanitized context only, rejects overwrite/outside-project output and reuses the established rights exclusion/notices. From `backend/`:

```powershell
..\.venv\Scripts\python.exe -m tools.prepare_candidate_build ../.qa-runtime/rebuild-final
```

Compare every relative path and SHA256 with [FINAL_BUILD_MANIFEST.json](FINAL_BUILD_MANIFEST.json). The newly generated context matched every Phase 24 accepted-context hash; the PostgreSQL recipe is additionally included. Use `deploy/Dockerfile.candidate` from that context, never the unsanitized repository root as the application build context. Build with a new image name, e.g. from project root:

```powershell
& $docker build -f .qa-runtime/rebuild-final/deploy/Dockerfile.candidate -t mma-owner-app:review .qa-runtime/rebuild-final
& $docker build -f .qa-runtime/rebuild-final/deploy/Dockerfile.postgres-candidate -t mma-owner-postgres:review .qa-runtime/rebuild-final
```

Recipes pin base digests, lock dependencies and exact APK upgrade versions. Preserve installed immutable images and the manifest: upstream package availability is external, and rebuilding is not promised to yield byte-identical image IDs. If pinned package inputs disappear, stop rather than silently substitute versions. Rebuilds require fresh inventory/security/regression acceptance; no build or image replacement was necessary in this phase. A newly generated staging configuration must use separate project/ports/networks/storage/secrets and must never attach original PGDATA. No reproducibility command authorizes deployment.

## Proposed cutover and rollback — not executed

1. Close security, rights, professional and target operations gates; identify approved immutable artifacts, durable storage, secrets, operator and backup policy. Validate musl locale/collation/extension behavior for representative real histories before approving the Debian-to-Alpine transition.
2. Preserve original running containers. Rehearse logical restore into a separate target and verify hashes, schema, session invalidation and browser workflows. Never mount original writable PGDATA in the candidate.
3. Obtain explicit owner approval for a write-freeze window and exact target. Take a final native backup, restore separately, reconcile deletion/retention obligations, verify canonical records and rerun target smoke/security checks.
4. Obtain explicit cutover approval before changing ingress. Monitor readiness, errors and ownership/session behavior. Preserve the original route/container/archive identities.
5. Before new writes, rollback can restore the original route. After new writes, freeze and reconcile/export those writes before reverting; routing to the stale source loses data. Retirement/deletion requires separate owner authorization. Public launch is a separate decision.

## Maintenance checklist

- Check health/readiness and bounded monitor signals; assign an incident owner.
- Preserve secret ACLs; rotate through a reviewed procedure and keep AI budgets disabled unless separately authorized.
- Retain immutable images, lockfiles, sanitized manifest and private evidence; review advisories and obtain a current trusted image scan.
- Back up before migrations/changes; periodically rehearse separate-target restore, session invalidation and deletion reconciliation.
- Never stop original tmpfs/archive containers or run broad Docker cleanup; do not confuse disposable candidate storage with durable service.
- Record specialist decisions and exact staging/public deployment approvals independently. No further numbered development phase is proposed.
