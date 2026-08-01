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

## Market-Data Ingestion (Phase 7A)

Ingestion is the first outbound provider call in the project. It is gated by two flags that both
default to `false`; with either off the worker registers no ingestion job at all:

```env
MARKET_DATA_ENABLED=true
TWELVE_DATA_API_KEY=<your key>
MARKET_DATA_INGESTION_ENABLED=true
MARKET_DATA_INGESTION_INTERVAL_MINUTES=15
MARKET_DATA_INGESTION_LOOKBACK_CANDLES=48
```

The job runs on the configured interval, fetches closed candles for EURUSD M15 and H1 over a rolling
window ending at the latest closed candle boundary, and stores them through the duplicate-safe
repository. Windows deliberately overlap between runs so short provider gaps heal on the next tick.

Operational behaviour:

- Success updates `last_successful_market_fetch`, visible in `GET /api/v1/system/status`.
- An empty provider response is a success, not a failure — the forex market is closed on weekends.
- A failing pair is isolated: the remaining pairs still ingest on the same tick.
- Provider errors are recorded through the standard error path (`last_error` plus an error event)
  and never propagate into the scheduler.
- Default load is roughly 8 provider requests per hour, well inside a free Twelve Data plan.

Ingestion stores candles only. It produces no signals, price levels, scoring, AI output, or messages.

## Economic-Calendar Ingestion (Phase 7B)

Gated by two flags that both default to `false`:

```env
CALENDAR_ENABLED=true
FMP_API_KEY=<your key>
CALENDAR_INGESTION_ENABLED=true
CALENDAR_INGESTION_INTERVAL_MINUTES=60
CALENDAR_INGESTION_LOOKBACK_HOURS=24
CALENDAR_INGESTION_HORIZON_HOURS=72
```

The job fetches scheduled events for the configured currencies (EUR and USD by default) over a
window that straddles the tick: back over recent releases and forward over announced ones, because
calendars are published ahead of time. Events are stored through the duplicate-safe repository, so
overlapping windows update rather than duplicate.

Operational behaviour:

- Success updates `last_successful_calendar_fetch`, visible in `GET /api/v1/system/status`.
- An empty response is a success, not a failure — quiet calendar days exist.
- Provider errors are recorded through the standard error path and never propagate into the
  scheduler.
- **The FMP economic calendar is not available on the free (Basic) plan.** Verified live on
  2026-08-01: `/stable/economic-calendar` answers `402 Restricted Endpoint`, while `/stable/quote`
  with the same key answers `200` — so the key is valid and only the subscription is missing. The
  retired `/api/v3/economic_calendar` answers `403 Legacy Endpoint` for anyone who did not subscribe
  before 2025-08-31. Per FMP's plan comparison, the calendar is included from **Starter** (limited to
  a one-year range) and in full from **Premium**.
- A 402 raises `ProviderPlanRestrictedError` (`PROVIDER_PLAN_RESTRICTED`), deliberately separate
  from `ProviderUnsupportedRequestError`: no parameter change can fix a subscription, so the two
  failures need different reactions. The tick records the error and reports `failed`; the worker
  keeps running.
- With no calendar subscription, set `CALENDAR_ENABLED=false`. Leaving it on spends one request an
  hour and writes the same error into `last_error`, which masks real failures.

Ingestion stores events only. It produces no signals, price levels, scoring, AI output, or messages.

## Historical Market-Data Backfill (Phase 7D-1)

The scheduled ingestion job only ever reaches back a few hours, so history accumulates in real time.
Backfill fills the past on demand, which is what later threshold calibration needs. It is a manual
script and is deliberately never registered as a scheduler job: on a timer it would spend provider
quota repeatedly for data already stored.

```bash
uv run python -m scripts.backfill_market_data --days 180 --timeframe M15 --dry-run
```

```bash
uv run python -m scripts.backfill_market_data --days 180 --timeframe M15
```

Arguments: `--pair` (default `EURUSD`), `--timeframe`, `--days` (default 30), `--chunk-candles`,
`--delay-seconds`, `--dry-run`, `--database-url`.

`--dry-run` prints the chunk plan and the request count without contacting the provider, so quota can
be checked before it is spent. At defaults, 180 days is 18 requests for M15 and 6 for H1. Requests go
oldest-first, so an interrupted run leaves a contiguous recent history rather than islands, and each
chunk is written through the duplicate-safe `candles.upsert_many` — re-running a range updates
instead of duplicating.

Requires `MARKET_DATA_ENABLED=true` and a provider key. With the provider disabled the script says so
and exits 1 without any network call.

### Reading the truncation warning

`app/adapters/twelve_data.py` sends no `outputsize`, so a provider-side result cap could return only
the newest bars of a requested chunk and silently drop the oldest. That would leave invisible holes
in history and corrupt every calibration built on it.

Each chunk is therefore checked by range coverage, not by count: when the oldest returned candle
sits more than a quarter of the chunk duration after the requested start, the chunk is flagged and
the line is printed with `<- POSSIBLY TRUNCATED`. The run then reports that it did not complete
cleanly and the script exits non-zero.

Counting alone would produce false alarms — a chunk spanning a weekend legitimately returns fewer
candles. An empty chunk (closed market) is a success and is never flagged, because a response with no
candles carries no evidence either way.

