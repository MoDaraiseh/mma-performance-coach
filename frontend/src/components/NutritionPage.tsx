import {
  Activity,
  Dumbbell,
  Flame,
  Heart,
  Sparkles,
  Utensils,
} from "lucide-react";
import { useState } from "react";
import { api } from "../api";
import type { Runner } from "../types";
import { Nutrition, Profile, Saved } from "../types";
import { fmt } from "../utils";
import { Card, Empty, Metric, Note, Tag } from "./ui";
import NutritionWorkbench from "./NutritionWorkbench";
export default function NutritionPage({
  nutrition,
  profile,
  run,
  refresh,
  busy,
}: {
  nutrition: Saved<Nutrition> | null;
  profile: Profile;
  run: Runner;
  refresh: () => Promise<void>;
  busy: boolean;
}) {
  const [day, setDay] = useState(0),
    [grocery, setGrocery] = useState(false),
    [refreshKey, setRefreshKey] = useState(0),
    [message, setMessage] = useState("");
  const n = nutrition?.data,
    data = n?.days[day];
  return (
    <>
      <div className="button-row nutrition-actions">
        <div className="tags">
          {profile.diet.length ? (
            profile.diet.map((d) => <Tag key={d}>{d}</Tag>)
          ) : (
            <Tag>No dietary restrictions recorded</Tag>
          )}
          {profile.allergies.length > 0 && (
            <Tag tone="red">Allergies: {profile.allergies.join(", ")}</Tag>
          )}
        </div>
        <button
          disabled={busy}
          className="primary"
          onClick={() =>
            run(async () => {
              if (nutrition) {
                await api("/nutrition/proposals", "POST", {
                  kind: "regenerate",
                });
                setMessage(
                  "Meal plan preview saved below; approve it to apply changes.",
                );
              } else {
                await api("/nutrition", "POST");
                await refresh();
              }
              setRefreshKey((n) => n + 1);
            })
          }
        >
          <Sparkles size={16} />
          {nutrition ? "Preview updated meal plan" : "Generate meal plan"}
        </button>
      </div>
      {message && <p role="status">{message}</p>}
      {!n ? (
        <Empty>Generate your meal template to begin.</Empty>
      ) : !n.available ? (
        <Card title="Individual guidance is needed">
          <p>{n.reason}</p>
          <Note>{n.guidance}</Note>
        </Card>
      ) : (
        <>
          <div className="metric-grid">
            <Metric
              title="Estimated maintenance"
              value={`${n.estimated_maintenance?.toLocaleString()} kcal`}
              detail={`Approximate uncertainty: ${n.range?.join("–")} kcal`}
              icon={Flame}
            />
            <Metric
              title="Protein · selected day"
              value={`${fmt(data?.totals.protein)} g`}
              detail={`Guidance: ${n.macro_guidance?.protein_g.join("–") ?? "Unspecified"} g/day`}
              icon={Dumbbell}
            />
            <Metric
              title="Carbohydrate · selected day"
              value={`${fmt(data?.totals.carbs)} g`}
              detail="Ingredient estimate"
              icon={Activity}
            />
            <Metric
              title="Fat · selected day"
              value={`${fmt(data?.totals.fat)} g`}
              detail="Ingredient estimate"
              icon={Heart}
            />
          </div>
          <Card
            title="Estimated fueling targets"
            eyebrow="NOT MEASURED EXPENDITURE"
          >
            <p>
              Planned energy: {n.target_calories ?? n.estimated_maintenance}{" "}
              kcal · {n.goal_note}
            </p>
            <p>
              Protein guidance: {n.macro_guidance?.protein_g.join("–")} g/day ·
              carbohydrate reference: {n.macro_guidance?.carbs_g.join("–")}{" "}
              g/day · fat guidance: {n.macro_guidance?.fat_g.join("–")} g/day.
            </p>
            <p>{n.macro_guidance?.note}</p>
            {n.effective_weight_kg != null && (
              <p>
                Calculation body mass: {n.effective_weight_kg} kg.{" "}
                {n.weight_review?.needs_review
                  ? "Approved sustained check-in median; the saved profile was not overwritten."
                  : "Saved profile measurement; not independently verified."}
              </p>
            )}
            {n.warnings?.map((warning) => (
              <Note key={warning}>{warning}</Note>
            ))}
          </Card>
          <Card
            title="Your seven-day meal template"
            action={
              <button
                className="secondary"
                onClick={() => setGrocery(!grocery)}
              >
                <Utensils size={15} />
                {grocery ? "View meals" : "Grocery list"}
              </button>
            }
          >
            {grocery ? (
              <>
                <table>
                  <thead>
                    <tr>
                      <th>Ingredient</th>
                      <th>Estimated weekly quantity</th>
                    </tr>
                  </thead>
                  <tbody>
                    {n.grocery.map((i) => (
                      <tr key={i.food}>
                        <td>{i.food}</td>
                        <td>
                          {i.grams >= 1000
                            ? `${(i.grams / 1000).toFixed(2)} kg`
                            : `${i.grams} g`}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p className="muted">
                  Quantities refer to ingredient preparation state shown. Review
                  portions and package sizes before shopping.
                </p>
              </>
            ) : (
              <>
                <div className="day-tabs">
                  {n.days.map((d, i) => (
                    <button
                      className={i === day ? "active" : ""}
                      key={d.day}
                      onClick={() => setDay(i)}
                    >
                      Day {d.day}
                    </button>
                  ))}
                </div>
                <div className="meal-grid">
                  {data?.meals.map((m, i) => (
                    <div className="meal-card" key={m.name}>
                      <div className="meal-art">
                        <Utensils size={30} />
                        <span>0{i + 1}</span>
                      </div>
                      <p className="eyebrow">{m.name}</p>
                      <h3>
                        {m.title ||
                          m.ingredients
                            .slice(0, 2)
                            .map((i) =>
                              i.food
                                .replace(" (cooked)", "")
                                .replace(" (dry)", ""),
                            )
                            .join(" & ")}
                      </h3>
                      <strong className="meal-calories">
                        {Math.round(m.calories)} <small>kcal</small>
                      </strong>
                      <div className="macro-row">
                        <span>P {m.protein}g</span>
                        <span>C {m.carbs}g</span>
                        <span>F {m.fat}g</span>
                      </div>
                      <details>
                        <summary>Ingredients & portions</summary>
                        {m.ingredients.map((i) => (
                          <p key={i.food}>
                            {i.grams} g {i.food}
                            {i.source && (
                              <>
                                {" "}
                                ·{" "}
                                <a
                                  className="source"
                                  href={i.source.url}
                                  target="_blank"
                                  rel="noreferrer"
                                >
                                  USDA {i.source.fdc_id}
                                </a>
                              </>
                            )}
                          </p>
                        ))}
                        <p>{m.preparation}</p>
                        {m.preparation_steps && (
                          <ol>
                            {m.preparation_steps.map((step) => (
                              <li key={step}>{step}</li>
                            ))}
                          </ol>
                        )}
                        <p>{m.cooking_note}</p>
                        <p>
                          Macro-derived energy: {m.calories} kcal · source
                          database energy: {m.source_calories ?? "Not recorded"}{" "}
                          kcal. Different energy conventions; values are not
                          interchangeable.
                        </p>
                      </details>
                      <button
                        className="secondary no-print"
                        disabled={busy}
                        onClick={() =>
                          run(async () => {
                            await api("/nutrition/proposals", "POST", {
                              kind: "meal_swap",
                              day: day + 1,
                              meal: m.name,
                            });
                            setRefreshKey((n) => n + 1);
                            setMessage(
                              `Day ${day + 1} ${m.name} substitution preview saved below. Active meals unchanged until approval.`,
                            );
                          })
                        }
                      >
                        Preview {m.name.toLowerCase()} substitute
                      </button>
                    </div>
                  ))}
                </div>
                <div className="meal-totals">
                  <strong>Day {day + 1} total</strong>
                  <span>{fmt(data?.totals.calories)} kcal</span>
                  <span>P {fmt(data?.totals.protein)}g</span>
                  <span>C {fmt(data?.totals.carbs)}g</span>
                  <span>F {fmt(data?.totals.fat)}g</span>
                </div>
                {data?.nutrients && (
                  <p>
                    Catalog totals: fiber {data.nutrients.fiber ?? "Unknown"} g;
                    sodium {data.nutrients.sodium_mg ?? "Unknown"} mg; calcium{" "}
                    {data.nutrients.calcium_mg ?? "Unknown"} mg; iron{" "}
                    {data.nutrients.iron_mg ?? "Unknown"} mg; potassium{" "}
                    {data.nutrients.potassium_mg ?? "Unknown"} mg. These totals
                    do not establish dietary adequacy; added salt and unlisted
                    ingredients are excluded.
                  </p>
                )}
                {data?.training_context && (
                  <Note>
                    {data.training_context.weekday}:{" "}
                    {data.training_context.note}
                  </Note>
                )}
              </>
            )}
          </Card>
          <div className="two-column">
            <Card title="Training & recovery days">
              <p>{n.guidance}</p>
              <p>{n.training_note}</p>
              <p>
                Meal timing days:{" "}
                {n.training_days?.join(", ") || "Not supplied"}.
              </p>
              <p>{n.budget_note}</p>
              <Note>
                Meal timing should support comfort and consistency. Hydrate
                regularly and respond to thirst; this app does not prescribe
                water manipulation.
              </Note>
            </Card>
            <Card title="Substitutions & dietary safety">
              <p>{n.substitutions}</p>
            </Card>
          </div>
          <details className="method">
            <summary>Calculation and ingredient assumptions</summary>
            <p>{n.method}</p>
            <p>
              Resting estimate: {n.rmr} kcal × activity factor{" "}
              {n.activity_factor}. The displayed total is calculated from
              rounded meal macros.
            </p>
          </details>
        </>
      )}
      <NutritionWorkbench
        run={run}
        refresh={refresh}
        busy={busy}
        refreshKey={refreshKey}
      />
    </>
  );
}
