# Phase 9A-8 Verification Report — A Second Instrument

Generated: 2026-08-09

`PROJECT_PHASE = "phase_9a8_second_instrument_foundation"`

The last remediation item from the full project review. Everything this project has ever measured was
measured on EURUSD, so no threshold had ever been asked to mean the same thing somewhere else.

## Why NOKSEK rather than GBPUSD

The roadmap said GBPUSD. It is the wrong choice for this particular question.

GBPUSD correlates with EURUSD at roughly 0.85–0.9, because both are three-quarters a dollar move. A
threshold that transfers from one to the other has been tested against the same market seen twice,
which is weak evidence for exactly the same reason M15 against H1 is weak evidence.

NOKSEK has no dollar on either side, about **1.8× the relative volatility per candle** (0.073% of
price versus 0.040%), and a session profile centred on Oslo and Stockholm rather than London and New
York. It is the harder test, and a threshold that survives it has been shown something.

The risk was that thin data would confound the answer — "the threshold does not transfer" would be
indistinguishable from "the data is poor". So the data was checked before anything was calibrated.

## The data holds up

| check | NOKSEK | EURUSD |
| --- | ---: | ---: |
| weekday candles closing at the previous close | 20 of 959 (2.1%) | 13 of 759 (1.7%) |
| flat candles (high = low) | 0 | 0 |
| windows with fewer than 12 candles | none below 11 | some down to 1 |
| `market_data_complete` failures | 1.12% / 1.26% | 1.03% |

Not stale, not thin, and in fact **cleaner than our EURUSD history**, which still carries the gaps
from worker outages. The Wednesday London sample shows ordinary trading: distinct ranges, ten pips of
travel inside a fifteen-minute candle.

One observation that matters beyond this slice: **NOKSEK's weekend filler is not visibly flat.** Its
average weekend range (0.000766) is slightly *larger* than its weekday range (0.000726), where
EURUSD's weekend rows were long runs of byte-identical highs and lows. The signature that made the
contamination obvious on one instrument would not have appeared on the other. Phase 9A-4 chose a
calendar-based rule over a heuristic on the values; this is the first evidence that the choice was
the right one and not merely the tidy one.

The backfill also earned its truncation guard: one M15 chunk failed on the first attempt and the run
reported that it had **not** completed cleanly. A re-run inserted the missing 999 candles and closed
cleanly. Exactly the designed behaviour, exercised for real rather than in a test.

## `max_close_excursion_atr` transfers untouched

| | M15 | H1 |
| --- | ---: | ---: |
| EURUSD | 3.43% | 2.56% |
| **NOKSEK** | **2.86%** | **2.19%** |

The bound of 5.0 was calibrated entirely on EURUSD and **was not changed**. Across instruments the
spread is 0.57 points on M15 and 0.37 on H1; across all four series the whole range is 2.19% to 3.43%.

This is the strongest evidence the project has that normalising by the window's own average true
range makes a threshold portable. M15 against H1 is one market observed at two resolutions; EURUSD
against NOKSEK is two markets with nearly double the volatility between them, and the rule fires at
the same rate on both.

## `volatility_ratio` fails again, for a second reason

The band set yesterday at 0.35/2.3 fires on **10.88%** of NOKSEK H1 windows — outside the 1–10%
corridor. Phase 9A-6 found this field was only partly timeframe-neutral; it is not
instrument-neutral either.

A sweep over all four series at once:

| band | EURUSD M15 | EURUSD H1 | NOKSEK M15 | NOKSEK H1 |
| --- | ---: | ---: | ---: | ---: |
| 0.35 – 2.3 (previous) | 3.32% | 7.69% | 7.19% | **10.88%** |
| **0.30 – 2.5 (taken)** | **1.91%** | **4.66%** | **4.77%** | **6.79%** |
| 0.28 – 2.8 | 1.32% | 2.82% | 3.33% | 5.03% |
| 0.25 – 3.0 | 1.02% | 2.06% | 2.55% | 3.34% |

0.30/2.5 keeps all four inside the corridor with the most room at the **floor**, which is the
constraint that bit last time: the pre-2026-08-08 band had quietly fallen to 0.99% on clean EURUSD
M15. Wider bands drift toward that floor again.

The convergence criterion still cannot be met — a 4.88-point spread across the four series that no
band removes. That is now **two independent confirmations of the same weakness**, from a timeframe
change and an instrument change, and it is recorded rather than resolved by dropping the criterion.

Verified after the edit: 1.91%, 4.66%, 4.77%, 6.79%, matching the sweep exactly.

There is a small irony worth keeping. The lower bound is 0.30, which is what Phase 7D-2 chose; the
upper is 2.5, which is what 7D-2 replaced. The band has arrived back at a mixture of both — by a
completely different route, over clean data and two instruments, with evidence the original had not.

## Two fields that behave identically on both

`move_efficiency`: median 0.260 and 0.279 on EURUSD, 0.248 and 0.252 on NOKSEK. Bounded by
construction and stable across instrument and timeframe, as it should be.

`session_name_allowed`: 40.27% / 40.40% on EURUSD, 40.33% / 40.23% on NOKSEK. Four figures within
0.17 of each other, because the rule reads the clock and nothing else. That is not a calibration
success — it is confirmation that the rule measures the time of day rather than the market, and that
its severity, not its threshold, is the open question.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 115 source files |
| `uv run pytest` | Passed; 698 passed, 9 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

Stored: 180 days of NOKSEK on M15 and H1, roughly 16,000 and 4,300 candles, all from `twelve_data`.
The worker does not ingest NOKSEK — it is historical only, which is all this test needed.

## What this does and does not settle

- **It settles that the ATR-normalised excursion bound is portable.** One number, two instruments,
  two timeframes, four firing rates inside a 1.24-point range.
- **It settles that `volatility_ratio` is not**, and gives the second independent reason.
- **It does not provide a fresh out-of-sample test for a direction.** NOKSEK is genuinely unseen
  data, so it *could* serve as one — but the 9A-3 candidate is disproved and there is nothing
  currently waiting to be tested against it. Spending it now would waste it.
- **Costs are still unmeasured**, and on a minor cross they are worse than on EURUSD. Nothing here
  changes the standing caveat that every outcome figure in this project is gross.
