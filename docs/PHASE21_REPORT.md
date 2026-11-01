# Phase 21: compatibility review and installation approval boundary

**Superseded status:** additional ACL authorization was subsequently received and applied. See [actual staging execution, recovery results and remaining blockers](PHASE21_STAGING_RESULTS.md). Earlier pending/blocked statements below are historical snapshots.

Date: 2026-11-01. **Runtime installed and verified; staging blocked by existing directory ACL.** The initial review below is retained as historical evidence; the authorized execution update supersedes its pending-installation statements.

## Authorized execution update

### Subsequent scoped ACL authorization: protected-child stop

The owner subsequently authorized adding only an inheritable ReadAndExecute allow rule for their current Windows SID on `.qa-runtime/phase18`, preserving ownership, entries and inheritance protection, and explicitly required stopping if protected children need separate rules.

Read-only host identity resolved the intended account to `IWA2024\darai_qtguapt`. Before applying any rule, recursive ACL inspection found **two protected child directories: `secrets` and `backups`**. Their ACLs block inheritance from the staging root. The `secrets` directory grants OWNER RIGHTS/SYSTEM/Administrators and therefore needs its own explicit rule for the owner account to read credentials. Parent permission alone cannot satisfy the staging preflight.

**Stopped before Set-Acl: zero ACL changes were applied.** No owner/entry/protection change, secret regeneration or value disclosure occurred. Evidence: ignored `.qa-runtime/phase21/acl-boundary.json`. No container build/start, PostgreSQL migration, backup/restore, monitoring, security scan or regression suite ran in this continuation. Previous runtime results below remain historical evidence, not new executions.

**Next narrowly scoped authorization needed:** add an explicit inheritable ReadAndExecute allow entry for the same current owner SID on the protected `.qa-runtime/phase18/secrets` directory, preserving its ownership, existing entries and protection, in addition to the already approved root entry. Credential files themselves were not identified as protected children and should inherit from that directory; verify effective read access without displaying values. Leave protected `backups` unchanged. Any later backup-output permission requirement must be identified separately; no write, FullControl, Everyone/Users rule, ownership change or ACL reset is proposed.

The original root-only permission proposal below is superseded by this finding. Staging remains blocked at the owner's explicit protected-child boundary; public deployment remains unauthorized.

Owner confirmed **personal use** and approved the identified installation scope in the next message. This satisfies the licensing-category question under Docker's cited terms and the Step 3 scope approval. No purchase was made. Windows UAC was used for the required administrator check and approved WSL installation; outside-sandbox execution alone did not elevate the token.

### Actual installation and runtime results

- Administrator feature query succeeded: VirtualMachinePlatform **Enabled**, legacy Microsoft-Windows-Subsystem-Linux **Disabled**. The packaged WSL2 route does not require enabling WSL1. Earlier diagnostic launches produced no evidence; the corrected direct encoded diagnostic returned exit 0 and administrator=True. No execution-policy setting was changed.
- `wsl --install --no-distribution` completed with **exit 0**. WSL **3.0.3.0**, kernel **6.18.54.1-1**, default version **2** observed. `wsl --version` and `wsl --status` both exit 0 outside the sandbox; no user distribution is installed (list command reports that fact with nonzero exit). The WSL1 warning concerns the deliberately unused legacy feature. No reboot was requested by the recorded installer output or initiated by the agent.
- Official Docker Desktop **4.97.0.244584** installer downloaded from the release-note URL. SHA256 **2668273f82b342a058a28f9ab53ea7bddde10bb6d51307ce2ec54c2d36459744** matches the official checksum. Authenticode **Valid**, publisher **Docker Inc**.
- Executed installer arguments: `install --user --backend=wsl-2 --no-windows-containers --quiet`; **exit 0**. No automatic license-acceptance flag or always-run-service flag supplied. Standard Desktop bundles include optional CLI plugins; their installation is not evidence that AI/cloud/model services were enabled or used. No optional plugin command or paid API invocation was made.
- Docker client **29.9.2 / a82e528**, Compose **v5.6.1** observed. `docker desktop start --timeout 45` initially timed out (exit 1); follow-up backend log reports the Linux/WSL daemon ready after **58.8 seconds**, and Desktop status reports running. The timeout is retained as an initial failure, not counted as successful execution.
- Actual engine: **29.9.2**, OSType **linux**, kernel **6.18.54.1-microsoft-standard-WSL2**, **16 CPUs**, **7,193,137,152 bytes** VM memory. This operational WSL2 backend resolves the practical virtualization prerequisite; no BIOS, boot or VBS security change was needed.
- Active context **desktop-linux**, endpoint `npipe:////./pipe/dockerDesktopLinuxEngine`; default context also local. DOCKER_HOST, DOCKER_CONTEXT and CONTAINER_HOST absent. No remote endpoint used. Initial pre-start engine connection failed as expected before daemon startup; it is not counted as runtime verification.
- Docker AutoStart=False observed; no com.docker.service was returned by the service query. No manual firewall, BIOS, unrelated-service, boot or reboot change was made. Other queried settings returned blank and are **not** treated as confirmed false. Docker settings report LicenseTermsVersion=2; no fabricated account sign-in or agent acceptance event is claimed.

