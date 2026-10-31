export interface Experience {
  technical_goals?: string;
  enjoyment?: number | null;
  discipline: string;
  level: string;
  months: number;
  sessions: number;
  instructor: boolean;
  competition: boolean;
  strengths: string;
  weaknesses: string;
  interested: boolean;
}
export interface Benchmark {
  name: string;
  value: number;
  unit: string;
  reps: number;
  effort: number;
  provenance: string;
}
export interface Profile {
  name: string;
  age: number;
  division: string;
  metabolic_sex: string;
  height_cm: number;
  weight_kg: number;
  wingspan_cm: number | null;
  standing_reach_cm: number | null;
  leg_cm: number | null;
  arm_cm: number | null;
  waist_cm: number | null;
  hip_cm: number | null;
  shoulder_cm: number | null;
  neck_cm: number | null;
  body_fat: number | null;
  resting_hr: number | null;
  country: string;
  dominant_hand: string;
  stance: string;
  units: string;
  goal: string;
  objectives: string[];
  horizon: string;
  preferred: string[];
  experience: Experience[];
  benchmarks: Benchmark[];
  gym_years: number;
  strength_coach?: boolean;
  power_practice?: boolean;
  available_days?: string[] | null;
  current_frequency: number;
  workout_minutes: number;
  days: number;
  minutes: number;
  sleep: number;
  activity: string;
  gym: boolean;
  equipment?: string[] | null;
  conditioning_mode?: string;
  mma_gym: boolean;
  boxing_equipment: boolean;
  partners: boolean;
  budget: string;
  diet: string[];
  allergies: string[];
  food_preferences: string;
  limitations: string;
  recovery: string;
  mobility: string;
  clinical_nutrition: boolean;
  competitive: boolean;
  intensity: string;
  priority: string;
  is_demo: boolean;
}
export interface Saved<T> {
  id: string;
  version: number;
  created_at: string;
  data: T;
}
export interface Exercise {
  catalog_id?: string;
  category?: string;
  rpe?: number;
  rep_range?: number[];
  block_minutes?: number;
  progression_rule?: string;
  technique_focus?: string;
  suggested_load_kg?: number;
  alternative_ids?: string[];
  name: string;
  sets: number;
  reps: string;
  rest: string;
  cue: string;
  substitution: string;
}
export interface TrainingSession {
  objective?: string;
  id: string;
  day: string;
  type: string;
  minutes: number;
  effort: number;
  warmup: string;
  cooldown: string;
  exercises: Exercise[];
  time_note: string;
}
export interface Week {
  week: number;
  phase: string;
  deload: boolean;
  focus: string;
  sessions: TrainingSession[];
}
export interface Plan {
  recovery_days?: string[];
  availability_note?: string;
  power_note?: string;
  lineage_id?: string;
  history_plan_ids?: string[];
  review_week?: number;
  continuation?: boolean;
  changes?: string[];
  scheduling_note?: string;
  available?: boolean;
  reason?: string;
  weeks: Week[];
  days: number;
  requested_days: number;
  method: string;
  limitations: string;
  inputs: Profile;
  version: number;
}
export interface Fighter {
  record?: {
    wins: number;
    losses: number;
    draws: number;
    no_contests: number;
    as_of: string;
    scope: string;
  } | null;
  id: string;
  name: string;
  height_cm: number | null;
  reach_cm: number | null;
  listed_weight_kg: number | null;
  division: string;
  stance: string | null;
  background: string[];
  styles: string[];
  status: string;
  source: string;
  source_date: string;
  verified_at: string;
  note: string;
  current_division?: string | null;
  career_status?: string;
  competition_division?: string;
  division_history?: { name: string; context: string; source_ids: string[] }[];
  statistics?: {
    name: string;
    value: number;
    unit: string;
    as_of: string;
    scope: string;
  }[];
  sources?: {
    license_reference?: string | null;
    license_url?: string | null;
    attribution?: string;
    id: string;
    url: string;
    publisher: string;
    observed_at: string;
    published_at?: string | null;
    method: string;
    rights: string;
  }[];
  field_sources?: Record<string, string[]>;
  issues?: string[];
}
export interface Match {
  fighter: Fighter;
  score: number | null;
  breakdown: Record<string, number>;
  effective_weights: Record<string, number>;
  excluded: string[];
  similarities: string;
  insight: string;
  coverage?: number;
  basis?: string;
  physical_components?: Record<string, number>;
  physical_effective_weights?: Record<string, number>;
  excluded_reasons?: Record<string, string>;
  differences?: string[];
  eligibility_notes?: string[];
  quality?: {
    evidence_support?: string;
    stale: boolean;
    observation_age_days: number;
    missing_physical: string[];
    issues: string[];
  };
  reference?: { verified_at: string; version: string };
}
export type Weights = Record<
  "physical" | "background" | "style" | "stance" | "weight_class",
  number
