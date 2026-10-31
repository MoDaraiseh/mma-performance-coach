# Phase 4: fighter matching and Comparison Lab

Review date: **2026-10-31**. Development is confined to `mma-performance-coach/`; the original tracker and its configuration/data remain unchanged. The normal athlete database was not migrated or used for QA.

## Delivery and requirement status

| Area | Audited baseline | Delivered implementation | Status / evidence |
| --- | --- | --- | --- |
| Fighter records | Three men's snapshots; scalar division and coarse source URL/date | Eleven validated records: seven men, four women; original measurements, canonical cm/kg, field-level source IDs, method/rights/dates | Implemented curated subset; `fighter_catalog.py`, `fighter_models.py`, source register below |
| Career/division context | Historical/current context mixed in one string | Explicit source-status, nullable current division, documented UFC division history; inactive women's featherweight remains historical | Implemented; matching/API tests cover current/history, retired records and category mismatch |
| Data providers | Local/database `all()` interface only | Validated local/database providers plus operator-configured licensed JSON export adapter; no network collection | Local and file adapter verified. Live commercial provider and redistribution rights **unverified** |
| Refresh/history | Startup inserted missing records only | Authenticated explicit refresh; validates export, locks writes, rejects older-date replacement/provider collisions, atomically archives old/new content hashes | Implemented; repeat refresh, rollback, concurrency, preservation and unavailable-provider API tests |
| Similarity | Combined physical Gaussian, coarse scalar class comparison, top three only | Per-measurement Gaussian scores, height/reach/optional ratio weights, background/style Jaccard, stance agreement, reference-based history/current division compatibility | Implemented deterministic heuristics; not scientifically calibrated or a professional skill assessment |
| Missing/stale data | Excluded groups but no completeness measure | Requested-weight coverage including missing physical subdimensions; exclusions with reasons; observation age, 365-day filter, minimum coverage and active/status/division filters | Implemented; unknowns are not zero or invented measurements |
| Manual lab | Search could select a fighter without a breakdown; saving required top-three rank | Shared scoring for any valid record; cross-category or unsupported comparisons explicitly unscored; manual favorites work outside top three | Implemented through UI/API; Edge and regression tests |
| Interactive controls | Five group sliders | Group sliders, physical subweights, optional style study preferences, current/history choice, coverage/status/freshness/division filters, search, reset and refresh controls | Implemented; backend-ranked updates debounced 150 ms; obsolete responses ignored |
| Explanations and visuals | One physical chart and partial breakdown | Physical chart/table, component bars, effective group/subweights, coverage, selection context, signed differences, shared disciplines, missing data, provenance/history/statistic details | Implemented; accessible numeric tables accompany visuals |
| Favorites/export | Inputs saved but UI mixed old fighter/current athlete data | Immutable match, algorithm, reference, profile, source and weight snapshots; loaded chart uses saved profile; explicit current re-evaluation | Implemented; JSON account export includes comparison records and their source snapshots |
| Source coverage | No women, little historical context | Women, retired and not-fighting snapshots; sparse historical statistics with dated scopes; conflicting results omitted | Partial by design: no comprehensive database, current records/rankings or independently verified technical proficiency |

## Audit findings and smallest fixes

