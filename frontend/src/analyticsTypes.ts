export interface AnalyticsPoint {
  date: string;
  value: number;
  record_id: string;
  effort: number | null;
}
export interface AnalyticsSeries {
  id: string;
  label: string;
  unit: string;
  protocol: string;
  evidence: string;
  kind: string;
  observations: number;
  chart_truncated: boolean;
  points: AnalyticsPoint[];
  best: AnalyticsPoint;
  trend: {
    samples: number;
    span_days?: number;
    baseline?: AnalyticsPoint;
    current?: AnalyticsPoint;
    delta?: number;
    status: string;
    note: string;
  };
}
export interface AthleteAnalytics {
  period: { start: string; end: string };
  coverage: {
    total_events: number;
    loaded_events: number;
    truncated: boolean;
    event_limit: number;
    series_total: number;
    series_returned: number;
    chart_point_limit: number;
    invalid_benchmark_entries: number;
    source_plan_limit: number;
    source_plans_loaded: number;
  };
  series: AnalyticsSeries[];
  weekly: {
    week: string;
    minutes: number;
    completed: number;
    failed: number;
    missed: number;
    load_au: number;
    missing_rpe: number;
    partial_week: boolean;
  }[];
  adherence: {
    planned: number | null;
    completed: number | null;
    percent: number | null;
    all_program_slots?: number;
    start_date?: string;
    note: string;
  };
  martial_arts: {
    minutes: { discipline: string; minutes: number }[];
    workouts_with_practice: number;
    workouts_loaded: number;
    note: string;
  };
  achievements: {
    id: string;
    date: string;
    discipline: string;
    title: string;
    evidence: string;
  }[];
  observations: string[];
  milestones: string[];
  limitations: string[];
  priorities: string[];
  reassessments: {
    version: number;
    checkpoint: number;
    reason: string;
    benchmark_changes: {
      name: string;
      before: number;
      after: number;
      unit: string;
    }[];
  }[];
  profile_summary: {
    goal: string;
    height_cm: number;
    weight_kg: number;
    age: number;
  } | null;
  nutrition_summary: {
    version: number;
    note: string;
    usable: boolean;
    as_of: string;
    target_calories: number | null;
    macro_targets: Record<string, number> | null;
  } | null;
}
