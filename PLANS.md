# AI Trading OS Plans

## Completed Foundation Scope

- Project metadata and uv-compatible dependency management.
- FastAPI health, readiness, system status, and scanning-state endpoints.
- Async PostgreSQL models, Alembic migration, repositories, and unit of work.
- Worker process with heartbeat and health-check jobs.
- Telegram disabled mode, authorization, Russian text validation, and one-emoji formatting.
- Future provider and agent contracts without live calls or analysis.
- Safety scan for forbidden real-order execution concepts.
- Documentation and tests for foundation behavior.
- Phase 2 foundation hardening: Docker runtime defaults, internal API key security, redaction,
  UTC normalization, UoW lifecycle hardening, architecture boundary tests, typed provider
  contracts, disabled adapters, production Twelve Data/FMP adapters, and MockTransport-backed
  provider contract tests.
- Phase 3A data-quality foundation: duplicate-safe candle/event storage repositories,
  deterministic data-quality snapshots, and historical replay utilities for tests.
- Phase 3B feature engine foundation: deterministic closed-candle feature models, feature
  calculation engine, feature service over repository protocols, and safety tests confirming no
  strategy/signals/trading activation.
- Phase 3C indicator/context foundation: deterministic closed-candle context models, context
  calculation engine over Phase 3B features, context service over repository protocols, and safety
  tests confirming no strategy/signals/trading activation.
- Phase 3D analysis snapshot foundation: deterministic readiness report models, analysis snapshot
  engine over Phase 3A/3B/3C outputs, analysis service over repository protocols, and safety tests
  confirming no strategy/signals/trading activation.
- Phase 3E Telegram readiness foundation: local `/snapshot` readiness reports in Telegram,
  UnitOfWork-backed analysis service wiring, local seed data utility, and safety tests confirming no
  strategy/signals/trading activation.
- Phase 3F readiness scheduler foundation: deterministic pair/timeframe readiness plans, latest
  closed-window resolution, snapshot digest payloads, deduplication keys, and safety tests
  confirming no strategy/signals/trading activation.
- Phase 3G Telegram digest command foundation: manual `/digest` command wiring over the existing
  readiness digest service, default EURUSD M15/H1 digest arguments, and safety tests confirming no
  strategy/signals/trading activation.
- Phase 3H scheduled digest delivery foundation: disabled-by-default scheduled readiness digest
  due checks, mockable notification sending, deduplication records, and safety tests confirming no
  strategy/signals/trading activation.
- Phase 3I persistent digest delivery audit foundation: neutral scheduled digest delivery audit
  table, SQLAlchemy-backed deduplication store, UoW integration, and safety tests confirming no
  strategy/signals/trading activation.
- Merged Phase 3I snapshot versioning and evidence foundation: `schema_version` fields on feature,
  context, and analysis snapshot metadata; deterministic `data_completeness_ratio` on
  feature/context snapshots; candle-level `used_candle_open_times`/`used_candle_close_times`
  evidence timestamps on feature snapshots; an unwired, read-only `AnalysisAgent` Protocol in
  `app/schemas/agents.py`; and safety tests confirming no strategy/signals/trading activation.
- Phase 4A signal contract foundation: immutable contract/value models, validation rules,
  deterministic serialization, deterministic fingerprinting, and safety tests confirming no signal
  generation or execution activation.
- Phase 4B strategy rule specification foundation: immutable rule specification models, operator
  validation, deterministic serialization, deterministic fingerprinting, and safety tests confirming
  no rule evaluation, signal generation, scoring, or execution activation.
- Phase 4C strategy ruleset validation foundation: immutable validation issue/report models,
  static structural checks for `StrategyRuleSet`, deterministic validation reports, and safety tests
  confirming no market-data rule evaluation, signal generation, scoring, or execution activation.
- Phase 4D strategy ruleset registry foundation: immutable registry item/snapshot models,
  deterministic disabled built-in `StrategyRuleSet` fixtures, Phase 4C validation reports, and
  safety tests confirming no market-data rule evaluation, signal generation, scoring, or execution
  activation.
- Phase 4E disabled pipeline report shell foundation: immutable disabled pipeline report models, a
  disabled shell over Phase 4D registry snapshots, deterministic report serialization/
  fingerprinting, and safety tests confirming no decision engine, rule evaluation, signal
  generation, scoring, or execution activation.
