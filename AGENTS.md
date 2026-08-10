# AI Trading OS Agent Guide

AI Trading OS is a foundation for a future Forex analysis and paper-trading platform.

Current project phase: phase_8d_local_explainer_foundation.
Phase 8D let a model on this machine answer `/explain`, and made it measurable whether one can.
**LM Studio, Ollama, llama.cpp and vLLM all serve the same `/v1/chat/completions` as OpenAI**, so
the 8B adapter was *generalised* rather than copied: `ChatCompletionsExplanationAdapter` takes a
provider name and an optional key, and a local endpoint is sent **no `Authorization` header at
all**. One transport, one module that can reach a model — the 8B boundary is unchanged and the
surface that has to stay honest did not double.
`OPENAI_ENABLED` became `EXPLANATION_PROVIDER=disabled|openai|local`, and the old flag is
**refused at startup rather than ignored**: it was set in both `.env` and `compose.yaml`, and a
setting that quietly stops working is worse than one that fails loudly.
**A model is not adopted because it answered; it is adopted because it passed.**
`scripts/evaluate_explanations.py` reports the share of answers the Phase 8A validator accepted
and a histogram of why it rejected the rest. `UNKNOWN_NUMBER` means the model invents figures —
no amount of prompt work makes that acceptable. See `docs/phase8d-verification-report.md`.
Phase 9C-1 built the forward outcome ledger, taken **before 9B** because delivery has nothing worth
delivering. On every closed window the worker fixes the levels for **both directions** and stores
them with the pipeline's verdict; a separate later tick settles the outcome from candles that
arrived afterwards. No account, no position size, no profit and loss, no direction chosen.
**Recording and resolving are two jobs on purpose**, not one: that is how "the plan was fixed before
its future was visible" becomes a property of the schedule instead of a comment. The value is
pre-registration, and it is checkable per row — `recorded_at` and `as_of` are both stored, so a row
written after its own future is self-identifying.
**When a boundary genuinely has to move, narrow it and name what may cross.** Three safety tests
were narrowed here; each names the one permitted file and gained a stricter replacement. Routing
around a boundary through an intermediate import would have passed the same tests and been worse.
See `docs/phase9c1-verification-report.md`.
Phase 9A-8 added a second instrument, **NOKSEK rather than GBPUSD on purpose**: GBPUSD correlates
with EURUSD at 0.85-0.9 because both are mostly a dollar move, so a threshold transferring there
proves little. NOKSEK has no dollar, about 1.8x the relative volatility, and a different session
profile — the harder test.
`max_close_excursion_atr` **transferred untouched**: the bound of 5.0, calibrated on EURUSD alone,
fires on 2.86% and 2.19% of NOKSEK windows against 3.43% and 2.56% on EURUSD. That is the strongest
evidence here that normalising by the window's own average true range makes a threshold portable.
`volatility_ratio` failed again — 10.88% on NOKSEK H1, outside the corridor — so the band moved to
**0.30/2.5**, which keeps all four series inside with the most room at the floor. It is now confirmed
twice, by a timeframe change and an instrument change, that this field is not normalised well enough;
recorded, not resolved by dropping the criterion.
**Calibrate across instruments, not only timeframes.** M15 against H1 is one market observed twice.
And NOKSEK's weekend filler is *not* visibly flat, unlike EURUSD's — the value-based signature that
made the contamination obvious on one instrument would have missed it on the other, which is why the
closed-market rule is calendar-based. See `docs/phase9a8-verification-report.md`.
Phase 9A-7 closed three measurement gaps, none of which was a failing test — each was a number that
meant something other than what it was read as. The drawdown measured only declines, so a window
that climbed steeply reported zero and a warning rule read that as calm;
`market_context.max_close_excursion_atr` takes the larger of the fall and the rise. The entry band
was measured from, so `stop=1.5` behaved as 1.6 and every break-even figure was computed for
multipliers nobody had set; distances now come from the anchor. And `RuleBehaviour` ignored
availability, calling a rule OFTEN_FIRES on 68 observations out of 17 078 — `RARELY_OBSERVED` is now
judged first.
**A constant must mean what it says at the point of use.** Before trusting a threshold, check what
the code does with it, not only what it is named.
The warning rule now reads `market_context.max_close_excursion_atr` bounded at **5.0**, firing on
3.43% (M15) and 2.56% (H1) — a 0.87-point spread, so both acceptance criteria are met. Keeping 4.0
would have fired at nearly 12%: a symmetric field is by construction never smaller than the one-sided
one it replaces, so replacing a field always requires recalibrating its bound.
The baseline is re-measured with the corrected geometry: LONG 38.50% / SHORT 44.38% on M15 and
39.06% / 45.53% on H1, break-even 42.86%. SHORT sits above break-even on both — that is a six-month
downtrend measured gross of costs, not an edge, and must never be quoted as one.
See `docs/phase9a7-verification-report.md`.
Phase 9A-6 re-derived every threshold over windows built **only from traded candles**, and
`data_quality.market_open` now judges every candle in the window rather than only its `as_of`.
`max_close_drawdown_atr` stays at 4.0 and earned it: 5.98% and 5.96% on M15 and H1, a 0.02-point
spread. `volatility_ratio` moved from 0.30/3.5 to **0.35/2.3**, because on clean data the old band
fired on 0.99% of M15 windows — the filler had been supplying both tails it was drawn around.
**Two acceptance criteria proved incompatible for that field, and the report says so rather than
picking a band that hides it:** the 1-10% corridor and the one-point convergence criterion cannot
both be met, because the timeframe spread grows monotonically with how much the band fires. The
convergence 7D-2 reported was an artefact of contamination. When a criterion cannot be met, record
that; do not quietly drop the criterion.
The Phase 9A-2 baseline was re-measured and is superseded: ambiguity fell from 2-4% to 0.5-0.6%,
timeouts from ~20% to ~14%, and the two timeframes converged to within 0.7 points. The sample's
drift is about 6 points in favour of SHORT on both. See `docs/phase9a6-verification-report.md`.
Phase 9A-5 makes provenance decide what counts as an observation. `REAL_MARKET_DATA_PROVIDERS` in
`app/core/constants.py` names the providers whose rows record a market; everything else is fabricated
by definition, and `load_history` — the one door every calibration passes through — refuses it unless
`--allow-synthetic` is passed. `scripts/purge_synthetic_data.py` removes such rows, dry-run first.
**Why a whitelist and not a sanity check on the values:** the seeded candles found on 2026-08-07 were
well-formed OHLC, correctly ordered, in a plausible range — and four hundred pips from the market,
sitting on the same timestamps as real ones. De-duplication keeps the first provider alphabetically,
so `local-seed` beat `twelve_data` on all thirty. No check on the numbers would have caught it.
**Verification and demo scripts must never write to a database a calibration reads** without their
rows being distinguishable; the `provider` column is that record, so never reuse a real provider's
name for a fixture. See `docs/phase9a5-verification-report.md`.
Phase 9A-4 gave a warning consequences. `data_quality.market_open` is REQUIRED, so a window recorded
while the market was shut is `NOT_READY` instead of trusted, and `READY_WITH_WARNINGS` exists so the
headline can no longer say all is well while failures are listed underneath it.
**The lesson is bigger than the fix.** A rule saying exactly this already existed as a WARNING and
failed on 28.08% of six months of windows; `warning_failure_count` was computed and never passed to
the status calculation, so the project observed its own contamination, printed it in every replay,
and built three phases on top. **A severity that cannot change an output is a comment.** Before
adding a check, establish what failing it does.
Two rules follow from it. A field that is always knowable must never resolve to `None` — "the market
was shut" is an observation, and returning `None` makes the rule UNAVAILABLE rather than failed,
which is silence. And an unavailable *warning* is silence rather than a finding, while an unavailable
*mandatory* rule fails closed: a mandatory condition nobody could check has not been satisfied.
See `docs/phase9a4-verification-report.md`.
Phase 9A-3 is where this project first takes a market view. `app/domain/direction_candidate.py` is
the **only** module exempt from the rule that no function may return a `SignalDirection`, and the
exemption holds only while four things stay true: the return type is optional, it cannot import the
outcome measurement that judges it, it imports no other layer, and nothing wired references it.
The candidate proposes a direction **against** a conspicuously one-sided window, above an efficiency
of 0.60, and abstains otherwise — including on any window the pipeline does not consider ready.
**It was measured and it failed, and the module stays unwired and disproved.** Its apparent edge came
from the data provider's synthetic weekend rows; exclude weekends and the in-sample result reverses
sign on both timeframes. See the addendum in `docs/phase9a3-verification-report.md`.
**The stored history is about 28% weekend filler.** This provider returns a continuous 24/7 series,
and the market is shut from Friday evening to Sunday evening. Those rows carry prices forward, so
they depress the average true range and the return to real trading looks like a violent one-sided
move. Anything calibrated over stored history — the Phase 7C thresholds, the Phase 9A-2 baseline —
was measured partly on filler and should be re-measured weekend-free before anything is built on it.
The filter moved into the domain in 9A-4 (`app/domain/market_calendar.py`).
**The held-out 40% of this history has now been examined twice and is spent.** No future candidate on
EURUSD may claim a fresh out-of-sample test against it; genuinely unseen data now means another
instrument or a later period.
Phase 9A-2 adds outcome measurement: `app/domain/outcome_measurement.py` walks forward from a fixed
plan and records whether the target or the protective level came first. It is the **only** module
permitted to read data after `as_of`, and its results must never flow back into a snapshot, a rule,
or a decision. A candle spanning both levels is `AMBIGUOUS`, counted rather than guessed. Every
figure is gross of costs, and any document quoting one must say so. The baseline it produced
(EURUSD M15, 38.4% LONG / 43.1% SHORT at the 9A defaults) is what any future direction has to beat —
per direction, not against 50%. See `docs/phase9a2-verification-report.md`.
Phase 9A builds price levels and nothing else: `app/domain/signal_price_plan.py` takes a direction
as an argument and places entry, protective and target levels at multiples of the window's average
true range. It contains no strategy — nothing in this project decides "up" or "down", and a test
asserts no function anywhere returns a `SignalDirection`. The multipliers are conventions, not
calibrations, because judging a stop distance needs outcome measurement the project does not have.
Contracts are `DRAFT` and `NOT_ACTIONABLE`, carry no risk plan, and are wired to nothing.
Phase 8C delivers explanations through a separate `/explain EURUSD M15` command, gated by two flags
that are both off by default (`OPENAI_ENABLED`, `EXPLANATION_DELIVERY_ENABLED`). The deterministic
report is always sent in full; an explanation is appended only after passing Phase 8A validation,
and any failure — disabled, unreachable, rejected, or out of time — becomes one honest line under
the report. `/review` is untouched and still spends nothing. This closes Phase 8.
Phase 8B adds the OpenAI adapter behind the Phase 8A contract: plain httpx, `OPENAI_ENABLED=false`
by default, and wired to nothing (8C does that). It cannot return unchecked text — `explain_validated`
runs the Phase 8A validator and the outcome carries text only when the answer was accepted. The
prompt contains our own serialized contract and nothing a stranger wrote.
Phase 8A defines what a future Chief AI may be given (`ExplanationInput`) and how its answer is
checked before anyone reads it. It contains no provider, no network call, no key, and is wired to
nothing. Validation is fail-closed: any finding means the deterministic Russian text is used
instead. The model may repeat numbers it was given and no others.
Phase 7D-2 replays the built-in rules over stored history and reports how each one behaved, so the
Phase 7C thresholds can be derived from an observed distribution instead of two live windows. The
replay is read-only, never scheduled, and changes no threshold by itself: it measures, and a
threshold moves only through a deliberate edit that records its evidence.
Phase 7D-1 adds a manual historical backfill script so later calibration has a real distribution to
work from. It is deliberately never scheduled: on a timer it would burn provider quota repeatedly.
It stores candles only and reports a suspected provider truncation rather than silently accepting a
short response.
Phase 7B adds economic-calendar ingestion and the two event rules that consume it, bringing the
rule set to eleven across four rulesets (data quality, market context, event context, time filter).
Calendar ingestion is gated by two flags that are both off by default (`CALENDAR_ENABLED`,
`CALENDAR_INGESTION_ENABLED`). The ingestion window straddles the tick, reaching forward over
announced releases, because calendars are published ahead of time; the analysis snapshot still only
exposes what happened at or before `as_of`, so the rules read backwards. Rules stay descriptive:
they answer "can this window be trusted" and "what regime is this", never "what should be traded".
No directions, no price levels, no scoring, no AI. Rules and rulesets stay `enabled=False`. External
integrations remain disabled by default. The project contains no strategy engine, no signal
generation engine, no `SignalContract` construction, no broker order APIs, no paper trading, and no
real trading.

