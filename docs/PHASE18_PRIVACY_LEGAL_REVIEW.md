# Phase 18 privacy, consent and terms preparation

Prepared 2026-11-01. **Internal review draft/checklist, not approved legal text and not ready to publish.** Applicable jurisdiction, controller/entity, audience, hosting and processors are unspecified. No qualified legal approval was supplied. Do not invent statutory rights, consent wording, retention promises or professional sign-offs. Complete owner fields and qualified review before launch.

## Owner and reviewer record — leave unapproved fields blank

Controller/legal entity: ____________________

Contact and privacy/rights request channel: ____________________

Audience, age policy and jurisdictions served: ____________________

Hosting region, operator and subprocessors: ____________________

Legal reviewer/credentials/jurisdiction: ____________________

Reviewed code/artifact revision and notice version: ____________________

Review date, approval status/scope and signature: ____________________

## Privacy notice content checklist

| Subject | Actual application behavior to disclose/review | Owner decision/evidence needed |
| --- | --- | --- |
| Athlete information | Self-reported age/measurements/metabolic inputs, goals, experience, schedule, dietary preferences/allergies, injury/recovery notes, logs/progress and achievements | Classify sensitivity/lawful processing for intended jurisdiction; minimize optional health-related data; no verified clinical facts implied |
| Purpose | Educational deterministic assessments, plan templates, nutrition estimates, heuristic fighter study comparisons, history and explicit proposed-change workflows | Document permitted scope; no professional proficiency/diagnosis/clinical nutrition claim |
| Identity/session | Hashed bearer sessions and owned revocation; local recovery in loopback mode; optional managed issuer/subject linking, no email-based merging | Real provider, tenant, recovery/MFA/logout and supported identity claims; separate provider/app session retention |
| AI processing | Optional server-side configured provider receives bounded current context; stored/user/external prose is untrusted and cannot grant actions | Named processor/model, exact categories transferred, location/retention/training-use terms, contractual review, user choice and withdrawal behavior |
| Offline mode | Deterministic coach and calculations function without provider; Phase18 staging has blank key, zero budgets and no external runtime network | State which capabilities are local, which require external processing and which requests remain unsupported |
| User control | Profile/preferences editable; explicit plan proposals require separate approval; account JSON/CSV/report exports and deletion are ownership-scoped | Explain supported correction/deletion interfaces, identity verification for support and unresolved measurement-correction UI limitations |
| Retention | Automated retention is disabled by default; when explicitly enabled, configured draft/conversation policies apply. Approved plans/progress/history are protected by current maintenance scope | Choose and implement lawful per-category schedules; do not promise all records expire after30days. Backups/logs have separate pending schedules |
| Deletion/backups | Local account deletion removes owned application records/sessions; older backups require reconciliation before restored service | Define backup expiry, restore-time erasure reconciliation, residual logs, confirmation and support escalation; test in real infrastructure |
| Logs/monitoring | Template route/status/duration and fixed aggregate counters; operator snapshots/alerts exclude names/raw URLs/notes/token labels | Actual access controls, storage, retention and incident investigation policy; no raw callback/query logging |
| Cookies/local storage | Same-origin session/OIDC state cookies; UI draft behavior and account-recovery display require exact browser-storage review | Publish names/purposes/expiry/security attributes, persistence and consent rules for target jurisdiction; no unsupported cookie-compliance claim |
| Data recipients/security | No hosting/secret manager/external collector configured here; production controls remain unverified | Identify actual vendors/regions/transfers, roles, encryption, breach-response process and real security measures before making promises |
| Requests/complaints | No owner-approved public privacy channel or service response policy exists | Establish contact, verification, escalation, applicable rights and response obligations with qualified review |

## Consent and user-understanding checklist

- Separate account/notice acknowledgement, optional sensitive-input processing and optional third-party AI processing where legally required. Plan-change approval is **not** a substitute for privacy consent.
- Explain the exact fields sent to the selected provider before opt-in; support meaningful offline choice. `use_ai` is an invocation flag, not proof of compliant informed consent.
- Define a versioned notice/consent record, timestamp, scope, withdrawal and audit retention if required. These are **not implemented as a public consent system** in this phase.
- Validate youth eligibility/guardian requirements for the chosen service jurisdiction; the app's conservative under18 training/nutrition boundaries do not establish legal parental consent.
- Ensure consent cannot silently enable paid calls, mutate approved plans or authorize provider tools. A separate explicit approval is required to persist each supported plan proposal.
- Do not require allergy/medical details unnecessary for service. Unknown allergen metadata is not absence, and no meal is certified by this catalog.

## Terms of service content checklist

Define owner/entity/contact, permitted audience/age/jurisdictions, account and recovery responsibilities, acceptable use, service availability and support, pricing (if any; no paid service has been authorized here), updates/termination and dispute/complaint process with counsel. Do not select governing law or invent liability waivers on the owner's behalf.

State application limitations: educational estimates/templates, self-reported data, nonclinical guidance, no fighting-potential prediction or professional-athlete equivalence, no event eligibility/target fight weight, no rapid dehydration/weight cuts, no rehabilitation or medical diagnosis. Contact training, throws/submissions and injury-sensitive work require qualified supervision; symptoms and medical/competition nutrition needs require appropriate professionals. No expert has approved this application.

Explain versioned plans/history, explicit approval/rejection, source/staleness checks, unsupported AI actions, sparse/missing fighter information and the distinction between numerical similarity and professional skill. Describe optional provider failures/offline fallback without promising truth or uninterrupted operation. Preserve data export/deletion rights according to the approved privacy policy.

## Content/data rights checklist

All11original fighter records retain unresolved rights; `original-fighter-rights-audit.json` records source URLs/status without relabeling permissions. The staging context excludes the entire original module before Docker COPY; source/internal data remain preserved. Direct UFC terms access again returned403, with no bypass or permission inference. No legal determination that those records may be distributed was established.

Eight staged adaptations retain [article/history/source/change/CC-BY-SA notices](FIGHTER_SUPPLEMENT_LICENSE.md). [Wikimedia reuse terms](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#7._Licensing_of_Content) were reopened; actual attribution/share-alike/trademark and intended distribution still need qualified review. Technical exclusion is not a blanket license for application code or the whole artifact.

[USDA terms](https://fdc.nal.usda.gov/api-guide/) identify FoodData Central composition as public-domain/CC0; preserve the existing55-food source/version/units and editorial uncertainty. Composition does not establish halal certification, absence of allergens/cross-contact, current prices or complete micronutrient adequacy. Preserve font/icon/library notices and generate the full built-image SBOM/license inventory before publication. No fighter photograph/logo/biography or new external feed was added.

## Acceptance gate

Complete owner fields; review actual deployed data flows/vendors and targeted audience; implement required consent/storage/retention/support controls; validate deletion/backup reconciliation and third-party terms; obtain dated exact-revision legal review. Leave approval pending until genuine evidence exists. These drafts/checklists cannot close the public-launch gate by themselves. No policy was published and no consent/legal approval is claimed.
