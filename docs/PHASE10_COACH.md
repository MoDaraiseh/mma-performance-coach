# Phase 10 — context-aware coaching and controlled actions

All changes are confined to `mma-performance-coach/`. Normal athlete data is preserved. Tests use disposable databases and mocked providers. Schema head remains **0006**; additional assessment snapshots use the existing versioned aggregate table.

## Audit and baseline

Baseline **251 backend / 12 frontend tests passed**. Existing architecture: `mma_agent.py` calls optional OpenAI Responses with structured JSON, two bounded attempts, timeout/token controls and local fallback; `coach_actions.py` builds deterministic candidates; account-scoped endpoints in `main.py` bind previews to input IDs and workout history; approval revalidates and appends versions in a serialized account transaction. Daily quotas, conversation retention tooling and server-only keys already existed.

Gaps resolved: limited recent history/benchmark context; no conversational reschedule, frequency, assessment or evidence-gated progression capability; no primary-question authorization gate on provider-selected actions; unsafe claims checked only in the answer, not limitations; unrequested provider tool outputs ignored; older same-day check-ins selected on ties; sparse offline progress explanations; and no dedicated reproducible adversarial evaluation set.

## Current context and evidence

`coach_context.py` assembles only account-authorized records and computed summaries:

| Information | Selection and meaning |
| --- | --- |
| Profile/goals | Goal, age group, availability, technical experience and discipline priorities; self-reported |
| Physical measurements | Height, weight and wingspan only for relevant physical/relative-strength questions; no proficiency inferred |
| Athletic assessment | Relevant observed inputs versus estimates, explicit missing domains and observation-date uncertainty |
| Training | Current usable approved week; stale prescriptions are withheld; deterministic exercise alternatives |
| Workouts | Latest five by completion/recording date, up to four performance entries and three sets each; no free-text notes |
| Recovery/progress | Latest three check-in summaries; newest version resolves same-day ties; comparable benchmark deltas and workload analytics |
| Progression | Up to six deterministic decisions when relevant and the approved plan is usable; missing/stale recovery prevents increases |
| Nutrition | Current usable targets, diet/allergy restrictions and meal summary; estimates clearly identified; stale targets withheld |
| Reassessments | Three newest account reports via a bounded query; source/profile/check-in/workout mismatches mark historical context |
| Fighters | Current validated database snapshots, recalculated default-weight top three, coverage/missing dimensions/differences/source links/freshness; custom lab rankings can differ |

No names/country fields, raw workout/check-in notes or complete conversation history are forwarded. Questions and goal/discipline prose can themselves contain personal information; this is minimization, not guaranteed anonymization. All prose and imported content are untrusted data. Whole optional sections are dropped toward a 14,000-character context budget, with omissions disclosed; serialized input above 16,000 characters causes explicit local fallback. Restrictions are never silently removed to fit. Schema/instructions also consume tokens, so character bounds are not token counts.

The UI discloses context sections and omissions. Self-reported observations are not independently verified facts. Relative strength, benchmark changes, workload and fighter resemblance are deterministic calculations. Energy expenditure, periodization and progression thresholds are estimates/heuristics, not clinical diagnoses or validated professional-potential predictions.

## Specialized guidance

Offline coaching now renders discipline priorities, recorded consistency, comparable strength/endurance changes, recovery gates, plateau explanations, current macro/energy context and missing-data limitations. Exercise alternatives and nutrition replacements use the existing curated catalogs. Fighter explanations use deterministic database-backed read results, even when AI is requested: no provider generates professional records or statistics. No current record is invented when absent.

Optional OpenAI may explain selected context and return one typed intent. It has no executable tools or database access. All numerical calculations remain in services. Unknown questions/actions, unsupported foods, ambiguous days, unsafe cuts and medical/rehabilitation requests produce clarification/referral or an explicit unsupported result. Limited English phrase recognition is deliberate; unsupported paraphrases may need rewording. A model cannot authorize a capability absent from the primary user request.

## Action contract and persistence

