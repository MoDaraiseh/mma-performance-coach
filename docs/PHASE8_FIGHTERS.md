# Phase 8 — source-aware fighter data and matching

Review date: **2026-10-31**. Changes and QA stay inside `mma-performance-coach/`. Original tracker files and normal athlete data were not modified by QA. No paid provider, scraping job, hosted service or public deployment was used.

## Baseline and delivered scope

Baseline **221 backend tests / 11 frontend tests passed**. Reviewed fighter models/providers, all 11 original records, provenance/rights, refresh archives, division references, Gaussian/Jaccard matching, manual/favorite snapshots, sliders, search/UI and tests.

The bundle now has **17 validated source-snapshot records: 10 men and 7 women**, including **six new attributed secondary-source snapshots**. Validation establishes schema/provenance consistency and review of the cited source, **not independent confirmation of an athlete's measurements, current status or professional skill**. This is a study subset, not comprehensive UFC coverage.

| Area | Phase 8 change | Remaining boundary |
| --- | --- | --- |
| Coverage | Added Kamaru Usman, Jon Jones, Henry Cejudo, Rose Namajunas, Ronda Rousey and Miesha Tate; three men/three women | Current career status/division for all six is explicitly unknown; no live roster claim |
| Permissions | Reviewed Wikimedia reuse terms, retained article/history attribution, CC BY-SA 4.0 link and adaptation notice per record | Original 11 official-source records still have unestablished redistribution rights; no blanket commercial license |
| Data architecture | Typed optional dated professional record, external identifiers, source attribution/license URL; indexed metadata and import-batch history | No verified current professional records in the bundle; statistics remain sparse historical observations |
| Search | Server pagination and query/competition category/historical division/stance/career filters; bounded JSON results | Substring matching scans normalized metadata; no full-text or production capacity claim |
| Matching | `resemblance-v3`, partial physical evidence contributes only its supported requested weight; exact normalized percentages; shared division lookup | Gaussian scales and category heuristics are uncalibrated resemblance rules, never probabilities |
| Governance | Offline preview token, changed-field conflict review, atomic apply, duplicate/identity checks, retained before/after batch snapshots and guarded rollback | Operator must actually verify rights and source conflicts; no public upload/admin portal or automatic fuzzy identity merge |
| UI | Debounced paginated search, filters, source/license disclosure, coverage report, supported-record messages and existing charts/favorites | Style traits remain unavailable; matching sliders cannot invent them |

## Measurable coverage objective and actual result

The iteration target was **six reusable, attributed additions split equally across men/women**, with at least one documented historical participant in all eight men's active reference divisions and all three women's active reference divisions. All targets were met using accessible secondary sources. This is historical participation coverage, **not coverage of every active fighter or current roster slot**. The infrastructure accepts up to 10,000 file records; only 17 real records are bundled. The 1,000-row load fixture is synthetic and never counted as fighters.

[Generated quality report](evidence/phase8/data-quality.json): historical counts overlap because a fighter can appear in multiple divisions.

| Category | Historical UFC division | Validated snapshots |
| --- | --- | ---: |
| Men | Flyweight | 2 |
| Men | Bantamweight | 1 |
| Men | Featherweight | 2 |
| Men | Lightweight | 2 |
| Men | Welterweight | 2 |
| Men | Middleweight | 3 |
| Men | Light Heavyweight | 3 |
| Men | Heavyweight | 3 |
| Women | Strawweight | 3 |
| Women | Flyweight | 5 |
| Women | Bantamweight | 3 |
| Women | Featherweight, historical inactive reference | 1 |

Current-division assertions remain only in the original eight source snapshots: men's Featherweight 1, Lightweight 1, Middleweight 1, Heavyweight 2; women's Flyweight 2 and Bantamweight 1. These are dated source assertions, not a verified live roster. Status counts: Active 8, Retired 2, Not fighting 1, Unknown 6. All 17 have sourced height/reach/listed weight; two have a stance, eleven have documented background and two have historical statistics. Zero has a verified current professional record or controlled style traits. A fresh review date does not make an old measurement current.

## Source access and license decisions