## Start and Checks

- Install: `uv sync`
- Start Docker stack: `docker compose up --build`
- Migrate: `uv run alembic upgrade head`
- Test: `uv run pytest`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Type-check: `uv run mypy app`
- Full check: `make check`

## Repository Layout

- `app/api`: API adapters.
- `app/services`: application services.
- `app/domain`: domain value objects and contracts.
- `app/persistence`: database models, repositories, unit of work.
- `app/telegram`: Telegram adapter.
- `app/scheduler`: worker process.
- `docs`: detailed project documentation.

## Rules

- Dependency direction is adapters -> application services -> domain.
- Domain code must not import FastAPI, Telegram, SQLAlchemy, PostgreSQL, APScheduler, OpenAI, market-data providers, or calendar providers.
- Use async SQLAlchemy sessions only; one `AsyncSession` per unit of work or task.
- Use `Decimal` for financial values. Do not use binary floating point for money, prices, percentages, or risk.
- Store timestamps in UTC; present user-facing time in Europe/Stockholm when needed.
- Telegram user-facing text must be Russian.
- Every Telegram message must contain exactly one semantic emoji at the beginning.
- Never add real trading execution, broker order APIs, real account credentials, or live position management.
- Never add strategy execution logic, setup scoring, buy/sell recommendations, paper trading,
  broker APIs, order execution, or real trading while working in foundation phases. In Phase 4A,
  `LONG`/`SHORT` may appear only as contract enum values, not as generated recommendations. Rule
  evaluation against real market data is allowed starting in Phase 4F, strictly bounded by the
  Phase 4F rule below.
