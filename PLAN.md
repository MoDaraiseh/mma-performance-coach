# Implementation plan

Build an isolated local application without changing the existing law tracker.

1. Core: validated athlete profile, local account sessions, SQLite persistence, physical calculations, sourced division references and three sourced fighter snapshots.
2. Programs: explainable style recommendations, time-bounded 12-week plans, dietary-aware seven-day meal estimates.
3. Tracking: comparison controls, saved comparisons, workout logs, progress, reassessment and explicit revision approval, optional structured OpenAI coaching.
4. Delivery: critical mathematical and API tests, frontend type/build checks, workflow verification, setup and methodology documentation.

Decisions: canonical metric units; missing measurements remain null; no competitive potential score; weight-class comparisons are scale references only. Default nutrition supports maintenance rather than weight cutting. Local account creation generates a high-entropy recovery token; only its hash is stored. No production authentication claim.

## Delivery

- Core, program generation, comparison, logging, revisions and reassessment workflows implemented and API-tested.
- 45 backend tests and 8 frontend tests pass; TypeScript and production build pass; Ruff checks and formatting pass. npm audit reports no vulnerabilities in the installed set.
- Phase 1 replaces the initial browser blocker: 38 Playwright tests pass (7 intentional applicability skips), with all five requested viewport widths, screenshots, axe checks, complete journeys and inspected A4 prints. See docs/PHASE1_QA.md.
- Production identity, expanded licensed fighter/food catalogs, clinical program review, full cultural/budget meal optimization and PostgreSQL runtime verification remain outside this local version. See README and docs/DELIVERY.md.


Phase15: current implementation and verification are recorded in docs/PHASE15_DELIVERY.md and docs/PHASE15_FEATURE_MATRIX.md. Historical plan counts above describe the original delivery. Independent app source checkpoints exclude personal/runtime data.
