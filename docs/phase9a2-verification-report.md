# Phase 9A-2 Verification Report — Outcome Measurement

Generated: 2026-08-07

## Scope

Phase 9A ended with one sentence repeated three times: **nothing in this project measures what
happened after a window.** Two things were blocked on it — calibrating the 9A level multipliers, and
ever showing that a direction beats a coin toss. This slice adds the measurement, and with it the
baseline any future directional claim has to beat.

`PROJECT_PHASE = "phase_9a2_outcome_measurement_foundation"`

Numbered 9A-2 rather than a new phase, the way 7D split into 7D-1 and 7D-2.

## The exception this slice makes, and the fence around it

Every other part of this project is bound by the Phase 3D invariant: a snapshot exposes only data at
or before its `as_of`, and nothing after it may influence a decision. Outcome measurement is the
deliberate exception — it exists precisely to read the future.

The exception is safe only if the result cannot flow back, so three tests fence it in:

- the analysis path (`analysis_engine`, `feature_engine`, `context_engine`, `snapshot_review`,
  `rule_replay`, `signal_price_plan`, every `strategy_*` module) may not contain the string
  `outcome_measurement` at all;
- no service, route, command, or job may reference it — measurement is an offline instrument, never
  something running on a timer;
- the module imports no persistence, adapter, Telegram, API, or scheduler code.

The forward slice itself lives in `scripts/measure_outcomes.py`, one line with a comment on it, and
it starts one candle *after* the window's own `as_of` candle — so nothing a plan was built from is
ever measured as that plan's own outcome.

## Three honesties built into the result shape

**Ambiguity is a kind, not a coin flip.** When one candle's range spans both the protective level and
the target, OHLC records four prices and not their order. Resolving that silently — in either
direction — is the classic way a backtest flatters its author. `AMBIGUOUS` is counted in its own
right, and `target_first_share` puts it in the denominator so it counts against the plan without
being reported as a loss it was not observed to be.

**Not resolving is a kind too.** `TIMEOUT` windows are never dropped and never counted as losses.

**Outcomes are gross.** The project stores OHLC and no spread, so nothing here can subtract a cost.
The script prints that sentence under every table rather than leaving it to a reader to remember.

Entry is assumed filled at the entry-band midpoint on the first forward candle — a market entry at
the anchor. Waiting for a pullback into the band would be a strategy decision, and this module has no
strategy in it.

## Implementation

- `app/domain/entities/outcome.py` — `OutcomeKind`, `WindowOutcome` (validator: a resolved outcome
  must name its bar, an unresolved one must not), `OutcomeStatistics` (validator: the counts add up;
  shares are `Decimal | None`, never a substituted zero).
- `app/domain/outcome_measurement.py` — `measure_outcome`, `aggregate_outcomes`. Pure domain.
- `app/domain/rule_replay.py` — the window walk was extracted into `iter_replay_windows` and
  `order_candles`, so measurement and rule replay sample **the same moments in the same order**
  rather than two lookalike walks. `replay_windows` now builds on the extracted iterator and behaves
  identically.
- `scripts/measure_outcomes.py` — the CLI, with `--stop-multiplier` and `--target-multiplier`,
  because sweeping them is the entire point.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 111 source files |
| `uv run pytest` | Passed; 646 passed, 7 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

Unit coverage: each outcome kind reached deliberately, the horizon hiding a later resolution, the
walk stopping at the first resolution rather than continuing, SHORT mirroring LONG on a mirrored
series, both entity validators, and shares reported as unavailable rather than zero.

## The baseline

EURUSD, 180 days of stored history, window 12, step 1, horizon 24 candles, levels at the Phase 9A
defaults (stop 1.5 ATR, target 2.0 ATR):

```text
M15  (16,587 windows)   target%   ambiguous%   timeout%   avg bars
  LONG                   38.44%       2.15%     20.74%       7.2
  SHORT                  43.07%       2.11%     20.18%       7.1

H1   (4,203 windows)    target%   ambiguous%   timeout%   avg bars
  LONG                   34.91%       3.62%     18.39%       7.8
  SHORT                  45.76%       3.20%     18.13%       8.0
```

**Ambiguity is small: 2–4%.** This was the number that could have invalidated everything else, and it
does not. The conclusions below are drawn from a sample where the data can adjudicate 96–98% of
resolved windows.

