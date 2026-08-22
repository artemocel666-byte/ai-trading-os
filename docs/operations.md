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

Counting alone would produce false alarms whenever a chunk legitimately holds fewer candles than its
span suggests. An empty chunk (closed market) is a success and is never flagged, because a response
with no candles carries no evidence either way.

The original wording here cited a weekend as that example. Measured on 2026-08-07, this provider does
not thin out over weekends at all — it returns a continuous 24/7 series — so the weekend is a poor
illustration even though the range-based check remains the right one.

If a chunk is flagged, treat that range as incomplete: narrow it with a smaller `--chunk-candles` and
re-run that period rather than accepting the stored result.

Backfill stores candles only. It produces no signals, price levels, scoring, AI output, or messages.

## Fabricated Rows in Stored History

The local seeder and the phase verification scripts write into the same database the calibrations
read from, under their own provider names. On 2026-08-07 that turned out to matter: the database held
30 `local-seed` EURUSD M15 candles **on the same timestamps as real ones**, quoting 1.1005 where the
market was at 1.1441, plus five invented economic events — every event the project had.

The collision was the dangerous part. `MarketFeatureEngine` de-duplicates by `(open_time, provider)`
and keeps the first, `local-seed` sorts before `twelve_data`, so the invented candle replaced the
real observation on each of those thirty timestamps without raising anything beyond a
`DUPLICATE_CANDLE` issue.

`app/core/constants.py` names the providers whose rows are real. Anything else is fabricated by
definition — no heuristic on the values is needed, and none would have helped: the seed candles were
well-formed OHLC with sane highs and lows.

### Finding and removing them

```bash
uv run python -m scripts.purge_synthetic_data
```

Dry run by default: it prints every provider it would delete, and flags fabricated candles that
collide with real ones. Add `--confirm` to delete. **Take a dump first** — this is not reversible
from the script:

```bash
docker compose exec postgres pg_dump -U ai_trading_os ai_trading_os > backup.sql
```

### The guard that matters more

`load_history` in `scripts/replay_rules.py` — the single door every calibration goes through —
**refuses to run over fabricated rows**. Replay, outcome measurement and direction evaluation all
inherit it. Test fixtures and deliberate experiments pass `--allow-synthetic`; nothing gets it by
accident.

After a purge, the calendar is genuinely empty, so both event rules become `NEVER_FIRES` and
`NOT_OBSERVED` and `scripts/replay_rules.py` exits non-zero. That is correct: a rule that cannot be
exercised is a finding. Acknowledge it deliberately rather than weakening the check:

```bash
uv run python -m scripts.replay_rules --days 180 \
  --allow-quiet event_context.high_impact_event_count \
  --allow-quiet event_context.minutes_since_latest_event \
  --allow-quiet data_quality.latest_candle_age_minutes
```

## Gaps in Stored History

The worker does not have to run continuously, but **nothing announces a gap**. A missing Tuesday
looks exactly like a present one until somebody queries for it, and every calibration built on that
history silently inherits the hole. This section exists because the same diagnosis has been done from
scratch more than once.

### Why gaps appear, and why ingestion cannot heal them

Each scheduled tick asks the provider for the last `MARKET_DATA_INGESTION_LOOKBACK_CANDLES` candles
(default 48). The overlap is deliberate and it absorbs short interruptions — a missed tick, a network
blip, a restart — without any manual step.

But 48 candles is a different amount of *time* per timeframe:

| timeframe | 48 candles reach back |
| --- | --- |
| M15 | 12 hours |
| H1 | 48 hours |

Anything older than that is invisible to the worker forever. It does not know the gap exists, so it
never asks for it. This also explains a confusing symptom: after the same outage, H1 looks healthy
while M15 is missing days.

### Detecting a gap

Ask the database where consecutive candles are further apart than one bar:

