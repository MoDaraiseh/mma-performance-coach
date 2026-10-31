"""One validated division reference for assessment and fighter comparison."""

from copy import deepcopy

from pydantic import Field, model_validator
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from .schemas import StrictModel

SOURCE = "https://www.ufc.com/news/understanding-ufc-weight-classes-and-weigh-ins"
LIMITS = [
    ("Flyweight", 125),
    ("Bantamweight", 135),
    ("Featherweight", 145),
    ("Lightweight", 155),
    ("Welterweight", 170),
    ("Middleweight", 185),
    ("Light Heavyweight", 205),
    ("Heavyweight", 265),
]


class DivisionRow(StrictModel):
    name: str
    title_lb: float = Field(gt=0, le=300)
    non_title_lb: float = Field(gt=0, le=301)
    active: bool
    note: str | None = None


class DivisionReference(StrictModel):
    rows: list[DivisionRow] = Field(min_length=1)
    source: str
    verified_at: str
    note: str
    version: str = "legacy-reference"

    @model_validator(mode="after")
    def consistent(self):
        from datetime import date

        if date.fromisoformat(self.verified_at) > date.today():
            raise ValueError("Future reference observation")
        if not self.source.startswith("https://www.ufc.com/"):
            raise ValueError("Reference must identify the reviewed official source")
        if len({r.name for r in self.rows}) != len(self.rows):
            raise ValueError("Duplicate divisions")
        if any(r.non_title_lb != r.title_lb + 1 for r in self.rows):
            raise ValueError("This reference models the documented one-pound allowance")
        return self


def bundled_reference(division="Men"):
    limits = (
        LIMITS
        if division == "Men"
        else [("Strawweight", 115), ("Flyweight", 125), ("Bantamweight", 135)]
    )
    rows = [
        {"name": name, "title_lb": lb, "non_title_lb": lb + 1, "active": True}
        for name, lb in limits
    ]
    if division == "Women":
        rows.append(
            {
                "name": "Featherweight",
                "title_lb": 145,
                "non_title_lb": 146,
                "active": False,
                "note": "Historical UFC division; not an active reference division.",
            }
        )
    return {
        "rows": rows,
        "source": SOURCE,
        "verified_at": "2026-10-31",
        "version": "ufc-reference-2026-10-31",
        "note": "Title limit, typical non-title allowance and everyday body weight are different contexts. Regulator/event rules control eligibility. No target weight or cut is inferred.",
    }


def current_reference(division="Men"):
    from .db import ReferenceSnapshot, Session

    try:
        with Session() as db:
            row = db.scalar(select(ReferenceSnapshot).where(ReferenceSnapshot.id == division))
            if row:
                return DivisionReference.model_validate(row.payload).model_dump(exclude_none=True)
    except OperationalError as exc:
        # Pure service use before database initialization uses the same reviewed bundle.
        if "no such table" not in str(exc):
            raise
    return deepcopy(bundled_reference(division))
