# Phase 20: prerequisite discovery and authorization boundary

Date: 2026-11-01. **BLOCKED; isolated staging has not executed.**

## Actual environment results

- Branch: `phase18-isolated-staging`; HEAD `ec221e6b00108f445e825e0e535482c36e329eaa`. Existing Phase 19 documentation changes were preserved.
- Release `v1.0.0-rc.17` still resolves to commit `2f43e4d66e76e921bc40d3840611c347ab9824c8`.
- Read-only Windows CIM discovery reports Windows 11 Home, 64-bit, build 26300; registry reports Core / 26H2 / revision 9711. Vendor support for this exact edition/build is not established.
- AMD Ryzen 7 7730U. Firmware virtualization reports True, but SLAT and VM monitor mode flags report False. These results do not establish either compatibility or hardware incompatibility; resolve with Windows hypervisor diagnostics before installation. No BIOS or boot setting was changed.
- Usable RAM: 14,530,876 KiB (about 13.9 GiB); available at discovery: 3,328,020 KiB (about 3.2 GiB). Free C: storage: 294,965,776,384 bytes (about 274.7 GiB). Available memory is a snapshot, not a staging capacity test.
- Docker, Podman and psql were not found on PATH. The WSL launcher exists but explicitly reports WSL is not installed. No container engine/server/Compose version or image digest was observed.
- No TCP listener was returned for 18018, 18019, 5432 or 8123 in the discovery snapshot. Ports are not reserved.
- Elevated-session reads of staging preparation were denied, but normal workspace reads succeeded. All **89 context hashes match**; all three synthetic secret files and four environment files exist. No secret values were read or printed, no ACL changed and no credentials regenerated. Windows ACL suitability and environment values remain unverified. LanmanServer was observed Running / Automatic; no service change was made.
- Existing Compose/runbook inspected: sanitized context path, internal network, loopback 18018/18019, separate roles, disposable tmpfs database, read-only app containers and separate restore profile. These are configuration properties, not runtime verification. Existing containers and Docker context cannot be enumerated without a reachable engine; absence of containers is not asserted.

## Concrete proposed setup, awaiting owner authorization

1. Resolve read-only Windows hypervisor capability and exact Windows build support first. Docker's current page lists SLAT, 8 GB RAM and WSL >=2.1.5; its edition guidance lists Pro/Enterprise/Education while also noting Home permits Linux containers. Treat this ambiguity and the CPU flags as unresolved rather than declaring this host supported. See [official Windows requirements](https://docs.docker.com/desktop/setup/install/windows-install/).
2. Confirm owner eligibility for Docker Desktop free use or an existing entitlement under the [official license conditions](https://docs.docker.com/subscription-billing/desktop-license/). No purchase is permitted. If ineligible, stop for an explicitly approved alternative.
3. With specific owner approval, install WSL2 using `wsl --install --no-distribution`, enabling only its required Windows components. This is a system change; do not execute before approval. Pause for an owner-controlled reboot if required. Verify WSL version/status and update only within approved scope. See [Microsoft installation guidance](https://learn.microsoft.com/en-us/windows/wsl/install) and [command options](https://learn.microsoft.com/en-us/windows/wsl/basic-commands#install).
4. After compatibility and licensing checks pass, download the official signed Docker Desktop x86_64 installer, verify publisher/checksum, and install per-user with WSL2/Linux containers. Owner must accept terms. Do not purchase, enable cloud/Kubernetes/Windows containers, expose a daemon, alter firewall/BIOS or change unrelated services. Any additional service requirement needs specific approval.
5. Inspect existing secret ACL suitability before using the runtime; do not take ownership/reset permissions or overwrite preparation/credentials. Context hashes and file presence passed; synthetic environment configuration, secret protection and disabled paid AI still need pre-start validation.
6. Verify a local Docker endpoint, reject remote contexts, inspect project collisions and free resources, review pinned image inputs, then execute the existing [Phase 18 staging runbook](PHASE18_STAGING.md). Preserve the source database and use only disposable `mma_test*` databases. Private TLS/proxy configuration requires a reviewed local configuration and authorization before provisioning.

## Updated launch-gate matrix

| Deliverable | Phase 20 evidence / status |
| --- | --- |
| Environment report | Read-only host and source checks above; 89 context hashes match; compatibility and secret ACL suitability remain open |
| Runtime versions | WSL not installed; no Docker/Compose/PostgreSQL server version observed |
| Build / image digests | NOT RUN; runtime installation not authorized |
| PostgreSQL migration / isolation / concurrency | NOT RUN; head 0008 not exercised on PostgreSQL |
| Native separate-database restore | NOT RUN; integrity, session invalidation and recovery duration unverified |
| Container security / scanning | Configuration inspected only; actual users, health, permissions, images, exclusions and exposure unverified |
| TLS / proxy | NOT RUN; no certificate or proxy provisioned |
| Monitoring / outage / recovery | NOT RUN; no live container signals or restart evidence |
| Full regression | NOT RUN in Phase 20; stopped at authorization/prerequisite boundary; no application code changed |
| Licensing / expert review / public launch | Still pending; technical content exclusion does not establish licensing approval; public deployment unauthorized |

No application code, athlete database, production credentials, original tracker or release tag was changed. No install, feature/service/firewall/BIOS change, reboot, container build/pull/start, paid call, purchase or public deployment occurred. Readiness remains **local release candidate with unexecuted staging gates**. No Phase 18 results are counted as Phase 20 results.

**Next owner decision:** authorize the scoped WSL2 prerequisite installation and per-user Docker Desktop installation only after compatibility and no-purchase licensing checks pass; retain owner control of any reboot. Verify existing secret ACL suitability before starting staging. Do not interpret permission for read-only elevated discovery as installation approval.