```sql
SELECT prev_ot, open_time, (open_time - prev_ot) AS gap FROM (
  SELECT open_time, lag(open_time) OVER (ORDER BY open_time) AS prev_ot
  FROM candles WHERE timeframe = 'M15' AND open_time >= now() - interval '30 days'
) t WHERE open_time - prev_ot > interval '15 minutes' ORDER BY open_time;
```

The Postgres port is not published to the host, so run this inside the stack:

```bash
docker compose exec postgres psql -U ai_trading_os -d ai_trading_os
```

Worth knowing before reading the output: **this provider returns a continuous 24/7 series with no
weekend break at all** — about 28% of stored rows fall on a Saturday or Sunday. So a healthy series
shows *no* weekend gaps, and any gap you see is a real outage rather than a closed market. See the
caveat below about what that data is worth.

### Healing a gap

Backfill the affected range. It is duplicate-safe, so overshooting the window costs a request and
nothing else:

```bash
uv run python -m scripts.backfill_market_data --days 7 --timeframe M15
uv run python -m scripts.backfill_market_data --days 7 --timeframe H1
```

Use `--dry-run` first to see the request count against the provider quota. A useful habit: after any
stretch with the stack down, backfill a week on both timeframes before running any calibration.

### Keeping the worker alive on Windows

Containers run inside the WSL2 VM, which is started and owned by the Docker Desktop process of the
user who launched it. Consequences worth knowing:

- **Switching Windows profiles keeps it running.** The first session is not ended, so its processes
  continue. Task Manager under the second profile shows only that profile's processes, so Docker
  being invisible there proves nothing.
- **Signing out stops it**, as does sleep or hibernation.
- Every long-running service carries `restart: unless-stopped`, so a reboot or a Docker Desktop
  restart brings them back automatically, while a deliberate `docker compose stop` is respected.
  `migrate` has no policy on purpose — it is a one-shot job and is meant to exit.

Do not reason about whether an outage happened; the candle series is a precise log of when the worker
was alive. Query it.

### The weekend caveat

Weekend rows are not real market activity. The forex market is closed from Friday evening to Sunday
evening, and the provider fills that span with carried-forward prices — long runs of candles with
byte-identical highs and lows, then a sudden wide-ranged candle when trading actually resumes.

This matters for anything calibrated over stored history, because those rows depress the average true
range and the reopening looks like a violent one-directional move. Any analysis that treats every
stored candle as a traded candle is measuring roughly 28% filler.

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

## Chief AI Explanations (Phase 8B)

Off by default, behind two flags, and reachable only through the `/explain` command someone types.

```env
OPENAI_ENABLED=true
OPENAI_API_KEY=<your key>
OPENAI_MODEL=gpt-4.1
OPENAI_BASE_URL=https://api.openai.com
OPENAI_MAX_OUTPUT_TOKENS=400
EXPLANATION_DELIVERY_ENABLED=true
EXPLANATION_BUDGET_SECONDS=20
```

`/explain EURUSD M15` sends the same report as `/review` and appends either a checked explanation or
one line saying why there is none. One command is one paid request; `/review` remains free and calls
nothing. With either flag off, `/explain` still answers — report plus "слой пояснений выключен
настройками" — and no client is opened.

With `OPENAI_ENABLED=false`, `create_explanation_provider` returns a provider that raises
`IntegrationDisabledError` before any network call, so a misconfiguration cannot quietly spend money.

Operational behaviour:

- Output tokens are capped (`OPENAI_MAX_OUTPUT_TOKENS`, default 400 — enough for three or four
  Russian sentences). This is the ceiling on what a single explanation can cost.
- Provider failures map to the same errors as the other adapters: 401/403 authentication, 402 plan
  restriction, 429 rate limit, 5xx unavailable after retries, and timeouts. None of them propagate
  as a crash into a caller that has a deterministic text to fall back on.
- A model's answer is never used unchecked. `explain_validated` runs the Phase 8A validator, and the
  outcome carries text only when the answer was accepted; a rejected answer leaves no readable prose
  behind.
