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
  - Unlocked the explainer. The flag was `OPENAI_ENABLED` until Phase 8D replaced it.
  - 8D: a local explainer — **completed 2026-08-10**, see `docs/phase8d-verification-report.md`.
    Phase 8 reopens deliberately: `/explain` can now be answered by a model on this machine.
    LM Studio and friends serve the same `/v1/chat/completions` as OpenAI, so the 8B adapter was
    generalised rather than copied — one transport, still exactly one module that can reach a model,
    and a local endpoint is sent no API key at all. `OPENAI_ENABLED` became
    `EXPLANATION_PROVIDER=disabled|openai|local` and is refused at startup rather than ignored.
    `scripts/evaluate_explanations.py` measures the share of answers the Phase 8A validator accepts
    and why it rejects the rest, so a model is adopted on evidence rather than on impression. It
    earned itself immediately: `gpt-oss-20b` scored 20% with sixteen `UNKNOWN_NUMBER` rejections,
    every one of which was a correct rounding of a value it had been handed. Readings now reach
    the explainer at four significant digits and the same run scores 85%, with the validator
    unchanged. Median latency 3.4s, well inside the 20s budget.
- Phase 9: signals, delivery, and paper trading — the final phase; not started
  - 9A: price-level construction, deferred since Phase 4 — **completed 2026-08-05**, see
    `docs/phase9a-verification-report.md`. Scoped down during planning: the original wording said
    "assemble a `SignalContract` from a `PipelineDecisionReport`", which is impossible, because the
    pipeline produces no direction and the contract requires one. 9A therefore builds the level
    machinery with direction as an **input**, and adds the invariant that no function anywhere
    returns a `SignalDirection`. The `calculate_*` term ban now applies project-wide with one
    exempted module — before this slice it only existed in per-phase file lists, so a new file could
    have defined one unnoticed.
  - 9A-2: outcome measurement — **completed 2026-08-07**, see
    `docs/phase9a2-verification-report.md`. The capability 9A named as missing: for each historical
    window, walk forward and record whether the target or the protective level came first. The only
    module in the project allowed to read past `as_of`, fenced off from the analysis path by three
    tests. Produced the project's first baseline — EURUSD M15, 38.4% LONG / 43.1% SHORT at the 9A
    defaults, gross of costs — and a multiplier sweep in which nothing pays for its own geometry
    without a direction.
  - 9A-3: a directional candidate and its verdict — **completed 2026-08-07, verdict NEGATIVE**, see
    `docs/phase9a3-verification-report.md` and its addendum. The first market view in this project,
    and it did not survive. The candidate initially cleared criteria fixed before the run, then the
    stored history was found to be about 28% synthetic weekend rows; excluding weekends reverses the
    in-sample result on both timeframes, which voids the selection the whole result rested on. The
    module stays in the tree, unwired and disproved, so the next idea reuses the apparatus. The
    anti-strategy AST invariant is now scoped to one exempted module with four narrower tests in its
    place, and that stands regardless of the verdict.
  - 9A-4: the market-open gate — **completed 2026-08-07**, see
    `docs/phase9a4-verification-report.md`. A remediation slice, the first item from the full project
    review of the same day. `data_quality.market_open` is REQUIRED, so a window recorded while the
    market was shut is `NOT_READY`; `READY_WITH_WARNINGS` exists so a failing warning reaches the
    headline. The rule saying this already existed as a WARNING and failed on 28.08% of windows while
    changing nothing, because `warning_failure_count` was computed and never used.
  - 9A-5: market-data provenance — **completed 2026-08-07**, see
    `docs/phase9a5-verification-report.md`. The second remediation item. 39 fabricated rows removed,
    of which 30 were seed candles sitting on real timestamps quoting prices four hundred pips out and
    winning the de-duplication. `load_history` now refuses fabricated rows by default.
  - 9A-6: recalibration on traded candles — **completed 2026-08-08**, see
    `docs/phase9a6-verification-report.md`. `volatility_ratio` moved to 0.35/2.3;
    `max_close_drawdown_atr` stayed at 4.0 with a 0.02-point cross-timeframe spread; the 9A-2
    baseline was re-measured and superseded. Two acceptance criteria proved incompatible for the
    volatility band, and that is recorded rather than resolved by dropping one.
  - 9A-7: three measurement gaps — **completed 2026-08-08**, see
    `docs/phase9a7-verification-report.md`. Symmetric excursion field bounded at 5.0 (3.43% / 2.56%),
    entry band no longer widening the risk geometry, availability-aware rule behaviour, and the
    baseline re-measured with the corrected geometry.
  - 9A-8: a second instrument — **completed 2026-08-09**, see
    `docs/phase9a8-verification-report.md`. NOKSEK chosen over GBPUSD because it is genuinely
    unlike EURUSD. The excursion bound transferred untouched; the volatility band failed again and
    moved to 0.30/2.5. Closes the remediation list from the 2026-08-07 review.
  - 9C-1: the forward outcome ledger — **completed 2026-08-10**, see
    `docs/phase9c1-verification-report.md`. Taken before 9B, which has nothing worth delivering. On
    every closed window the worker fixes the levels for **both** directions and stores them with the
    pipeline's verdict; a second tick settles the outcome later from candles that arrived
    afterwards. No account, no position size, no profit and loss, no direction chosen — the unused
    `paper_positions` table from Phase 1 assumes all four and stays untouched. The value is
    pre-registration, and it is checkable per row: `recorded_at` and `as_of` are both stored, so a
    row written after its own future is self-identifying. Three safety tests were narrowed to name
    the one permitted service, each replaced by something stricter. Verified against real EURUSD on
    a throwaway database: 384 rows, **zero** mismatches against a freshly computed
    `measure_outcome`.
  - 9B: Telegram signal delivery — the first user-visible LONG/SHORT output in the project. Still
    blocked by the absence of anything worth delivering, not by a task.
  - 9C-2: do the rules earn their place — **machinery completed 2026-08-11**, see
    `docs/phase9c2-verification-report.md`. Asked retrospectively over six months rather than
    waiting weeks for the ledger, because a retrospective test is biased in favour of the rules
    and can therefore disconfirm cheaply. Only three of the eleven rules claim anything about
    the market; the other eight are plumbing or dead. **Verdict: all three failed.** Largest edge
    across four series 2.78 points, negative; `session_name_allowed` flat at -1.01/+0.04/-0.16/
    -0.48 with 1,000-4,700 windows on the rejected side. Two of the three fire on 2-5% of
    windows by calibration and could not have partitioned anything: the 1-10% corridor optimises
    rarity, which is now measured and unrelated to outcomes.
  - 9C-3: the field against the outcome — **completed 2026-08-11**, see
    `docs/phase9c3-verification-report.md`. Deciles rather than a swept cut, so no parameter
    could be fitted. All four fields flat on target share across four series; `move_efficiency`
    measured for the first time and flattest of all. `volatility_ratio` predicts timeouts
    strongly (23% to 6%) and target share not at all — motion is not profit.
  - 9C-4: execution cost against outcomes — **completed 2026-08-12**, see
    `docs/phase9c4-verification-report.md`. A cost is now an axis on every outcome measurement,
    assumed rather than observed and swept over a pre-registered grid; a safety test keeps an
    assumed cost out of `app/services` and `app/persistence` so the 9C-1 ledger stays gross.
    **No cost is small enough** — all four series are below the 42.86% break-even at zero cost.
    The five-point bar for a finding is worth **0.15 average candle ranges** (0.153/0.163/0.134/
    0.147), so a candidate needs about 6.5 points over the base rate on EURUSD M15 to be level.
    Two pre-registered claims refuted; one of them corrects the reasoning published in 9C-3.
  - Beyond 9C-4: the ledger remains the unbiased confirmation of anything that survives. Nothing
    has survived yet, so there is currently no base rate worth presenting to a person. The one
    measurement 9C-4 names as earned: bucket windows by `cost / ATR`, the only quantity shown to
    order cost sensitivity and comparable across instruments even though ATR alone is not.
  - `REAL_TRADING_ENABLED` stays `False` permanently; no broker order API is ever added.

