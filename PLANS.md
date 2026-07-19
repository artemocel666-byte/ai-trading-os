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

## Current Implementation Status

The repository has completed the foundation phase, Phase 2 hardening/data adapters, Phase 3A
data-quality foundation, Phase 3B deterministic feature-engine foundation, Phase 3C deterministic
indicator/context foundation, Phase 3D deterministic analysis snapshot/readiness report foundation,
Phase 3E local Telegram readiness-report foundation, Phase 3F deterministic readiness scheduler and
snapshot digest foundation, Phase 3G manual Telegram digest command foundation, Phase 3H neutral
scheduled digest delivery foundation, and Phase 3I persistent neutral digest delivery audit
foundation plus the merged Phase 3I snapshot versioning/evidence foundation. Phase 4A signal
contract foundation is contract-only and defines future signal contract shapes without generating
signals or trading recommendations. Phase 4B strategy rule specification foundation is
specification-only and defines future rule set shapes without evaluating rules or activating
strategy logic. Phase 4C strategy ruleset validation foundation validates the structure of Phase 4B
rule sets without evaluating market data or producing decisions. Phase 4D strategy ruleset registry
foundation loads disabled built-in rule set fixtures and validates them through the Phase 4C
validator without evaluating data or producing decisions. Production Twelve Data and FMP adapters
exist, but live integrations remain disabled by default. Scanning state can be enabled or disabled,
Telegram can request readiness reports and readiness digests, and scheduled digest orchestration
remains disabled by default. Snapshots carry schema versions, deterministic data-completeness ratios,
and candle-level evidence timestamps. A read-only agent contract exists but is unimplemented and
unwired. No strategy engine, rule evaluation against market data, signal generation, concrete AI
agent, paper-trading, or execution flow is connected.

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
- Phase 4E+: future analytical agents and Decision Engine work remains not started
- Phase 5: Russian Chief AI explanations
- Phase 6: Telegram signal delivery
- Phase 7: backtesting and paper trading

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

Phase 4D strategy ruleset registry foundation is the current task. Later Phase 4 behavior,
including rule evaluation against market data, analytical agents, signal generation, and
decision-engine work, has not started and is not active.
