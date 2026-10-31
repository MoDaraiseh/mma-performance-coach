"""Validated data providers. No network collection or assumed redistribution rights."""

import json
from datetime import date
from pathlib import Path
from typing import Protocol

from .fighter_catalog import reviewed_records
from .fighter_models import FighterRecord


class FighterDataProvider(Protocol):
    def all(self) -> list[dict]: ...


def validated(payload):
    record = FighterRecord.model_validate(payload)
    if record.verified_at > date.today():
        raise ValueError("Verification date is in the future")
    if any(s.published_at and s.published_at > s.observed_at for s in record.sources):
        raise ValueError("Publication cannot follow observation")
    if any(s.method == "legacy_unverified" for s in record.sources):
        raise ValueError("Unverified source cannot support scored comparisons")
    result = record.model_dump(mode="json")
    result["source"] = str(record.sources[0].url)
    result["source_date"] = record.sources[0].observed_at.isoformat()
    return result


class DatabaseFighterProvider:
    def get(self, fighter_id):
        from .db import FighterSnapshot, Session

        with Session() as db:
            row = db.get(FighterSnapshot, fighter_id)
            if row:
                try:
                    return validated(row.payload)
                except ValueError:
                    return None
        return None

    def search(
        self, q="", category=None, division=None, stance=None, status=None, page=1, page_size=20
    ):
        from sqlalchemy import func, select

        from .db import FighterSnapshot as F
        from .db import Session
        from .fighter_index import name_key

        filters = [F.valid_index.is_(True)]
        if q.strip():
            filters.append(F.search_name.contains(name_key(q), autoescape=True))
        if category:
            filters.append(F.competition_category == category)
        if division:
            filters.append(F.division_index.contains("|" + division + "|", autoescape=True))
        if stance:
            filters.append(F.stance_index == stance)
        if status:
            filters.append(F.career == status)
        with Session() as db:
            total = db.scalar(select(func.count()).select_from(F).where(*filters))
            rows = db.scalars(
                select(F)
                .where(*filters)
                .order_by(F.search_name, F.id)
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).all()
            return {
                "items": [validated(r.payload) for r in rows],
                "total": total,
                "page": page,
                "page_size": page_size,
            }

    def all(self):
        from sqlalchemy import select

        from .db import FighterSnapshot, Session

        self.issues = []
        result = []
        with Session() as db:
            for row in db.scalars(select(FighterSnapshot).order_by(FighterSnapshot.id)):
                try:
                    result.append(validated(row.payload))
                except ValueError:
                    self.issues.append(
                        {
                            "id": row.id,
                            "reason": "Invalid or legacy provenance; reviewed-local refresh required.",
                        }
                    )
        return result


class SeededFighterProvider:
    def all(self):
        supplement = json.loads(
            (Path(__file__).parent / "data" / "fighters_wikimedia.json").read_text(encoding="utf-8")
        )
        return [validated(r) for r in [*reviewed_records(), *supplement]]


class LicensedFileFighterProvider:
    """Operator-supplied export; requires source-level license references.
    No network access, user-supplied path, or bundled commercial license.
    """

    def __init__(self, path, license_reference):
        if not license_reference.strip():
            raise ValueError("Operator license reference required")
        self.path, self.license_reference = Path(path), license_reference

    def all(self):
        if self.path.stat().st_size > 25_000_000:
            raise ValueError("Export exceeds 25 MB")
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(payload, list) or len(payload) > 10000:
            raise ValueError("Expected at most 10000 records")
        records = [validated(r) for r in payload]
        if len({r["id"] for r in records}) != len(records):
            raise ValueError("Duplicate fighter IDs")
        for r in records:
            if r["provider_id"] == "reviewed-local" or any(
                s["rights"] != "licensed" or s["license_reference"] != self.license_reference
                for s in r["sources"]
            ):
                raise ValueError(
                    "Export needs a distinct provider ID and matching source license references"
                )
        return records
