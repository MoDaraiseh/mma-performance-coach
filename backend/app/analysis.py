from .divisions import current_reference
from .matching import FighterMatchingService as FighterMatchingService
from .schemas import Profile

LB_PER_KG = 1 / 0.45359237


def weight_classes(division="Men"):
    return current_reference(division)


class WeightClassService:
    @staticmethod
    def assess(p: Profile):
        table = weight_classes(p.division)
        pounds = p.weight_kg * LB_PER_KG
        active = [r for r in table["rows"] if r["active"]]
        match = next((r for r in active if pounds <= r["title_lb"] + 1e-7), None)
        return {
            **table,
            "everyday_kg": p.weight_kg,
            "everyday_lb": round(pounds, 2),
            "scale_reference": match["name"] if match else "Above active reference limits",
            "target": "Insufficient information for an individualized target weight. Maintain sustainable habits and evaluate performance, recovery and health with a qualified professional.",
            "minor": p.age < 18,
            "guidance": "No weight-cutting advice for under-18 athletes."
            if p.age < 18
            else "This reference does not recommend changing divisions. Competitive weight management needs qualified sports nutrition and medical input.",
        }


class PhysicalProfileService:
    @staticmethod
    def assess(p: Profile):
        strengths, missing = [], []
        if p.wingspan_cm is not None:
            if p.wingspan_cm > p.height_cm + 3:
                strengths.append(
                    "Reported wingspan exceeds height by more than 3 cm; explore distance management with a coach."
                )
        else:
            missing.append("Wingspan: reach comparisons use height alone.")
        if any(e.months >= 12 for e in p.experience):
            strengths.append(
                "At least one year of self-reported discipline experience provides a learning foundation."
            )
        if not p.benchmarks:
            missing.append(
                "No athletic benchmarks: strength and conditioning ability cannot be rated."
            )
        return {
            "bmi": round(p.weight_kg / (p.height_cm / 100) ** 2, 2),
            "ape_index_cm": round(p.wingspan_cm - p.height_cm, 2)
            if p.wingspan_cm is not None
            else None,
            "reach_ratio": round(p.wingspan_cm / p.height_cm, 3)
            if p.wingspan_cm is not None
            else None,
            "lean_mass_kg": round(p.weight_kg * (1 - p.body_fat / 100), 2)
            if p.body_fat is not None
            else None,
            "waist_hip_ratio": round(p.waist_cm / p.hip_cm, 3) if p.waist_cm and p.hip_cm else None,
            "strengths": strengths,
            "missing": missing,
            "provenance": "Calculated from user-reported measurements, not independently verified. BMI is a descriptive ratio, not a body-fat, health clearance or skill measurement; adult BMI categories must not be applied to minors. Lean mass inherits uncertainty from the entered body-fat estimate. Body proportions do not establish fighting talent. Independent professional review is pending.",
            "benchmarks": [b.model_dump() for b in p.benchmarks],
        }


class FightingStyleAnalysisService:
    @staticmethod
    def assess(p: Profile):
        experienced = sorted(
            [e for e in p.experience if e.months > 0], key=lambda e: e.months, reverse=True
        )
        lead = (
            experienced[0].discipline
            if experienced
            else (p.preferred[0] if p.preferred else "Integrated MMA")
        )
        directions = {
            "Boxing": "Striking fundamentals with balanced MMA transitions",
            "Muay Thai": "Striking and clinch development",
            "Kickboxing": "Striking-focused exploration",
            "Wrestling": "Wrestling-focused MMA exploration",
            "BJJ": "Positional grappling and submission awareness",
            "Judo": "Clinch and takedown exploration",
        }
        from .athletics import discipline_priorities

        priorities = discipline_priorities(p)
        return {
            "direction": directions.get(lead, "Balanced all-around MMA"),
            "evidence": f"Preference/access allocation for {p.goal}; existing classes count toward training load. Body shape is not used to infer ability.",
            "priorities": priorities,
            "opportunities": [
                "Striking-focused MMA",
                "Wrestling-focused MMA",
                "Grappling and submissions",
                "Counter-striking",
                "Pressure footwork",
                "Clinch development",
                "Balanced MMA",
            ],
            "limitation": "Exploratory direction; technical ability is unverified. Counter-striking, pressure and clinch choices require coached observation. No personality or professional potential inferred.",
        }


class AthleticAssessmentService:
    @staticmethod
    def compare(baseline, current):
        def key(b):
            return (b["name"], b["unit"], b["reps"], b.get("provenance"), b.get("effort"))

        original = {key(b): b for b in baseline}
        rows = []
        for b in current:
            before = original.get(key(b))
            if before and before["unit"] == b["unit"] and before["reps"] == b["reps"]:
                delta = round(b["value"] - before["value"], 2)
                rows.append(
                    {
                        "name": b["name"],
                        "before": before["value"],
                        "after": b["value"],
                        "delta": delta,
                        "unit": b["unit"],
                        "note": "Lower is better for timed runs; higher for repetitions, jumps and loads. Measurement protocol and effort must be consistent.",
                    }
                )
        return rows
