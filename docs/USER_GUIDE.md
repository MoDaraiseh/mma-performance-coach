# Local user guide

Use the exact setup commands in README.md. Keep this app's database and configuration separate from the original tracker. Existing databases need a verified backup before Alembic upgrade to head0008; the acceptance tests do not migrate your personal database.

1. Open http://127.0.0.1:8000. Explore the synthetic demo or choose Build my athlete profile. Save the one-time recovery token privately; signing out ends the current session, not the recovery credential. Settings lists sessions and can revoke them. Never share recovery tokens or exports.
2. Complete the assessment wizard. Enter everyday weight, actual measurements, independent discipline experience, optional comparable benchmark results, availability, equipment, goals and dietary preferences. Mark measured versus estimated information honestly. Draft saving lets you return later.
3. Review Physical analysis and Fighting style. Division references are not weigh-in eligibility or a weight-cut target. Technical priorities reflect self-report/access/preferences and need your coach's judgment.
4. In Comparison lab inspect top matches, coverage, source dates and differences. Change weights or search/filter/manual compare. Saving a favorite preserves a snapshot; a high score does not establish professional skill.
5. Review Training and each session. Log the actual date, status, completed sets, repetitions, load, RPE and duration. Record missed/failed sessions honestly. Recovery feedback can hold progression; recommendations do not silently modify the approved plan.
6. In Nutrition review estimates, portions, ingredients and restrictions. Check packaging/certification and cross-contact with suppliers. Preview substitutions, inspect changed totals, then explicitly approve or reject. Profile/plan/preference changes can make old nutrition stale; regenerate deliberately without deleting history.
7. In Progress add dated check-ins and comparable tests. Choose a date window and development metric; expand the accessible chart data table. Set a Monday cycle anchor if you want due-versus-completed adherence. Sparse evidence is qualified, and records apply to the selected window. Narrow long windows when coverage warnings appear.
8. Request week4/8/12 reassessment. Review proposed changes and source versions. Approve only the intended changes; rejection leaves the current plan intact. If a proposal becomes stale, request a new preview.
9. Ask AI coach supported questions about your current plan, progression, discipline priorities, meals or comparisons. Offline mode uses local rules. Optional provider mode can fail or fall back and is explicitly labeled. A response is not proof that data changed: look for persisted approval confirmation.
10. Export private account JSON from Settings; use Progress CSV/JSON or browser Print for the current report. Keep downloads secure. Delete account data only when ready: confirmation removes application account records and sessions, but does not delete an external IdP account or operator backups/previous downloads.

For loading/network errors, retry after connectivity recovers. A401 returns to account recovery; a409 means the source changed and needs a fresh preview. Unavailable numerical recommendations are intentionally withheld for unsupported/minor/clinical/unsafe requests. Stop symptom-provoking training and seek qualified assessment; contact practice and competition nutrition require professional supervision.

This is a verified local release candidate, with automated checks rather than independent professional approval. See KNOWN_LIMITATIONS.md and PHASE14_ACCEPTANCE.md before broader use.


Phase15: Training now labels general development versus supervised amateur intent. Edit competition intent deliberately and review a new proposal when prompted; it never authorizes contact or increases workload automatically. The exercise library includes a Mobility filter and objective text. Nutrition supports selected nut/seed/avocado alternatives through the existing replacement preview; inspect the full ingredient/portion differences before approving. New catalog v3 may request reviewed regeneration of earlier meal plans; saved history is retained. Generic food labels are not certification or cross-contact assurance. Verify packaged ingredients and professional guidance for allergies.

## Features in detail

The full feature list, as it stood at release candidate `1.0.0-rc.17`. The README has a short summary.

- Six-step editable athlete assessment, backend draft saving, optional measurements, metric/imperial input, independent discipline history and benchmark evidence labels.
- Persistent local accounts with hashed high-entropy recovery tokens, HttpOnly SameSite cookies, user-scoped records, data download and complete account deletion.
- Physical calculations, explainable scale-weight division references, historical women's featherweight distinction, conservative target-weight uncertainty, and exploratory style priorities.
- Nineteen source-reviewed UFC fighter study snapshots (11 men, eight women; all attributed Wikipedia records under CC BY-SA 4.0), field-level provenance, division history, manual comparisons, configurable deterministic ranking and coverage, height/reach charts, immutable favorites, and explicit provider refresh with archived data revisions.
- A 12-week conservative training roadmap with phases, deloads, recovery constraints, equipment substitutions, session details and duplicate-safe workout logging.
- Estimated resting/TDEE/maintenance ranges, optional bounded goal adjustments, macro guidance, seven-day source-backed portions, dietary exclusions, meal feedback, substitution previews and approved nutrition versions.
- Weekly check-ins, weight/sleep/fatigue and benchmark charts, recorded personal bests, plan completion, comparable benchmark changes and reassessment reports.
- Contextual local coaching and optional structured OpenAI explanations/intents, using current usable plan/meal and recent progress summaries. Validated training/meal edits require explicit approval; provider failures fall back locally.
- Preview/approve/reject plan revisions, retained plan versions and original inputs, stale proposal protection. No chat text directly mutates a saved plan.
- Responsive charcoal/red UI, local font assets, accessible labels and print views. JSON export includes all user records and plan versions.
