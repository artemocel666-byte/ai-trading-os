# Phase 9D-3 Verification Report — Interest Rates, the First Data That Is Not a Price

Generated: 2026-08-15

`PROJECT_PHASE = "phase_9d3_interest_rate_ingestion"`

Six pre-registered measurements have returned nothing, and every one of them read the same input:
**past prices of the instrument itself**. 9D-2 drew the boundary explicitly — momentum is the only
cross-sectional field computable from prices alone, so what daily prices can say about the
cross-section has been asked and answered.

Carry is the one remaining candidate that is meaningful, obtainable and cheap. This slice brings it
in. **It measures nothing** — that is 9D-4, whose criteria were fixed in this slice's plan before a
single rate was looked at.

## Checked before planning, as 9D-1 taught

FRED serves three-month interbank rates for all ten universe currencies as CSV from a public
endpoint, **free and without an API key**. The data that could break a six-null streak turned out to
cost nothing, which is why it was worth probing before writing a plan around it.

Two properties of the source decided two design rules before any code was written:

| observed | rule it forced |
| --- | --- |
| `3.84` means 3.84% per annum | percent becomes a fraction in the adapter, once, where the source's convention is known |
| USD April 2020 is **blank** | a missing month is **absent**, never a zero |
| JPY April 2020 is **−0.039** | **no positivity constraint**, in the entity or the schema |

That last one matters more than it looks. Every price column in this schema carries a
`> 0` check. A rate column with one would have rejected real observations at the database boundary,
where the failure would have been hardest to read.

## The result

| | |
| --- | ---: |
| Currencies fetched | **10 of 10** |
| Rows stored | **5,855** |
| Span | 1956-01 .. 2026-06 |
| Rate range | −0.93% .. 27.20% |
| **Gaps inside any series** | **1** — USD, April 2020 |
| **Anchors with all ten currencies at the two-month lag** | **221 of 222** (2007-10 .. 2026-03) |

That last line is the figure Phase 9D-4 depends on, produced here rather than discovered there.
9D-2 measured over 226 monthly periods; carry will run over 221 of substantially the same history,
so the two results will be directly comparable.

The one incomplete anchor is June 2020, which needs April 2020's USD rate. It will be excluded and
counted, not filled.

The window ends in March 2026 because the EUR and GBP series stop in January — a property of the
source, not a loss of ours.

## Storage is faithful; the lag is a measurement choice

The row records the month the value describes, exactly as the source states it. *How stale a rate
must be before a measurement may rank on it* belongs to 9D-4's pre-registration, not to the table.
Baking a lag into storage would have made it impossible to question later.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 128 source files |
| `uv run pytest` | Passed; 874 passed, 9 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |
| Migration 0005 up, down and up again | Clean round-trip |

Spot-checks against the source CSV, chosen to test the three rules above:

| value | source | stored |
| --- | --- | --- |
| AUD 2008-01 | `7.180000000` | `0.07180000` |
| USD 2008-01 | `3.84` | `0.03840000` |
| JPY 2020-04 | `-0.03900` | `-0.00039000` |
| **USD 2020-04** | *blank* | **no row** |

USD March and May 2020 are both present, so the April absence is a genuine hole between two real
observations rather than the edge of the series.

Nineteen new tests. The ones that carry the design: a negative rate is accepted **and the test says
why it exists**, so nobody adds a positivity rule later thinking its absence was an oversight; an
empty value and a `.` placeholder both yield no row; a series that is empty throughout is refused
outright, because silence is not data; a rate must sit on the first instant of a month, so one month
cannot hold two rows; and the anchor-completeness count is asserted against a hand-built case.

Five safety assertions, of which one is the point: **rates may not appear in any Telegram, API,
scheduler or service file.** They are an input to measurement, never an output to a person — putting
an unmeasured number in front of someone is how it starts looking like a finding.

## Pre-registered for 9D-4, before any rate was looked at

- **Field:** carry differential = `rate(base) − rate(quote)`.
- **Point-in-time rule:** the rate is lagged **two full months**. At the anchor beginning month *M*
  the value dated *M−2* is used. A monthly average for *M−1* is complete only once *M−1* ends and is
  published later still, so two months errs toward *not knowing*.
- **Terciles, monthly rebalance, one-month holding** — unchanged from 9D-2, so the two are directly
  comparable.
- **Primary metric: total return** = spot return over the month **plus** carry accrued (annual
  differential ÷ 12).
- **Always reported beside it: the decomposition** — the spot-only spread and the carry-only spread.
  A positive total driven entirely by accrual is a different claim from one where the spot move
  cooperates, and one number cannot show which.
- **Why the total is not a tautology.** Uncovered interest parity predicts the high-rate currency
  depreciates by exactly the differential, so the total spread should be **zero**. The documented
  anomaly is that it does not. The null hypothesis is zero, which is what makes this a test rather
  than an accounting identity.
- **Criteria, all four required**, identical to 9D-2: mean total spread positive; **t ≥ 2.0**; the
  same sign in **both halves**; survives **2 basis points** per leg.
- **The same honest limit.** About 221 monthly periods make t = 2 an annualised Sharpe near 0.45. A
  faint real effect stays invisible, and a null will mean *we could not see it*.
- **One extra reading, because of what carry is.** Carry is the most-traded anomaly in currencies and
  its signature failure is *positive mean, catastrophic tail* — it broke violently in 2008 and on the
  franc in 2015. A t-statistic cannot see that, so 9D-4 also reports **the worst single month and the
  worst twelve-month stretch**. A spread whose mean passes while its tail is ruinous will be reported
  as exactly that, not as a finding.

## What this settles

Nothing about markets. It settles that the project can now ask a question of data it did not
previously have, and that the data arrived clean: ten currencies, one gap, 221 usable anchors.

Whether that changes any answer is 9D-4's business.
