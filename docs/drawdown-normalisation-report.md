# Drawdown Normalisation Report

Generated: 2026-08-05

## Scope

A maintenance slice, not a phase: it closes the one debt Phase 7D-2 recorded against itself. The
drawdown rule compared an absolute price move against a fixed bound while the move itself scales
with the timeframe, so a single threshold could not serve both M15 and H1. This replaces the field
with one that is normalised by the window's own average true range.

Project phase is unchanged (`phase_8c_explanation_delivery_foundation`); no phase boundary moved.

## The defect, restated

`(peak - close) / peak` is a fraction of price. It survives a change of price level — USDJPY at 150
and EURUSD at 1.10 both yield comparable fractions — but it does **not** survive a change of
timeframe. A 12-candle window spans 3 hours on M15 and 12 hours on H1, and price covers more ground
in 12 hours. The same bound therefore means "rare" on one timeframe and "ordinary" on the other:

| Bound | Fires on M15 | Fires on H1 |
| --- | --- | --- |
| 0.01 (pre-7D-2) | 0.26% | 0.14% |
| 0.004 (7D-2 compromise) | 1.19% | 7.14% |
| 0.0025 | 4.66% | 22.38% |

## The fix

New resolver `market_context.max_close_drawdown_atr` in `app/domain/strategy_field_resolver.py`:

```text
drawdown / (average_true_range / latest_close)
```

The division by `latest_close` is the part that is easy to get wrong. The drawdown is a *fraction*
and the ATR is an *absolute price amount*; dividing one by the other directly would be
dimensionally meaningless. Expressing the ATR as a fraction of price first makes the result a plain
count: **how many ordinary candle ranges deep was this decline.**

Unavailable rather than substituted when the context or feature snapshot is missing, when the ATR is
absent or zero, or when the latest close is absent or zero — a flat window has no scale to normalise
by, and a fabricated number would read as an observation.

## Calibration

Six months of stored EURUSD, replayed through `scripts/replay_rules.py`: 16 508 M15 and 4 153 H1
observations.

| Percentile | M15 | H1 |
| --- | --- | --- |
| p05 | 0.3428 | 0.3438 |
| p25 | 0.9222 | 0.8616 |
| p50 | 1.5616 | 1.5472 |
| p75 | 2.4839 | 2.3844 |
| p95 | 4.1100 | 4.0061 |
| p99 | 5.7283 | 5.3160 |

The distributions are nearly identical across timeframes, which is the whole claim of the change.

Candidate bounds:

| Bound | Fires on M15 | Fires on H1 | Spread |
| --- | --- | --- | --- |
| 3.0 | 15.57% | 14.06% | 1.51 п.п. |
| 3.5 | 9.15% | 8.38% | 0.77 п.п. |
| **4.0** | **5.65%** | **5.03%** | **0.62 п.п.** |
| 4.5 | 3.43% | 2.38% | 1.05 п.п. |
| 5.0 | 2.01% | 1.47% | 0.54 п.п. |

`MAXIMUM_CLOSE_DRAWDOWN_ATR = 4.0`, which sits at about the 95th percentile on both timeframes and
lands in the middle of the intended 1–10% band rather than at its edge.

## Acceptance

The criterion was fixed before the run: firing rates on M15 and H1 converge the way
`volatility_ratio` already does — within roughly one percentage point.

| Rule | Normalised | M15 | H1 | Spread |
| --- | --- | --- | --- | --- |
| `market_context.volatility_ratio` | yes | 5.75% | 5.78% | 0.03 п.п. |
| `market_context.max_close_drawdown_atr` | yes | **5.65%** | **5.03%** | **0.62 п.п.** |
| `market_context.max_close_drawdown` (before) | no | 1.19% | 7.14% | 5.95 п.п. |

Met: 0.62 against a budget of about 1.00, and a ten-fold improvement on the previous spread.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 108 source files |
| `uv run pytest` | Passed; 604 passed, 7 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

Four new resolver tests: the explicit formula including the price conversion; invariance when the
whole movement is scaled three-fold (the raw reading triples, the normalised one does not move); and
two unavailability cases (flat window, absent context).

Live `/review EURUSD M15` now shows both readings, so the absolute figure a person recognises stays
visible next to the one the rule uses:

```text
Замеры: волатильность 0.85, просадка 0.10% (3.04 ATR), сессия london.
```

## Remaining risks / notes

- The old field `market_context.max_close_drawdown` is still resolved and still displayed. It is no
  longer used by any rule. Keeping it costs nothing and a percentage is easier for a person to read
  than a count of candle ranges.
- Calibration is EURUSD-only and covers one six-month period, the same limitation the 7D-2 report
  records. The normalised field is expected to travel better across instruments than the absolute
  one did, but that is a prediction, not a measurement — it will be tested the first time a second
  pair is ingested.
- Normalisation has a known blind spot, worth remembering rather than fixing: when the denominator
  is itself extreme, a genuine outlier stops standing out. In a violent regime the "ordinary" candle
  range is already large, so a deep decline divided by it looks unremarkable.
