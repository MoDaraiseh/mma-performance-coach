"""Contracts for source-backed comparison data, not athletic proficiency models."""

from datetime import date
from typing import Literal

from pydantic import AnyHttpUrl, Field, model_validator

from .schemas import StrictModel


class FighterSource(StrictModel):
    id: str = Field(min_length=1, max_length=80)
    url: AnyHttpUrl
    publisher: str = Field(min_length=1, max_length=120)
    observed_at: date
    published_at: date | None = None
    method: Literal[
        "indexed_official_excerpt", "direct_review", "licensed_provider", "legacy_unverified"
    ]
    rights: Literal["not_established", "licensed"] = "not_established"
    license_reference: str | None = None
    license_url: AnyHttpUrl | None = None
    attribution: str = Field("", max_length=300)


class FighterDivision(StrictModel):
    name: str = Field(min_length=1, max_length=80)
    context: str = Field(min_length=1, max_length=300)
    source_ids: list[str] = Field(min_length=1)


class FighterStatistic(StrictModel):
    name: str = Field(min_length=1, max_length=120)
    value: float = Field(ge=0)
    unit: str = Field(min_length=1, max_length=60)
    as_of: date
    scope: str = Field(min_length=1, max_length=200)
    source_ids: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def bounded_percentage(self):
        if self.unit.lower() in {"%", "percent", "percentage"} and self.value > 100:
            raise ValueError("Percentage must be between 0 and 100")
        return self


class OriginalMeasurement(StrictModel):
    value: float = Field(gt=0)
    unit: Literal["cm", "in", "m", "kg", "lb"]


class ProfessionalRecord(StrictModel):
    wins: int = Field(ge=0, le=1000)
    losses: int = Field(ge=0, le=1000)
    draws: int = Field(0, ge=0, le=100)
    no_contests: int = Field(0, ge=0, le=100)
    as_of: date
    scope: str = Field(min_length=1, max_length=200)


class FighterRecord(StrictModel):
    schema_version: Literal[2] = 2
    provider_id: str = Field(min_length=1, max_length=80)
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,59}$")
    name: str = Field(min_length=1, max_length=120)
    competition_division: Literal["Men", "Women"]
    height_cm: float | None = Field(None, ge=120, le=240)
    reach_cm: float | None = Field(None, ge=100, le=260)
    listed_weight_kg: float | None = Field(None, ge=30, le=180)
    current_division: str | None = None
    division_history: list[FighterDivision] = Field(default_factory=list)
    stance: Literal["Orthodox", "Southpaw", "Switch"] | None = None
    background: list[str] = Field(default_factory=list, max_length=15)
    styles: list[str] = Field(default_factory=list, max_length=10)
    style_traits: list[
        Literal[
            "Counter-striking",
            "Pressure",
            "Clinch",
            "Grappling",
            "Wrestling transitions",
            "Balanced",
        ]
    ] = Field(default_factory=list)
    career_status: Literal["Active", "Retired", "Not fighting", "Unknown"] = "Unknown"
    statistics: list[FighterStatistic] = Field(default_factory=list, max_length=30)
    verified_at: date
    sources: list[FighterSource] = Field(min_length=1, max_length=20)
    field_sources: dict[str, list[str]]
    issues: list[str] = Field(default_factory=list)
    original_measurements: dict[
        Literal["height", "reach", "listed_weight"], OriginalMeasurement
    ] = Field(default_factory=dict)
    note: str = Field(default="", max_length=2000)
    # Compatibility fields are display-only, never treated as authoritative matching inputs.
    division: str = "Unknown"
    division_limit_lb: float | None = None
    status: str = "Unknown"
    record: ProfessionalRecord | None = None
    external_ids: dict[str, str] = Field(default_factory=dict, max_length=10)
    source: str = ""
    source_date: str = ""

    @model_validator(mode="after")
    def provenance(self):
        ids = {s.id for s in self.sources}
        if len(ids) != len(self.sources):
            raise ValueError("Source IDs must be unique")
        fields = (
            "name",
            "competition_division",
            "height_cm",
            "reach_cm",
            "listed_weight_kg",
            "current_division",
            "stance",
            "background",
            "styles",
            "style_traits",
        )
        for key in fields:
            if getattr(self, key) not in (None, [], "") and not self.field_sources.get(key):
                raise ValueError(f"Missing field provenance: {key}")
        if self.career_status != "Unknown" and not self.field_sources.get("career_status"):
            raise ValueError("Career status needs provenance")
        if self.record and not self.field_sources.get("record"):
            raise ValueError("Professional record needs provenance")
        referenced = [r for refs in self.field_sources.values() for r in refs]
        referenced += [r for d in self.division_history for r in d.source_ids]
        referenced += [r for stat in self.statistics for r in stat.source_ids]
        if any(r not in ids for r in referenced):
            raise ValueError("Unknown source reference")
        if any(s.observed_at > self.verified_at for s in self.sources):
            raise ValueError("Record verification cannot precede its source observation")
        if any(stat.as_of > self.verified_at for stat in self.statistics):
            raise ValueError("Statistics cannot postdate verification")
        if self.record and self.record.as_of > self.verified_at:
            raise ValueError("Professional record cannot postdate verification")
        if any(s.rights == "licensed" and not s.license_reference for s in self.sources):
            raise ValueError("Licensed sources require a license reference")
        for key, field, kind in (
            ("height", "height_cm", "length"),
            ("reach", "reach_cm", "length"),
            ("listed_weight", "listed_weight_kg", "weight"),
        ):
            if key in self.original_measurements:
                measurement = self.original_measurements[key]
                converted = normalize_measurement(measurement.value, measurement.unit, kind)
                if getattr(self, field) is None or abs(converted - getattr(self, field)) > 0.001:
                    raise ValueError("Original and normalized measurement disagree")
        return self


def normalize_measurement(value, unit, kind):
    import math

    if kind not in ("length", "weight") or not math.isfinite(float(value)) or float(value) <= 0:
        raise ValueError("Expected a positive finite measurement and known dimension")
    factors = {"cm": 1, "in": 2.54, "m": 100} if kind != "weight" else {"kg": 1, "lb": 0.45359237}
    if unit not in factors:
        raise ValueError("Unsupported measurement unit")
    return round(float(value) * factors[unit], 4)
