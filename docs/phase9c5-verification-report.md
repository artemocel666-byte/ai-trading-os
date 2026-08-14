# Phase 9C-5 Verification Report — Is Twelve Candles Too Short a View?

Generated: 2026-08-14

`PROJECT_PHASE = "phase_9c5_window_width_measurement"`

Three phases returned nulls and they shared one input: summary statistics of a **twelve-candle
window**. `DEFAULT_WINDOW_CANDLES = 12` was set in Phase 3 to match the Telegram snapshot
([rule_replay.py:28](app/domain/rule_replay.py:28)) and had never been questioned. On M15 that is
three hours of context being asked about the next six.

This slice changes exactly one thing: the window becomes **one calendar day** — 96 candles on M15,
24 on H1. Chosen as a span of time rather than a multiple of the old count, so that for the first
time the two timeframes see the same stretch of market. The horizon does not move; this changes
what we predict *from*, never what we predict.

Almost no code was needed. `--window-candles` was already an argument on every replay script, and
`iter_replay_windows` selects the window by time rather than by count, so the machinery took the
wider window untouched.

## The plumbing check, read before any field

A wide-window ATR estimates the same quantity as a narrow-window one, but far more steadily. If the
dispersion does not fall, the window is not really wider and nothing below can be read.

| series | median ATR (12) | median ATR (1 day) | IQR/median (12) | IQR/median (1 day) | windows (12 → 1 day) |
| --- | ---: | ---: | ---: | ---: | ---: |
| EURUSD M15 | 0.000484 | 0.000506 | 0.608 | **0.316** | 11,914 → 9,738 |
| EURUSD H1 | 0.001049 | 0.001053 | 0.509 | **0.375** | 2,792 → 2,481 |
| NOKSEK M15 | 0.000698 | 0.000713 | 0.670 | **0.298** | 11,712 → 9,614 |
| NOKSEK H1 | 0.001467 | 0.001454 | 0.425 | **0.342** | 2,721 → 2,422 |

The median is unchanged to within a percent on every series — same underlying quantity, as expected.
The dispersion halves on M15 (an eight-fold widening) and falls by about a quarter on H1 (a
two-fold widening), which is the √n pattern a mean should follow. **The window is genuinely wider.**

Sample retention under `--exclude-closed-market` is 82% on M15 and 89% on H1, better than the ~55%
the plan estimated, because a window is skipped only when it *contains* a carried-forward candle.

Base rates barely moved and all four remain below break-even: 41.65%, 42.48%, 40.87%, 41.76%
against 42.86%. The 9C-4 cost slope was re-derived at the new window rather than carried over and
came back at 28–33 points of target share per ATR of cost, against 30–37 at twelve candles. So five
points is still worth about 0.15 ATR, and the tradable bar per series is 6.2, 5.4, 7.0 and 6.1
points above the base rate.

## The pre-registered result: null on all four fields

`target_first_edge` in percentage points, gradient / band:

| field | EURUSD M15 | EURUSD H1 | NOKSEK M15 | NOKSEK H1 |
| --- | ---: | ---: | ---: | ---: |
| `volatility_ratio` | +1.26 / +0.54 | +0.36 / −0.80 | +2.19 / −0.28 | +1.93 / +0.09 |
| `max_close_excursion_atr` | +2.30 / −0.90 | **−5.67** / +2.09 | +1.40 / +0.59 | +0.73 / −1.17 |
| `max_close_drawdown_atr` | +0.96 / −1.27 | **−7.55** / +0.36 | +1.42 / +0.92 | +2.51 / +0.67 |
| `move_efficiency` | +2.14 / +0.08 | −0.82 / −0.97 | +0.82 / +0.13 | −1.51 / −0.74 |

No field clears the bar, which required **≥5 points with the same sign on all four series**.

**A wider view does not carry what a narrower one lacked.** Twenty-four hours of context orders the
next six no better than three hours did.

## The two largest readings this programme has ever produced, and why they are not a finding

−5.67 and −7.55 both clear five points in magnitude. Both are on **EURUSD H1**, both on
**excursion measures of the same window** — `max_close_excursion_atr` and `max_close_drawdown_atr`
are not independent readings — and both are the only negative on their row, with the other three
series positive.

EURUSD H1 at a 24-candle window is also the thinnest cell in the study: 2,481 windows, 248 per
decile, about 438 resolved outcomes per decile once both directions are pooled. The standard error
on a decile's share is then ≈2.36 points, and on a *gradient* — a difference of two deciles —
≈3.34 points. So −7.55 is 2.3 standard errors and −5.67 is 1.7. Across sixteen gradient readings,
one excursion of that size is roughly what chance produces.