### Staging preflight and precise new boundary

Normal workspace checks reverified **89 hashes, zero mismatches**. App/migration target `mma_test_stage`; restore target `mma_test_restore`; APP_ENV=test, API key blank, AI_GLOBAL_DAILY=0 and AI_GLOBAL_MONTHLY=0 in each application configuration. Only whitelisted nonsecret fields were output. Existing credentials/preparation were preserved.

`docker ps -a` returned no containers. However `docker compose -f deploy/compose.staging.json config --quiet` **failed, exit 1**: access denied reading `.qa-runtime/phase18/postgres.env` from the host owner session. ACL inspection in the workspace confirms `.qa-runtime/phase18` is owned by `IWA2024\CodexSandboxOffline`, inheritance protected, granting OWNER RIGHTS/SYSTEM/Administrators; prepared children inherit restrictive access. This explains the earlier split between workspace and host-session reads. It is not a missing file or a reason to regenerate secrets.

**Specific proposed additional change, NOT EXECUTED:** add the current Windows owner's SID an explicit **ReadAndExecute** inheritable allow entry on this project's `.qa-runtime/phase18` directory, preserving existing entries, ownership and inheritance protection. Confirm effective propagation to context, env and secret files; stop if any protected child needs a separate explicit rule. Do not grant Everyone/Users access, FullControl or write access; do not take ownership/reset ACLs or change parent/tracker directories. Existing backup-output paths will be assessed separately if later needed. This grants access to existing synthetic secrets and therefore requires explicit approval under the previously presented preservation scope before proceeding.

Local evidence is in ignored `.qa-runtime/phase21/`: administrator feature results, WSL install log/result, normalized WSL versions, official Docker checksums/installer and install result, sanitized preflight findings and ACL metadata. No secret values are recorded there. Reports do not treat the downloaded installer as a distributable release artifact.

| Current gate | Result after authorized setup |
| --- | --- |
| Owner scope / licensing category | Confirmed personal use and installation approval |
| WSL2 / Docker installation | Executed; versions and local WSL2 engine verified |
| Source/tag/context preservation | Original tag unchanged; all 89 hashes match; no app/data changes |
| Staging host access | **BLOCKED**; scoped read/traverse ACL addition requires approval |
| Container builds / digests / scans | NOT RUN; no staging image built |
| PostgreSQL migrations/FK/rollback/concurrency/ownership/versioning | NOT RUN |
| Native backup / separate restore / recovery duration | NOT RUN |
| Container security / health / runtime content exclusion | NOT RUN |
| Monitoring / outage / restart / TLS/proxy | NOT RUN; private TLS remains separately gated |
| Regression suite | NOT RUN in this continuation; application code unchanged and staging prerequisite failed |
| Public launch / independent review | Still blocked and public deployment unauthorized |

