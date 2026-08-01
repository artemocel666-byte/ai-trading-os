# AI Trading OS Agent Guide

AI Trading OS is a foundation for a future Forex analysis and paper-trading platform.

Current project phase: phase_8c_explanation_delivery_foundation.
Phase 8C delivers explanations through a separate `/explain EURUSD M15` command, gated by two flags
that are both off by default (`OPENAI_ENABLED`, `EXPLANATION_DELIVERY_ENABLED`). The deterministic
report is always sent in full; an explanation is appended only after passing Phase 8A validation,
and any failure — disabled, unreachable, rejected, or out of time — becomes one honest line under
the report. `/review` is untouched and still spends nothing. This closes Phase 8.
Phase 8B adds the OpenAI adapter behind the Phase 8A contract: plain httpx, `OPENAI_ENABLED=false`
by default, and wired to nothing (8C does that). It cannot return unchecked text — `explain_validated`
runs the Phase 8A validator and the outcome carries text only when the answer was accepted. The
prompt contains our own serialized contract and nothing a stranger wrote.
Phase 8A defines what a future Chief AI may be given (`ExplanationInput`) and how its answer is
checked before anyone reads it. It contains no provider, no network call, no key, and is wired to
nothing. Validation is fail-closed: any finding means the deterministic Russian text is used
instead. The model may repeat numbers it was given and no others.
Phase 7D-2 replays the built-in rules over stored history and reports how each one behaved, so the
Phase 7C thresholds can be derived from an observed distribution instead of two live windows. The
replay is read-only, never scheduled, and changes no threshold by itself: it measures, and a
threshold moves only through a deliberate edit that records its evidence.
Phase 7D-1 adds a manual historical backfill script so later calibration has a real distribution to
work from. It is deliberately never scheduled: on a timer it would burn provider quota repeatedly.
It stores candles only and reports a suspected provider truncation rather than silently accepting a
short response.
Phase 7B adds economic-calendar ingestion and the two event rules that consume it, bringing the
rule set to eleven across four rulesets (data quality, market context, event context, time filter).
Calendar ingestion is gated by two flags that are both off by default (`CALENDAR_ENABLED`,
`CALENDAR_INGESTION_ENABLED`). The ingestion window straddles the tick, reaching forward over
announced releases, because calendars are published ahead of time; the analysis snapshot still only
exposes what happened at or before `as_of`, so the rules read backwards. Rules stay descriptive:
they answer "can this window be trusted" and "what regime is this", never "what should be traded".
No directions, no price levels, no scoring, no AI. Rules and rulesets stay `enabled=False`. External
integrations remain disabled by default. The project contains no strategy engine, no signal
generation engine, no `SignalContract` construction, no broker order APIs, no paper trading, and no
real trading.

## Start and Checks

- Install: `uv sync`
- Start Docker stack: `docker compose up --build`
- Migrate: `uv run alembic upgrade head`
- Test: `uv run pytest`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Type-check: `uv run mypy app`
- Full check: `make check`

## Repository Layout

- `app/api`: API adapters.
- `app/services`: application services.
- `app/domain`: domain value objects and contracts.
- `app/persistence`: database models, repositories, unit of work.
- `app/telegram`: Telegram adapter.
- `app/scheduler`: worker process.
- `docs`: detailed project documentation.

## Rules

- Dependency direction is adapters -> application services -> domain.
- Domain code must not import FastAPI, Telegram, SQLAlchemy, PostgreSQL, APScheduler, OpenAI, market-data providers, or calendar providers.
- Use async SQLAlchemy sessions only; one `AsyncSession` per unit of work or task.
- Use `Decimal` for financial values. Do not use binary floating point for money, prices, percentages, or risk.
- Store timestamps in UTC; present user-facing time in Europe/Stockholm when needed.
- Telegram user-facing text must be Russian.
- Every Telegram message must contain exactly one semantic emoji at the beginning.
- Never add real trading execution, broker order APIs, real account credentials, or live position management.
- Never add strategy execution logic, setup scoring, buy/sell recommendations, paper trading,
  broker APIs, order execution, or real trading while working in foundation phases. In Phase 4A,
  `LONG`/`SHORT` may appear only as contract enum values, not as generated recommendations. Rule
  evaluation against real market data is allowed starting in Phase 4F, strictly bounded by the
  Phase 4F rule below.
- While working in Phase 3H, output is limited to neutral readiness reports and readiness digests.
  Scheduled delivery must remain disabled by default. Do not add Telegram trading signals, entry
  guidance, LONG/SHORT advice, buy/sell recommendations, automatic runtime loops, or paper-trading
  actions.
- While working in the merged Phase 3I snapshot versioning/evidence slice, schema versioning,
  data-completeness ratios, and evidence timestamps are descriptive-only and must not influence
  readiness status, quality checks, or any branching decision. The `AnalysisAgent` Protocol in
  `app/schemas/agents.py` must remain unimplemented and unwired to any service, route, or
  scheduler.
