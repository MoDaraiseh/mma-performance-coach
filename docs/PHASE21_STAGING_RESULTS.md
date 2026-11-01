# Phase 21 isolated staging execution results

Date: 2026-11-01. **Local PostgreSQL/container verification substantially exercised; host-loopback staging acceptance remains blocked. Public deployment is unauthorized.** This report supersedes earlier permission-blocked status in the [Phase 21 history](PHASE21_REPORT.md).

## Authorization and preservation

The owner confirmed personal use, approved WSL2/per-user Docker setup, then explicitly approved inheritable ReadAndExecute entries for their current Windows SID on `.qa-runtime/phase18` and its protected `secrets` directory. The protected `backups` directory was explicitly excluded.

Branch: `phase18-isolated-staging`. Starting HEAD: `1fa14995f2d289b9e1ea40ffa431641b581ce24b`; existing documentation edits were retained. Original release `v1.0.0-rc.17` still resolves to `2f43e4d66e76e921bc40d3840611c347ab9824c8`. No application source, original tracker, normal athlete database, original synthetic credential value or preparation file was modified. All **89 prepared context hashes** matched before and after execution.

## Actual ACL changes

Current host account was verified as `IWA2024\darai_qtguapt`, SID `S-1-5-21-3645006260-4010894991-199683691-1009`. Before mutation, recursive inspection confirmed only the two already identified protected children, `secrets` and `backups`.

| Directory | Actual result |
| --- | --- |
| `.qa-runtime/phase18` | One explicit Allow entry added for that SID: `(OI)(CI)(RX)` |
| `.qa-runtime/phase18/secrets` | Same single explicit inheritable entry added |
| `.qa-runtime/phase18/backups` | No mutation; original three entries, owner and protection preserved |

Both approved directories changed from three to four ACL entries. Final comparison confirms **all previous entries, ownership and inheritance-protection settings preserved**. No Everyone/Users grant, write/FullControl grant, ownership change or reset occurred. Normal descendants inherited the approved rule; no additional protected child needed a separate change.

The first PowerShell `Set-Acl` attempt failed with SeSecurityPrivilege unavailable. DACL-only `icacls /grant` succeeded for the two exact directories, one file processed each. Host-session file-open checks then passed for all four environment files, preparation metadata and all three synthetic password files; no content was displayed. Compose `config --quiet` passed. Evidence: ignored `.qa-runtime/phase21/acl-applied.json` and `acl-final-proof.json`.

## Runtime and build evidence

The installed runtime remains WSL **3.0.3.0**, Docker Desktop **4.97.0**, Engine **29.9.2**, Compose **5.6.1**. The active `desktop-linux` endpoint is a local Windows named pipe. No remote override was configured. No new host feature/service/firewall/BIOS change, reboot or purchase occurred during this execution.

Public base images were downloaded without account login or paid services and resolved to immutable digests:

| Image | Observed repository digest |
| --- | --- |
| Node | `node@sha256:c86ecead9e55a5210ac1727de38a4ca840bf03dcaf34dc9749addbf383b1920c` |
| Python | `python@sha256:516b51cb9db2ef061e465c803e50f64361b82cefd91e525b889b967b83e83527` |
| PostgreSQL | `postgres@sha256:3a4264520e121176619f54ff867d12774bc81e95e7b84db58d63bccdb6144b81` |

Compose built migrate/app/restore-app from the verified sanitized context with digest-pinned Node/Python inputs. Final local app image: **`sha256:4445750e0135806ee6099c9daf509d6f862e1fb4169d98539606f794ff02398b`**, configured UID **10001**. Build npm audit reported zero vulnerabilities for its 156-package dependency graph; this does not establish whole-image vulnerability clearance. The initial pull failed because the new Docker credential helper was absent from this process PATH; adding the installed Docker bin directory to process-local PATH resolved it without altering stored credentials or global PATH.

## PostgreSQL execution

Observed server/native tools: **PostgreSQL 18.6, Debian 18.6-1.pgdg13+2**, x86_64. Head **0008** and Alembic drift check passed. The guarded verifier ran inside one-off migration containers against a generated `qa_<32 hex>` schema in `mma_test_stage` and completed:

- Upgrade/check, downgrade to base, then upgrade to head.
- Foreign-key rejection and transaction rollback.
- Eight concurrent writes with contiguous versions.
- Owned API data, cross-account rejection and deletion.
- Approved plan revision retaining two versions, nutrition availability and exports.
- Recovery rejection after account deletion.