No athlete database, production credential/service, original tracker or release tag changed. No containers started, no public endpoint or paid/cloud service used. Next action is owner approval of the narrow staging read/traverse ACL addition; no installation reapproval is needed.

## Source and authorization record

Actual branch is `phase18-isolated-staging`; HEAD is `5180f778f235d0149a49e300c350cb240c3948f6`, not the supplied older application baseline. Git comparison against `ec221e6b00108f445e825e0e535482c36e329eaa` shows only three documentation changes for Phases 19/20. Application baseline is preserved. Original tag `v1.0.0-rc.17` resolves to `2f43e4d66e76e921bc40d3840611c347ab9824c8` and was not changed.

Owner conditionally authorized WSL2 and Docker Desktop, subject to official compatibility, no new licensing purchase, required components only, owner-controlled reboot, and no unrelated BIOS/firewall/service changes. Phase 21 Step 3 additionally says to present identified changes and proceed only after explicit approval. That specific-scope approval and licensing confirmation are pending; read-only outside-sandbox diagnostic permission does not grant Windows administrator elevation or installation approval.

## Host compatibility evidence

| Check | Actual evidence / interpretation |
| --- | --- |
| Edition/build | Windows 11 Home x64; Core / 26H2 / 26300.9711 from registry, consistent with prior discovery |
| Processor | AMD Ryzen 7 7730U; address width 64; firmware virtualization True |
| Conflicting flags | CIM still reports SLAT=False and VM monitor=False. However `Win32_ComputerSystem.HypervisorPresent=True`; `systeminfo` explicitly reports an active hypervisor and suppresses individual Hyper-V requirement results |
| Security | `systeminfo` reports virtualization-based security and hypervisor-enforced code integrity running. No security protection was disabled |
| SLAT conclusion | Active Windows hypervisor is strong evidence of working virtualization; raw CIM flags are not conclusive negative hardware evidence under this configuration. Independent exposed SLAT measurement was not obtained. No Coreinfo executable found on PATH; none downloaded, installed or executed |
| Windows features | Read-only `Get-WindowsOptionalFeature` queries for WSL and VirtualMachinePlatform failed because administrator elevation is required. Current process administrator-role check=False. Feature states remain unknown; no DISM modification attempted |
| Memory | CIM total physical memory 14,879,617,024 bytes (about 13.9 GiB). `systeminfo` available physical memory 2,697 MB during this check. Total exceeds Docker's published 8 GB minimum; current free memory does not establish build capacity |
| Storage | Phase 20's 274.7 GiB free snapshot was not rerun; recheck immediately before installation/build |
| Runtime | Prior WSL-not-installed result remains applicable; no install occurred. No actual Docker/Compose/PostgreSQL runtime versions or local endpoint verification available |

Microsoft's [Hyper-V requirements](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/host-hardware-requirements) explain suppressed checks on an active hypervisor. The [WSL FAQ](https://learn.microsoft.com/en-us/windows/wsl/faq) covers WSL2 on Home. [Windows release information](https://learn.microsoft.com/en-au/windows/release-health/windows11-release-information) lists 26H2/build 26300 as generally available and within servicing; this is not verification of the exact installed revision's patch currency or channel.

