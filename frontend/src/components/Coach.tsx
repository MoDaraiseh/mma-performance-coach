import { ArrowRight, ArrowUpRight, Check, Sparkles } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import type { Runner } from "../types";
import {
  CoachProposal,
  Conversation,
  Plan,
  Proposal,
  Saved,
  TrainingSession,
} from "../types";
import { Card, Note, Tag } from "./ui";
import { NutritionPreview } from "./NutritionWorkbench";

function SessionPreview({
  title,
  session,
}: {
  title: string;
  session: TrainingSession;
}) {
  return (
    <section>
      <h3>
        {title}: {session.day} · {session.minutes} minutes
      </h3>
      {session.exercises.map((ex, i) => (
        <p key={`${ex.name}-${i}`}>
          {ex.name}: {ex.sets} sets · {ex.reps} · rest {ex.rest} · RPE{" "}
          {ex.rpe ?? session.effort} · timed block {ex.block_minutes} minutes.{" "}
          {ex.technique_focus ?? ex.cue}
        </p>
      ))}
    </section>
  );
}
export default function Coach({
  plan,
  run,
  refresh,
  busy,
}: {
  plan: Saved<Plan> | null;
  run: Runner;
  refresh: () => Promise<void>;
  busy: boolean;
}) {
  const chatRef = useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<Saved<Conversation>[]>([]),
    [message, setMessage] = useState(""),
    [useAI, setUseAI] = useState(false),
    [configured, setConfigured] = useState(false),
    [days, setDays] = useState(plan?.data.days || 3),
    [reason, setReason] = useState("My availability has changed."),
    [proposals, setProposals] = useState<Saved<Proposal>[]>([]),
    [actions, setActions] = useState<Saved<CoachProposal>[]>([]);
  const load = async () => {
    setMessages(await api("/coach"));
    setProposals(await api("/revisions"));
    setActions(await api("/coach/actions"));
  };
  useEffect(() => {
    if (messages.length && chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);
  useEffect(() => {
    run(async () => {
      await load();
      const h = await api<{ ai_configured: boolean }>("/health");
      setConfigured(h.ai_configured);
    });
  }, []);
  const send = (text: string) =>
    run(async () => {
      await api("/coach", "POST", { message: text, use_ai: useAI });
      setMessage("");
      setMessages(await api("/coach"));
      setActions(await api("/coach/actions"));
    });
  return (
    <>
      <div className="coach-layout">
        <Card
          title="Your coaching conversation"
          eyebrow="IN YOUR CORNER"
          action={
            <Tag tone={useAI ? "red" : "green"}>
              {useAI ? "AI interpretation" : "Local guidance"}
            </Tag>
          }
        >
          <div className="chat" ref={chatRef}>
            <div className="coach-welcome">
              <span className="brand-icon">
                <Sparkles />
              </span>
              <h3>Make your next step a clear one.</h3>
              <p>
                I use your saved profile and plan to explain priorities. Start
                with a question below.
              </p>
              <div className="prompt-grid">
                {[
                  "Why did you recommend wrestling?",
                  "What should I work on for boxing?",
                  "Explain my fighter matches.",
                  "How do I adjust my schedule?",
                  "Make my Monday workout shorter to 20 minutes.",
                  "Suggest a different halal lunch with similar nutritional values.",
                  "Reschedule my Monday workout to Wednesday in week 1.",
                  "Change training frequency to 3 days per week from week 2.",
                  "Propose training progression from week 3.",
                  "Request an updated assessment.",
                  "Explain my progress and possible plateaus.",
                ].map((q) => (
                  <button disabled={busy} key={q} onClick={() => send(q)}>
                    {q}
                    <ArrowUpRight size={14} />
                  </button>
                ))}
              </div>
            </div>
            {messages.map((m) => (
              <div className="chat-pair" key={m.id}>
                <div className="user-bubble">{m.data.question}</div>
                <div className="coach-bubble">
                  <span className="eyebrow">
                    <Sparkles size={13} />
                    {m.data.mode}
                  </span>
                  <p>{m.data.answer}</p>
                  <small>{m.data.limitations}</small>
                  {m.data.context_summary && (
                    <details>
                      <summary>Context and evidence used</summary>
                      <p>{m.data.context_summary.note}</p>
                      <p>
                        Included: {m.data.context_summary.sections.join(", ")}
                      </p>
                      <p>
                        Omitted by size limit:{" "}
                        {m.data.context_summary.omitted.join(", ") || "None"}
                      </p>
                    </details>
                  )}
                  {m.data.action_summary && (
                    <Note>{m.data.action_summary}</Note>
                  )}
                  {m.data.action_error && (
                    <p role="status">
                      No change prepared: {m.data.action_error}
                    </p>
                  )}
                </div>
              </div>
            ))}
            {busy && (
              <p role="status" className="muted">
                Working with your saved context…
              </p>
            )}
          </div>
          <form
            className="chat-form"
            onSubmit={(e) => {
              e.preventDefault();
              if (message.trim()) send(message);
            }}
          >
            <textarea
              aria-label="Message your MMA coach"
              placeholder="Ask about your training, recovery or development…"
              maxLength={2000}
              required
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
            <button
              className="primary"
              disabled={busy || !message.trim()}
              aria-label="Send coaching question"
            >
              <ArrowRight size={18} />
            </button>
          </form>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={useAI}
              disabled={!configured}
              onChange={(e) => setUseAI(e.target.checked)}
            />
            Use OpenAI{" "}
            {configured
              ? "(question, goals, discipline background, usable plan/meal summaries, restrictions and recent recovery/training summaries are sent)"
              : "(not configured; local coach available)"}
          </label>
        </Card>
        <div>
          {[...actions].reverse().map((row) => (
            <Card
              key={row.id}
              title={`Coaching change ${row.version}: ${row.data.target}`}
              eyebrow={
                row.data.status === "approved"
                  ? "APPROVED AND SAVED"
                  : row.data.status === "rejected"
                    ? "REJECTED, ACTIVE PLAN UNCHANGED"
                    : "VALIDATED PREVIEW, NOT APPLIED"
              }
              action={<Tag>{row.data.status}</Tag>}
            >
              {row.data.changes.map((change) => (
                <p key={change}>{change}</p>
              ))}
              {row.data.nutrition_plan && (
                <NutritionPreview plan={row.data.nutrition_plan} />
              )}
              {row.data.status === "approved" && row.data.saved_plan_id && (
                <p role="status">
                  Saved {row.data.target} version{" "}
                  {row.data.saved_version ?? "(historical)"}. Record:{" "}
                  {row.data.saved_plan_id}
                </p>
              )}
              {row.data.assessment && (
                <section>
                  <h3>Updated assessment preview</h3>
                  <p>{row.data.assessment.note}</p>
                  <h4>User-entered observations</h4>
                  {row.data.assessment.observations.map((r) => (
                    <p key={r.name}>
                      {r.name}: {r.value} {r.unit}. {r.note}
                    </p>
                  ))}
                  <h4>Estimates</h4>
                  {row.data.assessment.estimates.map((r) => (
                    <p key={r.name}>
                      {r.name}: {r.value} {r.unit}. {r.note}
                    </p>
                  ))}
                  <p>
                    Missing domains:{" "}
                    {row.data.assessment.missing_domains.join(", ") ||
                      "None among collected domains"}
                    . Approval saves a separate snapshot; no plan or profile
                    changes.
                  </p>
                </section>
              )}
              {row.data.before_week && row.data.after_week && (
                <details>
                  <summary>Review weekly schedule differences</summary>
                  <h3>Before week {row.data.before_week.week}</h3>
                  {row.data.before_week.sessions.map((s) => (
                    <SessionPreview key={s.id} title="Before" session={s} />
                  ))}
                  <h3>Proposed week {row.data.after_week.week}</h3>
                  {row.data.after_week.sessions.map((s) => (
                    <SessionPreview key={s.id} title="Proposed" session={s} />
                  ))}
                </details>
              )}
              {row.data.from_week && row.data.plan && (
                <details>
                  <summary>Review all affected future weeks</summary>
                  {row.data.plan.weeks
                    .filter((w) => w.week >= (row.data.from_week ?? 1))
                    .map((w) => (
                      <section key={w.week}>
                        <h3>
                          Week {w.week}: {w.phase}
                        </h3>
                        {w.sessions.map((s) => (
                          <SessionPreview
                            key={s.id}
                            title="Proposed"
                            session={s}
                          />
                        ))}
                      </section>
                    ))}
                </details>
              )}
              {row.data.before_session && row.data.after_session && (
                <details>
                  <summary>
                    Review before and after workout prescriptions
                  </summary>
                  <SessionPreview
                    title="Before"
                    session={row.data.before_session}
                  />
                  <SessionPreview
                    title="Proposed"
                    session={row.data.after_session}
                  />
                  <Note>
                    Only this unlogged session changes. Other weeks, saved
                    profile and historical logs remain intact. Review all
                    exercise/time differences before approval.
                  </Note>
                </details>
              )}
              {row.data.status === "pending" && (
                <div className="button-row">
                  <button
                    className="primary"
                    disabled={busy}
                    onClick={() =>
                      run(async () => {
                        await api(`/coach/actions/${row.id}/approve`, "POST");
                        await refresh();
                        await load();
                      })
                    }
                  >
                    Approve coaching change
                  </button>
                  <button
                    className="secondary"
                    disabled={busy}
                    onClick={() =>
                      run(async () => {
                        await api(`/coach/actions/${row.id}/reject`, "POST");
                        await load();
                      })
                    }
                  >
                    Reject coaching change
                  </button>
                </div>
              )}
            </Card>
          ))}
          <Card title="Propose a plan change" eyebrow="YOU STAY IN CONTROL">
            <p className="muted">
              Preview a new weekly frequency. Your active plan changes only when
              you approve.
            </p>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                run(async () => {
                  await api("/revisions", "POST", { days, reason });
                  setProposals(await api("/revisions"));
                });
              }}
            >
              <label>
                Available days per week
                <input
                  type="number"
                  min="1"
                  max="6"
                  required
                  value={days}
                  onChange={(e) => setDays(+e.target.value)}
                />
              </label>
              <label>
                Reason
                <textarea
                  required
                  maxLength={1000}
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                />
              </label>
              <button className="primary" disabled={busy || !plan}>
                Preview change <ArrowRight size={15} />
              </button>
            </form>
            <Note>
              Each approved version retains its original profile inputs.
              Recovery constraints may cap the proposed days.
            </Note>
          </Card>
          {[...proposals].reverse().map((p) => (
            <Card
              key={p.id}
              title={`${p.data.before_days} → ${p.data.after_days} days per week`}
              eyebrow={`PROPOSAL ${p.version}`}
              action={
                <Tag tone={p.data.status === "pending" ? "red" : "green"}>
                  {p.data.status}
                </Tag>
              }
            >
              <p>{p.data.reason}</p>
              <p className="muted">
                Preview week {Math.min(12, (p.data.plan.review_week ?? 0) + 1)}:{" "}
                {p.data.plan.weeks[
                  Math.min(11, p.data.plan.review_week ?? 0)
                ].sessions
                  .map((s) => `${s.day} · ${s.type} (${s.minutes}m)`)
                  .join("; ")}
                .{" "}
                {p.data.plan.continuation
                  ? "This version continues the existing cycle and retains earlier sessions."
                  : "Training plan will restart at week 1 as a new version."}
              </p>
              <details>
                <summary>Review full proposed prescription</summary>
                {p.data.plan.changes?.map((change, i) => (
                  <p key={i}>{change}</p>
                ))}
                <Note>
                  {p.data.plan.scheduling_note} {p.data.plan.limitations}
                </Note>
                {p.data.plan.weeks
                  .filter((w) => w.week > (p.data.plan.review_week ?? 0))
                  .map((w) => (
                    <section key={w.week}>
                      <h3>
                        Week {w.week} - {w.phase}
                        {w.deload ? " - deload and reassess" : ""}
                      </h3>
                      {w.sessions.map((s) => (
                        <div key={s.id}>
                          <h4>
                            {s.day}: {s.type}, {s.minutes} minutes, RPE{" "}
                            {s.effort}
                          </h4>
                          {s.exercises.map((ex) => (
                            <p key={ex.name}>
                              {ex.name}: {ex.sets} sets, {ex.reps}, rest{" "}
                              {ex.rest}, RPE {ex.rpe ?? s.effort}
                              {ex.suggested_load_kg != null
                                ? `; suggested load ${ex.suggested_load_kg} kg`
                                : ""}
                              . {ex.technique_focus} {ex.progression_rule}
                            </p>
                          ))}
                        </div>
                      ))}
                    </section>
                  ))}
              </details>
              {p.data.status === "pending" && (
                <div className="button-row">
                  <button
                    className="primary"
                    disabled={busy}
                    onClick={() =>
                      run(async () => {
                        await api(`/revisions/${p.id}/approve`, "POST");
                        await refresh();
                        await load();
                      })
                    }
                  >
                    <Check size={15} /> Approve & apply
                  </button>
                  <button
                    className="secondary"
                    disabled={busy}
                    onClick={() =>
                      run(async () => {
                        await api(`/revisions/${p.id}/reject`, "POST");
                        await load();
                      })
                    }
                  >
                    Reject
                  </button>
                </div>
              )}
            </Card>
          ))}
        </div>
      </div>
    </>
  );
}