- The prompt contains only the serialized Phase 8A contract — our rule ids, statuses, and numbers.
  No market text or third-party string reaches the model.

The explanation layer produces no signals, price levels, scoring, or trading instructions; it can
only describe a decision that was already made deterministically.

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

## The Explainer: OpenAI or a Local Model (Phase 8D)

One setting chooses, and `disabled` is the default:

```env
EXPLANATION_PROVIDER=local        # disabled | openai | local
EXPLANATION_DELIVERY_ENABLED=true # second gate: a provider may exist and still not answer a user
LOCAL_LLM_BASE_URL=http://host.docker.internal:1234
LOCAL_LLM_MODEL=<the id LM Studio shows>
```

`OPENAI_ENABLED` was replaced and is now **refused at startup** rather than ignored. If the
container exits complaining about it, remove it from `.env` — a flag that quietly stopped working
would be worse than one that fails loudly.

### Running LM Studio

1. Load a model and start the server on port **1234**.
2. Turn on **"Serve on Local Network"**. LM Studio binds `127.0.0.1` by default, and the bot runs in
   a container, so without this `host.docker.internal:1234` is refused.
3. From the host command line the same server is `http://127.0.0.1:1234` — the CLI below takes
   `--base-url` for exactly this reason.

Nothing about the request changes between providers except the address and the credential: a local
endpoint is sent **no `Authorization` header at all**, and a contract test asserts it, so a paid key
cannot reach a process on this machine by accident.

### Latency, and what `/explain` does about it

`EXPLANATION_BUDGET_SECONDS` defaults to **20**. A small model on a CPU can need longer, and past
the budget `/explain` sends the deterministic report on its own with one line saying why there is no
explanation. That is working as designed, not failing — but if most calls come back without an
explanation, raise the budget rather than suspecting the model.

### Measuring a model before trusting it

```bash
uv run python scripts/evaluate_explanations.py --provider local --sample-size 20 --base-url http://127.0.0.1:1234
```

Read-only. It asks the model about real windows and reports how often the Phase 8A validator
accepted the answer, plus **why it rejected the rest** — which is the number that decides whether a
model is usable here:

- `UNKNOWN_NUMBER` dominating — the model invents figures. Disqualifying; nothing else matters.
- `ACTIONABLE_TEXT` — it gives trading advice it was told not to. Also disqualifying.
- `TOO_LONG` or `EMOJI_FOUND` — prompt problems, usually fixable without changing model.
- `NOT_RUSSIAN` — the model ignored the language instruction.

Rejected text is never printed: `explain_validated` drops it, so nothing unchecked reaches the
terminal.

## The Forward Outcome Ledger (Phase 9C-1)

Off by default. One flag turns on two jobs; with it off the worker registers neither:

```env
FORWARD_OUTCOME_RECORDING_ENABLED=true
FORWARD_OUTCOME_RECORD_INTERVAL_MINUTES=15
FORWARD_OUTCOME_RESOLVE_INTERVAL_MINUTES=15
FORWARD_OUTCOME_HORIZON_CANDLES=24
```

The ledger reads stored candles and **never calls a provider**. It is therefore useless without
market-data ingestion running: with ingestion off it will find nothing and record nothing, which is
the honest failure mode rather than a silent one.

Volume with the worker's current EURUSD M15 + H1 schedule: roughly **240 rows a day** — 96 M15
windows and 24 H1 windows, each recorded for both directions.

### Why there are two jobs

`forward_outcome_recording` fixes the levels and stores the row. `forward_outcome_resolution`
settles rows that are already stored, from candles that arrived later. Keeping them apart is what
makes "the plan was fixed before its future was visible" a property of the schedule rather than of a
comment, so **do not merge them** if you are ever tempted to save a tick.

### Reading it