| Priority | Root cause / impact | Resolution | Regression evidence |
| --- | --- | --- | --- |
| P1 | Favorites searched only the top-three result list; manual choices outside it could not be saved or explained | Single `compare()` path evaluates any validated fighter; ranking uses the same evaluator | `test_phase4_manual_favorites_refresh_and_history`, `phase4.spec.ts` |
| P1 | One division-limit scalar conflated history and current context | Named division history/current fields resolve against the same persisted active reference used by athlete assessment; listed fighter weight never enters matching | Current/history/category/listed-weight tests; shared-reference API test |
| P1 | Coarse provenance could not identify the source of a known attribute | Strict field/source contracts, unit agreement checks and explicit indexed-excerpt method; invalid/legacy rows surfaced and excluded until refresh | Provenance, malformed original, future-date and license tests |
| P2 | Missing reach was renormalized without exposing how much requested evidence was absent | Separate requested-weight coverage and measurement exclusions; optional minimum coverage | Perfect/partial/incomplete-record tests |
| P2 | Rounded scores were used as sort keys, creating artificial ties | Full-precision ordering followed by fighter ID for exact ties; whole-point display | Exact-tie and display-rounding tests |
| P2 | Saved-view selection used current athlete measurements with historical fighter inputs | Frozen profile/match view plus explicit re-evaluation; current manual response supplies current fighter data | Edge changes athlete height after saving, verifies original height on load and updated height after re-evaluation |
| P2 | Failed matching could leave old results; selecting an already selected fighter did not retry after failure | Clear pending/stale results, separate request errors, ignore obsolete responses, repeated selection triggers new request | Edge mocked 503 matching/manual failures and successful retry |
| P2 | New tables inherited an 860px-wide history layout and lacked keyboard-accessible scroll regions at narrow widths | Dedicated compact wrapping tables, named focusable regions and visible focus | Initial three axe failures; corrected expanded-view checks at all five widths |
| P2 | Print text was forced dark while select/input backgrounds stayed dark | Printed card controls use white backgrounds and light color scheme | Rendered A4 review and final print rerun; margin checks alone did not catch this |
| P2 | Model declared version uniqueness as a constraint while migration `0002` created a unique index | Align SQLAlchemy metadata with the existing unique index; uniqueness and stored data retained | Alembic check: no new operations; upgrade/downgrade preservation check |

## Data quality, provenance and coverage