## Explicit Non-Goals

Corrected 2026-08-05. Three entries below had gone stale: they were written when the project was
foundation-only and by Phase 8 they contradicted the roadmap outright, which is how a non-goals list
stops being read.

- No broker execution — permanent.
- No real trading; `REAL_TRADING_ENABLED` stays `False` — permanent.
- No fabricated market data, calendar data, or scan results — permanent.
- ~~No strategy logic~~ — still true today and deliberately so: nothing decides direction, and a
  safety test enforces it. It stops being a non-goal the day a direction slice is approved, and that
  day should be a deliberate decision rather than a drift.
- ~~No indicators or signal generation~~ — superseded. Indicators arrived in Phase 3B/3C and price
  levels in Phase 9A. What remains banned is *generating a signal*: a direction plus levels
  presented as a recommendation.
- ~~No OpenAI calls~~ — superseded by Phase 8B/8C. Calls are possible, disabled by default, and
  their output cannot change a deterministic report.

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

**Data quality comes before anything else.** The stored history is about 28% synthetic weekend rows,
discovered on 2026-08-07 while backfilling a routine gap. It already overturned the 9A-3 verdict, and
it sits underneath every number this project has calibrated: the Phase 7C thresholds re-derived in
7D-2, and the Phase 9A-2 baseline and multiplier sweep. Nothing further should be built on that
history until it is filtered.

