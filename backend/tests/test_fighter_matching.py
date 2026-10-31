from copy import deepcopy
from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.fighter_models import FighterRecord, normalize_measurement
from app.fighters import LicensedFileFighterProvider, SeededFighterProvider, validated
from app.matching import FighterMatchingService
from app.schemas import Experience, MatchWeights, Profile


class Provider:
    def __init__(self, records):
        self.records = records

    def all(self):
        return deepcopy(self.records)


def physical(**kwargs):
    return MatchWeights(physical=100, background=0, style=0, stance=0, weight_class=0, **kwargs)


def fighter():
    return SeededFighterProvider().all()[0]


def test_perfect_similarity_and_ratio():
    f = fighter()
    p = Profile(height_cm=f["height_cm"], wingspan_cm=f["reach_cm"])
    r = FighterMatchingService(Provider([f])).compare(p, physical(ratio_weight=50), f["id"])
    assert r["score"] == 100
    assert r["coverage"] == 100
    assert set(r["physical_components"].values()) == {100}
    assert r["basis"] == "physical"


def test_missing_reach_renormalizes_but_lowers_coverage():
    f = fighter()
    f["reach_cm"] = None
    r = FighterMatchingService(Provider([f])).compare(
        Profile(height_cm=f["height_cm"], wingspan_cm=175), physical(), f["id"]
    )
    assert r["score"] == 100
    assert r["coverage"] == 50
    assert r["physical_effective_weights"] == {"height": 100}
    assert "reach" in r["quality"]["missing_physical"]
    assert not FighterMatchingService(Provider([f])).rank(Profile(), physical(min_coverage=51))[
        "matches"
    ]


def test_incomplete_record_never_invents_physical_score():
    f = fighter()
    f["height_cm"] = f["reach_cm"] = None
    r = FighterMatchingService(Provider([f])).compare(Profile(), physical(), f["id"])
    assert r["score"] is None and r["coverage"] == 0
    assert "physical" in r["excluded"]
    assert not FighterMatchingService(Provider([f])).rank(Profile(), physical())["matches"]


def test_unit_normalization_and_inconsistent_original_rejected():
    assert normalize_measurement(71, "in", "length") == 180.34
    assert normalize_measurement(1.8034, "m", "length") == 180.34
    assert normalize_measurement(155, "lb", "weight") == pytest.approx(70.3068)
    for value, unit, kind in [
        (5, "lb", "length"),
        (float("nan"), "cm", "length"),
        (-1, "cm", "length"),
        (5, "cm", "unknown"),
    ]:
        with pytest.raises(ValueError):
            normalize_measurement(value, unit, kind)
    f = fighter()
    f["height_cm"] += 1
    with pytest.raises(ValidationError, match="disagree"):
        FighterRecord.model_validate(f)


def test_weights_change_ranking_and_ties_stable():
    a, b = fighter(), fighter()
    a.update(id="a", height_cm=180, reach_cm=160)
    b.update(id="b", height_cm=160, reach_cm=180)
    p = Profile(height_cm=180, wingspan_cm=180)
    service = FighterMatchingService(Provider([b, a]))
    assert (
        service.rank(p, physical(height_weight=100, reach_weight=0))["matches"][0]["fighter"]["id"]
        == "a"
    )
    assert (
        service.rank(p, physical(height_weight=0, reach_weight=100))["matches"][0]["fighter"]["id"]
        == "b"
    )
    ranking = service.rank(p, physical())
    assert [r["fighter"]["id"] for r in ranking["matches"]] == ["a", "b"]
    assert ranking == service.rank(p, physical())


def test_display_rounding_does_not_create_a_sort_tie():
    a, b = fighter(), fighter()
    a.update(id="a", height_cm=180.1)
    b.update(id="b", height_cm=180)
    ranking = FighterMatchingService(Provider([a, b])).rank(
        Profile(height_cm=180), physical(height_weight=100, reach_weight=0)
    )
    assert [r["score"] for r in ranking["matches"]] == [100, 100]
    assert [r["fighter"]["id"] for r in ranking["matches"]] == ["b", "a"]


def test_malformed_original_measurement_rejected_as_validation_error():
    f = fighter()
    f["original_measurements"]["height"] = {"unit": "in"}
    with pytest.raises(ValidationError):
        validated(f)


