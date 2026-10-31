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
import type { AthleteAnalytics as Report } from "../analyticsTypes";
import type { Runner } from "../types";
import { today } from "../utils";
import { Card, Empty, Note, Tag } from "./ui";

const arts = [
  "Boxing",
  "Muay Thai",
  "Kickboxing",
  "BJJ",
  "Wrestling",
  "Judo",
  "Integrated MMA",
];
function before90() {
  const d = new Date();
  d.setDate(d.getDate() - 89);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}
export default function AthleteAnalytics({
  refreshKey,
  planId,
  run,
  busy,
}: {
  refreshKey: string;
  planId?: string;
  run: Runner;
  busy: boolean;
}) {
  const [start, setStart] = useState(before90),
    [end, setEnd] = useState(today),
    [data, setData] = useState<Report | null>(null),
    [error, setError] = useState(""),
    [loading, setLoading] = useState(false),
    [selected, setSelected] = useState(""),
    [page, setPage] = useState(1),
    [history, setHistory] = useState<{
      total: number;
      items: {
        id: string;
        date: string;
        data: { weight_kg: number; sleep: number; fatigue: number };
      }[];
    } | null>(null),
    [cycle, setCycle] = useState(""),
    [achievement, setAchievement] = useState({
      date: today(),
      discipline: "Boxing",
      title: "",
      notes: "",
    }),
    [message, setMessage] = useState("");
  const query = `start=${start}&end=${end}`;
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    setData(null);
    api<Report>(`/analytics?${query}`)
      .then((d) => {
        if (active) {
          setData(d);
          setSelected((old) =>
            d.series.some((s) => s.id === old) ? old : (d.series[0]?.id ?? ""),
          );
        }
      })
      .catch((e) => {
        if (active) setError((e as Error).message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [query, refreshKey]);
  useEffect(() => {
    setPage(1);
  }, [query, refreshKey]);
  useEffect(() => {
    let active = true;
    setHistory(null);
    api<typeof history>(
      `/analytics/history?${query}&kind=checkin&page=${page}&page_size=10`,
    )
      .then((d) => {
        if (active) setHistory(d);
      })
      .catch((e) => {
        if (active) setError((e as Error).message);
      });
    return () => {
      active = false;
    };
  }, [query, page, refreshKey]);
  const current = data?.series.find((s) => s.id === selected);
  const reload = async () => {
    setData(await api<Report>(`/analytics?${query}`));
  };
  return (
    <div className="athlete-analytics">
      <Card
        title="Athletic development dashboard"
        eyebrow="OBSERVATIONS OVER TIME"
      >
        <div className="form-grid no-print">
          <label>
            Analytics start date
            <input
              aria-label="Analytics start date"
              type="date"
              max={end}
              value={start}
              onChange={(e) => setStart(e.target.value)}
            />
          </label>
          <label>
            Analytics end date
            <input
              aria-label="Analytics end date"
              type="date"
              min={start}
              max={today()}
              value={end}
              onChange={(e) => setEnd(e.target.value)}
            />
          </label>
        </div>
        {loading && <p role="status">Loading athlete analytics…</p>}
        {error && <p role="alert">{error}</p>}
        {data && (
          <>
            <p>
              Selected period: {data.period.start} to {data.period.end}.{" "}
              {data.coverage.loaded_events} of {data.coverage.total_events}{" "}
              recorded events analyzed.
            </p>
            {data.coverage.truncated && (
              <Note>
                Coverage limited to the latest {data.coverage.event_limit}{" "}
                events. Window records and trends are incomplete; narrow the
                interval. Raw CSV export includes the full selected interval.
              </Note>
            )}
            {data.coverage.invalid_benchmark_entries > 0 && (
              <Note>
                {data.coverage.invalid_benchmark_entries} unsupported or
                incomplete benchmark entries were excluded from calculations.
              </Note>
            )}
            {data.coverage.source_plans_loaded >=
              data.coverage.source_plan_limit && (
              <Note>
                Source-plan lookup reached its {data.coverage.source_plan_limit}
                -plan limit. Cross-version duplicate reconciliation may be
                incomplete; narrow the interval.
              </Note>
            )}
            <div className="button-row no-print">
              <a
                className="button secondary"
                href={`/api/analytics/export.csv?${query}`}
                download
              >
                Download progress CSV
              </a>
              <button
                className="secondary"
                disabled={busy}
                onClick={() =>
                  run(async () => {
                    const blob = new Blob([JSON.stringify(data, null, 2)], {
                      type: "application/json",
                    });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = "athlete-development-report.json";
                    a.click();
                    URL.revokeObjectURL(url);
                  })
                }
              >
                Download development report
              </button>
              <button className="secondary" onClick={() => window.print()}>
                Print development report
              </button>
            </div>
            <Note>
              Window baselines use actual check-ins and completed sets. Profile
              values are current saved inputs, not fabricated starting
              measurements. Comparisons are descriptive and do not establish
              causation.
            </Note>
            {data.profile_summary && (
              <p>
                Current saved profile: {data.profile_summary.height_cm} cm;{" "}
                {data.profile_summary.weight_kg} kg; goal:{" "}
                {data.profile_summary.goal}. These inputs are self-reported, not
                the selected period baseline.
              </p>
            )}
            <label>
              Development metric
              <select
                aria-label="Development metric"
                value={selected}
                onChange={(e) => setSelected(e.target.value)}
              >
                {!data.series.length && (
                  <option value="">No measured series</option>
                )}
                {data.series.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.label} · {s.unit} · {s.protocol} · {s.evidence}
                  </option>
                ))}
              </select>
            </label>
            {current ? (
              <>
                <h3>
                  {current.label} ({current.unit})
                </h3>
                <p>
                  {current.protocol} <Tag>{current.evidence}</Tag>
                </p>
                <p>
                  Window baseline: {current.trend.baseline?.value}{" "}
                  {current.unit} on {current.trend.baseline?.date}; latest:{" "}
                  {current.trend.current?.value} {current.unit} on{" "}
                  {current.trend.current?.date}. Change: {current.trend.delta}{" "}
                  {current.unit}.
                </p>
                <Note>
                  {current.trend.samples} distinct recorded dates.{" "}
                  {current.trend.note}
                </Note>
                {current.chart_truncated && (
                  <p>
                    Chart/table show the latest{" "}
                    {data.coverage.chart_point_limit} daily observations; window
                    comparison uses all loaded points.
                  </p>
                )}
                <div
                  className="chart-box"
                  role="img"
                  aria-label={`${current.label} by recorded date, values in ${current.unit}; accessible data table follows`}
                >
                  <ResponsiveContainer width="100%" height={280}>
                    <LineChart
                      data={current.points}
                      margin={{ top: 15, left: 10, right: 20, bottom: 25 }}
                    >
                      <CartesianGrid stroke="#2c2e33" />
                      <XAxis
                        dataKey="date"
                        label={{
                          value: "Recorded date",
                          position: "insideBottom",
                          offset: -15,
                          fill: "#9b9fa9",
                        }}
                        tick={{ fill: "#9b9fa9", fontSize: 10 }}
                      />
                      <YAxis
                        domain={["auto", "auto"]}
                        label={{
                          value: current.unit,
                          angle: -90,
                          position: "insideLeft",
                          fill: "#9b9fa9",
                        }}
                        tick={{ fill: "#9b9fa9", fontSize: 10 }}
                      />
                      <Tooltip
                        contentStyle={{
                          background: "#202125",
                          border: "1px solid #3b3d44",
                          color: "#fff",
                        }}
                      />
                      <Line
                        dataKey="value"
                        name={`${current.label} (${current.unit})`}
                        type="linear"
                        stroke="#ef4444"
                        dot={{ r: 4 }}
                        connectNulls={false}
                        isAnimationActive={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <details>
                  <summary>Accessible development data table</summary>
                  <div
                    className="table-scroll"
                    tabIndex={0}
                    role="region"
                    aria-label="Measurement data table"
                  >
                    <table>
                      <caption>
                        {current.label}: {current.unit}, {current.protocol}
                      </caption>
                      <thead>
                        <tr>
                          <th>Date</th>
                          <th>Value ({current.unit})</th>
                          <th>Reported effort</th>
                        </tr>
                      </thead>
                      <tbody>
                        {current.points.map((p) => (
                          <tr key={`${p.date}:${p.record_id}`}>
                            <td>{p.date}</td>
                            <td>{p.value}</td>
                            <td>{p.effort ?? "Unknown"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </details>
              </>
            ) : (
              <Empty>
                No measurements in this period. No synthetic baseline or trend
                is shown.
              </Empty>
            )}
          </>
        )}
      </Card>
      {data && (
        <>
          <Card title="Window records and comparisons">
            <Note>
              Highest supported loads and repetition results are separated by
              protocol and evidence. Lower times are better only for
              fixed-distance benchmark runs; jumps are distances, not measured
              power. Estimated inputs are not actual measured records.
            </Note>
            {data.series.filter((s) => s.kind !== "observation").length ? (
              <div
                className="table-scroll"
                tabIndex={0}
                role="region"
                aria-label="Comparable personal records"
              >
                <table>
                  <thead>
                    <tr>
                      <th>Metric / protocol</th>
                      <th>Baseline → latest</th>
                      <th>Window best</th>
                      <th>Evidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.series
                      .filter((s) => s.kind !== "observation")
                      .map((s) => (
                        <tr key={s.id}>
                          <td>
                            {s.label}
                            <br />
                            {s.protocol}
                          </td>
                          <td>
                            {s.trend.baseline?.value} → {s.trend.current?.value}{" "}
                            {s.unit}
                          </td>
                          <td>
                            {s.best.value} {s.unit}
                            <br />
                            {s.best.date}
                          </td>
                          <td>
                            {s.kind === "estimate"
                              ? "Estimated input"
                              : s.kind === "derived"
                                ? "Calculated from same-date inputs"
                                : s.evidence}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <Empty>No comparable performance records in this interval.</Empty>
            )}
            {data.coverage.series_total > data.coverage.series_returned && (
              <Note>
                Showing {data.coverage.series_returned} of{" "}
                {data.coverage.series_total} series. Narrow the period or use
                raw CSV for omitted observations.
              </Note>
            )}
          </Card>
          <Card title="Training volume and adherence">
            <p>
              {data.adherence.planned == null
                ? "Due-session attendance unknown"
                : `${data.adherence.completed} completed / ${data.adherence.planned} date-assigned due sessions`}
              .{" "}
              {data.adherence.percent == null
                ? "No supported adherence percentage."
                : `${data.adherence.percent}% logged completion of due slots.`}
            </p>
            <Note>{data.adherence.note}</Note>
            <div
              className="table-scroll"
              tabIndex={0}
              role="region"
              aria-label="Weekly training volume"
            >
              <table>
                <caption>
                  Actual logged weekly volume; partial weeks are not directly
                  comparable.
                </caption>
                <thead>
                  <tr>
                    <th>Week beginning</th>
                    <th>Minutes</th>
                    <th>Completed / failed / missed</th>
                    <th>RPE load (AU)</th>
                  </tr>
                </thead>
                <tbody>
                  {data.weekly.map((w) => (
                    <tr key={w.week}>
                      <td>
                        {w.week}
                        {w.partial_week ? " (partial)" : ""}
                      </td>
                      <td>{w.minutes}</td>
                      <td>
                        {w.completed} / {w.failed} / {w.missed}
                      </td>
                      <td>
                        {w.load_au}; {w.missing_rpe} missing RPE
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {!data.weekly.length && (
              <Empty>No logged training in this interval.</Empty>
            )}
            {planId && (
              <form
                className="no-print"
                onSubmit={(e) => {
                  e.preventDefault();
                  run(async () => {
                    await api("/analytics/schedule", "POST", {
                      plan_id: planId,
                      start_date: cycle,
                    });
                    await reload();
                    setMessage(
                      "Analytics cycle start saved. Approved workouts were not changed.",
                    );
                  });
                }}
              >
                <label>
                  Analytics cycle start (Monday)
                  <input
                    aria-label="Analytics cycle start (Monday)"
                    type="date"
                    required
                    value={cycle}
                    onChange={(e) => setCycle(e.target.value)}
                  />
                </label>
                <p>
                  This assigns dates for analytics only; it does not book
                  classes or change the approved training plan.
                </p>
                <button className="secondary" disabled={busy}>
                  Save analytics cycle start
                </button>
              </form>
            )}
            {data.milestones.map((m) => (
              <p key={m}>{m}</p>
            ))}
          </Card>
          <Card title="Martial arts development">
            <Note>{data.martial_arts.note}</Note>
            <p>
              {data.martial_arts.workouts_with_practice} of{" "}
              {data.martial_arts.workouts_loaded} loaded workouts contain
              explicit discipline minutes.
            </p>
            {data.martial_arts.minutes.map((r) => (
              <p key={r.discipline}>
                {r.discipline}: {r.minutes} recorded minutes
              </p>
            ))}
            {!data.martial_arts.minutes.length && (
              <Empty>
                No explicit discipline minutes recorded. Log them with a
                workout; profile experience is not attendance history.
              </Empty>
            )}
            <h3>Technical achievements</h3>
            {data.achievements.map((a) => (
              <p key={a.id}>
                {a.date} · {a.discipline}: {a.title}. {a.evidence}.
              </p>
            ))}
            <form
              className="no-print"
              onSubmit={(e) => {
                e.preventDefault();
                run(async () => {
                  await api("/analytics/achievements", "POST", achievement);
                  setAchievement({ ...achievement, title: "", notes: "" });
                  await reload();
                  setMessage(
                    "Technical achievement saved as a self-reported milestone.",
                  );
                });
              }}
            >
              <div className="form-grid">
                <label>
                  Achievement date
                  <input
                    aria-label="Achievement date"
                    type="date"
                    required
                    max={today()}
                    value={achievement.date}
                    onChange={(e) =>
                      setAchievement({ ...achievement, date: e.target.value })
                    }
                  />
                </label>
                <label>
                  Achievement discipline
                  <select
                    aria-label="Achievement discipline"
                    value={achievement.discipline}
                    onChange={(e) =>
                      setAchievement({
                        ...achievement,
                        discipline: e.target.value,
                      })
                    }
                  >
                    {arts.map((a) => (
                      <option key={a}>{a}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Technical achievement
                  <input
                    aria-label="Technical achievement"
                    required
                    maxLength={150}
                    value={achievement.title}
                    onChange={(e) =>
                      setAchievement({ ...achievement, title: e.target.value })
                    }
                  />
                </label>
              </div>
              <button className="secondary" disabled={busy}>
                Save technical achievement
              </button>
            </form>
          </Card>
          <Card title="Development insights and reassessment">
            <ul>
              {data.observations.map((o) => (
                <li key={o}>{o}</li>
              ))}
            </ul>
            <h3>Priorities for review</h3>
            {data.priorities.map((p) => (
              <p key={p}>{p}</p>
            ))}
            {data.reassessments.map((r) => (
              <section key={r.version}>
                <h3>
                  Saved checkpoint {r.checkpoint} · report {r.version}
                </h3>
                <p>{r.reason}</p>
                {r.benchmark_changes.map((b, i) => (
                  <p key={i}>
                    {b.name}: {b.before} → {b.after} {b.unit}
                  </p>
                ))}
                <p>
                  Historical report; use the reassessment approval controls
                  below for current-input changes.
                </p>
              </section>
            ))}
            {data.nutrition_summary && (
              <p>
                Nutrition version {data.nutrition_summary.version}:{" "}
                {data.nutrition_summary.note}
                {data.nutrition_summary.usable && (
                  <>
                    {" "}
                    Current approved estimate as of{" "}
                    {data.nutrition_summary.as_of}:{" "}
                    {data.nutrition_summary.target_calories} kcal;{" "}
                    {Object.entries(data.nutrition_summary.macro_targets ?? {})
                      .map(([k, v]) => `${k} ${v} g`)
                      .join(", ")}
                    .
                  </>
                )}
              </p>
            )}
            <details>
              <summary>Analytics interpretation limits</summary>
              <ul>
                {data.limitations.map((l) => (
                  <li key={l}>{l}</li>
                ))}
              </ul>
            </details>
          </Card>
        </>
      )}
      {message && <p role="status">{message}</p>}
      <Card title="Paginated measurement history">
        <div
          className="table-scroll"
          tabIndex={0}
          role="region"
          aria-label="Check-in history"
        >
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Weight (kg)</th>
                <th>Sleep (hours)</th>
                <th>Fatigue (1–10)</th>
              </tr>
            </thead>
            <tbody>
              {history?.items.map((r) => (
                <tr key={r.id}>
                  <td>{r.date}</td>
                  <td>{r.data.weight_kg}</td>
                  <td>{r.data.sleep}</td>
                  <td>{r.data.fatigue}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p>
          {history
            ? `${history.total} check-ins in this interval; page ${page}.`
            : "Loading history…"}
        </p>
        <div className="button-row no-print">
          <button
            className="secondary"
            disabled={!history || page === 1}
            onClick={() => setPage((p) => p - 1)}
          >
            Previous measurement page
          </button>
          <button
            className="secondary"
            disabled={!history || page * 10 >= history.total}
            onClick={() => setPage((p) => p + 1)}
          >
            Next measurement page
          </button>
        </div>
      </Card>
    </div>
  );
}
