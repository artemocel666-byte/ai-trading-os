# AI Trading OS

AI Trading OS is a safety-first foundation for a future modular Forex analysis and paper-trading platform. The current repository implements only infrastructure: API health/status endpoints, async PostgreSQL persistence, a scheduler heartbeat, Telegram command foundations, strict configuration, and safety contracts.

## Current Status

- Current project phase: phase_5_manual_review_layer_foundation.
- Phase 5 manual review layer foundation is complete: immutable read-only reports, a stdout-only
  CLI viewer, an authorized Telegram `/review` command, and deterministic in-memory comparison and
  quality summaries over existing disabled/non-actionable Phase 4G/4F/4E artifacts.
- Trading strategy: not implemented.
- Real trading: disabled and unsupported.
- External integrations: disabled by default.
- Telegram: can run in disabled mode without a token.
- Phase 3D: deterministic analysis snapshot/readiness report foundation only.
- Phase 3E: local Telegram readiness reports only.
- Phase 3F: neutral readiness scheduler/snapshot digest foundation only.
- Phase 3G: manual Telegram `/digest` readiness digest command only.
- Phase 3H: neutral scheduled digest delivery foundation only, disabled by default.
- Phase 3I: persistent neutral digest delivery audit foundation only.
- Merged Phase 3I snapshot versioning/evidence: schema versions, completeness ratios, candle
  evidence timestamps, and an unwired read-only agent contract only.
- Phase 4A: signal contract foundation only; contracts default to `NOT_ACTIONABLE`.
- Phase 4B: strategy rule specification foundation only; rule specs and rule sets default to
  disabled/non-actionable.
- Phase 4C: strategy ruleset validation foundation only; validates `StrategyRuleSet` structure
  without evaluating market data.
- Phase 4D: strategy ruleset registry/fixture foundation only; loads disabled built-in
  `StrategyRuleSet` fixtures and validates them through the Phase 4C validator.
- Phase 4E: disabled pipeline report shell foundation only; summarizes Phase 4D registry snapshots
  in deterministic non-actionable reports.
- Phase 4F: strategy rule evaluation foundation only; resolves rule `field_ref` values against real
  analysis snapshots and produces deterministic, unconditionally non-actionable evaluation reports.
- Phase 4G: strategy decision composition foundation only; composes evaluation reports across every
  registered ruleset into one deterministic, unconditionally non-actionable pipeline decision. This
  completes Phase 4.
- Phase 5: read-only manual review layer only; it presents existing reports without re-evaluating
  rules, reading market data, persisting review output, or enabling runtime action.

## Safety Warning

This project must not open, modify, or close real financial positions. It contains no broker order API, no real account credentials, and no automatic trading execution.

## Phase 2 Status

Phase 2 adds hardened runtime defaults, stronger secret redaction, strict UTC normalization, typed
`Candle` and `EconomicEvent` domain models, typed provider contracts, disabled-by-default provider
adapters, production Twelve Data and FMP adapters tested through `httpx.MockTransport`, and
architecture/safety verification. It still does not add strategy, indicators, analysis, signals,
OpenAI calls, or trading execution.

## Phase 3A Status

Phase 3A adds duplicate-safe storage/query repositories for normalized closed candles and economic
events, deterministic data-quality snapshots, and historical replay utilities for tests. It does not
add strategy, indicators, technical analysis, scoring, signals, AI agents, OpenAI calls, paper
trading, broker APIs, order execution, or real trading.

## Phase 3B Status

Phase 3B adds a deterministic, closed-candle-only feature engine that transforms existing normalized
Phase 3A candles and economic events into typed immutable feature snapshots. It computes descriptive
features only, such as latest close, candle counts, simple returns, rolling close means, ranges,
volume summaries, true ranges, economic-event counts, and quality issues. It does not produce
trading decisions, setup scoring, directions, recommendations, signals, AI output, broker activity,
paper trading, order execution, or real trading.

## Phase 3C Status

Phase 3C adds a deterministic, closed-candle-only indicator/context foundation over the Phase 3B
feature engine. It produces typed immutable context snapshots with descriptive close statistics,
return distribution summaries, moving averages, range and candle-shape summaries, event metadata,
time context, and deterministic data-quality issues. It does not produce strategy decisions, setup
scoring, confidence scoring, trade directions, recommendations, signals, AI output, broker activity,
paper trading, order execution, or real trading.

## Phase 3D Status

Phase 3D adds deterministic analysis snapshots and readiness reports over the Phase 3A storage,
Phase 3B feature, and Phase 3C context foundations. It answers neutral infrastructure questions
about window completeness, source inputs, excluded data, quality/context issues, attached summaries,
and no-future-data proof. It does not produce strategy decisions, setup scoring, confidence scoring,
trade directions, recommendations, signals, AI output, broker activity, paper trading, order
execution, or real trading.

