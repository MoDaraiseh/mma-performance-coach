# MMA Performance Coach

A local-first training workspace for amateur mixed martial artists. You complete a guided athlete assessment, and the app builds a conservative 12-week training plan and a seven-day meal plan from it. It also tracks workouts and check-ins and compares your measurements with a small, source-referenced set of UFC fighter snapshots. An optional AI coach can explain your plan and propose changes, and nothing is saved until you approve it.

**Stack:** React, TypeScript, Vite and Recharts on the frontend; FastAPI, Pydantic, SQLAlchemy and Alembic on the backend, with SQLite by default and PostgreSQL supported.

> **Status:** release candidate `1.0.0-rc.17`, intended for local use. It has not been publicly deployed, and its training and nutrition guidance has not yet been reviewed by qualified coaches, dietitians or medical professionals. It is not medical or nutritional advice. See [known limitations](docs/KNOWN_LIMITATIONS.md) and the [project history](docs/history/README.md) for the full release record.

## Features

- Six-step editable athlete assessment, backend draft saving, optional measurements, metric/imperial input, independent discipline history and benchmark evidence labels.
- Persistent local accounts with hashed high-entropy recovery tokens, HttpOnly SameSite cookies, user-scoped records, data download and complete account deletion.
- Physical calculations, explainable scale-weight division references, historical women's featherweight distinction, conservative target-weight uncertainty, and exploratory style priorities.
- Nineteen source-reviewed UFC fighter study snapshots (11 men, eight women; 11 official-source records and eight attributed Wikipedia records), field-level provenance, current/history division contexts, manual comparisons, configurable deterministic ranking and coverage, height/reach charts, immutable favorites, and explicit provider refresh with archived data revisions.
- A 12-week conservative training roadmap with phases, deloads, recovery constraints, equipment substitutions, session details and duplicate-safe workout logging.
- Estimated resting/TDEE/maintenance ranges, optional bounded goal adjustments, macro guidance, seven-day source-backed portions, dietary exclusions, meal feedback, substitution previews and approved nutrition versions.
- Weekly check-ins, weight/sleep/fatigue and benchmark charts, recorded personal bests, plan completion, comparable benchmark changes and reassessment reports.
- Contextual local coaching and optional structured OpenAI explanations/intents, using current usable plan/meal and recent progress summaries. Validated training/meal edits require explicit approval; provider failures fall back locally.
- Preview/approve/reject plan revisions, retained plan versions and original inputs, stale proposal protection. No chat text directly mutates a saved plan.
- Responsive charcoal/red UI, local font assets, accessible labels and print views. JSON export includes all user records and plan versions.

## Getting started (Windows)

From this directory, with Python 3.12+ and Node 22.12+ installed:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend\requirements.lock.txt
cd frontend
npm.cmd ci
npm.cmd run build
cd ..\backend
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000**. API documentation: **http://127.0.0.1:8000/docs**. Choose **Explore the demo** or create your athlete profile. Keep the one-time local recovery token private. It restores access after signing out or clearing cookies.

After dependencies are installed, `run-local.cmd` builds the frontend, applies migrations and starts the complete app. `requirements.lock.txt` and `package-lock.json` pin the verified dependency set; `requirements.txt` expresses supported package ranges.

For frontend development, keep the backend running and use a second terminal:

```powershell
cd frontend
npm.cmd run dev
```

