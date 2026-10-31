import SessionSecurity from "./components/SessionSecurity";
import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  CalendarDays,
  ChevronRight,
  Download,
  Dumbbell,
  Heart,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageSquare,
  Plus,
  Printer,
  Settings2,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Swords,
  Target,
  TrendingUp,
  Utensils,
  X,
} from "lucide-react";
import { lazy, Suspense, useEffect, useRef, useState } from "react";
import { api, ApiError } from "./api";
import Coach from "./components/Coach";

import NutritionPage from "./components/NutritionPage";

import Training from "./components/Training";
import { Card, Empty, Metric, Note, Tag } from "./components/ui";
import Wizard from "./components/Wizard";
import { useDialog } from "./components/useDialog";
import "./style.css";
import {
  Assessment,
  CheckIn,
  defaultProfile,
  Nutrition,
  Plan,
  Profile,
  Ranking,
  Saved,
  Workout,
} from "./types";
import { fmt } from "./utils";

const Comparison = lazy(() => import("./components/Comparison"));
const Progress = lazy(() => import("./components/Progress"));

type Page =
  | "Overview"
  | "Physical analysis"
  | "Fighting style"
  | "Comparison lab"
  | "Training"
  | "Nutrition"
  | "Progress"
  | "AI coach"
  | "Settings";
