# Phase 9A-6 Verification Report — Recalibration on Traded Candles

Generated: 2026-08-08

`PROJECT_PHASE = "phase_9a6_clean_calibration_foundation"`

The third remediation item. Phases 9A-4 and 9A-5 stopped the pipeline trusting data the market never
produced and data we produced ourselves; this one re-derives the numbers that had been calibrated
over both.

## A gap in 9A-4, closed first

`data_quality.market_open` judged the window's `as_of` and nothing else. That left the obvious case
open: a Monday-morning window reaches back into Sunday, so on H1 a twelve-candle window ending at
noon on Monday is built mostly from filler while its `as_of` sits in a live market. One contaminated
candle is enough to distort the average true range that every other measurement is normalised by.

The rule now judges **every candle the window is built from**, and `as_of` no longer gets a vote of
its own — a Friday 23:45 candle closes at Saturday 00:00, and judging that moment was rejecting 25
windows over six months that were built entirely from traded candles. What a window is made of is the
question; when it happens to end is not. With no candles at all, the moment is the only thing left to
judge, and it is used.

`--exclude-closed-market` was added to `scripts/replay_rules.py` and `scripts/measure_outcomes.py`,
skipping windows that touch a shut market. Skipping is for calibration only: production still sees
those windows and fails them, which is a report rather than a silence.

## What the clean distributions look like

Six months of EURUSD, windows built only from traded candles: **11,974 on M15 and 2,802 on H1**,
against 17,082 and 4,276 before filtering.

| | p01 | p03 | p05 | p95 | p97 | p99 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `volatility_ratio` M15 | 0.3354 | 0.4103 | 0.4538 | 1.9010 | 2.1220 | 2.7222 |
| `volatility_ratio` H1 | 0.2604 | 0.3224 | 0.3563 | 2.0417 | 2.2779 | 2.8921 |

## `max_close_drawdown_atr` — unchanged, and it earned that

| | p95 | fires at 4.0 |
| --- | ---: | ---: |
| M15 | 4.1403 | **5.98%** |
| H1 | 4.1149 | **5.96%** |

A **0.02 percentage-point** spread between timeframes, against 0.62 on the contaminated sample and
5.95 before the field was normalised at all. The threshold stays at 4.0 because the evidence got
stronger, not weaker. This is the closest thing the project has to proof that normalising a threshold
works.

## `volatility_ratio` — recalibrated, and the convergence was an illusion

The band moves from **0.30 / 3.5** to **0.35 / 2.3**.

The old band fires on 0.99% of clean M15 windows — below the 1–10% corridor fixed for warning rules
in 7D-2 — because the weekend filler had been supplying both tails of the distribution it was drawn
around. Remove the filler and the tails shrink, so a band drawn to catch them catches almost nothing.

A sweep over nine candidate bands, one walk, clean windows:

| band | M15 fires | H1 fires | spread |
| --- | ---: | ---: | ---: |
| 0.30 – 3.5 (old) | 0.99% | 2.86% | 1.87 |
| **0.35 – 2.3 (new)** | **3.29%** | **7.53%** | **4.25** |
| 0.40 – 2.5 | 3.86% | 9.81% | 5.96 |
| 0.45 – 2.2 | 7.45% | 14.95% | 7.50 |
| 0.50 – 2.0 | 11.51% | 20.84% | 9.33 |

**No band satisfies both acceptance criteria, and that is the finding.** The 1–10% corridor and the
one-percentage-point convergence criterion cannot both be met: the spread grows monotonically with
how much the band fires. 7D-2 reported 5.55% and 5.74% and concluded a single band was defensible —
that agreement was an artefact of contamination, and clean data does not reproduce it.

The band chosen fires 3.29% and 7.53%, inside the corridor on both timeframes, and the report says
plainly that the 4.25-point spread is real.

A plausible mechanism, offered as such: twelve M15 candles are three hours inside one liquidity
regime, while twelve H1 candles are half a day spanning Asia, London and New York. The window average
is taken over genuinely different regimes on H1, so the last candle's ratio is more dispersed. Unlike
`max_close_drawdown_atr`, this field is only partly timeframe-neutral, and now says so.

## The Phase 9A-2 baseline, re-measured

This supersedes the baseline in `docs/phase9a2-verification-report.md`.

| | windows | LONG target% | SHORT target% | ambiguous% | timeout% |
| --- | ---: | ---: | ---: | ---: | ---: |
| M15 contaminated | 16,587 | 38.44% | 43.07% | 2.15% | 20.74% |
| **M15 clean** | 11,974 | **38.88%** | **44.90%** | **0.63%** | 13.60% |
| H1 contaminated | 4,203 | 34.91% | 45.76% | 3.62% | 18.13% |
| **H1 clean** | 2,802 | **39.30%** | **45.59%** | **0.54%** | 13.78% |

Three things improved at once, and all three point the same way.

**Ambiguity fell by three quarters**, from 2–4% to 0.5–0.6%. The unadjudicable cases were mostly the
reopen candle, whose range spans everything. On clean data the measurement can decide 99.4% of
resolved windows, which is the single biggest gain in trustworthiness here.

**Timeouts fell from ~20% to ~14%.** Flat carried-forward prices reach no level, so weekend windows
were timing out by construction.

**The two timeframes converged.** Contaminated, LONG differed by 3.5 points between M15 and H1 and
SHORT by 2.7. Clean, the gaps are 0.4 and 0.7. A baseline that agrees across timeframes is measuring
the sample; one that does not is measuring the filler.

**The sample's drift is about 6 points in favour of SHORT, consistently on both timeframes** — 6.02
on M15 and 6.29 on H1, against 4.6 and 10.9 before. That is the number any future directional
candidate has to beat on its own windows, and it is now the same number whichever timeframe is used
to state it.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 115 source files |
| `uv run pytest` | Passed; 688 passed, 9 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

Firing rates after the edit match the sweep exactly: 3.29% and 7.53% for the volatility band, 5.98%
and 5.96% for the drawdown bound. `data_quality.market_open` reports `NEVER_FIRES` on a filtered walk,
which is correct by construction and needs `--allow-quiet` on such runs.

## Remaining

- **The event rules remain dead** and the calendar remains empty; nothing here changes that.
- **`time_filter.session_name_allowed` fires on 40.3% of clean windows** on both timeframes. The two
  agree closely, which suggests the field is sound and the *severity* is wrong: a rule that describes
  four hours in ten is not reporting an anomaly. Whether a session filter belongs as a warning at all
  is a question for evidence, not for adjusting the threshold until it feels quieter.
- **The 9A-3 retraction stands.** Nothing in this recalibration revisits it, and the held-out sample
  is still spent.
