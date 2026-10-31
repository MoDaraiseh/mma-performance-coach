"""Deterministic resemblance heuristics; no skill or outcome prediction."""

import math
from datetime import date

from .divisions import current_reference
from .fighters import SeededFighterProvider

GROUPS = ("physical", "background", "style", "stance", "weight_class")
ALGORITHM = "resemblance-v4"
METHOD = "Heuristic resemblance, not probability or professional proficiency. Individual physical scores = 100 * exp(-0.5 * standardized difference squared); height/reach scale 15 cm, derived reach/height ratio scale 0.05. Physical subweights and available group weights are renormalized; a partially observed physical group contributes only its supported fraction of the requested weight. Ratio defaults to zero to avoid double counting reach. Explicit background names normalize whitespace/case and Brazilian jiu-jitsu/BJJ aliases without inferring skills. Background/style use Jaccard set overlap, stance exact agreement. Division = 100 * exp(-nearest reference-limit difference / 30 lb), using active reference divisions only; everyday scale reference is not eligibility or a target. Missing data never scores zero. Coverage is the fraction of requested weight backed by available dimensions, including physical subweights. Rankings use unrounded scores, ties by fighter ID. Display rounded to whole points; comparisons with different coverage require caution. Stale means observed over 365 days ago, not necessarily incorrect."


def overlap(a, b):
    return 100 * len(a & b) / len(a | b)


def background_terms(values):
    """Normalize explicit names only; do not infer disciplines from style or teams."""
    aliases = {
        "brazilian jiu-jitsu": "bjj",
        "brazilian jiu jitsu": "bjj",
        "brazilian jiujitsu": "bjj",
        "muay-thai": "muay thai",
    }
    return {
        aliases.get(" ".join(v.casefold().split()), " ".join(v.casefold().split()))
        for v in values
        if v.strip()
    }


def percentages(values):
    total = sum(values.values())
    if not total:
        return {k: 0 for k in values}
    exact = {k: v / total * 10000 for k, v in values.items()}
    units = {k: math.floor(v) for k, v in exact.items()}
    for key in sorted(values, key=lambda k: (-(exact[k] - units[k]), k))[
        : 10000 - sum(units.values())
    ]:
        units[key] += 1
    return {k: v / 100 for k, v in units.items()}