[Docker's Windows requirements](https://docs.docker.com/desktop/setup/install/windows-install/) require WSL >=2.1.5, SLAT, enabled virtualization and 8 GB RAM. The page lists Pro/Enterprise/Education in its OS bullets but separately permits Linux containers on Home. Accordingly Home is not grounds to demand a paid Windows upgrade, but exact host/runtime compatibility remains provisional until feature state and WSL2 operation are verified. No Windows upgrade, security disabling or BIOS change is proposed. [Microsoft WSL troubleshooting](https://learn.microsoft.com/en-us/windows/wsl/troubleshooting) requires SLAT for WSL2.

Only selected deidentified findings are recorded here; the broad diagnostic output included unrelated machine/account/network metadata and has not been copied into repository evidence.

## Licensing: owner confirmation required

[Docker's current license page](https://docs.docker.com/subscription-billing/desktop-license/) allows personal use, education, noncommercial open source, and businesses with fewer than 250 employees **and** under US$10 million annual revenue. Larger organizational/government use requires an appropriate entitlement. Intended use, organization category/size/revenue and any existing entitlement were not supplied. A local Windows account or registered-owner field cannot establish eligibility. An owner question is pending; no free-use eligibility or contractual acceptance is assumed, and no purchase is authorized.

## Specific installation proposal for approval (not executed)

1. Obtain administrator access for read-only WSL/VirtualMachinePlatform feature inspection. This tool's outside-sandbox execution is currently not an elevated Windows token.
2. If licensing and remaining compatibility checks pass, install Microsoft's WSL2 package/kernel without a default user distribution using `wsl --install --no-distribution`. Enable only the Windows components the approved WSL2 installation actually requires, including Virtual Machine Platform where needed. Feature requirements must be inspected rather than assuming both legacy WSL and current packaged WSL are necessary. No full Hyper-V role, Containers feature, security disabling or boot configuration change is authorized by this scope.
3. Stop if restart is required; owner controls when to restart. Do not schedule or execute an automatic reboot. Verify WSL version/status afterward; any necessary WSL update remains within the identified WSL component scope, subject to owner approval below.
4. Obtain official x86_64 Docker Desktop per-user installer; compare the official published checksum and validate Authenticode publisher/signature before execution. Install only Desktop/Engine/Compose with WSL2 Linux-container backend. Per-user installation is documented as not requiring the privileged all-users helper service. Owner accepts license terms after eligibility confirmation.
5. Do not enable Kubernetes, cloud services, Windows containers, remote TCP daemon, firewall exceptions, unrelated services or start-at-login behavior. If installer/runtime demands any such extra change, stop and identify it. Existing LanmanServer Running/Automatic was observed in Phase 20; no service modification is proposed or newly verified here.
6. Once runtime works, record WSL/Engine/Compose versions, local context and `docker info`; reject remote/unexpected endpoints. Recheck resources, all 89 context hashes, existing synthetic secret ACLs/configuration, disabled paid AI, ports and disposable databases before the existing Phase 18 runbook. Do not reset staging files, secrets or athlete data. Private TLS/proxy setup requires separate scoped authorization.

## Updated execution and launch gates

| Requested deliverable | Phase 21 result |
| --- | --- |
| Host compatibility | Active hypervisor explains why raw flags are insufficient; administrator feature-state inspection and operational WSL2 verification pending |
| Licensing | Official terms checked; owner eligibility confirmation pending |
| Authorization | Conditional authorization recorded; identified component/feature scope above awaits Step 3 confirmation |
| Installed runtime versions | None installed or observed in Phase 21 |
| Engine/Compose/local context | NOT RUN; runtime unavailable |
| Staging preflight | Not repeated beyond source/tag review; historical 89-hash result is not a Phase 21 recheck |
| Build/digests/scans/container security | NOT RUN |
| PostgreSQL head 0008/FK/rollback/concurrency/ownership/versioning | NOT RUN |
| Separate-database native backup/restore/recovery time | NOT RUN |
| TLS/proxy/security/monitoring/outage/restart | NOT RUN; private TLS separately gated |
| Regression | NOT RUN; no application changes and installation prerequisites unresolved |
| Public launch | Unauthorized; runtime and independent licensing/security/professional review gates remain open |

No software download/install, host feature/service/firewall/BIOS change, reboot, paid AI request, production connection, athlete-data modification, purchase or public deployment occurred. Only project documentation is changed. Status remains a local release candidate awaiting runtime prerequisites; automated review does not constitute independent professional approval.
