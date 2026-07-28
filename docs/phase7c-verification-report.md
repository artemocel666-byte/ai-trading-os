# Phase 7C Verification Report

Generated: 2026-07-28

## Scope

Phase 7C replaces the three placeholder rule fixtures with nine analytical rules across three
rulesets, and adds the seven value resolvers they need.

`PROJECT_PHASE = "phase_7c_analytical_ruleset_foundation"`

## The defect this phase closes

All three placeholder rules used the `EXISTS` operator, which asks "did a value resolve?", not
"what is the value?". The resolver honestly returned `False` when there were no candles — and
`False is not None`, so the rule PASSED. Proven on 2026-07-27:

```text
readiness = BLOCKED, used_candles = 0   →  pipeline READY_FOR_REVIEW, "Замечаний: 0"
readiness = READY,   used_candles = 12  →  pipeline READY_FOR_REVIEW, "Замечаний: 0"
```

The rules validated the machinery, not the market, so `/review` gave the same answer regardless of
reality.

## The rules

| Ruleset | Rule | Operator | Severity |
| --- | --- | --- | --- |
| `foundation.data_quality.v1` | `data_quality.used_candle_count` | `GTE 8` | BLOCKING |
| | `data_quality.completeness_ratio` | `GTE 0.8` | REQUIRED |
| | `data_quality.market_data_complete` | `EQ true` | REQUIRED |
| | `data_quality.latest_candle_age_minutes` | `LTE 90` | WARNING |
| `foundation.market_context.v1` | `market_context.snapshot_ready` | `EQ true` | REQUIRED |
| | `market_context.volatility_ratio` | `BETWEEN 0.4 .. 2.5` | WARNING |
| | `market_context.max_close_drawdown` | `LTE 0.01` | WARNING |
| `foundation.time_filter.v1` | `time_filter.session_name` | `IN (london, new_york)` | WARNING |
| | `time_filter.utc_weekday` | `LTE 4` | WARNING |

Scope: descriptive only. These answer "can this window be trusted" and "what regime is this", never
"what should be traded". No direction, price level, scoring, or AI. Rules and rulesets keep
`enabled=False`.

## Threshold calibration evidence

Measured against live EURUSD Twelve Data windows on 2026-07-28 (12-candle windows):

```text
EURUSD M15  17:15..20:15   ATR = 0.00034083   last TR = 0.00025
  completeness_ratio = 1        volatility_ratio = 0.7335    max_close_drawdown = 0.00046
EURUSD H1   07:00..19:00   ATR = 0.00100417   last TR = 0.00061
  completeness_ratio = 1        volatility_ratio = 0.6075    max_close_drawdown = 0.00307
```

Calibration outcome:

- `max_close_drawdown` was planned at `0.02` and **would never have fired** — 43× the observed M15
  value and 6.5× the H1 value. Lowered to `0.01`, roughly three times the larger observation, so it
  stays quiet normally but still flags a genuinely large decline. Recorded in the source as a
  comment next to the constant.
- `volatility_ratio` band `0.4 .. 2.5` contains both observations (0.73, 0.61) with margin, so it
  fires only on real outliers. Kept.
- `completeness_ratio ≥ 0.8` and `latest_candle_age ≤ 90 min` both passed comfortably on healthy
  windows and fail on the degraded window below. Kept.

The sample is only two windows. Phase 7D replay over real history should revisit these numbers.

## Live proof: the pipeline now distinguishes states

Same code, same database, two different windows:

```text
--- ЗДОРОВОЕ ОКНО (live Twelve Data candles) ---
  snapshot readiness = READY
  PIPELINE STATUS    = READY_FOR_REVIEW
  all 9 rules PASSED
  /review -> Статус: READ_ONLY | Замечаний: 0

--- ТЕКУЩЕЕ ОКНО (no candles: worker had been stopped) ---
  snapshot readiness = BLOCKED
  PIPELINE STATUS    = BLOCKED
  data_quality.used_candle_count       BLOCKING FAILED
  data_quality.completeness_ratio      REQUIRED FAILED
  data_quality.market_data_complete    REQUIRED FAILED
  market_context.snapshot_ready        REQUIRED FAILED
  market_context.volatility_ratio      WARNING  UNAVAILABLE
  market_context.max_close_drawdown    WARNING  UNAVAILABLE
  data_quality.latest_candle_age_min   WARNING  UNAVAILABLE
  time_filter.* PASSED
  /review -> Статус: INCOMPLETE | Замечаний: 1
```

Before 7C both columns were identical. This is the property the phase exists to create.

Note the `UNAVAILABLE` results: resolvers return `None` when their source is missing rather than
substituting a value, so a missing measurement is visibly distinct from a failed one.

## Files

Created:

- `docs/phase7c-verification-report.md`

Modified:

- `app/domain/strategy_field_resolver.py` — seven new resolvers
- `app/domain/strategy_ruleset_registry.py` — nine rules across three rulesets, threshold constants,
  `_foundation_rule` extended for `expected_value`/`lower_bound`/`upper_bound`
- `app/core/constants.py`, `AGENTS.md`, `PLANS.md`, `README.md`
- `tests/unit/test_strategy_rule_evaluation_foundation.py`,
  `tests/unit/test_strategy_ruleset_registry_foundation.py`,
  `tests/unit/test_strategy_decision_composition_foundation.py`,
  `tests/unit/test_disabled_pipeline_report_shell_foundation.py`, plus the tests asserting the
  literal project-phase string

No migration was created. No API route, Telegram command, or scheduler job was added.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 98 source files |
| `uv run pytest` (excluding two pre-existing `.env`-placeholder collection failures) | Passed; 415 passed |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

Notable tests added:

- `test_compose_distinguishes_a_healthy_window_from_a_thin_one` — the regression that would have
  caught the original placeholder gap.
- `test_no_builtin_rule_uses_the_always_passing_exists_operator` — prevents the defect returning.
- `test_every_builtin_ruleset_validates_as_valid` — a banned vocabulary token would make a ruleset
  INVALID and the composer would silently skip it, so this keeps the rules actually running.
- `test_volatility_ratio_never_divides_by_zero` — a perfectly flat window has a zero average true
  range.

## Remaining risks / notes

- Thresholds are calibrated on two live windows only. Phase 7D should re-derive them from a real
  distribution over history.
- A single `max_close_drawdown` threshold spans both M15 and H1, whose windows cover very different
  spans of time. A per-timeframe threshold would be more precise and is worth revisiting.
- Event-proximity rules are absent by design: they need the calendar ingestion from Phase 7B.
- The registry keys were renamed from `foundation.*.minimum` / `foundation.time_filter.session` to
  `foundation.*.v1`, since these are no longer placeholders. Fingerprints change accordingly.