```bash
uv run python scripts/report_forward_outcomes.py --pair EURUSD --timeframe M15 --days 30
```

Read-only. `--traded-only` restricts to windows built entirely from traded candles;
`--decision-status READY_FOR_REVIEW` restricts to windows the rules accepted.

Two things the output will tell you that are easy to misread:

- **Pending is not a failure.** A row stays pending until its horizon has genuinely elapsed. Writing
  `TIMEOUT` early would turn a gap in ingestion into a measured result.
- **"N distinct configurations"** means rows in the range were written under different multipliers
  or a different horizon. They are answers to different questions; narrow the range before reading
  the pooled figures as one sample.

### If a threshold or a multiplier changes

Nothing needs to be done to old rows, and nothing should be. Each row carries the configuration that
produced it, so a change shows up as a break in the ledger rather than as a silent rewrite. Resist
the urge to backfill: a row whose `recorded_at` sits long after its `as_of` is not pre-registered,
and pre-registration is the only thing this ledger has that replaying history does not.

That same pair of timestamps is how you check a row is genuine — a real one shows a gap of a tick or
two, never days.

### Why the window can lag the clock

The window ends at the **newest stored candle**, not at the newest closed boundary. Recording and
ingestion run on the same interval and fire in the same second, and ingestion has a provider
round-trip to make first, so asking the clock produced a window one candle short every single time —
`data_quality.market_data_complete` failed on every row written on 2026-08-10 before this was fixed.

So a fresh `as_of` normally trails the wall clock by one tick, and by more if ingestion is behind.
That is the intended behaviour, not a fault. Nothing is lost: the skipped window is written by the
next tick under the same identity.

If `windows_without_data` is non-zero in the logs, ingestion has stored nothing at all for that
series — check `MARKET_DATA_INGESTION_ENABLED` and `last_successful_market_fetch` rather than looking
at the ledger.

## Daily Bars and the Currency Universe (Phase 9D-1)

Five phases of measurement asked about one series through time and answered nothing. Phase 9D
changes the question to a comparison *across* instruments over a horizon of months, which needs a
daily timeframe and more than two instruments. This section is the plumbing; it measures nothing.

```bash
uv run python -m scripts.backfill_market_data --universe --timeframe D1 --days 7000 --max-request-range-days 1000
```

Run it inside the worker container, which already holds the provider key and the right database
host. **Rebuild the image first** — the sources are baked in at build time, so a container started
before a code change will reject `--timeframe D1` with an argparse error.

`--universe` walks every pair the Phase 9D-1 currency set implies rather than a single `--pair`.
Each pair is probed with one small request before any history is asked for, so a pair the provider
does not quote costs one call instead of a whole backfill, and appears in the output as `refused`
rather than vanishing.

`--max-request-range-days` exists because the 31-day default protects *intraday* requests from
silent truncation. A daily series returns years in one call, and leaving the default in place would
turn a nineteen-year fill into hundreds of requests. Keep the chunk under the provider's per-call
bar cap: 1000 calendar days is about 700 daily bars, comfortably inside it.

### Why a daily window skips the weekend and an intraday one does not

Intraday the provider returns a continuous 24/7 series — about 28.5% of it carried forward while the
market is shut. The filler is *present*, so every slot is expected and the weekend is excluded later
by `is_market_open` at analysis time.

Daily bars behave differently, and the difference was measured rather than assumed. Over the same
142 weeks the provider sent EURUSD **58** Saturdays and **31** Sundays, against USDJPY's **84** and
**31**. Weekend dailies arrive erratically and *differently per instrument* — the one thing a
cross-sectional comparison cannot tolerate. So `TRADED_DAYS_ONLY_TIMEFRAMES` marks `D1` as expecting
weekdays only; a weekend bar that does arrive is stored and simply surplus.

Alignment is now a separate question from expectation. It asks whether the requested span is a whole
number of bars, not whether every slot produced one — the old check inferred it from the expected
count, an identity that breaks the moment a window skips a day.

