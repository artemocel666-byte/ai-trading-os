# Operations

## Startup

Docker startup:

```bash
docker compose up --build
```

Compose reads `.env` as an optional local runtime override. `.env.example` is only a template.
The API is bound to `127.0.0.1:8000` by default, and PostgreSQL is not exposed to the host by
the default Compose stack.

Local startup:

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:create_app --factory --reload
```

## Shutdown

Use `Ctrl+C` for foreground Compose or:

```bash
docker compose down
```

The worker and Telegram process handle shutdown signals and dispose database resources.

## Migrations

Apply migrations:

```bash
uv run alembic upgrade head
```

Create a migration:

```bash
uv run alembic revision --autogenerate -m "message"
```

## Logs

Application processes emit structured JSON logs with service, component, event, level, timestamp, request IDs where available, and redacted secret-like fields.

## Health Checks

- `GET /health` checks API liveness only.
- `GET /ready` checks database connectivity and schema access.
- `GET /api/v1/system/status` reports phase, scan state, worker heartbeat, enabled integrations, database status, and safety flags.

## Disabled Integrations

The default `.env.example` disables Telegram, OpenAI, market data, calendar, and scanning. Disabled providers raise typed errors before external calls.

## Local Telegram Readiness Demo

Phase 3E can run a local readiness report without live market or calendar integrations. Start
PostgreSQL, migrate the schema, seed deterministic local demo data, and then use `/snapshot EURUSD
M15` in the authorized Telegram chat.

```bash
docker compose up -d postgres
docker compose run --rm migrate alembic upgrade head
docker compose run --rm api python -m scripts.seed_local_snapshot_data
```

To use a real Telegram chat, create a bot token with BotFather, set `TELEGRAM_ENABLED=true`,
`TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USER_ID`, and `TELEGRAM_ALLOWED_CHAT_ID` in `.env`, then
start the bot service. The `/snapshot` command returns readiness reports only; it does not produce
trading guidance or paper-trading actions.

Phase 3F adds an internal readiness digest planner that can prepare neutral digest payloads for
configured pair/timeframe windows. It does not schedule automatic Telegram delivery by itself and
does not call market-data, calendar, AI, or broker services. Any future delivery path must keep
Telegram output limited to readiness reporting text.

Phase 3G exposes that digest foundation through a manual Telegram `/digest` command. `/digest`
returns the default EURUSD M15/H1 readiness digest, and `/digest EURUSD M15` returns a single
pair/timeframe digest. The command remains read-only and neutral; it does not schedule automatic
delivery, call providers, call AI services, contact brokers, or produce trading guidance.

Phase 3H adds a neutral scheduled digest delivery foundation. It can decide whether a digest is due,
build the same readiness payload, pass it to a mockable notification sender, and skip duplicate
deduplication keys. It is disabled by default with `SCHEDULED_DIGEST_ENABLED=false`, and the worker
does not register an automatic scheduled digest job. It does not call providers, AI services, or
brokers, and it does not produce trading guidance.

Phase 3I persists neutral scheduled digest delivery audit records in
`scheduled_digest_deliveries`. The table stores deduplication keys, delivery timestamps, sender
names, readiness status/counts, item summaries, and a neutral payload preview. It does not store
Telegram tokens, chat IDs, provider secrets, strategy decisions, trading guidance, or broker data.
Scheduled delivery remains disabled by default.

Phase 4A adds signal contract domain models only. It does not add runtime jobs, API endpoints,
Telegram signal handlers, persistence migrations, provider calls, AI/OpenAI/LLM calls, broker
calls, order execution, paper trading, or real trading. Contracts default to `NOT_ACTIONABLE` and
must not be treated as trading recommendations.

Phase 4B adds strategy rule specification domain models only. It does not evaluate rules, register
runtime jobs, expose API endpoints, add Telegram signal handlers, add persistence migrations, call
providers, call AI/OpenAI/LLM services, contact brokers, calculate scores, or produce trading
guidance. Rule specs and rule sets default to disabled/non-actionable.

Phase 4C adds strategy ruleset validation domain models and a validation-only checker for
`StrategyRuleSet` structure. It does not evaluate rules against market data, indicators, events,
context snapshots, analysis snapshots, or signal contracts. It does not register runtime jobs,
expose API endpoints, add Telegram signal handlers, add persistence migrations, call providers, call
AI/OpenAI/LLM services, contact brokers, calculate scores/confidence, or produce trading guidance.
Rule specs and rule sets remain disabled/non-actionable.

Phase 4D adds strategy ruleset registry and fixture domain models only. It loads disabled built-in
`StrategyRuleSet` fixtures, validates them through the Phase 4C validator, and produces
deterministic non-actionable registry snapshots. It does not evaluate rules against market data,
indicators, events, context snapshots, analysis snapshots, or signal contracts. It does not register
runtime jobs, expose API endpoints, add Telegram signal handlers, add persistence migrations, call
providers, call AI/OpenAI/LLM services, contact brokers, calculate scores/confidence, or produce
trading guidance. Rule specs, rule sets, registry items, and registry snapshots remain
disabled/non-actionable.

## Telegram Bot Local Setup

Create the bot in Telegram before enabling the `bot` service:

1. Open `@BotFather`.
2. Send `/newbot`.
3. Choose a display name, for example `AI Trading OS Local`.
4. Choose a username ending in `bot`, for example `ai_trading_os_local_bot`.
5. Copy the token. Telegram bot tokens look like `1234567890:AA...`; keep this value secret and
   never commit it.

Find the allowed Telegram identity:

- `TELEGRAM_ALLOWED_USER_ID`: send `/start` to `@userinfobot` or `@getmyid_bot` and copy the
  numeric `Id`.
- `TELEGRAM_ALLOWED_CHAT_ID`: for a direct private chat with the bot, this is usually the same as
  `TELEGRAM_ALLOWED_USER_ID`.
- To confirm the chat ID, send `/start` to your new bot and open
  `https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getUpdates` in a browser. Use the numeric
  `message.chat.id` value from the JSON response.

Create a local `.env` file in the repository root. Do not commit `.env`.

```env
APP_ENV=development
DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os
INTERNAL_API_KEY=development-internal-key-change-me

TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=1234567890:AA_REPLACE_WITH_REAL_SECRET
TELEGRAM_ALLOWED_USER_ID=123456789
TELEGRAM_ALLOWED_CHAT_ID=123456789

OPENAI_ENABLED=false
MARKET_DATA_ENABLED=false
CALENDAR_ENABLED=false
SCAN_ENABLED=false
SCHEDULED_DIGEST_ENABLED=false
SCHEDULED_DIGEST_INTERVAL_MINUTES=60
```

Prepare the local database and demo data:

```bash
docker compose up -d postgres
docker compose run --rm migrate alembic upgrade head
docker compose run --rm api python -m scripts.seed_local_snapshot_data
```

Start only the Telegram bot service:

```bash
docker compose up --build bot
```

Then send these commands to the bot in Telegram:

```text
/start
/status
/snapshot EURUSD M15
/digest
/digest EURUSD M15
```

Expected behavior: `/snapshot EURUSD M15` returns a Russian readiness report with one leading emoji.
`/digest` returns a Russian readiness digest with one leading emoji. These commands must not contain
LONG/SHORT directions, entry guidance, buy/sell recommendations, or paper-trade actions.

## Common Failure Cases

- Missing Telegram token while Telegram is enabled: configuration validation fails.
- PostgreSQL unavailable: readiness fails and state changes cannot persist.
- Migrations not applied: readiness returns not ready.
- Wrong internal API key: state-changing API calls return `UNAUTHORIZED`.

## Safe Recovery

1. Check `docker compose ps`.
2. Inspect `docker compose logs --no-color`.
3. Confirm PostgreSQL is healthy.
4. Run `uv run alembic upgrade head`.
5. Recheck `/ready` and `/api/v1/system/status`.
