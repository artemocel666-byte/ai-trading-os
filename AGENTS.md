# AI Trading OS Agent Guide

AI Trading OS is a foundation for a future Forex analysis and paper-trading platform.

Current project phase: phase_5_manual_review_layer_foundation.
Phase 5 adds a read-only manual review layer over existing disabled/non-actionable Phase 4G/4F/4E
reports: immutable review models, deterministic rendering and comparison, a stdout-only CLI, and an
authorized Telegram `/review` command. It does not re-evaluate rules, read market data, persist
review output, or enable runtime action. External integrations are disabled by default. The project
contains no strategy engine, no signal generation engine, no `SignalContract` construction, no
broker order APIs, no paper trading, and no real trading.

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
  construction is out of scope until Phase 8 (Telegram signal delivery, renumbered from the
  original Phase 6 when the roadmap gained Phase 6 snapshot-backed review and Phase 7 Chief AI
  explanations).
- While working in Phase 5, manual review domain code may consume only already-created immutable
  Phase 4G/4F/4E report artifacts. It must not call the Phase 4 evaluator/composer, read market data,
  use a database/session/UoW, call providers, register scheduler jobs, persist reports, or write
  runtime files. Reports, comparisons, CLI output, and `/review` replies must remain read-only,
  disabled/non-actionable, and contain explicit no-signal messaging. Do not add rule evaluation,
  strategy or decision engines, setup/confidence scoring, AI/OpenAI/LLM calls, automatic Telegram
  alerts, broker APIs, order execution, paper trading, or real trading.
- Never fabricate market data, calendar data, agent evidence, or scan results.
- LLM output may explain deterministic results only; it must not change prices, scores, risk, or rejected decisions.
- Update documentation when architecture or safety boundaries change.

## Definition of Done

Code is complete only when tests, formatting, linting, type checking, migrations, and relevant Docker checks have been run or a truthful limitation is documented in `docs/foundation-report.md`.
