# Phase 10-3 Pre-registration — Hidden Concentration

Written: 2026-08-22. **Committed before any code**, as 10-1 established.

## Context

10-2 gave the universe a description: what moved, whether it was the pair or the currency, and how
unusual today is against each instrument's own history. This adds the reading that most clearly
justifies the product — **how many bets a set of positions actually is.**

A person holding `EURUSD`, `GBPUSD` and `AUDUSD` believes they hold three positions. If those three
are 0.85 correlated they hold roughly **one position at triple size**, and the loss that arrives
will arrive on all three at once. Nothing about saying so requires a forecast: it is arithmetic on
stored prices, and it is the kind of thing that prevents real money being lost.

## Checked before planning, as 10-1 and 10-2 taught

**1. There is no correlation machinery in the project at all.** Genuinely new ground, not a
duplication risk.

**2. But there is an unmeasured claim, and it has been sitting in a docstring since 9D-1.**
`app/domain/currency_universe.py` states:

> Ten currencies give forty-five pairs, but every pair is a ratio of two members of the same small
> set, so the number of genuinely independent dimensions is **closer to nine**.

Nobody measured that. It is reasoning from the construction, and it is almost certainly the right
order of magnitude — but this project does not let assertions of that kind stand anywhere else, and
this phase is exactly the instrument for checking it. **10-3 measures the nine.**

**3. No numpy, and none is needed.** `Decimal.sqrt()` is already the project's convention
(`context_engine.py`, `cross_section.py`), and the concentration measure below avoids
eigendecomposition entirely — so nothing new enters the dependency list to answer this question.

**4. The 10-2 machinery is reused, not rebuilt**: `format_distribution` is still the only renderer,
`nearest_rank` and `percentile_rank` are still the only percentile definitions, and the one-concept
test gains whatever this phase defines once.

## Design

**Correlation of daily returns, in Decimal, pairwise.** Close-to-close returns over a fixed window.
No new dependency, no float in a financial path.

**The concentration measure, and why this one.** For `N` instruments held in equal size, portfolio
variance is proportional to the sum of every entry of the correlation matrix, so the **effective
number of independent bets** is

```
effective_bets = N² / ΣΣ ρ(i, j)
```

Its two boundary cases are the reason to prefer it: if every instrument is perfectly correlated the
sum is `N²` and the answer is **1**; if none are correlated the off-diagonals vanish, the sum is `N`
and the answer is **N**. It needs no eigendecomposition, it is exact in `Decimal`, and both extremes
are hand-checkable — which the pre-registered criteria below require.

**A single correlation number is a lonely central tendency, and the 10-2 rule applies to it.**
Correlation moves; reporting `0.6` for a window whose halves were `0.85` and `0.30` is the same
failure as a median without a spread, in a different costume. **Every correlation is therefore
reported with its two halves**, the way `CrossSectionProfile.half` has done since 9D-2.

**Overlapping observations travel with every figure.** Pairs have different histories, and two
instruments can only be correlated over the days both were priced. That count is part of the
reading, never assumed.

**The honest limit, stated up front.** A quarter is about 64 trading days, so a correlation carries
a standard error near `1/√64 ≈ 0.12`. **0.3 and 0.5 are not reliably distinguishable at this window**,
and the report has to say so rather than present two decimal places as precision.

**Absences named.** Two instruments without enough overlap get no correlation — never a zero, which
would read as "independent" and is the most dangerous possible substitution in this particular
feature.

## Acceptance criteria — fixed here, before the code

1. **Both boundary cases are hand-checked**: `N` perfectly correlated instruments give exactly 1
   effective bet, and `N` uncorrelated ones give exactly `N`.
2. **The product case is demonstrated**: three instruments correlated at 0.85 report close to one
   effective bet, asserted on a hand-built matrix.
3. **No correlation is reported without its stability**, both halves of the window beside it.
4. **Every correlation carries its overlapping-observation count.**
5. **Too little overlap yields an absence, never a zero.** A fabricated zero here would tell someone
   their positions are independent when nothing is known — the worst failure this feature can have.
6. **The 9D-1 claim is measured**, and the report states the measured effective count for the whole
   universe **whether or not it comes out near nine**. If it does not, the docstring is corrected in
   this slice.
7. **A live run over the current universe**, plumbing read before the content.
8. **No forecast, and nothing new reaches Telegram or the API.**

If criterion 5 cannot be demonstrated, the slice is not done: every other criterion improves a
number, and that one is the difference between a missing answer and a dangerous one.

## Changes

1. `app/domain/entities/concentration.py` — new: correlation and concentration readings, each
   carrying its own overlap count and its halves.
2. `app/domain/concentration.py` — new, pure: returns in, correlations and effective bets out.
3. `app/presentation/readings.py` — rendering for the new readings, in the one renderer module.
4. `scripts/report_concentration.py` — new, read-only; also accepts a list of instruments so a
   person can ask about the set they actually hold.
5. `app/domain/currency_universe.py` — the "closer to nine" claim replaced by the measured figure,
   with the measurement named.
6. Tests, including all eight criteria.
7. `docs/phase10-3-verification-report.md`, AGENTS.md, PLANS.md, README.md, operations.md, Notion.

## Explicitly not in this slice

- **No position sizing, no risk limits, no advice about what to hold.** The report says how many
  independent bets a named set is; what to do about that is the reader's business and stays theirs.
- **No forecast of correlation.** Correlations move, and saying how they will move is the same
  forbidden claim in a new place.
- **No COT** — 10-4.
- **No visual layer.** That comes when the content stops changing shape, and it will need its own
  pre-registration: a chart can imply a trend without a single word, so the criteria there are about
  permitted forms rather than permitted vocabulary.
- **No schema change**, so no migration.
