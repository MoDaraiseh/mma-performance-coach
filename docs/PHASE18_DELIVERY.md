# Phase 18 isolated staging and launch-blocker report

Prepared **2026-11-01** (Asia/Dubai). Readiness: **Local release candidate**. Not staging-ready or production-ready. Local preparation and feasible verification are complete; the actual container/PostgreSQL/private-infrastructure and external review gates remain open. No public deployment, production secret/database access, purchase, paid API call or original tracker/athlete-data alteration occurred.

## Integrity and changes

Verified release `v1.0.0-rc.17` resolves to `2f43e4d66e76e921bc40d3840611c347ab9824c8` and all recorded source/build/evidence manifest hashes matched before changes. Created separate branch **phase18-isolated-staging**. The tag, master release commit and original Phase17 manifest/evidence are preserved; no tag moved or release file was overwritten. New source commit/evidence hashes are recorded independently in `evidence/phase18/phase18-manifest.json`.

Implemented:

- `tools/prepare_staging.py`: new private output only, outside/existing-destination guards, fresh separate credentials/configs, sanitized context and file hashes; no service startup or `.env`/athlete-data read.
- `deploy/compose.staging.json` / `staging-init.sh`: loopback-only apps, internal network, ephemeral PostgreSQL source and separate restore databases, bootstrap/migration/runtime role separation, no runtime superuser/create privileges, one-time migration job and opt-in restore app. Application images use local-build/pull-never policy. Shell scripts retain LF through project-local attributes. Container/SQL behavior remains unexecuted.
- Technical exclusion of all 11unresolved original fighter records **before** creating the build context/layers. Internal original data stays intact; the candidate includes eight attributed supplement records, fighter notice and two full font notices. Local sanitized-app workflow proves eight-row matching and plan/account behavior. This is not qualified legal clearance or a complete SBOM. The repository/history still contains original records and must not be published as a rights-cleared source release.
- `app/monitoring.py`: fixed-label local readiness/error/auth/budget signals with conservative counter-reset/small-sample behavior; no notification/network/personal-data output. Operator snapshot report includes readiness/budget signals; two saved snapshots enable error/auth deltas.
- Twelve new regression cases, full synthetic reviewer output generator, updated specialist packs/methodology inventory, current legal/privacy/consent checklist, launch matrix and detailed staging/separate-DB recovery/security procedures. Training/nutrition equations and approved-plan workflows are unchanged; no new schema migration beyond0008.

## Actual tests and evidence

| Check | Actual result |
| --- | --- |
| Full backend Pytest | **370 passed**, zero failed, **80.76s**, two upstream Starlette/Authlib httpx deprecation warnings; [log](evidence/phase18/backend-tests.log) |
| Final focused staging/monitoring suite | **12 passed**,3.99s after final context/config/notice refinements; included in370, not12 additional unique tests; [log](evidence/phase18/final-focused-tests.log) |
| Frontend Vitest | **12 passed**, four files,3.92s; [log](evidence/phase18/frontend-tests.log) |
| Full Edge browser regression | **168 passed, zero failed, seven intentional skips**,175 scheduled, **649.39s**, native exit0; [native report](evidence/phase18/browser-results.json), [log](evidence/phase18/browser-run.log) |
| Browser scope | Installed Edge/Blink155, widths1440/1920/768/390/375, synthetic local SQLite API, all workspace/journey/log/proposal/export/delete flows. Source checkout uses19records; sanitized8-record candidate has separate real local TestClient workflow, not container-browser acceptance |
| Accessibility/print | Forty core-view axe scans report zero targeted violations/runtime errors; five A4 reports/18 nonblank pages with no text outside20pt margins; [print checks](evidence/phase18/print-checks.json). No manual screen-reader, physical-device or other-engine test was run in this phase |
| TypeScript/browser TypeScript/Vite | Passed through frontend/browser commands; [build](evidence/phase18/build.log) |
| Ruff/Prettier/pip consistency | Passed,84 Python files formatted; [lint](evidence/phase18/ruff-lint.log), [format](evidence/phase18/ruff-format.log), [Prettier](evidence/phase18/prettier.log), [pip](evidence/phase18/pip-check.log) |
| Dependency advisories | Fresh npm and38pinned Python dependency scans report zero known vulnerabilities; [npm](evidence/phase18/npm-audit.json), [Python](evidence/phase18/python-audit.json). These are not actual image scans or a penetration test |
| Shell/config | Git Bash `-n` syntax passed for init shell; JSON structure/isolation/separate credentials tested. Docker Compose config/build/runtime and PostgreSQL SQL were **not executed** |
| Sanitized context | Actual local migration upgrade/check, ready/operator report, registration/demo, eight licensed-source records, matching/training/nutrition and delete/recovery denial passed; no original record/file modified |
| SQLite recovery | One synthetic user/two plan versions, head0008, source unchanged, restored sessions invalidated; [report](evidence/phase18/backup-restore.json). Total temporary migration/fixture/backup/restore/check rehearsal **1.387s**; [timing](evidence/phase18/recovery-timing.json). Not PostgreSQL or production RPO/RTO |
| Local alert exercise | Five fixed signals from synthetic DB-not-ready/5xx/auth/AI80% snapshots; no external notifications; [CLI output](evidence/phase18/alert-cli.json), [fixtures/results](evidence/phase18/local-alert-evidence.json). Actual alert delivery/cadence unconfigured |
| AI safety/budgets | Full suite includes mocked schema/provider failures, retry/deadline/context/output limits, per-account quota, concurrent daily/monthly reservations, authorization/version/injection/exhaustion guards. Eighteen offline scenarios executed with zero live attempts; [offline report](evidence/phase18/offline-coach.json). Actual provider billing/project controls remain unverified |
| PostgreSQL runtime/version/native restore | **BLOCKED / NOT RUN**: no Docker/server/psql/pg_dump/pg_restore or authorized test URL; [availability](evidence/phase18/runtime.json). Recipe postgres:18 is not an observed version. Native separate-database recovery/rollback duration is unknown |