- While working in Phase 3H, output is limited to neutral readiness reports and readiness digests.
  Scheduled delivery must remain disabled by default. Do not add Telegram trading signals, entry
  guidance, LONG/SHORT advice, buy/sell recommendations, automatic runtime loops, or paper-trading
  actions.
- While working in the merged Phase 3I snapshot versioning/evidence slice, schema versioning,
  data-completeness ratios, and evidence timestamps are descriptive-only and must not influence
  readiness status, quality checks, or any branching decision. The `AnalysisAgent` Protocol in
  `app/schemas/agents.py` must remain unimplemented and unwired to any service, route, or
  scheduler.
- While working in Phase 4D, strategy registry vocabulary is allowed only inside explicit ruleset
  registry/fixture domain models, the registry loader, and their tests/docs. Rule specs, rule sets,
  registry items, and registry snapshots must remain disabled/non-actionable. Do not evaluate rules
  against candles, indicators, economic events, context snapshots, analysis snapshots, or signal
  contracts. Do not add strategy engines, signal generation, setup scoring, confidence scoring,
  Telegram signal sending, API signal routes, scheduler signal jobs, broker APIs, order execution,
  automatic runtime loops, or paper-trading actions.
- While working in Phase 4E, disabled pipeline report vocabulary is allowed only inside explicit
  pipeline report domain models, the disabled report shell, and their tests/docs. Pipeline reports
  must remain disabled/non-actionable. The shell may consume only Phase 4D registry snapshots. Do
  not evaluate rules against candles, indicators, economic events, context snapshots, analysis
  snapshots, or signal contracts. Do not add strategy engines, decision engines, signal generation,
  setup scoring, confidence scoring, Telegram signal sending, API signal routes, scheduler signal
  jobs, broker APIs, order execution, automatic runtime loops, or paper-trading actions.
