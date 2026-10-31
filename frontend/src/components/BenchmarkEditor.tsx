import { Plus, X } from "lucide-react";
import { Benchmark } from "../types";
export default function BenchmarkEditor({
  values,
  onChange,
}: {
  values: Benchmark[];
  onChange: (v: Benchmark[]) => void;
}) {
  const units: Record<string, string> = {
    Squat: "kg",
    "Bench press": "kg",
    Deadlift: "kg",
    "Overhead press": "kg",
    "Pull-ups": "reps",
    "Push-ups": "reps",
    Plank: "seconds",
    "Vertical jump": "cm",
    "Broad jump": "cm",
    "100m": "seconds",
    "1km": "seconds",
    "5km": "seconds",
  };
  return (
    <div className="benchmark-editor">
      <div className="settings-row">
        <h3>Optional athletic benchmarks</h3>
        <button
          type="button"
          className="secondary"
          disabled={values.length >= 20}
          onClick={() =>
            onChange([
              ...values,
              {
                name: "Squat",
                value: 40,
                unit: "kg",
                reps: 5,
                effort: 7,
                provenance: "self-reported",
              },
            ])
          }
        >
          <Plus size={14} /> Add result
        </button>
      </div>
      {values.map((b, i) => (
        <div className="benchmark-row" key={i}>
          <label>
            Test
            <select
              value={b.name}
              onChange={(e) =>
                onChange(
                  values.map((v, j) =>
                    j === i
                      ? {
                          ...v,
                          name: e.target.value,
                          unit: units[e.target.value],
                        }
                      : v,
                  ),
                )
              }
            >
              {Object.keys(units).map((k) => (
                <option key={k}>{k}</option>
              ))}
            </select>
          </label>
          <label>
            Result ({b.unit})
            <input
              type="number"
              min="0.1"
              max="100000"
              step="0.1"
              required
              value={b.value}
              onChange={(e) =>
                onChange(
                  values.map((v, j) =>
                    j === i ? { ...v, value: +e.target.value } : v,
                  ),
                )
              }
            />
          </label>
          <label>
            Reps
            <input
              type="number"
              min="1"
              max="100"
              required
              value={b.reps}
              onChange={(e) =>
                onChange(
                  values.map((v, j) =>
                    j === i ? { ...v, reps: +e.target.value } : v,
                  ),
                )
              }
            />
          </label>
          <label>
            Effort /10
            <input
              type="number"
              min="1"
              max="10"
              required
              value={b.effort}
              onChange={(e) =>
                onChange(
                  values.map((v, j) =>
                    j === i ? { ...v, effort: +e.target.value } : v,
                  ),
                )
              }
            />
          </label>
          <label>
            Evidence
            <select
              value={b.provenance}
              onChange={(e) =>
                onChange(
                  values.map((v, j) =>
                    j === i ? { ...v, provenance: e.target.value } : v,
                  ),
                )
              }
            >
              {["self-reported", "measured", "estimated"].map((v) => (
                <option key={v}>{v}</option>
              ))}
            </select>
          </label>
          <button
            type="button"
            aria-label={`Remove ${b.name} benchmark`}
            className="icon-button"
            onClick={() => onChange(values.filter((_, j) => j !== i))}
          >
            <X size={16} />
          </button>
        </div>
      ))}
    </div>
  );
}
