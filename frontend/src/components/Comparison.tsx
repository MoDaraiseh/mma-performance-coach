import {
  ChevronRight,
  Heart,
  Search,
  SlidersHorizontal,
  X,
} from "lucide-react";
import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../api";
import type { Runner } from "../types";
import { Fighter, Match, Profile, Ranking, Saved, Weights } from "../types";
import { fmt, labelMap } from "../utils";
import { Card, Empty, Note, Tag } from "./ui";
const groups = [
  "physical",
  "background",
  "style",
  "stance",
  "weight_class",
] as const;
const defaults: Weights = {
  physical: 60,
  background: 15,
  style: 10,
  stance: 5,
  weight_class: 10,
};
type Favorite = Saved<{ match: Match; weights: Weights; profile?: Profile }>;
type DataStatus = {
  quality?: {
    categories: Record<string, number>;
    supported_fields: Record<string, number>;
    unestablished_rights: number;
  };
  count: number;
  unavailable_records: { id: string; reason: string }[];
  providers: { id: string; available: boolean; description: string }[];
  revisions: { digest: string; entity: string }[];
};
export default function Comparison({
  profile,
  run,
  busy,
  notify,
}: {
  profile: Profile;
  run: Runner;
  busy: boolean;
  notify: (s: string) => void;
}) {
  const [weights, setWeights] = useState<Weights>({
      physical: 60,
      background: 15,
      style: 10,
      stance: 5,
      weight_class: 10,
    }),
    [ranking, setRanking] = useState<Ranking | null>(null),
    [query, setQuery] = useState(""),
    [all, setAll] = useState<Fighter[]>([]),
    [selected, setSelected] = useState<Fighter | null>(null),
    [favorites, setFavorites] = useState<Favorite[]>([]),
    [error, setError] = useState(""),
    [rankError, setRankError] = useState(""),
    [manualError, setManualError] = useState(""),
    [manual, setManual] = useState<Match | null>(null),
    [snapshot, setSnapshot] = useState<Favorite | null>(null),
    [dataStatus, setDataStatus] = useState<DataStatus | null>(null),
    [provider, setProvider] = useState("local"),
    [refreshKey, setRefreshKey] = useState(0),
    [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    category: "",
    division: "",
    stance: "",
    status: "",
  });
  const [searchPage, setSearchPage] = useState(1),
    [searchTotal, setSearchTotal] = useState(0),
    [searchLoading, setSearchLoading] = useState(false);
  useEffect(() => {
    let canceled = false;
    setSearchLoading(true);
    setAll([]);
    const timer = setTimeout(() => {
      const params = new URLSearchParams({
        q: query,
        page: String(searchPage),
        page_size: "10",
      });
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.set(key, value);
      });
      api<{ items: Fighter[]; total: number }>(`/fighters/search?${params}`)
        .then((r) => {
          if (!canceled) {
            setAll(r.items);
            setSearchTotal(r.total);
            setSearchLoading(false);
          }
        })
        .catch((e) => {
          if (!canceled) {
            setError(e.message);
            setSearchLoading(false);
          }
        });
    }, 150);
    return () => {
      canceled = true;
      clearTimeout(timer);
    };
  }, [query, filters, searchPage, refreshKey]);
  useEffect(() => {
    let cancelled = false;
    setRanking(null);
    setLoading(true);
    setRankError("");
    const timer = setTimeout(() => {
      api<Ranking>("/fighter-matches", "POST", weights)
        .then((r) => {
          if (!cancelled) {
            setRanking(r);
            setLoading(false);
            setRankError("");
          }
        })
        .catch((e) => {
          if (!cancelled) {
            setRankError(e.message);
            setLoading(false);
          }
        });
    }, 150);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [weights, profile, refreshKey]);
  useEffect(() => {
    api<DataStatus>("/fighter-data")
      .then(setDataStatus)
      .catch((e) => setError(e.message));
    api<Favorite[]>("/comparisons")
      .then(setFavorites)
      .catch((e) => setError(e.message));
  }, [refreshKey]);
  useEffect(() => {
    if (!selected || snapshot) {
      setManual(null);
      setManualError("");
      return;
    }
    let cancelled = false;
    setManual(null);
    setManualError("");
    const timer = setTimeout(() => {
      api<Match>(`/fighter-comparisons/${selected.id}`, "POST", weights)
        .then((result) => {
          if (!cancelled) setManual(result);
        })
        .catch((e) => {
          if (!cancelled) setManualError(e.message);
        });
    }, 150);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [selected, weights, profile, snapshot, refreshKey]);
  const total = groups.reduce((a, k) => a + weights[k], 0);
  const fighters = all;
  const currentMatch =
    snapshot?.data.match || (selected ? manual : ranking?.matches[0]);
  const compare =
    snapshot?.data.match.fighter || currentMatch?.fighter || selected;
  const shownProfile = snapshot?.data.profile || profile;
  const choose = (fighter: Fighter) => {
    setSnapshot(null);
    setSelected({ ...fighter });
  };
  const updateWeights = (next: Weights) => {
    setSnapshot(null);
    setWeights(next);
  };
  const saveComparison = (fighter: Fighter) =>
    run(async () => {
      await api(`/comparisons/${fighter.id}`, "POST", weights);
      setFavorites(await api("/comparisons"));
      notify("Comparison saved with profile, source snapshots and weights.");
    });
  return (
    <>
      <div className="lab-layout">
        <Card
          title="Define your comparison"
          eyebrow="YOUR CONTROLS"
          action={<SlidersHorizontal size={18} />}
        >
          <p className="muted">
            Move the sliders to change what matters. Rankings recalculate on the
            backend.
          </p>
          {groups.map((k) => {
            const v = weights[k];
            return (
              <label className="slider-row" key={k}>
                <span>
                  {labelMap[k]}
                  <strong>{total ? Math.round((v / total) * 100) : 0}%</strong>
                </span>
                <input
                  aria-label={labelMap[k]}
                  type="range"
                  min="0"
                  max="100"
                  value={v}
                  onChange={(e) =>
                    updateWeights({ ...weights, [k]: +e.target.value })
                  }
                />
              </label>
            );
          })}
          {total === 0 && (
            <p role="alert" className="red-text">
              At least one weight must be positive.
            </p>
          )}
          <Note>
            Unknown attributes are excluded. Effective weights differ by fighter
            and are shown below. Stance and technical fields are sparse; only
            supported values contribute. Coverage is separate from resemblance.
          </Note>
          <details>
            <summary>Physical factors and eligibility filters</summary>
            {(["height_weight", "reach_weight", "ratio_weight"] as const).map(
              (key) => (
                <label className="slider-row" key={key}>
                  <span>
                    {key === "height_weight"
                      ? "Height factor"
                      : key === "reach_weight"
                        ? "Reach factor"
                        : "Reach / height ratio factor"}
                    <strong>
                      {weights[key] ?? (key === "ratio_weight" ? 0 : 50)}
                    </strong>
                  </span>
                  <input
                    aria-label={
                      key === "height_weight"
                        ? "Height factor"
                        : key === "reach_weight"
                          ? "Reach factor"
                          : "Reach / height ratio factor"
                    }
                    type="range"
                    min="0"
                    max="100"
                    value={weights[key] ?? (key === "ratio_weight" ? 0 : 50)}
                    onChange={(e) =>
                      updateWeights({ ...weights, [key]: +e.target.value })
                    }
                  />
                </label>
              ),
            )}
            <p className="muted">
              Ratio is derived from height and reach. Its default weight is zero
              to avoid counting reach twice.
            </p>
            <label>
              Style study preferences (optional, multiple)
              <select
                multiple
                value={weights.style_preferences ?? []}
                onChange={(e) =>
                  updateWeights({
                    ...weights,
                    style_preferences: [...e.target.selectedOptions].map(
                      (option) => option.value,
                    ),
                  })
                }
              >
                {[
                  "Counter-striking",
                  "Pressure",
                  "Clinch",
                  "Grappling",
                  "Wrestling transitions",
                  "Balanced",
                ].map((style) => (
                  <option key={style}>{style}</option>
                ))}
              </select>
            </label>
            <p className="muted">
              Preferences are not measured skills. They affect scores only when
              a provider supplies matching verified style traits; the local
              bundle has none.
            </p>
            <label className="field">
              Division context
              <select
                value={weights.division_mode ?? "history"}
                onChange={(e) =>
                  updateWeights({
                    ...weights,
                    division_mode: e.target.value as "history" | "current",
                  })
                }
              >
                <option value="history">Documented UFC division history</option>
                <option value="current">Profile-listed current division</option>
              </select>
            </label>
            <label className="field">
              Minimum requested-weight coverage (%)
              <input
                type="number"
                min="0"
                max="100"
                value={weights.min_coverage ?? 0}
                onChange={(e) =>
                  updateWeights({ ...weights, min_coverage: +e.target.value })
                }
              />
            </label>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={weights.include_retired ?? true}
                onChange={(e) =>
                  updateWeights({
                    ...weights,
                    include_retired: e.target.checked,
                  })
                }
              />{" "}
              Include retired / not-fighting snapshots
            </label>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={weights.include_stale ?? true}
                onChange={(e) =>
                  updateWeights({ ...weights, include_stale: e.target.checked })
                }
              />{" "}
              Include observations older than 365 days
            </label>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={weights.same_division_only ?? false}
                onChange={(e) =>
                  updateWeights({
                    ...weights,
                    same_division_only: e.target.checked,
                  })
                }
              />{" "}
              Require shared active division reference
            </label>
          </details>
          <button className="secondary" onClick={() => updateWeights(defaults)}>
            Reset weights
          </button>
        </Card>
        <div>
          <Card
            title="Your closest comparisons"
            eyebrow="HEURISTIC RESEMBLANCE / 100"
            action={
              <Tag>
                {ranking?.coverage?.library_count ?? all.length} reviewed
                profiles
              </Tag>
            }
          >
            {[error, rankError, manualError]
              .filter(Boolean)
              .map((message, index) => (
                <p
                  role="alert"
                  className="red-text"
                  key={`${index}-${message}`}
                >
                  {message}
                </p>
              ))}
            {loading && <p role="status">Updating comparisons...</p>}
            {ranking?.matches.length ? (
              ranking.matches.map((m, i) => (
                <div
                  className={`match-row ${compare?.id === m.fighter.id ? "selected" : ""}`}
                  key={m.fighter.id}
                >
                  <button
                    className="match-select"
                    onClick={() => choose(m.fighter)}
                  >
                    <span className="fighter-initial">0{i + 1}</span>
                    <div>
                      <h3>{m.fighter.name}</h3>
                      <p>{m.fighter.division}</p>
                    </div>
                    <strong>
                      {m.score}
                      <small>/100</small>
                    </strong>
                  </button>
                  <button
                    className="icon-button"
                    aria-label={`Save ${m.fighter.name} comparison`}
                    disabled={busy}
                    onClick={() => saveComparison(m.fighter)}
                  >
                    <Heart size={18} />
                  </button>
                </div>
              ))
            ) : (
              <Empty>
                {total === 0
                  ? "Choose a positive comparison weight."
                  : "No defensible matches for these weights and filters. Missing dimensions may leave no supported comparison."}
              </Empty>
            )}
          </Card>
          <Card title="Search the fighter library">
            <label className="search-box">
              <Search size={17} />
              <input
                aria-label="Search fighters"
                placeholder="Search by fighter name…"
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value);
                  setSearchPage(1);
                }}
              />
            </label>
            <div className="form-grid fighter-search-filters">
              {(
                [
                  ["category", "Search competition category", ["Men", "Women"]],
                  [
                    "division",
                    "Search historical division",
                    [
                      "Strawweight",
                      "Flyweight",
                      "Bantamweight",
                      "Featherweight",
                      "Lightweight",
                      "Welterweight",
                      "Middleweight",
                      "Light Heavyweight",
                      "Heavyweight",
                    ],
                  ],
                  [
                    "stance",
                    "Search stance",
                    ["Orthodox", "Southpaw", "Switch", "Unknown"],
                  ],
                  [
                    "status",
                    "Search career status",
                    ["Active", "Retired", "Not fighting", "Unknown"],
                  ],
                ] as const
              ).map(([key, label, options]) => (
                <label key={key}>
                  {label}
                  <select
                    aria-label={label}
                    value={filters[key]}
                    onChange={(e) => {
                      setFilters({ ...filters, [key]: e.target.value });
                      setSearchPage(1);
                    }}
                  >
                    <option value="">All</option>
                    {options.map((option) => (
                      <option key={option}>{option}</option>
                    ))}
                  </select>
                </label>
              ))}
            </div>
            <p role="status">
              {searchLoading
                ? "Searching fighter records…"
                : `${searchTotal} records found; page ${searchPage}`}
            </p>
            <div className="search-results">
              {fighters.map((f) => (
                <button key={f.id} onClick={() => choose(f)}>
                  {f.name}
                  <ChevronRight size={16} />
                </button>
              ))}
              {!fighters.length && !searchLoading && (
                <Empty>No fighters found.</Empty>
              )}
            </div>
            <div className="fighter-page-controls">
              <button
                className="secondary"
                disabled={searchLoading || searchPage === 1}
                onClick={() => setSearchPage(searchPage - 1)}
              >
                Previous fighter page
              </button>
              <button
                className="secondary"
                disabled={searchLoading || searchPage * 10 >= searchTotal}
                onClick={() => setSearchPage(searchPage + 1)}
              >
                Next fighter page
              </button>
            </div>
          </Card>
        </div>
      </div>
      {snapshot && (
        <Note>
          Saved snapshot from {new Date(snapshot.created_at).toLocaleString()}.{" "}
          {snapshot.data.profile
            ? "Charts use the saved athlete profile and fighter data."
            : "Legacy save lacks athlete inputs; current measurements shown."}{" "}
          <button
            className="secondary"
            onClick={() => {
              setSnapshot(null);
              setSelected(snapshot.data.match.fighter);
            }}
          >
            Re-evaluate with current data
          </button>
        </Note>
      )}
      {compare && (
        <Card title={`You × ${compare.name}`} eyebrow="SIDE-BY-SIDE">
          <div className="button-row">
            <Tag>
              {compare.competition_division} ·{" "}
              {compare.career_status ?? compare.status}
            </Tag>
            <Tag>
              Current profile division:{" "}
              {compare.current_division || "Not established"}
            </Tag>
            {!snapshot && (
              <button
                className="secondary"
                disabled={busy || !currentMatch || total === 0}
                onClick={() => saveComparison(compare)}
              >
                Save selected comparison
              </button>
            )}
          </div>
          {selected && !currentMatch && (
            <p role="status">Comparison breakdown unavailable or updating.</p>
          )}
          <div className="two-column">
            <div className="chart-box">
              <ResponsiveContainer width="100%" height={240}>
                <BarChart
                  data={[
                    {
                      name: "Height (cm)",
                      You: shownProfile.height_cm,
                      Fighter: compare.height_cm,
                    },
                    ...(shownProfile.wingspan_cm && compare.reach_cm
                      ? [
                          {
                            name: "Wingspan / reach (cm)",
                            You: shownProfile.wingspan_cm,
                            Fighter: compare.reach_cm,
                          },
                        ]
                      : []),
                  ]}
                >
                  <CartesianGrid vertical={false} stroke="#303238" />
                  <XAxis
                    dataKey="name"
                    tick={{ fill: "#a4a7b0", fontSize: 11 }}
                  />
                  <YAxis
                    domain={[0, 240]}
                    tick={{ fill: "#a4a7b0", fontSize: 11 }}
                  />
                  <Tooltip
                    itemStyle={{ color: "#fff" }}
                    contentStyle={{
                      background: "#202125",
                      border: "1px solid #3b3d44",
                      color: "#fff",
                    }}
                  />
                  <Legend />
                  <Bar
                    isAnimationActive={false}
                    dataKey="You"
                    fill="#ef4444"
                    radius={[4, 4, 0, 0]}
                    maxBarSize={50}
                  />
                  <Bar
                    isAnimationActive={false}
                    dataKey="Fighter"
                    fill="#737986"
                    radius={[4, 4, 0, 0]}
                    maxBarSize={50}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div>
              <table>
                <thead>
                  <tr>
                    <th>Attribute</th>
                    <th>You</th>
                    <th>{compare.name.split(" ").at(-1)}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Height</td>
                    <td>{shownProfile.height_cm} cm</td>
                    <td>{fmt(compare.height_cm, " cm")}</td>
                  </tr>
                  <tr>
                    <td>Wingspan / reach</td>
                    <td>{fmt(shownProfile.wingspan_cm, " cm")}</td>
                    <td>{fmt(compare.reach_cm, " cm")}</td>
                  </tr>
                  <tr>
                    <td>Everyday weight (athlete)</td>
                    <td>{shownProfile.weight_kg} kg</td>
                    <td>Not established</td>
                  </tr>
                  <tr>
                    <td>Profile-listed fighter weight*</td>
                    <td>Not used as athlete target</td>
                    <td>{fmt(compare.listed_weight_kg, " kg")}</td>
                  </tr>
                  <tr>
                    <td>Stance</td>
                    <td>{shownProfile.stance}</td>
                    <td>{compare.stance || "Unavailable"}</td>
                  </tr>
                  <tr>
                    <td>Background</td>
                    <td>
                      {shownProfile.experience
                        .filter((e) => e.months > 0)
                        .map((e) => e.discipline)
                        .join(", ") || "Unrecorded"}
                    </td>
                    <td>{compare.background.join(", ") || "Unavailable"}</td>
                  </tr>
                  <tr>
                    <td>Style</td>
                    <td>Exploratory; unverified</td>
                    <td>{compare.styles.join(", ") || "Unavailable"}</td>
                  </tr>
                </tbody>
              </table>
              <small className="muted">
                *Listed fighter weight and everyday body weight are different
                contexts.
              </small>
            </div>
          </div>
          {[currentMatch]
            .filter((m): m is Match => Boolean(m))
            .map((m) => (
              <div key={m.fighter.id}>
                <h3>
                  {m.score === null
                    ? "Unscored comparison"
                    : `${m.score}/100 heuristic resemblance`}{" "}
                  · coverage {m.coverage ?? "unrecorded"}%
                </h3>
                <p>{m.similarities}</p>
                {m.eligibility_notes?.map((reason) => (
                  <p className="muted" key={reason}>
                    {reason}
                  </p>
                ))}
                <div className="breakdown">
                  {Object.entries(m.breakdown).map(([key, value]) => (
                    <div key={key}>
                      <span>
                        {labelMap[key]}{" "}
                        <small>
                          effective weight {m.effective_weights[key]}%
                        </small>
                      </span>
                      <div className="bar-track">
                        <i style={{ width: `${value}%` }} />
                      </div>
                      <strong>{value}</strong>
                    </div>
                  ))}
                </div>
                {m.physical_components && (
                  <div
                    className="comparison-table"
                    tabIndex={0}
                    role="region"
                    aria-label="Physical component table"
                  >
                    <table>
                      <caption>Physical similarity components</caption>
                      <thead>
                        <tr>
                          <th>Measurement</th>
                          <th>Resemblance / 100</th>
                          <th>Effective physical weight</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(m.physical_components).map(
                          ([key, value]) => (
                            <tr key={key}>
                              <td>{key}</td>
                              <td>{value}</td>
                              <td>{m.physical_effective_weights?.[key]}%</td>
                            </tr>
                          ),
                        )}
                      </tbody>
                    </table>
                  </div>
                )}
                <ul>
                  {m.differences?.map((difference) => (
                    <li key={difference}>{difference}</li>
                  ))}
                </ul>
                <ul>
                  {Object.entries(m.excluded_reasons ?? {}).map(
                    ([key, reason]) => (
                      <li key={key}>
                        {labelMap[key]}: {reason}
                      </li>
                    ),
                  )}
                </ul>
                {m.quality && (
                  <>
                    <p className="muted">
                      Observation age: {m.quality.observation_age_days} days ·{" "}
                      {m.quality.stale
                        ? "Stale (>365 days)"
                        : "Within 365-day observation window"}
                      . This does not establish a recent physical measurement.
                    </p>
                    <p>{m.quality.evidence_support}</p>
                  </>
                )}
                {m.reference && (
                  <p className="muted">
                    Division reference: {m.reference.version} · reviewed{" "}
                    {m.reference.verified_at}. No long-term target weight is
                    inferred.
                  </p>
                )}
                <p className="muted">
                  Excluded:{" "}
                  {m.excluded.map((k) => labelMap[k]).join(", ") || "None"}.{" "}
                  {m.insight}
                </p>
              </div>
            ))}
          <p className="muted">
            {compare.status} · {compare.note}
          </p>
          <a
            className="source"
            href={compare.source}
            target="_blank"
            rel="noreferrer"
          >
            Source record · snapshot {compare.source_date} · reviewed{" "}
            {compare.verified_at} ↗
          </a>
          <details className="fighter-provenance">
            <summary>Sources, division history and data quality</summary>
            <ul>
              {compare.division_history?.map((d) => (
                <li key={d.name}>
                  {d.name}: {d.context}
                </li>
              ))}
            </ul>
            <ul>
              {compare.issues?.map((issue) => (
                <li key={issue}>{issue}</li>
              ))}
            </ul>
            {compare.sources?.map((source) => (
              <p key={source.id}>
                <a
                  className="source"
                  href={source.url}
                  target="_blank"
                  rel="noreferrer"
                >
                  {source.publisher} · {source.id}
                </a>{" "}
                · observed {source.observed_at} ·{" "}
                {source.method.replaceAll("_", " ")} · rights:{" "}
                {source.rights.replaceAll("_", " ")}. {source.attribution}{" "}
                {source.license_url && (
                  <a
                    href={source.license_url}
                    className="source"
                    target="_blank"
                    rel="noreferrer"
                  >
                    {source.license_reference}
                  </a>
                )}
              </p>
            ))}
            <div
              className="comparison-table"
              tabIndex={0}
              role="region"
              aria-label="Field provenance table"
            >
              <table>
                <caption>Field-level source references</caption>
                <thead>
                  <tr>
                    <th>Field</th>
                    <th>Source IDs</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(compare.field_sources ?? {}).map(
                    ([key, refs]) => (
                      <tr key={key}>
                        <td>{key.replaceAll("_", " ")}</td>
                        <td>{refs.join(", ")}</td>
                      </tr>
                    ),
                  )}
                </tbody>
              </table>
            </div>
            <p>
              Professional record:{" "}
              {compare.record
                ? `${compare.record.wins}–${compare.record.losses}–${compare.record.draws}, ${compare.record.no_contests} no contests, as of ${compare.record.as_of}. ${compare.record.scope}`
                : "Not verified in this snapshot."}{" "}
              Athlete professional statistics are not collected.
            </p>
            {compare.statistics?.map((stat) => (
              <p key={stat.name}>
                {stat.name}: {stat.value} {stat.unit} · as of {stat.as_of}.{" "}
                {stat.scope}
              </p>
            ))}
          </details>
        </Card>
      )}
      <Card title="Saved comparisons">
        {favorites.length ? (
          favorites.map((f) => (
            <div className="settings-row" key={f.id}>
              <div>
                <h3>{f.data.match.fighter.name}</h3>
                <small className="muted">
                  {f.data.match.score == null
                    ? "Unscored"
                    : `${f.data.match.score}/100`}{" "}
                  · saved {new Date(f.created_at).toLocaleDateString()}
                </small>
              </div>
              <div className="button-row">
                <button
                  className="secondary"
                  onClick={() => {
                    setSnapshot(f);
                    setSelected(f.data.match.fighter);
                    setWeights(f.data.weights);
                  }}
                >
                  Load weights
                </button>
                <button
                  className="icon-button"
                  aria-label={`Remove ${f.data.match.fighter.name}`}
                  onClick={() =>
                    run(async () => {
                      await api(`/comparisons/${f.id}`, "DELETE");
                      setFavorites(await api("/comparisons"));
                    })
                  }
                >
                  <X size={17} />
                </button>
              </div>
            </div>
          ))
        ) : (
          <Empty>Save a comparison using the heart beside a match.</Empty>
        )}
      </Card>
      <Card
        title="Fighter data providers"
        eyebrow="PROVENANCE / EXPLICIT REFRESH"
      >
        <p>
          Curated subset, not a comprehensive UFC database.{" "}
          {dataStatus?.count ?? all.length} validated snapshots. No automated
          scraping or new web verification occurs on refresh.
        </p>
        {dataStatus?.quality && (
          <details>
            <summary>Coverage and data quality report</summary>
            <p>
              {Object.entries(dataStatus.quality.categories)
                .map(([key, value]) => `${key}: ${value}`)
                .join("; ")}
              . Records with unestablished redistribution rights:{" "}
              {dataStatus.quality.unestablished_rights}.
            </p>
            <p>
              {Object.entries(dataStatus.quality.supported_fields)
                .map(([key, value]) => `${key.replaceAll("_", " ")}: ${value}`)
                .join("; ")}
              . Counts reflect fields supplied, not independently verified
              competence or a complete UFC roster.
            </p>
          </details>
        )}
        {dataStatus?.unavailable_records.map((r) => (
          <p key={r.id}>
            {r.id}: {r.reason}
          </p>
        ))}
        <label className="field">
          Refresh provider
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
          >
            {dataStatus?.providers.map((p) => (
              <option key={p.id} value={p.id} disabled={!p.available}>
                {p.id} — {p.description}
                {p.available ? "" : " (unavailable)"}
              </option>
            ))}
          </select>
        </label>
        <button
          className="secondary"
          disabled={busy}
          onClick={() =>
            run(async () => {
              const result = await api<{ message: string; changed: number }>(
                `/fighter-data/refresh?provider=${provider}`,
                "POST",
              );
              setSnapshot(null);
              setSelected(null);
              setRefreshKey((n) => n + 1);
              notify(`${result.message} ${result.changed} changed.`);
            })
          }
        >
          Refresh reviewed fighter data
        </button>
        <p className="muted">
          Refresh preserves prior data revisions and saved comparisons. It never
          changes athlete inputs or training plans.{" "}
          {dataStatus?.revisions.length ?? 0} archived content revisions.
        </p>
      </Card>
      <details className="method">
        <summary>How the resemblance score works</summary>
        <p>{ranking?.method}</p>
      </details>
    </>
  );
}