- While working in Phase 4D, strategy registry vocabulary is allowed only inside explicit ruleset
  registry/fixture domain models, the registry loader, and their tests/docs. Rule specs, rule sets,
  registry items, and registry snapshots must remain disabled/non-actionable. Do not evaluate rules
  against candles, indicators, economic events, context snapshots, analysis snapshots, or signal
  contracts. Do not add strategy engines, signal generation, setup scoring, confidence scoring,
  Telegram signal sending, API signal routes, scheduler signal jobs, broker APIs, order execution,
  automatic runtime loops, or paper-trading actions.
- While working in Phase 4E, disabled pipeline report vocabulary is allowed only inside explicit
  pipeline report domain models, the disabled report shell, and their tests/docs. Pipeline reports
  must remain disabled/non-actionable. The shell may consume only Phase 4D registry snapshots. Do
  not evaluate rules against candles, indicators, economic events, context snapshots, analysis
  snapshots, or signal contracts. Do not add strategy engines, decision engines, signal generation,
  setup scoring, confidence scoring, Telegram signal sending, API signal routes, scheduler signal
  jobs, broker APIs, order execution, automatic runtime loops, or paper-trading actions.
- While working in Phase 4F, the evaluator (`app/domain/strategy_field_resolver.py`,
  `app/domain/strategy_rule_evaluator.py`) may only read `AnalysisSnapshot`,
  `MarketFeatureSnapshot`, and `MarketContextSnapshot`. It must never import
  `app.persistence`, `app.telegram`, `app.scheduler`, `app.api`, or `app.domain.entities.signal_contract`.
  It must never construct a `SignalContract`, calculate entries/stops/targets, calculate position
  size, or send a Telegram message. `RuleSetEvaluationReport.is_actionable` must remain `False`
  unconditionally, enforced by the model itself, not by caller discipline.
- While working in Phase 4G, the composer (`app/domain/strategy_decision_composer.py`) may only
  read the Phase 4D registry and `AnalysisSnapshot`/`MarketFeatureSnapshot`/`MarketContextSnapshot`
  through the Phase 4F evaluator. It must never import `app.domain.entities.signal_contract` or
  construct a `SignalContract`, and must never import `app.persistence`, `app.telegram`,
  `app.scheduler`, or `app.api`. `PipelineDecisionReport.is_actionable` must remain `False`
  unconditionally, enforced by the model itself. Real price-level (entry/stop/take-profit)
  construction is out of scope until Phase 9A (signals, delivery, and paper trading). See `PLANS.md`
  for the authoritative roadmap; the tail was renumbered on 2026-07-22 when Phase 7 was redefined as
  live data and real analysis.
- While working in Phase 5, manual review domain code may consume only already-created immutable
  Phase 4G/4F/4E report artifacts. It must not call the Phase 4 evaluator/composer, read market data,
  use a database/session/UoW, call providers, register scheduler jobs, persist reports, or write
  runtime files. Reports, comparisons, CLI output, and `/review` replies must remain read-only,
  disabled/non-actionable, and contain explicit no-signal messaging. Do not add rule evaluation,
  strategy or decision engines, setup/confidence scoring, AI/OpenAI/LLM calls, automatic Telegram
  alerts, broker APIs, order execution, paper trading, or real trading.
- While working in Phase 6, the snapshot-backed review (`app/domain/snapshot_review.py`,
  `app/telegram/snapshot_review_formatter.py`) may build an `AnalysisSnapshot` (only in the Telegram
  command layer, via the injected `AnalysisService`) and run the Phase 4G composer over it. The
  Phase 6 domain module must receive an already-built `AnalysisSnapshot` and must not import
  `app.persistence`, `app.adapters`, `app.scheduler`, `app.api`, or
  `app.domain.entities.signal_contract`. It must never construct a `SignalContract`, calculate price
  levels, call AI, or send an automatic/unsolicited message. `/review` output (both structural and
  snapshot-backed) must remain read-only and non-actionable.
- While working in Phase 7A, the ingestion service (`app/services/market_data_ingestion_service.py`,
  `app/domain/entities/ingestion.py`) may call `MarketDataProvider.get_closed_candles` and write
  candles through `candles.upsert_many`. It must depend on the provider Protocol, never a concrete
  adapter, and must not import `app.telegram`, `app.api`, or
  `app.domain.entities.signal_contract`. It must never produce signals, directions, price levels,
  scoring, AI output, or user-facing messages. Both `MARKET_DATA_ENABLED` and
  `MARKET_DATA_INGESTION_ENABLED` must stay `false` by default. An empty provider response is a
  normal outcome (closed market), not a failure, and one failing pair must not abort the others.
- While working in Phase 7C, built-in rules (`app/domain/strategy_ruleset_registry.py`) and their
  resolvers (`app/domain/strategy_field_resolver.py`) may read values the snapshot already computes,
  and nothing else: 7C adds no new indicator math, which belongs to the Phase 3B/3C engines. Rules
  must stay descriptive — no direction, no entry, no price levels, no scoring, no recommendation —
  and must keep `enabled=False` so they remain non-actionable. Do not use `EXISTS`/`NOT_EXISTS` for
  an analytical rule: those only test presence and pass on empty data. A resolver must return `None`
  when its source is missing rather than substituting a value, and must never raise or divide by
  zero. Every threshold must be calibrated against real observed data and the evidence recorded in
  the phase verification report.
