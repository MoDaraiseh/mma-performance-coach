# Phase 17 security, professional and licensing acceptance

2026-11-01. Automated inspection/regression only. This is not a penetration-test certificate, legal opinion or qualified sports-science approval. Source baseline `95651d9`; Phase 17 changes are release/QA tooling and documentation, preserving application/domain behavior.

## Security and infrastructure

| Control | Actual acceptance evidence | Remaining gate |
| --- | --- | --- |
| Owned data/actions/export/deletion | Full Pytest includes cross-user denial, version/source-bound approval, concurrent writes and deletion/expired session cases; browser journeys exercise persistence | Repeat against actual PostgreSQL/private deployment and independent pentest |
| OIDC binding and replay | Authlib cryptographic signed mocked transports test issuer/audience/expiry/nonce, PKCE, single-use state, linking conflicts; Phase 16 auth_time cases pass | Real tenant/key rotation/clock/MFA/lost-device and recovery-policy tests |
| Production cutover | Release policy blocks legacy recovery, missing acknowledgement/unlinked issuer; no automatic credential replacement | Owner-approved migration and verified access for all users; IdP deactivation does not automatically revoke app sessions |
| Session protection | Independent hashed bearer sessions, owned revocation, HttpOnly/SameSite and secure production validation; five-width browser Settings tests | Actual HTTPS cookie/proxy and incident revocation exercise |
| Origin/host/body/rate limits | Automated negative/regression tests and shared counter/quota concurrency | Real edge/slow-client/forwarded-header configuration, deployment load and abuse tests |
| AI permissions/injection | Strict server schemas, primary-request permission checks, context/version binding, bounded retry/timeouts and budgets; mocked malicious/failure responses | Semantic safety remains incomplete; actual model quality/cost unverified. No live provider call authorized |
| Logs/monitoring | Route templates, fixed counters, no raw request/body/token labels, aggregate operator-only CLI; failures do not replace API errors | Deployed collector privacy/access, alert delivery, load overhead and log retention exercise |
| Database | SQLite FK/rollback/migration/version/isolation tests and synthetic restore; offline PostgreSQL SQL checks | PostgreSQL/native restore unavailable; no real runtime acceptance |
| TLS/secrets/container | Settings guard HTTPS/OIDC credentials/hosts; nonroot/read-only/proxy templates; healthcheck source reviewed | Unbuilt images, mutable defaults, no image SBOM/scan, no TLS/reverse-proxy/secret-manager target |
| Dependency advisories | Fresh npm and pinned-requirement Python scans report zero known findings | Point-in-time known-advisory query; not proof of absence of vulnerabilities or supply-chain security |
| Backups/retention | Disposable SQLite restoration preserves source/plan versions and clears restored sessions; dry-run retention code covered | Encrypted offhost PostgreSQL restore, deletion reconciliation and actual RPO/RTO/retention scheduling |

P1 public-release blockers remain: real infrastructure acceptance, managed identity/cutover, independent security review, licensed distribution packaging, and qualified review of claimed training/nutrition scope. No new P0 local workflow defect was found during this acceptance; remaining external risks are not downgraded by passing mocks. Use the scoped independent test package in [Phase 16 operations](PHASE16_OPERATIONS.md) and [Phase 17 launch runbook](PHASE17_LAUNCH_RUNBOOK.md).

## Professional review

Inspected all four review packs and the 31-method inventory. Reviewer names, credentials, signatures, approval scopes and dates remain blank. No independently signed feedback was supplied/found, so no correction or approval is attributed to an expert. Seven current generated examples are synthetic and deterministic. Publication references support general principles; they do not validate exact thresholds/templates or this application.

Required closure: named qualified MMA coach, strength/conditioning specialist, sports dietitian and medical/safety reviewer where appropriate assess exact revision, examples, population/exclusion criteria, contact/coaching requirements, fatigue/injury/youth boundaries, meal adequacy/allergy/certification uncertainty and competition referral. Track findings by method ID/severity; implement justified corrections, retest and obtain dated scope-specific dispositions. Retain original signed documents privately; publish only authorized statements. Do not label plans professionally approved until that evidence exists.

## Data and content rights

| Asset | Actual coverage/provenance | Acceptance and distribution restriction |
| --- | --- | --- |
| Original fighter records | 11 source snapshots; official-source observations, no acquired redistribution grant | **Blocked for public distribution.** Obtain actual permission or exclude from release artifacts. Do not alter rights labels to bypass gates |
| Fighter supplement | Eight Wikipedia-derived adaptations; article/history URLs, changes, attribution and CC-BY-SA 4.0 references | Preserve [supplement notice](FIGHTER_SUPPLEMENT_LICENSE.md), source/license links and adaptation/share-alike obligations. Operator/legal review of intended distribution still required |
| Fighter data overall | 19 dated snapshots, 11 men/eight women; not comprehensive/current roster, zero verified current professional records | Runtime gate skips production bundled seeding and validates rights metadata, but original files remain in source/build context. **Do not publish this checkout/image as a cleared package** |
| Nutrition | 55 historical USDA SR Legacy April 2018 foods, source archive hash/version and units; all nine tracked nutrients present | USDA public-domain/CC0 terms reconfirmed; preserve source attribution. Composition does not certify halal/allergen status or complete dietary adequacy |
| Exercise guidance | 49 original curated entries, 15 qualified-coaching-required | No borrowed professional endorsement or technique validation; qualified review pending |
| Fighter images/logos | No copied fighter photographs, UFC logos or article media found in frontend source assets | Do not introduce them without separate rights review. Referencing UFC does not establish trademark endorsement |
| Fonts/icons | Installed DM Sans and Barlow Condensed LICENSE texts identify SIL OFL 1.1; lucide-react package declares ISC | Retain full installed license/copyright notices in actual distributed artifact; verify built-image notices and dependencies before launch |
| Libraries/external APIs | npm/Python lockfiles, optional server-side provider and offline data import tooling | No blanket app/third-party commercial license approval. Generate full artifact SBOM/notices; review intended provider terms/data processing before enabling external calls |

Primary source terms reopened during Phase 17: [USDA FoodData Central licensing](https://fdc.nal.usda.gov/api-guide/) identifies CC0/public-domain composition; [Wikimedia Terms of Use](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#7._Licensing_of_Content) describes attribution/adaptation/share-alike requirements. These terms do not clear the original 11 records. Direct UFC terms access returned HTTP403; no controls were bypassed and no new collection/permission was claimed. No external fighter API, scraping, paid service or roster refresh occurred.

## Launch decision

Public launch is **not appropriate** at this point. Private synthetic staging verification is an appropriate next authorized exercise after the owner selects infrastructure and scope; staging readiness itself remains unaccepted. The owner must separately approve private environment/access and any costs, arrange professional/legal/security reviews, and later explicitly authorize the exact public release after blocker closure. No authorization is inferred from this checklist or tag.
