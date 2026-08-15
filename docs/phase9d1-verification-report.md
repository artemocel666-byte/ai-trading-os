# Phase 9D-1 Verification Report — Daily Bars and a Currency Universe

Generated: 2026-08-15

`PROJECT_PHASE = "phase_9d1_daily_bars_and_universe"`

Five phases of measurement returned nothing, and the decisions taken on 2026-08-14 change the
question rather than the method: **currencies** (not stocks), **compared across instruments** (not
one series through time), over a horizon of **months** (not hours). The bar of evidence stays and
the project stays descriptive.

This slice builds the instrument. **It measures nothing.** That is 9D-2.

## Why the horizon is the substantive part

9C-4 established that at a six-hour horizon a round-trip cost of 0.15 ATR consumes the entire
five-point bar. Cost is fixed per round trip; the move is not. Measured against the live provider on
EURUSD: median **daily** range 55 pips, median move over 21 trading days 103 pips, against the M15
median ATR of 4.9 pips.

| | what a plan reaches for | a 1-pip round trip is |
| --- | ---: | ---: |
| M15, 6-hour horizon | ~10 pips | **~10% of it** |
| daily bars, 1-month horizon | ~103 pips | **~1% of it** |

The spread does not change; what it is measured against grows tenfold. This is the one lever the
project has measured to matter.

## Nothing was replaced

`M15` and `H1` keep their data, their pipeline, their `/review` surface and their forward ledger.
`D1` is additional rows under a different timeframe — no migration, no rewrite. The failed intraday
measurements are **not** re-run on daily bars.

M15 behaviour was verified unchanged: `profile_execution_cost.py` on EURUSD M15 returns a pooled
41.66% at zero cost against a published 41.65%, ATR interquartile spread 0.315 against 0.316. The
difference is 60 windows of fresh candles. The real proof is 834 tests, including every pre-existing
M15 assertion, passing unaltered.

## The weekend rule was measured, and the measurement refuted both guesses

The provider *does* send weekend daily bars — erratically, and **differently per instrument**. Over
the same 142 weeks EURUSD had 58 Saturdays and 31 Sundays; USDJPY had 84 and 31. Expecting them
would report a gap in most weeks and a *different* gap per instrument, which is the one thing a
cross-sectional comparison cannot tolerate.

So `D1` expects weekdays only (`TRADED_DAYS_ONLY_TIMEFRAMES`) while `M15`/`H1` keep expecting every
slot, because their weekend filler is at least *present*. A weekend daily that does arrive is stored
and simply surplus.

Alignment became a separate question from expectation: it now asks whether the span is a whole
number of bars, not whether every slot produced one. The old check inferred one from the other, an
identity that breaks the moment a window skips a day.

## The result

| | |
| --- | ---: |
| Pairs in the universe (10 currencies) | 45 |
| Quoted by the provider | **44** (only `NZDSEK` refused) |
| Filled cleanly | **44 of 44** |
| Failed chunks in the final run | **0** |
| Daily bars stored | **224,587** |
| Years of history, every pair | **20** (2007–2026) |
| Bars per pair | 5,055–5,135, median 5,106 |
| Rows skipped as impossible | 905 (0.4%) |

Read from the database rather than from the run: **all 44 pairs are present in every year from 2007
to 2026**, with per-year counts between 226 and 313. The widest within-year spread is 2020
(236–262), where the skipped rows concentrate — consistent with that year's volatility.

## Four defects, one disease: a concept written in two places

The slice took three attempts to fill, and the reasons are worth recording because they are the same
reason.

| where | the two copies |
| --- | --- |
| Docker image | the container's sources against the working tree |
| `TIMEFRAME_TO_DELTA` | the domain map against a private copy in the adapter |
| request-range limit | the service's chunk size against the adapter's own guard |
| `_expected_open_times` | `feature_engine.py` against `entities/data_quality.py` |

The third was the dangerous one: overriding only the service made it ask for thousand-day chunks
that the adapter rejected before any network call, and the run reported **"the provider does not
quote these 45 pairs"** — a wrong answer wearing the shape of a real one. The CLI override now lands
in the settings, read once by both.

The fourth had existed since Phase 3 and would have split silently on the first change that needed
the two copies to differ. That change was this one.

## The defect that actually caused the holes

Not rate limiting, and not the provider's history. A "failed" chunk's response was **200, valid
JSON, 714 rows** — and our parser refused all of them because some were impossible.

The rows in question are days whose close sits outside the bar's own high-low range: EURGBP on
2021-01-01 closed at 0.88749999 against a low of 0.88779998 — three pips below its own minimum,
against a daily range of 56. Not a rounding artefact, which is what this was first mistaken for.
`Candle` is right to refuse such a row; a close outside its own day's range is not a price.