The tool's generated schemas were cleaned up. Both migration/runtime roles were observed non-superuser, without CREATEDB/CREATEROLE. The runtime role cannot create schemas or public tables; actual attempted DDL was rejected and probes rolled back.

Two initial execution failures were retained and corrected operationally:

1. A later Compose command omitted the earlier POSTGRES_IMAGE digest environment setting. Compose reconciled the changed image reference and recreated the still-empty disposable tmpfs database; the next Alembic check correctly failed. No athlete or synthetic fixture data existed yet. Explicit migrations restored public schema head 0008; later verifier commands used `run --no-deps` to avoid dependency reconciliation. The final database container uses the tag reference but its actual image resolves to the observed local PostgreSQL digest. **Future commands must keep image variables consistent and must not recreate a populated tmpfs database.** Do not blindly repeat `up` from a different image environment.
2. TestClient uses host `testserver`, excluded by staging's configured allowed hosts. The initial probe returned 400. Adding `ALLOWED_HOSTS=testserver,127.0.0.1,localhost` **only to the disposable verifier container** allowed the guarded test to pass. Deployed app host restrictions were retained and separately tested.

No application-source fix or weakening of deployed security controls was needed for these verifier configuration issues.

## Native backup and separate-database recovery

The first archive was restored into the initially empty `mma_test_restore`; its opt-in restore application ran healthy under uvicorn. An early combined fixture check failed because its expected export hash preceded a later offline-coach write. Reference rows also differed after restore startup reseeded the sanitized catalog following the earlier empty database recreation. These were investigated rather than accepted as a passing integrity comparison.

The source app was restarted to restore its reference bootstrap. That correctly cleared its tmpfs fixture-token file, so fresh **synthetic** fixtures were created; original synthetic users/records were preserved. A clean second timed rehearsal used a **new, initially absent/empty `mma_test_restore_phase21b` database**, owned by the existing migrator with runtime DML privileges. No source or prior restore database was overwritten.

Verified successful second rehearsal:

| Check | Actual result |
| --- | --- |
| Native archive | Custom-format `pg_dump`; `pg_restore --list` and error-stopping native restore succeeded |
| Source/restore data | Matching count and canonical row hashes for **4 users, 26 records, 8 fighter snapshots, 2 division references** |
| Sessions | Four archived sessions invalidated in destination; old cookies rejected |
| Application | Two known fixture owners recovered independently, two plan versions each, equal canonical exported record payloads and cross-account write rejection |
| Source preservation | Source row/count hashes unchanged across the timed rehearsal |
| Measured interval | **11.647 seconds** from backup start through restore, invalidation and application/data verification; database setup and image downloads excluded |
| Application test boundary | Timed destination used a one-off runtime with in-process ASGI HTTP tests; first destination also exercised a running uvicorn restore service. No host-browser PostgreSQL acceptance is claimed |
| Archive | 110,318 bytes; SHA256 `5eb49d4f74d1397028ef639e956adf1768af0567b4b77b50218b1303161f57d3` |

The successful archive remains private inside the disposable database container at `/tmp/phase21b.dump`; a restrictive umask was used. **No archive was written to or permission added on protected `backups`.** This verifies logical recovery, not durable/off-host/encrypted backup retention or production RPO/RTO. Evidence: ignored `.qa-runtime/phase21/recovery-result.json`.

## Actual security, networking and monitoring

Passed inside the container/runtime:

- App UID 10001; read-only root filesystem rejects writes; capabilities ALL dropped; no-new-privileges enabled.
- Internal Docker network; app has no outbound default route. No external connectivity probe or paid AI call was made.
- Runtime DDL rejection; separate role credentials; migration/runtime permissions inspected.
- Blank provider key, test mode, zero daily/monthly AI budgets and zero outbound attempt reservations.
- Invalid Host gives 400; untrusted Origin and cross-site write give 403. CSP, nosniff, frame DENY, same-origin referrer and restricted permissions headers observed.
- Built image's original `reviewed_records()` is empty; sanitized provider returns eight fighters. Git/private `.env`/backend tests absent; font notice present. Technical exclusion is **not legal clearance**.
- Installed Python `pip check` passes. Its non-writable cache warning is expected under the nonroot/read-only runtime.

