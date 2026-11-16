# Phase 18 private staging and verification procedure

Prepared 2026-11-01. Baseline `v1.0.0-rc.17` / `2f43e4d66e76e921bc40d3840611c347ab9824c8` is unchanged. Work is on **phase18-isolated-staging**. No public deployment, production credential/database access, purchase or paid API call is authorized. Local container execution is prepared but **not run**: Docker, PostgreSQL and native tools are absent. Actual server version is unknown; `postgres:18` is a mutable recipe input, not an observed runtime version or verified digest.

## Preparation already exercised locally

`backend/tools/prepare_staging.py` writes only a **new** directory under this project's ignored `.qa-runtime/`. It refuses outside destinations and existing output, reads no `.env` or athlete database, and never starts services. It creates fresh separate bootstrap/migration/runtime random credentials, distinct app/migration/restore environment files and a sanitized build context. Do not print these files or commit them. POSIX modes are requested; Windows ACLs must be independently inspected/restricted before using the credentials.

The context copies an explicit selection of tracked runtime/build files, excludes backend tests, frontend test fixtures, Git/private/runtime files and the entire original 11-fighter implementation. Only a generated empty `reviewed_records()` interface and eight attributed supplement records remain. Full fighter and two font notices are copied into the generated Dockerfile's final-image instructions. This is technical exclusion, not blanket legal clearance or a complete dependency SBOM. Internal original data/source and all athlete data remain intact.

Tests migrate and exercise the sanitized candidate with **disposable SQLite**, including readiness, account creation/demo, eight-row fighter search/matching, saved training/nutrition and account deletion/recovery denial. This proves local candidate application compatibility; it does not prove a Docker build or PostgreSQL runtime. Prepare the final context from the committed branch, using the supplied default destination:

```powershell
# From backend, after locked frontend dependencies are installed:
..\.venv\Scripts\python.exe tools/prepare_staging.py
```

Default output: `.qa-runtime/phase18/`; alternate validation output can be selected with `--destination`, but the Compose recipe points specifically at the default folder. Never reuse/reset an existing folder to bypass the no-overwrite guard; choose a new owner-approved disposable directory and adjust a copied local recipe if necessary. Secret values are not printed. Preparation hashes every context file in `preparation.json`.

## Container isolation and role design

`deploy/compose.staging.json` is Docker Compose's supported JSON-form configuration. It has a fixed project name `mma-phase18-isolated`, internal network, no PostgreSQL host port, disposable tmpfs DB storage, app bound only to127.0.0.1:18018 and an opt-in restore app bound only to127.0.0.1:18019. Application images use pull_policy=never: build the reviewed local context first; do not pull an arbitrary project-named image. App/migration containers are nonroot, read-only, no capabilities, no-new-privileges, with temporary /tmp. No host athlete database or original tracker is mounted.

Bootstrap reads separate local password files; `deploy/staging-init.sh` creates `mma_test_stage` and `mma_test_restore`, a non-superuser owning migration role and a separate non-superuser runtime role without CREATE/CREATEDB/CREATEROLE. Runtime gets only CONNECT, schema USAGE and table DML/sequence permissions; it receives neither admin nor migration password. Default privileges cover migration-created tables. Init runs only on fresh disposable DB data. The runtime-role design is source-reviewed/tested structurally, **not verified against an actual PostgreSQL server**.

Synthetic loopback mode uses APP_ENV=test, local recovery, HTTP cookies, no live IdP, OPENAI_API_KEY blank, global AI ceilings0, retention disabled. These deliberate local-only settings **do not pass production gates** and must not be publicly exposed. Internal runtime network blocks external providers; Docker build dependency/image downloads would still require network. No build/download was attempted here.

## Runtime steps when prerequisites are available

1. Confirm Docker context/daemon is **local and owner-authorized**, no remote DOCKER_HOST/context, available memory, free loopback ports18018/18019 and no existing project collision. Confirm secrets folder ACLs. Do not install/licence Docker, buy services, publish ports broadly or use a production daemon without new authorization.
2. Review generated context/hashes and notices. Supply verified NODE_IMAGE/PYTHON_IMAGE/POSTGRES_IMAGE digest references and record selected digests. Current defaults are unpinned local placeholders. Inspect `docker compose -f deploy/compose.staging.json config --quiet` without rendering secret environment values to shared logs. JSON structural tests here are not execution of that command.
3. From project root, build/start only this isolated project:

```powershell
docker compose -f deploy/compose.staging.json build migrate app restore-app
docker compose -f deploy/compose.staging.json up --no-build -d app
docker compose -f deploy/compose.staging.json ps
```

Migration job runs `alembic upgrade head` once, before app start. Verify migration exit0, health/readiness at local18018, DB role privileges, runtime inability to create schemas/tables and actual server version via `SELECT version()`. Archive redacted logs, exact branch commit, image digests, Alembic head0008 and evidence. Do not infer actual versions from image names.

4. Run `alembic check` through the isolated migration service. Run existing guarded PostgreSQL tooling from a one-off migration container with the synthetic URL already in that container's DATABASE_URL:

```powershell
docker compose -f deploy/compose.staging.json run --rm migrate python -m alembic check
docker compose -f deploy/compose.staging.json run --rm migrate sh -c 'MMA_TEST_DATABASE_URL="$DATABASE_URL" python tools/verify_postgres.py'
```