- While working in Phase 4F, the evaluator (`app/domain/strategy_field_resolver.py`,
  `app/domain/strategy_rule_evaluator.py`) may only read `AnalysisSnapshot`,
  `MarketFeatureSnapshot`, and `MarketContextSnapshot`. It must never import
  `app.persistence`, `app.telegram`, `app.scheduler`, `app.api`, or `app.domain.entities.signal_contract`.
  It must never construct a `SignalContract`, calculate entries/stops/targets, calculate position
  size, or send a Telegram message. `RuleSetEvaluationReport.is_actionable` must remain `False`
  unconditionally, enforced by the model itself, not by caller discipline.
- While working in Phase 4G, the composer (`app/domain/strategy_decision_composer.py`) may only
  read the Phase 4D registry and `AnalysisSnapshot`/`MarketFeatureSnapshot`/`MarketContextSnapshot`
  through the Phase 4F evaluator. It must never import `app.domain.entities.signal_contract` or
  construct a `SignalContract`, and must never import `app.persistence`, `app.telegram`,
  `app.scheduler`, or `app.api`. `PipelineDecisionReport.is_actionable` must remain `False`
  unconditionally, enforced by the model itself. Real price-level (entry/stop/take-profit)
  construction is out of scope until Phase 9A (signals, delivery, and paper trading). See `PLANS.md`
  for the authoritative roadmap; the tail was renumbered on 2026-07-22 when Phase 7 was redefined as
  live data and real analysis.
