from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Experience(StrictModel):
    discipline: str = Field(min_length=1, max_length=60)
    level: Literal["None", "Beginner", "Novice", "Intermediate", "Advanced", "Competitive"] = (
        "Beginner"
    )
    months: int = Field(0, ge=0, le=900)
    sessions: int = Field(0, ge=0, le=14)
    instructor: bool = False
    competition: bool = False
    strengths: str = Field("", max_length=500)
    weaknesses: str = Field("", max_length=500)
    interested: bool = True
    enjoyment: int | None = Field(None, ge=1, le=5)
    technical_goals: str = Field("", max_length=300)


class Benchmark(StrictModel):
    name: Literal[
        "Squat",
        "Bench press",
        "Deadlift",
        "Overhead press",
        "Pull-ups",
        "Push-ups",
        "Plank",
        "Vertical jump",
        "Broad jump",
        "100m",
        "1km",
        "5km",
    ]
    value: float = Field(gt=0, le=100000)
    unit: Literal["kg", "reps", "seconds", "cm"]
    reps: int = Field(1, ge=1, le=100)
    effort: int = Field(7, ge=1, le=10)
    provenance: Literal["self-reported", "measured", "estimated"] = "self-reported"

    @model_validator(mode="after")
    def check_unit(self):
        expected = {
            "Squat": "kg",
            "Bench press": "kg",
            "Deadlift": "kg",
            "Overhead press": "kg",
            "Pull-ups": "reps",
            "Push-ups": "reps",
            "Plank": "seconds",
            "Vertical jump": "cm",
            "Broad jump": "cm",
            "100m": "seconds",
            "1km": "seconds",
            "5km": "seconds",
        }
        if self.unit != expected[self.name]:
            raise ValueError(f"{self.name} requires {expected[self.name]}")
        return self


class Profile(StrictModel):
    name: str = Field("Athlete", min_length=1, max_length=80)
    age: int = Field(26, ge=13, le=90)
    division: Literal["Men", "Women"] = "Men"
    metabolic_sex: Literal["male", "female", "unspecified"] = "unspecified"
    height_cm: float = Field(180, ge=120, le=240)
    weight_kg: float = Field(78, ge=30, le=250)
    wingspan_cm: float | None = Field(None, ge=100, le=260)
    standing_reach_cm: float | None = Field(None, ge=100, le=330)
    leg_cm: float | None = Field(None, ge=30, le=150)
    arm_cm: float | None = Field(None, ge=20, le=120)
    waist_cm: float | None = Field(None, ge=40, le=220)
    hip_cm: float | None = Field(None, ge=40, le=220)
    shoulder_cm: float | None = Field(None, ge=20, le=100)
    neck_cm: float | None = Field(None, ge=20, le=70)
    body_fat: float | None = Field(None, ge=5, le=60)
    resting_hr: int | None = Field(None, ge=30, le=150)
    country: str = Field("", max_length=80)
    dominant_hand: Literal["Right", "Left", "Ambidextrous"] = "Right"
    stance: Literal["Orthodox", "Southpaw", "Switch", "Unknown"] = "Unknown"
    units: Literal["metric", "imperial"] = "metric"
    goal: str = Field("Develop MMA skills", min_length=1, max_length=120)
    objectives: list[str] = Field(default_factory=list, max_length=13)
    horizon: str = Field("12 weeks", max_length=100)
    preferred: list[str] = Field(default_factory=lambda: ["Boxing", "BJJ"], max_length=10)
    experience: list[Experience] = Field(default_factory=list, max_length=10)
    benchmarks: list[Benchmark] = Field(default_factory=list, max_length=20)
    gym_years: float = Field(0, ge=0, le=70)
    strength_coach: bool = False
    power_practice: bool = False
    current_frequency: int = Field(0, ge=0, le=14)
    workout_minutes: int = Field(45, ge=15, le=180)
    days: int = Field(4, ge=1, le=6)
    available_days: (
        list[Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]]
        | None
    ) = Field(None, min_length=1, max_length=7)
    minutes: int = Field(60, ge=20, le=180)
    sleep: float = Field(7.5, ge=2, le=12)
    activity: Literal["low", "moderate", "high"] = "moderate"
    gym: bool = True
    equipment: (
        list[
            Literal["dumbbells", "bench", "bands", "bike", "rower", "rope", "medicine_ball", "mats"]
        ]
        | None
    ) = Field(None, max_length=8)
    mma_gym: bool = True
    boxing_equipment: bool = False
    partners: bool = False
    budget: Literal["Low", "Moderate", "Flexible"] = "Moderate"
    diet: list[Literal["Halal", "Vegetarian", "Vegan", "Dairy-free", "Gluten-free"]] = Field(
        default_factory=list
    )
    allergies: list[str] = Field(default_factory=list, max_length=20)
    food_preferences: str = Field("", max_length=500)
    limitations: str = Field("", max_length=1000)
    recovery: str = Field("", max_length=500)
    mobility: Literal["Unknown", "Limited", "Comfortable"] = "Unknown"
    clinical_nutrition: bool = False
    competitive: bool = False
    intensity: Literal["Gentle", "Balanced", "Challenging"] = "Balanced"
    priority: Literal["Balanced", "Strength", "Conditioning"] = "Balanced"
    conditioning_mode: Literal[
        "auto", "walking", "cycling", "rowing", "run_walk", "jump_rope", "interval_cycling"
    ] = "auto"
    is_demo: bool = False


