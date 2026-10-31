from copy import deepcopy

import pytest
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from test_api import account
from test_api import client as api_client

from app.db import FighterSnapshot, Session, engine
from app.fighter_governance import import_records, quality, rollback
from app.fighters import DatabaseFighterProvider, SeededFighterProvider, validated
from app.matching import FighterMatchingService, percentages
from app.schemas import MatchWeights, Profile

client = api_client


@pytest.fixture(scope="session", autouse=True)
def close_focused_database():
    yield
    engine.dispose()


def sample():
    f = deepcopy(next(f for f in SeededFighterProvider().all() if f["id"] == "usman"))
    f.update(
        id="synthetic-qa",
        name="Synthetic QA Fighter",
        provider_id="qa-only",
        external_ids={},
        issues=["Synthetic test fixture, not an athlete record"],
    )
    return f


def test_actual_coverage_licenses_and_no_current_status_inference():
    rows = SeededFighterProvider().all()
    report = quality(rows)
    assert report["validated_count"] == 19 and report["categories"] == {"Men": 11, "Women": 8}
    assert len([r for r in report["history_divisions"] if r["category"] == "Men"]) == 8
    assert {r["division"] for r in report["history_divisions"] if r["category"] == "Women"} >= {
        "Strawweight",
        "Flyweight",
        "Bantamweight",
    }
    new = [r for r in rows if r["provider_id"] == "wikimedia-reviewed"]
    assert len(new) == 8
    assert all(r["current_division"] is None and r["career_status"] == "Unknown" for r in new)
    assert all(
        s["license_reference"] == "CC-BY-SA-4.0" and s["attribution"]
        for r in new
        for s in r["sources"]
    )


def test_partial_physical_support_does_not_keep_full_group_influence():
    f = sample()
    f["reach_cm"] = None
    p = Profile(height_cm=f["height_cm"], wingspan_cm=200, stance="Southpaw")
    r = FighterMatchingService().evaluate(
        p, MatchWeights(physical=60, stance=40, background=0, style=0, weight_class=0), f
    )
    assert r["score"] == 43  # physical 30/(30+40), rather than 60/(60+40)
    assert r["coverage"] == 70
    assert sum(r["effective_weights"].values()) == 100


@pytest.mark.parametrize(
    "values",
    [{"a": 1, "b": 1, "c": 1}, {"a": 0, "b": 0.001, "c": 100}, {"a": 17, "b": 31, "c": 63}],
)
def test_normalized_weights_exactly_sum_to_100(values):
    assert sum(percentages(values).values()) == pytest.approx(100)


def test_professional_record_provenance_and_future_dates():
    f = sample()
    f["record"] = {
        "wins": 10,
        "losses": 2,
        "draws": 0,
        "no_contests": 1,
        "as_of": "2026-10-30",
        "scope": "Synthetic test record",
    }
    with pytest.raises(ValueError, match="provenance"):
        validated(f)
    f["field_sources"]["record"] = ["wikipedia-review"]
    assert validated(f)["record"]["wins"] == 10
    f["record"]["as_of"] = "2099-01-01"
    with pytest.raises(ValueError):
        validated(f)


def test_import_preview_apply_reject_conflict_and_safe_rollback(client):
    account(client)
    client.post("/api/demo")
    before = client.get("/api/export").json()
    f = sample()
    report = import_records([f])
    assert report["changes"]
    assert DatabaseFighterProvider().get(f["id"]) is None
    applied = import_records([f], report["preview_token"])
    assert DatabaseFighterProvider().get(f["id"])["name"] == f["name"]
    correction = deepcopy(f)
    correction["issues"].append("Explicit reviewed correction")
    conflict = import_records([correction])
    with pytest.raises(ValueError, match="Conflicts"):
        import_records([correction], conflict["preview_token"])
    corrected = import_records([correction], conflict["preview_token"], True)
    with pytest.raises(ValueError, match="Later changes"):
        rollback(applied["batch_id"], True)
    rollback(corrected["batch_id"], True)
    assert rollback(applied["batch_id"])["status"] == "rollback_preview"
    rollback(applied["batch_id"], True)
    assert DatabaseFighterProvider().get(f["id"]) is None
    assert client.get("/api/export").json() == before