- While working in Phase 5, manual review domain code may consume only already-created immutable
  Phase 4G/4F/4E report artifacts. It must not call the Phase 4 evaluator/composer, read market data,
  use a database/session/UoW, call providers, register scheduler jobs, persist reports, or write
  runtime files. Reports, comparisons, CLI output, and `/review` replies must remain read-only,
  disabled/non-actionable, and contain explicit no-signal messaging. Do not add rule evaluation,
  strategy or decision engines, setup/confidence scoring, AI/OpenAI/LLM calls, automatic Telegram
  alerts, broker APIs, order execution, paper trading, or real trading.
- While working in Phase 6, the snapshot-backed review (`app/domain/snapshot_review.py`,
  `app/telegram/snapshot_review_formatter.py`) may build an `AnalysisSnapshot` (only in the Telegram
  command layer, via the injected `AnalysisService`) and run the Phase 4G composer over it. The
  Phase 6 domain module must receive an already-built `AnalysisSnapshot` and must not import
  `app.persistence`, `app.adapters`, `app.scheduler`, `app.api`, or
  `app.domain.entities.signal_contract`. It must never construct a `SignalContract`, calculate price
  levels, call AI, or send an automatic/unsolicited message. `/review` output (both structural and
  snapshot-backed) must remain read-only and non-actionable.
- While working in Phase 7A, the ingestion service (`app/services/market_data_ingestion_service.py`,
  `app/domain/entities/ingestion.py`) may call `MarketDataProvider.get_closed_candles` and write
  candles through `candles.upsert_many`. It must depend on the provider Protocol, never a concrete
  adapter, and must not import `app.telegram`, `app.api`, or
  `app.domain.entities.signal_contract`. It must never produce signals, directions, price levels,
  scoring, AI output, or user-facing messages. Both `MARKET_DATA_ENABLED` and
  `MARKET_DATA_INGESTION_ENABLED` must stay `false` by default. An empty provider response is a
  normal outcome (closed market), not a failure, and one failing pair must not abort the others.
- While working in Phase 7C, built-in rules (`app/domain/strategy_ruleset_registry.py`) and their
  resolvers (`app/domain/strategy_field_resolver.py`) may read values the snapshot already computes,
  and nothing else: 7C adds no new indicator math, which belongs to the Phase 3B/3C engines. Rules
  must stay descriptive — no direction, no entry, no price levels, no scoring, no recommendation —
  and must keep `enabled=False` so they remain non-actionable. Do not use `EXISTS`/`NOT_EXISTS` for
  an analytical rule: those only test presence and pass on empty data. A resolver must return `None`
  when its source is missing rather than substituting a value, and must never raise or divide by
  zero. Every threshold must be calibrated against real observed data and the evidence recorded in
  the phase verification report.
- While working in Phase 7B, calendar ingestion
  (`app/services/economic_calendar_ingestion_service.py`,
  `app/domain/entities/calendar_ingestion.py`) may call `EconomicCalendarProvider.get_events` and
  write events through `economic_events.upsert_many`, depending on the provider Protocol and never a
  concrete adapter. Both `CALENDAR_ENABLED` and `CALENDAR_INGESTION_ENABLED` stay `false` by
  default. An empty response is a normal outcome (a quiet calendar), not a failure, and provider
  errors are recorded rather than raised into the scheduler. Ingest forward but evaluate backward:
  storing announced releases is legitimate, while surfacing post-`as_of` events into a snapshot
  would break the Phase 3D no-future-data proof and must stay a separate, deliberate decision.