See the [source/permissions register](SOURCES.md#phase-4-fighter-register-2026-10-31) for every profile URL, original inches/pounds, supporting history articles and known conflicts. Field-level IDs, original units and review method are also returned by the API and visible in the lab.

The bundle contains Max Holloway, Alexander Volkanovski, Israel Adesanya, Valentina Shevchenko, Zhang Weili, Joanna Jedrzejczyk, Georges St-Pierre, Tom Aspinall, Alex Pereira, Demetrious Johnson and Amanda Nunes. Source snapshots indicate eight active, two retired and one not fighting; these are not a live career-status feed. Retired/not-fighting athletes have no asserted current division. Histories are deliberately incomplete documented UFC subsets, not entire competitive biographies.

All 11 have source-listed height/reach/weight. Only five have included documented discipline backgrounds; zero have a verified current stance or shared controlled style traits. Two have explicitly historical statistics, excluded from matching: St-Pierre's 26 wins at his 2019 retirement announcement and Jedrzejczyk's pre-UFC 275 6.62 significant strikes landed/minute. All current fight-record fields remain null. Raw source style labels are not measured skill ratings.

Current profile coverage does not cover every active class: no current men's bantamweight, flyweight, welterweight or light-heavyweight entry, and no current women's strawweight entry. Historical records improve study coverage but do not fill those current-roster gaps. Category mismatches are available only as unscored manual references. Women's historical featherweight does not become an active reference class.

Direct official profile requests returned **HTTP 403**. Facts were reviewed through indexed official UFC excerpts, with method `indexed_official_excerpt`. Review/observation dates are **not physical measurement dates**. Some excerpts disagree internally about bout results and profile-versus-ranking division context; disputed results and exact transition dates are omitted, and division ambiguity is disclosed. No scraper, photos, logos, biographies or fabricated statistics were added. Commercial redistribution permission has **not been established**.

## Mathematics and interpretation

The [methodology](METHODOLOGY.md#fighter-matching-phase-4) specifies every factor, scale, default weight, missing-data rule and filter. `backend/app/matching.py` is the deterministic implementation; no LLM computes scores or changes inputs.

For physical measurement `x`, score is `100 * exp(-0.5 * ((athlete_x - fighter_x) / scale)^2)`. Height/reach scales are 15 cm; optional derived ratio scale is 0.05. Physical subweights default to height/reach/ratio = 50/50/0. A separate ratio weight is optional because it reuses reach/height evidence. Group defaults are physical/background/style/stance/division = 60/15/10/5/10. Shared discipline/style sets use Jaccard overlap, not proficiency. Only mutually supported attributes enter scoring. Coverage independently reports how much requested weight had support, including the fraction of physical subweights available.

Division compatibility compares the athlete's everyday scale reference with source-backed current/history names mapped to active championship limits. This is not competition eligibility. Listed fighter weight, a long-term target and everyday weight are distinct; neither listed weight nor a proposed target is used to infer class compatibility. Non-title allowances remain separate reference values. Exact numerical equality can yield 100; that never implies professional skill or probable success. Whole-point scores avoid spurious decimal precision, but are still heuristic resemblance numbers, not probabilities.

`resemblance-v2` ranks full-precision results descending, breaking exact ties by ID. Unavailable weighted dimensions are renormalized, so differing coverage must be considered alongside score. No available weighted factor yields no ranked result and an unscored manual result. Zero group weights, or zero physical subweights with physical enabled, are rejected. Local style/stance sliders cannot create unavailable facts. Returned explanations list supported factors, important differences, missing factors and predominantly physical/contextual basis; the UI directs study toward qualified coaching.

## Integration and operation

Relevant files: `backend/app/fighter_models.py`, `fighter_catalog.py`, `fighters.py`, `matching.py`, `divisions.py`, `fighter_refresh.py`; `frontend/src/components/Comparison.tsx`; migration `0004_fighter_data_revisions.py`.

| Endpoint | Behavior |
| --- | --- |
| `GET /api/fighters?q=` | Validated searchable factual snapshots; invalid/legacy records excluded |
| `POST /api/fighter-matches` | Current profile + validated weight/filter configuration; top three and coverage summary |
| `POST /api/fighter-comparisons/{id}` | Same evaluator without top-three restriction; unsupported/category mismatch may be unscored |
| `POST /api/comparisons/{id}` | User-owned immutable favorite including inputs and provenance |
| `GET /api/comparisons`, `DELETE /api/comparisons/{saved_id}` | Account-scoped saved comparisons/removal |
| `GET /api/fighter-data` | Provider availability, unavailable records and public-data revision payloads/hashes |
| `POST /api/fighter-data/refresh?provider=local` | Explicit reviewed-bundle import; archives changed/previous payloads; never advances verification dates |
| `POST /api/fighter-data/refresh?provider=licensed` | Server-configured licensed JSON export; unavailable provider returns 503 |

All match, comparison, provider status and refresh operations require the local authenticated account; only the public factual fighter listing is public. Refresh updates shared public reference data, never athlete profiles, plans or saved favorites. This local application has no production administrator/tenant policy; production shared-provider refresh needs authorization/rate controls.

Upgrade an existing MMA database explicitly, from `backend/`:

```powershell
..\.venv\Scripts\python.exe -m alembic upgrade head
```

Required head is **0004**. Startup only adds missing bundle records and references; it preserves existing snapshots. The lab's local refresh is how an existing user opts into the new reviewed snapshot versions. Legacy provenance is not silently backfilled. Reimporting the same payload is idempotent. SQLite refresh takes a writer lock before reading dates; row locks are requested on other engines. Old/new payloads are content-addressed in `fighter_data_revisions`. Favorites retain their own snapshots even after a refresh. No automatic rollback UI is included; archived data can be inspected via the authenticated provider-status API.

Optional operator variables `FIGHTER_LICENSED_EXPORT` and `FIGHTER_LICENSE_REFERENCE` enable the file adapter. The export is a list of at most 1000 `FighterRecord` v2 objects, at most 2 MB, canonical cm/kg, unique IDs, field-specific source references, source rights `licensed` and matching license references. Original units, if supplied, must agree with canonical measurements. Duplicate IDs, malformed data, unsupported units, future observations and license-reference mismatches are rejected. A provider cannot take over another provider's ID. The adapter does not prove an agreement's legal sufficiency and no commercial service was configured or exercised.

## Validation and evidence

Baseline rerun: **115 backend Pytest and eight frontend tests passed**, app TypeScript passed. Final backend: **132 passed**, one existing Starlette/httpx deprecation warning. Added tests cover perfect physical/ratio similarity, missing reach, absent measurements, unit normalization/mismatch, provenance, future dates, stale data, zero/invalid weights, background/style/stance fixtures, slider-driven ranking changes, exact/rounded ties, division contexts/mismatches, listed-weight independence, licensed export validation, manual favorites, legacy refresh, idempotency, rollback, concurrent refresh and older-data rejection. Fixtures for stance/style test supported provider behavior; no such values were invented for local athletes.

Frontend Vitest: **eight passed**. App/browser TypeScript, Vite production build, Ruff and Prettier passed. [Migration evidence](evidence/phase4/migrations.json): upgrade from `0003`, downgrade/re-upgrade, preservation of a legacy fighter payload, and Alembic no-schema-difference check all passed in disposable SQLite. PostgreSQL remains unverified.

Full real **Edge/Playwright** run: **63 passed, seven intentional skips**, across desktop 1440/1920, tablet 768 and mobile 390/375. Skips are the three desktop/tablet mobile-drawer cases and four duplicate viewport print cases. [Full results](evidence/phase4/browser-results.json). Earlier full attempt: 55 passed, three expanded-table axe failures and seven skips; [initial report](evidence/phase4/browser-initial.json) retained rather than claimed passing. These failures led to the wrapping/focus correction.

Final focused controls/error/snapshot/print verification is recorded in [focused results](evidence/phase4/browser-final-focused.json). This follows the full run and checks the final print-control contrast and independent error states, plus loading an actual saved profile after athlete inputs change. Final focused result: **11 passed, four intentional duplicate-print skips** across all five viewports. During this added regression, intermediate focused attempts were interrupted after test-harness errors: a reloaded page resets collapsed details, and mobile navigation must wait for the app to mount. The harness now opens the section and waits for the overview heading after reload. These interrupted attempts are not counted as passing browser coverage.

Evidence screenshots: [1440](evidence/phase4/desktop-1440-phase4-comparison-lab.png), [1920](evidence/phase4/desktop-1920-phase4-comparison-lab.png), [768](evidence/phase4/tablet-768-phase4-comparison-lab.png), [390](evidence/phase4/mobile-390-phase4-comparison-lab.png), [375](evidence/phase4/mobile-375-phase4-comparison-lab.png). Expanded sources/controls and charts are exercised with no document horizontal overflow and no axe violations. Keyboard slider arrows, retry behavior, favorite/save/load, manual selection, division filters, zero weights and explicit refresh are exercised. The full suite also rechecks onboarding, training/progress/reassessment/approval, JSON export, keyboard/modal behavior and offline/mocked-configured coach workflows.

Four A4 reports are exported and checked for nonblank pages and safe text margins: [comparison](evidence/phase4/comparison-lab-a4.pdf), [athlete overview](evidence/phase4/overview-a4.pdf), [training](evidence/phase4/training-a4.pdf), [nutrition](evidence/phase4/nutrition-a4.pdf). [Print checks](evidence/phase4/print-checks.json) and [rendered pages](evidence/phase4/print-pages/) accompany the PDFs. Comparison pages are visually reviewed, including wrapping component/source tables and control contrast; automated margin checks do not prove visual quality by themselves.

## Explicit remaining limits

- Eleven dated factual study records, not comprehensive coverage, a current roster or a licensed live statistics database. Indexed excerpts can be stale or inconsistent; disputed content is omitted and ambiguities are visible.
- No source-backed current stance or shared stylistic-trait data in the local bundle. Shared backgrounds are sparse and do not quantify skill or experience equivalence. No professional proficiency comparison.
- Source observation freshness is a 365-day product rule, not assurance of current measurements, source correctness, licensing or career status. Local refresh never performs a new external verification.
- Gaussian scales, group weights and coverage rules are transparent heuristics, not validated athlete clustering or an outcome model. No arbitrary overall completion percentage is assigned.
- Live licensed provider access, commercial redistribution rights, PostgreSQL/concurrent production deployments, non-Edge engines, physical devices and manual screen-reader testing remain unverified. Paid AI is outside this phase and does not compute rankings.
- Public-data revisions are retained and inspectable; there is no user-facing rollback editor or automatic feed scheduling. Production refresh needs administrator authorization and provider-specific usage controls.

Next priorities are a properly licensed, independently reviewed inclusive feed; resolving source ambiguities; qualified review of a shared style taxonomy and matching scales; then broader browser/device/assistive-technology and production-database verification.


Final verification: 132 backend + eight frontend tests; 63 full-matrix Edge cases (seven intentional skips), followed by 11 final focused Edge cases (four intentional skips). Four A4 documents contain 11 pages total (comparison four, overview two, training three, nutrition two), all with nonblank text and no text outside safe margins. Comparison print pages were visually reviewed after the control-background correction. Unscored saved references are explicitly labeled **Unscored**. No required Phase 4 implementation work remains for the verified local-subset scope; live licensed coverage and the explicit limitations above remain future work.