**Unresolved networking acceptance failure:** despite requested HostIp `127.0.0.1` and HostPort `18018`, actual app NetworkSettings.Ports is `{"8000/tcp":[]}` and Windows loopback readiness cannot connect. Restore port is likewise not an effective published endpoint. The containers are healthy internally, but the all-internal topology on this Docker Desktop runtime has not supplied working host port publication. No network isolation, host firewall or Docker daemon setting was weakened to make this pass. A reviewed local ingress/relay design and retest are needed. See [Docker port-publishing semantics](https://docs.docker.com/engine/network/port-publishing/); configuration alone is not proof of effective exposure.

A real **pause/unpause** of the disposable DB (without stop/recreation) was exercised with a bounded three-second connection probe. Existing `evaluate_alerts` emitted critical `database_not_ready`; after unpause readiness/head 0008 returned and signals cleared. Source app restart then returned ready. Measured pause-through-restart-check interval: **20.222 seconds**. No external notification occurred. This used a custom bounded readiness wrapper around the existing evaluator; `app.operations` itself reads DB aggregates before reporting and is **not validated as a resilient outage collector**. Timeout/error handling and continuous collection remain operational gaps. Evidence: ignored `.qa-runtime/phase21/monitoring-result.json`.

Private TLS/proxy/secure-cookie production tests were **not executed**; no separately authorized proxy/certificate was provisioned. Test-mode HTTP settings cannot satisfy production transport gates. No full image CVE scan, complete SBOM/license audit, independent security review or expert/legal approval is claimed.

## New regression results

| Check | Actual result in this execution |
| --- | --- |
| Backend Pytest | **370 passed**, two upstream deprecation warnings, 79.45 seconds on corrected run |
| Initial backend run | 364 passed / six fixture setup errors: inaccessible shared Windows pytest temp directory. Corrected by a fresh project-local `--basetemp`, with no permission changes to that shared directory |
| Frontend Vitest | **12 passed**, four files |
| Application TypeScript / Vite | Passed through `npm run build` |
| Browser TypeScript | Passed |
| Ruff | Passed |
| Prettier frontend/src/e2e/config | Passed |
| PostgreSQL guarded verifier | Passed after the isolated configuration corrections above |
| Python runtime dependencies | `pip check` passed |
| Real Edge subset | **40 passed, zero failures/skips/flaky**, five widths: 1440, 1920, 768, 390, 375; journey, responsive/accessibility/modal/keyboard, Phase 13 identity/security and Phase 15 refinements |

Browser tests used the existing **disposable SQLite browser server on 8123**, not the inaccessible PostgreSQL container endpoint. Individual tests completed, but Windows server teardown hung. After identity-checking the exact disposable QA Python parent/child processes, graceful termination was rejected; those two processes were force-stopped. Playwright then exited **0** and wrote the final JSON report, duration 376.470 seconds. No unrelated process/service was stopped. This intervention and the backend's initial fixture errors are not hidden as clean first attempts. Browser evidence: [browser-results.json](evidence/phase21/browser-results.json). This was a focused 40-case run, not a rerun of Phase 18's full 175 scheduled cases. No new print/TLS coverage is claimed.

## Updated launch gates and final state

| Gate | Current status |
| --- | --- |
| Approved exact ACL changes | **Passed**; two RX entries only; backups unchanged |
| Local runtime / sanitized build / context integrity | **Passed** |
| PostgreSQL migration/transactions/concurrency/ownership/versioning | **Passed** in guarded disposable scope |
| Native separate-database logical recovery | **Passed**, with explicit application/timing/retention boundaries above |
| Container controls / selected security checks | **Passed** for the checks listed; not a penetration test or complete scan |
| Local outage/restart/evaluator | **Passed** using bounded probe; resilient ongoing collector still incomplete |
| Windows loopback browser-to-container journey | **Blocked**; effective published ports absent |
| TLS/proxy/secure-cookie / live IdP | **Unverified / separately gated** |
| Durable backups / full image scan / external expert-security-legal reviews | **Open** |
| Public launch | **Blocked and unauthorized** |

At evidence capture the source app, database and first restore app were healthy. They remain running on the isolated Docker network to preserve the synthetic tmpfs database and container-local archives; no effective Windows host application port was observed. **Stopping/recreating the database can discard these artifacts.** Do not use broad Docker cleanup commands or reset the prepared directory. Existing credentials and protected backups are unchanged.

Detailed local evidence/scripts remain under ignored `.qa-runtime/phase21/`, including final runtime metadata, ACL comparisons, native recovery and monitoring results; raw container secret environments are excluded. No production connection, real athlete-data modification, paid request, purchase or public deployment occurred. Readiness is **verified local container/PostgreSQL candidate with unresolved ingress and external launch gates**, not production acceptance.