- While working in Phase 7D-1, the backfill
  (`app/services/market_data_backfill_service.py`, `scripts/backfill_market_data.py`) must stay a
  manual script and must never be registered as a scheduler job. It must chunk requests inside
  `provider_max_request_range_days`, pace them with a delay, and flag a chunk as possibly truncated
  when the oldest returned candle sits far after the requested start — silently accepting a short
  response would corrupt every later calibration. A run that failed or looked truncated must not
  report success, and the CLI must exit non-zero.
- While working in Phase 7D-2, the replay (`app/domain/rule_replay.py`,
  `app/domain/rule_calibration.py`, `app/domain/entities/calibration.py`,
  `scripts/replay_rules.py`) must stay read-only and must never be registered as a scheduler job.
  The domain modules take candles and events as arguments and must not import `app.persistence`,
  a session, or a unit of work — the Phase 4G boundary keeps the composer out of anything that owns
  storage, so loading history belongs to the caller. Replay must evaluate through the real
  `AnalysisEngine` and Phase 4G composer rather than a lookalike, otherwise the measured pass rates
  say nothing about `/review`. It must never rewrite thresholds automatically: a threshold change is
  a reviewable edit that records the percentile and sample size it came from. A rule that never
  fired across real history is a defect to report, not a rule that passed.
- While working in Phase 8A, the explanation contract (`app/domain/entities/explanation.py`,
  `app/domain/explanation_contract.py`) must stay pure domain code: no `httpx`, no OpenAI, no
  `app.persistence`, `app.adapters`, `app.telegram`, `app.api`, or `app.scheduler`, and no service,
  route, command, or job may reference it — 8A ships unwired, and the adapter arrives in 8B. Do not
  reuse the older scored Chief AI request stub in `app/schemas/agents.py`: it demands fields the
  pipeline never produces and the safety tests ban. `ExplanationInput` carries no direction, price
  level, position size, or scoring field, and stays non-actionable. Validation returns findings
  rather than raising, and an explanation counts as accepted only when nothing was found; a caller
  that sees any finding must fall back to the deterministic text rather than repair the answer. The
  actionable-text check must cover Russian as well as English — the Phase 5 detector alone matches
  "buy", not "покупай", and this project speaks Russian to its user.
- While working in Phase 8B, the explanation adapter (`app/adapters/openai_explanations.py`) is the
  only file in the project allowed to reach a model, and only it is exempt from the `OpenAI`/`LLM`
  term ban — every trading-behaviour ban still applies to it. It must not import `app.persistence`,
  `app.telegram`, `app.api`, `app.scheduler`, or `app.schemas.agents`, and no service, command,
  route, or job may reference it until 8C. `OPENAI_ENABLED` stays `false` by default and the
  disabled provider must raise before any network call. The API key travels in the `Authorization`
  header, never a query parameter. Prompts may contain only the Phase 8A contract's own serialized
  content — no market text, no third-party strings. `explain_validated` must run the Phase 8A
  validator, and a rejected answer must leave no readable text in the outcome. Cap output tokens so
  a runaway generation cannot become an unbounded bill.
- While working in Phase 8C, the explanation may only reach a user through the `/explain` command a
  person types. No service, scheduler job, or API route may build the provider or call it: an
  automatic path would spend money and show model text to someone who never asked. The deterministic
  report must be sent in full in every case, including when the model fails — the explanation is an
  appendix and says so. Never show text that failed validation; report the issue codes instead. Both
  `OPENAI_ENABLED` and `EXPLANATION_DELIVERY_ENABLED` default to `false`, and the call must run
  inside `EXPLANATION_BUDGET_SECONDS` so a slow provider cannot hang a Telegram command. `/review`,
  `/snapshot`, `/digest`, and scheduled delivery stay model-free.
- A threshold on a raw magnitude is a defect waiting to surface. Before adding a rule over a
  measured quantity, divide it by what is typical for that window — the timeframe, the instrument,
  and the period all change what "large" means. `market_context.volatility_ratio` and
  `market_context.max_close_drawdown_atr` are the pattern; the pre-2026-08-05 absolute drawdown
  bound is the counter-example, which fired on 1.19% of M15 and 7.14% of H1 windows for the same
  data. Acceptance for a normalised field: firing rates across timeframes within about one
  percentage point. Dimensions must match — a fraction of price is not comparable to an absolute
  price amount without converting one of them first.