- While working in Phase 7B, calendar ingestion
  (`app/services/economic_calendar_ingestion_service.py`,
  `app/domain/entities/calendar_ingestion.py`) may call `EconomicCalendarProvider.get_events` and
  write events through `economic_events.upsert_many`, depending on the provider Protocol and never a
  concrete adapter. Both `CALENDAR_ENABLED` and `CALENDAR_INGESTION_ENABLED` stay `false` by
  default. An empty response is a normal outcome (a quiet calendar), not a failure, and provider
  errors are recorded rather than raised into the scheduler. Ingest forward but evaluate backward:
  storing announced releases is legitimate, while surfacing post-`as_of` events into a snapshot
  would break the Phase 3D no-future-data proof and must stay a separate, deliberate decision.
- While working in Phase 7D-1, the backfill
  (`app/services/market_data_backfill_service.py`, `scripts/backfill_market_data.py`) must stay a
  manual script and must never be registered as a scheduler job. It must chunk requests inside
  `provider_max_request_range_days`, pace them with a delay, and flag a chunk as possibly truncated
  when the oldest returned candle sits far after the requested start — silently accepting a short
  response would corrupt every later calibration. A run that failed or looked truncated must not
  report success, and the CLI must exit non-zero.
- While working in Phase 7D-2, the replay (`app/domain/rule_replay.py`,
  `app/domain/rule_calibration.py`, `app/domain/entities/calibration.py`,
  `scripts/replay_rules.py`) must stay read-only and must never be registered as a scheduler job.
  The domain modules take candles and events as arguments and must not import `app.persistence`,
  a session, or a unit of work — the Phase 4G boundary keeps the composer out of anything that owns
  storage, so loading history belongs to the caller. Replay must evaluate through the real
  `AnalysisEngine` and Phase 4G composer rather than a lookalike, otherwise the measured pass rates
  say nothing about `/review`. It must never rewrite thresholds automatically: a threshold change is
  a reviewable edit that records the percentile and sample size it came from. A rule that never
  fired across real history is a defect to report, not a rule that passed.
- While working in Phase 8A, the explanation contract (`app/domain/entities/explanation.py`,
  `app/domain/explanation_contract.py`) must stay pure domain code: no `httpx`, no OpenAI, no
  `app.persistence`, `app.adapters`, `app.telegram`, `app.api`, or `app.scheduler`, and no service,
  route, command, or job may reference it — 8A ships unwired, and the adapter arrives in 8B. Do not
  reuse the older scored Chief AI request stub in `app/schemas/agents.py`: it demands fields the
  pipeline never produces and the safety tests ban. `ExplanationInput` carries no direction, price
  level, position size, or scoring field, and stays non-actionable. Validation returns findings
  rather than raising, and an explanation counts as accepted only when nothing was found; a caller
  that sees any finding must fall back to the deterministic text rather than repair the answer. The
  actionable-text check must cover Russian as well as English — the Phase 5 detector alone matches
  "buy", not "покупай", and this project speaks Russian to its user.
- While working in Phase 8B, the explanation adapter (`app/adapters/openai_explanations.py`) is the
  only file in the project allowed to reach a model, and only it is exempt from the `OpenAI`/`LLM`
  term ban — every trading-behaviour ban still applies to it. It must not import `app.persistence`,
  `app.telegram`, `app.api`, `app.scheduler`, or `app.schemas.agents`, and no service, command,
  route, or job may reference it until 8C. `OPENAI_ENABLED` stays `false` by default and the
  disabled provider must raise before any network call. The API key travels in the `Authorization`
  header, never a query parameter. Prompts may contain only the Phase 8A contract's own serialized
  content — no market text, no third-party strings. `explain_validated` must run the Phase 8A
  validator, and a rejected answer must leave no readable text in the outcome. Cap output tokens so
  a runaway generation cannot become an unbounded bill.
- While working in Phase 8C, the explanation may only reach a user through the `/explain` command a
  person types. No service, scheduler job, or API route may build the provider or call it: an
  automatic path would spend money and show model text to someone who never asked. The deterministic
  report must be sent in full in every case, including when the model fails — the explanation is an
  appendix and says so. Never show text that failed validation; report the issue codes instead. Both
  `OPENAI_ENABLED` and `EXPLANATION_DELIVERY_ENABLED` default to `false`, and the call must run
  inside `EXPLANATION_BUDGET_SECONDS` so a slow provider cannot hang a Telegram command. `/review`,
  `/snapshot`, `/digest`, and scheduled delivery stay model-free.
- Never fabricate market data, calendar data, agent evidence, or scan results.
- LLM output may explain deterministic results only; it must not change prices, scores, risk, or rejected decisions.
- Update documentation when architecture or safety boundaries change.

## Definition of Done

Code is complete only when tests, formatting, linting, type checking, migrations, and relevant Docker checks have been run or a truthful limitation is documented in `docs/foundation-report.md`.
