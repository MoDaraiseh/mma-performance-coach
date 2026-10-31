from types import SimpleNamespace

import pytest
from sqlalchemy import select
from test_api import account
from test_api import client as client

from app.db import ExternalIdentity, FighterSnapshot, OperatorCounter, Session, User
from app.identity import validate_fresh_authentication
from app.operations import record_http
from app.release_policy import inspect_release, require_release


@pytest.mark.parametrize("value", [None, True, "1000", 900, 1100, float("nan")])
def test_fresh_authentication_rejects_missing_stale_future_or_invalid(value):
    with pytest.raises(ValueError):
        validate_fresh_authentication({"auth_time": value}, {"started_at": 1000}, now=1020)


def test_fresh_authentication_accepts_clock_skew():
    validate_fresh_authentication({"auth_time": 990}, {"started_at": 1000}, now=1020)


def policy(**kwargs):
    return SimpleNamespace(
        **{
            "oidc_issuer": "https://identity.example",
            "allow_legacy_recovery": False,
            "identity_cutover_acknowledged": True,
            "fighter_distribution_reviewed": True,
            **kwargs,
        }
    )


def test_release_policy_preserves_accounts_and_blocks_unlicensed_seed(client):
    account(client)
    with Session.begin() as db:
        before = db.scalar(select(User))
        original = before.token_hash
        result = inspect_release(db, policy())
        assert result["unlinked_accounts"] == 1
        assert result["fighter_records_blocking_distribution"] == 11
        with pytest.raises(RuntimeError):
            require_release(db, policy())
        assert before.token_hash == original
        assert db.scalar(select(FighterSnapshot)) is not None


def test_cutover_requires_configured_issuer_and_explicit_ack(client):
    account(client)
    with Session.begin() as db:
        uid = db.scalar(select(User.id))
        link = ExternalIdentity(
            id="synthetic-link", user_id=uid, issuer="https://other.example", subject="synthetic"
        )
        db.add(link)
        db.flush()
        assert inspect_release(db, policy())["unlinked_accounts"] == 1
        link.issuer = "https://identity.example"
        db.flush()
        assert inspect_release(db, policy())["unlinked_accounts"] == 0
        result = inspect_release(
            db, policy(identity_cutover_acknowledged=False, allow_legacy_recovery=True)
        )
        assert any("MFA" in b for b in result["blockers"])
        assert any("acknowledgement" in b for b in result["blockers"])


def test_http_monitoring_is_bounded_and_has_no_request_data(client):
    with Session() as db:
        before = (
            db.get(OperatorCounter, "http.total").count
            if db.get(OperatorCounter, "http.total")
            else 0
        )
    record_http(503, 600)
    record_http(200, 80)
    with Session() as db:
        assert db.get(OperatorCounter, "http.total").count == before + 2
        assert db.get(OperatorCounter, "http.latency_ms.le_1000").count >= 1
        assert db.get(OperatorCounter, "http.503").count == 1


def test_licensed_only_dataset_passes_policy_without_changing_records(client):
    from sqlalchemy import delete

    with Session.begin() as db:
        for row in db.scalars(select(FighterSnapshot)):
            if any(s["rights"] != "licensed" for s in row.payload["sources"]):
                db.execute(delete(FighterSnapshot).where(FighterSnapshot.id == row.id))
        result = inspect_release(db, policy())
        assert result["fighter_records"] == 8
        assert result["ready"]
        require_release(db, policy())
