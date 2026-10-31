"""Small reviewed factual subset. URLs support fields, not redistribution rights.

Observed via indexed official excerpts on 2026-10-31; direct requests returned 403.
No bulk collection, images, biographies, inferred skills or current fight records.
"""

from .fighter_models import FighterRecord, normalize_measurement

VERIFIED = "2026-10-31"


def reviewed_records():
    # Inches and pounds as published; conversion does not add measurement precision.
    rows = [
        (
            "holloway",
            "Max Holloway",
            "Men",
            71,
            69,
            155,
            "Lightweight",
            ["Featherweight", "Lightweight"],
            "Active",
            [],
            ["Muay Thai"],
            "max-holloway?language_content_entity=en&page=8",
        ),
        (
            "volkanovski",
            "Alexander Volkanovski",
            "Men",
            66,
            71.5,
            158.3,
            "Featherweight",
            ["Featherweight", "Lightweight"],
            "Active",
            ["BJJ", "Wrestling"],
            [],
            "alexander-volkanovski",
        ),
        (
            "adesanya",
            "Israel Adesanya",
            "Men",
            76,
            80,
            185,
            "Middleweight",
            ["Middleweight", "Light Heavyweight"],
            "Active",
            ["Kickboxing", "Boxing", "BJJ"],
            ["Freestyle"],
            "israel-adesanya",
        ),
        (
            "shevchenko",
            "Valentina Shevchenko",
            "Women",
            65,
            67,
            124.6,
            "Flyweight",
            ["Flyweight"],
            "Active",
            [],
            ["Muay Thai"],
            "valentina-shevchenko?page=1",
        ),
        (
            "zhang",
            "Zhang Weili",
            "Women",
            64,
            63,
            124.6,
            "Flyweight",
            ["Strawweight", "Flyweight"],
            "Active",
            [],
            ["Muay Thai"],
            "zhang-weili",
        ),
        (
            "jedrzejczyk",
            "Joanna Jedrzejczyk",
            "Women",
            66,
            65.5,
            116,
            None,
            ["Strawweight", "Flyweight"],
            "Retired",
            ["Muay Thai"],
            ["Striker"],
            "joanna-jedrzejczyk?id=&page=1",
        ),
        (
            "st-pierre",
            "Georges St-Pierre",
            "Men",
            70.5,
            76,
            184.4,
            None,
            ["Welterweight", "Middleweight"],
            "Retired",
            [],
            ["Karate"],
            "georges-st-pierre",
        ),
        (
            "aspinall",
            "Tom Aspinall",
            "Men",
            77,
            78,
            254,
            "Heavyweight",
            ["Heavyweight"],
            "Active",
            [],
            ["Freestyle"],
            "tom-aspinall?page=1",
        ),
        (
            "pereira",
            "Alex Pereira",
            "Men",
            76,
            79,
            251,
            "Heavyweight",
            ["Middleweight", "Light Heavyweight", "Heavyweight"],
            "Active",
            ["Kickboxing"],
            ["Kickboxer"],
            "alex-pereira",
        ),
        (
            "johnson",
            "Demetrious Johnson",
            "Men",
            63,
            66,
            125,
            None,
            ["Flyweight"],
            "Not fighting",
            [],
            [],
            "temetoriasu-shiyonson",
        ),
        (
            "nunes",
            "Amanda Nunes",
            "Women",
            68,
            69,
            135,
            "Bantamweight",
            ["Bantamweight", "Featherweight"],
            "Active",
            ["Boxing", "BJJ", "Judo", "Karate"],
            ["Striker"],
            "amanda-nunes?language_content_entity=es",
        ),
    ]
    output = []
    for (
        fid,
        name,
        category,
        height,
        reach,
        pounds,
        current,
        history,
        status,
        background,
        styles,
        slug,
    ) in rows:
        url = "https://www.ufc.com/athlete/" + slug
        source = {
            "id": "profile",
            "url": url,
            "publisher": "UFC",
            "observed_at": VERIFIED,
            "method": "indexed_official_excerpt",
            "rights": "not_established",
        }
        payload = dict(
            provider_id="reviewed-local",
            id=fid,
            name=name,
            competition_division=category,
            height_cm=normalize_measurement(height, "in", "length"),
            reach_cm=normalize_measurement(reach, "in", "length"),
            listed_weight_kg=normalize_measurement(pounds, "lb", "weight"),
            current_division=current,
            division_history=[
                {
                    "name": d,
                    "context": "Source-listed UFC competition history; not an assertion of current eligibility or complete career history.",
                    "source_ids": ["profile"],
                }
                for d in history
            ],
            career_status=status,
            background=background,
            styles=styles,
            verified_at=VERIFIED,
            sources=[source],
            field_sources={
                k: ["profile"]
                for k in [
                    "name",
                    "competition_division",
                    "height_cm",
                    "reach_cm",
                    "listed_weight_kg",
                    "career_status",
                    "background",
                    "styles",
                    "current_division",
                ]
            },
            original_measurements={
                "height": {"value": height, "unit": "in"},
                "reach": {"value": reach, "unit": "in"},
                "listed_weight": {"value": pounds, "unit": "lb"},
            },
            division=" / ".join(history),
            status=status + " at source snapshot",
            source=url,
            source_date=VERIFIED,
            issues=[
                "Indexed official excerpts reviewed; direct profile access returned 403. Observation date is not a new measurement date.",
                "Stance and a shared validated style taxonomy unavailable. Source style labels do not establish proficiency.",
            ],
            note="Sparse factual study comparison. Listed weight is not everyday weight, a division limit, or a recommended target. Background means documented practice, not skill equivalence.",
        )
        if fid in ("zhang", "pereira"):
            payload["issues"].append(
                "Profile-listed current division differs from some ranking listings. Conflicting bout-result text omitted; no win/loss record inferred."
            )
        if fid == "adesanya":
            payload["issues"].append(
                "Conflicting bout-result text omitted; no current win/loss record inferred."
            )
        if fid == "johnson":
            payload["issues"].append(
                "UFC status is 'Not Fighting'; this does not verify current global retirement status."
            )
        if fid == "nunes":
            payload["issues"].append(
                "Historical women's Featherweight is inactive in the current UFC reference model."
            )
        history_sources = {
            "holloway": "https://www.ufc.com/news/max-holloway-career-highlights-ufc-308-topuria-vs-holloway-abu-dhabi",
            "volkanovski": "https://www.ufc.com/news/significant-stats-ufc-284-makhachev-vs-volkanovski",
            "adesanya": "https://www.ufc.com/event/ufc-259",
        }
        if fid in history_sources:
            payload["sources"].append(
                {**source, "id": "division-history", "url": history_sources[fid]}
            )
            payload["division_history"] = [
                {**d, "source_ids": ["division-history"]} for d in payload["division_history"]
            ]
        if fid == "volkanovski":
            payload["sources"][0]["url"] = (
                "https://www.ufc.com/index.php/athlete/alexander-volkanovski"
            )
            payload["source"] = payload["sources"][0]["url"]
            payload["sources"].append(
                {
                    **source,
                    "id": "current-division",
                    "url": "https://www.ufc.com/news/where-we-stand-ufc-featherweight-division",
                    "published_at": "2026-02-04",
                }
            )
            payload["field_sources"]["current_division"] = ["current-division"]
        if fid == "st-pierre":
            payload["sources"].append(
                {
                    **source,
                    "id": "retirement",
                    "url": "https://www.ufc.com/news/ufc-and-canadian-icon-georges-st-pierre-retires",
                    "published_at": "2019-02-21",
                }
            )
            payload["field_sources"]["career_status"] = ["retirement"]
            payload["division_history"] = [
                {**d, "source_ids": ["retirement"]} for d in payload["division_history"]
            ]
            payload["statistics"] = [
                {
                    "name": "Career MMA wins at retirement announcement",
                    "value": 26,
                    "unit": "wins",
                    "as_of": "2019-02-21",
                    "scope": "Historical career figure at retirement announcement; excluded from matching.",
                    "source_ids": ["retirement"],
                }
            ]
        if fid == "jedrzejczyk":
            payload["sources"].append(
                {
                    **source,
                    "id": "historical-stats",
                    "url": "https://www.ufc.com/news/significant-stats-ufc-275-teixeira-prochazka",
                }
            )
            payload["statistics"] = [
                {
                    "name": "Significant strikes landed per minute",
                    "value": 6.62,
                    "unit": "strikes/min",
                    "as_of": "2022-06-11",
                    "scope": "Pre-UFC 275 historical UFC article; event-context date, not current statistics. Excluded from matching.",
                    "source_ids": ["historical-stats"],
                }
            ]
        output.append(FighterRecord.model_validate(payload).model_dump(mode="json"))
    return output