**The disproportion was the bug: one impossible row destroyed 714 good ones**, two or three chunks
per pair, which is where the multi-year holes came from.

The row is now **skipped and counted, never repaired**. Widening the low to admit the close would be
editing an observation, which is the one thing this project does not do. Each skip is logged with
its pair, date and reason — the exception's *type name*, not its message, because a provider message
can quote a request URL and a request URL carries the API key.

### Data quality differs between pairs by a factor of four

Measured over the same 1000-day window: **1.3%** of EURGBP days are impossible against **5.5%** of
EURSEK days. That is worth knowing before a cross-section is built on these series.

The ceiling above which a whole response is still refused was first set at 5% — which landed between
those two numbers and kept failing EURSEK. It is now **25%**, and deliberately not "just above the
worst sample": setting it there would be fitting a threshold to the data it must judge, the habit
five phases were spent avoiding. A quarter of a response being impossible is a feed to refuse; five
percent is a series to note.

### Why the failure reason had to be recorded first

The service caught every exception and stored `failed=True` and nothing else, so the cause had to be
guessed from the shape of the gaps — and the first two guesses were wrong. With the reason recorded,
the final runs showed **two distinct causes**: `ProviderInvalidPayloadError` for the malformed rows,
and one genuine `ProviderRateLimitError` on EURJPY — provoked by diagnostic requests being made
concurrently with the fill. Without the reason, those two would have been one mystery, and fixing
either alone would have looked like a failure of the fix.

## The check that was missing

A fill can report success per pair and still leave a universe whose members cover different spans.
`coverage_shortfalls` now reports the sample's median bar count and every pair more than 10% below
it, and the run prints it. Deliberately relative: the right absolute count depends on an
instrument's real history, which the script cannot know. It is a comparability test, not a
completeness one.

The final run's verdict: *median 5106 bars per pair, range 5053..5135 — every pair is within 10% of
the median, the universe is comparable.*

## Retro-check on the existing intraday history

The same parser bug could have holed the M15 and H1 history that five phases of measurement rest on.
It did not: stored M15 runs 2,880–2,973 bars per month against a 24/7 expectation of 96 per day,
continuous across every month. One EURUSD gap of about two days in July 2026 is live-ingestion
downtime, not a chunk failure.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 124 source files |
| `uv run pytest` | Passed; 834 passed, 9 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |
| EURUSD M15 unchanged | 41.66% against a published 41.65% |
| every pair, every year | 44 of 44, 2007–2026 |

Twenty-one new tests. The ones that carry the design: a daily window spanning a weekend is complete
rather than gapped, asserted beside an intraday window that still expects every slot so the two
cannot drift; alignment holds for a window that skips a day; **a timeframe cannot be half-added**,
which is the defect that happened here; one impossible row does not destroy a response and is not
repaired; a mostly-impossible response is still refused; and coverage is judged against the sample
rather than an absolute.

## Pre-registered for 9D-2, before any data was seen

- **Formation 3 months, holding 1 month.** Fixed once; a different horizon would be a separate test
  with its own record, not an adjustment to this one.
- **Terciles, not deciles.** 44 pairs drawn from 10 currencies are roughly nine independent
  dimensions, not forty-four; buckets built from them are correlated.
- **The honest limit.** Twenty years is about 240 monthly periods. Detectable at two standard errors
  is an annualised Sharpe near 0.45 — enough to see a strong effect and **not** enough to confirm a
  faint one. A null there will mean *we could not see it*, not *it is not there*. Every previous
  phase could say the stronger thing.
- **A holdout exists for the first time.** Nineteen years allows reserving the last several and not
  looking until the end. NOKSEK was previously the only unseen data, and it was one instrument.

## The decision 9D-2 depends on, recorded but not implemented

**A ranking is a direction.** Today no module may return a `SignalDirection` outside the unwired
candidate, and every measurement pools both directions so no directional claim can be read out. That
rule exists because the project had no measured basis for a direction. A cross-sectional ranking is
structurally one.

Proposed redraw, preserving what the rule protected: a ranking **may exist in the measurement layer**,
**may never be delivered** to a user, and `REAL_TRADING_ENABLED` stays permanently `False`. The
safety test moves from *"no direction exists"* to *"no direction is delivered"*.

## Known and left for 9D-2

For `D1`, a stored weekend bar must be **excluded from** a window rather than disqualify it.
`--exclude-closed-market` currently drops any window containing a non-traded candle, which on a long
daily window would drop nearly all of them. Different semantics from the intraday filter, and
cheaper to notice now than mid-measurement.
