# AI Trading OS

AI Trading OS is a safety-first foundation for a future modular Forex analysis and paper-trading platform. The current repository implements only infrastructure: API health/status endpoints, async PostgreSQL persistence, a scheduler heartbeat, Telegram command foundations, strict configuration, and safety contracts.

## Current Status

- Current project phase: phase_9a3_market_view_candidate_foundation.
- Phase 6 snapshot-backed read-only review is complete: `/review EURUSD M15` builds a real analysis
  snapshot, runs the Phase 4G composer over it, and presents the pipeline decision through the
  Phase 5 manual review layer — still read-only and non-actionable.
- Phase 7A market-data ingestion is complete: a worker job can now fetch closed candles from the
  provider and store them, gated by two flags that both default to off.
- Phase 7C analytical rulesets are complete: descriptive rules replaced the three placeholder
  fixtures, so `/review` now reports different statuses for different data instead of always
  reporting the same thing.
- Phase 7B calendar ingestion is complete: scheduled economic events are fetched into storage and
  consumed by an event ruleset, bringing the rule set to eleven across four rulesets.
- Phase 7D-1 historical backfill is complete: `scripts/backfill_market_data.py` fills history in
  paced chunks so calibration has a real distribution.
- Phase 7D-2 historical validation is complete: `scripts/replay_rules.py` replays every rule over
  stored history and reports how often each one fired, which is how the Phase 7C thresholds were
  re-derived. This closes Phase 7.
- Phase 8A explanation contract is complete: the project now defines what a future Chief AI may be
  shown and what it is allowed to answer, with no provider, no network call, and no wiring.
- Phase 8B OpenAI adapter is complete: a real provider exists behind that contract, disabled by
  default.
- Phase 8C explanation delivery is complete: `/explain EURUSD M15` shows the deterministic report
  and appends a checked explanation, or one honest line saying why there is none. This closes
  Phase 8.
- Phase 9A price levels are complete: entry, protective and target levels are placed at multiples of
  the window's average true range, with direction supplied as an input. There is still no strategy —
  nothing in the project decides up or down, and a test enforces that.
- Phase 9A-2 outcome measurement is complete: `scripts/measure_outcomes.py` walks forward from each
  historical window and records whether the target or the protective level came first. It produced
  the project's first baseline, which is what any future direction has to beat.
- Phase 9A-3 built the first market view in this project and **then disproved it**. The candidate
  initially cleared criteria fixed in advance; the stored history was then found to be about 28%
  synthetic weekend rows, and excluding them reverses the in-sample result. The module stays unwired
  and disproved. Next: filtering closed-market data, re-measuring what was calibrated on it, and a
  second instrument.
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
- Phase 6: snapshot-backed read-only review only; `/review EURUSD M15` composes a pipeline decision
  over a real snapshot and presents it read-only. No signals, no buy/sell, no AI, no price levels.

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
construction is deliberately deferred to Phase 9A (signals, delivery, and paper trading), where
actual price levels are needed.

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

## Phase 6 Status

Phase 6 adds snapshot-backed read-only review. When called with arguments, `/review EURUSD M15`
builds a real `AnalysisSnapshot` from stored candles through the existing `AnalysisService`, runs
the Phase 4G `StrategyDecisionComposer` over it, and presents the resulting `PipelineDecisionReport`
through the Phase 5 manual review layer. The bare `/review` (no arguments) still renders the
structural Phase 4E disabled report. Wiring lives in `app/domain/snapshot_review.py` (pure domain,
receives an already-built snapshot) and `app/telegram/snapshot_review_formatter.py` (Russian
output).

Phase 6 does not construct a `SignalContract`, calculate price levels or position size, generate
signals, provide recommendations, call AI/OpenAI/LLM services, send automatic Telegram alerts, use
broker APIs, execute orders, or enable paper or real trading. The snapshot-backed review is
read-only and non-actionable.

## Phase 7A Status