## Phase 3E Status

Phase 3E adds a local Telegram readiness-report slice over the deterministic Phase 3D analysis
snapshot foundation. It wires the Telegram bot to the real UnitOfWork-backed analysis service,
adds `/snapshot EURUSD M15`, formats Russian readiness reports with exactly one leading semantic
emoji, and provides `scripts/seed_local_snapshot_data.py` for local demo candles/events. It still
does not produce strategy decisions, setup scoring, confidence scoring, trade directions,
recommendations, signals, AI output, broker activity, paper trading, order execution, or real
trading.

## Phase 3F Status

Phase 3F adds a deterministic readiness scheduler and snapshot digest foundation. It plans neutral
readiness windows for configured pairs/timeframes, resolves the latest fully closed M15/H1 boundary,
aggregates Phase 3D snapshot readiness states, creates deterministic deduplication keys, and builds
Telegram-safe readiness digest payload text. It does not send automatic Telegram messages, produce
strategy decisions, setup scoring, confidence scoring, trade directions, recommendations, signals,
AI output, broker activity, paper trading, order execution, or real trading.

## Phase 3G Status

Phase 3G adds a manual Telegram `/digest` command over the Phase 3F readiness digest service. The
command returns Russian, neutral readiness digest text for the default EURUSD M15/H1 schedule or a
single requested pair/timeframe. It does not add automatic Telegram delivery, provider calls,
strategy decisions, setup scoring, confidence scoring, trade directions, recommendations, signals,
AI output, broker activity, paper trading, order execution, or real trading.

## Phase 3H Status

Phase 3H adds a neutral scheduled digest delivery foundation. It can decide whether a readiness
digest is due on a tick, build the existing readiness digest payload, pass it to a mockable
notification sender, and skip duplicate deduplication keys. Scheduled delivery is disabled by
default and no automatic delivery loop is registered in the worker. It does not add provider calls,
AI output, strategy decisions, setup scoring, confidence scoring, trade directions, recommendations,
signals, broker activity, paper trading, order execution, or real trading.

## Phase 3I Digest Audit Status

Phase 3I adds persistent audit storage for neutral scheduled readiness digest delivery records. It
stores delivered digest deduplication keys, delivery timestamps, sender names, project phase,
readiness status/counts, included pair/timeframe summary, and a neutral payload preview. It does not
store secrets, Telegram tokens, or chat IDs. Scheduled delivery remains disabled by default, and this
phase does not add provider calls, AI output, strategy decisions, setup scoring, confidence scoring,
trade directions, recommendations, signals, broker activity, paper trading, order execution, or real
trading.

## Phase 4A Status

Phase 4A starts Phase 4 but is contract-only. It adds immutable signal contract models, validation
rules, deterministic JSON serialization, and deterministic fingerprinting for future signal objects.
Contracts default to `NOT_ACTIONABLE` and are not recommendations. Phase 4A does not generate
signals, does not provide trading recommendations, does not calculate entries/stops/targets, does
not calculate position size, does not call AI/OpenAI/LLM services, does not send Telegram signals,
does not use broker APIs, does not execute orders, and does not enable paper or real trading.

## Phase 4B Status

Phase 4B is strategy rule specification foundation only. It adds immutable rule-specification
models, operator/category/severity enums, validation rules, deterministic JSON serialization, and
deterministic fingerprinting for future rule specifications. Rule specs and rule sets default to
disabled and non-actionable. Phase 4B does not evaluate rules, does not generate signals, does not
provide trading recommendations, does not calculate entries/stops/targets, does not calculate
position size, does not calculate setup score or confidence, does not call AI/OpenAI/LLM services,
does not send Telegram signals, does not use broker APIs, does not execute orders, and does not
enable paper or real trading.

## Phase 4C Status

Phase 4C is strategy ruleset validation foundation only. It adds immutable validation issue/report
models and a deterministic validator that checks `StrategyRuleSet` structure, disabled flags, static
field-reference registry membership, category/field compatibility, forbidden action/scoring/
confidence language, and validation-report determinism. Phase 4C does not evaluate rules against
market data, indicators, economic events, context snapshots, analysis snapshots, or signal
contracts. It does not generate signals, does not provide trading recommendations, does not
calculate entries/stops/targets, does not calculate position size, does not calculate setup score or
confidence, does not call AI/OpenAI/LLM services, does not send Telegram signals, does not use
broker APIs, does not execute orders, and does not enable paper or real trading. Rule specs and rule
sets remain disabled/non-actionable.

