import {
  ArrowRight,
  CalendarDays,
  Check,
  Dumbbell,
  Heart,
  Plus,
} from "lucide-react";
import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../api";
import type { Runner } from "../types";
import { CheckIn, Plan, Profile, Reassessment, Saved, Workout } from "../types";
import { today } from "../utils";
import TrainingInsights from "./TrainingInsights";
import BenchmarkEditor from "./BenchmarkEditor";
import { Card, Empty, Metric, Note, Tag } from "./ui";
import AthleteAnalytics from "./AthleteAnalytics";
export default function Progress({
  profile,
  checks,
  logs,
  plan,
  run,
  refresh,
  notify,
  busy,
  dataVersion = 0,
}: {
  profile: Profile;
  checks: Saved<CheckIn>[];
  logs: Saved<Workout>[];
  plan: Saved<Plan> | null;
  run: Runner;
  refresh: () => Promise<void>;
  notify: (s: string) => void;
  busy: boolean;
  dataVersion?: number;
}) {
  const [reviewWeek, setReviewWeek] = useState(
    Math.max(4, plan?.data.review_week ?? 4),
  );
  const [form, setForm] = useState(false),
    [input, setInput] = useState<CheckIn>({
      date: today(),
      weight_kg: profile.weight_kg,
      sleep: profile.sleep,
      fatigue: 4,
      notes: "",
      benchmarks: [],
    }),
    [reports, setReports] = useState<Saved<Reassessment>[]>([]),
    [chart, setChart] = useState("weight_kg"),
    [historyError, setHistoryError] = useState("");
  useEffect(() => {
    api<Saved<Reassessment>[]>("/reassessments")
      .then(setReports)
      .catch(() =>
        setHistoryError(
          "Reassessment history could not load. Reopen Progress to retry.",
        ),
      );
  }, []);
  const sorted = [...checks].sort((a, b) =>
    a.data.date.localeCompare(b.data.date),
  );
  const workouts = plan
    ? logs.filter(
        (l) =>
          (l.data.plan_id === plan.id ||
            plan.data.history_plan_ids?.includes(l.data.plan_id)) &&
          (!l.data.status || l.data.status === "completed"),
      )
    : [];
  const benchmarkKey = (b: CheckIn["benchmarks"][number]) =>
    `${b.name} | ${b.unit} | ${b.reps} reps | ${b.provenance}`;
  const benchmarkNames = [
    ...new Set(checks.flatMap((c) => c.data.benchmarks.map(benchmarkKey))),
  ];
  const chartData = sorted.map((c) => ({
    date: c.data.date,
    value: chart.startsWith("benchmark:")
      ? c.data.benchmarks.find((b) => benchmarkKey(b) === chart.slice(10))
          ?.value
      : c.data[chart as "weight_kg" | "sleep" | "fatigue"],
  }));
  const totalSessions =
    plan?.data.weeks.reduce((sum, w) => sum + w.sessions.length, 0) || 0;
  const records = benchmarkNames.map((name) => {
    const entries = checks.flatMap((c) =>
      c.data.benchmarks
        .filter((b) => benchmarkKey(b) === name)
        .map((b) => ({ ...b, date: c.data.date })),
    );
    const timedRun = ["100m", "1km", "5km"].includes(entries[0].name);
    const best = entries.reduce((a, b) =>
      (timedRun ? b.value < a.value : b.value > a.value) ? b : a,
    );
    return { ...best, key: name };
  });
  return (
    <>
      <AthleteAnalytics
        refreshKey={`${dataVersion}:${plan?.id}:${checks.at(-1)?.id}:${logs.at(-1)?.id}`}
        planId={plan?.id}
        run={run}
        busy={busy}
      />
      {historyError && (
        <p role="alert" className="red-text">
          {historyError}
        </p>
      )}
      <div className="metric-grid">
        <Metric
          title="Check-ins recorded"
          value={`${checks.length}`}
          detail="Latest loaded check-ins; window analytics above covers longer histories"
          icon={CalendarDays}
        />
        <Metric
          title="Sessions completed"
          value={`${workouts.length} / ${totalSessions}`}
          detail="Loaded completed sessions / all prescribed slots; this is not due-session adherence"
          icon={Check}
        />
        <Metric
          title="Training minutes"
          value={`${workouts.reduce((s, l) => s + l.data.minutes, 0)}`}
          detail="Actual logged minutes · active plan"
          icon={Dumbbell}
        />
        <Metric
          title="Latest fatigue"
          value={
            sorted.length ? `${sorted.at(-1)?.data.fatigue}/10` : "No check-in"
          }
          detail="Self-reported · contextual signal"
          icon={Heart}
        />
      </div>
      <Card
        title="Your progress, in context"
        action={
          <button className="primary" onClick={() => setForm(!form)}>
            <Plus size={16} /> Weekly check-in
          </button>
        }
      >
        <div className="day-tabs">
          {(["weight_kg", "sleep", "fatigue"] as const).map((k) => (
            <button
              key={k}
              className={chart === k ? "active" : ""}
              onClick={() => setChart(k)}
            >
              {k === "weight_kg"
                ? "Weight (kg)"
                : k === "sleep"
                  ? "Sleep (hours)"
                  : "Fatigue (1–10)"}
            </button>
          ))}
          {benchmarkNames.length > 0 && (
            <select
              aria-label="Benchmark trend"
              value={chart.startsWith("benchmark:") ? chart : ""}
              onChange={(e) => {
                if (e.target.value) setChart(e.target.value);
              }}
            >
              <option value="">
                Choose a strength or conditioning benchmark
              </option>
              {benchmarkNames.map((n) => (
                <option key={n} value={`benchmark:${n}`}>
                  {n}
                </option>
              ))}
            </select>
          )}
        </div>
        {checks.length ? (
          <div className="chart-box">
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient
                    id="progressGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop offset="0%" stopColor="#ef4444" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid vertical={false} stroke="#2c2e33" />
                <XAxis
                  dataKey="date"
                  tick={{ fill: "#9b9fa9", fontSize: 11 }}
                />
                <YAxis
                  domain={chart === "fatigue" ? [0, 10] : ["auto", "auto"]}
                  tick={{ fill: "#9b9fa9", fontSize: 11 }}
                />
                <Tooltip
                  contentStyle={{
                    background: "#202125",
                    border: "1px solid #3b3d44",
                    color: "#fff",
                  }}
                />
                <Area
                  isAnimationActive={false}
                  type="linear"
                  dataKey="value"
                  stroke="#ef4444"
                  fill="url(#progressGradient)"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <Empty>
            Your first check-in starts the trend. No synthetic progress data is
            shown.
          </Empty>
        )}
        <Note>
          Small fluctuations can reflect measurement variation, hydration or
          routine. Compare repeated measurements under similar conditions before
          drawing conclusions.
        </Note>
        {form && (
          <form
            className="checkin-form"
            onSubmit={(e) => {
              e.preventDefault();
              run(async () => {
                await api("/progress", "POST", input);
                await refresh();
                setForm(false);
                notify("Check-in saved.");
              });
            }}
          >
            <div className="form-grid">
              <label>
                Date
                <input
                  type="date"
                  required
                  max={today()}
                  value={input.date}
                  onChange={(e) => setInput({ ...input, date: e.target.value })}
                />
              </label>
              <label>
                Weight (kg)
                <input
                  type="number"
                  min="30"
                  max="250"
                  step="0.1"
                  required
                  value={input.weight_kg}
                  onChange={(e) =>
                    setInput({ ...input, weight_kg: +e.target.value })
                  }
                />
              </label>
              <label>
                Body fat (%) · optional
                <input
                  type="number"
                  min="5"
                  max="60"
                  step="0.1"
                  value={input.body_fat ?? ""}
                  onChange={(e) =>
                    setInput({
                      ...input,
                      body_fat: e.target.value ? +e.target.value : null,
                    })
                  }
                />
              </label>
              <label>
                Mobility
                <select
                  aria-label="Mobility"
                  value={input.mobility ?? "Unknown"}
                  onChange={(e) =>
                    setInput({ ...input, mobility: e.target.value })
                  }
                >
                  {["Unknown", "Limited", "Comfortable"].map((v) => (
                    <option key={v}>{v}</option>
                  ))}
                </select>
              </label>
              <label>
                Sleep (hours)
                <input
                  type="number"
                  min="2"
                  max="12"
                  step="0.1"
                  required
                  value={input.sleep}
                  onChange={(e) =>
                    setInput({ ...input, sleep: +e.target.value })
                  }
                />
              </label>
              <label>
                Muscle soreness (0-10, optional)
                <input
                  type="number"
                  min="0"
                  max="10"
                  value={input.soreness ?? ""}
                  onChange={(e) =>
                    setInput({
                      ...input,
                      soreness: e.target.value === "" ? null : +e.target.value,
                    })
                  }
                />
              </label>
              <label>
                Recovery readiness (1-5, optional)
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={input.readiness ?? ""}
                  onChange={(e) =>
                    setInput({
                      ...input,
                      readiness: e.target.value === "" ? null : +e.target.value,
                    })
                  }
                />
              </label>
              <label>
                Fatigue (1–10)
                <input
                  type="number"
                  min="1"
                  max="10"
                  required
                  value={input.fatigue}
                  onChange={(e) =>
                    setInput({ ...input, fatigue: +e.target.value })
                  }
                />
              </label>
            </div>
            <label>
              Recovery, skill milestones or other notes
              <textarea
                maxLength={1000}
                value={input.notes}
                onChange={(e) => setInput({ ...input, notes: e.target.value })}
              />
            </label>
            <BenchmarkEditor
              values={input.benchmarks}
              onChange={(b) => setInput({ ...input, benchmarks: b })}
            />
            <button disabled={busy} className="primary">
              Save check-in
            </button>
          </form>
        )}
      </Card>
      <Card title="Recorded personal bests">
        <p className="muted">
          These quick records use the latest loaded check-ins. Use window
          records above for longer intervals. Compared only within the same
          test, units, repetition count and evidence label. Effort and testing
          conditions still affect comparability.
        </p>
        {records.length ? (
          <table>
            <thead>
              <tr>
                <th>Test</th>
                <th>Best result</th>
                <th>Repetitions</th>
                <th>Evidence</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r) => (
                <tr key={r.key}>
                  <td>{r.name}</td>
                  <td>
                    {r.value} {r.unit}
                  </td>
                  <td>{r.reps}</td>
                  <td>{r.provenance}</td>
                  <td>{r.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <Empty>
            Record benchmarks in your check-ins to see comparable results.
          </Empty>
        )}
      </Card>
      <Card
        title="Reassess your development"
        eyebrow="WEEKS 4 · 8 · 12"
        action={
          <button
            disabled={busy || !checks.length || !plan}
            className="secondary"
            onClick={() =>
              run(async () => {
                await api("/reassessments", "POST", { week: reviewWeek });
                setReports(await api("/reassessments"));
              })
            }
          >
            Run reassessment <ArrowRight size={15} />
          </button>
        }
      >
        <p className="muted">
          Review your latest check-in against the active plan’s original inputs.
          Suggestions never replace your plan automatically.
        </p>
        <label>
          Reassessment checkpoint
          <select
            aria-label="Reassessment checkpoint"
            value={reviewWeek}
            onChange={(e) => setReviewWeek(+e.target.value)}
          >
            {[4, 8, 12].map((w) => (
              <option key={w} value={w}>
                Week {w}
              </option>
            ))}
          </select>
        </label>
        {[...reports].reverse().map((r) => (
          <div className="reassessment" key={r.id}>
            <Tag>Reassessment v{r.version}</Tag>
            <h3>{r.data.reason}</h3>
            <div className="tags">
              <Tag>
                Weight change {r.data.weight_change_kg > 0 ? "+" : ""}
                {r.data.weight_change_kg} kg
              </Tag>
              <Tag>{r.data.sessions_logged} sessions logged</Tag>
              <Tag>
                {r.data.before_days} → {r.data.suggested_days} suggested days
              </Tag>
            </div>
            {r.data.benchmark_changes.map((b) => (
              <p key={b.name}>
                {b.name}: {b.before} → {b.after} {b.unit} (change {b.delta}).{" "}
                {b.note}
              </p>
            ))}
            <p className="muted">{r.data.note}</p>
            {r.data.nutrition_review && (
              <Note>
                Nutrition review: {r.data.nutrition_review.reason}.{" "}
                {r.data.nutrition_review.needs_review
                  ? "Open Nutrition to preview and approve current-input meals; no automatic replan occurred."
                  : "Current nutrition retained; isolated fluctuations do not regenerate targets."}
              </Note>
            )}
            {r.data.review && (
              <details>
                <summary>Actual performance and workload decisions</summary>
                <p>
                  {r.data.review.workload.completed} completed,{" "}
                  {r.data.review.workload.failed} failed,{" "}
                  {r.data.review.workload.missed} missed. {r.data.review.note}
                </p>
                {r.data.review.decisions.map((d) => (
                  <p key={d.exercise}>
                    {d.exercise}: {d.action.replaceAll("_", " ")}. {d.reason}
                  </p>
                ))}
              </details>
            )}
            <button
              disabled={busy || r.data.review_week === 12}
              className="secondary"
              onClick={() =>
                run(async () => {
                  await api(`/reassessments/${r.id}/proposal`, "POST");
                  await refresh();
                  notify(
                    "Proposal created. Open AI coach to review and approve or reject it.",
                  );
                })
              }
            >
              Preview recommended adjustment
            </button>
          </div>
        ))}
      </Card>
      <TrainingInsights
        refreshKey={`${dataVersion}:${plan?.id}:${logs.length}:${checks.length}`}
      />
      <Card title="Recent check-ins">
        {sorted.length ? (
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Weight</th>
                <th>Sleep</th>
                <th>Fatigue</th>
                <th>Body fat / mobility</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {[...sorted].reverse().map((c) => (
                <tr key={c.id}>
                  <td>{c.data.date}</td>
                  <td>{c.data.weight_kg} kg</td>
                  <td>{c.data.sleep} h</td>
                  <td>{c.data.fatigue}/10</td>
                  <td>
                    {c.data.body_fat == null
                      ? "Unknown"
                      : `${c.data.body_fat}%`}{" "}
                    / {c.data.mobility ?? "Unknown"}
                  </td>
                  <td>{c.data.notes || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <Empty>No check-ins yet.</Empty>
        )}
      </Card>
    </>
  );
}