Phase 7A adds market-data ingestion — the first outbound provider call in the project. A worker job
fetches closed candles for the configured pairs/timeframes over a rolling, deliberately overlapping
window and stores them through the existing duplicate-safe `candles.upsert_many`, recording
`last_successful_market_fetch` on success.

To actually turn it on you need **both** flags plus a Twelve Data API key:

```text
MARKET_DATA_ENABLED=true
TWELVE_DATA_API_KEY=<your key>
MARKET_DATA_INGESTION_ENABLED=true
MARKET_DATA_INGESTION_INTERVAL_MINUTES=15
MARKET_DATA_INGESTION_LOOKBACK_CANDLES=48
```

With either flag off (the default) the worker registers no ingestion job and no network call is made.
Behaviour worth knowing: an empty provider response is treated as success, not failure, because the
forex market is closed on weekends; and if one pair fails, the others still ingest. Provider errors
are recorded in system state rather than raised into the scheduler.

Phase 7A stores candles only. It produces no signals, directions, price levels, scoring, AI output,
or user-facing messages, and adds no Telegram command and no API route.

## Phase 7C Status

Phase 7C replaced the three placeholder rule fixtures with nine analytical rules across three
rulesets. The placeholders used the `EXISTS` operator, which only asks whether a value resolved —
so they passed identically on live market data and on an empty database, and `/review` always
answered the same thing. The new rules read actual values.

| Ruleset | Rules |
| --- | --- |
| `foundation.data_quality.v1` | used candle count ≥ 8 (BLOCKING), completeness ratio ≥ 0.8, market-data completeness, latest-candle age ≤ 90 min |
| `foundation.market_context.v1` | context readiness, volatility ratio within 0.30–3.5 of its own window average, max close-to-close drawdown ≤ 4.0 candle ranges |
| `foundation.time_filter.v1` | London/New York liquidity session, weekday |

Thresholds shown are the current ones. They were re-derived from six months of observed history in
Phase 7D-2, and the drawdown rule was later switched to an ATR-normalised field so that one bound
means the same thing on M15 and H1 — see `docs/drawdown-normalisation-report.md`. The event ruleset
(`foundation.event_context.v1`) joined in Phase 7B, bringing the set to eleven rules.

Severity drives the outcome: a BLOCKING failure makes the pipeline `BLOCKED`, a REQUIRED failure
makes it `NOT_READY`, and WARNING failures are recorded while the pipeline stays
`READY_FOR_REVIEW`. So `/review EURUSD M15` now answers `READ_ONLY` on a fresh full window,
`INCOMPLETE` on a stale or sparse one, and `BLOCKED` when there are too few candles.

These rules are descriptive only. They answer "can this window be trusted" and "what regime is
this" — never "what should be traded". No directions, price levels, scoring, or AI. Rules and
rulesets remain `enabled=False` and non-actionable. A rule on proximity to high-impact events was
deliberately left out because it needs the calendar from Phase 7B.

## Phase 7B Status

Phase 7B adds economic-calendar ingestion and the event rules that consume it. Shipping ingestion
without a consumer is the defect this project already hit twice, so the rules are part of the slice.

Enable it with **both** flags plus an FMP API key:

```text
CALENDAR_ENABLED=true
FMP_API_KEY=<your key>
CALENDAR_INGESTION_ENABLED=true
CALENDAR_INGESTION_INTERVAL_MINUTES=60
CALENDAR_INGESTION_LOOKBACK_HOURS=24
CALENDAR_INGESTION_HORIZON_HOURS=72
```

The window straddles the tick — it reaches back over recent releases and forward over announced
ones, because calendars are published in advance. Storing a future scheduled release is not
lookahead bias; the analysis snapshot still only exposes what happened at or before `as_of`, so the
rules read backwards. That is why there is no "event in the next 30 minutes" rule: surfacing future
events into a snapshot would break the Phase 3D no-future-data proof and is a separate decision.