- Phase 4F strategy rule evaluation foundation: a field resolver registry mapping the three
  existing `field_ref` values to real `AnalysisSnapshot` data, an operator evaluator (EXISTS/
  NOT_EXISTS/EQ/NE/GT/GTE/LT/LTE/BETWEEN/IN), severity-based aggregation into a deterministic
  `RuleSetEvaluationReport` (BLOCKED/NOT_READY/READY_FOR_REVIEW), unconditionally non-actionable
  reports, and safety tests confirming no `SignalContract` construction, decision engine, signal
  generation, or execution activation.
- Phase 4G strategy decision composition foundation (closes Phase 4): a composer that loads every
  registered ruleset from the Phase 4D registry, skips structurally invalid ones, evaluates the
  valid ones through the Phase 4F evaluator, and combines the results into one deterministic
  `PipelineDecisionReport` (BLOCKED/NOT_READY/READY_FOR_REVIEW), unconditionally non-actionable,
  and safety tests confirming no `SignalContract` construction, price/risk calculation, or
  execution activation.
- Phase 5 manual review layer foundation: immutable read-only report models and builder over
  existing Phase 4G/4F/4E artifacts, deterministic stdout text/JSON rendering, an authorized manual
  Telegram `/review` command, in-memory report comparison and completeness summaries, and safety
  tests confirming no new evaluation, signal, scoring, AI, persistence, or execution behavior.
- Phase 6 snapshot-backed read-only review: `/review EURUSD M15` builds a real `AnalysisSnapshot`
  from stored candles (via the existing `AnalysisService`), runs the Phase 4G composer over it, and
  presents the resulting `PipelineDecisionReport` through the Phase 5 manual review layer. A pure
  domain wiring function plus a Russian snapshot-review formatter, with safety tests confirming no
  `SignalContract` construction, price levels, AI, automatic messaging, or execution behavior. The
  bare `/review` still renders the structural Phase 4E report.
- Phase 7A market-data ingestion foundation: the first code in the project that calls a provider and
  stores the result. `MarketDataIngestionService` fetches closed candles over a rolling, deliberately
  overlapping window (`latest_closed_boundary` minus `lookback_candles`) and writes them through the
  duplicate-safe `candles.upsert_many`, recording `last_successful_market_fetch` on success. A worker
  job is registered, but only when both `MARKET_DATA_ENABLED` and `MARKET_DATA_INGESTION_ENABLED` are
  true; both default to false. An empty provider response is a success (closed market), not a failure,
  and a failing pair is isolated so the rest of the tick still runs. Provider errors are recorded
  through `record_system_error` rather than raised into the scheduler. Ingestion writes candles only:
  no signals, directions, price levels, scoring, AI, or messages.
- Phase 7C analytical ruleset foundation: nine descriptive rules across three rulesets replacing the
  three placeholder fixtures. The placeholders used `EXISTS`, which only asks whether a value
  resolved, so they passed identically on live data and on an empty database. The new rules read
  values, so the pipeline reports different statuses for different data — the property the project
  had been missing. Adds seven value resolvers (used candle count, completeness ratio, market-data
  completeness, latest-candle age, volatility ratio, max close-to-close drawdown, UTC weekday), each
  returning `None` when its source is absent rather than substituting a value. Thresholds were
  calibrated against live Twelve Data windows and the evidence recorded in the verification report.
  Rules stay `enabled=False` and produce no direction, price level, scoring, or AI output.
- Phase 7B calendar ingestion foundation: `EconomicCalendarIngestionService` fetches scheduled
  events over a window that straddles the tick (default 24h back, 72h forward, since calendars are
  published ahead) and stores them through the duplicate-safe `economic_events.upsert_many`,
  recording `last_successful_calendar_fetch`. A worker job is registered only when both
  `CALENDAR_ENABLED` and `CALENDAR_INGESTION_ENABLED` are true; both default to false. An empty
  response is a success (a quiet calendar), and provider errors are recorded rather than raised.
  Ships the `foundation.event_context.v1` ruleset — high-impact event count and minutes since the
  latest event — so the data has a consumer, bringing the rule set to eleven across four rulesets.
  Ingest forward, evaluate backward: the snapshot still proves no post-`as_of` data was used.
- Phase 7D-1 historical backfill foundation: `MarketDataBackfillService` plus
  `scripts/backfill_market_data.py` fill historical candles chunk by chunk so later calibration has
  a real distribution instead of a two-window sample. Chunk width is the candle budget clamped by
  `provider_max_request_range_days`; chunks run oldest-first with a pacing delay, and a failed chunk
  is isolated so the rest of the range still fills. Because `app/adapters/twelve_data.py` sends no
  `outputsize`, a provider result cap could silently drop the oldest bars of a chunk, so each chunk
  is flagged `possibly_truncated` when its first returned candle sits far after the requested start,
  and a run with any failed or truncated chunk does not report success. Deliberately a manual
  script, never a scheduled job.