The [UFC terms](https://www.ufc.com/news/terms-use) indexed excerpt prohibits automated extraction; direct access to the terms/profile resources returned 403. No access control was bypassed, no UFC/UFCStats scraper was added, and no assumed scraping/redistribution permission was inferred from a third-party dataset label. UFCStats and licensed commercial feeds remain potential operator-reviewed sources, not bundled permissions or active integrations.

The [Wikimedia reuse terms](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#7._Licensing_of_Content) permit reuse under the underlying license with attribution/share-alike obligations. Six article snapshots were read and a small factual subset adapted, with no article narratives, images, logos or fair-use media. [Supplement license/attribution](FIGHTER_SUPPLEMENT_LICENSE.md) links every source/history and the license. Original imperial figures are retained; cm/kg are arithmetic conversions, not additional measurement precision. Wikipedia is a secondary, editable source; no official verification is implied. A source field labelled “Style” alone is not treated as professional skill. Background entries use explicitly recorded practice/ranks or wrestling history; raw descriptive styles remain separate.

New source observations are dated reviews, not claims of current athletic activity. For example, Rousey's listed 142 lb is retained as a source-listed weight while her included UFC history is Bantamweight; non-UFC featherweight context is not promoted into a current UFC division. Usman's disputed/source-listed Middleweight context is not imported as UFC history. Jones's current career status remains unknown rather than resolving inconsistent activity summaries by guesswork. Live records, significant-striking/takedown/submission rates and unsupported stance/style fields are omitted, not fabricated.

Redistributing the entire original-plus-supplement database is not automatically authorized. Only the six-record adaptation carries the explicit reuse notice; rights for the original 11 and any future licensed export must be resolved separately. The app remains subject to the Phase 6 production/data-license gates.

## Data layer, migration and query behavior

**Run Alembic through 0006 before starting this version.** The migration adds normalized searchable name/category/status/stance/division metadata, a partial unique valid-identity index and `fighter_import_batches`. Existing fighter payloads are backfilled through validation; invalid/legacy snapshots are excluded from search and listed as unavailable, not deleted. Athlete tables and saved comparisons are not rewritten. Duplicate valid identities in an existing database cause migration failure for operator review rather than silent merging/deletion.

SQLAlchemy write hooks keep metadata aligned with payload changes. Database pagination fetches only the requested page (max 50) and count; ordering is normalized name then ID. Accent-insensitive normalization supports searches such as Jedrzejczyk; wildcard characters are treated literally. Search historical division and current matching context remain distinct controls. Null stance/status stays Unknown and is filterable.

`GET /api/fighters/search?q=...&category=Women&division=Bantamweight&stance=Orthodox&status=Unknown&page=1&page_size=10` returns `{items,total,page,page_size}`. Query length, page and page-size are bounded. Legacy `/api/fighters` remains a list response capped at 50 and advertises `X-Result-Limit`; larger integrations must use pagination. The lab uses the new endpoint, ignores superseded responses and resets pagination on search/filter changes. Ranking still evaluates the candidate set deterministically; it is not limited to the current search page.

Manual lookup now uses the fighter primary key rather than scanning every payload. Ranking resolves the common division reference once per request, removing the prior per-fighter reference query. No athlete-response cache was introduced. With 1,000 synthetic records, the [local benchmark](evidence/phase8/performance.json) measured two queries per search/ranking and one per manual lookup: medians 8.96 ms, 117.93 ms and 0.43 ms respectively over ten samples. These include local SQLite/Python overhead, not network/device/production load results.

## Similarity and explanation

The existing height/reach Gaussian scales (15 cm), optional reach/height scale (0.05), reference-division compatibility, stance agreement and documented-background/style overlap remain deterministic. Group controls normalize to exactly 100% using a deterministic largest-remainder basis-point allocation; enabled physical subweights normalize similarly. Ties use unrounded total score then fighter ID. Original measured/listed weight never becomes a competition limit or target weight.

The important correction is **supported contribution**. If physical weight is 60 and half its requested subdimensions are available, it contributes 30 to the final aggregation, not 60. Other available groups are renormalized against that supported contribution. With a perfect height-only score and a known stance mismatch weighted 40, the result is about 43, not 60. Missing measurements do not become zero, but incomplete evidence cannot quietly retain full group influence. Requested-evidence coverage remains a separate percentage. Whole-point resemblance is not a probability, calibrated confidence score or professional skill comparison.

Results retain component scores, effective weights, physical differences, shared background, unsupported dimensions, category/division exclusions, observation age, source issues and a qualified evidence-support label. Current/history context, minimum coverage, stance/style availability and saved snapshots stay explicit. Saved comparisons keep their original profile, fighter, weights/algorithm/reference snapshots; re-evaluation is deliberate. Imports and rollback never rewrite athlete favorites or plan history.

## Offline refresh, conflict reconciliation and rollback

No provider network call is required at startup. The existing reviewed-local reimport remains for compatibility; it validates the full export and rejects duplicate IDs/normalized identities before writes, and keeps archived revisions. Ordinary production users still cannot refresh shared fighter data. The new operator workflow is separate and never accepts a public HTTP-uploaded path.

From `backend/`, with the intended database URL and an independently reviewed source-permitted JSON file:

```powershell
..\.venv\Scripts\python.exe -m app.fighter_governance C:\reviewed-data\fighters.json
```

Default is preview only: review changed fields, before/after values, identities, source/license references, dates, quality and `preview_token`. All rows validate before mutation; files are capped at 25 MB / 10,000 records. Every source must have explicit licensed/reuse rights and a reference. The tool checks duplicates by ID, normalized category/name and supplied external identifiers. Potential aliases require explicit canonical-ID reconciliation; no fuzzy merge is guessed. Provider takeover and older observation replacement are rejected. A license-reference string is an operator attestation, not external proof of permission.

After reviewing the concrete preview, apply its exact token:

```powershell
..\.venv\Scripts\python.exe -m app.fighter_governance C:\reviewed-data\fighters.json --apply-token REVIEWED_TOKEN
```

Changed existing values also require `--accept-conflicts` after review. The token binds the proposed file and database before/after values; intervening changes reject an old preview. The transaction stores a batch ID and complete before/after changes. No automatic averaging or authority claim resolves a conflicting measurement; the operator chooses the documented supported value and retains rationale in source/issues metadata.

Preview rollback first, then explicitly apply:

```powershell
..\.venv\Scripts\python.exe -m app.fighter_governance --rollback BATCH_ID
..\.venv\Scripts\python.exe -m app.fighter_governance --rollback BATCH_ID --apply-rollback
```

Rollback restores only that batch's prior fighter payloads or removes its newly inserted public snapshots, atomically, and records resolution. It refuses resolved/unknown batches or fighters whose current values differ from the batch's expected result. No athlete records, frozen favorites, workouts or profiles are removed. Test on a disposable DB and rehearse backups; never use destructive migration/rollback tests on personal data.

## Validation and actual results

- Baseline: **221 backend / 11 frontend** passed.
- Current backend: **239 passed**, one existing Starlette/httpx deprecation; [output](evidence/phase8/pytest.txt).
- Frontend: **12 passed**, including server pagination and filter-triggered page reset.
- New tests cover partial-physical weighting, exact normalized percentages, dated professional record provenance, invalid percentages, six-record license/status coverage, duplicate IDs/names/external IDs, conflict/token/rollback protection, athlete export preservation, indexed metadata updates, literal/accent queries, pagination/filter bounds, fixed query counts and 1,000 synthetic records.
- Existing unit normalization, threshold/missing-data/tie/weight/stale/division tests remain passing. SQLite upgrade/check/downgrade/re-upgrade and PostgreSQL offline SQL compile are included. Real PostgreSQL runtime remains unverified.
- App/browser TypeScript, Vite, Ruff and Prettier checks are run. Full Edge matrix: **108 passed, zero failed, seven intentional viewport-specific skips** in 6.1 minutes. All ten new Phase 8 cases passed at 1440/1920/768/390/375 px. Four A4 reports (13 pages) passed [text/margin checks](evidence/phase8/print-checks.json); mobile source/license presentation and a rendered comparison page were visually inspected.

The [first focused browser attempt](evidence/phase8/browser-focused.json) failed all four cases at implicit select-label interaction; explicit accessible labels fixed it. Heading locators were also corrected to the existing side-by-side card title. [Corrected focused run](evidence/phase8/browser-focused-fixed.json): **four passed** on desktop/mobile, covering pagination, filters, license/source quality and unknown women's current status. Full prior-workflow regression passed in [the final Edge report](evidence/phase8/browser-results.json). Seven intentional skips are non-mobile drawer checks at three widths and duplicate print runs at four widths; no retries/flaky passes were used.

## Remaining work and review boundaries

No comprehensive current roster, verified live record feed or dense current statistics. Reuse rights for the original 11 remain unresolved. Secondary-source disagreements need independent corroboration, and exact source-revision capture can strengthen reproducibility. Bulk imports are operator tools, not a managed-provider scheduler or public administration interface. Substring metadata search and full candidate scoring are adequate at the synthetic scale tested, not a production scalability guarantee. Real PostgreSQL, multiworker load, backup restoration, live licensed providers, other browser engines/devices and external security/specialist review remain outstanding. Similarity scales and weights require domain review; they cannot predict competitive outcomes or fighting potential.


Browser evidence includes provenance [1440](evidence/phase8/desktop-1440-phase8-provenance.png), [1920](evidence/phase8/desktop-1920-phase8-provenance.png), [768](evidence/phase8/tablet-768-phase8-provenance.png), [390](evidence/phase8/mobile-390-phase8-provenance.png), [375](evidence/phase8/mobile-375-phase8-provenance.png), and women/history screenshots in the same folder. Original tracker tracked files remain unchanged.