**This is exactly the shape 9A-3 had**, and the same-sign-on-four-series criterion is what stops it
becoming a headline. Fixing that criterion in advance is worth more here than in any previous phase,
because this is the first phase where the pre-registered criteria had something large to reject.

Honesty about a pattern that is nonetheless there: EURUSD H1 has shown negative excursion gradients
at **both** window widths (−1.45 and −3.01 at twelve candles, −5.67 and −7.55 at twenty-four), and
they grew with the window. It is one series out of four. **It will not be followed up**, per the
clause fixed before the run — chasing an effect that appears on one of four series is the failure
this project has already paid for once.

## The one consistent sign, and why it changes nothing

`volatility_ratio`'s gradient is now the same sign on all four series for the first time: +1.26,
+0.36, +2.19, +1.93. At twelve candles it was +1.68, +1.03, +1.01, **−0.36**. Widening the window
made it consistent without making it larger — the mean is about 1.4 points, against a 5-point
detection bar and a ~6.2-point tradable bar.

It is worth stating what confirming 1.4 points would take. At that effect size the standard error
would need to be near 0.5 points, which needs roughly 195,000 windows per series. The forward
ledger — the only unseen data this project has — writes about 50 rows a day. **Even if it is real,
it cannot be confirmed here inside a decade, and 9C-4 already showed it would not pay if it were:
1.4 points is under a quarter of the cost of a single spread.**

## Replication of a published observation

Not a new test, and not part of the pre-registration: 9C-3 reported that `volatility_ratio`
predicts whether a window resolves at all. It survives the wider window unchanged in character.

| series | decile 1 timeout | decile 10 timeout | decile 1 target | decile 10 target |
| --- | ---: | ---: | ---: | ---: |
| EURUSD M15 | 21.63% | 3.95% | 40.52% | 41.79% |
| EURUSD H1 | 14.52% | 5.42% | 42.92% | 43.28% |
| NOKSEK M15 | 19.82% | 6.55% | 39.91% | 42.10% |
| NOKSEK H1 | 14.67% | 5.35% | 40.68% | 42.61% |

Motion, still not direction. The timeout spread stays large and portable; target share in those same
deciles stays within 2.2 points, on the wrong side of a 42.86% break-even. Two configurations, eight
series-measurements, same answer.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 123 source files |
| `uv run pytest` | Passed; 808 passed, 9 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |
| sweep and field runs agree | pooled 41.65 / 42.48 / 40.87 / 41.76 in both, exactly |

That last row is the check that matters for a measurement-only slice: the cost sweep and the field
profiler are separate code paths over the same windows, and they report identical pooled figures on
all four series. The sixteen readings therefore rest on one sample, not on a drifting one.

The only code change is the ATR dispersion check itself. `_nearest_rank` in `rule_calibration.py`
became public as `nearest_rank`, which it had briefly been in 9C-3 before being reverted the same
day when that slice's design changed. It is public now for the reason it was not then: a second
caller genuinely needs it. One definition of a percentile in this project, or none.

## What this settles

- **A wider window carries nothing the narrow one lacked.** Four fields, four series, two
  configurations, and the answer does not move.
- **The pre-committed clause now fires: no other window width will be tried.** Not 48, not 192. The
  protection against sweeping a structural parameter is a commitment made before the numbers
  existed, and it is being honoured with two five-point readings on the table.
- **The question is no longer how to slice this data.** It is what data to add. Everything measured
  in 9C-2, 9C-3, 9C-4 and 9C-5 has been a function of OHLC over one instrument's recent past, and
  four independent attempts to find structure in it have returned nothing that clears a bar set at
  a sixth of a spread.
- **The measurement harness is what these phases actually produced.** Four pre-registered
  hypotheses, four honest nulls, two self-corrections, and no false claim published. That is not a
  consolation prize; it is the only part of this project with a demonstrated track record.

## What it means for the product

Unchanged, and now for a fifth reason: there is still nothing to tell a person about what follows a
window like theirs. The single honest sentence that survives is the timeout observation, and it
tells a reader how likely their window is to *do* something, never what.

The live question is the one 9C-4 left and this phase sharpens: **add information, or stop
predicting.** Adding information means a source that is not this instrument's own recent prices —
the economic calendar remains blocked behind a paid FMP plan, verified 2026-08-01. Stopping means
accepting that the deliverable is the bench rather than the forecast.

Neither is a coding decision, and neither should be taken by an agent.
