# Phase 7D-2 Verification Report

Generated: 2026-08-01

## Scope

Phase 7D-2 replays the built-in rules over the history Phase 7D-1 stored and reports how each one
behaved, so the Phase 7C thresholds could be re-derived from an observed distribution instead of the
two live windows the 7C report flagged as its weakest point. This closes Phase 7.

`PROJECT_PHASE = "phase_7d2_historical_validation_foundation"`

Two questions, answered by measurement:

1. **Does each rule behave sanely?** A descriptive rule must be quiet in normal conditions *and*
   able to fire. A rule that passes every window of six months is dead — the Phase 7C `EXISTS`
   defect wearing a different mask.
2. **Where do the thresholds belong?** Percentiles of the observed values replace guesses.

Stated before looking at the data, so the calibration was not fitted to taste: warnings should fire
on roughly 1–10% of windows; blocking and required data-quality rules should pass on nearly every
window of a healthy feed.

## Implementation

- `app/domain/entities/calibration.py` — `FieldDistribution`, `RuleOutcomeTally`,
  `RuleCalibrationReport`. The behaviour verdict is a computed field derived from the counts, so it
  cannot drift from the numbers it describes.
- `app/domain/rule_calibration.py` — nearest-rank percentiles over `Decimal`. No interpolation: every
  reported figure is a value the sample actually contained, and no binary floating point touches a
  price.
- `app/domain/rule_replay.py` — the window walk, evaluating through the **real** `AnalysisEngine` and
  the Phase 4G `StrategyDecisionComposer`. Pass rates measured against a lookalike evaluator would
  say nothing about what `/review` reports.
- `scripts/replay_rules.py` — CLI; loads the range once and prints two tables.

**Layering note.** The walk first lived in `app/services/rule_replay_service.py`, and two Phase 4
safety tests failed: no file in `app/services/` may reference `StrategyDecisionComposer` or be named
after rules. That boundary is deliberate — the composer stays out of anything owning a session so no
automatic pipeline can grow around it. The Phase 6 precedent applies: composition lives in the
domain (`app/domain/snapshot_review.py`), and the calling layer loads the data. The walk therefore
moved into `app/domain/rule_replay.py` and history loading into the script, with a new safety test
asserting the domain module never touches persistence.

## Measurements

Six months of EURUSD, 2026-01-30 to 2026-07-29. 16 909 M15 windows and 4 219 H1 windows, 12 candles
each — the same window shape `/review` builds.

### Field distributions (before recalibration)

M15, n = 16 909 windows:

```text
  field                                          n     n/a          min          p05          p25       median          p75          p95          max
  data_quality.completeness_ratio            16909       0      0.08333            1            1            1            1            1            1
  data_quality.latest_candle_age_minutes     16909       0            0            0            0            0            0            0            0
  data_quality.used_candle_count             16909       0            1           12           12           12           12           12           12
  event_context.high_impact_event_count      16909       0            0            0            0            0            0            0            1
  event_context.minutes_since_latest_event      68   16841      1.86267           15           45           75          120          165          180
  market_context.max_close_drawdown          16907       2            0      0.00005       0.0003      0.00062      0.00113      0.00244      0.03819
  market_context.volatility_ratio            16908       1      0.04029      0.31884      0.63651      0.88158      1.22667      2.06452     10.79842
  time_filter.utc_weekday                    16909       0            0            0            1            3            5            6            6
```

Finer quantiles for the two fields that were recalibrated:

| Field | Timeframe | p01 | p03 | p05 | p95 | p98 | p99 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| volatility_ratio | M15 | 0.15643 | 0.24490 | 0.31884 | 2.06452 | 2.75079 | 3.52522 |
| volatility_ratio | H1 | 0.15258 | 0.26128 | 0.31304 | 2.19455 | 3.02813 | 3.61260 |
| max_close_drawdown | M15 | 0.000025 | 0.000035 | 0.000052 | 0.002441 | 0.003257 | 0.004267 |
| max_close_drawdown | H1 | 0.000026 | 0.000077 | 0.000119 | 0.004546 | 0.005890 | 0.007222 |

