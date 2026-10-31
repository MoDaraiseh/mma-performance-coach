# Phase 19 environment discovery — stopped at runtime prerequisite

Date: **2026-11-01**. Outcome: **BLOCKED; local release candidate remains unchanged.** No container/PostgreSQL runtime verification occurred. This report follows Phase19's explicit instruction to stop before provisioning when a compatible local runtime is unavailable.

## Actual discovery and preservation

| Check | Actual result |
| --- | --- |
| Branch / initial worktree | `phase18-isolated-staging`; clean before this documentation-only report |
| Application baseline | `ec221e6b00108f445e825e0e535482c36e329eaa` |
| Original release tag | `v1.0.0-rc.17` still resolves to `2f43e4d66e76e921bc40d3840611c347ab9824c8` |
| Docker / Compose / Podman | No CLI on PATH; checked documented system/per-user install locations contain no corresponding executable; no matching runtime service returned |
| PostgreSQL | No postgres/psql/pg_ctl/pg_dump/pg_restore on PATH; standard PostgreSQL installation directory absent |
| WSL | Windows `wsl.exe` launcher exists, but `--version`, `--status` and `--list --verbose` report **WSL is not installed** (nonzero exits). A launcher is not an installed Linux runtime |
| Remote runtime/test DB | DOCKER_HOST/DOCKER_CONTEXT/CONTAINER_HOST and MMA_TEST_DATABASE_URL are not configured; no remote daemon/database was contacted |
| Relevant ports | No listener found at18018,18019,5432 or8123 at discovery time. This is a snapshot, not a reservation |
| Prepared staging files | All **89 context hashes** match Phase18 preparation; app/migration/restore/PostgreSQL configuration files exist. Credential file presence only was checked; no secret values were read/printed |
| Isolation guards inspected | Loopback-only app/restore ports, internal network, separate roles/configs, tmpfs test data; guarded PostgreSQL tool requires postgresql+psycopg/mma_test* and generated qa_hex schema |
| Existing data/history | No athlete DB, production credential/database, existing volume, release tag or original tracker was changed |

Machine-readable evidence: [environment.json](evidence/phase19/environment.json). Discovery used Get-Command, Test-Path/common install locations, read-only service/installer metadata queries, WSL status commands, .NET local TCP listener enumeration and Git/context integrity checks. No exhaustive disk/network scan or firmware/service change occurred. WSL output is preserved with encoding normalized in the evidence file.

## Exact prerequisite and installation instructions — NOT EXECUTED

Required: an owner-approved **local Linux container engine with Compose support**, capable of running the existing Phase18 JSON recipe. For the Docker Desktop WSL2 route, this machine first needs WSL2 installed; Docker's current documentation requires WSL2.1.5 or newer. Firmware virtualization and complete Windows edition/feature/service eligibility were **not verified or changed**. Review [Docker Windows requirements/install steps](https://docs.docker.com/desktop/setup/install/windows-install/) before selecting this route.