| Typed intent | Validated behavior |
| --- | --- |
| `reschedule_workout` | One unlogged future uncoached session moves to an unoccupied permitted weekday, preserving identity/exercises/duration. Rejects coached-class moves and adjacent hard-session clusters, including week boundaries. No booking is claimed. |
| `exercise_substitution` | Existing equipment/category-compatible catalog alternatives, retaining the timed block; previous load suggestions are removed. |
| `change_frequency` | From a chosen future week, within saved availability and workload/recovery caps. Earlier weeks and logs remain unchanged. It cannot implicitly authorize exercise progression. Actual feasible days may be capped. |
| `meal_swap` | Current plan and catalog-backed protein/grain/produce replacement, including named known foods; exclusions/portions/macros/groceries revalidated. Unknown foods are not silently ignored. |
| `request_assessment` | Recomputes athletic observations/estimates/missing domains; approval saves a separate `coach_assessment` snapshot. It does not collect a new measurement, change a plan, or advance the week 4/8/12 checkpoint. |
| `explain_matches` | Read-only deterministic explanation using the athlete's current profile and default matching weights. No change proposal or plan write. |
| `progress_training` | Reuses actual comparable performance and fresh stable recovery, with existing conservative overload rules and deloads. No evidence, fatigue, failed/missed work or unavailable headroom prevents unsupported increases. |
| Existing `shorten_session` / `schedule_boxing` | Preserved: shorten one unlogged session or focus an existing non-contact solo block; no inferred coached class or contact practice. |

The request produces a typed interpretation, backend validation and a persisted **preview**. It never applies a plan automatically. UI shows old/new session or week, every affected future prescription, meal differences, or assessment observations. Explicit approval rechecks ownership, unresolved status, profile/training/nutrition/preferences/check-in bindings, reassessment IDs, workout record IDs and deterministic candidate equality before appending a version. The stored canonical request permission must still match intent arguments. Legacy proposals retain their existing validation path.

Approval confirms the actual saved target/version/record ID only after persistence. Rejection leaves plans intact. Stale input/history returns 409. Existing plan lineage and logs remain recoverable; progression previews do not advance completed reassessment checkpoints. Assessment snapshots and proposals remain personal account history/export data and are deleted with the account; conversation/draft retention rules do not automatically prune these audit records.

## Provider reliability, cost and privacy