### Two findings the replay produced

**1. `time_filter.session_name_allowed` could never fire.** Over six months it recorded 9 867 passes,
0 failures and 7 042 UNAVAILABLE on M15. The resolver returned `None` outside London and New York,
and an unresolved field makes the rule UNAVAILABLE rather than failed — so a window outside both
sessions, which is exactly what the rule exists to flag, produced silence.

Fixed in `app/domain/strategy_field_resolver.py`: the resolver now reports `off_session`. This is not
a substituted value — the hour is known, so "neither session" is a real reading. The Phase 7C rule
about returning `None` applies to a *missing source*, which this never was.

**2. `data_quality.latest_candle_age_minutes` cannot be exercised by this replay.** Every `as_of` in
the walk is a candle close, so the age is 0 by construction. The rule is not dead: it detects a
stalled feed, and a backfilled history contains no stalled feed. Rather than weaken the rule or the
check, the CLI grew `--allow-quiet RULE_ID`, a named acknowledgement that this history cannot
exercise a specific rule. Every other silent rule still fails the run.

### Thresholds re-derived

| Constant | Before | After | Evidence |
| --- | --- | --- | --- |
| `MINIMUM_VOLATILITY_RATIO` | 0.4 | 0.30 | ≈p03 (0.2449 M15, 0.2613 H1) |
| `MAXIMUM_VOLATILITY_RATIO` | 2.5 | 3.5 | ≈p99 (3.5252 M15, 3.6126 H1) |
| `MAXIMUM_CLOSE_DRAWDOWN` | 0.01 | 0.004 | between p98 and p99 on H1; above p99 on M15 |

Firing rates before and after, over the same windows:

| Rule | M15 before | M15 after | H1 before | H1 after |
| --- | --- | --- | --- | --- |
| `market_context.volatility_ratio` | 10.45% | **5.55%** | 13.84% | **5.74%** |
| `market_context.max_close_drawdown` | 0.26% | **1.19%** | 0.14% | **7.14%** |
| `time_filter.session_name_allowed` | 0.00% (could not fire) | **41.65%** | 0.00% | **41.76%** |

Every other rule was left alone; its firing rate is unchanged.

### Full rule behaviour after recalibration

M15:

```text
  rule                                       severity    passed   failed      n/a    fires  behaviour
  data_quality.completeness_ratio            REQUIRED     16890       19        0    0.11%  RARELY_FIRES
  data_quality.latest_candle_age_minutes     WARNING      16909        0        0    0.00%  NEVER_FIRES
  data_quality.market_data_complete          REQUIRED     16650      259        0    1.53%  RARELY_FIRES
  data_quality.used_candle_count             BLOCKING     16901        8        0    0.05%  RARELY_FIRES
  event_context.high_impact_event_count      WARNING      16897       12        0    0.07%  RARELY_FIRES
  event_context.minutes_since_latest_event   WARNING         60        8    16841   11.76%  OFTEN_FIRES
  market_context.max_close_drawdown          WARNING      16706      201        2    1.19%  RARELY_FIRES
  market_context.snapshot_ready              REQUIRED     16650      259        0    1.53%  RARELY_FIRES
  market_context.volatility_ratio            WARNING      15970      938        1    5.55%  RARELY_FIRES
  time_filter.session_name_allowed           WARNING       9867     7042        0   41.65%  OFTEN_FIRES
  time_filter.utc_weekday                    WARNING      12201     4708        0   27.84%  OFTEN_FIRES
```

H1:

```text
  data_quality.completeness_ratio            REQUIRED      4209       10        0    0.24%  RARELY_FIRES
  data_quality.latest_candle_age_minutes     WARNING       4219        0        0    0.00%  NEVER_FIRES
  data_quality.market_data_complete          REQUIRED      4141       78        0    1.85%  RARELY_FIRES
  data_quality.used_candle_count             BLOCKING      4211        8        0    0.19%  RARELY_FIRES
  event_context.high_impact_event_count      WARNING       4216        3        0    0.07%  RARELY_FIRES
  event_context.minutes_since_latest_event   WARNING         27        1     4191    3.57%  RARELY_FIRES
  market_context.max_close_drawdown          WARNING       3917      301        1    7.14%  RARELY_FIRES
  market_context.snapshot_ready              REQUIRED      4140       79        0    1.87%  RARELY_FIRES
  market_context.volatility_ratio            WARNING       3977      242        0    5.74%  RARELY_FIRES
  time_filter.session_name_allowed           WARNING       2457     1762        0   41.76%  OFTEN_FIRES
  time_filter.utc_weekday                    WARNING       3043     1176        0   27.87%  OFTEN_FIRES
```

`OFTEN_FIRES` on the two time-filter rules is correct, not a miscalibration. They are structural
filters that describe *when* the window sits, not anomaly detectors: about 2 days in 7 are weekend
(27.8% observed, matching 2/7 = 28.6%) and a little over 40% of hours fall outside London and New
York. The 1–10% target applies to anomaly-style warnings. The provider returns a continuous series
including weekend bars, which is why the weekday rule has anything to report at all.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 105 source files |
| `uv run pytest` | Passed; 527 passed, 7 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

Command used for the recorded runs:

```bash
docker compose run --rm api python -m scripts.replay_rules --days 180 --timeframe M15 \
  --allow-quiet data_quality.latest_candle_age_minutes
```

### The recalibrated rules through the real `/review` path

Rendered with the production formatter over a window that has data (`as_of` 2026-07-29 11:30Z, the
last stored candle close), so the new thresholds can be read in the text the bot would send:

```text
===== /review EURUSD M15 =====
Статус: READ_ONLY. Итог правил: READY_FOR_REVIEW.
Данные: свечей 12 из 12, полнота 100%, возраст 0 мин.
Правила: пройдено 10 из 11.
- события: 1 из 2; не пройдено: event_context.high_impact_event_count
Замеры: волатильность 0.85, просадка 0.10%, сессия london.

===== /review EURUSD H1 =====
Правила: пройдено 10 из 11.
Замеры: волатильность 1.28, просадка 0.14%, сессия london.
```

Both readings sit inside the re-derived bounds (0.85 and 1.28 within 0.30–3.5; 0.10% and 0.14% under
0.4%), and the event rule fails on the Phase 7B stub release stored at 08:58Z that day — which is the
whole path working, not a calibration problem.

A `/review` for the current wall-clock window reports `свечей 0 из 12` and `BLOCKED`, because
ingestion has been off since 2026-07-29 and the recent window is genuinely empty. That is the
data-quality rules doing their job.

## Remaining risks / notes

- **The event rules are still uncalibrated.** Storage holds five economic events in total: three
  `local-seed` MEDIUM entries and two `phase7b-proof` HIGH stubs from the Phase 7B offline proof. No
  real FMP history exists, because Phase 7B ingestion needs an API key the project does not have. The
  numbers above for `event_context.*` describe stub data and must not be read as calibration; both
  thresholds were left untouched for that reason.
- **`MAXIMUM_CLOSE_DRAWDOWN` is a compromise, not a fit.** It compares an absolute price move against
  a fixed bound while the move itself scales with the timeframe: 0.0025 fires on 4.66% of M15 but
  22.38% of H1 windows. 0.004 keeps both inside the target band (1.19% / 7.14%) but is loose for M15
  and tight for H1. Normalising the field by average true range, or scoping thresholds per timeframe,
  would remove the compromise; both are rule-content changes beyond this slice.
- Calibration covers EURUSD only, and one six-month period. Another pair or a differently-behaved
  regime may sit elsewhere; the replay is cheap to re-run when more history exists.
- The replay samples one `as_of` per candle close, so it measures moments when data had just
  arrived. A window requested mid-candle would show a slightly different `latest_candle_age_minutes`
  and nothing else.
