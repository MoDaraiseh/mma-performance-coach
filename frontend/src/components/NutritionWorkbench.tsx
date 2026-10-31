import { useEffect, useState } from "react";
import { api } from "../api";
import type {
  Ingredient,
  Nutrition,
  NutritionPreferences,
  NutritionProposal,
  Runner,
  Saved,
} from "../types";
import { Card, Empty, Note, Tag } from "./ui";

export function NutritionPreview({ plan }: { plan: Nutrition }) {
  if (!plan.available)
    return (
      <Note>
        Numerical meals withheld: {plan.reason} {plan.guidance}
      </Note>
    );
  return (
    <>
      <p>
        Proposed energy: {plan.target_calories ?? plan.estimated_maintenance}{" "}
        kcal. P {plan.macro_targets?.protein} g · C {plan.macro_targets?.carbs}{" "}
        g · F {plan.macro_targets?.fat} g.
      </p>
      {plan.changes?.map((change) => (
        <p key={change}>{change}</p>
      ))}
      {plan.substitution_comparison && (
        <div>
          <h3>Substitution differences before approval</h3>
          <p>
            Before: {plan.substitution_comparison.before.calories} kcal. After:{" "}
            {plan.substitution_comparison.after.calories} kcal.
          </p>
          <p>
            Change:{" "}
            {Object.entries(plan.substitution_comparison.delta)
              .map(([k, v]) => `${k}: ${v > 0 ? "+" : ""}${v}`)
              .join("; ")}
            . Portions below are rebalanced to preserve daily targets.
          </p>
          <p>
            Before portions:{" "}
            {plan.substitution_comparison.before.ingredients
              .map((i) => `${i.grams} g ${i.food}`)
              .join("; ")}
          </p>
          <p>
            After portions:{" "}
            {plan.substitution_comparison.after.ingredients
              .map((i) => `${i.grams} g ${i.food}`)
              .join("; ")}
          </p>
        </div>
      )}
      <details>
        <summary>Review all proposed meals, portions and totals</summary>
        {plan.days.map((day) => (
          <section key={day.day}>
            <h3>Day {day.day}</h3>
            {day.meals.map((meal) => (
              <div key={meal.name}>
                <h4>
                  {meal.name}: {meal.title ?? meal.name}
                </h4>
                <p>
                  {meal.calories} kcal · P {meal.protein} g · C {meal.carbs} g ·
                  F {meal.fat} g.
                </p>
                <p>
                  {meal.ingredients
                    .map((i) => `${i.grams} g ${i.food}`)
                    .join("; ")}
                </p>
              </div>
            ))}
            <p>
              Day total: {day.totals.calories} kcal; P {day.totals.protein} g ·
              C {day.totals.carbs} g · F {day.totals.fat} g.
            </p>
          </section>
        ))}
        <h3>Updated groceries</h3>
        {plan.grocery.map((i) => (
          <p key={i.food}>
            {i.food}: {i.grams} g, preparation state as named.
          </p>
        ))}
      </details>
    </>
  );
}

