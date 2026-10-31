# Source and permissions register

## Phase 9 nutrition review — 2026-10-31

The catalog expands from 22 to **40** records from the official [USDA SR Legacy April 2018 archive](https://fdc.nal.usda.gov/download-datasets/). [USDA's API guide](https://fdc.nal.usda.gov/api-guide/) identifies public-domain data under CC0 1.0. No external API key, scraping, branded-product rights assumption or startup dependency is used. The source archive hash is pinned in the importer and every record. Review date does not make this historical snapshot current.

New sodium/calcium/iron/potassium are extracted by nutrient IDs 1093/1087/1089/1092, in mg per 100 g edible food; fiber remains g per 100 g. Optional missing composition is null. All 40 currently contain these nutrients. Product cross-contact and halal certification are unknown, separate from generic composition and editorial exclusions. See [coverage and methodology](PHASE9_NUTRITION.md).

Initial review date: **2026-10-30**. Phase 4 fighter/reference review: **2026-10-31**. No continuous updates are implied. API source metadata accompanies individual fighter records.

| Reference | Data used |
| --- | --- |
| [UFC weight classes](https://www.ufc.com/news/understanding-ufc-weight-classes-and-weigh-ins) | Championship limits and typical non-title allowances. |
| [UFC rankings](https://www.ufc.com/rankings) | Distinction between active women's divisions and historical featherweight availability; recheck before competition use. |
| [Max Holloway career highlights](https://www.ufc.com/news/max-holloway-career-highlights-ufc-308-topuria-vs-holloway-abu-dhabi) | Historical 2024 snapshot: height 71 in, reach 69 in, featherweight/lightweight history. Current record, weight and status intentionally omitted. |
| [Alexander Volkanovski official profile](https://www.ufc.com/athlete/alexander-volkanovski?language_content_entity=en&page=1) | Source-listed height 66 in, reach 71.5 in and weight 158.30 lb, plus featherweight context and source-listed activity status. |
| [Israel Adesanya official profile](https://www.ufc.com/athlete/israel-adesanya?language_content_entity=en&page=1) | Height 76 in, reach 80 in, listed weight 185 lb, Freestyle label and professional boxing/kickboxing background. |
| [Original Mifflin–St Jeor study](https://pubmed.ncbi.nlm.nih.gov/2305711/) | Simplified resting expenditure equation. |
| [NIDDK Body Weight Planner](https://www.niddk.nih.gov/health-information/weight-management/body-weight-planner) | Adult-only scope and exclusion of pregnancy/breastfeeding from automated adult weight-planning tools. |
| [ACSM resistance exercise guidance](https://www.acsm.org/docs/default-source/files-for-resource-library/resistance-training-for-health.pdf) | General background for conservative resistance exercise; app templates are not a validated MMA protocol. |
| [OpenAI structured output documentation](https://developers.openai.com/api/docs/guides/structured-outputs) | Responses API schema-based output implementation. |

Some UFC direct page opens returned HTTP 403. Factual profile fields were reviewed through the search service's indexed official UFC excerpts; they are stored as **development snapshots**, not a current licensed statistics feed. URLs and dates remain visible. No fight records or current rankings are invented.

## Rights and ingestion

Public accessibility is not evidence of redistribution rights. No automated scraper, live bulk-download integration, athlete image download, UFC logo or copyrighted biography is included. This is a minimal manually curated factual development subset with attribution. Commercial redistribution permissions have **not** been established. Before expanding or publicly distributing a live dataset, obtain an appropriate license or documented permission and review provider terms, robots policies, rate limits and permitted caching.

`FighterDataProvider` isolates data access. `SeededFighterProvider` supplies the reviewed development subset; startup persists it without overwriting existing snapshots. API comparisons read `DatabaseFighterProvider`. Replace this with a licensed adapter or validated import without changing matching logic. Unknown fields remain absent/null. Public snapshots survive user account deletion because they contain no athlete account data.

Fonts are bundled through Fontsource packages, which retain upstream license files in their packages. No external font request occurs at runtime. Lucide icons are used without UFC branding. The original illustrative ingredient subset was superseded by the source-backed USDA catalog documented in the Phase 5/9 registers above and below.


Phase 2 source note (2026-10-30): the legacy ACSM PDF link above returned HTTP 404 when checked. It is retained as historical background, not claimed as freshly verified evidence for template v2. The new timed-block/progression choices are explicitly labeled product heuristics and require qualified review. No new fighter or nutrient records were added during this audit.


## Phase 3 training sources (checked 2026-10-30)

The [Phase 3 scientific-basis table](PHASE3_TRAINING.md#scientific-basis) maps each source to its supported principle and limitation. The current catalog links [ACSM's 2026 resistance-training position stand](https://pmc.ncbi.nlm.nih.gov/articles/PMC12965823/), [CDC intensity guidance](https://www.cdc.gov/physical-activity-basics/measuring/), and the [IOC load consensus](https://bjsm.bmj.com/content/50/17/1030). Additional context: [ACSM 2009 progression](https://pubmed.ncbi.nlm.nih.gov/19204579/), [Foster 2001 session-RPE monitoring](https://pubmed.ncbi.nlm.nih.gov/11708692/), and [Saw et al. subjective monitoring review](https://pmc.ncbi.nlm.nih.gov/articles/PMC4789708/).

Catalog cues and mistake/modification text are original editorial summaries, not copied source text or source-specific biomechanical validation. Muscle lists are broad involvement descriptions. Exact app thresholds and 12-week organization are heuristics; sources do not establish their effectiveness for individual MMA athletes. The 2009 source is historical context, not presented as the latest adult guidance. No new licensed fighter/nutrient data or athlete imagery was introduced.


## Phase 4 fighter register (2026-10-31)

This register supersedes the original three-record descriptions above. Direct profile requests returned **403**; review used the search service's **indexed official UFC excerpts**, not a full live feed. The stored `observed_at`/`verified_at` date identifies that review, not when measurements were taken. Copyright/redistribution rights remain **not established**. No scraper, complete biographies, images, current rankings or live statistics are included. Coverage is 11 fighters: seven men and four women; it is not comprehensive across UFC divisions.

| Official profile | Height / reach (in) | Listed weight (lb) | Current profile division / history used | Source status |
| --- | --- | --- | --- | --- |
| [Max Holloway](https://www.ufc.com/athlete/max-holloway?language_content_entity=en&page=8) | 71 / 69 | 155 | Lightweight / featherweight, lightweight | Active |
| [Alexander Volkanovski](https://www.ufc.com/index.php/athlete/alexander-volkanovski) | 66 / 71.5 | 158.3 | Featherweight / featherweight, lightweight | Active |
| [Israel Adesanya](https://www.ufc.com/athlete/israel-adesanya) | 76 / 80 | 185 | Middleweight / middleweight, light heavyweight | Active |
| [Valentina Shevchenko](https://www.ufc.com/athlete/valentina-shevchenko?page=1) | 65 / 67 | 124.6 | Flyweight / flyweight only in this subset | Active |
| [Zhang Weili](https://www.ufc.com/athlete/zhang-weili) | 64 / 63 | 124.6 | Profile-listed flyweight / strawweight, flyweight | Active |
| [Joanna Jedrzejczyk](https://www.ufc.com/athlete/joanna-jedrzejczyk?id=&page=1) | 66 / 65.5 | 116 | No current division / strawweight, flyweight | Retired |
| [Georges St-Pierre](https://www.ufc.com/athlete/georges-st-pierre) | 70.5 / 76 | 184.4 | No current division / welterweight, middleweight | Retired |
| [Tom Aspinall](https://www.ufc.com/athlete/tom-aspinall?page=1) | 77 / 78 | 254 | Heavyweight / heavyweight | Active |
| [Alex Pereira](https://www.ufc.com/athlete/alex-pereira) | 76 / 79 | 251 | Profile-listed heavyweight / middleweight, light heavyweight, heavyweight | Active |
| [Demetrious Johnson](https://www.ufc.com/athlete/temetoriasu-shiyonson) | 63 / 66 | 125 | No current division / flyweight | Not Fighting (not a verified global retirement claim) |
| [Amanda Nunes](https://www.ufc.com/athlete/amanda-nunes?language_content_entity=es) | 68 / 69 | 135 | Bantamweight / bantamweight, historical featherweight | Active at indexed snapshot |

Field-level source IDs are stored with every known matching attribute. Profile Q&A supports Volkanovski's BJJ/wrestling, Adesanya's kickboxing/boxing/BJJ, Jedrzejczyk's Muay Thai, Pereira's kickboxing and Nunes's boxing/BJJ/judo/karate practice. Missing background is unknown. Raw style labels (Muay Thai, Freestyle, Karate, Striker, Kickboxer) remain descriptive; they are not inferred skill scores or automatically translated into pressure/counter/grappling traits. No current stance is asserted.

Additional history sources: [Holloway career article](https://www.ufc.com/news/max-holloway-career-highlights-ufc-308-topuria-vs-holloway-abu-dhabi), [UFC 284](https://www.ufc.com/news/significant-stats-ufc-284-makhachev-vs-volkanovski), [UFC 259](https://www.ufc.com/event/ufc-259), [2026 featherweight context](https://www.ufc.com/news/where-we-stand-ufc-featherweight-division), and [St-Pierre retirement announcement, 2019-02-21](https://www.ufc.com/news/ufc-and-canadian-icon-georges-st-pierre-retires). The retirement article supports his historical 26 career wins; this is not a live record. [Pre-UFC 275 statistics](https://www.ufc.com/news/significant-stats-ufc-275-teixeira-prochazka) supports Jedrzejczyk's historical 6.62 significant strikes landed/minute, labeled with the 2022-06-11 event context. Neither statistic affects similarity.

Conflicting bout-table/narrative results on Adesanya, Pereira and Zhang excerpts are deliberately omitted. Pereira and Zhang have profile-listed division versus ranking-list differences; both the current-profile context and documented history remain visible, with no assertion that one division covers an entire career. Zhang's exact transition date is omitted because excerpts disagree. Nunes's current source-listed activity is not replaced by remembered 2023 retirement history. The current [UFC division reference](https://www.ufc.com/news/understanding-ufc-weight-classes-and-weigh-ins) and [rankings](https://www.ufc.com/rankings) support active women's 115/125/135 and historical inactive 145; title/non-title/everyday/listed/target weights are separate contexts.

`LicensedFileFighterProvider` accepts an operator-supplied JSON export only with matching source license references; it does not establish the legal sufficiency of those references, fetch third-party URLs or include a commercial agreement. Live provider access and commercial redistribution remain unverified. Local refresh reimports this fixed reviewed bundle; it does not claim fresh external verification. Existing invalid/legacy provenance is surfaced and excluded pending explicit refresh. Refresh is atomic, rejects newer-date replacement/provider collisions, archives old/new content hashes and leaves favorites and athlete data intact.


## Phase 5 nutrition and coaching sources (reviewed 2026-10-31)

- [USDA download register](https://fdc.nal.usda.gov/download-datasets/) and [official SR Legacy CSV archive](https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip): 22 factual ingredient records extracted directly from `food.csv` and `food_nutrient.csv`, not generated by an LLM. The archived release is April 2018; FDC publication fields are 2019-04-01. The 2026 review date is not a new nutrient analysis.
- [USDA licensing/API guide](https://fdc.nal.usda.gov/api-guide/): USDA states FoodData Central data are public domain, published under CC0 1.0. Attribution is included. No API key or live lookup is needed by the application.
- [Mifflin?St Jeor original equation](https://pubmed.ncbi.nlm.nih.gov/2305711/): adult resting energy estimate, not measured expenditure or a competition diet.
- [ISSN protein position stand](https://pmc.ncbi.nlm.nih.gov/articles/PMC5477153/): exercising-adult protein guidance. [ISSN review](https://pmc.ncbi.nlm.nih.gov/articles/PMC6090881/): general exercise carbohydrate/fat context and individualized higher-volume needs. Exact activity factors, energy bands, adjustment caps, screening thresholds and meal solver rules are app heuristics, not validated by those papers.
- [Official OpenAI structured-output documentation](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses): Responses `text.format`, strict JSON Schema, nullable structured intents and handling invalid/refused/incomplete output. Schema adherence is not proof that an action or explanation is correct; the backend validates every proposal independently.

The normalized [ingredient catalog](../backend/app/data/ingredients.json) includes each original description, FDC URL/ID, per-100g source kcal, protein, carbohydrate, fat and fiber, units, serving basis and source metadata. [Reproducible importer](../backend/tools/import_usda.py) requires a downloaded official archive and makes no network requests. Archive SHA-256: `b80817294b8850530aaedf2e515c02593b1824f763a0ff356e5c2081643e6fd0`.

Included FDC IDs: rice 168878; lentils 172421; chickpeas 173757; potato 170440; broccoli 170379; banana 173944; olive oil 171413; chicken 171477; tofu 172475; oats 173904; quinoa 168917; black beans 173735; Greek yogurt 170894; egg 173424; carrot 170393; tomato 170457; apple 171688; orange 169097; bulgur 170287; couscous 169700; spinach 168462; salmon 175168. Source energy remains distinct from the app's 4/4/9 macro-derived display energy. No nutrient values were hand-invented to reconcile the two.

Diet/allergen screening, halal sourcing notes, role labels, preparation cues, inspired ingredient patterns and relative cost tiers are editorial metadata. They are not USDA certifications, live prices, authentic cuisine claims or allergy-safety guarantees. This historical generic subset is not a comprehensive food, branded-product, restaurant or complete-diet database. Neither USDA nor the scientific references endorse this application.


## Phase 6 deployment/security implementation references

Reviewed 2026-10-31: [Starlette middleware](https://www.starlette.io/middleware/) for host/header deployment mechanics; [SQLAlchemy SQLite dialect](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html) and [SQLite foreign keys](https://www.sqlite.org/foreignkeys.html) for explicit FK enforcement; [PostgreSQL pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html) for operator backup/restore guidance. These references do not certify this application's security or database compatibility.

Phase 6 changes no athlete science equations, fighter snapshot observations or USDA nutrient values. Existing source/coverage dates remain unchanged. New performance figures are synthetic local measurements in `evidence/phase6/performance.json`, not clinical or production results. Audits are dated advisory queries, not an endorsement or complete supply-chain assessment.


## Phase 7 training review references

Reviewed 2026-10-31: the primary [2026 ACSM resistance-training position stand](https://pmc.ncbi.nlm.nih.gov/articles/PMC12965823/) was opened and reviewed for general healthy-adult progressive resistance/power principles; [IOC load consensus](https://pubmed.ncbi.nlm.nih.gov/27535989/) supports individualized load/context monitoring. Direct BMJ article access returned 403; the primary PubMed abstract and accessible consensus material informed only the general monitoring context. No injury-risk ratio or universally safe workload percentage is inferred.

The exact four/three-day caps, self-reported stage cutoffs, fatigue thresholds, 14/28-day windows, three-exposure plateau rule and power/interval doses are product heuristics requiring qualified review, not conclusions validated by those sources. Kickboxing/Judo additions are original editorial non-contact/coached-practice cues. No fighter observations or USDA nutrient values changed in Phase 7.


## Phase 8 fighter supplement and permissions

[Six-record attribution/license notice](FIGHTER_SUPPLEMENT_LICENSE.md), [exact JSON records](../backend/app/data/fighters_wikimedia.json) and [quality report](evidence/phase8/data-quality.json). Reviewed 2026-10-31. [Wikimedia Terms of Use](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#7._Licensing_of_Content) allows reuse subject to source license/attribution/share-alike obligations; the six adapted records carry CC BY-SA 4.0 and source/history links. Wikidata's CC0 policy was also reviewed but **does not license these Wikipedia-derived records as CC0**.

| Fighter | Source | Original listed height / reach / weight | Included UFC history |
| --- | --- | --- | --- |
| Kamaru Usman | [Wikipedia contributors](https://en.wikipedia.org/wiki/Kamaru_Usman) | 72 in / 76 in / 185 lb | Welterweight only; source Middleweight context not asserted as UFC history |
| Jon Jones | [Wikipedia contributors](https://en.wikipedia.org/wiki/Jon_Jones) | 76 in / 84.5 in / 238 lb | Light Heavyweight, Heavyweight |
| Henry Cejudo | [Wikipedia contributors](https://en.wikipedia.org/wiki/Henry_Cejudo) | 64 in / 64 in / 135 lb | Flyweight, Bantamweight |
| Rose Namajunas | [Wikipedia contributors](https://en.wikipedia.org/wiki/Rose_Namajunas) | 65 in / 65 in / 125 lb | Strawweight, Flyweight |
| Ronda Rousey | [Wikipedia contributors](https://en.wikipedia.org/wiki/Ronda_Rousey) | 66 in / 68 in / 142 lb | Bantamweight; non-UFC featherweight not included |
| Miesha Tate | [Wikipedia contributors](https://en.wikipedia.org/wiki/Miesha_Tate) | 66 in / 65 in / 136 lb | Bantamweight, Flyweight |

All six current career/division/record fields remain unknown; only explicitly supported backgrounds and two stances were included. Source imperial/metric rounding differences are disclosed. These are observed secondary-source facts, not independent official measurement verification. No biographies, images or statistics were fabricated.

The [UFC terms](https://www.ufc.com/news/terms-use) indexed text prohibits automated extraction; direct requests returned 403. No bypass, UFC/UFCStats scraper or assumed sublicensing from an unrelated dataset was used. Original 11 rights remain unestablished, distinct from the licensed six-record supplement. Licensed external files need operator verification of actual access/redistribution terms; a license-reference string alone is not proof.


## Phase 12 safety source audit

See the [dated reference register and source-access limitations](review/METHODOLOGY_INVENTORY.md#source-register). Primary Mifflin and 2026 ACSM pages were opened; official NIDDK, AAP, UFC, ISSN and IOC excerpts were consulted for scope/rationale. Direct UFC/IOC-journal requests returned 403 and the direct protein page challenged browser access. Exact app thresholds and templates remain product heuristics; no author, clinician or organization endorsed this application. No new nutrient/fighter data or license permissions were obtained.


## Phase14 release acceptance

The [current acceptance report](PHASE14_ACCEPTANCE.md), [feature matrix](PHASE14_FEATURE_MATRIX.md), [known limitations](KNOWN_LIMITATIONS.md), [user guide](USER_GUIDE.md) and [AI configuration guide](AI_CONFIGURATION.md) consolidate the release. Current schema head is0008. Historical results above retain their phase-specific context; Phase14 evidence supersedes release totals. No public deployment, live AI, real IdP or PostgreSQL runtime verification is claimed. Source validation rechecks bundled schemas/provenance and nutrient completeness; it does not reverify current fighter facts online.


## Phase15 curated additions (2026-10-31)

Food catalog v3 contains55 USDA SR Legacy April2018 records, extracted from the same official ZIP whose SHA256 is b80817294b8850530aaedf2e515c02593b1824f763a0ff356e5c2081643e6fd0. See backend/tools/import_usda.py for the explicit FDC identifiers/selection and preserved nutrient units, publication/review dates and per-field missing values. Reproduction requires the official archive at the download_url stored in each record; it is not committed or a startup network dependency. [USDA licensing](https://fdc.nal.usda.gov/api-guide/#bkmk-9) states CC0/public-domain use. Generic ingredient allergy tags and cost tiers are editorial, not USDA certification or current prices. Added nuts/seeds, skim/soy milk, turkey/beef, avocado, mango, vegetables and rice noodles; all9tracked nutrient values are present in all55records.

Two new source-backed historical participants: [Alexander Volkov](https://en.wikipedia.org/wiki/Alexander_Volkov_(fighter)) and [Antonina Shevchenko](https://en.wikipedia.org/wiki/Antonina_Shevchenko). Reviewed the article text/measurements and historical UFC sections; copied only a small factual subset. Volkov: source-listed79in height/80in reach/257lb weight, historical UFC Heavyweight, documented BJJ rank. Antonina:68in/68in/125lb, historical UFC Flyweight, Southpaw, documented MuayThai/kickboxing participation. Current division/status and professional records remain unknown. Canonical cm/kg are arithmetic conversions of the listed imperial figures, not new measurements. Article text is a secondary source and does not independently establish physical accuracy. No live statistics, team-to-skill inference or subjective style trait was added.

[Wikimedia reuse terms](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#7._Licensing_of_Content) require attribution/license/share-alike for adaptations. All eight adapted records retain per-source links/license references; [supplement license](FIGHTER_SUPPLEMENT_LICENSE.md) names every article/history. The original11records retain unresolved redistribution rights; the19record bundle has no blanket commercial license. No prohibited scraping or paid data service was used.

Exercise additions use editorial coaching cues and existing general resistance/load principles, plus [CDC adult activity guidance](https://www.cdc.gov/physical-activity-basics/guidelines/adults.html). These sources support general categories and conservative practice, not validation of individual techniques, specific doses or MMA efficacy. New power/partner drills explicitly require qualified supervision. Independent specialist review remains pending.


[Food-label guidance from the FDA](https://www.fda.gov/consumers/consumer-updates/have-food-allergies-read-label) distinguishes peanuts from tree nuts and directs consumers to ingredient labels. The application's conservative treatment of the ambiguous input "nuts" excludes both groups; this is an editorial screening rule, not a diagnosis or a guarantee about cross-contact. Explicit peanut/peanuts spellings normalize together. Product labels and qualified allergy care remain necessary.