> & {
  height_weight?: number;
  reach_weight?: number;
  ratio_weight?: number;
  division_mode?: "current" | "history";
  include_retired?: boolean;
  include_stale?: boolean;
  same_division_only?: boolean;
  min_coverage?: number;
  style_preferences?: string[];
};
export interface Ranking {
  matches: Match[];
  weights: Weights;
  method: string;
  coverage?: {
    library_count: number;
    eligible_count: number;
    unavailable_records: { id: string; reason: string }[];
  };
}
export interface Assessment {
  physical: {
    bmi: number;
    ape_index_cm: number | null;
    reach_ratio: number | null;
    lean_mass_kg: number | null;
    waist_hip_ratio: number | null;
    strengths: string[];
    missing: string[];
    provenance: string;
    benchmarks: Benchmark[];
  };
  weight: {
    everyday_kg: number;
    everyday_lb: number;
    scale_reference: string;
    target: string;
    minor: boolean;
    guidance: string;
    source: string;
    verified_at: string;
    note: string;
    rows: {
      name: string;
      title_lb: number;
      non_title_lb: number;
      active: boolean;
    }[];
  };
  style: {
    direction: string;
    evidence: string;
    priorities: {
      discipline: string;
      priority: number;
      purpose: string;
      frequency: string;
      access: string;
    }[];
    opportunities: string[];
    limitation: string;
  };
}
export interface Meal {
  name: string;
  title?: string;
  recipe_id?: string;
  preparation?: string;
  preparation_steps?: string[];
  cooking_note?: string;
  source_calories?: number;
  ingredients: {
    id?: string;
    food: string;
    grams: number;
    source?: {
      url: string;
      fdc_id: number;
      description: string;
      license: string;
    };
  }[];
  protein: number;
  carbs: number;
  fat: number;
  calories: number;
}
export interface Nutrition {
  available: boolean;
  reason?: string;
  rmr?: number;
  activity_factor?: number;
  estimated_maintenance?: number;
  range?: number[];
  days: {
    day: number;
    meals: Meal[];
    totals: Record<string, number>;
    nutrients?: Record<string, number | null>;
    training_context?: {
      weekday: string;
      approved_minutes: number;
      note: string;
    };
  }[];
  grocery: { food: string; grams: number }[];
  method?: string;
  guidance: string;
  substitutions?: string;
  inputs?: Profile;
  target_calories?: number;
  macro_targets?: Record<string, number>;
  macro_guidance?: {
    protein_g: number[];
    carbs_g: number[];
    fat_g: number[];
    note: string;
  };
  goal_note?: string;
  warnings?: string[];
  changes?: string[];
  substitution_comparison?: {
    before: Meal;
    after: Meal;
    delta: Record<string, number>;
  };
  training_days?: string[];
  training_note?: string;
  budget_note?: string;
  effective_weight_kg?: number;
  weight_review?: { needs_review: boolean; reason: string };
}
export interface NutritionPreferences {
  cooking_skill?: string;
  cooking_minutes?: number;
  meals_per_day?: number | null;
  objective: string;
  culture: string;
  budget: string | null;
  dislikes: string[];
  unavailable: string[];
  add_diet: string[];
  add_allergies: string[];
  snacks: boolean;
  hunger: number | null;
  satisfaction: number | null;
  training_days: string[] | null;
}
export interface Ingredient {
  id: string;
  name: string;
  serving_g: number;
  role: string;
  allergens: string[];
  cost_tier: number;
  per_100g: {
    protein: number;
    carbs: number;
    fat: number;
    source_calories: number;
    fiber: number | null;
    sodium_mg?: number | null;
    calcium_mg?: number | null;
    iron_mg?: number | null;
    potassium_mg?: number | null;
  };
  source: {
    url: string;
    fdc_id: number;
    description: string;
    dataset: string;
    license: string;
    reviewed_at: string;
  };
}
export interface NutritionProposal {
  status: string;
  plan: Nutrition;
  saved_plan_id?: string;
  change: {
    kind: string;
    day: number;
    meal: string;
    protein_id?: string | null;
  };
}
export interface CoachProposal {
  status: string;
  target: "nutrition" | "training" | "assessment";
  saved_plan_id?: string;
  saved_version?: number;
  from_week?: number;
  before_week?: { week: number; sessions: TrainingSession[] };
  after_week?: { week: number; sessions: TrainingSession[] };
  assessment?: {
    observations: { name: string; value: number; unit: string; note: string }[];
    estimates: { name: string; value: number; unit: string; note: string }[];
    missing_domains: string[];
    note: string;
  };
  changes: string[];
  plan?: Plan;
  nutrition_plan?: Nutrition;
  before_session?: TrainingSession;
  after_session?: TrainingSession;
}
export interface CheckIn {
  soreness?: number | null;
  readiness?: number | null;
  body_fat?: number | null;
  mobility?: string;
  date: string;
  weight_kg: number;
  sleep: number;
  fatigue: number;
  notes: string;
  benchmarks: Benchmark[];
}
export interface ExercisePerformance {
  notes?: string;
  exercise_name: string;
  sets: {
    reps?: number;
    weight_kg?: number;
    duration_seconds?: number;
    distance_m?: number;
    rpe?: number;
  }[];
}
export interface Workout {
  practices?: { discipline: string; minutes: number }[];
  fatigue?: number | null;
  performances?: ExercisePerformance[];
  status?: "completed" | "missed" | "failed";
  completed_on?: string;
  session_id: string;
  plan_id: string;
  minutes: number;
  effort: number | null;
  notes: string;
}
export interface Proposal {
  base_plan_id: string;
  before_days: number;
  after_days: number;
  reason: string;
  plan: Plan;
  status: string;
}
export interface Conversation {
  context_summary?: {
    version: number;
    sections: string[];
    omitted: string[];
    note: string;
  };
  question: string;
  answer: string;
  mode: string;
  limitations: string;
  action_id?: string;
  action_summary?: string;
  action_error?: string;
}
export interface Reassessment {
  nutrition_review?: { needs_review: boolean; reason: string };
  review_week?: number;
  review?: TrainingReview;
  weight_change_kg: number;
  before_days: number;
  suggested_days: number;
  sessions_logged: number;
  benchmark_changes: {
    name: string;
    before: number;
    after: number;
    delta: number;
    unit: string;
    note: string;
  }[];
  reason: string;
  note: string;
}
export const defaultProfile: Profile = {
  name: "",
  age: 26,
  division: "Men",
  metabolic_sex: "unspecified",
  height_cm: 180,
  weight_kg: 78,
  wingspan_cm: null,
  standing_reach_cm: null,
  leg_cm: null,
  arm_cm: null,
  waist_cm: null,
  hip_cm: null,
  shoulder_cm: null,
  neck_cm: null,
  body_fat: null,
  resting_hr: null,
  country: "",
  dominant_hand: "Right",
  stance: "Unknown",
  units: "metric",
  goal: "Develop MMA skills",
  objectives: [],
  horizon: "12 weeks",
  preferred: ["Boxing", "BJJ"],
  experience: [],
  benchmarks: [],
  gym_years: 0,
  current_frequency: 0,
  workout_minutes: 45,
  days: 4,
  minutes: 60,
  sleep: 7.5,
  activity: "moderate",
  gym: true,
  mma_gym: true,
  boxing_equipment: false,
  partners: false,
  budget: "Moderate",
  diet: [],
  allergies: [],
  food_preferences: "",
  limitations: "",
  recovery: "",
  mobility: "Unknown",
  clinical_nutrition: false,
  competitive: false,
  intensity: "Balanced",
  priority: "Balanced",
  is_demo: false,
};

