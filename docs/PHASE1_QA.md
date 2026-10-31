# Phase 1 — browser QA and UI/UX verification

Date: **2026-10-30** (Asia/Dubai). Scope: the existing `mma-performance-coach/` app only. The original tracker source, configuration and data were not changed.

## Baseline and implementation map

Before changes: **45 backend tests**, **5 frontend tests**, and TypeScript checks passed. The app uses state-based navigation in `App.tsx`, not separate React Router URLs. There are no new page URLs introduced by this phase.

| Workspace | Main implementation | Principal API groups |
| --- | --- | --- |
| Overview / physical assessment | `src/App.tsx` | profile, assessment, weight-classes |
| Fighting style | `src/App.tsx` | assessment |
| Comparison lab | `components/Comparison.tsx` | fighters, fighter-matches, comparisons |
| Training | `components/Training.tsx` | training-plans, training-sessions |
| Nutrition | `components/NutritionPage.tsx` | nutrition |
| Progress / reassessment | `components/Progress.tsx` | progress, reassessments |
| AI coach / revisions | `components/Coach.tsx` | coach, revisions, health |
| Account / export | `src/App.tsx` | auth, account, export |
| Onboarding | `components/Wizard.tsx`, `BenchmarkEditor.tsx` | profile, profile/draft |

Backend route definitions remain in `backend/app/main.py`. Existing deterministic analysis, program generation and ownership rules were preserved.

## Real browser coverage

**Executed using Microsoft Edge 155.0.4283.45 through Playwright, headless on Windows.** Mobile/tablet entries are browser viewport/touch emulation, not physical devices. The production Vite build was served by a real FastAPI process and disposable SQLite database on port 8123. No development browser connector or desktop UI fallback was needed.

| Project | CSS viewport | Eight main pages | Complete journey | Keyboard / modal | Loading / failure | Assessment axe |
| --- | --- | --- | --- | --- | --- | --- |
| Desktop | 1440 × 1000 | Pass | Pass | Pass | Pass | Pass |
| Large desktop | 1920 × 1080 | Pass | Pass | Pass | Pass | Pass |
| Tablet | 768 × 1024 | Pass | Pass | Pass | Pass | Pass |
| Mobile | 390 × 844 | Pass | Pass | Pass | Pass | Pass |
| Small mobile | 375 × 812 | Pass | Pass | Pass | Pass | Pass |

The full matrix contains **38 passed tests and 7 intentional skips**: the mobile-only drawer test skips the three non-mobile projects, and the fixed A4 print test skips four duplicate screen configurations. Skips are not counted as browser coverage. A separate focused A4 rerun verifies the final print-only refinements.

Machine-readable [browser results](evidence/phase1/browser-results.json) preserve test outcomes. Each viewport has a `*-checks.json` containing the actual browser version, document width, page names, axe findings and runtime errors. The eight-page sweep recorded **no document-level horizontal overflow, no uncaught page errors and no failing application/static responses** in the seeded workflow.

## Journey checklist

- [x] Load the app and create a local account through the UI.
- [x] Complete all six onboarding steps using Jordan QA: 29 years, 181 cm, 79 kg, 186 cm wingspan, boxing experience, a squat benchmark, four available days, a development goal and Halal restriction.
- [x] Save a draft; dismiss/reopen the wizard and restore Casey QA's saved draft.
- [x] Save the athlete; retrieve assessment; verify the specific scale-reference result is **Middleweight** for the 79 kg fixture.
- [x] Search real seeded fighters, adjust physical weights, recalculate, and save a comparison.
- [x] Review the training week; open an exercise session; log a workout; reopen a completed session and keyboard-access its disclosures.
- [x] Review a seven-day meal template, select day seven and show the grocery list.
- [x] Save a progress check-in and request reassessment; verify recovery-based adjustment guidance.
- [x] Preview and reject a revision; preview and approve another revision.
- [x] Use the real local coach with OpenAI unavailable.
- [x] Exercise the configured AI toggle, request payload and labeled response using **mocked browser transport**, explicitly marked as such in the response.
- [x] Download JSON and inspect its profile and two training-plan versions, including record-type metadata.
- [x] Exercise a 503 loading failure, a failed workout save followed by retry, native required-field validation and a server validation error inside onboarding.
- [x] Print overview, selected training week, selected nutrition day and fighter comparison to A4 PDFs; inspect rendered output.

## Bugs found and fixed