The new `foundation.event_context.v1` ruleset adds two rules: no high-impact release inside the
window, and enough time elapsed since the most recent one. On a window with no release at all the
second rule reports `UNAVAILABLE` rather than passing — there is nothing to measure, and `/review`
renders that distinctly from a failure.

An empty provider response is a success, not a failure: quiet calendar days exist. Provider errors
are recorded in system state rather than raised into the scheduler.

## Phase 7D-1 Status

Phase 7D-1 adds a manual historical backfill so later calibration works from a real distribution
rather than the two live windows Phase 7C had to use. It is a script, never a scheduled job:
on a timer it would spend provider quota repeatedly for no benefit.

```bash
uv run python -m scripts.backfill_market_data --days 180 --timeframe M15 --dry-run
uv run python -m scripts.backfill_market_data --days 180 --timeframe M15
```

`--dry-run` prints the chunk plan and request count without touching the provider, so quota use can
be checked before it is spent. At defaults, 180 days of M15 is 18 requests and of H1 is 6 — both far
inside a free tier's daily allowance.

**Read the truncation warning.** `app/adapters/twelve_data.py` sends no `outputsize`, so a provider
result cap could silently drop the oldest bars of a chunk and leave invisible holes in history. Each
chunk is therefore flagged `POSSIBLY TRUNCATED` when its oldest returned candle sits far after the
requested start, and the script exits non-zero if any chunk failed or looked truncated. A run that
prints that warning must be treated as incomplete history, not as a success.

Backfill stores candles only: no signals, price levels, scoring, AI output, or messages.

## Phase 7D-2 Status

Phase 7D-2 replays the built-in rules over the history Phase 7D-1 stored and reports how each rule
behaved, so thresholds come from an observed distribution rather than from two live windows.

```bash
uv run python -m scripts.replay_rules --days 180 --timeframe M15
```

The run prints two tables — the distribution of every numeric field, and per-rule passed/failed/
unavailable counts with a behaviour verdict — and exits non-zero if any rule never fired. A rule
that passes every window of six months cannot report anything, which is the same defect as the
`EXISTS` operator Phase 7C removed; the exit code makes that a finding rather than a success.

Replay is read-only and never scheduled. It writes nothing, and it changes no threshold by itself:
each threshold move is a hand-made edit in `app/domain/strategy_ruleset_registry.py` that records
the percentile and sample size behind it. Measurements and evidence live in
`docs/phase7d2-verification-report.md`.

## Phase 8A Status

Phase 8A settles two questions before any LLM exists in the codebase: **what a Chief AI may see**,
and **how its answer is checked**. It adds `ExplanationInput` (`app/domain/entities/explanation.py`)
and the builder/validator pair in `app/domain/explanation_contract.py`. There is no provider, no
HTTP client, no API key, and no service, command, route, or job that references any of it. A safety
test asserts that.

`ExplanationInput` is a frozen projection of an already-composed `PipelineDecisionReport`: pair,
timeframe, `as_of`, decision status, candle counts, per-ruleset pass/fail counts with the failed rule
ids, and the numeric readings `/review` already prints. It has no direction, price level, position
size, or scoring field — an explainer receives facts, not a handle on the pipeline.

`validate_explanation_text` returns findings instead of raising, and an explanation is accepted only
when there are none. It rejects:

- empty text, text with no Cyrillic, and text over 2000 characters
- actionable trading instructions in **English or Russian** — the Phase 5 detector matches "buy",
  not "покупай", and the user-facing language here is Russian
- any emoji in the body, so the Telegram formatter stays the only thing that adds one
- **any number that was not in the input**, which is what stops a model from inventing a price
  target; a ratio may also be written as its percentage

The check is deliberately strict. A false rejection costs the deterministic text the user would have
received anyway; a false acceptance puts an invented number in front of someone about to risk money.

## Phase 8B Status