class FighterMatchingService:
    def __init__(self, provider=None):
        self.provider = provider or SeededFighterProvider()

    def evaluate(self, p, weights, f, reference=None):
        raw = {k: getattr(weights, k) for k in GROUPS}
        physical_raw = {
            "height": weights.height_weight,
            "reach": weights.reach_weight,
            "ratio": weights.ratio_weight,
        }
        physical = {}
        differences = []
        if f.get("height_cm") is not None:
            delta = p.height_cm - f["height_cm"]
            physical["height"] = 100 * math.exp(-0.5 * (delta / 15) ** 2)
            differences.append(f"Height: you minus fighter {delta:+.1f} cm.")
        if p.wingspan_cm is not None and f.get("reach_cm") is not None:
            delta = p.wingspan_cm - f["reach_cm"]
            physical["reach"] = 100 * math.exp(-0.5 * (delta / 15) ** 2)
            differences.append(
                f"Wingspan versus listed reach: {delta:+.1f} cm; measurement protocols may differ."
            )
            if f.get("height_cm"):
                delta = p.wingspan_cm / p.height_cm - f["reach_cm"] / f["height_cm"]
                physical["ratio"] = 100 * math.exp(-0.5 * (delta / 0.05) ** 2)
        components, reasons = {}, {}
        available_physical = sum(physical_raw[k] for k in physical)
        if available_physical:
            components["physical"] = (
                sum(physical_raw[k] * v for k, v in physical.items()) / available_physical
            )
        else:
            reasons["physical"] = "No requested physical measurements available on both sides."
        known = {e.discipline for e in p.experience if e.months > 0}
        if known and f.get("background"):
            components["background"] = overlap(
                background_terms(known), background_terms(f["background"])
            )
            differences.append(
                "Shared documented disciplines: "
                + (
                    ", ".join(
                        sorted(
                            k
                            for k in known
                            if background_terms([k]) & background_terms(f["background"])
                        )
                    )
                    or "none"
                )
                + "; practice duration and proficiency are not comparable."
            )
        else:
            reasons["background"] = (
                "Documented practice needed on both sides; unknown is not no experience."
            )
        if weights.style_preferences and f.get("style_traits"):
            components["style"] = overlap(set(weights.style_preferences), set(f["style_traits"]))
        else:
            reasons["style"] = (
                "No shared validated style descriptors; raw profile labels are descriptive only."
            )
        if p.stance != "Unknown" and f.get("stance"):
            components["stance"] = 100 if p.stance == f["stance"] else 0
        else:
            reasons["stance"] = "Verified stance needed on both sides."
        reference = reference or current_reference(p.division)
        active = {r["name"]: r["title_lb"] for r in reference["rows"] if r["active"]}
        own = next(
            (
                r
                for r in reference["rows"]
                if r["active"] and p.weight_kg / 0.45359237 <= r["title_lb"] + 1e-7
            ),
            None,
        )
        names = (
            [f.get("current_division")]
            if weights.division_mode == "current"
            else [d["name"] for d in f.get("division_history", [])]
        )
        divisions = [d for d in names if d in active]
        division_match = bool(own and own["name"] in divisions)
        if own and divisions and p.division == f["competition_division"]:
            components["weight_class"] = 100 * math.exp(
                -min(abs(own["title_lb"] - active[d]) for d in divisions) / 30
            )
            differences.append(
                f"Everyday scale reference: {own['name']}; fighter {weights.division_mode}: {', '.join(divisions)}. Not weight-cutting advice or eligibility."
            )
        else:
            reasons["weight_class"] = (
                "No compatible active division reference in the selected history/current context."
            )
        stale_days = (date.today() - date.fromisoformat(f["verified_at"])).days
        stale = stale_days > 365
        supported = {
            k: raw[k] * (available_physical / sum(physical_raw.values()) if k == "physical" else 1)
            for k in components
        }
        total = sum(supported.values())
        coverage_weight = sum(raw[k] for k in components if k != "physical")
        if "physical" in components:
            coverage_weight += raw["physical"] * available_physical / sum(physical_raw.values())
        coverage = round(100 * coverage_weight / sum(raw.values()), 1)
        exclusions = []
        if p.division != f["competition_division"]:
            exclusions.append(
                "Different men's/women's competition category; unscored manual reference only."
            )
        if not weights.include_retired and f.get("career_status") != "Active":
            exclusions.append("Not active at the source snapshot.")
        if stale and not weights.include_stale:
            exclusions.append("Stale observation excluded by filter.")
        if weights.same_division_only and not division_match:
            exclusions.append("Does not share the selected active division reference.")
        if coverage < weights.min_coverage:
            exclusions.append("Below requested data coverage.")
        if not total:
            exclusions.append("No weighted dimensions can be scored.")
        score = (
            sum(supported[k] * v for k, v in components.items()) / total
            if total and not exclusions
            else None
        )
        used = [k for k in components if raw[k] > 0]
        basis = (
            "physical"
            if used == ["physical"]
            else "physical and contextual"
            if "physical" in used
            else "contextual"
        )
        if "physical" in used and len(used) > 1 and supported["physical"] / total >= 0.6:
            basis = "predominantly physical"
        return {
            "fighter": f,
            "score": round(score) if score is not None else None,
            "_sort_score": score,
            "algorithm": ALGORITHM,
            "breakdown": {k: round(v) for k, v in components.items()},
            "effective_weights": percentages(supported),
            "score_contributions": {
                k: round(supported[k] * v / total, 1) if total else 0
                for k, v in components.items()
                if raw[k] > 0
            },
            "physical_components": {k: round(v) for k, v in physical.items()},
            "physical_effective_weights": percentages({k: physical_raw[k] for k in physical}),
            "coverage": coverage,
            "basis": basis,
            "excluded": [k for k in GROUPS if k not in components],
            "excluded_reasons": reasons,
            "eligibility_notes": exclusions,
            "differences": differences,
            "similarities": f"{basis.capitalize()} study comparison using {', '.join(used) or 'no supported dimensions'}. {coverage}% requested-weight coverage.",
            "insight": "Use comparison to discuss distance, movement and discipline study with a qualified coach. No comparable professional proficiency or competitive outcome is implied.",
            "quality": {
                "stale": stale,
                "observation_age_days": stale_days,
                "missing_physical": [k for k in physical_raw if k not in physical],
                "issues": f.get("issues", []),
                "evidence_support": "Limited evidence: compare coverage and source quality"
                if coverage < 60 or stale
                else "Supported requested dimensions; not statistical confidence",
            },
            "reference": reference,
        }

    def compare(self, p, weights, fighter_id):
        fighter = (
            self.provider.get(fighter_id)
            if hasattr(self.provider, "get")
            else next((f for f in self.provider.all() if f["id"] == fighter_id), None)
        )
        if fighter is None:
            return None
        result = self.evaluate(p, weights, fighter)
        result.pop("_sort_score")
        return result

    def rank(self, p, weights):
        fighters = self.provider.all()
        reference = current_reference(p.division)
        results = [self.evaluate(p, weights, f, reference) for f in fighters]
        eligible = sorted(
            [r for r in results if r["_sort_score"] is not None],
            key=lambda r: (-r["_sort_score"], r["fighter"]["id"]),
        )
        for r in eligible:
            r.pop("_sort_score")
        raw = {k: getattr(weights, k) for k in GROUPS}
        return {
            "matches": eligible[:3],
            "weights": percentages(raw),
            "method": METHOD,
            "algorithm": ALGORITHM,
            "coverage": {
                "library_count": len(fighters),
                "eligible_count": len(eligible),
                "unavailable_records": getattr(self.provider, "issues", []),
            },
        }