Concretely, and in this order. Item 1 is done; the rest is the remediation list from the full project
review of 2026-08-07.

1. ~~**Move the weekend filter into the domain**~~ — **done 2026-08-07 as 9A-4.**
2. ~~**Clean the database**~~ — **done 2026-08-07 as 9A-5**, and it was worse than estimated: 39 rows,
   including 30 seed candles that had been replacing real observations outright.
3. ~~**Re-measure what was calibrated on filler**~~ — **done 2026-08-08 as 9A-6.**
4. ~~**Close the measurement gaps found in the review**~~ — **done 2026-08-08 as 9A-7**, including
   both calibration follow-ups.
5. ~~**A second instrument**~~ — **done 2026-08-09 as 9A-8**, using NOKSEK rather than GBPUSD
   because a pair that correlates 0.85-0.9 with EURUSD is barely a second test. 180 days stored on
   both timeframes; historical only, the worker does not ingest it. It remains available as genuinely
   unseen data for a future candidate, and spending it on nothing would waste it.
6. **Then, and only then, another directional candidate** — or the decision to stop looking for one.

9B (delivery) is not blocked by a task but by the absence of anything worth delivering: there is no
direction that survives inspection. 9C (paper trading) is the cheapest source of genuinely fresh
data and is a reasonable next build even with no candidate, because it starts accumulating the one
thing this history can no longer provide.

**9C-1 built that ledger on 2026-08-10**, and it is off by default: nothing accumulates until
`FORWARD_OUTCOME_RECORDING_ENABLED=true` and the worker runs. The next task is therefore not code —
it is letting it run long enough to hold a sample worth reading. About 240 rows a day on the two
EURUSD series the worker already ingests.

**After 9C-2 the open list changed shape.** The eleven rules are a data-quality gate plus three
measurements that do not predict anything, so there is currently no basis for telling a person
what usually follows a window like theirs. The next tests, in order: sweep a field's threshold
against outcomes rather than against firing rate; and check whether the volatility band selects
windows that resolve *at all*, which the timeout figures hint at and which needs its own
pre-registered criteria.

~~Still open and unchanged: spread data, without which every outcome stays gross and no result can be
shown to survive costs.~~ — **retired in that form on 2026-08-12 by 9C-4.** Costs are now an axis on
every outcome measurement, assumed rather than observed and swept over a pre-registered grid, and
the answer is that **no cost is small enough**: all four series sit below break-even before anything
is charged. The five-point bar this project uses to call a field informative is worth about **0.15
average candle ranges** of execution cost, so a candidate must clear roughly 6.5 points above the
base rate on EURUSD M15 merely to be level. What replaces the open item is narrower: observing a
real spread is worth doing when a candidate exists whose margin is close enough to 0.15 ATR for the
precision to matter. None is. See `docs/phase9c4-verification-report.md`.

Superseded planning note: **Phase 9A (`SignalContract` assembly and price levels) was the next task.** It is the first
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