- `OPENAI_API_KEY` stays server-side. `OPENAI_MODEL` retains the existing default `gpt-4o-mini`; model identifier syntax is checked. Operators must choose a model supporting the schema; no live model compatibility or availability is asserted.
- Fixed Responses endpoint, `store:false`, strict JSON Schema, Pydantic validation, **1,100 maximum output tokens**, **at most two HTTP attempts**, **20-second overall deadline**, 12-second request timeout (3-second connect). Only bounded transient connection/429/503 cases retry; invalid output is not retried indefinitely.
- At most **one intent** per response. Extra provider function/computer/web-search calls are rejected and never executed. There is no shell, browser, email, external URL fetching or general-purpose agent loop.
- Numeric/prose guards reject unsupported numbers and selected unsafe/premature-persistence claims in both answer and limitations. These are defense in depth, not proof of semantic truth. A model can still produce an incorrect non-numeric explanation; human review remains necessary.
- Provider unavailability, refusal, incomplete/invalid output, oversize context and invalid configuration fall back to visibly labeled local guidance. A legitimate user-requested local proposal may still be prepared, always requiring approval.
- `AI_PER_DAY` defaults to **20 requested AI interactions per account/day**. It counts requested use, including gated/offline outcomes, not just billed calls. Worst-case retry count is two attempts per eligible interaction; quotas are not a currency budget. Input tokens include schema/instructions. Prices vary by configured model: consult [official pricing](https://developers.openai.com/api/docs/pricing).
- Usage logs contain attempts, returned input/output token counts, outcome, duration, context character count and interpreted proposal count; no key, raw provider body, question, athlete name or measurements. A zero token count when usage was not returned means unknown/not reported, not guaranteed zero cost. `tool_proposals` counts interpreted intents before final action validation.
- `store:false` is a request setting, not a claim that the provider has no retention. Users opt into the provider in the UI; review provider data terms and your own deployment policy.

[Official OpenAI structured-output documentation](https://developers.openai.com/api/docs/guides/structured-outputs) was reviewed for strict-schema use and refusal/incomplete handling. **No live or paid provider call was made for this delivery.**

## Reproducible evaluations

`backend/tests/fixtures/coach_evaluations.json` has **18 named scenarios**: beginner, experienced, incomplete measurements, conflicting diets/allergies, schedule changes, missing fighter/food data, unsafe cuts, medical requests, hallucinated fighter claims, stale plans, prompt injection, conflicting arguments, unsafe secondary output, unauthorized tools, invented numbers, provider timeout and invalid schema. `test_phase10.py` executes mocked output/transport behavior with exact mode/call-count/action expectations. Additional API/unit tests check ownership, duplicate approval, permission tampering, rejected/stale changes, preserved history/checkpoints, recovery/real-performance progression, catalog recognition and schedule constraints.

From `backend/`:

```powershell
..\.venv\Scripts\python.exe -m pytest tests/test_phase10.py -q
..\.venv\Scripts\python.exe tools/evaluate_coach.py --limit 3
```

The second command is a synthetic offline smoke report, not the mocked adversarial evaluator or an automatic domain-quality grade. Optional live smoke evaluation requires **all** of `--live`, `MMA_LIVE_COACH_EVAL=1`, a server-side `OPENAI_API_KEY` and an explicit `OPENAI_MODEL`. It uses synthetic incomplete context, no athlete database and no plan writes. Default limit three cases; maximum ten per invocation. Calls may incur charges. Run only after deliberate operator configuration:

```powershell
# Set the three environment variables securely; never put the key in frontend code.
..\.venv\Scripts\python.exe tools/evaluate_coach.py --live --limit 3
```

Output records modes, answers and usage for manual review. It does not establish live sports-coaching quality, prompt-injection immunity or model safety. Live evaluation was **not run**.

## Verification and remaining limits

Baseline: 251 backend / 12 frontend passed. Updated checks and browser results are recorded below after completion. Initial focused browser execution passed both assessment/reschedule flows but failed two context-disclosure assertions due to a test race with conversation refresh. Waiting for the latest user bubble corrected the test; the next four desktop/mobile cases passed without retries.

Remaining: no independent sports-science/medical/nutrition/security sign-off, no live-provider quality validation, no robust semantic hallucination proof, limited natural-language recognition, no arbitrary multi-tool/autonomous workflows, no coached-class booking, no calendar integration and no clinical/competition weight-management advice. Current offline classifier/context rules are deterministic heuristics; unknowns and specialist review remain explicit. Production identity/PostgreSQL/multiworker/restore gates from Phase 6 remain unchanged and are not represented as newly verified.

## Actual test results and evidence

| Check | Actual result |
| --- | --- |
| Baseline | 251 backend / 12 frontend passed |
| Final backend | **278 passed**; one existing upstream Starlette/httpx deprecation; [output](evidence/phase10/pytest.txt) |
| New Phase 10 coverage | 18 mocked scenarios plus nine additional API/unit cases; [evaluation coverage](evidence/phase10/evaluation-coverage.json) |
| Frontend | **12 passed** |
| Full real Edge regression | **123 passed, zero failed, seven intentional skips**, zero flaky cases or suite errors in 7.9 minutes; [report](evidence/phase10/browser-results.json) |
| Focused correction | Four desktop/mobile cases passed; [report](evidence/phase10/browser-focused-fixed.json) |
| Final UI/context confirmation | **35 passed**, zero failures/skips, native exit 0 in 2.3 minutes across all five widths; new auto-scroll assertions, existing coach/nutrition actions and complete journeys; [report](evidence/phase10/browser-final-coach.json) |
| App/browser TypeScript, Vite | Passed |
| Ruff / Prettier | Passed; 53 Python files formatted |
| A4 reports | Four reports / 14 pages; text and safe-margin checks passed; [checks](evidence/phase10/print-checks.json) |
| Offline CLI smoke | Three synthetic cases, no provider calls or writes; [output](evidence/phase10/offline-evaluation.json) |
| Live provider | **Not run**; no live quality or account/model compatibility claim |

The full browser matrix exercised 1440/1920/768/390/375 px, including all ten new assessment/reschedule/frequency/context cases and existing nutrition, coaching, account, progression, accessibility, responsive and complete-journey checks. Seven skips avoid duplicate PDF checks and desktop-only drawer checks. Installed headless Edge and viewport emulation are not physical-device or cross-engine verification. Targeted axe checks reported zero violations in the new reschedule flows, not full accessibility certification.

Visual review found a further UX defect: new replies could remain below the chat's internal scroll position while welcome prompts stayed visible. The smallest fix scrolls that container to its latest reply after message refresh, without animation. A browser assertion checks the latest response bottom lies in the chat viewport. This UI correction and the final historical-context flag are covered by the subsequent targeted coach/journey rerun; results are recorded below. Existing approvals and plan generation are unchanged by scrolling.

Screenshots are in [the evidence directory](evidence/phase10/), including [desktop preview](evidence/phase10/desktop-1440-phase10-reschedule.png) and [mobile preview](evidence/phase10/mobile-375-phase10-reschedule.png). Full-page captures can place a fixed header at its current scroll position. Desktop and mobile previews were visually inspected. Original tracker tracked files remain unchanged; athlete QA uses disposable databases and no configured personal provider key.