class MatchWeights(StrictModel):
    physical: float = Field(60, ge=0, le=100)
    background: float = Field(15, ge=0, le=100)
    style: float = Field(10, ge=0, le=100)
    stance: float = Field(5, ge=0, le=100)
    weight_class: float = Field(10, ge=0, le=100)
    height_weight: float = Field(50, ge=0, le=100)
    reach_weight: float = Field(50, ge=0, le=100)
    ratio_weight: float = Field(0, ge=0, le=100)
    division_mode: Literal["history", "current"] = "history"
    include_retired: bool = True
    include_stale: bool = True
    same_division_only: bool = False
    min_coverage: float = Field(0, ge=0, le=100)
    style_preferences: list[
        Literal[
            "Counter-striking",
            "Pressure",
            "Clinch",
            "Grappling",
            "Wrestling transitions",
            "Balanced",
        ]
    ] = Field(default_factory=list, max_length=6)

    @model_validator(mode="after")
    def nonzero(self):
        if self.physical + self.background + self.style + self.stance + self.weight_class == 0:
            raise ValueError("At least one matching weight must be positive")
        if self.physical > 0 and self.height_weight + self.reach_weight + self.ratio_weight == 0:
            raise ValueError("At least one physical subweight must be positive")
        return self


class CheckIn(StrictModel):
    date: date
    weight_kg: float = Field(ge=30, le=250)
    sleep: float = Field(ge=2, le=12)
    fatigue: int = Field(ge=1, le=10)
    notes: str = Field("", max_length=1000)
    benchmarks: list[Benchmark] = Field(default_factory=list, max_length=20)
    body_fat: float | None = Field(None, ge=5, le=60)
    mobility: Literal["Unknown", "Limited", "Comfortable"] = "Unknown"
    soreness: int | None = Field(None, ge=0, le=10)
    readiness: int | None = Field(None, ge=1, le=5)


class ExerciseSet(StrictModel):
    reps: int | None = Field(None, ge=1, le=100)
    weight_kg: float | None = Field(None, ge=0, le=1000)
    duration_seconds: float | None = Field(None, gt=0, le=10800)
    distance_m: float | None = Field(None, gt=0, le=100000)
    rpe: float | None = Field(None, ge=1, le=10)

    @model_validator(mode="after")
    def has_performance(self):
        if self.reps is None and self.duration_seconds is None and self.distance_m is None:
            raise ValueError("Record repetitions, duration or distance for each set")
        return self


class ExercisePerformance(StrictModel):
    exercise_name: str = Field(min_length=1, max_length=200)
    sets: list[ExerciseSet] = Field(min_length=1, max_length=10)
    notes: str = Field("", max_length=500)


class DisciplinePractice(StrictModel):
    discipline: Literal[
        "Boxing", "Muay Thai", "Kickboxing", "BJJ", "Wrestling", "Judo", "Integrated MMA"
    ]
    minutes: int = Field(ge=1, le=180)


class TechnicalAchievement(StrictModel):
    date: date
    discipline: Literal[
        "Boxing", "Muay Thai", "Kickboxing", "BJJ", "Wrestling", "Judo", "Integrated MMA"
    ]
    title: str = Field(min_length=1, max_length=150)
    notes: str = Field("", max_length=500)


class AnalyticsSchedule(StrictModel):
    plan_id: str = Field(max_length=36)
    start_date: date


class WorkoutLog(StrictModel):
    practices: list[DisciplinePractice] = Field(default_factory=list, max_length=7)
    fatigue: int | None = Field(None, ge=1, le=10)
    plan_id: str | None = None
    completed_on: date | None = None
    session_id: str = Field(min_length=1, max_length=50)
    minutes: int = Field(ge=0, le=180)
    effort: int | None = Field(None, ge=1, le=10)
    notes: str = Field("", max_length=1000)
    status: Literal["completed", "missed", "failed"] = "completed"
    performances: list[ExercisePerformance] = Field(default_factory=list, max_length=12)

    @model_validator(mode="after")
    def status_consistency(self):
        if sum(p.minutes for p in self.practices) > self.minutes or len(
            {p.discipline for p in self.practices}
        ) != len(self.practices):
            raise ValueError(
                "Discipline minutes must fit actual session time, with each discipline entered once"
            )
        if self.status in {"completed", "failed"} and self.minutes == 0:
            raise ValueError("Performed sessions require positive minutes")
        if self.status == "missed" and (self.minutes or self.performances):
            raise ValueError("Missed sessions have zero training minutes and no performance sets")
        if len({p.exercise_name for p in self.performances}) != len(self.performances):
            raise ValueError("Record each exercise once, with all its sets")
        return self


class CoachRequest(StrictModel):
    message: str = Field(min_length=1, max_length=2000)
    use_ai: bool = False


class CoachOutput(StrictModel):
    answer: str = Field(min_length=1, max_length=4000)
    limitations: str = Field(min_length=1, max_length=1000)


class RevisionRequest(StrictModel):
    days: int = Field(ge=1, le=6)
    reason: str = Field(min_length=1, max_length=1000)


class ReassessmentRequest(StrictModel):
    week: Literal[4, 8, 12] = 4


class SubstitutionRequest(StrictModel):
    session_id: str = Field(min_length=1, max_length=50)
    exercise_name: str = Field(min_length=1, max_length=200)
    alternative_id: str = Field(min_length=1, max_length=100)
