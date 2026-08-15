# Phase 9D-2 Verification Report — The First Cross-Sectional Measurement

Generated: 2026-08-15

`PROJECT_PHASE = "phase_9d2_cross_section_measurement"`

Five phases asked what follows a window on one instrument and answered nothing. 9D-1 built a
different instrument. This asks the different question:

**Do the currencies that rose most over the last three months behave differently over the next month
than those that rose least?**

Formation three months, holding one month, terciles — all fixed in the Phase 9D-1 plan before any
daily data existed, and not revisited.

## The correction this phase rests on

I had said the Phase 9C-3 decile machinery would transfer to a cross-section. **It would not.**
`build_field_outcome_profile` sorts every observation together and cuts buckets globally, which here
would have ranked a 2008 return against a 2015 one — a comparison through time wearing
cross-sectional clothes, and exactly the confusion this phase exists to avoid.

Ranking happens **inside each date**, and only then are the dates pooled. A guard in
`rank_into_buckets` refuses a group spanning more than one moment, because that mistake would be
invisible in the output.

## Plumbing, read before the result

| | |
| --- | ---: |
| Pairs with stored daily history | **44** |
| History | 2007-06-19 .. 2026-08-15 |
| Rebalance dates | **226** |
| Instruments per date | **min 44, median 44, max 44** |
| Instrument-dates dropped for missing prices | **0** |

Every instrument is present on every date. That is the cleanest cross-section this project could
have asked for, and it is what 9D-1's coverage repair bought.

## The result: null on all four criteria

Top-tercile mean return minus bottom-tercile mean, per month, both legs charged:

| cost per leg | periods | mean | standard error | t |
| --- | ---: | ---: | ---: | ---: |
| 0 bp | 226 | **−0.153%** | 0.206% | **−0.74** |
| 1 bp | 226 | −0.173% | 0.206% | −0.84 |
| 2 bp | 226 | −0.193% | 0.206% | −0.94 |
| 5 bp | 226 | −0.253% | 0.206% | −1.23 |
| 10 bp | 226 | −0.353% | 0.206% | −1.71 |

| criterion | result |
| --- | --- |
| mean spread positive | **no** — it is negative |
| t ≥ 2.0 | **no** — −0.74 |
| same sign in both halves | **no** — +0.097% then −0.483% |
| survives 2 bp per leg | **no** |

**All four fail.** The annualised Sharpe of the gross spread is about **−0.17**; the bar was +0.45.

The point estimate is not merely small, it is the *wrong sign*: currencies that rose most did
slightly worse over the following month. That shape is reversal rather than momentum — and at
t = −0.74 it is noise, not a finding in the other direction. Saying otherwise would be reading a
result off a number that cannot support one.

## The tempting number, and why it is left alone

The second half reads **−0.483% with t = −2.11**, which clears two standard errors in magnitude.

It is not a finding, for three reasons stated before it was looked at:

1. **It is the wrong sign for the hypothesis.** The pre-registered criterion is a positive spread;
   a negative one that happens to be large is a different claim, and one nobody registered.
2. **The halves are a stability check on a headline that already failed**, not a test in their own
   right. A stability check on a null has nothing to stabilise.
3. **Ten numbers were on the table** — two halves across five cost levels — and one excursion past
   two standard errors among ten correlated readings is roughly what chance produces.

This is the third phase in a row where the largest number in the table was rejected by criteria
fixed in advance. 9C-5 rejected −7.55, and it was right to.

## What this settles, and what it does not

- **Cross-sectional currency momentum, as measured here, is not there to see.** Twenty years,
  forty-four instruments, complete coverage, non-overlapping monthly periods, nothing selected
  anywhere — and the spread is negative and inside one standard error.
- **A null here is weaker than the nulls before it, and that was said in advance.** 226 periods make
  t = 2 an annualised Sharpe near 0.45. A real effect of Sharpe 0.2 would be invisible to this
  design. "We could not see it" is the honest reading, not "it is not there".
- **One field only.** This tested the one cross-sectional field computable from prices alone.
  The other classic candidates — carry and value — need interest rates and price levels, and the
  project has neither. **That is the boundary this phase draws: what daily prices alone can say
  about the cross-section has now been asked and answered.**
- **Costs never got a chance to matter.** The gross spread is already negative, so the sweep is
  academic — the same shape as 9C-4's finding, arrived at independently.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 126 source files |
| `uv run pytest` | Passed; 855 passed, 9 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |
| instruments present per rebalance date | 44 of 44, every date |

Twenty-one new tests. The ones that carry the design: **ranking happens inside a date**, asserted by
a fixture where one instrument holds the same field value on two dates and lands top of one and
bottom of the other — a global ordering would place it mid-pack on both and report nothing;
observations spanning several dates are refused rather than averaged; the statistic is computed over
periods and matches a hand-computed t of 3; cost is charged on both legs; a spread that works in only
one half does not clear; and a stale anchor price is refused rather than used, so a convenience
cannot silently compare this month's price with last quarter's.

## The line that moved

A cross-sectional ranking is structurally a direction — the headline number is what the top did
*minus* what the bottom did — so the project's oldest rule had to change. It moved from **"no
direction exists"** to **"no direction is delivered"**:

| | before | now |
| --- | --- | --- |
| may a ranking exist? | no | **yes, in the measurement layer only** |
| may it reach a user? | n/a | **no** — a safety test bans `cross_section` from every service, Telegram, API and scheduler file |
| may the project trade? | no | **no**, `REAL_TRADING_ENABLED` stays permanently `False` |

What the old rule actually protected is untouched: this cannot quietly become a trading bot, and a
person is still told only what was measured.

## Where this leaves the project

Six pre-registered measurements, six nulls. The method has now been applied to a short horizon and a
long one, to one instrument and to forty-four, to time-series and to cross-section. Nothing measured
has cleared a bar set before the run.

What has been built along the way is a bench that says no reliably, and a body of honest negative
results that most projects never produce because they never look. The next real choice is the one
9C-5 named and this phase sharpens: **add information that is not this market's own past prices, or
accept that the deliverable is the measurement bench rather than a forecast.**
