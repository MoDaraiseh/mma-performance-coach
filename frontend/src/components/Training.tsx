import {
  ArrowRight,
  Check,
  ChevronLeft,
  ChevronRight,
  Dumbbell,
  Heart,
  X,
} from "lucide-react";
import { lazy, Suspense, useEffect, useState } from "react";
import { api } from "../api";
import type { ExercisePerformance, Runner } from "../types";
import { Plan, Saved, TrainingSession, Workout } from "../types";
import { Card, Note, Tag } from "./ui";
import PerformanceEditor from "./PerformanceEditor";
import { today } from "../utils";
import { useDialog } from "./useDialog";
const TrainingInsights = lazy(() => import("./TrainingInsights"));
export default function Training({
  plan,
  logs,
  run,
  refresh,
  busy,
}: {
  plan: Saved<Plan> | null;
  logs: Saved<Workout>[];
  run: Runner;
  refresh: () => Promise<void>;
  busy: boolean;
}) {
  const [performances, setPerformances] = useState<ExercisePerformance[]>([]);
  const [fatigue, setFatigue] = useState<number | "">("");
  const [practiceDiscipline, setPracticeDiscipline] = useState(""),
    [practiceMinutes, setPracticeMinutes] = useState(0);
  const [week, setWeek] = useState(
      Math.min(12, (plan?.data.review_week ?? 0) + 1),
    ),
    [selected, setSelected] = useState<TrainingSession | null>(null),
    [minutes, setMinutes] = useState(30),
    [effort, setEffort] = useState<number | "">(""),
    [completedOn, setCompletedOn] = useState(today()),
    [status, setStatus] = useState<"completed" | "failed">("completed"),
    [substitutionMessage, setSubstitutionMessage] = useState(""),
    [notes, setNotes] = useState(""),
    [logError, setLogError] = useState("");
  const [history, setHistory] = useState<Saved<Plan>[]>([]);
  const [historyError, setHistoryError] = useState("");
  useEffect(() => {
    api<Saved<Plan>[]>("/training-plans/history")
      .then(setHistory)
      .catch(() =>
        setHistoryError(
          "Plan history could not load. Reopen Training to retry.",
        ),
      );
    setWeek(Math.min(12, (plan?.data.review_week ?? 0) + 1));
    setSelected(null);
    setPerformances([]);
  }, [plan?.id]);
  const current = plan?.data.weeks[week - 1];
  const dialog = useDialog(Boolean(selected), () => setSelected(null));
  if (!plan)
    return (
      <Card title="Build your 12-week plan">
        <p>
          Generate a conservative roadmap from your saved availability and
          training background.
        </p>
        <button
          disabled={busy}
          className="primary"
          onClick={() =>
            run(async () => {
              await api("/training-plans", "POST");
              await refresh();
            })
          }
        >
          Generate training plan <ArrowRight size={16} />
        </button>
      </Card>
    );
  const historicalWeek = week <= (plan.data.review_week ?? 0);
  const lineageIds = new Set(plan.data.history_plan_ids ?? []);
  const done = (id: string) =>
    logs.some(
      (l) =>
        (l.data.plan_id === plan.id || lineageIds.has(l.data.plan_id)) &&
        l.data.session_id === id,
    );
  return (
    <>
      {plan.data.available === false && <Note>{plan.data.reason}</Note>}
      {substitutionMessage && <p role="status">{substitutionMessage}</p>}
      {plan.data.availability_note && (
        <Note>
          {plan.data.availability_note} Recovery days:{" "}
          {plan.data.recovery_days?.join(", ")}. {plan.data.power_note}
        </Note>
      )}
      {historicalWeek && (
        <Note>
          Historical checkpoint week: retained for review. Current prescriptions
          begin after week {plan.data.review_week}; logging these prior weeks is
          closed.
        </Note>
      )}
      {historyError && <p role="alert">{historyError}</p>}
      <Card title="Saved program history">
        <p className="muted">
          Earlier versions remain read-only. Changes require a new proposal in
          AI coach.
        </p>
        {[...history].reverse().map((entry) => (
          <details key={entry.id}>
            <summary>
              Version {entry.version} · {entry.data.days} days ·{" "}
              {new Date(entry.created_at).toLocaleDateString()}
              {entry.id === plan.id ? " · Active" : " · Archived"}
            </summary>
            <p>{entry.data.method}</p>
            <Note>
              Historical prescription. Review current health and availability
              before using it.
            </Note>
            {entry.data.weeks.map((w) => (
              <p key={w.week}>
                Week {w.week} · {w.phase}:{" "}
                {w.sessions
                  .map((s) => `${s.day}: ${s.type} (${s.minutes} min)`)
                  .join("; ") || "Exercise prescription withheld"}
              </p>
            ))}
          </details>
        ))}
      </Card>
      <div className="phase-strip">
        {["Foundation", "Development", "Consolidation"].map((phase, i) => (
          <button
            key={phase}
            onClick={() => setWeek(i * 4 + 1)}
            className={current?.phase === phase ? "active" : ""}
          >
            <span>0{i + 1}</span>
            <div>
              <strong>{phase}</strong>
              <small>
                Weeks {i * 4 + 1}–{i * 4 + 4}
              </small>
            </div>
            {current?.phase === phase && <Tag tone="red">Selected phase</Tag>}
          </button>
        ))}
      </div>
      <Card
        title={`Week ${week} · ${current?.phase}`}
        action={
          <div className="week-switch">
            <button
              className="icon-button"
              aria-label="Previous week"
              disabled={week === 1}
              onClick={() => setWeek(week - 1)}
            >
              <ChevronLeft size={18} />
            </button>
            <select
              aria-label="Training week"
              value={week}
              onChange={(e) => setWeek(+e.target.value)}
            >
              {Array.from({ length: 12 }, (_, i) => (
                <option key={i} value={i + 1}>
                  Week {i + 1}
                </option>
              ))}
            </select>
            <button
              className="icon-button"
              aria-label="Next week"
              disabled={week === 12}
              onClick={() => setWeek(week + 1)}
            >
              <ChevronRight size={18} />
            </button>
          </div>
        }
      >
        <p>
          {current?.focus}{" "}
          {current?.deload && <Tag tone="green">Deload & reassess</Tag>}
        </p>
        {plan.data.available !== false && (
          <div className="training-grid">
            {[
              "Monday",
              "Tuesday",
              "Wednesday",
              "Thursday",
              "Friday",
              "Saturday",
              "Sunday",
            ].map((day) => {
              const s = current?.sessions.find((x) => x.day === day);
              return (
                <div className={`training-day ${s ? "" : "rest"}`} key={day}>
                  <p className="eyebrow">{day}</p>
                  {s ? (
                    <>
                      <div
                        className={`schedule-icon ${s.type === "Technique" ? "purple" : s.type === "Conditioning" ? "green" : ""}`}
                      >
                        <Dumbbell size={21} />
                      </div>
                      <h3>{s.type}</h3>
                      <p>
                        {s.minutes} minutes · RPE {s.effort}
                      </p>
                      <small>{s.exercises[0].name}</small>
                      <button
                        disabled={busy}
                        className={
                          done(s.id) ? "text-button green-text" : "secondary"
                        }
                        onClick={() => {
                          setSelected(s);
                          setPerformances([]);
                          setPracticeDiscipline("");
                          setPracticeMinutes(0);
                          setFatigue("");
                          setStatus("completed");
                          setCompletedOn(today());
                          setSubstitutionMessage("");
                          setMinutes(Math.ceil(s.minutes));
                          setEffort("");
                          setNotes("");
                          setLogError("");
                        }}
                      >
                        {done(s.id) ? (
                          <>
                            <Check size={15} />{" "}
                            {logs.find(
                              (l) =>
                                l.data.plan_id === plan.id &&
                                l.data.session_id === s.id,
                            )?.data.status === "missed"
                              ? "Missed"
                              : "Logged"}
                          </>
                        ) : (
                          <>
                            View session <ArrowRight size={14} />
                          </>
                        )}
                      </button>
                    </>
                  ) : (
                    <>
                      <Heart size={23} />
                      <h3>Recovery</h3>
                      <small>
                        Rest, easy walking and comfortable mobility.
                      </small>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </Card>
      <div className="two-column">
        <Card title="Progression with purpose">
          <p>{plan.data.method}</p>
          <p>{plan.data.scheduling_note}</p>
          <p className="muted">
            Input snapshot: {new Date(plan.created_at).toLocaleDateString()} ·
            version {plan.version}. {plan.data.days} planned days of{" "}
            {plan.data.requested_days} requested.
          </p>
          <Note>{plan.data.limitations}</Note>
        </Card>
        <Card title="Recovery is part of training">
          <h3>Check in at weeks 4, 8 and 12</h3>
          <p className="muted">
            Repeat the same benchmarks and review sleep, fatigue and
            consistency. Avoid interpreting a single day’s scale change as
            progress or regression.
          </p>
          <p className="muted">
            If pain, unusual fatigue or dizziness occurs, stop and seek
            qualified advice.
          </p>
        </Card>
      </div>
      <Suspense
        fallback={<p role="status">Loading training intelligence...</p>}
      >
        <TrainingInsights refreshKey={`${plan.id}:${logs.length}`} catalog />
      </Suspense>
      {selected && (
        <div className="modal-backdrop">
          <section
            ref={dialog}
            className="modal session-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="session-title"
          >
            <button
              className="modal-close icon-button"
              aria-label="Close session"
              onClick={() => setSelected(null)}
            >
              <X />
            </button>
            <p className="eyebrow">
              WEEK {week} · {selected.day.toUpperCase()}
            </p>
            <h2 id="session-title">{selected.type}</h2>
            <p>{selected.objective}</p>
            <Tag>
              {selected.minutes} min · RPE {selected.effort}
            </Tag>
            <p className="muted">{selected.warmup}</p>
            {selected.exercises.map((ex) => (
              <div className="exercise" key={ex.name}>
                <h3>{ex.name}</h3>
                <p>
                  {ex.sets} sets × {ex.reps} · rest {ex.rest}
                </p>
                <p className="muted">{ex.cue}</p>
                <p>
                  RPE {ex.rpe ?? selected.effort} ? {ex.block_minutes ?? "?"}{" "}
                  work minutes including rests. {ex.technique_focus}
                </p>
                {ex.suggested_load_kg != null && (
                  <p>
                    Reviewed load suggestion: {ex.suggested_load_kg} kg only if
                    a suitable small increment is available.
                  </p>
                )}
                <p className="muted">{ex.progression_rule}</p>
                <details>
                  <summary>Exercise substitution</summary>
                  <p>{ex.substitution}</p>
                  {!historicalWeek &&
                    !done(selected.id) &&
                    Boolean(ex.alternative_ids?.length) && (
                      <label>
                        Preview alternative for {ex.name}
                        <select
                          aria-label={`Preview alternative for ${ex.name}`}
                          defaultValue=""
                          disabled={busy}
                          onChange={(e) => {
                            const alternative = e.target.value;
                            if (!alternative) return;
                            run(async () => {
                              await api(
                                "/training-plans/substitution-preview",
                                "POST",
                                {
                                  session_id: selected.id,
                                  exercise_name: ex.name,
                                  alternative_id: alternative,
                                },
                              );
                              setSelected(null);
                              setSubstitutionMessage(
                                "Substitution proposal created. Open AI coach to review details and approve or reject.",
                              );
                            });
                          }}
                        >
                          <option value="">
                            Choose an alternative proposal
                          </option>
                          {ex.alternative_ids?.map((id) => (
                            <option key={id} value={id}>
                              {id.replaceAll("-", " ")}
                            </option>
                          ))}
                        </select>
                      </label>
                    )}
                </details>
              </div>
            ))}
            <p className="muted">
              {selected.cooldown}. {selected.time_note}
            </p>
            {historicalWeek ? (
              <Note>Past checkpoint prescription ? read-only.</Note>
            ) : done(selected.id) ? (
              <Note>This session is already logged in the active plan.</Note>
            ) : (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  run(async () => {
                    setLogError("");
                    try {
                      await api("/training-sessions", "POST", {
                        session_id: selected.id,
                        plan_id: plan.id,
                        completed_on: completedOn,
                        status,
                        performances,
                        practices: practiceDiscipline
                          ? [
                              {
                                discipline: practiceDiscipline,
                                minutes: practiceMinutes,
                              },
                            ]
                          : [],
                        minutes,
                        effort: effort === "" ? null : effort,
                        fatigue: fatigue === "" ? null : fatigue,
                        notes,
                      });
                      await refresh();
                      setSelected(null);
                    } catch (e) {
                      setLogError((e as Error).message);
                      throw e;
                    }
                  });
                }}
              >
                {logError && (
                  <p role="alert" className="red-text">
                    {logError}
                  </p>
                )}
                <h3>Log this session</h3>
                <label>
                  Post-session fatigue (1–10, optional)
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={fatigue}
                    onChange={(e) =>
                      setFatigue(e.target.value === "" ? "" : +e.target.value)
                    }
                  />
                </label>
                <div className="form-grid">
                  <label>
                    Session date
                    <input
                      type="date"
                      required
                      max={today()}
                      value={completedOn}
                      onChange={(e) => setCompletedOn(e.target.value)}
                    />
                  </label>
                  <label>
                    Session outcome
                    <select
                      aria-label="Session outcome"
                      value={status}
                      onChange={(e) =>
                        setStatus(e.target.value as typeof status)
                      }
                    >
                      <option value="completed">Completed</option>
                      <option value="failed">
                        Failed / stopped before completion
                      </option>
                    </select>
                  </label>
                </div>
                <PerformanceEditor
                  names={selected.exercises.map((ex) => ex.name)}
                  values={performances}
                  onChange={setPerformances}
                />
                <div className="form-grid">
                  <label>
                    Martial arts discipline (optional)
                    <select
                      aria-label="Martial arts discipline (optional)"
                      value={practiceDiscipline}
                      onChange={(e) => setPracticeDiscipline(e.target.value)}
                    >
                      <option value="">Not recorded</option>
                      {[
                        "Boxing",
                        "Muay Thai",
                        "Kickboxing",
                        "BJJ",
                        "Wrestling",
                        "Judo",
                        "Integrated MMA",
                      ].map((d) => (
                        <option key={d}>{d}</option>
                      ))}
                    </select>
                  </label>
                  {practiceDiscipline && (
                    <label>
                      Actual discipline minutes
                      <input
                        aria-label="Actual discipline minutes"
                        type="number"
                        required
                        min={1}
                        max={minutes}
                        value={practiceMinutes || ""}
                        onChange={(e) =>
                          setPracticeMinutes(Number(e.target.value))
                        }
                      />
                    </label>
                  )}
                </div>
                <div className="form-grid">
                  <label>
                    Actual minutes
                    <input
                      type="number"
                      min="1"
                      max="180"
                      required
                      value={minutes}
                      onChange={(e) => setMinutes(+e.target.value)}
                    />
                  </label>
                  <label>
                    Effort (1–10)
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={effort}
                      onChange={(e) =>
                        setEffort(e.target.value === "" ? "" : +e.target.value)
                      }
                    />
                  </label>
                </div>
                <label>
                  Notes
                  <textarea
                    maxLength={1000}
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                  />
                </label>
                <button
                  type="button"
                  className="secondary"
                  disabled={busy}
                  onClick={() =>
                    run(async () => {
                      await api("/training-sessions", "POST", {
                        session_id: selected.id,
                        plan_id: plan.id,
                        completed_on: completedOn,
                        minutes: 0,
                        status: "missed",
                        notes,
                      });
                      await refresh();
                      setSelected(null);
                    })
                  }
                >
                  Mark session missed
                </button>
                <button className="primary" disabled={busy}>
                  <Check size={16} /> Save workout
                </button>
              </form>
            )}
          </section>
        </div>
      )}
    </>
  );
}
