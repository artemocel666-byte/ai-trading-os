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
signal-contract price-level construction deliberately deferred to Phase 6. Production Twelve Data
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
persisted and remain disabled/non-actionable.

## Future Phases

- Phase 2: market-data and calendar adapters — completed as disabled-by-default factories plus
  production adapters covered by MockTransport-backed contract tests
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
- Phase 6: Telegram signal delivery — includes the deferred `SignalContract` price-level
  (entry/stop/take-profit) construction that Phase 4 deliberately did not build; not started
- Phase 7: backtesting and paper trading — not started

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

Phase 5 manual review layer foundation is complete. Later phases have not started. Real
`SignalContract` construction and all trading behavior remain inactive.
