# AI Trading OS

AI Trading OS is a safety-first foundation for a future modular Forex analysis and paper-trading platform. The current repository implements only infrastructure: API health/status endpoints, async PostgreSQL persistence, a scheduler heartbeat, Telegram command foundations, strict configuration, and safety contracts.

## Current Status

- Current project phase: phase_3h_scheduled_digest_delivery_foundation.
- Trading strategy: not implemented.
- Real trading: disabled and unsupported.
- External integrations: disabled by default.
- Telegram: can run in disabled mode without a token.
- Phase 3D: deterministic analysis snapshot/readiness report foundation only.
- Phase 3E: local Telegram readiness reports only.
- Phase 3F: neutral readiness scheduler/snapshot digest foundation only.
- Phase 3G: manual Telegram `/digest` readiness digest command only.
- Phase 3H: neutral scheduled digest delivery foundation only, disabled by default.

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
signals, broker activity, paper trading, order execution, or real trading. Phase 4 has not started.

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
