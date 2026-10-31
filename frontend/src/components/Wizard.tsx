import { ArrowRight, Check, ChevronLeft, X } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../api";
import { Profile } from "../types";
import { disciplines, goals } from "../utils";
import BenchmarkEditor from "./BenchmarkEditor";
import { Note } from "./ui";
import { useDialog } from "./useDialog";
export default function Wizard({
  initial,
  onClose,
  onSave,
}: {
  initial: Profile;
  onClose: () => void;
  onSave: (p: Profile) => Promise<void>;
}) {
  const dialog = useDialog(true, onClose);
  const [p, setP] = useState<Profile>({ ...initial }),
    [step, setStep] = useState(0),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [saved, setSaved] = useState(false);
  const titles = [
    "The person behind the athlete",
    "Your physical baseline",
    "Your martial arts experience",
    "Strength & athletic background",
    "Lifestyle & recovery",
    "Your development goals",
  ];
  useEffect(() => {
    if (!initial.name)
      api<Profile | null>("/profile/draft")
        .then((d) => {
          if (d) setP(d);
        })
        .catch(() =>
          setError(
            "Saved draft could not be restored. Retry before replacing a draft you need.",
          ),
        );
  }, []);
  const update = <K extends keyof Profile>(key: K, value: Profile[K]) => {
    setP((prev) => ({ ...prev, [key]: value }));
    setSaved(false);
  };
  const field = (
    key: keyof Profile,
    label: string,
    min: number,
    max: number,
    optional = false,
    increment = "0.1",
  ) => {
    const imperial =
      p.units === "imperial" &&
      (String(key).endsWith("_cm") || key === "weight_kg");
    const factor = key === "weight_kg" ? 2.2046226218 : 1 / 2.54;
    const value = p[key];
    const shown =
      typeof value === "number" && imperial
        ? Number((value * factor).toFixed(2))
        : value;
    return (
      <label key={key}>
        {label
          .replace("(cm)", imperial ? "(in)" : "(cm)")
          .replace("(kg)", imperial ? "(lb)" : "(kg)")}
        {optional && <small>Optional</small>}
        <input
          type="number"
          min={imperial ? Number((min * factor).toFixed(2)) : min}
          max={imperial ? Number((max * factor).toFixed(2)) : max}
          step={increment === "1" ? "1" : "any"}
          required={!optional}
          value={shown == null ? "" : String(shown)}
          onChange={(e) =>
            update(
              key,
              (e.target.value === "" && optional
                ? null
                : imperial
                  ? Number((+e.target.value / factor).toFixed(4))
                  : +e.target.value) as never,
            )
          }
        />
      </label>
    );
  };
  const select = (key: keyof Profile, label: string, options: string[]) => (
    <label>
      {label}
      <select
        value={String(p[key])}
        onChange={(e) => update(key, e.target.value as never)}
      >
        {options.map((o) => (
          <option key={o}>{o}</option>
        ))}
      </select>
    </label>
  );
  const check = (key: keyof Profile, label: string) => (
    <label className="checkbox">
      <input
        type="checkbox"
        checked={Boolean(p[key])}
        onChange={(e) => update(key, e.target.checked as never)}
      />
      {label}
    </label>
  );
  const toggle = (key: "diet" | "preferred" | "objectives", value: string) =>
    update(
      key,
      p[key].includes(value)
        ? p[key].filter((x) => x !== value)
        : [...p[key], value],
    );
  const save = async (final = false) => {
    setBusy(true);
    setError("");
    try {
      if (final) await onSave({ ...p, is_demo: false });
      else {
        await api("/profile/draft", "PUT", p);
        setSaved(true);
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };
  return (
    <div className="modal-backdrop">
      <section
        ref={dialog}
        className="modal wizard"
        role="dialog"
        aria-modal="true"
        aria-labelledby="wizard-title"
      >
        <button
          type="button"
          className="modal-close icon-button"
          aria-label="Close assessment"
          onClick={onClose}
        >
          <X />
        </button>
        <p className="eyebrow">ATHLETE ASSESSMENT · STEP {step + 1} OF 6</p>
        <h2 id="wizard-title">{titles[step]}</h2>
        {initial.name && (
          <button
            type="button"
            className="secondary"
            disabled={busy}
            onClick={async () => {
              setBusy(true);
              setError("");
              try {
                const draft = await api<Profile | null>("/profile/draft");
                if (draft) {
                  setP(draft);
                  setStep(0);
                  setSaved(false);
                } else setError("No newer saved draft is available.");
              } catch (e) {
                setError((e as Error).message);
              } finally {
                setBusy(false);
              }
            }}
          >
            Resume saved draft
          </button>
        )}
        <p className="muted">
          Your inputs guide recommendations. Optional measurements can be left
          blank.
        </p>
        <div className="wizard-steps">
          {titles.map((t, i) => (
            <button
              key={t}
              type="button"
              aria-label={`Go to step ${i + 1}`}
              className={i <= step ? "active" : ""}
              onClick={() => setStep(i)}
            >
              {i < step ? <Check size={14} /> : i + 1}
            </button>
          ))}
        </div>
        {error && (
          <p className="red-text" role="alert">
            {error}
          </p>
        )}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (step < 5) setStep(step + 1);
            else save(true);
          }}
        >
          {step === 0 && (
            <div className="form-grid">
              <label>
                Name
                <input
                  required
                  minLength={1}
                  maxLength={80}
                  value={p.name}
                  onChange={(e) => update("name", e.target.value)}
                />
              </label>
              {field("age", "Age", 13, 90, false, "1")}
              {select("division", "Competition division", ["Men", "Women"])}
              {select("metabolic_sex", "Metabolic equation input (optional)", [
                "unspecified",
                "male",
                "female",
              ])}
              {select("units", "Measurement units", ["metric", "imperial"])}
              {field("height_cm", "Height (cm)", 120, 240)}
              {field("weight_kg", "Everyday weight (kg)", 30, 250)}
              {select("dominant_hand", "Dominant hand", [
                "Right",
                "Left",
                "Ambidextrous",
              ])}
              {select("stance", "Stance", [
                "Unknown",
                "Orthodox",
                "Southpaw",
                "Switch",
              ])}
              <label>
                Country (optional)
                <input
                  maxLength={80}
                  value={p.country}
                  onChange={(e) => update("country", e.target.value)}
                />
              </label>
              <div className="full">
                {select("goal", "Primary objective", goals)}
              </div>
            </div>
          )}
          {step === 1 && (
            <>
              <div className="form-grid">
                {field("wingspan_cm", "Total wingspan (cm)", 100, 260, true)}
                {field(
                  "standing_reach_cm",
                  "Standing reach (cm)",
                  100,
                  330,
                  true,
                )}
                {field("leg_cm", "Leg length (cm)", 30, 150, true)}
                {field("arm_cm", "Arm length (cm)", 20, 120, true)}
                {field("waist_cm", "Waist circumference (cm)", 40, 220, true)}
                {field("hip_cm", "Hip circumference (cm)", 40, 220, true)}
                {field("shoulder_cm", "Shoulder width (cm)", 20, 100, true)}
                {field("neck_cm", "Neck circumference (cm)", 20, 70, true)}
                {field("body_fat", "Body fat (%)", 5, 60, true)}
                {field(
                  "resting_hr",
                  "Resting heart rate (bpm)",
                  30,
                  150,
                  true,
                  "1",
                )}
              </div>
              <Note>
                Wingspan is fingertip-to-fingertip. Standing reach is
                floor-to-fingertip overhead. They are different measurements.
                Self-reported body fat is an estimate.
              </Note>
            </>
          )}
          {step === 2 && (
            <>
              <p className="muted">
                Choose each discipline you have practiced or would like to
                learn. Experience remains self-reported.
              </p>
              <div className="discipline-choices">
                {disciplines.map((d) => (
                  <button
                    className={
                      p.experience.some((e) => e.discipline === d)
                        ? "selected"
                        : ""
                    }
                    key={d}
                    type="button"
                    onClick={() =>
                      update(
                        "experience",
                        p.experience.some((e) => e.discipline === d)
                          ? p.experience.filter((e) => e.discipline !== d)
                          : [
                              ...p.experience,
                              {
                                discipline: d,
                                level: "None",
                                months: 0,
                                sessions: 0,
                                instructor: false,
                                competition: false,
                                strengths: "",
                                weaknesses: "",
                                interested: true,
                              },
                            ],
                      )
                    }
                  >
                    {d}
                  </button>
                ))}
              </div>
              {p.experience.map((ex, index) => {
                const edit = (key: string, value: unknown) =>
                  update(
                    "experience",
                    p.experience.map((v, j) =>
                      j === index ? { ...v, [key]: value } : v,
                    ),
                  );
                return (
                  <div className="experience-block" key={ex.discipline}>
                    <h3>{ex.discipline}</h3>
                    <div className="form-grid">
                      <label>
                        Experience level
                        <select
                          value={ex.level}
                          onChange={(e) => edit("level", e.target.value)}
                        >
                          {[
                            "None",
                            "Beginner",
                            "Novice",
                            "Intermediate",
                            "Advanced",
                            "Competitive",
                          ].map((x) => (
                            <option key={x}>{x}</option>
                          ))}
                        </select>
                      </label>
                      <label>
                        Months practiced
                        <input
                          type="number"
                          min="0"
                          max="900"
                          required
                          value={ex.months}
                          onChange={(e) => edit("months", +e.target.value)}
                        />
                      </label>
                      <label>
                        Sessions / week
                        <input
                          type="number"
                          min="0"
                          max="14"
                          required
                          value={ex.sessions}
                          onChange={(e) => edit("sessions", +e.target.value)}
                        />
                      </label>
                      <div>
                        <label className="checkbox">
                          <input
                            type="checkbox"
                            checked={ex.instructor}
                            onChange={(e) =>
                              edit("instructor", e.target.checked)
                            }
                          />
                          Instructor access
                        </label>
                        <label className="checkbox">
                          <input
                            type="checkbox"
                            checked={ex.competition}
                            onChange={(e) =>
                              edit("competition", e.target.checked)
                            }
                          />
                          Competition experience
                        </label>
                        <label className="checkbox">
                          <input
                            type="checkbox"
                            checked={ex.interested}
                            onChange={(e) =>
                              edit("interested", e.target.checked)
                            }
                          />
                          Interested in developing
                        </label>
                      </div>
                      <label>
                        Self-assessed strengths
                        <input
                          maxLength={500}
                          value={ex.strengths}
                          onChange={(e) => edit("strengths", e.target.value)}
                        />
                      </label>
                      <label>
                        Self-assessed gaps
                        <input
                          maxLength={500}
                          value={ex.weaknesses}
                          onChange={(e) => edit("weaknesses", e.target.value)}
                        />
                      </label>
                      <label>
                        Technical goals for {ex.discipline}
                        <input
                          maxLength={300}
                          value={ex.technical_goals ?? ""}
                          onChange={(e) =>
                            edit("technical_goals", e.target.value)
                          }
                        />
                      </label>
                      <label>
                        Enjoyment (1–5, optional)
                        <input
                          type="number"
                          min="1"
                          max="5"
                          value={ex.enjoyment ?? ""}
                          onChange={(e) =>
                            edit(
                              "enjoyment",
                              e.target.value === "" ? null : +e.target.value,
                            )
                          }
                        />
                      </label>
                    </div>
                  </div>
                );
              })}
            </>
          )}
          {step === 3 && (
            <>
              <label className="checkbox">
                <input
                  type="checkbox"
                  checked={p.strength_coach ?? false}
                  onChange={(e) => update("strength_coach", e.target.checked)}
                />
                Access to a qualified strength and conditioning coach
              </label>
              <label className="checkbox">
                <input
                  type="checkbox"
                  checked={p.power_practice ?? false}
                  onChange={(e) => update("power_practice", e.target.checked)}
                />
                Request supervised explosive practice when appropriate
              </label>
              <div className="form-grid">
                {field("gym_years", "Years of strength training", 0, 70)}
                {field(
                  "current_frequency",
                  "Current workouts per week",
                  0,
                  14,
                  false,
                  "1",
                )}
                {field(
                  "workout_minutes",
                  "Typical workout (minutes)",
                  15,
                  180,
                  false,
                  "1",
                )}
                {select("mobility", "Mobility self-assessment", [
                  "Unknown",
                  "Limited",
                  "Comfortable",
                ])}
              </div>
              <BenchmarkEditor
                values={p.benchmarks}
                onChange={(v) => update("benchmarks", v)}
              />
              <Note>
                Use existing comfortable results. This assessment does not ask
                you to perform maximal lifts or exhaustive tests.
              </Note>
            </>
          )}
          {step === 4 && (
            <>
              <fieldset>
                <legend>Exact available weekdays (optional)</legend>
                <p>
                  Leave all unchecked for a template calendar. The day-count cap
                  still applies.
                </p>
                {[
                  "Monday",
                  "Tuesday",
                  "Wednesday",
                  "Thursday",
                  "Friday",
                  "Saturday",
                  "Sunday",
                ].map((day) => (
                  <label className="checkbox" key={day}>
                    <input
                      type="checkbox"
                      checked={p.available_days?.includes(day) ?? false}
                      onChange={(e) => {
                        const days = e.target.checked
                          ? [...(p.available_days ?? []), day]
                          : (p.available_days ?? []).filter((d) => d !== day);
                        update("available_days", days.length ? days : null);
                      }}
                    />
                    {day}
                  </label>
                ))}
              </fieldset>
              <div className="form-grid">
                {field(
                  "days",
                  "Available training days per week",
                  1,
                  6,
                  false,
                  "1",
                )}
                {field(
                  "minutes",
                  "Maximum daily training minutes",
                  20,
                  180,
                  false,
                  "1",
                )}
                {field("sleep", "Typical sleep (hours)", 2, 12)}
                {select("activity", "Daily activity", [
                  "low",
                  "moderate",
                  "high",
                ])}
                {select("budget", "Food budget", [
                  "Low",
                  "Moderate",
                  "Flexible",
                ])}
                <label>
                  Food preferences
                  <input
                    maxLength={500}
                    value={p.food_preferences}
                    onChange={(e) => update("food_preferences", e.target.value)}
                  />
                </label>
                <label>
                  Food allergies (comma separated)
                  <input
                    maxLength={300}
                    value={p.allergies.join(", ")}
                    onChange={(e) =>
                      update(
                        "allergies",
                        e.target.value.split(",").map((v) => v.trim()),
                      )
                    }
                  />
                </label>
                <label>
                  Recovery concerns
                  <input
                    maxLength={500}
                    value={p.recovery}
                    onChange={(e) => update("recovery", e.target.value)}
                  />
                </label>
                <label className="full">
                  Injury or training limitations (optional)
                  <textarea
                    maxLength={1000}
                    value={p.limitations}
                    onChange={(e) => update("limitations", e.target.value)}
                  />
                </label>
              </div>
              <div className="check-grid">
                {check("gym", "Commercial gym access")}
                {check("mma_gym", "MMA gym access")}
                {check("boxing_equipment", "Boxing equipment")}
                {check("partners", "Grappling partners")}
                {check(
                  "clinical_nutrition",
                  "Clinical nutrition needs, pregnancy/breastfeeding or eating-disorder concerns (withhold targets)",
                )}
              </div>
              <h3>Dietary restrictions</h3>
              <label>
                Conditioning preference
                <select
                  aria-label="Conditioning preference"
                  value={p.conditioning_mode ?? "auto"}
                  onChange={(e) => update("conditioning_mode", e.target.value)}
                >
                  {Object.entries({
                    auto: "Choose from available equipment",
                    walking: "Walking",
                    cycling: "Cycling",
                    rowing: "Rowing",
                    run_walk: "Run / walk",
                    jump_rope: "Jump rope",
                    interval_cycling: "Controlled cycling intervals",
                  }).map(([key, name]) => (
                    <option key={key} value={key}>
                      {name}
                    </option>
                  ))}
                </select>
              </label>
              <fieldset>
                <legend>Available training equipment</legend>
                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={p.equipment != null}
                    onChange={(e) =>
                      update("equipment", e.target.checked ? [] : null)
                    }
                  />
                  Specify equipment individually (otherwise gym access assumes
                  dumbbells/bench; MMA gym assumes mats)
                </label>
                {p.equipment != null && (
                  <div className="check-grid">
                    {[
                      "dumbbells",
                      "bench",
                      "bands",
                      "bike",
                      "rower",
                      "rope",
                      "medicine_ball",
                      "mats",
                    ].map((item) => (
                      <label className="checkbox" key={item}>
                        <input
                          type="checkbox"
                          checked={p.equipment?.includes(item) ?? false}
                          onChange={(e) =>
                            update(
                              "equipment",
                              e.target.checked
                                ? [...(p.equipment ?? []), item]
                                : (p.equipment ?? []).filter((v) => v !== item),
                            )
                          }
                        />
                        {item.replaceAll("_", " ")}
                      </label>
                    ))}
                  </div>
                )}
              </fieldset>
              <div className="discipline-choices">
                {[
                  "Halal",
                  "Vegetarian",
                  "Vegan",
                  "Dairy-free",
                  "Gluten-free",
                ].map((d) => (
                  <button
                    className={p.diet.includes(d) ? "selected" : ""}
                    type="button"
                    key={d}
                    onClick={() => toggle("diet", d)}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </>
          )}
          {step === 5 && (
            <>
              <div className="form-grid">
                <div className="full">
                  {select("goal", "Primary development goal", goals)}
                </div>
                <label>
                  Time horizon
                  <input
                    maxLength={100}
                    value={p.horizon}
                    onChange={(e) => update("horizon", e.target.value)}
                  />
                </label>
                {select("priority", "Strength / conditioning priority", [
                  "Balanced",
                  "Strength",
                  "Conditioning",
                ])}
                {select("intensity", "Preferred coaching intensity", [
                  "Gentle",
                  "Balanced",
                  "Challenging",
                ])}
              </div>
              <h3>Additional objectives</h3>
              <div className="discipline-choices">
                {goals
                  .filter((g) => g !== p.goal)
                  .map((d) => (
                    <button
                      key={d}
                      type="button"
                      className={p.objectives.includes(d) ? "selected" : ""}
                      onClick={() => toggle("objectives", d)}
                    >
                      {d}
                    </button>
                  ))}
              </div>
              <h3>Preferred disciplines</h3>
              <div className="discipline-choices">
                {disciplines.map((d) => (
                  <button
                    key={d}
                    type="button"
                    className={p.preferred.includes(d) ? "selected" : ""}
                    onClick={() => toggle("preferred", d)}
                  >
                    {d}
                  </button>
                ))}
              </div>
              {check(
                "competitive",
                "Interested in supervised competition development",
              )}
              <Note>
                Your assessment will distinguish calculations, self-reported
                experience and heuristic guidance. No measurements establish
                professional fighting potential. Competitive planning needs
                qualified supervision.
              </Note>
            </>
          )}
          <div className="wizard-actions">
            <button
              type="button"
              className="text-button"
              disabled={busy}
              onClick={() => save()}
            >
              {saved ? (
                <>
                  <Check size={15} /> Draft saved
                </>
              ) : (
                "Save progress"
              )}
            </button>
            <div className="button-row">
              {step > 0 && (
                <button
                  type="button"
                  className="secondary"
                  onClick={() => setStep(step - 1)}
                >
                  <ChevronLeft size={15} /> Back
                </button>
              )}
              <button className="primary" disabled={busy}>
                {busy
                  ? "Saving…"
                  : step === 5
                    ? "Save athlete profile"
                    : "Continue"}
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </form>
      </section>
    </div>
  );
}