## Current Implementation Status

The repository has completed the foundation phase, Phase 2 hardening/data adapters, Phase 3A
data-quality foundation, Phase 3B deterministic feature-engine foundation, Phase 3C deterministic
indicator/context foundation, Phase 3D deterministic analysis snapshot/readiness report foundation,
Phase 3E local Telegram readiness-report foundation, Phase 3F deterministic readiness scheduler and
snapshot digest foundation, Phase 3G manual Telegram digest command foundation, Phase 3H neutral
scheduled digest delivery foundation, and Phase 3I persistent neutral digest delivery audit
foundation plus the merged Phase 3I snapshot versioning/evidence foundation. Phase 4A signal
contract foundation is contract-only and defines future signal contract
shapes without generating signals or trading recommendations. Phase 4B strategy rule specification
foundation is specification-only and defines future rule set shapes without evaluating rules or
activating strategy logic. Phase 4C strategy ruleset validation foundation validates the structure of
Phase 4B rule sets without evaluating market data or producing decisions. Phase 4D strategy ruleset
registry foundation loads disabled built-in rule set fixtures and validates them through the Phase
4C validator without evaluating data or producing decisions. Phase 4E disabled pipeline report shell
foundation consumes only Phase 4D registry snapshots and produces deterministic disabled reports
without becoming a decision engine. Phase 4F strategy rule evaluation foundation resolves rule
`field_ref` values against real `AnalysisSnapshot` data and produces deterministic, unconditionally
non-actionable `RuleSetEvaluationReport` objects without constructing a `SignalContract` or becoming
a decision engine. Phase 4G strategy decision composition foundation composes those evaluation
reports across every registered ruleset into one deterministic, unconditionally non-actionable
`PipelineDecisionReport`, without constructing a `SignalContract` or calculating price levels. This
closes Phase 4: the full declarative rule pipeline now runs end to end against real data, with
signal-contract price-level construction deliberately deferred to Phase 9A. Production Twelve Data
and FMP adapters exist, but live
integrations remain disabled by default. Scanning state can be enabled or disabled, Telegram can
request readiness reports and readiness digests, and scheduled digest orchestration remains disabled
by default. Snapshots carry schema versions, deterministic data-completeness ratios, and
candle-level evidence timestamps. A read-only agent contract exists but is unimplemented and
unwired. Phase 4 (4A-4G) is complete: rules declared as data, validated, registered, evaluated
against real snapshots, and composed into one deterministic pipeline decision. No `SignalContract`
is ever constructed, no strategy engine, no signal generation, concrete AI agent, paper-trading, or
execution flow is connected.
Phase 5 adds a presentation-only manual review layer. It consumes existing immutable report
artifacts without invoking the Phase 4 evaluator/composer and provides local stdout and authorized
Telegram inspection plus deterministic in-memory comparison. Manual review reports are never
persisted and remain disabled/non-actionable. Phase 6 adds snapshot-backed review: `/review EURUSD
M15` builds a real `AnalysisSnapshot` from stored candles, runs the Phase 4G composer over it, and
presents the resulting pipeline decision through the same read-only manual review layer, still
non-actionable and without any signal, AI, or execution behavior.

## Future Phases

- Phase 2: market-data and calendar adapters — completed as disabled-by-default factories plus
  production adapters covered by MockTransport-backed contract tests. Adapters alone do not fetch
  anything: the market-data ingestion service that actually calls `get_closed_candles` and stores
  the result arrived in Phase 7A. Calendar ingestion (`get_events`) is still unwired and is Phase 7B.
- Phase 3A: data-quality foundation — completed without trading analysis or decisions
- Phase 3B: deterministic feature engine foundation — completed without trading decisions
- Phase 3C: deterministic indicator/context foundation — completed without trading decisions
- Phase 3D: deterministic analysis snapshot/readiness report foundation — completed without trading decisions
- Phase 3E: local Telegram readiness reports — completed without trading decisions
- Phase 3F: neutral readiness scheduler/snapshot digest foundation — completed without trading decisions
- Phase 3G: manual Telegram digest command foundation — completed without trading decisions
- Phase 3H: neutral scheduled digest delivery foundation — completed without trading decisions
- Phase 3I: persistent digest delivery audit foundation — completed without trading decisions
- Merged Phase 3I snapshot versioning/evidence foundation — completed without trading decisions
- Phase 4A: signal contract foundation — contract-only, no signal generation or trading decisions
- Phase 4B: strategy rule specification foundation — specification-only, no rule evaluation or trading decisions
- Phase 4C: strategy ruleset validation foundation — validation-only, no market-data rule evaluation
- Phase 4D: strategy ruleset registry foundation — registry/fixture-only, no market-data rule evaluation
- Phase 4E: disabled pipeline report shell foundation — report-shell-only, no decision engine
- Phase 4F: strategy rule evaluation foundation — evaluator-only, unconditionally non-actionable,
  no SignalContract construction, no decision engine
