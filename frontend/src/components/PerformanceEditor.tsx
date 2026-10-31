import type { ExercisePerformance } from "../types";

export default function PerformanceEditor({
  names,
  values,
  onChange,
}: {
  names: string[];
  values: ExercisePerformance[];
  onChange: (values: ExercisePerformance[]) => void;
}) {
  return (
    <fieldset>
      <legend>Actual exercise performance · optional</legend>
      <p className="muted">
        Record only sets you performed. Enter repetitions, timed seconds or
        distance for each set; load and RPE are optional. Missing effort
        prevents progression.
      </p>
      {names.map((name) => {
        const entry = values.find((v) => v.exercise_name === name);
        return (
          <div key={name} className="exercise">
            <h4>{name}</h4>
            {entry?.sets.map((set, index) => (
              <div className="form-grid" key={index}>
                {(
                  [
                    "reps",
                    "weight_kg",
                    "duration_seconds",
                    "distance_m",
                    "rpe",
                  ] as const
                ).map((key) => (
                  <label key={key}>
                    {key === "reps"
                      ? "Repetitions"
                      : key === "weight_kg"
                        ? "Load (kg)"
                        : key === "duration_seconds"
                          ? "Duration (seconds)"
                          : key === "distance_m"
                            ? "Distance (m)"
                            : "Set RPE (1–10)"}{" "}
                    · set {index + 1} · {name}
                    <input
                      type="number"
                      min={key === "weight_kg" ? 0 : 1}
                      max={
                        key === "reps"
                          ? 100
                          : key === "weight_kg"
                            ? 1000
                            : key === "rpe"
                              ? 10
                              : key === "distance_m"
                                ? 100000
                                : 10800
                      }
                      step={key === "reps" ? 1 : "any"}
                      required={
                        key === "reps"
                          ? !set.duration_seconds && !set.distance_m
                          : false
                      }
                      value={set[key] ?? ""}
                      onChange={(e) =>
                        onChange(
                          values.map((v) =>
                            v.exercise_name !== name
                              ? v
                              : {
                                  ...v,
                                  sets: v.sets.map((s, i) =>
                                    i !== index
                                      ? s
                                      : {
                                          ...s,
                                          [key]: e.target.value
                                            ? +e.target.value
                                            : undefined,
                                        },
                                  ),
                                },
                          ),
                        )
                      }
                    />
                  </label>
                ))}
                <button
                  type="button"
                  className="text-button"
                  onClick={() =>
                    onChange(
                      values
                        .map((v) =>
                          v.exercise_name !== name
                            ? v
                            : {
                                ...v,
                                sets: v.sets.filter((_, i) => i !== index),
                              },
                        )
                        .filter((v) => v.sets.length),
                    )
                  }
                >
                  Remove set {index + 1} · {name}
                </button>
              </div>
            ))}
            {entry && (
              <label>
                Exercise notes · {name}
                <textarea
                  maxLength={500}
                  value={entry.notes ?? ""}
                  onChange={(e) =>
                    onChange(
                      values.map((v) =>
                        v.exercise_name === name
                          ? { ...v, notes: e.target.value }
                          : v,
                      ),
                    )
                  }
                />
              </label>
            )}
            <button
              type="button"
              className="secondary"
              disabled={(entry?.sets.length ?? 0) >= 10}
              onClick={() =>
                onChange(
                  entry
                    ? values.map((v) =>
                        v.exercise_name !== name
                          ? v
                          : { ...v, sets: [...v.sets, {}] },
                      )
                    : [...values, { exercise_name: name, sets: [{}] }],
                )
              }
            >
              Add actual set · {name}
            </button>
          </div>
        );
      })}
    </fieldset>
  );
}
