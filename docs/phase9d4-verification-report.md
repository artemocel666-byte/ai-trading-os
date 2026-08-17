# Phase 9D-4 Verification Report — Carry, and the First Null That Explains Itself

Generated: 2026-08-17

`PROJECT_PHASE = "phase_9d4_carry_measurement"`

Six pre-registered measurements returned nothing, and every one read past prices of the instrument
itself. This is the seventh, and the first that reads something else: the interest rate differential
between two currencies, stored in Phase 9D-3.

**It also returns nothing — and it is the first one that says why.** The previous six ended at "no
signal here". This one ends with a mechanism, a number for how much of it operates, and a tail
reading that would have disqualified the result even if the statistic had passed.

Every choice below was fixed in the Phase 9D-3 plan, **before a single rate was looked at**.

## Plumbing, read before the result

| | |
| --- | ---: |
| Pairs with daily history | **44 of 45** |
| Currencies with stored rates | **10 of 10** |
| Anchors examined | 229 |
| Excluded for an incomplete rate cross-section | **5** |
| **Rebalance dates measured** | **224** |
| **Instruments on every date** | **44 — min, median and max alike** |
| Instrument-dates dropped for a missing price | **0** |

The width is the line that matters: min, median and max are all 44, so every one of the 224
cross-sections ranked the entire universe. Not one date was measured on a thinned field.

The five exclusions are named rather than counted: **2020-06** — the USD gap at April 2020 that
Phase 9D-3 found and predicted this phase would lose — and **2026-04 through 2026-07**, where the
EUR and GBP series end in January 2026 and the two-month lag runs off the end of the data. Nothing
was filled.

Phase 9D-3 predicted 221 usable anchors in the window 2007-10 .. 2026-03. Over its slightly wider
price history this run kept 224, of which exactly 221 fall in that window. **The two phases agree
with each other about what is missing**, which is the point of having counted it there.

## The result

Ranked by carry differential into terciles, rebalanced monthly, held one month. Top minus bottom.

| cost per leg | periods | mean / month | s.e. | t |
| --- | ---: | ---: | ---: | ---: |
| 0 bp | 224 | **+0.110%** | 0.207% | **+0.53** |
| 1 bp | 224 | +0.090% | 0.207% | +0.44 |
| **2 bp** *(criterion)* | 224 | **+0.070%** | 0.207% | **+0.34** |
| 5 bp | 224 | +0.010% | 0.207% | +0.05 |
| 10 bp | 224 | −0.090% | 0.207% | −0.43 |

| criterion | |
| --- | --- |
| mean spread positive | **True** |
| **t ≥ 2.0** | **False** — +0.34 |
| same sign in both halves | **True** (+0.039%, +0.102%) |
| survives 2 bp per leg | **True** |

**VERDICT: does not clear.**

Three of four criteria passed, which no previous phase managed. It changes nothing — the criteria
were pre-registered as *all four required*, precisely so that a near miss could not be talked into a
result after the fact.

## The decomposition, which is the actual content of this phase

Measured over **identical buckets** — same ranking, same instruments, the return split in two:

| component | mean / month | t | summed over 224 months |
| --- | ---: | ---: | ---: |
| **carry** (accrual) | +0.318% | **+42.76** | **+71.2%** |
| **spot** (price move) | −0.207% | −1.00 | **−46.5%** |
| **total** | +0.110% | +0.53 | **+24.7%** |

> **The carry line's t of 42.76 is a tautology, not a finding.** It says the tercile with the
> highest rate differential had a higher rate differential than the tercile with the lowest — the
> ranking variable measured as its own outcome. It would be near-infinite for any ranking on any
> field. It is printed because the decomposition is not readable without it, and labelled because it
> is the single most misreadable number in this report.

What the two real lines say: **the high-rate currencies did depreciate, and gave back about
two-thirds of what they paid.** Uncovered interest parity predicts they give back *all* of it, so
the spot spread should have been −0.318% against the observed −0.207%. The gap between prediction
and observation **is** the total, +0.110% per month, at t = +0.53.

So the finding, stated in the direction the data supports: **we cannot reject uncovered interest
parity.** The documented carry premium is not absent from this sample — it is +24.7% over
eighteen years — but it is smaller than the noise around it, and this design was pre-registered as
unable to confirm anything that faint.

## The tail, which was pre-registered for exactly this

| | | |
| --- | ---: | --- |
| Worst single month | **−16.85%** | October 2008 |
| **Worst twelve-month stretch** | **−41.62%** | February 2008 .. January 2009 |

Set against the whole history: **the strategy made +24.7% gross across 224 months and lost 41% in
one of them.** Everything it earned in eighteen and a half years does not cover its worst single
year.

This is why the tail reading was written into the plan before any rate was fetched. A mean and a
t-statistic describe the middle of a distribution and are structurally blind to its edge; carry's
signature failure is *positive mean, catastrophic tail*, and it is visible here in the exact place
the literature says to look. **Had the t-statistic passed, this would still not have been a
finding** — and saying so afterwards would have been worth nothing if the reading had not been
specified in advance.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` / `ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 130 source files |
| `uv run pytest` | Passed; **895 passed**, 9 skipped (21 new) |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

Twenty-one new tests. The ones carrying the design:

- **A rate from the month before the anchor cannot be reached.** Stated as the leak it prevents: a
  May average is only complete once May ends and is published later still, so ranking on it in early
  June would be borrowing the future and reporting it as skill.
- **An anchor missing one currency is dropped whole**, not just the pairs touching it — one absent
  rate removes nine of forty-five pairs and moves every remaining bucket boundary.
- **The three components rank over identical buckets**, asserted directly. If they could drift, the
  spot and carry lines would describe different portfolios and adding them would mean nothing.
- **The spot and carry spreads sum to the total**, with the fixture built so no division rounds the
  identity.
- **The worst stretch is a window search, not the neighbourhood of the worst month** — the fixture is
  chosen so the two answers differ, and the worst three-month run *starts on a positive month*.
- **A positive mean can hide a ruinous year**: eleven months of +2% and one of −20% average positive,
  and no criterion in this project would notice the twelfth.

Five safety assertions. One is new in kind: **`RATE_LAG_MONTHS`, `shift_months` and `month_start`
must each exist in exactly one file.** That is this project's most expensive recurring lesson made
executable — `TIMEFRAME_TO_DELTA` was once half-added and every daily request was refused before the
network call, producing a wrong answer shaped like a real one; the request-range limit lived in two
places and a CLI override reached only one. Three scripts now read the lag, and a private copy in
any of them would let a measurement and the coverage report that justifies it disagree silently
about what point-in-time means.

## Two defects found and fixed along the way

- **`--format json` emitted text before the opening brace** in both this script and the 9D-2 one:
  the plumbing summary printed ahead of the payload, so no reader could parse the output. The
  plumbing now travels *inside* the JSON rather than being dropped from it — the discipline is that
  it cannot be skipped, not that it must be printed.
- **The first draft of the safety test matched the bare word "carry"** and failed on the word
  "carrying" in a comment three layers away. Narrowed to import paths and public names.

## What this settles, and what it does not

It settles that the carry differential does not order this cross-section strongly enough for this
design to see, that the reason is uncovered interest parity doing most of what it claims, and that
the residual comes with a tail this project would not report as an opportunity under any statistic.

It does not settle that carry is dead — 224 monthly periods make t = 2 an annualised Sharpe near
0.45, and a real effect below that stays invisible here. As with the six before it, **a null means
we could not see it.**

Seven pre-registered measurements, seven nulls, and the largest number in every table rejected by
criteria fixed in advance.