export type Runner = (task: () => Promise<void>) => Promise<void>;

export interface CatalogExercise {
  id: string;
  name: string;
  category: string;
  movement_pattern: string;
  muscles: string[];
  equipment: string[];
  difficulty: string;
  technique: string;
  sets_guidance: string;
  repetition_guidance: string;
  common_mistakes: string;
  modification_notes: string;
  alternatives: string[];
  requires_coach: boolean;
  evidence_note: string;
  source_ids: string[];
}
export interface TrainingReview {
  recovery: {
    status: string;
    flags: string[];
    fresh_checkin: boolean;
    note: string;
  };
  workload: {
    last_7_days_minutes: number;
    previous_7_days_minutes: number;
    session_rpe_load_au: number;
    sessions_missing_rpe: number;
    completed: number;
    missed: number;
    failed: number;
    logged_completion_percent: number | null;
    note: string;
  };
  decisions: {
    exercise: string;
    catalog_id?: string;
    action: string;
    reason: string;
    target: number | null;
  }[];
  note: string;
}
export interface TrainingIntelligence {
  assessment: {
    development?: {
      dimensions: {
        dimension: string;
        status: string;
        evidence: string[];
        limits: string;
      }[];
      technical: {
        discipline: string;
        stage: string;
        recorded: boolean;
        months: number | null;
        sessions: number | null;
        proficiency: string;
        technical_goals: string;
        focus: string;
        development_reason: string;
      }[];
      directions: { direction: string; reason: string; discipline: string }[];
      note: string;
    };
    observations: AthleticObservation[];
    estimates: AthleticObservation[];
    mobility: string;
    experience: string;
    recovery: string;
    missing_domains: string[];
    note: string;
  };
  review: TrainingReview;
  logs: (Workout & { record_id: string; recorded_at: string })[];
  plan_id: string | null;
}
export interface AthleticObservation {
  name: string;
  domain: string;
  value: number;
  unit: string;
  reps: number;
  effort: number;
  provenance: string;
  derived: string | null;
  note: string;
}