- Phase 4G: strategy decision composition foundation — composes evaluation reports across every
  registered ruleset into one deterministic, unconditionally non-actionable pipeline decision;
  **closes Phase 4**
- Phase 5: read-only manual review layer foundation — completed without new rule evaluation,
  trading output, persistence, AI, or execution behavior
- Phase 6: snapshot-backed read-only review — `/review EURUSD M15` over a stored snapshot through
  the Phase 4G composer; no signals, no buy/sell, no AI; completed
- Phase 7: live data and real analysis — closes the two gaps found on 2026-07-22 (no ingestion
  path, placeholder-only rules); **completed**
  - 7A: market-data ingestion service plus worker job, disabled by default — **completed**. Rolling
    overlapping window, empty response treated as success, per-item failure isolation, errors
    recorded via `record_system_error`. First-run backfill deliberately deferred; the rolling window
    covers roughly the last 12 hours by default.
  - 7B: economic-calendar ingestion on the same pattern via `EconomicCalendarProvider.get_events` —
    **completed**. The window straddles the tick (default 24h back, 72h forward) because calendars
    are published ahead. Records `last_successful_calendar_fetch`. Ships the two event rules that
    consume the data, so the slice is end to end rather than another unused adapter.
  - 7C: real analytical `StrategyRuleSet` content replacing the three structural fixtures —
    **completed**. Nine rules: data quality (used candle count, completeness ratio, market-data
    completeness, latest-candle age), market context (context readiness, volatility ratio versus its
    own window average, max close-to-close drawdown), and time filter (liquidity session, weekday).
    A rule on proximity to high-impact events was deliberately left out because it needs the
    calendar from 7B.
  - 7D-1: manual historical backfill script — **completed**. Chunks requests by candle budget
    clamped to `provider_max_request_range_days`, paces them, and flags a chunk as possibly
    truncated when the oldest returned candle sits far after the requested start. Never scheduled.
  - 7D-2: historical validation of the rules — **completed**, closing Phase 7. `app/domain/
    rule_replay.py` plus `scripts/replay_rules.py` walk stored history through the real
    `AnalysisEngine` and Phase 4G composer and report per-rule firing rates and field
    distributions. Read-only and never scheduled. Sane behaviour was defined before the run:
    warnings fire on 1-10% of windows, data-quality rules pass on nearly all of them. Recalibrated
    the volatility band (0.4/2.5 -> 0.30/3.5) and the drawdown bound (0.01 -> 0.004) against
    16 909 M15 and 4 219 H1 windows, and fixed a rule that could never fire: the session resolver
    returned `None` off-session, making the rule UNAVAILABLE instead of failed.
  - Unlocks `MARKET_DATA_ENABLED=true`/`CALENDAR_ENABLED=true` becoming meaningful, and makes
    `/review EURUSD M15` report real market analysis instead of placeholder checks.
  - Still no signals, directions, price levels, or AI.
- Phase 8: Russian Chief AI explanations — first LLM connection, disabled-by-default, explains
  deterministic reports in Russian without changing them; **completed**
  - 8A: `ExplanationInput` contract shaped for the real `PipelineDecisionReport`, plus an output
    validator — **completed**. No network call and wired to nothing. The validator is fail-closed
    (accepted only when no finding) and rejects: empty/non-Russian/over-long text, actionable
    instructions in English **and Russian**, any emoji in the body, and any number absent from the
    input. That last check is what makes a fabricated figure impossible to slip through. The scored
    Chief AI request stub in `app/schemas/agents.py` was deliberately not reused: it requires fields
    the pipeline never produces and the safety tests ban.
  - 8B: production OpenAI adapter, disabled by default — **completed**. Plain httpx in the same
    shape as the other two adapters, covered by MockTransport contract tests plus adversarial tests
    where a stub model lies six different ways and the decision fingerprint stays byte-identical.
    `explain_validated` runs the Phase 8A validator, and the outcome carries text only when the
    answer was accepted, so unchecked prose has no path out. Wired to nothing; 8C does that.
  - 8C: Telegram delivery — **completed**, closing Phase 8. A separate `/explain EURUSD M15`
    command rather than an addition to `/review`, because every call costs money and `/review` is
    the command you run repeatedly. The deterministic report is always sent in full; an explanation
    is appended only after passing 8A validation, and every failure — disabled, unreachable,
    rejected, timed out — becomes one honest line beneath it. Two flags, both off by default, and a
    latency budget so a slow provider cannot hang a command.
  - Unlocks `OPENAI_ENABLED=true`.
