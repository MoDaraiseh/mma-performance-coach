# Risk decisions for unfixed image findings

> **Status: DRAFT, NOT APPROVED.** Prepared 12 November 2026 for owner review. Nothing in this document takes effect until the owner completes the approval block. It does not approve staging replacement or public deployment; those approvals remain separate.

## Scope

This record covers two scanner findings for which no vendor fix exists in the pinned distribution. It applies only to the **isolated loopback review/staging candidate**, built from `deploy/Dockerfile.candidate` and `deploy/Dockerfile.postgres-candidate` at or after `e6e4b6d`. Production is out of scope; see [Production database plan](#production-database-plan-proposed).

| ID | Finding | Image | Vendor fix |
| --- | --- | --- | --- |
| R1 | CVE-2026-86140 (high 8.0), plus 10 low/medium libxml2 findings | `mma-review-postgres:patched`, libxml2 2.13.9-r2 | None in Alpine 3.24 (checked 12 November 2026). The upstream fix is 2.15.4. |
| R2 | CVE-2026-119586 (high 8.5) | `mma-review-app:patched`, sqlite-libs 3.53.4-r0 | None in Alpine 3.24 (checked 12 November 2026) |

The musl CVE-2026-107891 finding is **not** part of this record. Alpine names the installed 1.2.6-r3 as fixed, and the scanner discrepancy is already dispositioned in [FINAL_DELIVERY](history/FINAL_DELIVERY.md).

## Alternatives evaluated

- **Debian-based official image** (`postgres@sha256:e3d24f6906d0760bf4da0dae872415391ededefad23fd471c47dc53b0ddf3c42`, Debian 13.7, PostgreSQL 18.6). Scanned 12 November 2026: 147 findings, 4 critical and 40 high. It contains the same CVE-2026-86140 in libxml2 2.9.14 (`2.12.7+dfsg+really2.9.14-2.1+deb13u3`), with no Debian update available, and adds 6 high krb5 findings with no fix. **Rejected:** it does not remove R1 and increases exposure.
- **PostgreSQL built from source without libxml2** (`--without-libxml`). This would remove R1, but it replaces the vendor binary with a self-maintained build. Phase 24 rejected it. **Deferred:** reconsider only if no vendor fix appears and production cannot use a managed database.
- **Wait for a vendor fix.** This remains the intended resolution; see [Re-check procedure](#re-check-procedure).

## Exposure assessment (verified 12 November 2026)

**R1, libxml2 in PostgreSQL.** The vulnerable code runs only when the server parses XML, through SQL XML functions or `::xml` casts.
- The application contains no XML usage: there is no `xml` reference in `backend/app` or `backend/migrations`.
- All application queries go through SQLAlchemy with bound parameters. The only raw SQL is fixed literals: `PRAGMA foreign_keys=ON` and `BEGIN IMMEDIATE`, both SQLite-only, and `CURRENT_TIMESTAMP` and partial-index predicates in the schema.
- No endpoint accepts SQL or XML.
- The runtime role `mma_stage_runtime` is not a superuser and cannot create databases or roles. It has no CREATE on `public`, only DML.
- The database listens only on an internal Docker network (`internal: true`) with no published port.
- Staging ingress is loopback-only (`127.0.0.1`).
- Reaching the flaw would therefore require an attacker who can already run arbitrary SQL as a database role. That is a prior compromise of credentials or of the application.
- The 14 `xml*` functions remain executable by any role that can connect. This is not proof the path is unreachable; it means reaching it requires SQL execution.

**R2, sqlite-libs in the application image.** The library is present because the Python 3.14 runtime links the `sqlite3` module.
- With `DATABASE_URL` set to PostgreSQL, the application opens no SQLite database.
- The SQLite code paths (`backend/app/db.py`, the `tools/sqlite_*` utilities) are used only for local development and offline tooling.
- No endpoint accepts a SQLite file or SQL.
- The container runs as non-root (UID 10001) with a read-only root filesystem, all capabilities dropped and no-new-privileges.

## Compensating controls (verified in review acceptance)

- Non-root, read-only containers with all capabilities dropped and no-new-privileges. gosu is removed from the database image.
- Internal-only database network, no published database port, loopback-only ingress.
- Least-privilege database roles: migrator and runtime are split, and the runtime role has DML only.
- Host, Origin and cross-site request rejection; restrictive CSP and security headers.
- Paid AI is disabled in staging: blank key, zero budgets.

These reduce exposure. They do not eliminate the vulnerabilities.

## Proposed decision

1. **Accept R1 and R2 for the isolated loopback staging candidate only.** This acceptance expires on **12 December 2026**, or earlier if any of the following occurs:
   - Alpine publishes a fixed libxml2 or sqlite-libs package. Then pin it, rebuild, rescan and re-accept.
   - The candidate is exposed beyond loopback, uses real user data, or gains any feature that parses XML or executes user-supplied SQL.
   - A public exploit or an exploitation report appears for either CVE.
   - The scanner reports a higher severity or new reachability information.
2. **This decision does not cover public deployment or real user data.** Production requires either a vendor-fixed image, or the managed-database plan below plus an independent security review of R2.
3. **Re-check for vendor fixes at least weekly** until the findings are resolved.

## Production database plan (proposed)

Run production on a **managed PostgreSQL 18 service**, so that database patching, durable backups and point-in-time recovery are the provider's documented responsibility. The candidate PostgreSQL image would then be used only for staging. Selection requirements:

- PostgreSQL major version 18, with a published security-patching policy or SLA.
- Private networking only (no public endpoint), with TLS enforced between the application and the database.
- Automated backups with point-in-time recovery, a retention period that meets the deletion and retention policy, and encryption at rest.
- Separate migrator and runtime roles with the same privileges as `deploy/roles.sql.example`.
- Acceptance before cutover:
  - run `tools/verify_postgres.py` against a disposable schema;
  - run a native restore drill into a separate database, using the FINAL_DELIVERY backup and recovery steps;
  - run the browser and outage checks against the target.

Choosing a provider, region, budget and operator is an owner decision and is not made here.

## Re-check procedure

From the project root, with Docker running:

```powershell
$docker = "$env:LOCALAPPDATA/Programs/DockerDesktop/resources/bin/docker.exe"
& $docker run --rm --entrypoint sh postgres@sha256:10a5c69a83035ab5239f5620d708520e8b28f5aa1f2b20143e6024532edadfb5 -c "apk update -q; apk policy libxml2 sqlite-libs"
```

The record changes only if a version newer than `libxml2 2.13.9-r2` or `sqlite-libs 3.53.4-r0` appears. When it does:
1. Pin the new version in the candidate recipe.
2. Rebuild with a new tag.
3. Run `docker scout cves` on the new image.
4. Repeat the review acceptance described in [POST_HANDOFF_REVIEW](history/POST_HANDOFF_REVIEW.md).
5. Close the item here.

## Approval

| Field | Value |
| --- | --- |
| Decision | ☐ Approved as proposed ☐ Approved with changes ☐ Rejected |
| Changes / conditions | |
| Approved by (owner) | |
| Independent security reviewer (recommended) | |
| Date | |
| Expiry | 12 December 2026 unless changed above |