Seven skips are intentional: drawer checks excluded at three nonmobile widths; fixed A4 paper layout executed once rather than repeated at four other viewports. Phase17's UTC fixture correction is included in this fresh complete green run; no failure was hidden/reclassified. Evidence is local and Git-ignored; archive it privately with source/context hashes. Browser traces and generated credentials must not be published.

Full regression commands follow [TESTING](TESTING.md); Phase18 uses `MMA_QA_PHASE=phase18`, `PW_REPORT_FILE=../docs/evidence/phase18/browser-results.json`, `PW_EVIDENCE_DIR=../docs/evidence/phase18` and dedicated `.qa-runtime/pytest-phase18` basetemp. Final focused suite uses its own QA folder. Advisory/browser commands required authorized network/process access; no service was provisioned. Restore and source inventory tools now route Phase18 evidence without overwriting prior phases.

## Blocker status and remaining work

The [launch-gate matrix](PHASE18_LAUNCH_GATES.md) records each gate/status/closure action. The [staging procedure](PHASE18_STAGING.md) gives exact local recipe/role/isolation design, guarded PostgreSQL tests, separate `mma_test_stage`→`mma_test_restore` backup/validation/app smoke, timing/rollback safeguards, identity/TLS workflow and independent security-review scope. Those runtime procedures remain prepared, not executed.

Live identity: no authorized synthetic IdP tenant/credentials are available. Signed mocked OIDC/session/recovery/linking tests pass, but real MFA/recovery/logout/rotation and provider policy are unverified. Loopback test-mode HTTP/local recovery deliberately does not satisfy production HTTPS/OIDC/cutover. No production secrets were inspected to fill this gap.

Fighter rights: [11-record source/right audit](evidence/phase18/original-fighter-rights-audit.json) establishes no affirmative redistribution permission. Direct UFC terms access returned403; no bypass/scraping/new permission was attempted. Build-time exclusion is verified, while actual image contents and intended eight-record CC-BY-SA attribution/share-alike/distribution need qualified review. USDA CC0 source terms were reopened;55 historical foods remain composition data, not allergy/certification/clinical adequacy guarantees.

Specialists: all four reviewer packs,31-method inventory and seven updated selected examples remain unsigned/PENDING. New [full examples](evidence/phase18/specialist-full-examples.json) include all 12 weeks and all 7 nutrition days where generated; minor/rapid-cut/unknown-allergen cases honestly withhold numerical meal plans. `tools/build_staging_review.py` reproduces them. No reviewer opinion, signature, credential or professional approval was invented.

Legal/privacy: [internal checklist/drafts](PHASE18_PRIVACY_LEGAL_REVIEW.md) cover entity/jurisdiction/audience, sensitive inputs, optional third-party AI, consent, retention, deletion/backups, terms, data/content rights and safety notices. Owner/reviewer approval fields remain blank. No policy/terms was published or legal compliance asserted. A public versioned consent/support/retention system still requires owner/legal decisions and appropriate implementation.

## Next required approvals and readiness decision

To continue: authorize/install a suitable **local container runtime** (including any applicable licence decision), or provide a named explicitly authorized isolated PostgreSQL/private environment, operator access and synthetic test scope under a zero-cost/explicit ceiling. Review generated local-secret ACLs and image digest inputs before execution. No production credentials, public networking, paid provider or external notification service may be substituted.

Then execute real PostgreSQL/role/concurrency/migration and separate-database recovery/app tests, actual container/SBOM/image scan, private TLS/IdP/MFA/recovery, secret injection, monitoring delivery and incident/rollback rehearsal. Arrange independent specialist, security and legal/licensing/privacy/terms reviews; implement justified findings and retest. If live AI will be enabled, separately authorize bounded paid/live testing and verify actual provider spend controls; otherwise keep it disabled.

Only evidence can close these gates; owner approval does not waive them. **Public deployment is not appropriate and was not attempted. Staging configuration is prepared; staging readiness is not yet established.** The original approved release remains intact, and all changes/evidence are confined to this project/development branch.