The guarded tool accepts only `postgresql+psycopg` and `mma_test*`, creates/drops a random qa_hex schema and tests upgrade/check/down/up, FK rejection, rollback, concurrent writes, owned API data/export/deletion and plan versions. It never substitutes a normal athlete URL. Set no `MMA_TEST_RESTORE` in that Python image: native tools are not installed there. Its existing optional same-database schema restore does **not** satisfy the separate-database recovery gate below. Preserve failures and timing, never call this passed unless executed successfully.

## Separate-database backup, restore and rollback rehearsal

Not executed. Source is `mma_test_stage`; destination is the **separate, initially empty** `mma_test_restore` created by init. Never target a different database, public/production system, existing user database or normal DATABASE_URL. Names alone are not permission; inspect the exact local container/role/DB before execution.

1. Create only synthetic users, measurements, two approved plan versions, exercise logs and proposed/rejected changes through the source app. Record expected owned records, versions, payload hashes and schema. Keep synthetic recovery credentials private; do not place bearer values in reports/command-line arguments.
2. Using the database container's native tools and migration password file, make a custom-format archive of `mma_test_stage` to a new /tmp filename. Avoid URLs/passwords in CLI logs. Example inside the isolated database container: set `PGPASSWORD` from `/run/secrets/migrator_password`, then `pg_dump -h127.0.0.1 -Umma_stage_migrator -dmma_test_stage --format=custom --no-owner --file=/tmp/phase18.dump`. Do not echo the password; no set-x. Inspect `pg_restore --list` and hash the archive with SHA256. Copy a private synthetic archive to the generated backups folder, never overwrite an existing backup.
3. Confirm destination has no user tables. Inspect archive schema entries first: if restoring a CREATE public schema entry would conflict with init-created empty public, stop for a reviewed restore list omitting only that redundant schema/ACL entry; never force cleanup or omit data silently. Restore with the same owner role into `mma_test_restore`, `pg_restore --exit-on-error --no-owner --no-privileges -h127.0.0.1 -Umma_stage_migrator --dbname=mma_test_restore /tmp/phase18.dump` (with the reviewed `--use-list` when required). Do not use `--clean`, drop a database, or overwrite the source. Verify runtime default grants, head0008, FKs, per-table counts and representative exact profile/plan/log payload hashes against the source. An archive hash alone does not prove restored-data integrity.
4. In the disposable restored DB only, invalidate login sessions/OIDC flows before serving restored data, then verify two synthetic owners can recover their own accounts, cannot access each other's records, see both plan versions/logs, approve only fresh proposals and export/delete only owned data. Use the opt-in `restore-app` profile; it reads only restore.env and connects to the separate restore database:

```powershell
docker compose -f deploy/compose.staging.json --profile recovery up -d restore-app
```

5. Record start/end monotonic recovery timings, actual pg_dump/server/pg_restore versions, archive hash, source/destination identifiers, validation results and synthetic app smoke results. Deliberately fail only a disposable copy/configuration to rehearse recovery; retain source intact. Confirm original staging records unchanged before marking the rehearsal successful. Do not equate synthetic recovery with achieved production RPO/RTO.
6. Stop only this specific local project after evidence capture. Data resides in tmpfs and is disposable; stopping/recreating the database can discard it. No cleanup command should be run against a shared/existing project. Keep private evidence/backup under approved retention; do not touch parent tracker or athlete files. Staging rollback is restart of an approved prior **sanitized** artifact against a compatible disposable DB, or restore to another new disposable destination; never a blind downgrade/deletion.

See [PostgreSQL logical backup guidance](https://www.postgresql.org/docs/current/backup-dump.html). No backup encryption, hosted recovery, WAL/PITR or production objectives are claimed by these local instructions.

## Identity, HTTPS, monitoring and security acceptance

Live identity is not configured/authorized. Preserve signed mocked OIDC regressions; prepare a dedicated synthetic IdP tenant with exact loopback/TLS staging callback, fresh login/auth_time, nonce/state/PKCE replay, two-account linking/conflicts, expiry/revocation/logout, MFA/lost-device/recovery and explicit legacy-cutover checks. Do not use real users/production clients. Provider logout/deactivation does not automatically revoke app sessions; independently test and document that limitation. Production settings require HTTPS/OIDC and explicit cutover; loopback local mode cannot establish those gates.

Local HTTP is intentionally limited to loopback and is **not TLS acceptance**. Before any wider private environment, configure approved TLS/proxy, exact hosts/origin/trusted peers, secure cookies, secret injection and request limits and rerun isolation/CSRF/abuse tests. No wildcard CORS or forwarded trust should be added to make a test pass. Generate actual image SBOM/dependency/font notices and scan the built image; current advisory scans cover Python/npm locks only.

`python -m app.operations` is an operator-only aggregate snapshot; it now includes local readiness/budget signals. `python -m app.monitoring --current snapshot.json --previous previous.json` compares deidentified saved snapshots and emits fixed-label local signals only. Snapshot cadence/window/notification routing are not configured. Synthetic Phase18 fixtures test DB/migration outage, >=5%5xx with >=20responses, five failed sign-ins and80%AIattempt reservation. Counter resets/small samples are conservative; lifetime latency buckets do not establish windowed p95. No external email/webhook/page is sent.

Independent security-review package: exact branch revision/context hashes, software/schema/role map, two synthetic credentials transferred privately, bounded local scope, no paid providers and stop-on-cross-account/data-corruption rules. Test real TLS/proxy spoofing, auth/recovery/MFA/link replay, object ownership, stale approval races, prompt/tool injection, rate/body limits, log leakage, roles/backups and restart. Require severity/reproduction/evidence, remediation and independent retest. Reviewer identity/date/signature/acceptance remain blank. Automated safety/security tests do not establish a penetration test.