## Phase 4D Status

Phase 4D is strategy ruleset registry and fixture foundation only. It adds immutable registry item
and snapshot models plus a deterministic built-in registry of disabled foundation `StrategyRuleSet`
fixtures. The registry validates each fixture through the Phase 4C validator and can produce a
deterministic, non-actionable snapshot/fingerprint of available rulesets.

Phase 4D does not evaluate rules against market data, candles, indicators, economic events, context
snapshots, analysis snapshots, or signal contracts. It does not generate signals, does not provide
trading recommendations, does not calculate entries/stops/targets, does not calculate position
size, does not calculate setup score or confidence, does not call AI/OpenAI/LLM services, does not
send Telegram signals, does not use broker APIs, does not execute orders, and does not enable paper
or real trading. Rule specs, rule sets, registry items, and registry snapshots remain
disabled/non-actionable.

## Merged Phase 3I Snapshot Versioning Status

Phase 3I adds a snapshot versioning and evidence foundation over Phase 3A-3H. It adds a
`schema_version` field to feature, context, and analysis snapshot metadata; a deterministic
`data_completeness_ratio` (used candles / expected candles, bounded to `[0, 1]`) on feature and
context snapshots; candle-level `used_candle_open_times`/`used_candle_close_times` evidence
timestamps on the feature candle summary; and an unwired, read-only `AnalysisAgent` Protocol
alongside the existing `AgentReport`/`EvidenceReference` contract in `app/schemas/agents.py`. It
does not implement or wire any agent, does not add a Decision Engine, registry, or Risk Engine, and
does not add strategy decisions, setup scoring, confidence scoring, trade directions,
recommendations, signals, AI output, broker activity, paper trading, order execution, or real
trading.

## Phase 4E Status

Phase 4E is disabled pipeline report shell foundation only. It adds immutable blocker/report models
and a disabled shell that consumes only Phase 4D registry snapshots, counts registered rule sets,
records registry validation status, records whether everything remains disabled/non-actionable, and
produces deterministic disabled pipeline reports.

Phase 4E does not evaluate rules against market data, candles, indicators, economic events, context
snapshots, analysis snapshots, or signal contracts. It is not a decision engine. It does not
generate signals, does not provide trading recommendations, does not calculate entries/stops/
targets, does not calculate position size, does not calculate setup score or confidence, does not
call AI/OpenAI/LLM services, does not send Telegram signals, does not use broker APIs, does not
execute orders, and does not enable paper or real trading. Pipeline reports remain
disabled/non-actionable.

## Phase 4F Status

Phase 4F is strategy rule evaluation foundation only. It adds a field resolver registry
(`app/domain/strategy_field_resolver.py`) that resolves the three existing `field_ref` values
(`data_quality.closed_candles_available`, `market_context.snapshot_ready`,
`time_filter.session_name`) against a real `AnalysisSnapshot`, and a `StrategyRuleEvaluator`
(`app/domain/strategy_rule_evaluator.py`) that applies rule operators
(EXISTS/NOT_EXISTS/EQ/NE/GT/GTE/LT/LTE/BETWEEN/IN) and aggregates results by severity into a
deterministic `RuleSetEvaluationReport` (`BLOCKED`/`NOT_READY`/`READY_FOR_REVIEW`).

Phase 4F does not construct a `SignalContract`, does not become a decision engine, does not
evaluate against live/enabled data sources (no provider calls), does not calculate
entries/stops/targets, does not calculate position size, does not call AI/OpenAI/LLM services, does
not send Telegram signals, does not use broker APIs, does not execute orders, and does not enable
paper or real trading. `RuleSetEvaluationReport.is_actionable` is unconditionally `False`, enforced
by the model itself.

## Phase 4G Status — Phase 4 Complete

Phase 4G is strategy decision composition foundation only. It adds `StrategyDecisionComposer`
(`app/domain/strategy_decision_composer.py`), which loads every registered ruleset from the Phase
4D registry, skips structurally invalid ones (recorded as `SkippedRuleset` entries), evaluates the
valid ones through the Phase 4F `StrategyRuleEvaluator`, and combines the results into one
deterministic `PipelineDecisionReport` (`BLOCKED`/`NOT_READY`/`READY_FOR_REVIEW`).

This closes Phase 4: the full declarative rule pipeline (declare -> validate -> register -> evaluate
-> compose) now runs end to end against real `AnalysisSnapshot` data. Phase 4G does not construct a
`SignalContract`, does not calculate entries/stops/targets, does not calculate position size, does
not call AI/OpenAI/LLM services, does not send Telegram signals, does not use broker APIs, does not
execute orders, and does not enable paper or real trading. `PipelineDecisionReport.is_actionable` is
unconditionally `False`, enforced by the model itself. Real `SignalContract` price-level
construction is deliberately deferred to Phase 6, where actual price levels are needed for Telegram
signal delivery.

