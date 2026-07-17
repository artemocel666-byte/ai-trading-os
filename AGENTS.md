# AI Trading OS Agent Guide

AI Trading OS is a foundation for a future Forex analysis and paper-trading platform.

Current project phase: phase_3i_snapshot_versioning_and_evidence_foundation.
Phase 3I is limited to descriptive snapshot schema versioning, deterministic data-completeness
ratios, candle-level evidence timestamps, and an unwired, read-only agent contract, all layered
over the existing Phase 3A-3H foundation. External integrations are disabled by default. The
project contains no strategy, no signals, no broker order APIs, no paper trading, and no real
trading. Phase 4 has not started.

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
- Never add strategy, setup scoring, LONG/SHORT direction, buy/sell recommendations, paper trading,
  broker APIs, order execution, or real trading while working in foundation phases.
- While working in Phase 3H, output is limited to neutral readiness reports and readiness digests.
  Scheduled delivery must remain disabled by default. Do not add Telegram trading signals, entry
  guidance, LONG/SHORT advice, buy/sell recommendations, automatic runtime loops, or paper-trading
  actions.
- While working in Phase 3I, schema versioning, data-completeness ratios, and evidence timestamps
  are descriptive-only and must not influence readiness status, quality checks, or any branching
  decision. The `AnalysisAgent` Protocol in `app/schemas/agents.py` must remain unimplemented and
  unwired to any service, route, or scheduler in this phase. Do not add concrete agents, a Decision
  Engine, a registry, or trading terms.
- Never fabricate market data, calendar data, agent evidence, or scan results.
- LLM output may explain deterministic results only; it must not change prices, scores, risk, or rejected decisions.
- Update documentation when architecture or safety boundaries change.

## Definition of Done

Code is complete only when tests, formatting, linting, type checking, migrations, and relevant Docker checks have been run or a truthful limitation is documented in `docs/foundation-report.md`.
