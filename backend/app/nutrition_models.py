from typing import Literal

from pydantic import Field

from .schemas import StrictModel

DIETS = Literal["Halal", "Vegetarian", "Vegan", "Dairy-free", "Gluten-free"]


class NutritionPreferences(StrictModel):
    objective: Literal["Maintain", "Build gradually", "Sustainable reduction"] = "Maintain"
    culture: Literal[
        "Varied", "Middle Eastern inspired", "South Asian inspired", "Mediterranean inspired"
    ] = "Varied"
    budget: Literal["Low", "Moderate", "Flexible"] | None = None
    dislikes: list[str] = Field(default_factory=list, max_length=1000)
    unavailable: list[str] = Field(default_factory=list, max_length=1000)
    cooking_skill: Literal["Beginner", "Comfortable"] = "Beginner"
    cooking_minutes: int = Field(30, ge=10, le=120)
    meals_per_day: Literal[3, 4] | None = None
    add_diet: list[DIETS] = Field(default_factory=list, max_length=5)
    add_allergies: list[str] = Field(default_factory=list, max_length=20)
    snacks: bool = True
    hunger: int | None = Field(None, ge=1, le=5)
    satisfaction: int | None = Field(None, ge=1, le=5)
    training_days: (
        list[Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]]
        | None
    ) = Field(None, max_length=7)


class NutritionChange(StrictModel):
    kind: Literal["regenerate", "meal_swap"] = "regenerate"
    day: int = Field(1, ge=1, le=7)
    meal: Literal["Breakfast", "Lunch", "Dinner", "Recovery snack"] = "Lunch"
    protein_id: str | None = Field(None, max_length=60)
    food_id: str | None = Field(None, max_length=60)


class CoachIntent(StrictModel):
    kind: Literal[
        "explain",
        "shorten_session",
        "exercise_substitution",
        "schedule_boxing",
        "meal_swap",
        "reschedule_workout",
        "change_frequency",
        "request_assessment",
        "explain_matches",
        "progress_training",
    ]
    week: int = Field(1, ge=1, le=12)
    day: (
        Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] | None
    ) = None
    minutes: int | None = Field(None, ge=20, le=180)
    meal_day: int = Field(1, ge=1, le=7)
    meal: Literal["Breakfast", "Lunch", "Dinner", "Recovery snack"] = "Lunch"
    exercise_id: str | None = Field(None, max_length=80)
    alternative_id: str | None = Field(None, max_length=80)
    protein_id: str | None = Field(None, max_length=60)
    food_id: str | None = Field(None, max_length=60)
    target_day: (
        Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] | None
    ) = None
    days: int | None = Field(None, ge=1, le=6)


class AdaptiveCoachOutput(StrictModel):
    answer: str = Field(min_length=1, max_length=4000)
    limitations: str = Field(min_length=1, max_length=1000)
    intent: CoachIntent | None = None
