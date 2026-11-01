# Phase 22: local Docker ingress and PostgreSQL browser acceptance

Date: 2026-11-01. **Ingress repaired; real Edge-to-PostgreSQL acceptance passed.** Full staging/release readiness is not asserted: the outage/collector and broader release limitations below remain open. No public deployment occurred.

## Root cause and repair decision

The healthy app was attached exclusively to the internal `mma-phase18-isolated_isolated` bridge. Its requested binding was `127.0.0.1:18018:8000`, but the container had no default gateway, effective Ports was `{"8000/tcp":[]}`, and Windows had no corresponding listener. The app was already listening correctly on `0.0.0.0:8000` inside its container. Effective Compose configuration retained the requested binding; configuration was not evidence of publication.

This is the behavior explained by a Moby maintainer in [upstream discussion 53256](https://github.com/moby/moby/discussions/53256): publication is wired through a container's default-gateway network; an internal-only container has none. The recommended remedy is a separate proxy attached to internal and ordinary bridge networks. [Docker port-publication documentation](https://docs.docker.com/engine/network/port-publishing/) describes explicit loopback bindings and gateway semantics. Host firewall and service changes were neither needed nor performed.

Implemented the separate-proxy option, preserving app/database isolation:

```text
Windows Edge -> 127.0.0.1:18018 -> secret-free TCP relay :8080
                                      |
                           existing internal bridge
                                      |
                                 app :8000 -> PostgreSQL :5432
```

Only the relay joins the new ordinary bridge. App and database remain on the original internal network; the app still has no outbound default route. The relay has potential outbound routing but its code connects only to fixed `app:8000`, accepts no target from Host/URL/environment, and has no database or AI credentials. No outbound service request was made. This narrowly bounded ingress boundary is not an assertion of independent proxy/security review.

## Exact source/configuration changes

- [compose.ingress.json](../deploy/compose.ingress.json): separate project `mma-phase22-ingress`, one ingress service, existing sanitized image pinned to digest `sha256:4445750e0135806ee6099c9daf509d6f862e1fb4169d98539606f794ff02398b`, pull disabled; existing internal network declared external; one new bridge; **only `127.0.0.1:18018:8080`** published.
- [staging_relay.py](../deploy/staging_relay.py): transparent fixed-upstream TCP relay. It preserves HTTP/Host/Origin/cookies, logs no request bytes or identities, limits concurrent connections to 32, bounds upstream/send/idle/connection lifetime, and supports half-close/streaming. No HTTP security middleware was modified.
- Relay controls: UID 10001, read-only root, all capabilities dropped, no-new-privileges, 64 PID / 128 MiB / 0.5 CPU bounds. Its only bind mount is the relay script, read-only. It receives no staging env file or secret mounts.
- [playwright.staging.config.ts](../frontend/playwright.staging.config.ts) and [staging-e2e](../frontend/staging-e2e/journey.spec.ts): dedicated external PostgreSQL browser suite, fixed loopback base URL, **no webServer/SQLite fixture**, no API mocking. Trace capture disabled because synthetic recovery credentials flow through requests. Browser TypeScript configuration includes the new suite.
- [test_phase22.py](../backend/tests/test_phase22.py): real socket regression for large binary payloads, half-close and unchanged request bytes/target despite an arbitrary Host header.
- Generated staging test outputs ignored; no original Phase 18 context, credentials, Compose model, application features or database schema changed. The 89 prepared context hashes still match.

## Preservation evidence

Source revision at verification: `9b4cf86450a7f46243aa6ecfdb8e7c4dfbdd42a0`, branch `phase18-isolated-staging`. Original release tag remains `v1.0.0-rc.17` -> `2f43e4d66e76e921bc40d3840611c347ab9824c8`.

Before changes, exact project labels, full container/image IDs, start timestamps, network membership, bind/tmpfs mounts, data hashes and archive hashes were saved. These existing containers retain their **exact IDs, images and start timestamps**:

| Existing service | Container ID prefix | Final state |
| --- | --- | --- |
| PostgreSQL | `96ae890980a3` | Running, healthy |
| Source app | `eee16a46eac3` | Running, healthy |
| First restore app | `0f2c72d307f9` | Running, healthy |
| Completed migration job | `9e920cd02592` | Original exited-0 job preserved |

No existing container was stopped/recreated/restarted, and no `down`, prune or broad cleanup command was used. PostgreSQL's `/var/lib/postgresql` remains the same 512 MiB tmpfs. Its container-local archives `/tmp/phase21.dump` and `/tmp/phase21b.dump` retain their SHA256 hashes. No protected backups directory or ACL changed.

After browser fixture cleanup, all original canonical count/row hashes match: **4 users, 26 records, 8 fighter snapshots, 2 division references**. The initial assertion-failure fixture was cleaned using its exact generated name and post-snapshot record timestamp, through normal account deletion with an in-memory synthetic test session. No pre-existing account was targeted. Successful journeys verify deletion through the UI; afterEach/finally cleanup is limited to each new test's own account contexts.

Evidence: [before.json](evidence/phase22/before.json), [after.json](evidence/phase22/after.json), [fixture cleanup](evidence/phase22/fixture-cleanup.json).

## Before/after Windows connectivity

| Check | Before | After |
| --- | --- | --- |
| App's effective publication | Empty | Remains empty; original app untouched |
| New relay effective publication | Absent | `8080/tcp -> 127.0.0.1:18018` |
| Windows listener | Absent | **127.0.0.1:18018 only** |
| Host GET `/api/ready` | Cannot connect | **HTTP 200**, `{"status":"ready"}` |
| PostgreSQL host binding | None | None |
| Existing restore publication | Ineffective | Still not repaired/published; no restore ingress was needed for the primary journey |

Docker Desktop logs show actual `exposer.Add` / forwarding to relay `172.19.0.2:8080` on the loopback address. The listener snapshot contains no wildcard/IPv6/public app binding and no host PostgreSQL listener at 5432. No external-machine connectivity test was attempted; the claim is supported by actual binding/listener inspection rather than public probing.

## Real browser acceptance: PostgreSQL, not SQLite

Final command: `npx playwright test --config playwright.staging.config.ts`, using installed Edge, one worker and the existing local container app. **10 passed, 0 failed, 0 skipped, 0 flaky; 80.439 seconds; runner exit 0.** Each of the five widths (1440, 1920, 768, 390, 375) ran the complete journey and session/ownership/security case.

The journey exercised:

1. New synthetic account and all onboarding steps: physical measurements, boxing experience/frequency/coaching access, strength benchmark, availability, goals/diet and profile save.
2. Physical assessment and divisional reference, verified-supplement fighter matching, configurable weights, search and saved comparison. It uses names actually present in the eight-row sanitized dataset rather than requiring excluded fighters.
3. Generated training, actual exercise repetitions/load and session logging.
4. Nutrition generation, proposed lunch substitution, unchanged saved version before approval, approval as a new version, day-seven and grocery-list views.
5. Progress check-in, fatigue-based reassessment, deterministic offline coaching; provider control stays disabled.
6. Proposed plan change, reject then approve, preserved plan history.
7. Downloaded JSON athlete report, matching athlete name and two plan versions.
8. **Direct PostgreSQL SQL assertions** that the exact unique profile and per-exercise workout record exist in `mma_test_stage`, schema head 0008.
9. Screenshot, no horizontal overflow or browser JS errors in the tested journey, UI account deletion, unauthenticated profile denial and direct SQL confirmation of profile removal.

The second case verifies real owner isolation and cross-account write rejection; HttpOnly, **SameSite=Strict** session cookies; secure=False only because this is explicitly HTTP loopback test mode; invalid Host 400; untrusted Origin 403; and CSP/nosniff/frame DENY headers. No response mocking or security bypass is used. This does not satisfy production Secure-cookie/TLS/live-IdP acceptance.

Initial attempts are disclosed:

- First desktop journey failed on a test selector expecting the full name in a heading that displays only the first name. Assertion corrected; product behavior unchanged.
- Next desktop run passed the journey but revealed that the test incorrectly expected Lax cookies; actual Strict is stronger. Test corrected to the implementation.
- First five-width run passed 9/10; last registration received a genuine HTTP 429. Registration fixtures now honor the actual Retry-After once (maximum 60-second wait), with no quota or middleware change. Final complete rerun passed 10/10.

[Final browser JSON](evidence/phase22/browser-results.json), [earlier five-width attempt](evidence/phase22/browser-attempt-five-widths.json), [desktop screenshot](evidence/phase22/desktop-1440-postgres-acceptance.png), [375 px screenshot](evidence/phase22/mobile-375-postgres-acceptance.png). Screenshots exist for all five widths. Full print/PDF or automated accessibility re-audit was not part of this new suite; earlier SQLite findings are not counted as PostgreSQL coverage.

## Application/security/monitoring verification

Whitelisted runtime configuration confirms driver `postgresql+psycopg`, database `mma_test_stage`, APP_ENV=test, allowed hosts `127.0.0.1,localhost`, UID 10001, blank provider key and daily/monthly AI budgets 0. Runtime counters show no outbound reservations. The app's existing read-only/nonroot controls and internal network are preserved. The ingress has no environment variable containing credentials/database/provider secrets and only the read-only script mount. No global Docker setting, Windows firewall, host service, BIOS or ACL was changed.

The existing guarded PostgreSQL verifier passed again using a fresh generated schema and `run --rm --no-deps`, with `testserver` allowed **only inside the verifier**: migrations up/check/down/up, FK, rollback, concurrency, ownership, plan versions, nutrition/export, account deletion and recovery denial. No dependency reconciliation or database recreation occurred.

After browser tests, **only the exact preserved PostgreSQL container** was briefly paused/unpaused with a finally-unpause guard. A custom bounded three-second readiness probe plus the existing alert evaluator emitted critical `database_not_ready`; after unpause head 0008/ready returned and alerts cleared. Windows loopback readiness returned 200 after recovery. No app/database restart or external alert was used. [Monitoring evidence](evidence/phase22/monitoring-result.json).

**Remaining operational defect:** the loopback readiness request during the pause timed out at the client's 1.5-second bound instead of promptly returning structured unavailable status. The bounded probe catches the outage, but the ordinary aggregate-report CLI/continuous collector still needs robust database timeout/error handling. This phase does not mark that broader monitoring gate passed. No TLS/proxy certificate, external IdP, full image CVE scan, new native recovery rehearsal, independent penetration test or professional/legal sign-off was claimed.

## New regression results

| Check | Actual Phase 22 result |
| --- | --- |
| Backend Pytest | **371 passed**, two upstream deprecation warnings, 83.12 s; fresh project-local basetemp |
| Relay regression | Included: real sockets, large payload and half-close |
| Frontend tests | **12 passed**, four files |
| Application TypeScript / Vite production build | Passed |
| Browser TypeScript | Passed including staging suite |
| Ruff check / changed Python format check | Passed; one test line reformatted before final check |
| Prettier | Passed for frontend, browser suites/configs and ingress JSON |
| PostgreSQL guarded verifier | Passed against generated disposable schema |
| Real Edge-to-PostgreSQL | **10 passed**, five widths; previous failed attempts retained/disclosed |

No prior Phase 18/21 counts are represented as new runs. Detailed local inspection/scripts remain in ignored `.qa-runtime/phase22`; sanitized evidence is under ignored `docs/evidence/phase22`. Generated traces/request credentials are excluded from source control.

## Operating and rollback procedure

From the project root, with the installed Docker bin directory in the current process PATH, first verify local context, exact original container IDs/data hashes, existing internal network and port availability. Then:

```powershell
# Separate project: never reconciles/recreates the original database or app.
docker compose -f deploy/compose.ingress.json config --quiet
docker compose -f deploy/compose.ingress.json up --no-build --no-deps -d ingress
docker compose -f deploy/compose.ingress.json ps
Invoke-WebRequest http://127.0.0.1:18018/api/ready -UseBasicParsing

# Explicit ingress-only rollback, if desired; do not run it to stop PostgreSQL.
docker compose -f deploy/compose.ingress.json stop ingress
```

The pinned local image must already exist and be the reviewed sanitized artifact. Do not replace it with an arbitrary image, run base-project `up` from a different image-variable environment, or use `down`/prune. PostgreSQL and its archives remain ephemeral; stopping/recreating that database can lose them. The original app's ineffective requested mapping remains historical configuration; the new relay owns the working host port.

## Updated launch-gate matrix

| Gate | Result |
| --- | --- |
| Root cause / isolated repair / Windows loopback | **Passed** |
| Existing containers, data, archives, credentials and release tag | **Preserved**, IDs/start times/hashes verified |
| Real UI journey with PostgreSQL persistence/deletion | **Passed**, all five widths |
| Session/ownership/origin/host/listener protections | **Passed** in HTTP local-test scope |
| Migration/concurrency/versioning regression | **Passed** |
| Pause/unpause local alert and recovery | **Passed** for bounded probe/evaluator; normal readiness timeout and continuous collector **open** |
| Restore-app host ingress | Not repaired; not part of primary endpoint acceptance |
| TLS, live identity, full image scan, durable backup retention, independent reviews | **Open/unverified**, no new authorization or completion claimed |
| Full staging/release readiness | **Not declared** while these applicable gates remain open |
| Public deployment | **Unauthorized; not executed** |

Final state: original containers still running/healthy, completed migration job unchanged, new loopback relay healthy. The tested application is accessible at **http://127.0.0.1:18018**. No production credential/database or real athlete data was accessed; no original tracker change, paid AI request, purchase or public application exposure occurred.