const nav: { label: Page; icon: typeof Activity }[] = [
  { label: "Overview", icon: LayoutDashboard },
  { label: "Physical analysis", icon: Activity },
  { label: "Fighting style", icon: Swords },
  { label: "Comparison lab", icon: SlidersHorizontal },
  { label: "Training", icon: Dumbbell },
  { label: "Nutrition", icon: Utensils },
  { label: "Progress", icon: TrendingUp },
  { label: "AI coach", icon: MessageSquare },
];
export default function App() {
  const pendingTasks = useRef(0);
  const [dataVersion, setDataVersion] = useState(0);
  const [ready, setReady] = useState(false),
    [account, setAccount] = useState(false),
    [profile, setProfile] = useState<Profile | null>(null),
    [page, setPage] = useState<Page>("Overview"),
    [assessment, setAssessment] = useState<Assessment | null>(null),
    [plan, setPlan] = useState<Saved<Plan> | null>(null),
    [nutrition, setNutrition] = useState<Saved<Nutrition> | null>(null),
    [checks, setChecks] = useState<Saved<CheckIn>[]>([]),
    [logs, setLogs] = useState<Saved<Workout>[]>([]),
    [rank, setRank] = useState<Ranking | null>(null),
    [wizard, setWizard] = useState(false),
    [mobile, setMobile] = useState(false),
    [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [busy, setBusy] = useState(false),
    [recovery, setRecovery] = useState(""),
    [restore, setRestore] = useState("");
  const [authOptions, setAuthOptions] = useState({
    managed_sign_in: false,
    local_registration: true,
    legacy_recovery: true,
  });
  useEffect(() => {
    api<typeof authOptions>("/auth/config")
      .then(setAuthOptions)
      .catch(() => {});
  }, []);
  const navigationDialog = useDialog(mobile, () => setMobile(false));
  useEffect(() => {
    const media = window.matchMedia("(max-width: 700px)");
    const close = () => {
      if (!media.matches) setMobile(false);
    };
    media.addEventListener("change", close);
    const opened = new Map<HTMLDetailsElement, boolean>();
    const beforePrint = () => {
      document
        .querySelectorAll<HTMLDetailsElement>("main details")
        .forEach((d) => {
          if (!opened.has(d)) opened.set(d, d.open);
          d.open = true;
        });
    };
    const afterPrint = () => {
      opened.forEach((open, d) => {
        d.open = open;
      });
      opened.clear();
    };
    window.addEventListener("beforeprint", beforePrint);
    window.addEventListener("afterprint", afterPrint);
    return () => {
      media.removeEventListener("change", close);
      window.removeEventListener("beforeprint", beforePrint);
      window.removeEventListener("afterprint", afterPrint);
      afterPrint();
    };
  }, []);
  async function refresh() {
    const p = await api<Profile>("/profile");
    setProfile(p);
    const results = await Promise.allSettled([
      api<Assessment>("/assessment"),
      api<Saved<Plan>>("/training-plans"),
      api<Saved<Nutrition> | null>("/nutrition"),
      api<Saved<CheckIn>[]>("/progress?limit=100"),
      api<Saved<Workout>[]>("/training-sessions?limit=100"),
      api<Ranking>("/fighter-matches", "POST", {
        physical: 60,
        background: 15,
        style: 10,
        stance: 5,
        weight_class: 10,
      }),
    ]);
    if (
      results.some(
        (r) =>
          r.status === "rejected" &&
          r.reason instanceof ApiError &&
          r.reason.status === 401,
      )
    ) {
      expireSession();
      return;
    }
    if (results[0].status === "fulfilled") setAssessment(results[0].value);
    if (results[1].status === "fulfilled") setPlan(results[1].value);
    if (results[2].status === "fulfilled") setNutrition(results[2].value);
    if (results[3].status === "fulfilled") setChecks(results[3].value);
    if (results[4].status === "fulfilled") setLogs(results[4].value);
    if (results[5].status === "fulfilled") setRank(results[5].value);
    setDataVersion((v) => v + 1);
    const failures = results.filter(
      (r, i) =>
        r.status === "rejected" &&
        !(i === 1 && r.reason instanceof ApiError && r.reason.status === 404),
    );
    if (failures.length)
      setError("Some dashboard data could not load. Refresh to retry.");
  }
  useEffect(() => {
    api<{ has_profile: boolean }>("/auth/session")
      .then(async (s) => {
        setAccount(true);
        if (s.has_profile) await refresh();
      })
      .catch((e: Error) => {
        if (e instanceof ApiError && e.status === 401) expireSession();
        else setError(e.message);
      })
      .finally(() => setReady(true));
  }, []);
  function expireSession() {
    setAccount(false);
    setProfile(null);
    setAssessment(null);
    setPlan(null);
    setNutrition(null);
    setChecks([]);
    setLogs([]);
    setRank(null);
    setRecovery("");
    setWizard(false);
    setMobile(false);
  }
  async function run(task: () => Promise<void>) {
    pendingTasks.current += 1;
    setBusy(true);
    setError("");
    try {
      await task();
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) expireSession();
      setError((e as Error).message);
    } finally {
      pendingTasks.current -= 1;
      setBusy(pendingTasks.current > 0);
    }
  }
  async function register(demo = false) {
    await run(async () => {
      const r = await api<{ recovery_token: string }>("/auth/register", "POST");
      setRecovery(r.recovery_token);
      setAccount(true);
      if (demo) {
        await api("/demo", "POST");
        await refresh();
      } else setWizard(true);
    });
  }
  const navigate = (p: Page) => {
    setPage(p);
    setMobile(false);
    window.scrollTo(0, 0);
  };
  const exportData = () =>
    run(async () => {
      const data = await api("/export");
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "mma-athlete-report.json";
      a.click();
      URL.revokeObjectURL(url);
    });
  const completed = plan
    ? logs.filter((l) => l.data.plan_id === plan.id).length
    : 0;
  if (!ready)
    return (
      <div className="loading" role="status" aria-live="polite">
        <Swords /> Loading your training workspace…
      </div>
    );
  return (
    <>
      <div className="app-shell">
        <aside
          ref={navigationDialog}
          id="workspace-navigation"
          className={mobile ? "sidebar open" : "sidebar"}
          role={mobile ? "dialog" : undefined}
          aria-modal={mobile ? true : undefined}
          aria-label="Workspace navigation"
        >
          <button
            className="icon-button mobile-nav-close"
            aria-label="Close navigation"
            onClick={() => setMobile(false)}
          >
            <X size={20} />
          </button>
          <a href="#" className="brand" onClick={() => navigate("Overview")}>
            <span className="brand-icon">
              <Swords size={24} />
            </span>
            <span>
              MMA<span className="brand-sub">PERFORMANCE COACH</span>
            </span>
          </a>
          <p className="nav-caption">YOUR WORKSPACE</p>
          <nav aria-label="Main navigation">
            {nav.map(({ label, icon: Icon }) => (
              <button
                key={label}
                className={`nav-item ${page === label ? "active" : ""}`}
                aria-current={page === label ? "page" : undefined}
                onClick={() => navigate(label)}
              >
                <Icon size={19} />
                {label}
                {label === "AI coach" && <span className="new-dot" />}
              </button>
            ))}
          </nav>
          <div className="sidebar-bottom">
            <div className="coach-mini">
              <span className="red-icon">
                <Sparkles size={19} />
              </span>
              <h3>A smarter corner.</h3>
              <p>
                Purposeful training.
                <br />
                Measurable progress.
              </p>
              <button onClick={() => navigate("AI coach")}>
                Meet your coach <ArrowRight size={15} />
              </button>
            </div>
            <button
              className={`nav-item ${page === "Settings" ? "active" : ""}`}
              onClick={() => navigate("Settings")}
            >
              <Settings2 size={18} /> Settings & data
            </button>
            <div className="athlete-mini">
              <span className="avatar">
                {profile?.name?.slice(0, 2).toUpperCase() || "AT"}
              </span>
              <div>
                <strong>{profile?.name || "Your athlete profile"}</strong>
                <small>
                  {profile?.is_demo ? "Demo athlete" : "Local workspace"}
                </small>
              </div>
            </div>
          </div>
        </aside>
        {mobile && (
          <button
            className="nav-scrim"
            aria-label="Close navigation backdrop"
            onClick={() => setMobile(false)}
          />
        )}
        <div className="main-shell">
          <header className="topbar">
            <div>
              <button
                className="icon-button mobile-toggle"
                aria-label="Toggle navigation"
                aria-controls="workspace-navigation"
                aria-expanded={mobile}
                onClick={() => setMobile(!mobile)}
              >
                <Menu size={22} />
              </button>
              <span className="breadcrumb">
                Workspace <ChevronRight size={13} /> <strong>{page}</strong>
              </span>
            </div>
            <div className="top-actions">
              <span className="local-status">
                <span /> Local workspace
              </span>
              <button
                className="icon-button"
                aria-label="Settings"
                onClick={() => navigate("Settings")}
              >
                <Settings2 size={18} />
              </button>
              <span className="avatar small">
                {profile?.name?.slice(0, 2).toUpperCase() || "AT"}
              </span>
            </div>
          </header>
          <main>
            {error && (
              <div role="alert" className="alert error">
                {error}
                <button aria-label="Dismiss error" onClick={() => setError("")}>
                  <X size={16} />
                </button>
              </div>
            )}
            {notice && (
              <div role="status" className="alert">
                {notice}
                <button
                  aria-label="Dismiss notification"
                  onClick={() => setNotice("")}
                >
                  <X size={16} />
                </button>
              </div>
            )}
            {recovery && (
              <div className="recovery">
                <ShieldCheck size={22} />
                <div>
                  <strong>Save your local account recovery token</strong>
                  <p>
                    This token grants access to your athlete data. Keep it
                    private. It is shown only once.
                  </p>
                  <code>{recovery}</code>
                </div>
                <button
                  onClick={() => setRecovery("")}
                  className="icon-button"
                  aria-label="Dismiss recovery token"
                >
                  <X size={18} />
                </button>
              </div>
            )}
            {!profile ? (
              <section className="welcome">
                <Tag tone="red">YOUR NEXT ROUND STARTS HERE</Tag>
                <h1>
                  Train with purpose.
                  <br />
                  <span>Build your complete game.</span>
                </h1>
                <p>
                  Your measurements, your experience, your goals. One connected
                  workspace for a sustainable MMA development journey.
                </p>
                <div className="welcome-actions">
                  <button
                    className="primary"
                    disabled={busy}
                    onClick={() =>
                      account
                        ? setWizard(true)
                        : authOptions.managed_sign_in
                          ? window.location.assign("/api/auth/oidc/login")
                          : register()
                    }
                  >
                    {!account && authOptions.managed_sign_in
                      ? "Sign in securely"
                      : "Build my athlete profile"}{" "}
                    <ArrowRight size={17} />
                  </button>
                  {!account && authOptions.local_registration && (
                    <button
                      className="secondary"
                      disabled={busy}
                      onClick={() => register(true)}
                    >
                      Explore the demo
                    </button>
                  )}
                </div>
                {!account &&
                  authOptions.managed_sign_in &&
                  authOptions.legacy_recovery && (
                    <Note>
                      Existing local profile? Restore its recovery token and
                      link managed sign-in from Settings before your first
                      managed sign-in. An unlinked provider identity creates a
                      separate account; it does not migrate your existing data.
                    </Note>
                  )}
                <div className="welcome-features">
                  <Metric
                    title="Know your baseline"
                    value="01"
                    detail="Explainable physical assessments"
                    icon={Activity}
                  />
                  <Metric
                    title="Make a plan"
                    value="12 weeks"
                    detail="Training, recovery and nutrition"
                    icon={CalendarDays}
                  />
                  <Metric
                    title="Find your direction"
                    value="Your game"
                    detail="Purposeful skill development"
                    icon={Target}
                  />
                </div>
                {!account && authOptions.legacy_recovery && (
                  <form
                    className="restore"
                    onSubmit={(e) => {
                      e.preventDefault();
                      run(async () => {
                        await api("/auth/restore", "POST", { token: restore });
                        setAccount(true);
                        const s = await api<{ has_profile: boolean }>(
                          "/auth/session",
                        );
                        if (s.has_profile) await refresh();
                      });
                    }}
                  >
                    <label htmlFor="restore">
                      Returning athlete? Restore with your private token
                    </label>
                    <div>
                      <input
                        id="restore"
                        type="password"
                        value={restore}
                        onChange={(e) => setRestore(e.target.value)}
                        required
                      />
                      <button className="secondary" disabled={busy}>
                        Restore account
                      </button>
                    </div>
                  </form>
                )}
              </section>
            ) : (
              <>
                <div className="page-heading">
                  <div>
                    <p className="eyebrow">
                      {profile.is_demo
                        ? "DEMO ATHLETE · SAMPLE INPUTS"
                        : "YOUR ATHLETE WORKSPACE"}
                    </p>
                    <h1>
                      {page === "Overview"
                        ? `Let's get better, ${profile.name.split(" ")[0]}.`
                        : page === "Comparison lab"
                          ? "Fighter comparison lab"
                          : page === "AI coach"
                            ? "Your corner. Always ready."
                            : page === "Training"
                              ? "The work behind the progress."
                              : page === "Nutrition"
                                ? "Fuel your development."
                                : page === "Progress"
                                  ? "Every session adds up."
                                  : page === "Settings"
                                    ? "Your profile. Your data."
                                    : page === "Fighting style"
                                      ? "Build your complete game."
                                      : "Understand your baseline."}
                    </h1>
                    <p>
                      {page === "Overview"
                        ? "A clear picture of where you are. A focused plan for what’s next."
                        : page === "Comparison lab"
                          ? "Explore physical resemblance. Learn from different approaches."
                          : page === "Training"
                            ? "A progressive 12-week roadmap, built around your availability."
                            : page === "Nutrition"
                              ? "Estimated fueling, source-backed portions and reviewed changes."
                              : page === "Progress"
                                ? "Track consistent measurements and reassess with context."
                                : page === "AI coach"
                                  ? "Context from your saved profile. Guidance you can understand."
                                  : "Evidence, context and a clear next step."}
                    </p>
                  </div>
                  <div className="heading-actions">
                    {page === "Overview" && (
                      <button
                        className="secondary"
                        onClick={() => setWizard(true)}
                      >
                        <Settings2 size={15} /> Edit profile
                      </button>
                    )}
                    <button
                      className="secondary"
                      onClick={() => window.print()}
                      title="Print this view or save it as a PDF in the print dialog"
                    >
                      <Printer size={15} /> Print report
                    </button>
                  </div>
                </div>
                {page === "Overview" && (
                  <>
                    <div className="overview-grid">
                      <section className="hero">
                        <div className="hero-lines" />
                        <Tag tone="red">YOUR DEVELOPMENT. YOUR PACE.</Tag>
                        <h2>
                          Train with intention.
                          <br />
                          Come back stronger.
                        </h2>
                        <p>
                          {profile.goal}. A foundation of skill, strength
                          <br className="desktop" /> and consistent work.
                        </p>
                        <button
                          className="primary"
                          onClick={() => navigate("Training")}
                        >
                          View your training plan <ArrowRight size={16} />
                        </button>
                        <div className="hero-footer">
                          <span>
                            <span className="status-dot" />{" "}
                            {plan
                              ? "12-week plan active"
                              : "Ready to build your plan"}
                          </span>
                          <span>
                            Built around you <ShieldCheck size={14} />
                          </span>
                        </div>
                        <div className="octagon-art">
                          <div />
                          <Swords size={95} strokeWidth={1} />
                          <span>
                            SHOW UP.
                            <br />
                            BUILD YOUR GAME.
                          </span>
                        </div>
                      </section>
                      <Card
                        title="Your athlete profile"
                        eyebrow="THE BASELINE"
                        action={
                          <button
                            className="text-button"
                            onClick={() => navigate("Physical analysis")}
                            aria-label="View physical analysis"
                          >
                            <ArrowUpRight size={19} />
                          </button>
                        }
                        className="profile-card"
                      >
                        <div className="profile-name">
                          <span className="avatar large">
                            {profile.name.slice(0, 2).toUpperCase()}
                          </span>
                          <div>
                            <h3>{profile.name}</h3>
                            <p>
                              {profile.age} years ·{" "}
                              {profile.stance === "Unknown"
                                ? "Stance unrecorded"
                                : profile.stance}
                            </p>
                          </div>
                        </div>
                        <div className="profile-stats">
                          <div>
                            <small>HEIGHT</small>
                            <strong>
                              {fmt(profile.height_cm)} <em>cm</em>
                            </strong>
                          </div>
                          <div>
                            <small>WEIGHT</small>
                            <strong>
                              {fmt(profile.weight_kg)} <em>kg</em>
                            </strong>
                          </div>
                          <div>
                            <small>WINGSPAN</small>
                            <strong>
                              {fmt(profile.wingspan_cm)}{" "}
                              <em>{profile.wingspan_cm ? "cm" : ""}</em>
                            </strong>
                          </div>
                        </div>
                        <div className="division-row">
                          <span>Scale-weight reference</span>
                          <Tag>
                            {assessment?.weight.scale_reference || "Loading"}
                          </Tag>
                        </div>
                        <small className="muted">
                          Everyday weight comparison · not weigh-in eligibility
                        </small>
                      </Card>
                    </div>
                    <div className="metric-grid">
                      <Metric
                        title="Weekly availability"
                        value={`${profile.days} days`}
                        detail={`Up to ${profile.minutes} minutes per day`}
                        icon={CalendarDays}
                      />
                      <Metric
                        title="Sessions logged"
                        value={`${completed}`}
                        detail="In your active 12-week plan"
                        icon={Dumbbell}
                      />
                      <Metric
                        title="Sleep baseline"
                        value={`${profile.sleep} h`}
                        detail="Self-reported typical duration"
                        icon={Heart}
                      />
                      <Metric
                        title="Current focus"
                        value={profile.priority}
                        detail="Sustainable, progressive development"
                        icon={Target}
                      />
                    </div>
                    <div className="two-column">
                      <Card
                        title="Your training week"
                        eyebrow="THE GAME PLAN"
                        action={
                          <button
                            className="text-button"
                            onClick={() => navigate("Training")}
                          >
                            Full plan <ArrowRight size={14} />
                          </button>
                        }
                      >
                        {plan?.data.available === false ? (
                          <Note>{plan.data.reason}</Note>
                        ) : plan ? (
                          <>
                            <div className="week-label">
                              <Tag tone="red">
                                Week{" "}
                                {Math.min(12, (plan.data.review_week ?? 0) + 1)}
                              </Tag>
                              <span>
                                {
                                  plan.data.weeks[
                                    Math.min(11, plan.data.review_week ?? 0)
                                  ].phase
                                }{" "}
                                phase
                              </span>
                              <small>
                                {plan.data.days} sessions ·{" "}
                                {plan.data.weeks[
                                  Math.min(11, plan.data.review_week ?? 0)
                                ].sessions.reduce(
                                  (s, x) => s + x.minutes,
                                  0,
                                )}{" "}
                                min
                              </small>
                            </div>
                            <div className="schedule-preview">
                              {[
                                "Monday",
                                "Tuesday",
                                "Wednesday",
                                "Thursday",
                                "Friday",
                                "Saturday",
                                "Sunday",
                              ].map((day) => {
                                const s = plan.data.weeks[
                                  Math.min(11, plan.data.review_week ?? 0)
                                ].sessions.find((x) => x.day === day);
                                return (
                                  <div
                                    key={day}
                                    className={
                                      s ? "schedule-day" : "schedule-day rest"
                                    }
                                  >
                                    <span>{day.slice(0, 3)}</span>
                                    <div
                                      className={`schedule-icon ${s?.type === "Technique" ? "purple" : s?.type === "Conditioning" ? "green" : ""}`}
                                    >
                                      {s ? (
                                        <Dumbbell size={17} />
                                      ) : (
                                        <Heart size={17} />
                                      )}
                                    </div>
                                    <strong>{s?.type || "Recovery"}</strong>
                                    <small>
                                      {s ? `${s.minutes} min` : "Rest & reset"}
                                    </small>
                                  </div>
                                );
                              })}
                            </div>
                          </>
                        ) : (
                          <Empty>
                            <p>No plan generated yet.</p>
                            <button
                              className="primary"
                              onClick={() =>
                                run(async () => {
                                  await api("/training-plans", "POST");
                                  await refresh();
                                })
                              }
                            >
                              Generate my plan
                            </button>
                          </Empty>
                        )}
                      </Card>
                      <Card
                        title="From your corner"
                        eyebrow="COACHING INSIGHTS"
                        action={<Sparkles size={18} className="red-text" />}
                      >
                        <div className="insight">
                          <span className="insight-number">01</span>
                          <div>
                            <h3>Build a balanced foundation</h3>
                            <p>{assessment?.style.evidence}</p>
                          </div>
                        </div>
                        <div className="insight">
                          <span className="insight-number">02</span>
                          <div>
                            <h3>Consistency before intensity</h3>
                            <p>
                              Use your {profile.days} available days to practice
                              quality movement. Leave room for recovery.
                            </p>
                          </div>
                        </div>
                        <button
                          className="text-button"
                          onClick={() => navigate("AI coach")}
                        >
                          Talk to your coach <ArrowRight size={15} />
                        </button>
                      </Card>
                    </div>
                    <div className="two-column">
                      <Card
                        title="Fighters to study"
                        eyebrow="PHYSICAL RESEMBLANCE"
                        action={
                          <button
                            className="text-button"
                            onClick={() => navigate("Comparison lab")}
                          >
                            Open lab <ArrowRight size={14} />
                          </button>
                        }
                      >
                        {rank?.matches.length ? (
                          <div className="mini-fighters">
                            {rank.matches.map((m, i) => (
                              <button
                                key={m.fighter.id}
                                onClick={() => navigate("Comparison lab")}
                              >
                                <span className="fighter-initial">
                                  0{i + 1}
                                </span>
                                <div>
                                  <strong>{m.fighter.name}</strong>
                                  <small>{m.fighter.division}</small>
                                </div>
                                <span>
                                  {m.score}
                                  <small> / 100</small>
                                </span>
                              </button>
                            ))}
                          </div>
                        ) : (
                          <Empty>
                            No defensible matches in this development dataset.
                          </Empty>
                        )}
                        <small className="muted">
                          Heuristic resemblance · not skill or potential · dated
                          development snapshots
                        </small>
                      </Card>
                      <Card
                        title="Fuel for the work"
                        eyebrow="NUTRITION"
                        action={<Utensils size={18} className="red-text" />}
                      >
                        {nutrition?.data.available ? (
                          <>
                            <div className="nutrition-preview">
                              <strong>
                                {nutrition.data.estimated_maintenance?.toLocaleString()}
                                <small>kcal / day</small>
                              </strong>
                              <Tag>Maintenance estimate</Tag>
                            </div>
                            <p className="muted">
                              An estimated starting point. Actual needs vary
                              with your training, health and recovery.
                            </p>
                          </>
                        ) : (
                          <p className="muted">
                            {nutrition?.data.reason ||
                              "Build a seven-day maintenance meal template from your saved profile."}
                          </p>
                        )}
                        <button
                          className="text-button"
                          onClick={() => navigate("Nutrition")}
                        >
                          View nutrition <ArrowRight size={15} />
                        </button>
                      </Card>
                    </div>
                    <Note>
                      Recommendations combine user-reported inputs,
                      deterministic calculations and conservative templates.
                      They do not assess professional fighting potential.
                      Independent professional review is pending; automated
                      checks are not expert approval. Templates do not establish
                      medical clearance or nutritional completeness.
                    </Note>
                  </>
                )}
                {page === "Physical analysis" && assessment && (
                  <>
                    <div className="metric-grid">
                      <Metric
                        title="BMI"
                        value={fmt(assessment.physical.bmi)}
                        detail="Weight ÷ height² · screening ratio"
                        icon={Activity}
                      />
                      <Metric
                        title="Ape index"
                        value={fmt(assessment.physical.ape_index_cm, " cm")}
                        detail="Wingspan minus height"
                        icon={ArrowUpRight}
                      />
                      <Metric
                        title="Reach / height"
                        value={fmt(assessment.physical.reach_ratio)}
                        detail="Wingspan is not standing reach"
                        icon={Swords}
                      />
                      <Metric
                        title="Estimated lean mass"
                        value={fmt(assessment.physical.lean_mass_kg, " kg")}
                        detail="Weight × (1 − reported body fat)"
                        icon={Dumbbell}
                      />
                    </div>
                    <div className="two-column">
                      <Card title="What your inputs support">
                        <h3>Potential advantages</h3>
                        {assessment.physical.strengths.length ? (
                          assessment.physical.strengths.map((x) => (
                            <p key={x} className="bullet">
                              {x}
                            </p>
                          ))
                        ) : (
                          <p className="muted">
                            More measurements and benchmarks are needed before
                            reporting physical advantages.
                          </p>
                        )}
                        <h3>Confidence & missing evidence</h3>
                        {assessment.physical.missing.map((x) => (
                          <p key={x} className="bullet">
                            {x}
                          </p>
                        ))}
                        <Note>{assessment.physical.provenance}</Note>
                        <button
                          className="secondary"
                          onClick={() => setWizard(true)}
                        >
                          Update measurements
                        </button>
                      </Card>
                      <Card
                        title="Weight-class reference"
                        eyebrow={
                          profile.division.toUpperCase() + "’S DIVISIONS"
                        }
                      >
                        <div className="division-big">
                          {assessment.weight.scale_reference}
                        </div>
                        <p>
                          {assessment.weight.everyday_kg} kg /{" "}
                          {assessment.weight.everyday_lb} lb everyday weight
                        </p>
                        <table>
                          <thead>
                            <tr>
                              <th>Division</th>
                              <th>Title limit</th>
                              <th>Typical non-title</th>
                            </tr>
                          </thead>
                          <tbody>
                            {assessment.weight.rows.map((r) => (
                              <tr
                                key={r.name}
                                className={
                                  r.name === assessment.weight.scale_reference
                                    ? "highlight-row"
                                    : ""
                                }
                              >
                                <td>
                                  {r.name}
                                  {!r.active && " (historical)"}
                                </td>
                                <td>{r.title_lb} lb</td>
                                <td>{r.non_title_lb} lb</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                        <p className="muted">{assessment.weight.note}</p>
                        <a
                          className="source"
                          href={assessment.weight.source}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Official UFC reference · verified{" "}
                          {assessment.weight.verified_at} ↗
                        </a>
                      </Card>
                    </div>
                    <Card title="Sustainable weight guidance">
                      <p>{assessment.weight.target}</p>
                      <Note>{assessment.weight.guidance}</Note>
                    </Card>
                    <Card
                      title="Athletic benchmarks"
                      action={
                        <button
                          className="secondary"
                          onClick={() => setWizard(true)}
                        >
                          <Plus size={15} /> Add benchmark
                        </button>
                      }
                    >
                      {profile.benchmarks.length ? (
                        <table>
                          <thead>
                            <tr>
                              <th>Benchmark</th>
                              <th>Result</th>
                              <th>Repetitions</th>
                              <th>Effort</th>
                              <th>Evidence</th>
                            </tr>
                          </thead>
                          <tbody>
                            {profile.benchmarks.map((b, i) => (
                              <tr key={i}>
                                <td>{b.name}</td>
                                <td>
                                  {b.value} {b.unit}
                                </td>
                                <td>{b.reps}</td>
                                <td>{b.effort}/10</td>
                                <td>{b.provenance}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      ) : (
                        <Empty>
                          No benchmarks recorded. Missing results are never
                          treated as zero.
                        </Empty>
                      )}
                    </Card>
                  </>
                )}
                {page === "Fighting style" && assessment && (
                  <>
                    <Card
                      title={assessment.style.direction}
                      eyebrow="EXPLORATORY DEVELOPMENT DIRECTION"
                    >
                      <p>{assessment.style.evidence}</p>
                      <Note>{assessment.style.limitation}</Note>
                    </Card>
                    <div className="two-column">
                      {assessment.style.priorities.map((x) => (
                        <Card
                          key={x.discipline}
                          title={x.discipline}
                          eyebrow={`PRIORITY 0${x.priority}`}
                        >
                          <p>{x.purpose}</p>
                          <div className="detail-line">
                            <CalendarDays size={16} />
                            {x.frequency}
                          </div>
                          <div className="detail-line">
                            <ShieldCheck size={16} />
                            {x.access}
                          </div>
                          <p className="muted">
                            {profile.experience.find(
                              (e) => e.discipline === x.discipline,
                            )?.level || "No experience recorded"}{" "}
                            · Adapt complexity with your instructor; establish
                            fundamentals before live resistance.
                          </p>
                        </Card>
                      ))}
                    </div>
                    <Card title="Directions to explore">
                      <div className="tags">
                        {assessment.style.opportunities.map((x) => (
                          <Tag key={x}>{x}</Tag>
                        ))}
                      </div>
                      <p className="muted">
                        Discuss tactics with a coach using observed technical
                        ability. Physique alone does not select your fighting
                        style.
                      </p>
                    </Card>
                  </>
                )}
                {page === "Comparison lab" && (
                  <Suspense
                    fallback={
                      <div className="empty" role="status">
                        Loading analytics?
                      </div>
                    }
                  >
                    <Comparison
                      profile={profile}
                      run={run}
                      busy={busy}
                      notify={setNotice}
                    />
                  </Suspense>
                )}
                {page === "Training" && (
                  <Training
                    plan={plan}
                    logs={logs}
                    run={run}
                    refresh={refresh}
                    busy={busy}
                  />
                )}
                {page === "Nutrition" && (
                  <NutritionPage
                    nutrition={nutrition}
                    profile={profile}
                    run={run}
                    refresh={refresh}
                    busy={busy}
                  />
                )}
                {page === "Progress" && (
                  <Suspense
                    fallback={
                      <div className="empty" role="status">
                        Loading analytics?
                      </div>
                    }
                  >
                    <Progress
                      dataVersion={dataVersion}
                      profile={profile}
                      checks={checks}
                      logs={logs}
                      plan={plan}
                      run={run}
                      refresh={refresh}
                      notify={setNotice}
                      busy={busy}
                    />
                  </Suspense>
                )}
                {page === "AI coach" && (
                  <Coach plan={plan} run={run} refresh={refresh} busy={busy} />
                )}
                {page === "Settings" && (
                  <>
                    <SessionSecurity run={run} busy={busy} />
                    <Card title="Athlete profile">
                      <div className="settings-row">
                        <div>
                          <h3>{profile.name}</h3>
                          <p className="muted">
                            Edit your measurements, training history,
                            preferences and goals.
                          </p>
                        </div>
                        <button
                          className="secondary"
                          onClick={() => setWizard(true)}
                        >
                          Edit assessment
                        </button>
                      </div>
                      <Note>
                        Editing your profile does not silently replace your
                        active plan. Generate a proposal in AI Coach to review
                        and approve a new plan. Regenerate nutrition separately
                        when dietary needs change.
                      </Note>
                    </Card>
                    <Card title="Data & privacy">
                      <p className="muted">
                        Profiles, plans, logs and conversations are stored in
                        the application database. Optional AI receives only a
                        reduced coaching context and your question. Avoid
                        including identifying or medical information in chat.
                      </p>
                      <div className="button-row">
                        <button className="secondary" onClick={exportData}>
                          <Download size={16} /> Download all data
                        </button>
                        <button
                          className="secondary"
                          onClick={() =>
                            run(async () => {
                              await api("/auth/logout", "POST");
                              window.location.reload();
                            })
                          }
                        >
                          <LogOut size={16} /> Sign out
                        </button>
                      </div>
                    </Card>
                    <Card title="Delete application account">
                      <p>
                        Delete your profile and all associated plans, logs,
                        comparisons and conversations. This cannot be undone.
                        Your identity-provider account is managed separately;
                        deleting application data does not delete that account.
                      </p>
                      <button
                        className="danger"
                        onClick={() => {
                          if (
                            window.confirm(
                              "Permanently delete this account and all its data?",
                            )
                          )
                            run(async () => {
                              await api("/account", "DELETE");
                              window.location.reload();
                            });
                        }}
                      >
                        Delete my account and data
                      </button>
                    </Card>
                  </>
                )}
              </>
            )}
            <footer>
              <span>
                <Swords size={13} /> MMA PERFORMANCE COACH
              </span>
              <span>
                Built for the work. Independent platform · No UFC affiliation.
              </span>
              <span>Evidence before assumptions.</span>
            </footer>
          </main>
        </div>
      </div>
      {wizard && (
        <Wizard
          initial={profile || defaultProfile}
          onClose={() => setWizard(false)}
          onSave={async (p) => {
            await api("/profile", "PUT", p);
            if (!plan) await api("/training-plans", "POST");
            if (!nutrition) await api("/nutrition", "POST");
            await refresh();
            setWizard(false);
            setNotice(
              "Athlete profile saved. Active plans retain their original input version.",
            );
          }}
        />
      )}
    </>
  );
}