**LONG and SHORT are not complementary, and should not be.** They cannot sum to 100%: a window where
price moves 1.6 ATR against you before travelling 2.1 ATR in either direction is a loss for both
directions. What matters is the *gap* between them — 4.6 п.п. on M15, 10.9 п.п. on H1, SHORT ahead
both times. That is drift in the sample: EURUSD did not spend these six months going nowhere. It is a
finding in its own right, and it sets the rule for 9B: **a direction must beat the baseline for its
own direction, not 50%.** A rule that only ever says SHORT would have looked clever here for reasons
that have nothing to do with the rule.

## The multiplier sweep

EURUSD M15, same window and horizon. "Break-even" is the target share at which the geometry pays for
itself, `stop_eff / (stop_eff + target_eff)`, where each effective distance is measured from the
entry midpoint and so carries the 0.1 ATR half-band.

| stop | target | break-even | LONG target% | SHORT target% | timeout% |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1.0 | 1.0 | 50.0% | 48.54% | 48.14% | 5.9% |
| 1.0 | 2.0 | 34.4% | 29.77% | 32.49% | 14.2% |
| 1.5 | 1.5 | 50.0% | 47.18% | 50.45% | 16.0% |
| **1.5** | **2.0** | **43.2%** | **38.44%** | **43.07%** | **20.7%** |
| 1.5 | 3.0 | 34.0% | 26.05% | 31.59% | 27.9% |
| 2.0 | 2.0 | 50.0% | 45.87% | 51.95% | 25.9% |
| 2.0 | 4.0 | 33.9% | 23.96% | 30.59% | 39.4% |
| 3.0 | 3.0 | 50.0% | 44.70% | 53.42% | 44.0% |

Three things this says.

**The measurement is correct.** At every symmetric setting (`stop == target`) the LONG and SHORT
counts come out as exact mirror images of each other — at 1.0/1.0, 7,574 and 7,511 simply swap sides.
That symmetry had to hold by construction and does, which is the strongest arithmetic check available
without a second implementation.

**No configuration is free money, and the wide ones are the worst.** Every row lands *below* its
break-even, and the shortfall grows with the target-to-stop ratio: −1.5 п.п. at 1:1, −4.8 at 1.5:2,
−10 at 2:4. Without a direction, widening the target does not buy expectancy — it sells it. This is
the expected result, and getting the expected result from a new instrument is what makes the
instrument usable.

**1.5 / 2.0 is not displaced.** Nothing in the sweep is profitable, so nothing here justifies moving
the Phase 9A defaults. What changed is their status: they were untested conventions, and they are now
conventions with a measured baseline attached (38.4% / 43.1% on M15). Calibration proper belongs to
whatever produces a direction, because the best stop distance depends on the entries it protects.

### The horizon is not distorting this

The obvious objection to a 24-candle horizon is that it truncates slow winners more than fast losers,
biasing the sweep against wide targets. Tested directly at 1.5 / 2.0 on M15:

| horizon | timeout% | LONG target% | SHORT target% |
| ---: | ---: | ---: | ---: |
| 24 | 20.7% | 38.44% | 43.07% |
| 48 | 12.9% | 38.64% | 43.52% |
| 96 | 6.6% | 38.17% | 43.73% |

Timeouts fall by two thirds and the target share moves by less than half a point. Unresolved windows
resolve in roughly the same proportion as resolved ones, so the horizon is a reporting choice rather
than a thumb on the scale.

## Remaining risks / notes

- **Every figure is gross of costs.** With no spread data, nothing here can be netted. On M15 the
  spread is a material share of a 2 ATR target, so the real numbers are worse than the table by an
  amount this project cannot currently quantify.
- **One instrument, one period.** Six months of EURUSD. The LONG/SHORT gap is direct evidence that a
  single period carries a direction of its own; a second pair or a different six months could move
  the baseline.
- **Windows overlap.** Step 1 means consecutive windows share eleven of twelve candles and their
  forward paths overlap heavily, so 16,587 measurements are nowhere near 16,587 independent
  observations. The counts are stable, not statistically powerful — no confidence interval should be
  read off them.
- **Entry is assumed filled.** A real order at the band midpoint might not fill on a gap. There is no
  slippage model here and no pretence of one.
- **Nothing is wired, and nothing here reaches a user.** The module is offline machinery, guarded by
  three tests that say so.
- **Direction is still the open question**, and it still blocks 9B — but it is no longer unanswerable.
  Any candidate can now be measured against the numbers above, on the same windows, in the same
  configuration.