## Phase 5 Status

Phase 5 is a read-only manual review layer over already-created disabled/non-actionable Phase
4G/4F/4E report artifacts. It adds immutable manual review models and a report builder, deterministic
text/JSON rendering, the stdout-only `scripts/manual_review_report.py` viewer, an authorized manual
Telegram `/review` command, and in-memory report comparison and completeness summaries. The builder
accepts an existing Phase 4G `PipelineDecisionReport`; local CLI and Telegram review use the safe
Phase 4E disabled registry report because it requires no market data, database, provider, scheduler,
or messaging call.

Phase 5 does not evaluate rules against market data, generate signals, provide recommendations,
calculate price levels, position size, setup score, or confidence, call AI/OpenAI/LLM services, send
automatic Telegram alerts, use broker APIs, execute orders, or enable paper or real trading. It is
not a strategy engine or decision engine. Runtime commands print or reply only and do not write
files or persist manual review reports.

Run the local viewer with:

```bash
uv run python scripts/manual_review_report.py
uv run python scripts/manual_review_report.py --format text
uv run python scripts/manual_review_report.py --format json
```

## Prerequisites

- Python 3.12
- uv
- Docker and Docker Compose
- PostgreSQL for local non-Docker development

## Mac and Linux Setup

```bash
uv sync
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:create_app --factory --reload
```

## Windows Setup

Use PowerShell with Python 3.12 and uv installed:

```powershell
uv sync
Copy-Item .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:create_app --factory --reload
```

## Docker Startup

The default configuration starts without paid API keys. Compose uses `.env` as an optional
local override file and does not use `.env.example` at runtime:

```bash
docker compose up --build
```

The Compose stack runs PostgreSQL, applies Alembic migrations, starts the API, starts the worker, and starts the Telegram process in disabled mode when `TELEGRAM_ENABLED=false`.

## Environment Configuration

Copy `.env.example` to `.env` for local overrides. The example keeps:

```text
TELEGRAM_ENABLED=false
OPENAI_ENABLED=false
MARKET_DATA_ENABLED=false
CALENDAR_ENABLED=false
SCAN_ENABLED=false
SCHEDULED_DIGEST_ENABLED=false
```

Secrets are required only when the matching integration is enabled.

## Migrations

```bash
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "message"
```

## Tests and Checks

```bash
make check
make test
make lint
make typecheck
```

Integration tests require a reachable `TEST_DATABASE_URL`; otherwise they skip with a clear message.

## API Endpoints

- `GET /health`
- `GET /ready`
- `GET /api/v1/system/status`
- `POST /api/v1/system/scanning/start`
- `POST /api/v1/system/scanning/stop`

State-changing endpoints require the `X-Internal-API-Key` header.
The default development key is rejected when `APP_ENV` is not `development`.

## Telegram Disabled Mode

When `TELEGRAM_ENABLED=false`, the bot process starts and remains healthy without creating a Telegram client or making network calls. When enabled, a bot token, allowed user ID, and allowed chat ID are required.
For a local live Telegram test, see `docs/operations.md` and configure `TELEGRAM_BOT_TOKEN`,
`TELEGRAM_ALLOWED_USER_ID`, and `TELEGRAM_ALLOWED_CHAT_ID` in an uncommitted `.env` file.

## Current Limitations

- No strategy, signals, OpenAI calls, backtesting, position sizing, broker execution, or real trading.
- `/scan_now` explicitly remains disconnected from analysis snapshots and does not fabricate a scan result.
- `/snapshot` returns readiness reports only and does not produce trading guidance.
- `/digest` returns manual readiness digests only and does not produce trading guidance.
- `/review` returns a short authorized read-only manual review summary and persists nothing.
- Scheduled digest delivery is disabled by default and has no automatic worker loop.
- Worker jobs only update heartbeat and run foundation health checks.

## Directory Overview

- `app/api`: FastAPI adapters.
- `app/core`: configuration, errors, logging, time, security, enums.
- `app/domain`: provider and repository contracts plus financial value objects.
- `app/persistence`: SQLAlchemy models, repositories, unit of work.
- `app/services`: application services.
- `app/telegram`: Telegram authorization, formatting, commands, delivery.
- `app/scheduler`: worker process and jobs.
- `docs`: product, architecture, database, operations, and implementation notes.
- `tests`: unit, integration, and contract tests.