- Phase 9: signals, delivery, and paper trading — the final phase; not started
  - 9A: `SignalContract` assembly from `PipelineDecisionReport`, including the price-level
    (entry/stop/take-profit) construction deferred since Phase 4. The `calculate_entry`/
    `calculate_stop`/`calculate_target` safety-term ban is lifted only inside this slice.
  - 9B: Telegram signal delivery — the first user-visible LONG/SHORT output in the project.
  - 9C: paper trading — simulated positions and outcome tracking, no real money.
  - `REAL_TRADING_ENABLED` stays `False` permanently; no broker order API is ever added.

## Explicit Non-Goals

- No broker execution.
- No real trading.
- No strategy logic.
- No indicators or signal generation.
- No OpenAI calls.
- No fabricated market data or scan results.

## Known Risks

- Local Docker or PostgreSQL availability can affect verification.
- Future provider adapters must preserve disabled-by-default behavior.
- Telegram message validation is intentionally simple and should be tightened as message complexity grows.

## Next Planned Task

**Phase 7 is complete.** Ingestion (7A), analytical rules (7C), calendar ingestion (7B), historical
backfill (7D-1), and historical validation (7D-2) are all done: the application fetches real data,
evaluates real rules over it, and the thresholds are derived from six months of observed EURUSD
history rather than from guesses. See `docs/phase7d2-verification-report.md`.

**Phase 8 is complete.** The contract (8A), the provider (8B), and delivery through `/explain` (8C)
all exist, with both flags off by default. See `docs/phase8a-`, `8b-`, and
`phase8c-verification-report.md`.

**Phase 9A (`SignalContract` assembly and price levels) is the next planned task.** It is the first
slice that computes an entry, a protective level, and a target — work deferred since Phase 4 — and
the `calculate_entry`/`calculate_stop`/`calculate_target` term ban lifts only inside it. Everything
before it stayed descriptive on purpose; 9A is where that changes, so its safety boundary deserves
more care than any slice so far.

A live model call has still never been made. It needs the user's key and money; the 8B report
records what to run and what it would cost, and `/explain` is now the way to do it.

Two items carried out of Phase 7, to be picked up when they stop being blocked rather than as new
phases:

- The `event_context.*` thresholds remain uncalibrated. Storage holds five economic events, all
  seeds or stubs. Verified on 2026-08-01: an FMP key exists and works, but the economic calendar is
  not on the free plan (`402 Restricted Endpoint`; a control call to `/stable/quote` returned 200).
  FMP includes the calendar from Starter (one-year range) and in full from Premium. Until a plan or
  another provider is in place, keep `CALENDAR_ENABLED=false` and re-run `scripts/replay_rules.py`
  once real calendar history exists.
- ~~`MAXIMUM_CLOSE_DRAWDOWN` is a cross-timeframe compromise~~ — **closed 2026-08-05**, see
  `docs/drawdown-normalisation-report.md`. The rule now reads
  `market_context.max_close_drawdown_atr` against a bound of 4.0 typical candle ranges and fires on
  5.65% of M15 and 5.03% of H1 windows, a 0.62 percentage-point spread against the previous 5.95.
  The lesson generalises and is now a standing rule in `AGENTS.md`: a threshold on a raw magnitude
  is a defect waiting to surface, because the timeframe, the instrument, and the period all change
  what "large" means.

Phase 7 comes before Chief AI because until 7A the application had no ingestion path at all, and
until 7C the rules passed identically on live data and on an empty database. Explaining that output
with an LLM would have explained nothing. Chief AI is Phase 8, signals/delivery/paper trading is
Phase 9. Real `SignalContract` construction and all trading behavior remain inactive until Phase 9A.

### Parallel work between agents

Phase 3I was once implemented twice independently. To avoid a repeat:

- 7A/7B (ingestion) and 7C (rule content) touch different files and can be built in parallel by
  different agents.
- 7D depends on 7C.
- Phase 8 and Phase 9 slices are strictly sequential; do not parallelize them.