## Execution Cost Sweeps (Phase 9C-4)

Every outcome figure this project prints is gross by default: the database holds OHLC and no spread.
Since 9C-4 a cost can be **assumed** and swept, which is a different thing from observing one and is
labelled as such everywhere it appears.

```bash
uv run python -m scripts.profile_execution_cost --pair EURUSD --timeframe M15 --days 180 --exclude-closed-market
```

Read-only. It re-measures the same windows once per cost on a grid fixed in the source
(`DEFAULT_COST_GRID`, from zero to 0.00050 in price units) and prints the whole curve, never a
chosen point. `--cost` is repeatable if you want a different grid; it must include zero, because
without a free measurement every other point is relative to an already-handicapped sample.

`scripts/measure_outcomes.py` and `scripts/profile_field_outcomes.py` take a single `--cost-price`
for the same purpose. Those three scripts are the only files in the repository allowed to pass a
cost, and a safety test enforces it — an assumed number must never be stored beside an observed
candle, which is the line Phase 9A-5 drew with the `provider` column.

### Reading the output

Two figures are derived from the curve, both defined before any run:

- **break-even cost** — where target-first share crosses `stop / (stop + target)`, 42.86% for the
  Phase 9A multipliers. On all four stored series this reads *"no cost is small enough"*, because the
  gross figure is already below break-even. That is reported as a statement rather than as an
  interpolated negative number.
- **cost worth 5.00 points of target share** — the five-point bar 9C-2 and 9C-3 used to call a field
  informative, expressed as a cost. Measured at 0.153, 0.163, 0.134 and 0.147 of median ATR across
  the four series.

Divide by the printed median ATR before comparing anything across timeframes. A cost in price units
is a raw magnitude, and the standing rule about raw magnitudes applies: the 9C-4 pre-registration
stated a claim in price units, and it failed on H1 by roughly the ratio of the two timeframes' candle
ranges.

The ATR line also prints quartiles and the interquartile range as a fraction of the median. That
last number is the check to run whenever `--window-candles` changes: a wider window estimates the
same ATR far more steadily, so the fraction must visibly fall. It went 0.608 to 0.316 on EURUSD M15
between a twelve-candle and a one-day window while the median moved less than a percent. **If the
median moves and the spread does not, the window did not widen and nothing downstream is readable.**

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


## Carry cross-section (Phase 9D-4)

Ranks the currency universe by lagged interest rate differential each month and reports the
top-minus-bottom spread with its decomposition. Read-only — it evaluates and prints, and writes
nothing. Needs the Phase 9D-1 daily backfill and the Phase 9D-3 rate backfill to have run.

```bash
docker compose run --rm -T worker python -u -m scripts.profile_carry
```

`--format json` emits the same run as a machine-readable payload, **including the plumbing summary**
— the coverage figures travel inside the JSON rather than ahead of it, so the output parses.

Read the plumbing block before the verdict. `instruments per date: min/median/max` is the line that
matters: if the minimum falls well below the maximum, some cross-sections ranked a thinned universe
and every number after it means less than it appears to. Anchors excluded for an incomplete rate
cross-section are listed by date rather than merely counted, because a date dropped for a missing
rate is a fact about the data and not a rounding detail.

The tail block is not optional reading. A mean and a t-statistic describe the middle of a
distribution and are blind to its edge; carry's documented failure mode is a positive mean with a
ruinous tail. A spread whose mean passes while its worst twelve months exceed its lifetime gain is
reported as exactly that.


## Keeping the universe current (Phase 10-1)

The worker fills daily bars for all 45 universe pairs once a day on a **cron** trigger at
`DAILY_UNIVERSE_INGESTION_HOUR_UTC` (default 02:00), and refreshes interest rates weekly. Both are
off by default; set `DAILY_UNIVERSE_INGESTION_ENABLED` and `INTEREST_RATE_INGESTION_ENABLED`.