export default function NutritionWorkbench({
  run,
  refresh,
  busy,
  refreshKey,
}: {
  run: Runner;
  refresh: () => Promise<void>;
  busy: boolean;
  refreshKey: number;
}) {
  const [catalog, setCatalog] = useState<Ingredient[]>([]),
    [prefs, setPrefs] = useState<NutritionPreferences | null>(null),
    [proposals, setProposals] = useState<Saved<NutritionProposal>[]>([]),
    [history, setHistory] = useState<Saved<Nutrition>[]>([]),
    [message, setMessage] = useState("");
  const [swapDay, setSwapDay] = useState(1),
    [swapMeal, setSwapMeal] = useState("Lunch"),
    [swapFood, setSwapFood] = useState("");
  const load = async () => {
    const [cat, settings, rows, versions] = await Promise.all([
      api<{ items: Ingredient[] }>("/nutrition/catalog"),
      api<NutritionPreferences>("/nutrition/preferences"),
      api<Saved<NutritionProposal>[]>("/nutrition/proposals"),
      api<Saved<Nutrition>[]>("/nutrition/history"),
    ]);
    setCatalog(cat.items);
    setPrefs((draft) => draft ?? settings);
    setProposals(rows);
    setHistory(versions);
  };
  useEffect(() => {
    run(load);
  }, [refreshKey]);
  const multi = (key: "dislikes" | "unavailable", values: string[]) =>
    prefs && setPrefs({ ...prefs, [key]: values });
  return (
    <div className="nutrition-workbench no-print">
      {message && <p role="status">{message}</p>}
      <Card title="Choose a food substitution">
        <p>
          Choose a replacement protein or grain, fruit for breakfast/snack, or
          vegetable for lunch/dinner. Other portions are rebalanced to preserve
          targets. Excluded foods and infeasible portions are rejected; review
          differences before approval.
        </p>
        <fieldset disabled={busy}>
          <legend>Replacement preview</legend>
          <div className="form-grid">
            <label>
              Meal day
              <select
                aria-label="Meal day"
                value={swapDay}
                onChange={(e) => setSwapDay(Number(e.target.value))}
              >
                {[1, 2, 3, 4, 5, 6, 7].map((d) => (
                  <option key={d} value={d}>
                    Day {d}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Meal to customize
              <select
                aria-label="Meal to customize"
                value={swapMeal}
                onChange={(e) => setSwapMeal(e.target.value)}
              >
                {["Breakfast", "Lunch", "Dinner", "Recovery snack"].map((m) => (
                  <option key={m}>{m}</option>
                ))}
              </select>
            </label>
            <label>
              Replacement food
              <select
                aria-label="Replacement food"
                value={swapFood}
                onChange={(e) => setSwapFood(e.target.value)}
              >
                <option value="">Choose a catalog food</option>
                {catalog.map((i) => (
                  <option key={i.id} value={i.id}>
                    {i.name}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <button
            className="secondary"
            disabled={!swapFood}
            onClick={() =>
              run(async () => {
                await api("/nutrition/proposals", "POST", {
                  kind: "meal_swap",
                  day: swapDay,
                  meal: swapMeal,
                  food_id: swapFood,
                });
                await load();
                setMessage(
                  "Food replacement preview saved. Review before and after portions below, then approve or reject.",
                );
              })
            }
          >
            Preview chosen food replacement
          </button>
        </fieldset>
      </Card>
      <Card
        title="Preferences & meal feedback"
        eyebrow="YOUR INPUTS, NOT GENERATED ASSUMPTIONS"
      >
        <Note>
          New exclusions apply to nutrition suggestions. Existing profile
          allergies and diets remain in force; remove them only by editing your
          profile. Feedback never changes the active plan automatically.
        </Note>
        <details>
          <summary>Edit nutrition preferences</summary>
          {prefs && (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                run(async () => {
                  const saved = await api<Saved<NutritionPreferences>>(
                    "/nutrition/preferences",
                    "PUT",
                    prefs,
                  );
                  setPrefs(saved.data);
                  await refresh();
                  await load();
                  setMessage(
                    "Feedback saved. Preview an updated meal plan and approve it before using new targets.",
                  );
                });
              }}
            >
              <fieldset disabled={busy}>
                <legend>Nutrition preferences and feedback</legend>
                <div className="form-grid">
                  <label>
                    Cooking skill
                    <select
                      aria-label="Cooking skill"
                      value={prefs.cooking_skill ?? "Beginner"}
                      onChange={(e) =>
                        setPrefs({ ...prefs, cooking_skill: e.target.value })
                      }
                    >
                      <option>Beginner</option>
                      <option>Comfortable</option>
                    </select>
                  </label>
                  <label>
                    Assembly time limit (minutes)
                    <input
                      aria-label="Assembly time limit (minutes)"
                      type="number"
                      min={10}
                      max={120}
                      value={prefs.cooking_minutes ?? 30}
                      onChange={(e) =>
                        setPrefs({
                          ...prefs,
                          cooking_minutes: Number(e.target.value),
                        })
                      }
                    />
                  </label>
                  <label>
                    Meals per day
                    <select
                      aria-label="Meals per day"
                      value={prefs.meals_per_day ?? ""}
                      onChange={(e) =>
                        setPrefs({
                          ...prefs,
                          meals_per_day: e.target.value
                            ? Number(e.target.value)
                            : null,
                        })
                      }
                    >
                      <option value="">Use snack preference</option>
                      <option value="3">3 main meals</option>
                      <option value="4">3 main meals + snack</option>
                    </select>
                  </label>
                  <label>
                    Nutrition objective
                    <select
                      value={prefs.objective}
                      onChange={(e) =>
                        setPrefs({ ...prefs, objective: e.target.value })
                      }
                    >
                      {[
                        "Maintain",
                        "Build gradually",
                        "Sustainable reduction",
                      ].map((s) => (
                        <option key={s}>{s}</option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Ingredient pattern preference
                    <select
                      value={prefs.culture}
                      onChange={(e) =>
                        setPrefs({ ...prefs, culture: e.target.value })
                      }
                    >
                      {[
                        "Varied",
                        "Middle Eastern inspired",
                        "South Asian inspired",
                        "Mediterranean inspired",
                      ].map((s) => (
                        <option key={s}>{s}</option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Food budget preference
                    <select
                      value={prefs.budget ?? ""}
                      onChange={(e) =>
                        setPrefs({ ...prefs, budget: e.target.value || null })
                      }
                    >
                      <option value="">Use saved profile</option>
                      {["Low", "Moderate", "Flexible"].map((s) => (
                        <option key={s}>{s}</option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Additional allergies (comma separated)
                    <input
                      maxLength={500}
                      value={prefs.add_allergies.join(", ")}
                      onChange={(e) =>
                        setPrefs({
                          ...prefs,
                          add_allergies: e.target.value
                            .split(",")
                            .map((s) => s.trim()),
                        })
                      }
                    />
                  </label>
                  <label>
                    Food dislikes
                    <select
                      aria-label="Food dislikes"
                      multiple
                      value={prefs.dislikes}
                      onChange={(e) =>
                        multi(
                          "dislikes",
                          [...e.target.selectedOptions].map((o) => o.value),
                        )
                      }
                    >
                      {catalog.map((i) => (
                        <option value={i.id} key={i.id}>
                          {i.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Unavailable ingredients
                    <select
                      aria-label="Unavailable ingredients"
                      multiple
                      value={prefs.unavailable}
                      onChange={(e) =>
                        multi(
                          "unavailable",
                          [...e.target.selectedOptions].map((o) => o.value),
                        )
                      }
                    >
                      {catalog.map((i) => (
                        <option value={i.id} key={i.id}>
                          {i.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Hunger (optional, 1 low–5 high)
                    <input
                      type="number"
                      min="1"
                      max="5"
                      value={prefs.hunger ?? ""}
                      onChange={(e) =>
                        setPrefs({
                          ...prefs,
                          hunger:
                            e.target.value === "" ? null : +e.target.value,
                        })
                      }
                    />
                  </label>
                  <label>
                    Satisfaction (optional, 1 low–5 high)
                    <input
                      type="number"
                      min="1"
                      max="5"
                      value={prefs.satisfaction ?? ""}
                      onChange={(e) =>
                        setPrefs({
                          ...prefs,
                          satisfaction:
                            e.target.value === "" ? null : +e.target.value,
                        })
                      }
                    />
                  </label>
                </div>
                <fieldset>
                  <legend>Additional dietary restrictions</legend>
                  {[
                    "Halal",
                    "Vegetarian",
                    "Vegan",
                    "Dairy-free",
                    "Gluten-free",
                  ].map((diet) => (
                    <label className="checkbox" key={diet}>
                      <input
                        type="checkbox"
                        checked={prefs.add_diet.includes(diet)}
                        onChange={(e) =>
                          setPrefs({
                            ...prefs,
                            add_diet: e.target.checked
                              ? [...prefs.add_diet, diet]
                              : prefs.add_diet.filter((s) => s !== diet),
                          })
                        }
                      />
                      {diet}
                    </label>
                  ))}
                </fieldset>
                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={prefs.snacks}
                    onChange={(e) =>
                      setPrefs({ ...prefs, snacks: e.target.checked })
                    }
                  />{" "}
                  Include optional recovery snack
                </label>
                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={prefs.training_days === null}
                    onChange={(e) =>
                      setPrefs({
                        ...prefs,
                        training_days: e.target.checked ? null : [],
                      })
                    }
                  />{" "}
                  Use approved training calendar for meal timing
                </label>
                {prefs.training_days !== null && (
                  <fieldset>
                    <legend>
                      Reported training days (nutrition timing only)
                    </legend>
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
                          checked={prefs.training_days?.includes(day)}
                          onChange={(e) =>
                            setPrefs({
                              ...prefs,
                              training_days: e.target.checked
                                ? [...(prefs.training_days ?? []), day]
                                : (prefs.training_days?.filter(
                                    (s) => s !== day,
                                  ) ?? []),
                            })
                          }
                        />
                        {day}
                      </label>
                    ))}
                  </fieldset>
                )}
                <button className="primary" disabled={busy}>
                  Save nutrition feedback
                </button>
              </fieldset>
            </form>
          )}
        </details>
      </Card>
      <Card
        title="Meal plan proposals"
        eyebrow="PREVIEW → APPROVAL → NEW SAVED VERSION"
      >
        {!proposals.length && (
          <Empty>
            Use “Preview updated meal plan” or a meal's substitution button to
            prepare changes.
          </Empty>
        )}
        {[...proposals].reverse().map((row) => (
          <section className="nutrition-proposal" key={row.id}>
            <h3>
              Nutrition proposal {row.version} <Tag>{row.data.status}</Tag>
            </h3>
            <NutritionPreview plan={row.data.plan} />
            {row.data.status === "pending" && (
              <div className="button-row">
                <button
                  className="primary"
                  disabled={busy}
                  onClick={() =>
                    run(async () => {
                      await api(
                        `/nutrition/proposals/${row.id}/approve`,
                        "POST",
                      );
                      await refresh();
                      await load();
                      setMessage(
                        "Meal plan approved and saved as a new version.",
                      );
                    })
                  }
                >
                  Approve meal plan
                </button>
                <button
                  className="secondary"
                  disabled={busy}
                  onClick={() =>
                    run(async () => {
                      await api(
                        `/nutrition/proposals/${row.id}/reject`,
                        "POST",
                      );
                      await load();
                      setMessage(
                        "Proposal rejected; active meal plan unchanged.",
                      );
                    })
                  }
                >
                  Reject meal plan
                </button>
              </div>
            )}
          </section>
        ))}
      </Card>
      <Card title="Nutrition catalog & saved history">
        <details>
          <summary>Inspect {catalog.length} source-backed ingredients</summary>
          <p>
            Values per 100 g in the stated preparation state. Source energy
            differs from 4P+4C+9F because of fiber and food-specific factors.
            Cost tiers are editorial relative categories, not local prices.
            Allergy labels require package and cross-contact checks.
          </p>
          {catalog.map((i) => (
            <details key={i.id}>
              <summary>{i.name}</summary>
              <p>
                Source {i.per_100g.source_calories} kcal · protein{" "}
                {i.per_100g.protein} g · carbohydrate {i.per_100g.carbs} g · fat{" "}
                {i.per_100g.fat} g · fiber {i.per_100g.fiber ?? "Unknown"} g.
              </p>
              <p>
                Sodium: {i.per_100g.sodium_mg ?? "Unknown"} mg; calcium:{" "}
                {i.per_100g.calcium_mg ?? "Unknown"} mg; iron:{" "}
                {i.per_100g.iron_mg ?? "Unknown"} mg; potassium:{" "}
                {i.per_100g.potassium_mg ?? "Unknown"} mg. Missing values are
                not zero. Product halal certification and cross-contact are
                unknown.
              </p>
              <p>
                Screened allergens:{" "}
                {i.allergens.join(", ") ||
                  "None listed for generic ingredient; not a safety guarantee"}
                . Cost tier {i.cost_tier}.
              </p>
              <a
                className="source"
                href={i.source.url}
                target="_blank"
                rel="noreferrer"
              >
                USDA FDC {i.source.fdc_id} · {i.source.dataset} ·{" "}
                {i.source.license} · reviewed {i.source.reviewed_at}
              </a>
              <p>{i.source.description}</p>
            </details>
          ))}
        </details>
        <details>
          <summary>Saved nutrition versions ({history.length})</summary>
          <p>
            Historical snapshots are retained for audit and export; use only the
            current reviewed plan.
          </p>
          {[...history].reverse().map((row) => (
            <p key={row.id}>
              Version {row.version} ·{" "}
              {row.data.available
                ? `${row.data.target_calories ?? row.data.estimated_maintenance} kcal estimate`
                : "Targets withheld"}{" "}
              · {new Date(row.created_at).toLocaleDateString()}
            </p>
          ))}
        </details>
      </Card>
    </div>
  );
}