Open the URL printed by Vite (normally http://127.0.0.1:5173). Its `/api` proxy connects to port 8000. Restart the backend after building the frontend for the first time: static serving is configured at backend import time.

On macOS/Linux replace `.venv\Scripts\python.exe` with `.venv/bin/python` and `npm.cmd` with `npm`.

## Configuration

Copy `.env.example` to `.env` in the repository root if configuration is needed.

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./mma.db` | Relative SQLite paths resolve against `backend/` regardless of the launch directory, so the default is always `backend/mma.db`. PostgreSQL runtime was verified on the isolated staging candidate (Phases 21-24); production PostgreSQL remains unverified. |
| `OPENAI_API_KEY` | empty | Optional, server-only. All calculations and local coaching work without it. |
| `OPENAI_MODEL` | `gpt-4o-mini` | Configurable Responses API model with structured output support. |
| `COOKIE_SECURE` | `false` | Set `true` behind HTTPS for deployment. |
| `FIGHTER_LICENSED_EXPORT` | empty | Optional server-local licensed fighter JSON export path; no feed bundled. |
| `FIGHTER_LICENSE_REFERENCE` | empty | Operator license reference; must match each export source. |

Alembic imports the same database configuration as the API. Migrations are explicit; startup fails on an uninitialized database. Public deployment remains gated on PostgreSQL, external HTTPS/proxy, identity-policy and operational review; see docs/DEPLOYMENT.md.

## Architecture

```text
frontend/src/
  App.tsx                  workspace shell, overview and assessment views
  api.ts, types.ts         API client and typed contracts
  components/              onboarding, comparison, training, meals, progress, coach
  components/ui.tsx        reusable presentation components
backend/app/
  main.py                  authenticated REST services and AI orchestration
  schemas.py               strict validated input contracts
  db.py                    SQLAlchemy persistence
  analysis.py              physical, division, style, matching, benchmark services
  programs.py              compatibility exports for training/nutrition services
  nutrition*.py            calculations, composition/integrity and strict contracts
  ingredients.py           source-backed USDA catalog; dietary.py screens exclusions
  coach_actions.py         bounded coaching intents and validated candidates
  fighters.py              replaceable provider interface and sourced seed adapter
backend/migrations/        explicit versioned schema migrations
backend/tests/             mathematical and API integration tests
docs/                      methodology, provenance, delivery status
```

The local schema uses users, versioned typed JSON athlete aggregates, public fighter snapshots and reference snapshots. It intentionally does **not** create a separate relational table for every conceptual entity in the brief. Profile experiences, goals and measurements are captured in profile versions; meals and exercises live in immutable plan input/output aggregates. This keeps the local implementation compact while preserving ownership and history. Structured exercise and USDA food catalogs, per-exercise performance logs and nutrition/coaching proposal aggregates now extend this storage model; no relational table is added for every food or exercise.

## Tests and checks

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest -q
cd ..\frontend
npm.cmd run test
npm.cmd run typecheck
npm.cmd run build
npm.cmd audit
```

### Browser QA

Real-browser coverage, fixes and evidence are documented in [the Phase 1 QA report](docs/history/PHASE1_QA.md). The browser suite uses installed Microsoft Edge in headless mode and builds the production frontend first:

```powershell
cd frontend
npm.cmd run test:browser
npm.cmd run test:browser:report
```

Tests cover 1440, 1920, 768, 390 and 375 CSS-pixel widths. They start an isolated API on port **8123**, create a disposable database under this application's ignored `.qa-runtime/`, and force the AI key to empty. They refuse to reuse a server already on that port. Normal `backend/mma.db` is not used. A configured AI interface is tested with a labeled mocked transport; no paid provider call is made.

If Edge is unavailable, install Playwright Chromium with `npm.cmd exec playwright -- install chromium`, then set `$env:PW_CHANNEL='chromium'` before running the suite. Missing browser executables are a failed prerequisite, not a passing or silently skipped browser run. Reports and traces are local; avoid committing test artifacts containing recovery credentials. Saved screenshot evidence dismisses the synthetic account's recovery token first.

For optional print-page text/margin checks and PNG renders:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pip install -r requirements-qa.txt
..\.venv\Scripts\python.exe tests\check_prints.py
```

The app's **Print report** button prints the current view (including the selected training week or nutrition day), with ingredient/method disclosures expanded temporarily. **Settings & data → Download all data** exports all saved versions and includes record types.

Core tests require no paid APIs. Optional backend lint/format uses Ruff, which is not part of the locked requirements; run it without installing into the project environment with `uvx ruff check backend` and `uvx ruff format --check backend` (verified with Ruff 0.17.4). Frontend formatting: `npm.cmd exec prettier -- --check src tools vite.config.ts`.

See [delivery status](docs/history/DELIVERY.md) for exact results and verification limits, [methodology](docs/METHODOLOGY.md) for formulas, and [sources](docs/SOURCES.md) for provenance and data permissions.

## Limitations

This is a working local first version, not the entire production specification. The fighter library is intentionally small (19 dated snapshots, including eight women), and omits unverified current records, most stance data and imagery. Two explicitly historical statistics are descriptive only. Style similarity is excluded without a shared source-backed taxonomy. No live scraping, licensed feed, professional ability score or automated weight cut is implemented.

Training uses conservative templates and a 49-exercise catalog, not clinically reviewed individualized programming. Food values come from a 55-food public-domain USDA subset; meals target general macro guidance, with no complete micronutrient or competition-specific optimization. Structured exclusions and inspired ingredient patterns are supported; budget tiers do not represent real prices, and legacy preference prose is not automatically interpreted. The coach supports whitelisted language-driven previews plus the existing frequency form, rather than arbitrary plan rewriting. Reassessments are user-triggered, with week 4/8/12 prompts in the plan rather than scheduled notifications. Adherence is reported as recorded plan completion, not automatically inferred attendance. Exercise performance logging supports optional actual sets, repetitions, load and timed duration, alongside session duration/effort and separate check-in benchmarks.

Before public deployment: validate the implemented session/rate/production controls under the actual HTTPS proxy and PostgreSQL deployment, decide token-identity suitability, schedule retention and review consent/backup governance, obtain rights for expanded datasets, review training/nutrition with qualified practitioners, and complete real-device, manual assistive-technology and cross-browser QA. The requested responsive browser matrix now runs in headless Edge; a real paid AI response has not been exercised.

## Documentation

| Topic | Document |
| --- | --- |
| User guide | [docs/USER_GUIDE.md](docs/USER_GUIDE.md) |
| Architecture and API | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/API.md](docs/API.md) |
| Methodology (formulas and rules) | [docs/METHODOLOGY.md](docs/METHODOLOGY.md) |
| Data sources and provenance | [docs/SOURCES.md](docs/SOURCES.md), [fighter data license](docs/FIGHTER_SUPPLEMENT_LICENSE.md) |
| AI configuration | [docs/AI_CONFIGURATION.md](docs/AI_CONFIGURATION.md) |
| Deployment and security | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md), [docs/SECURITY.md](docs/SECURITY.md) |
| Testing | [docs/TESTING.md](docs/TESTING.md) |
| Known limitations | [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md) |
| Release status and phase-by-phase history | [docs/history/](docs/history/README.md), [original plan](docs/history/PLAN.md) |

## License

The application code is MIT licensed; see [LICENSE](LICENSE). The license covers the code, not third-party data. The 11 fighter records from official ufc.com athlete profiles are factual measurements with a source link for each field. The eight-record fighter supplement is adapted from Wikipedia under CC BY-SA 4.0; see [docs/FIGHTER_SUPPLEMENT_LICENSE.md](docs/FIGHTER_SUPPLEMENT_LICENSE.md). USDA food data is public domain (CC0). Details: [known limitations](docs/KNOWN_LIMITATIONS.md#public-source-repository) and [sources](docs/SOURCES.md).
