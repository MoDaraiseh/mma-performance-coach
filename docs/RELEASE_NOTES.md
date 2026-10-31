# Phase14 release notes

2026-10-31: consolidated acceptance of the existing local application. Preserved existing application workflows, personal databases, approved plans and the original tracker.

- Reran the combined backend, frontend, browser, accessibility, migration, security and dependency checks; exact actual results are recorded in PHASE14_ACCEPTANCE.md.
- Added a release feature matrix, user guide, AI configuration guide, explicit known limitations and public-launch gates.
- Added three-sample browser load/dashboard timing coverage at every configured viewport; timings are observations, not SLAs.
- Fixed evidence routing in the responsive QA test to honor PW_EVIDENCE_DIR. Earlier test code hard-coded Phase1 for accessibility summaries; the initial full run could replace those legacy summaries. Phase14 copies/rechecks provide current evidence; old summaries are not represented as immutable historical artifacts.
- Extended print inspection, API/fighter benchmark and synthetic restore evidence routing to Phase14. Expanded the offline evaluation CLI limit to the actual18-scenario set. No domain calculation, approval policy or personal record was changed.
- Current schema remains0008. Existing installations must back up and explicitly migrate before running. Do not interpret old phase-specific schema statements as the current head.

No public deployment, live paid AI evaluation or independent expert sign-off occurred. See PHASE14_ACCEPTANCE.md for the release decision and owner checklist.