- While working in Phase 9A, `app/domain/signal_price_plan.py` is the only file allowed to compute
  entries, protective levels, or targets; every other module in `app/` is scanned for those terms
  and must contain none. Distances are average-true-range multiples, never fixed prices. The module
  must not import `app.persistence`, `app.adapters`, `app.telegram`, `app.api`, or `app.scheduler`,
  and no service, command, route, or job may reference it — 9B does the wiring. Contracts stay
  `DRAFT` and `NOT_ACTIONABLE` with `risk_plan=None`: position size needs an account balance the
  project does not have and must not invent. **Direction is an argument, never a conclusion.** No
  function anywhere may return a `SignalDirection`; the day one does, somebody is adding a strategy
  and must say so out loud. The multipliers are uncalibrated conventions and any document mentioning
  them must say so. Since 9A-2 they at least have a measured baseline attached; a sweep found no
  setting that pays for its own geometry without a direction, so nothing justifies moving them yet.
- While working in Phase 9A-2, `app/domain/outcome_measurement.py` is the only module in the project
  allowed to look past `as_of`, and `scripts/measure_outcomes.py` is the only place that slices
  candles from after a window. Everything in the analysis path — `analysis_engine`, `feature_engine`,
  `context_engine`, `snapshot_review`, `rule_replay`, `signal_price_plan`, every `strategy_*` module
  — is forbidden from even naming it, and no service, route, command, or job may reference it:
  measurement is an offline instrument, never a scheduled one. A result that flows back into a
  decision would break the Phase 3D no-future-data proof.
  Three reporting rules, each enforced by the shape of the result rather than by memory: a candle
  spanning both levels is `AMBIGUOUS` and counted in the denominator, never silently resolved the
  flattering way; an unresolved window is `TIMEOUT`, never dropped and never scored as a loss; shares
  are `None` when nothing resolved, never a substituted zero. Every outcome is gross of costs — there
  is no spread data — and any table quoting one must say so on the same page.
  When comparing directions, compare against the baseline **for that direction**: the six-month
  EURUSD sample carries a drift of its own (SHORT ahead by 4.6 п.п. on M15 and 10.9 on H1 with no
  strategy at all), so a rule that always says SHORT would look clever for reasons that are not the
  rule. Overlapping windows mean the counts are stable, not statistically powerful; no confidence
  interval may be read off them.
- While working in Phase 9A-3 or on any later directional idea, `app/domain/direction_candidate.py`
  is the only file in `app/` allowed to return a `SignalDirection`, and it must return an optional
  one — a candidate that cannot abstain is not acceptable here. It may not import
  `outcome_measurement` or anything from `app.persistence`, `app.adapters`, `app.telegram`,
  `app.api`, or `app.scheduler`, and no service, route, command, or job may reference it. A second
  module producing directions is a strategy leaking out of the one place allowed to hold one.
  **A directional idea is evaluated before it is believed, and the method is not negotiable:**
  acceptance criteria are written down *before* the first run; the threshold and the sign are chosen
  on the first 60% of history; the remaining 40% is run **once** and never re-tuned against; and the
  comparison is against a coin toss **on the candidate's own windows**, never against the global
  baseline, which carries the sample's drift. Because the benchmark pools both sides of each window,
  a hypothesis and its inversion are one signed result rather than two attempts.
  Any figure quoted from that evaluation carries its caveats or is not quoted: overlapping windows
  make the effective sample far smaller than the counts, so no significance may be claimed; every
  outcome is gross of costs and the project cannot yet compute what costs would leave; and a
  mechanism written after the numbers is a story, not evidence. A negative verdict is a result — the
  candidate stays in the tree, unwired and disproved, so the next idea reuses the apparatus.
- Never fabricate market data, calendar data, agent evidence, or scan results.
- LLM output may explain deterministic results only; it must not change prices, scores, risk, or rejected decisions.
- Update documentation when architecture or safety boundaries change.

## Definition of Done

Code is complete only when tests, formatting, linting, type checking, migrations, and relevant Docker checks have been run or a truthful limitation is documented in `docs/foundation-report.md`.