| Finding / root cause | Smallest practical correction | Regression evidence |
| --- | --- | --- |
| Low-contrast primary buttons, sidebar captions, insight numbers and footer text; tablet phase numbers fell below 4.5:1 at the smaller font size. | Darkened red button backgrounds and raised affected foreground contrast. | Axe across all eight pages at all five widths. |
| Mobile navigation was translated offscreen but remained keyboard/screen-reader accessible. | Hidden closed drawer, expanded/current semantics, labeled close/scrim controls, focus trapping, Escape and focus restoration. Resize closes the drawer. | Both mobile projects; all-width keyboard tests. |
| Modal background remained accessible to assistive technology. | Temporarily mark sibling branches inert and restore prior states on close. | Unit regression and browser modal interaction/axe. |
| Completed workout dialogs trapped Tab on the close button because native `summary` controls were absent from the focus selector. | Include disclosure summaries in modal focus traversal. | Completed-session keyboard step in the full journey. |
| Narrow icon-only physical-analysis control was 19 px wide; several mobile controls were too small. | Minimum mobile button dimensions and larger step/range targets; seven-day preview becomes four columns rather than tiny squeezed text. | Mobile button-size assertions and screenshots. |
| Search icon stacked above its input because global label flex direction was inherited. | Explicit horizontal flex direction on search labels. | Comparison screenshots at five widths. |
| No reduced-motion handling; chart animation showed misleading intermediate heights during initial rendering. | Honor reduced motion; render numerical chart bars/areas without tweening. | Computed-style assertion and chart screenshots. |
| Backend/session failures were swallowed, making an unavailable service resemble a new account. JSON parsing errors were also raw. | Typed API errors, actionable network/unreadable-response messages, explicit startup feedback; only expected unauthenticated/absent-plan states are ignored. | Browser failure test and API-client unit regressions. |
| Workout save errors appeared behind the modal; draft/history load errors could silently disappear. | Show workout errors inside the modal and retain it for retry; surface draft/history failures. | Browser retry/error tests; onboarding validation. |
| Print inherited dark backgrounds and pale text, produced an extra blank overview page, hid fighter data carried by buttons, and omitted closed ingredient disclosures. | White print containers, explicit print contrast/pagination, preserved data-bearing button content, and temporary disclosure expansion/restoration. | Actual PDFs, page renders, no-blank-page and safe-margin checks. |
| “Export report” opened printing without saying so. | Rename to “Print report,” with save-to-PDF guidance. JSON download remains separate. | Browser print control presence and downloaded JSON inspection. |
| JSON export omitted record kinds, obscuring profile/plan/log distinctions. | Include `kind` in exported records without changing stored data. | Backend export assertion and browser JSON inspection. |
| Missing favicon caused an avoidable browser asset 404. | Add a local SVG favicon. | Workspace response-error monitoring. |

Initial failures caused by ambiguous test locators were corrected in the test harness; they are not reported as product bugs. The Windows sandbox could launch Edge but did not reliably tear down the test process tree, so final matrix runs used approved execution outside that sandbox. They still used the isolated app test database.

## Accessibility and responsive findings

Automated axe checks targeted **WCAG 2 A/AA and 2.1 AA**. All **40 workspace scans** and **five onboarding-dialog scans** completed without targeted violations. These are automated findings, not a claim of full WCAG conformance.

Keyboard checks exercised modal entry, forward/backward focus wrapping, completed-session disclosures, Escape and restoration. Closed mobile navigation no longer participates in focus order. Native required-field validation, labels, error/status announcements and visible focus styling are retained. Charts have adjacent data tables or log summaries; screenshot review checked their layout and labels. Buttons in the mobile overview size sample met the test's 44 px height / 24 px width threshold; CSS uses larger minimums for ordinary mobile buttons.

Normal screen layouts preserve the existing charcoal surfaces, red accent and typography. Changes are limited to spacing/readability corrections, touch controls and known layout bugs. There was no whole-interface redesign. Long content and tables wrap within the tested viewport; chart containers remain responsive.

## Print and export evidence

The four A4 QA PDFs and their rendered page PNGs live under `docs/evidence/phase1/`. They use synthetic demo data. Each final PDF has **two pages**; text extraction found no empty pages and the margin check found no text outside a 20-point safe region. Actual page renders were reviewed for clipping, contrast, alignment and continuation. The overview's seven-day mini schedule is kept together; nutrition portions/methods and fighter names/breakdowns remain printable. These print outputs cover the current selected view, not every week/day at once; the JSON download includes all saved plan versions.

The repeatable inspector is `backend/tests/check_prints.py`; [print checks](evidence/phase1/print-checks.json) record page/text/margin results. Rendered screenshots and screenshot links are indexed in [the evidence directory](evidence/phase1/README.md).

## Checks and limits

| Check | Result |
| --- | --- |
| Browser matrix | 38 passed, 7 intentional skips |
| Backend Pytest | 45 passed; one existing upstream Starlette transport deprecation warning |
| Frontend Vitest | 8 passed |
| TypeScript / Vite production build | Passed |
| Ruff / Prettier | Passed |
| npm audit | Zero vulnerabilities in the installed dependency set |
| A4 rendering / extraction / margins | Four reports inspected; no blank pages or unsafe-margin text |

Unresolved verification limits: no physical phone/tablet, Safari/WebKit or Firefox run; no manual NVDA/JAWS/VoiceOver session; no real printer-driver test; no real paid OpenAI call or review of model response quality. Configured AI success was browser-mocked, while offline coaching used the real backend. Existing product/data limitations in the README remain unchanged. These do not invalidate the exercised Edge workflows, but they remain follow-up work before broad release.

Run `npm.cmd run test:browser` from `frontend/` to reproduce the browser matrix. It requires installed Edge (or configured Playwright Chromium), Node and the app's Python dependencies. Reports are regenerated; do not run against production accounts or substitute a live database.


Phase 2 evidence note: the initial Phase 2 regression reused the legacy PDF output filenames in `evidence/phase1/`, refreshing those four PDF files. Phase 1 screenshots/results remain historical. Use `evidence/phase2/` for final Phase 2 browser/PDF results; the suite now supports a separate PDF evidence directory.
