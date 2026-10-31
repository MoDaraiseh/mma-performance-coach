# AI configuration and operational boundaries

Offline coaching works without credentials. Configure only the MMA project's server environment or app-root .env; never place an API key in Vite/frontend variables, source files, screenshots or exports. No live provider call was made during release acceptance.

Optional configuration: OPENAI_API_KEY, OPENAI_MODEL (default gpt-4 o-mini), AI_ALLOWED_MODELS (matching allowlist), AI_MAX_OUTPUT_TOKENS (default1100), AI_MAX_CONTEXT_CHARS (default16000), AI_PER_DAY (default20 per account), AI_GLOBAL_DAILY (1000 outbound-attempt reservations), AI_GLOBAL_MONTHLY (10000). Restart the backend after changes. Production also needs the identity/database/HTTPS settings in DEPLOYMENT.md.

A logical configured request reserves two outbound attempts against shared UTC-day/calendar-month counters before invocation, including failures; there are no refunds. At most two attempts and a20-second overall deadline are allowed. The full serialized provider request is bounded to40,000 ASCII characters. These character/attempt controls are not exact token-dollar spend caps. Output limits and usage are recorded; no raw personal prompt is added to operator usage metrics. Deliberate user conversations are account records governed separately by retention.

AI_INPUT_USD_PER_MILLION and AI_OUTPUT_USD_PER_MILLION default0 (unconfigured estimates). Operators must verify current rates with the provider, configure actual project spending controls and monitor billing; local estimates are not invoice reconciliation. No pricing or production capacity guarantee is made.

The context service selects current usable approved plans, profile facts, recent logs/recovery/progress and qualified summaries. User notes and imported descriptions are untrusted data. Structured output does not grant permissions: typed intent arguments, canonical user request, ownership, source versions and deterministic candidates are validated by the backend. Every saved change requires explicit user approval. Stale or unsupported actions fail visibly. Numerical formulas, nutrient values and fighter evidence come from deterministic/source-backed services.

Configured-provider testing uses mocked transports, including successful structured output, invalid output, injected tool attempts, schema/claim rejection, bounded retry/timeout/error fallback, quotas and global budgets. Live quality remains unverified. The18-scenario fixture is backend/tests/fixtures/coach_evaluations.json. Offline smoke: from backend run `..\.venv\Scripts\python.exe tools/evaluate_coach.py --limit 18`. Optional live evaluation additionally requires explicit authorization, --live, MMA_LIVE_COACH_EVAL=1, an explicit model and a server key; it can incur charges and was not run.

Offline answers are finite rules, not equivalent to a live model or qualified coach. Semantic safety and explanation accuracy still need human review. See PHASE10_COACH.md, PHASE13_INFRASTRUCTURE.md and PHASE14_ACCEPTANCE.md.
