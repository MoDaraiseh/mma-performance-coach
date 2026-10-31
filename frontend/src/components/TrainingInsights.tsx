import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../api";
import type { CatalogExercise, TrainingIntelligence } from "../types";
import { Card, Empty, Note, Tag } from "./ui";

export default function TrainingInsights({
  refreshKey,
  catalog = false,
}: {
  refreshKey: string;
  catalog?: boolean;
}) {
  const [data, setData] = useState<TrainingIntelligence | null>(null);
  const [exercises, setExercises] = useState<CatalogExercise[]>([]);
  const [sources, setSources] = useState<Record<string, string>>({});
  const [error, setError] = useState("");
  const [category, setCategory] = useState("All");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState("");
  const [metric, setMetric] = useState<
    "weight_kg" | "reps" | "duration_seconds" | "distance_m" | "rpe"
  >("weight_kg");
  useEffect(() => {
    let active = true;
    setError("");
    api<TrainingIntelligence>("/training-intelligence")
      .then((value) => {
        if (active) setData(value);
      })
      .catch((e) => {
        if (active) setError((e as Error).message);
      });
    if (catalog)
      api<{ exercises: CatalogExercise[]; sources: Record<string, string> }>(
        "/exercise-catalog",
      )
        .then((value) => {
          if (active) {
            setExercises(value.exercises);
            setSources(value.sources);
          }
        })
        .catch((e) => {
          if (active) setError((e as Error).message);
        });
    return () => {
      active = false;
    };
  }, [refreshKey, catalog]);
  const names = [
    ...new Set(
      data?.logs.flatMap((log) =>
        (log.performances ?? []).map((ex) => ex.exercise_name),
      ) ?? [],
    ),
  ].sort();
  const name = names.includes(selected) ? selected : (names[0] ?? "");
  const rows = (data?.logs ?? [])
    .flatMap((log) =>
      (log.performances ?? [])
        .filter((ex) => ex.exercise_name === name)
        .flatMap((ex) =>
          ex.sets.map((set, index) => ({
            ...set,
            date: log.completed_on ?? log.recorded_at.slice(0, 10),
            key: `${log.record_id}-${index}`,
            session: log.session_id,
            status: log.status ?? "completed",
            set: index + 1,
            notes: ex.notes || log.notes,
            sessionRpe: log.effort,
          })),
        ),
    )
    .sort((a, b) => a.date.localeCompare(b.date));
  const trend = rows.map((row) => ({
    label: `${row.date} / ${row.session} / set ${row.set}`,
    value: row[metric] ?? null,
  }));
  return (
    <div className="no-print">
      {error && (
        <p role="alert">Training intelligence could not load: {error}</p>
      )}
      {!data ? (
        !error && <p role="status">Loading training intelligence...</p>
      ) : (
        <>
          {data.assessment.development && (
            <Card
              title="Athlete development model"
              eyebrow="SEPARATE DIMENSIONS, NO COMPOSITE SCORE"
            >
              <Note>{data.assessment.development.note}</Note>
              <div className="development-grid">
                {data.assessment.development.dimensions.map((axis) => (
                  <section key={axis.dimension}>
                    <h3>{axis.dimension}</h3>
                    <Tag>{axis.status}</Tag>
                    <p>
                      {axis.evidence.join("; ") ||
                        "No comparable evidence entered."}
                    </p>
                    <p className="muted">{axis.limits}</p>
                  </section>
                ))}
              </div>
              <h3>Independent technical development</h3>
              {data.assessment.development.technical.map((row) => (
                <details key={row.discipline}>
                  <summary>
                    {row.discipline}: {row.stage}
                  </summary>
                  <p>
                    {row.recorded
                      ? `${row.months} months; ${row.sessions} sessions/week; self-reported ${row.proficiency}.`
                      : "Experience, frequency and proficiency not entered."}
                  </p>
                  <p>
                    {row.focus}. {row.development_reason}
                  </p>
                </details>
              ))}
              <h3>Useful technical directions</h3>
              {data.assessment.development.directions.map((row) => (
                <p key={row.discipline}>
                  <strong>
                    {row.discipline}: {row.direction}.
                  </strong>{" "}
                  {row.reason}
                </p>
              ))}
            </Card>
          )}
          <Card title="Athletic performance evidence">
            <Note>{data.assessment.note}</Note>
            <h3>Recorded observations</h3>
            {data.assessment.observations.length ? (
              data.assessment.observations.map((row, i) => (
                <p key={i}>
                  <strong>
                    {row.domain}: {row.name}
                  </strong>{" "}
                  — {row.value} {row.unit}, {row.reps} reps, effort {row.effort}
                  /10 <Tag>{row.provenance}</Tag>
                  <br />
                  {row.derived}
                </p>
              ))
            ) : (
              <Empty>
                No recorded benchmarks. Add comfortable existing results in your
                profile or check-in.
              </Empty>
            )}
            <h3>Estimates · kept separate</h3>
            {data.assessment.estimates.length ? (
              data.assessment.estimates.map((row, i) => (
                <p key={i}>
                  {row.name}: {row.value} {row.unit} · estimated input.{" "}
                  {row.derived}
                </p>
              ))
            ) : (
              <p className="muted">No estimated benchmark inputs.</p>
            )}
            <p>
              Mobility: {data.assessment.mobility} (self-assessed).{" "}
              {data.assessment.experience}
            </p>
            <p className="muted">
              Missing observed domains:{" "}
              {data.assessment.missing_domains.join(", ") ||
                "None in this limited test set"}
              . {data.assessment.recovery}
            </p>
          </Card>
          <Card title="Recovery and progression review">
            <Tag>{data.review.recovery.status}</Tag>
            <p>
              {data.review.recovery.flags.join("; ") ||
                "No reported adverse flags; missing signals remain unknown."}
            </p>
            <Note>{data.review.recovery.note}</Note>
            <p>
              Last 7 days: {data.review.workload.last_7_days_minutes} actual
              minutes; previous 7 days:{" "}
              {data.review.workload.previous_7_days_minutes}. Session-RPE load:{" "}
              {data.review.workload.session_rpe_load_au} AU;{" "}
              {data.review.workload.sessions_missing_rpe} performed sessions
              without RPE.
            </p>
            <p>
              {data.review.workload.completed} completed ·{" "}
              {data.review.workload.failed} failed ·{" "}
              {data.review.workload.missed} missed. Logged completion:{" "}
              {data.review.workload.logged_completion_percent == null
                ? "Unknown"
                : `${data.review.workload.logged_completion_percent}%`}
              .
            </p>
            <p className="muted">{data.review.workload.note}</p>
            <details>
              <summary>Exercise progression decisions</summary>
              {data.review.decisions.map((row) => (
                <p key={row.exercise}>
                  <strong>
                    {row.exercise}: {row.action.replaceAll("_", " ")}
                  </strong>
                  {row.target != null
                    ? ` · proposed target ${row.target}${row.action === "increase_load" ? " kg" : row.action === "increase_duration" ? " min" : " reps"}`
                    : ""}
                  . {row.reason}
                </p>
              ))}
            </details>
            <Note>
              {data.review.note} Open Progress to create a week 4/8/12
              reassessment preview.
            </Note>
          </Card>
          <Card title="Exercise performance over time">
            {!names.length ? (
              <Empty>
                Log actual exercise sets to build your performance history. No
                estimated sessions are plotted.
              </Empty>
            ) : (
              <>
                <div className="form-grid">
                  <label>
                    Recorded exercise
                    <select
                      aria-label="Recorded exercise"
                      value={name}
                      onChange={(e) => setSelected(e.target.value)}
                    >
                      {names.map((n) => (
                        <option key={n}>{n}</option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Performance metric
                    <select
                      aria-label="Performance metric"
                      value={metric}
                      onChange={(e) =>
                        setMetric(e.target.value as typeof metric)
                      }
                    >
                      {Object.entries({
                        weight_kg: "Load (kg)",
                        reps: "Repetitions",
                        duration_seconds: "Duration (seconds)",
                        distance_m: "Distance (m)",
                        rpe: "Set RPE",
                      }).map(([key, label]) => (
                        <option key={key} value={key}>
                          {label}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
                <p className="muted">
                  Each point is an actual set; compare equal repetitions,
                  technique and effort. A higher load alone does not prove
                  improvement. Failed attempts remain labeled in the table.
                </p>
                {trend.some((row) => row.value != null) && (
                  <div
                    role="img"
                    aria-label={`${name} recorded ${metric} trend; values also listed in the table`}
                  >
                    <ResponsiveContainer width="100%" height={230}>
                      <LineChart data={trend}>
                        <CartesianGrid stroke="#35383d" />
                        <XAxis dataKey="label" hide />
                        <YAxis
                          domain={["auto", "auto"]}
                          tick={{ fill: "#b8bdc8" }}
                        />
                        <Tooltip
                          itemStyle={{ color: "#f4f5f7" }}
                          contentStyle={{
                            background: "#202125",
                            border: "1px solid #525762",
                            color: "white",
                          }}
                        />
                        <Line
                          dataKey="value"
                          stroke="#ef4444"
                          isAnimationActive={false}
                          connectNulls={false}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}
                <div
                  className="table-wrap"
                  role="region"
                  aria-label="Actual exercise set history"
                  tabIndex={0}
                >
                  <table>
                    <caption>Actual sets · {name}</caption>
                    <thead>
                      <tr>
                        {[
                          "Date / session",
                          "Status / set",
                          "Reps",
                          "Load kg",
                          "Seconds",
                          "Distance m",
                          "Set / session RPE",
                          "Notes",
                        ].map((h) => (
                          <th key={h}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((row) => (
                        <tr key={row.key}>
                          <td>
                            {row.date}
                            <br />
                            {row.session}
                          </td>
                          <td>
                            {row.status} / {row.set}
                          </td>
                          <td>{row.reps ?? "Unknown"}</td>
                          <td>{row.weight_kg ?? "Unknown"}</td>
                          <td>{row.duration_seconds ?? "Unknown"}</td>
                          <td>{row.distance_m ?? "Unknown"}</td>
                          <td>
                            {row.rpe ?? "Unknown"} /{" "}
                            {row.sessionRpe ?? "Unknown"}
                          </td>
                          <td>{row.notes || "—"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </Card>
        </>
      )}
      {catalog && (
        <Card title="Exercise catalog">
          <Note>
            Informational practice library. Catalog inclusion is not a
            prescription. Advanced impact, throws, contact and injury-sensitive
            programming require qualified coaches. Alternatives may change the
            training focus.
          </Note>
          <div className="form-grid">
            <label>
              Find an exercise
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                type="search"
              />
            </label>
            <label>
              Exercise category
              <select
                aria-label="Exercise category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                {["All", ...new Set(exercises.map((ex) => ex.category))].map(
                  (c) => (
                    <option key={c}>{c}</option>
                  ),
                )}
              </select>
            </label>
          </div>
          <p>
            {
              exercises.filter(
                (ex) =>
                  (category === "All" || ex.category === category) &&
                  `${ex.name} ${ex.movement_pattern}`
                    .toLowerCase()
                    .includes(query.toLowerCase()),
              ).length
            }{" "}
            exercises shown
          </p>
          {exercises
            .filter(
              (ex) =>
                (category === "All" || ex.category === category) &&
                `${ex.name} ${ex.movement_pattern}`
                  .toLowerCase()
                  .includes(query.toLowerCase()),
            )
            .map((ex) => (
              <details key={ex.id} className="exercise">
                <summary>
                  {ex.name} · {ex.category} · {ex.difficulty}
                </summary>
                <p>
                  Pattern: {ex.movement_pattern}. Muscles involved:{" "}
                  {ex.muscles.join(", ")}. Equipment:{" "}
                  {ex.equipment.join(", ") ||
                    "No specialist equipment; suitable stable space/support still required"}
                  .
                </p>
                <p>{ex.technique}</p>
                {ex.objective && <p>Objective: {ex.objective}</p>}
                <p>
                  {ex.sets_guidance}. {ex.repetition_guidance}.
                </p>
                <p>Common mistakes: {ex.common_mistakes}</p>
                <Note>{ex.modification_notes}</Note>
                <p>
                  Alternatives:{" "}
                  {ex.alternatives
                    .map((id) => exercises.find((e) => e.id === id)?.name ?? id)
                    .join(", ")}
                </p>
                <p className="muted">{ex.evidence_note}</p>
                {ex.source_ids.map((id) => (
                  <a
                    key={id}
                    href={sources[id]}
                    target="_blank"
                    rel="noreferrer"
                  >
                    General {id} guidance
                  </a>
                ))}
              </details>
            ))}
        </Card>
      )}
    </div>
  );
}