def test_history_current_and_category_mismatch():
    service = FighterMatchingService()
    p = Profile(weight_kg=77)
    history = service.compare(p, MatchWeights(), "st-pierre")
    current = service.compare(p, MatchWeights(division_mode="current"), "st-pierre")
    assert history["breakdown"]["weight_class"] == 100
    assert "weight_class" in current["excluded"]
    assert service.compare(p, physical(), "nunes")["score"] is None
    assert service.compare(p, physical(same_division_only=True), "aspinall")["score"] is None
    assert service.compare(p, physical(include_retired=False), "st-pierre")["score"] is None


def test_listed_weight_does_not_influence_division_score():
    a = fighter()
    b = deepcopy(a)
    b["listed_weight_kg"] = 150
    service = FighterMatchingService(Provider([a]))
    before = service.compare(Profile(), MatchWeights(), a["id"])
    service.provider = Provider([b])
    after = service.compare(Profile(), MatchWeights(), b["id"])
    assert before["score"] == after["score"]
    assert before["breakdown"] == after["breakdown"]


def test_staleness_filter_and_honest_missing_style():
    f = fighter()
    f["verified_at"] = (date.today() - timedelta(days=366)).isoformat()
    service = FighterMatchingService(Provider([f]))
    assert service.compare(Profile(), physical(), f["id"])["quality"]["stale"]
    assert not service.rank(Profile(), physical(include_stale=False))["matches"]
    assert not service.rank(
        Profile(), MatchWeights(physical=0, background=0, style=100, stance=0, weight_class=0)
    )["matches"]


def test_documented_background_stance_and_shared_style():
    f = fighter()
    f.update(background=["Boxing", "BJJ"], stance="Orthodox", style_traits=["Pressure"])
    p = Profile(stance="Orthodox", experience=[Experience(discipline="Boxing", months=12)])
    result = FighterMatchingService(Provider([f])).compare(
        p, MatchWeights(style_preferences=["Pressure"]), f["id"]
    )
    assert result["breakdown"]["background"] == 50
    assert result["breakdown"]["stance"] == result["breakdown"]["style"] == 100


def test_catalog_field_provenance_and_observed_dates():
    records = SeededFighterProvider().all()
    assert len(records) == 19
    assert len([r for r in records if r["competition_division"] == "Women"]) == 8
    for record in records:
        assert validated(record) == record
        assert record["record"] is None
        if record["provider_id"] == "reviewed-local":
            assert record["stance"] is None
        assert record["style_traits"] == []
        assert all(
            s["method"] in {"indexed_official_excerpt", "direct_review"} for s in record["sources"]
        )
    f = fighter()
    f["field_sources"].pop("height_cm")
    with pytest.raises(ValidationError, match="provenance"):
        validated(f)
    f = fighter()
    f["field_sources"]["height_cm"] = ["invented"]
    with pytest.raises(ValidationError, match="Unknown source"):
        validated(f)
    f = fighter()
    f["verified_at"] = (date.today() + timedelta(days=1)).isoformat()
    with pytest.raises(ValueError, match="future"):
        validated(f)


def test_zero_weights_and_invalid_values():
    with pytest.raises(ValidationError):
        MatchWeights(physical=0, background=0, style=0, stance=0, weight_class=0)
    with pytest.raises(ValidationError):
        MatchWeights(height_weight=0, reach_weight=0, ratio_weight=0)
    with pytest.raises(ValidationError):
        MatchWeights(physical=float("nan"))


def test_licensed_export_rejects_unlicensed_and_accepts_validated_file(tmp_path):
    import json

    path = tmp_path / "licensed.json"
    f = fighter()
    path.write_text(json.dumps([f]), encoding="utf-8")
    with pytest.raises(ValueError, match="license"):
        LicensedFileFighterProvider(str(path), "operator-contract-123").all()
    f["provider_id"] = "example-licensed-provider"
    for source in f["sources"]:
        source.update(
            method="licensed_provider", rights="licensed", license_reference="operator-contract-123"
        )
    path.write_text(json.dumps([f]), encoding="utf-8")
    assert (
        LicensedFileFighterProvider(str(path), "operator-contract-123").all()[0]["provider_id"]
        == "example-licensed-provider"
    )
    path.write_text(json.dumps([f, f]), encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate"):
        LicensedFileFighterProvider(str(path), "operator-contract-123").all()