Phase 8B supplies the provider behind the Phase 8A contract: `app/adapters/openai_explanations.py`,
plain httpx against the chat-completions endpoint, in the same shape as the Twelve Data and FMP
adapters and tested the same way — through `httpx.MockTransport`, with no key and no spend.

It stays off. `OPENAI_ENABLED=false` is the default, `create_explanation_provider` returns a
disabled provider that raises before any network call, and no service, command, route, or job
references any of it; 8C does the wiring. A safety test asserts each of those.

Two properties matter more than the HTTP details:

- **Unchecked text cannot escape.** `explain_validated` runs the Phase 8A validator and returns an
  outcome that carries text *only* when the answer was accepted. A rejected answer leaves no
  readable prose behind, so nothing downstream can print it or try to repair it.
- **The prompt carries only our own data** — the contract's serialized JSON. No market text, no
  third-party strings, nothing a stranger could write, so prompt injection is not a surface here.

Enabling it needs `OPENAI_ENABLED=true` and `OPENAI_API_KEY`; `OPENAI_MODEL`, `OPENAI_BASE_URL`, and
`OPENAI_MAX_OUTPUT_TOKENS` (default 400) are configurable. Output tokens are capped so a runaway
generation cannot become an unbounded bill. Nothing calls the provider yet even when enabled.

## Phase 8C Status

Phase 8C is the first slice where a model's words can reach a person, so the design is about what
happens when the model is wrong, missing, or slow.

`/explain EURUSD M15` renders exactly the report `/review` produces and appends one of two things:

```text
Пояснение (ИИ, проверено):
Окно данных полное: использовано 12 свечей из 12. ...
Пояснение не меняет решение выше.
```

```text
Пояснение недоступно: ответ не прошёл проверку.
Причины: ACTIONABLE_TEXT, UNKNOWN_NUMBER.
```

The deterministic report is sent in full in every case — provider disabled, unreachable, rate
limited, rejected by validation, or out of time. There is no path where `/explain` returns less than
`/review` would have, and text that failed validation is never shown.

**It is a separate command on purpose.** Every model call costs money, and `/review` is the command
you run repeatedly while watching data; it stays free and instant, calls nothing, and is byte-identical
whether or not the explanation layer is configured.

Both gates default to off: `OPENAI_ENABLED` (a provider exists) and `EXPLANATION_DELIVERY_ENABLED`
(it may answer a user). `EXPLANATION_BUDGET_SECONDS` (default 20) bounds the wait, because a Telegram
command must not hang on a provider. Nothing automatic — no service, job, or route — can call a
model; only the typed command can.

## Phase 9A Status

Phase 9A builds the price levels deferred since Phase 4 — and only those.
`app/domain/signal_price_plan.py` places an entry band, a protective level and two targets at
multiples of the window's average true range, anchored on the latest close. A stop twenty pips away
is tight on one instrument and absurd on another; one placed 1.5 average candle ranges away means
the same thing anywhere.

**Direction is an argument, not a conclusion.** The pipeline produces no direction — all eleven rules
are descriptive — so the builder is handed one. A safety test asserts that no function anywhere in
`app/` returns a `SignalDirection`, which is the mechanical signature of a strategy appearing. That
test failing is the signal that somebody is adding one.

**The multipliers are conventions, not calibrations.** Every other threshold in this project was
derived from an observed distribution; these could not be, because judging a protective distance
requires knowing whether that level or the target was reached first. Phase 9A-2 added that
measurement and found nothing that beats them, so they stand — as conventions with a baseline
attached rather than bare guesses. See `docs/phase9a-verification-report.md`.

Contracts are `DRAFT` and `NOT_ACTIONABLE`, carry no risk plan — position size needs an account
balance this project does not have — and are wired to nothing.

## Phase 9A-2 Status

Phase 9A-2 measures what happened *after* a window: for each historical moment, walk forward from the
fixed plan and record whether the target or the protective level was reached first.

```bash
uv run python -m scripts.measure_outcomes --days 180 --timeframe M15
```