1. **Owner authorization first.** Phase19 explicitly prohibits installing system software, enabling virtualization, changing firewall rules or host services without approval. Authorize the specific runtime, necessary WSL/Windows feature setup and any reboot separately. Do not purchase anything. Confirm applicable [Docker Desktop licensing](https://docs.docker.com/subscription-billing/desktop-license/); eligibility for free use has not been established for the owner. If a paid subscription would be required, stop and select an already entitled or separately approved no-cost alternative; do not buy a subscription.
2. After authorization, inspect Windows edition/support and CPU virtualization status using Windows Settings/Task Manager. If firmware virtualization is disabled or host services need changes, obtain approval for those exact changes; do not automatically enable Hyper-V, BIOS settings, firewall access or services.
3. For the approved WSL2 route, an administrator can install WSL without an unnecessary default Ubuntu distribution using the following **documented commands, not executed here**:

```powershell
# System-changing: owner approval and appropriate administrator access required.
wsl --install --no-distribution
# Reboot only if requested/approved, then verify:
wsl --version
wsl --status
# If the installed WSL is older than Docker's required version, approve/update it:
wsl --update
```

Microsoft documents `--no-distribution` in its [WSL commands](https://learn.microsoft.com/en-us/windows/wsl/basic-commands#install); [installation/restart guidance](https://learn.microsoft.com/en-us/windows/wsl/install) explains the Windows feature changes. Docker does not require a user Linux distribution for Windows CLI use with its [WSL2 backend](https://docs.docker.com/desktop/features/wsl/). No WSL install/update/restart command was run during Phase19.

4. Download Docker Desktop only from the official installer link above, verify its publisher/checksum, and have the owner review/accept applicable terms. Use the approved per-user installation when supported, enable its WSL2 Linux-container backend and reopen PowerShell. Do not enable Kubernetes, Windows containers, remote TCP daemon exposure, public networking or cloud services for this test. WinGet is absent here; no package manager was installed as a workaround. A [Podman installation](https://podman-desktop.io/docs/installation/windows-install) is an alternative only after explicit owner selection, prerequisite approval and separate Compose/recipe compatibility verification; it was not installed or assumed compatible.
5. Verify `docker --version`, `docker compose version`, the selected **local** context and `docker info`; reject remote endpoints before any build/run. Record actual client/engine/Compose versions. Review generated secret ACLs, source/context hashes, image digests and existing project/port collisions. Use the PostgreSQL container in the existing recipe; installing a separate host PostgreSQL service is not necessary for that recipe.
6. Resume [Phase18's staging runbook](PHASE18_STAGING.md) with its existing prepared context/credentials. The preparer refuses existing destinations: do not overwrite/reset `.qa-runtime/phase18/` or regenerate its secrets blindly. Build only the sanitized context; never use the whole repository as a cleared public artifact. No image digest or build result exists until an actual build is performed.

## Phase 19 results and updated gates

| Deliverable / gate | Current result | Required next action |
| --- | --- | --- |
| Environment discovery | **Executed; blocker identified** | Owner-authorized local runtime/prerequisite installation |
| Container build/digests/security | **NOT RUN**; no image built/scanned, no UID/filesystem/network/health runtime assertion | Build approved sanitized context; inspect image IDs/digests, user, read-only compatibility, internal network/ports, notices/excluded content and scan when available |
| PostgreSQL/version/migrations | **NOT RUN**; actual server version unknown, no new migration execution | Guarded disposable mma_test* upgrade/check/down/up, FK, rollback, concurrency, versions, ownership/export/deletion; record actual version/head0008 |
| Separate-database backup/restore | **NOT RUN**; no native archive/restore/session invalidation/app recovery or recovery time | Synthetic source to separate initially empty restore DB; preserve source, compare counts/payloads/history, invalidate restored sessions and time app recovery |
| Private TLS/proxy | **NOT RUN**; no testing certificate/proxy provisioned | Authorized local test certificate/proxy, secure cookie/host/origin/header rejection checks; do not claim public trusted TLS |
| Monitoring/restart/recovery | **NOT RUN in a container**; prior synthetic alert tests are not a real outage/restart | Local-only collector/snapshots, deliberate disposable outage/auth/API failures, restart/recovery and fixed-label alert evaluation; no external notification |
| Phase19 regression | **Not rerun after stop condition; no application code changed** | Run complete source/database/browser/security/container regression once authorized runtime is available |
| Historical Phase18 regression |370backend/12frontend/168Edge passed, seven intentional skips; **prior-phase evidence only**, not new Phase19 execution | Preserve evidence; do not count these as PostgreSQL/container acceptance |
| Licensing/professional/security/legal | Original11 excluded from prepared context, but no actual built-image verification or external approval; specialist/security/legal/privacy/terms gates still pending | Real artifact review and qualified independent findings/remediation/retest; no fabricated sign-offs |
| Staging/production readiness | **Local release candidate only**; public deployment unauthorized | Close runtime and independent review gates before readiness promotion; owner approval cannot replace them |

No installer/download/image pull/build, host feature/service/firewall change, database creation/deletion, new volume, paid AI call, purchase or public deployment occurred. Existing synthetic files and credentials remain untouched. The exact next owner decision is approval of a specific eligible local runtime and required WSL/host prerequisites under a no-purchase constraint. This report is documentation only; it does not claim completion of the blocked runtime objective.
