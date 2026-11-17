# Source and permissions register

## Phase 9 nutrition review — 2026-10-31

The catalog expands from 22 to **40** records from the official [USDA SR Legacy April 2018 archive](https://fdc.nal.usda.gov/download-datasets/). [USDA's API guide](https://fdc.nal.usda.gov/api-guide/) identifies public-domain data under CC0 1.0. No external API key, scraping, branded-product rights assumption or startup dependency is used. The source archive hash is pinned in the importer and every record. Review date does not make this historical snapshot current.

New sodium/calcium/iron/potassium are extracted by nutrient IDs 1093/1087/1089/1092, in mg per 100 g edible food; fiber remains g per 100 g. Optional missing composition is null. All 40 currently contain these nutrients. Product cross-contact and halal certification are unknown, separate from generic composition and editorial exclusions. See [coverage and methodology](history/PHASE9_NUTRITION.md).

Initial review date: **2026-10-30**. Phase 4 fighter/reference review: **2026-10-31**. No continuous updates are implied. API source metadata accompanies individual fighter records.

| Reference | Data used |
| --- | --- |
| [UFC weight classes](https://www.ufc.com/news/understanding-ufc-weight-classes-and-weigh-ins) | Championship limits and typical non-title allowances. |
| [UFC rankings](https://www.ufc.com/rankings) | Distinction between active women's divisions and historical featherweight availability; recheck before competition use. |
| [Original Mifflin–St Jeor study](https://pubmed.ncbi.nlm.nih.gov/2305711/) | Simplified resting expenditure equation. |
| [NIDDK Body Weight Planner](https://www.niddk.nih.gov/health-information/weight-management/body-weight-planner) | Adult-only scope and exclusion of pregnancy/breastfeeding from automated adult weight-planning tools. |
| [ACSM resistance exercise guidance](https://www.acsm.org/docs/default-source/files-for-resource-library/resistance-training-for-health.pdf) | General background for conservative resistance exercise; app templates are not a validated MMA protocol. |
| [OpenAI structured output documentation](https://developers.openai.com/api/docs/guides/structured-outputs) | Responses API schema-based output implementation. |

## Rights and ingestion

Public accessibility is not evidence of redistribution rights. No automated scraper, live bulk-download integration, athlete image download, UFC logo or copyrighted biography is included. The fighter records are a small, manually curated subset adapted from Wikipedia under CC BY-SA 4.0, with attribution. Before expanding or publicly distributing a live dataset, obtain an appropriate license or documented permission and review provider terms, robots policies, rate limits and permitted caching.

`FighterDataProvider` isolates data access. `SeededFighterProvider` supplies the reviewed development subset; startup persists it without overwriting existing snapshots. API comparisons read `DatabaseFighterProvider`. Replace this with a licensed adapter or validated import without changing matching logic. Unknown fields remain absent/null. Public snapshots survive user account deletion because they contain no athlete account data.

Fonts are bundled through Fontsource packages, which retain upstream license files in their packages. No external font request occurs at runtime. Lucide icons are used without UFC branding. The original illustrative ingredient subset was superseded by the source-backed USDA catalog documented in the Phase 5/9 registers above and below.


Phase 2 source note (2026-10-30): the legacy ACSM PDF link above returned HTTP 404 when checked. It is retained as historical background, not claimed as freshly verified evidence for template v2. The new timed-block/progression choices are explicitly labeled product heuristics and require qualified review. No new fighter or nutrient records were added during this audit.


## Phase 3 training sources (checked 2026-10-30)

The [Phase 3 scientific-basis table](history/PHASE3_TRAINING.md#scientific-basis) maps each source to its supported principle and limitation. The current catalog links [ACSM's 2026 resistance-training position stand](https://pmc.ncbi.nlm.nih.gov/articles/PMC12965823/), [CDC intensity guidance](https://www.cdc.gov/physical-activity-basics/measuring/), and the [IOC load consensus](https://bjsm.bmj.com/content/50/17/1030). Additional context: [ACSM 2009 progression](https://pubmed.ncbi.nlm.nih.gov/19204579/), [Foster 2001 session-RPE monitoring](https://pubmed.ncbi.nlm.nih.gov/11708692/), and [Saw et al. subjective monitoring review](https://pmc.ncbi.nlm.nih.gov/articles/PMC4789708/).

Catalog cues and mistake/modification text are original editorial summaries, not copied source text or source-specific biomechanical validation. Muscle lists are broad involvement descriptions. Exact app thresholds and 12-week organization are heuristics; sources do not establish their effectiveness for individual MMA athletes. The 2009 source is historical context, not presented as the latest adult guidance. No new licensed fighter/nutrient data or athlete imagery was introduced.


## Fighter records from Wikipedia (2026-11-17)

On 2026-11-17 the 11 records taken from official ufc.com profiles (the Phase 4 register, now only in git history) were replaced by records adapted from English Wikipedia under CC BY-SA 4.0, handled like the Phase 8 supplement below. Each record keeps the same application ID, cites its article, and stores the revision it was read from (`external_ids.wikipedia-en-revision`). The links below open that exact revision.

Values come from the article's infobox at that revision: height, reach and listed weight as published; stance only where the infobox states one; background only from the infobox `style` and `rank` fields (including belt ranks); and division history from the infobox weight classes for MMA, which can include bouts outside the UFC. Current division, career status and fight records are unknown for all of them, as for the Phase 8 records. No images, biographies or statistics were copied.

| Fighter (revision) | Revision ID | Height / reach / listed weight | Stance | Background | Division history |
| --- | --- | --- | --- | --- | --- |
| [Max Holloway](https://en.wikipedia.org/w/index.php?title=Max_Holloway&oldid=1384078139) | 1384078139 | 71 in / 69 in / 170 lb | not stated | BJJ | Featherweight, Lightweight, Welterweight |
| [Alexander Volkanovski](https://en.wikipedia.org/w/index.php?title=Alexander_Volkanovski&oldid=1384732303) | 1384732303 | 66 in / 71.5 in / 145 lb | Orthodox | none stated | Featherweight, Lightweight, Welterweight |
| [Israel Adesanya](https://en.wikipedia.org/w/index.php?title=Israel_Adesanya&oldid=1385933236) | 1385933236 | 76 in / 80 in / 185 lb | Switch | Kickboxing | Middleweight, Light Heavyweight |
| [Valentina Shevchenko](https://en.wikipedia.org/w/index.php?title=Valentina_Shevchenko&oldid=1386092351) | 1386092351 | 65 in / 66.5 in / 125 lb | Southpaw | Muay Thai, Taekwondo, Judo | Bantamweight, Flyweight |
| [Zhang Weili](https://en.wikipedia.org/w/index.php?title=Zhang_Weili&oldid=1384948982) | 1384948982 | 64 in / 63 in / 125 lb | Switch | BJJ | Strawweight, Flyweight |
| [Joanna Jędrzejczyk](https://en.wikipedia.org/w/index.php?title=Joanna_Jędrzejczyk&oldid=1383746405) | 1383746405 | 66 in / 65.5 in / 115 lb | not stated | Muay Thai, Kickboxing, BJJ | Strawweight, Flyweight |
| [Georges St-Pierre](https://en.wikipedia.org/w/index.php?title=Georges_St-Pierre&oldid=1385755393) | 1385755393 | 70 in / 76 in / 170 lb | not stated | none stated | Welterweight, Middleweight |
| [Tom Aspinall](https://en.wikipedia.org/w/index.php?title=Tom_Aspinall&oldid=1385977885) | 1385977885 | 77 in / 78 in / 255 lb | Orthodox | none stated | Heavyweight |
| [Alex Pereira](https://en.wikipedia.org/w/index.php?title=Alex_Pereira&oldid=1385109552) | 1385109552 | 76 in / 79 in / 251 lb | Orthodox | Kickboxing, BJJ | Middleweight, Light Heavyweight, Heavyweight |
| [Demetrious Johnson](https://en.wikipedia.org/w/index.php?title=Demetrious_Johnson&oldid=1380867659) | 1380867659 | 63 in / 66 in / 135 lb | Orthodox | BJJ | Flyweight, Bantamweight |
| [Amanda Nunes](https://en.wikipedia.org/w/index.php?title=Amanda_Nunes&oldid=1385828415) | 1385828415 | 68 in / 69 in / 135 lb | Orthodox | BJJ, Judo | Bantamweight, Featherweight |

Notes recorded with the affected records: Max Holloway's 170 lb listed weight is the infobox value at this revision, which also lists a 2026 Welterweight entry; Demetrious Johnson's Bantamweight entry covers 135 lb bouts in ONE Championship, which names that class Flyweight; women's Featherweight (Amanda Nunes) is inactive in the current UFC reference model.

A local database seeded before this change keeps the old records until a fighter data refresh. The refresh accepts this one provider change (`reviewed-local` to `wikimedia-reviewed`) for the same fighter IDs and archives the old payloads; any other provider change is still rejected.

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

[Attribution/license notice](FIGHTER_SUPPLEMENT_LICENSE.md) (now covering all 19 records), [exact JSON records](../backend/app/data/fighters_wikimedia.json) and quality report (`evidence/phase8/data-quality.json`). Reviewed 2026-10-31. [Wikimedia Terms of Use](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#7._Licensing_of_Content) allows reuse subject to source license/attribution/share-alike obligations; the six adapted records carry CC BY-SA 4.0 and source/history links. Wikidata's CC0 policy was also reviewed but **does not license these Wikipedia-derived records as CC0**.

| Fighter | Source | Original listed height / reach / weight | Included UFC history |
| --- | --- | --- | --- |
| Kamaru Usman | [Wikipedia contributors](https://en.wikipedia.org/wiki/Kamaru_Usman) | 72 in / 76 in / 185 lb | Welterweight only; source Middleweight context not asserted as UFC history |
| Jon Jones | [Wikipedia contributors](https://en.wikipedia.org/wiki/Jon_Jones) | 76 in / 84.5 in / 238 lb | Light Heavyweight, Heavyweight |
| Henry Cejudo | [Wikipedia contributors](https://en.wikipedia.org/wiki/Henry_Cejudo) | 64 in / 64 in / 135 lb | Flyweight, Bantamweight |
| Rose Namajunas | [Wikipedia contributors](https://en.wikipedia.org/wiki/Rose_Namajunas) | 65 in / 65 in / 125 lb | Strawweight, Flyweight |
| Ronda Rousey | [Wikipedia contributors](https://en.wikipedia.org/wiki/Ronda_Rousey) | 66 in / 68 in / 142 lb | Bantamweight; non-UFC featherweight not included |
| Miesha Tate | [Wikipedia contributors](https://en.wikipedia.org/wiki/Miesha_Tate) | 66 in / 65 in / 136 lb | Bantamweight, Flyweight |

All six current career/division/record fields remain unknown; only explicitly supported backgrounds and two stances were included. Source imperial/metric rounding differences are disclosed. These are observed secondary-source facts, not independent official measurement verification. No biographies, images or statistics were fabricated.

No UFC or UFCStats scraper, and no data assumed sublicensed from an unrelated dataset, was used. Licensed external files need operator verification of actual access/redistribution terms; a license-reference string alone is not proof.


## Phase 12 safety source audit

See the [dated reference register and source-access limitations](history/review/METHODOLOGY_INVENTORY.md#source-register). Primary Mifflin and 2026 ACSM pages were opened; official NIDDK, AAP, UFC, ISSN and IOC excerpts were consulted for scope/rationale. Direct UFC/IOC-journal requests returned 403 and the direct protein page challenged browser access. Exact app thresholds and templates remain product heuristics; no author, clinician or organization endorsed this application. No new nutrient/fighter data or license permissions were obtained.


## Phase14 release acceptance

The [current acceptance report](history/PHASE14_ACCEPTANCE.md), [feature matrix](history/PHASE14_FEATURE_MATRIX.md), [known limitations](KNOWN_LIMITATIONS.md), [user guide](USER_GUIDE.md) and [AI configuration guide](AI_CONFIGURATION.md) consolidate the release. Current schema head is0008. Historical results above retain their phase-specific context; Phase14 evidence supersedes release totals. No public deployment, live AI, real IdP or PostgreSQL runtime verification is claimed. Source validation rechecks bundled schemas/provenance and nutrient completeness; it does not reverify current fighter facts online.


## Phase15 curated additions (2026-10-31)

Food catalog v3 contains55 USDA SR Legacy April2018 records, extracted from the same official ZIP whose SHA256 is b80817294b8850530aaedf2e515c02593b1824f763a0ff356e5c2081643e6fd0. See backend/tools/import_usda.py for the explicit FDC identifiers/selection and preserved nutrient units, publication/review dates and per-field missing values. Reproduction requires the official archive at the download_url stored in each record; it is not committed or a startup network dependency. [USDA licensing](https://fdc.nal.usda.gov/api-guide/#bkmk-9) states CC0/public-domain use. Generic ingredient allergy tags and cost tiers are editorial, not USDA certification or current prices. Added nuts/seeds, skim/soy milk, turkey/beef, avocado, mango, vegetables and rice noodles; all9tracked nutrient values are present in all55records.

Two new source-backed historical participants: [Alexander Volkov](https://en.wikipedia.org/wiki/Alexander_Volkov_(fighter)) and [Antonina Shevchenko](https://en.wikipedia.org/wiki/Antonina_Shevchenko). Reviewed the article text/measurements and historical UFC sections; copied only a small factual subset. Volkov: source-listed79in height/80in reach/257lb weight, historical UFC Heavyweight, documented BJJ rank. Antonina:68in/68in/125lb, historical UFC Flyweight, Southpaw, documented MuayThai/kickboxing participation. Current division/status and professional records remain unknown. Canonical cm/kg are arithmetic conversions of the listed imperial figures, not new measurements. Article text is a secondary source and does not independently establish physical accuracy. No live statistics, team-to-skill inference or subjective style trait was added.

[Wikimedia reuse terms](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#7._Licensing_of_Content) require attribution/license/share-alike for adaptations. All eight adapted records retain per-source links/license references; [supplement license](FIGHTER_SUPPLEMENT_LICENSE.md) names every article/history. The original11records retain unresolved redistribution rights; the19record bundle has no blanket commercial license. No prohibited scraping or paid data service was used.

Exercise additions use editorial coaching cues and existing general resistance/load principles, plus [CDC adult activity guidance](https://www.cdc.gov/physical-activity-basics/guidelines/adults.html). These sources support general categories and conservative practice, not validation of individual techniques, specific doses or MMA efficacy. New power/partner drills explicitly require qualified supervision. Independent specialist review remains pending.


[Food-label guidance from the FDA](https://www.fda.gov/consumers/consumer-updates/have-food-allergies-read-label) distinguishes peanuts from tree nuts and directs consumers to ingredient labels. The application's conservative treatment of the ambiguous input "nuts" excludes both groups; this is an editorial screening rule, not a diagnosis or a guarantee about cross-contact. Explicit peanut/peanuts spellings normalize together. Product labels and qualified allergy care remain necessary.