Cron rather than an interval on purpose: the ingestion service has no wall-clock gate, so a
1440-minute interval on a worker restarted daily by a deploy or a closing laptop could go its whole
life without firing — and that failure looks exactly like nothing happening.

To run either path by hand, on exactly the code the scheduler runs:

```bash
docker compose run --rm -T worker python -u -m scripts.run_universe_sweep
```

```bash
docker compose run --rm -T worker python -u -m scripts.run_rate_refresh
```

The sweep takes about nine minutes: 45 requests held at least
`PROVIDER_MIN_REQUEST_INTERVAL_SECONDS` apart (default 12). It prints the elapsed time against the
pacing floor, so a setting that stopped being applied would be visible rather than assumed.

To read freshness without fetching anything:

```bash
docker compose run --rm -T worker python -u -m scripts.report_data_freshness
```

It exits non-zero when anything is behind, so it can gate a script.

**Read `absent` separately from `stale`.** `NZDSEK` has never been stored because the provider does
not quote it; that is a standing fact, not a problem that appeared today. An alarm that includes it
would fire every day and stop being read — which is the failure this whole check exists to prevent.

**A weekend is not staleness.** A Friday daily bar closes at Saturday 00:00 UTC, so from Saturday
morning until Monday night the newest bar we should hold is Friday's. The check derives that from
`expected_open_times`, the same definition the data-quality machinery uses.


## Market state (Phase 10-2)

Describes where the currency universe stands against its own history. Read-only, and it contains no
forecast — no ranking by expected return, and nothing phrased as an expectation.

```bash
docker compose run --rm -T worker python -u -m scripts.report_market_state
```

Read the plumbing block first: how many pairs have daily history, how many have enough history for a
percentile, and which were too thin. A description built on a thinned universe is not the same
description.

**Three sections.** The currency decomposition answers whether a pair moved because of its base or
its quote — one chart cannot separate those, and forty-four pairs can. Each line carries the range
it was averaged over, because a mean near zero over a wide range is a different fact from a mean
near zero over a narrow one. The percentile section gives each pair's latest daily span a scale
against its own history. The carry section refuses to print at all unless every universe currency
has a rate for the required month, and names the missing ones when it refuses.

**One rule governs every number here.** A central tendency is never rendered without its spread and
its sample size; `app/presentation/readings.py` is the only place allowed to format a distribution,
and a safety test enforces that. A current observation — today's rate differential, say — is not a
collapsed distribution and needs no spread.


## Hidden concentration (Phase 10-3)

Says how many independent bets a set of instruments actually is. Read-only, no forecast.

```bash
docker compose run --rm -T worker python -u -m scripts.report_concentration --instruments EURUSD,GBPUSD,AUDUSD
```

Omit `--instruments` to measure the whole stored universe; 946 pairs take about four seconds.

**Read `1.2` as "one bet at triple size".** The measure is `N² / ΣΣρ`: perfectly correlated
instruments come to exactly 1, uncorrelated ones to exactly N.

**Read the halves, not just the coefficient.** Every correlation is reported over the window and
over each half of it. A quarter is about sixty-four trading days, so the standard error is near
0.12 and 0.3 is not reliably distinguishable from 0.5 — the halves are where that uncertainty
becomes visible. A live example worth remembering: `AUDUSD/EURJPY` at +0.05 overall, +0.61 and
−0.29 across the halves.

**A missing correlation is never a zero.** If any pair in the set lacks forty overlapping days the
whole answer is withheld and the missing pairs are named. Zero would read as independence, and
telling somebody their positions are unrelated when nothing is known is the worst thing this
feature could do.

**The universe figure is not the factor count.** It measures about 16.6 effective bets, while
`currency_universe` says ten currencies give at most nine independent directions. Both are right:
rank counts the factors, this counts diversification, and the second exceeds the first whenever
correlations are negative.