@pytest.mark.parametrize(
    "kind", ["same-id", "same-name", "unknown-rights", "provider-takeover", "older"]
)
def test_duplicate_and_unauthorized_imports_are_atomic(client, kind):
    f = sample()
    report = import_records([f])
    import_records([f], report["preview_token"])
    bad = deepcopy(f)
    if kind == "same-id":
        payload = [f, f]
    elif kind == "same-name":
        bad["id"] = "other-id"
        payload = [bad]
    elif kind == "unknown-rights":
        bad["sources"][0]["rights"] = "not_established"
        payload = [bad]
    elif kind == "provider-takeover":
        bad["provider_id"] = "other-provider"
        payload = [bad]
    else:
        bad["verified_at"] = "2026-10-30"
        bad["sources"][0]["observed_at"] = "2026-10-30"
        payload = [bad]
    with pytest.raises(ValueError):
        import_records(payload)
    assert DatabaseFighterProvider().get(f["id"]) == validated(f)


def test_changed_preview_token_and_rollback_repeat_rejected(client):
    f = sample()
    report = import_records([f])
    f["issues"].append("Changed after review")
    with pytest.raises(ValueError, match="Preview changed"):
        import_records([f], report["preview_token"])
    report = import_records([f])
    batch = import_records([f], report["preview_token"])
    rollback(batch["batch_id"], True)
    with pytest.raises(ValueError):
        rollback(batch["batch_id"], True)


def test_search_pagination_filters_literal_query_and_query_count(client):
    account(client)
    result = client.get("/api/fighters/search?page_size=5").json()
    second = client.get("/api/fighters/search?page_size=5&page=2").json()
    assert result["total"] == 19 and len(result["items"]) == 5
    assert not ({f["id"] for f in result["items"]} & {f["id"] for f in second["items"]})
    filtered = client.get(
        "/api/fighters/search?category=Women&division=Bantamweight&stance=Orthodox"
    ).json()
    assert "rousey" in {f["id"] for f in filtered["items"]}
    assert client.get("/api/fighters/search?q=%25").json()["total"] == 0
    assert (
        client.get("/api/fighters/search?q=Jedrzejczyk").json()["items"][0]["id"] == "jedrzejczyk"
    )
    assert client.get("/api/fighters/search?page_size=1000").status_code == 422
    statements = []

    def capture(*args):
        statements.append(args[2])

    event.listen(engine, "before_cursor_execute", capture)
    try:
        FighterMatchingService(DatabaseFighterProvider()).rank(Profile(), MatchWeights())
    finally:
        event.remove(engine, "before_cursor_execute", capture)
    assert (
        len(statements) <= 3
    )  # fighter scan + one shared division reference, not one query per fighter


def test_database_identity_guard_and_metadata_updates(client):
    f = sample()
    first = validated(f)
    with Session.begin() as db:
        db.add(FighterSnapshot(id=first["id"], payload=first, verified_at=first["verified_at"]))
    f["id"] = "duplicate-other"
    with pytest.raises(IntegrityError), Session.begin() as db:
        db.add(FighterSnapshot(id=f["id"], payload=validated(f), verified_at=f["verified_at"]))
    with Session.begin() as db:
        row = db.get(FighterSnapshot, first["id"])
        changed = deepcopy(row.payload)
        changed["name"] = "Renamed QA"
        row.payload = changed
    assert DatabaseFighterProvider().search("Renamed")["total"] == 1


def test_thousand_synthetic_records_paginate_without_loading_all_payloads(client):
    f = sample()
    with Session.begin() as db:
        for n in range(1000):
            item = deepcopy(f)
            item.update(id=f"qa-{n:04}", name=f"Synthetic {n:04}")
            db.add(
                FighterSnapshot(
                    id=item["id"], payload=validated(item), verified_at=item["verified_at"]
                )
            )
    rows = DatabaseFighterProvider().search("Synthetic", page=20, page_size=25)
    assert rows["total"] == 1000 and len(rows["items"]) == 25
    assert rows["items"][0]["id"] == "qa-0475"


def test_external_identifier_duplicate_is_rejected_even_when_names_differ(client):
    a = sample()
    a["external_ids"] = {"qa-namespace": "same"}
    b = deepcopy(a)
    b.update(id="second-qa", name="Different Alias")
    with pytest.raises(ValueError, match="external identifier"):
        import_records([a, b])


def test_out_of_range_percentage_is_not_accepted_as_a_statistic():
    f = sample()
    f["statistics"] = [
        dict(
            name="Takedown accuracy",
            value=101,
            unit="%",
            as_of="2026-10-30",
            scope="Synthetic validation test",
            source_ids=["wikipedia-review"],
        )
    ]
    with pytest.raises(ValueError, match="Percentage"):
        validated(f)
