# AI Trading OS Agent Guide

AI Trading OS is a foundation for a future Forex analysis and paper-trading platform.

Current project phase: phase_4b_strategy_rule_specification_foundation.
Phase 4B is strategy rule specification foundation only. It defines typed immutable contracts for
future rule specifications and validation/serialization rules only. External integrations are
disabled by default. The project contains no strategy engine, no rule evaluation, no signal
generation engine, no broker order APIs, no paper trading, and no real trading.

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
- Never add strategy execution logic, rule evaluation, setup scoring, buy/sell recommendations,
  paper trading, broker APIs, order execution, or real trading while working in foundation phases.
  In Phase 4A, `LONG`/`SHORT` may appear only as contract enum values, not as generated
  recommendations.
- While working in Phase 4B, strategy/rule vocabulary is allowed only inside explicit strategy rule
  specification domain models and their tests/docs. Rule specs and rule sets must default to
  disabled/non-actionable. Do not add rule evaluation, signal generation, setup scoring, confidence
  scoring, Telegram signal sending, API signal routes, scheduler signal jobs, broker APIs, order
  execution, automatic runtime loops, or paper-trading actions.
- Never fabricate market data, calendar data, agent evidence, or scan results.
- LLM output may explain deterministic results only; it must not change prices, scores, risk, or rejected decisions.
- Update documentation when architecture or safety boundaries change.

## Definition of Done

Code is complete only when tests, formatting, linting, type checking, migrations, and relevant Docker checks have been run or a truthful limitation is documented in `docs/foundation-report.md`.