`--stop-multiplier` and `--target-multiplier` sweep the Phase 9A level conventions; `--horizon-candles`
bounds how long a plan is given to resolve.

**This is the only module in the project allowed to read data after `as_of`.** Everywhere else the
Phase 3D invariant holds. Three tests fence the exception in: the analysis path may not name
`outcome_measurement` at all, no service, route, command or job may reference it, and it imports no
persistence, adapter, Telegram, API or scheduler code. A measurement that flowed back into a decision
would be look-ahead bias with a report attached.

**Ambiguity is counted, not guessed.** When one candle's range spans both levels, OHLC records four
prices and not their order; that window is `AMBIGUOUS` and counts against the plan rather than being
resolved the flattering way. On six months of EURUSD it is 2–4% of the sample, which is why the rest
of the numbers are usable.

**Every figure is gross of costs** — the project stores no spread — and the script says so under every
table.

The baseline, EURUSD over 180 days at the Phase 9A defaults: 38.4% of resolved M15 windows reached the
target first going LONG, 43.1% going SHORT. The gap is drift in the sample, not skill, which is
exactly why a future directional rule must be judged against the baseline for its own direction
rather than against a coin toss. See `docs/phase9a2-verification-report.md`.

## Phase 9A-3 Status

Phase 9A-3 is the first time this project takes a market view. `app/domain/direction_candidate.py`
is the only module exempt from the rule that no function may return a `SignalDirection`, and Phase 9A
wrote in advance that the day that test failed, somebody would be adding a strategy and would have to
say so out loud. This is that.

```bash
uv run python -m scripts.evaluate_direction --days 180 --timeframe M15 --sweep
```

**The candidate.** A new descriptive field measures how *straight* a window moved rather than how
far — `|Σ returns| / Σ|returns|`, bounded to `[0, 1]`. Above 0.60 the candidate proposes a direction
**against** the move; below it, and on any window the pipeline does not consider ready, it returns
`None`. It speaks about roughly one window in eight, and a safety test requires its return type to
stay optional so it can never be made to have an opinion on all of them.

**The method matters more than the candidate.** Acceptance criteria were fixed before the first run;
the sign and threshold were chosen on the first 60% of history; the last 40% was run once. The
comparison is against a coin toss *on the candidate's own windows*, not against the Phase 9A-2
baseline, which carries the sample's drift. The sign was chosen by measurement and contradicted the
intuitive reading — continuation lost at every threshold on both timeframes.

**Held out**: edge over a coin toss of +6.84 percentage points on M15 and +15.48 on H1. All four
criteria met — and then withdrawn the same day.

**Why it was withdrawn.** Backfilling a routine gap revealed that the stored history has no weekend
break: this provider returns a continuous 24/7 series, and about 28% of stored candles are
carried-forward filler from a closed market. The transition out of that filler — flat prices, then
one violently wide candle when trading resumes — is exactly the shape the candidate keys on.
Re-running with `--exclude-weekends` reverses the in-sample edge on both timeframes (−3.55 and
−6.61), which voids the very sweep that selected the hypothesis, and coverage falls below the
pre-registered floor.

The module stays in the tree, unwired and disproved, so the next candidate reuses the apparatus
rather than starting from an empty file. `docs/phase9a3-verification-report.md` keeps the original
report intact with a retraction header and an addendum, because what was believed and why is part of
the record.

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
MARKET_DATA_INGESTION_ENABLED=false
CALENDAR_ENABLED=false
CALENDAR_INGESTION_ENABLED=false
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
- `/review` (no args) returns a short authorized read-only structural review summary and persists
  nothing. `/review EURUSD M15` returns a snapshot-backed read-only review over a real pipeline
  decision — still no signals, no price levels, no AI.
- Scheduled digest delivery is disabled by default and has no automatic worker loop.
- Worker jobs update heartbeat, run foundation health checks, and — only when both market-data flags
  are enabled — ingest closed candles from the provider.

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
