# Phase 17 browser acceptance

2026-11-01, isolated synthetic SQLite/API server at local HTTP8123, one Playwright worker. No athlete database or live AI/IdP was used. Core runtime: installed Edge/Blink155.0.4283.45; five viewports1440x1000,1920x1080,768x1024,390x844,375x812. Additional installed Chromium revision1248 (packaged156.0.8078.4) executes desktop1440/mobile375 smoke journeys. Both runtimes use Blink; Firefox/WebKit are not installed in the available Playwright browser cache and were not tested.

## Native runs and acceptance accounting

| Run | Actual result | Evidence |
| --- | --- | --- |
| Full Edge matrix | **163 passed, five failed, seven intentionally skipped**,175 scheduled;761.75s | [Native full report](evidence/phase17/browser-results.json), [log](evidence/phase17/browser-run.log) |
| First corrected Phase11 recheck | **15 native cases passed**, zero failed/skipped;68.06s | [Native report](evidence/phase17/edge-phase11-recheck.json), [log](evidence/phase17/edge-phase11-recheck.log) |
| Final consistent UTC Phase11 recheck | **15 passed**, zero failed/skipped; 68.38s; explicit native exit0 | [Final report](evidence/phase17/edge-phase11-final.json), [log](evidence/phase17/edge-phase11-final.log) |
| Chromium core journeys | **Four passed**, zero failed/skipped;36.83s, desktop1440/mobile375 | [Native report](evidence/phase17/chromium-smoke-results.json), [log with native exit0](evidence/phase17/chromium-smoke.log) |

The original full report is intentionally retained with its five failures; it is not described as a single all-green run. All five failures were the same calendar fixture at different widths. Focused reruns cover all three Phase11 cases at all five widths (including ten already-passing cases); their counts must not be added as unique functional coverage. After successful correction, coverage is168 accepted Edge cases/seven intentional skips across the original175 scheduled combinations, supported by separate full and focused evidence. Chromium adds runtime confirmation, not four newly implemented features.

Intentional skips: mobile drawer at the two desktop widths and tablet (three skips; actual drawer checks execute at both mobile widths); fixed A4 print layout outside the designated1440 viewport (four skips; all five PDFs execute at1440). These are declared scope exclusions, not unavailable-browser passes.

## Failure, root cause and regression confirmation

The calendar fixture computed Monday with local `getDay`/`setDate`, then submitted `toISOString().slice(0,10)`. Before04:00 Dubai, that converts local Monday to UTC Sunday. All five API requests returned422 because the backend correctly requires a Monday; no approved plan was changed. This was a test-data timezone defect, not a user calendar persistence failure.

Small fix: use UTC date/weekday arithmetic consistently in `frontend/e2e/phase11.spec.ts`. A fixed-time reproduction at2026-11-01T02:30:00+04:00 shows old2026-10-11 (Sunday) versus corrected2026-10-12 (Monday): [evidence](evidence/phase17/utc-fixture-reproduction.json). The fresh rechecks exercise actual successful schedule persistence, unchanged approved-plan ID, downloaded report, history pagination and date filtering at all five widths. Initial failure screenshots/context/traces are preserved under `evidence/phase17/initial-failures/` (synthetic credentials may occur in traces; keep private).

The first focused invocation's shell wrapper returned1 despite15 passing native assertions and an empty native errors list. The final invocation repeats the consistent fixtures with explicit native exit capture; its result is recorded rather than inferring a clean shell status from the passing assertion count.

## Workflow and responsive acceptance

Executed source maps: journey (onboarding/logging/reassessment/approve/reject/export and mocked configured AI); phase2–10 (profile/staleness, exercise logs/progression, comparisons/weights/favorites/provenance, nutrition substitutions/restrictions, session expiry/deletion, athletic scheduling, fighter pagination, food preferences and controlled AI actions); phase11 (analytics/history/calendar/report); phase12 (honest review status and rapid-cut withholding); phase13 (owned sessions/revocation and mocked managed migration/linking); phase14 (actual browser warm-load measurements); phase15 (expanded catalogs, Mobility filters/objectives, macro-balanced fat-food approval/history and allergy rejection). Error, loading, stale-conflict, rejected-change and fresh persistence reads are exercised; buttons alone do not establish acceptance.

Navigation/drawer, forms/labels/validation, chart tables, calendars, comparison controls, modal focus/Escape/restoration, touch targets, reduced motion, overflow and keyboard behavior execute at requested widths. Forty core-view axe summaries (eight views x five widths) report **zero targeted violations and no captured runtime errors**, with additional dialog/feature assertions in the suite. [1440 checks](evidence/phase17/desktop-1440-checks.json), [1920 checks](evidence/phase17/desktop-1920-checks.json), [tablet](evidence/phase17/tablet-768-checks.json), [390](evidence/phase17/mobile-390-checks.json), [375](evidence/phase17/mobile-375-checks.json).

This is automated accessibility coverage, not complete WCAG conformance, manual screen-reader review or physical-device testing. Other engines, zoom/font/OS combinations and exhaustive assistive-technology behavior remain unverified. Provider pages and configured AI output are mocked, not actual tenant/model validation.

## Visual, print and export evidence

Fresh screenshots are available under `evidence/phase17/`; representative desktop overview and mobile nutrition approval layout were inspected. [Desktop overview](evidence/phase17/desktop-1440-overview.png), [mobile nutrition approval](evidence/phase17/mobile-390-phase15-approved-food-replacement.png), [375 progress](evidence/phase17/mobile-375-progress.png), [comparison](evidence/phase17/desktop-1440-comparison-lab.png). No redesign or application CSS change was needed. Screenshot inspection is representative, not a claim of exhaustive manual review of every pixel.

Five A4 reports total18 pages: comparison5/nutrition4/overview2/progress4/training3. All pages have nonblank extracted text and no text detected outside20pt margins. One rendered nutrition page was visually inspected for readable hierarchy/estimates/limits. [Print checks](evidence/phase17/print-checks.json), rendered pages in `evidence/phase17/print-pages/`. Exports validate required content and owned CSV/JSON/download workflows; print is current detailed view/week/day, not a complete book of all program sessions. No physical-printer or PDF assistive-technology conformance claim.

All evidence is local and Git-ignored. Archive redacted artifacts with the release manifest; browser traces are private test material, not public launch assets. [Final acceptance](PHASE17_ACCEPTANCE.md) and [performance interpretation](PHASE17_PERFORMANCE.md) retain external blockers and measured-sample limitations.