If a chunk is flagged, treat that range as incomplete: narrow it with a smaller `--chunk-candles` and
re-run that period rather than accepting the stored result.

Backfill stores candles only. It produces no signals, price levels, scoring, AI output, or messages.

## Rule Replay and Calibration (Phase 7D-2)

Replays every built-in rule over stored history and reports how each one behaved. Read-only: it
loads the range once and writes nothing. It is a manual script and is never registered as a
scheduler job, because replaying the same past on a timer produces the same answer forever.

```bash
uv run python -m scripts.replay_rules --days 180 --timeframe M15
```

```bash
uv run python -m scripts.replay_rules --days 180 --timeframe H1 --step-candles 4 --format json
```

Arguments: `--pair` (default `EURUSD`), `--timeframe`, `--days` (default 180), `--window-candles`
(default 12, matching the `/review` window), `--step-candles`, `--format text|json`,
`--database-url`.

Each stored candle close is one `as_of`, so the sampled moments are exactly the moments a window
could have been requested with fresh data. Windows are selected by time, the same way the production
query does, so a gap in history produces a genuinely incomplete window instead of a back-filled one.
`--step-candles` subsamples when a full walk over six months of M15 is slower than needed.

### Reading the output

- **Field distributions** — count, unavailable count, and min/p05/p25/median/p75/p95/max for every
  numeric field, computed by nearest rank so each figure is a value the data actually contained.
  Boolean and session-name fields have no distribution; their rule tallies carry the story.
- **Rule behaviour** — passed/failed/unavailable per rule, the share of evaluated windows in which
  it fired, and a verdict: `NEVER_FIRES`, `RARELY_FIRES`, `OFTEN_FIRES`, `ALWAYS_FIRES`, or
  `NOT_OBSERVED`.

`NEVER_FIRES` and `NOT_OBSERVED` are defects, not clean bills of health: a rule that could not
report anything over months of real data is not protecting anything. The script exits non-zero when
any rule lands there.

Target shape for a healthy rule set: warnings fire on roughly 1–10% of windows, and blocking or
required data-quality rules pass on nearly every window of a healthy feed. A data-quality rule that
fails often is usually measuring our own storage gaps rather than the market.

Replay never edits thresholds. Move them by hand in `app/domain/strategy_ruleset_registry.py`,
recording in a comment which percentile and sample size the new value came from, then re-run and
compare. Recorded evidence lives in `docs/phase7d2-verification-report.md`.

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

Phase 4E adds disabled pipeline report shell domain models only. It consumes only Phase 4D registry
snapshots, summarizes registry counts and blockers, and produces deterministic non-actionable
reports. It is not a decision engine. It does not evaluate rules against market data, indicators,
events, context snapshots, analysis snapshots, or signal contracts. It does not register runtime
jobs, expose API endpoints, add Telegram signal handlers, add persistence migrations, call
providers, call AI/OpenAI/LLM services, contact brokers, calculate scores/confidence, or produce
trading guidance. Pipeline reports remain disabled/non-actionable.

## Phase 5 Manual Review

The Phase 5 local viewer builds a manual review report from the existing Phase 4E disabled registry
report and prints to stdout only. It requires no database, market/calendar provider, Telegram token,
AI service, or broker connection, and it does not write files or persist the report.

```bash
uv run python scripts/manual_review_report.py
uv run python scripts/manual_review_report.py --format text
uv run python scripts/manual_review_report.py --format json
```

Text output includes `READ-ONLY MANUAL REVIEW`, `NO TRADING SIGNAL`,
`NO BUY/SELL RECOMMENDATION`, and `NON-ACTIONABLE`. JSON output uses deterministic key and section
ordering. An incomplete source is reported through typed issues rather than replaced with invented
data.

When Telegram is enabled, an authorized user can request the same read-only summary with `/review`.
The command performs no database read/write, provider call, scheduler registration, automatic alert,
AI call, or persistence. It does not evaluate Phase 4 rules or produce trading guidance.

Phase 6 adds snapshot-backed review. `/review EURUSD M15` builds a real `AnalysisSnapshot` from
stored candles through the existing `AnalysisService`, runs the Phase 4G composer over it, and
presents the resulting pipeline decision through the same read-only manual review layer. The bare
`/review` (no arguments) still returns the structural Phase 4E report. The snapshot-backed path
reads stored candles only; it constructs no `SignalContract`, calculates no price levels, calls no
AI, sends no automatic alert, and produces no trading guidance. Seed local demo candles with
`scripts/seed_local_snapshot_data.py` (see the Local Telegram Readiness Demo above) before trying
`/review EURUSD M15`.

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
TELEGRAM_BOT_TOKEN=PASTE_TELEGRAM_BOT_TOKEN_HERE
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
/review
/review EURUSD M15
```

Expected behavior: `/snapshot EURUSD M15` returns a Russian readiness report with one leading emoji.
`/digest` returns a Russian readiness digest with one leading emoji. These commands must not contain
LONG/SHORT directions, entry guidance, buy/sell recommendations, or paper-trade actions. `/review`
returns a Russian read-only manual review summary with one leading emoji and explicit
`NO TRADING SIGNAL`/`NON-ACTIONABLE` markers. `/review EURUSD M15` returns a Russian snapshot-backed
read-only review over a real Phase 4G pipeline decision, with the same no-signal/non-actionable
markers and no price levels.

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
