# Phase 10-3 Verification Report — Hidden Concentration

Generated: 2026-08-22

`PROJECT_PHASE = "phase_10_3_hidden_concentration"`

Pre-registered in [`docs/phase10-3-preregistration.md`](phase10-3-preregistration.md), committed
before any code (`ac6604e`).

## The eight criteria

| | criterion | result |
| --- | --- | --- |
| 1 | Both boundary cases hand-checked | **Pass** — perfectly correlated → exactly 1, uncorrelated → exactly N |
| 2 | Three instruments at 0.85 → about one bet | **Pass** — 9 / 8.1 = 1.11, and **1.2 live** |
| 3 | No correlation without its two halves | **Pass** — the entity cannot hold one |
| 4 | Every correlation carries its overlap count | **Pass** |
| 5 | **Too little overlap yields an absence, never a zero** | **Pass** |
| 6 | The 9D-1 claim is measured | **Pass — and it needed care; see below** |
| 7 | A live run, plumbing read first | **Pass** — 44 instruments, 85 returns each |
| 8 | No forecast, nothing new in Telegram or the API | **Pass** |

## The product, on real data

```
EURUSD, GBPUSD, AUDUSD: позиций 3, независимых ставок примерно 1.2

  EURUSD/GBPUSD: +0.81 (половины +0.78 и +0.84, общих дней 85)
  EURUSD/AUDUSD: +0.71 (половины +0.77 и +0.63, общих дней 85)
  GBPUSD/AUDUSD: +0.63 (половины +0.60 и +0.65, общих дней 85)
```

**Three positions are 1.2 independent bets.** Somebody holding all three believes they are
diversified across three instruments and is in fact making one bet at roughly triple size. Nothing
in that sentence is a forecast — it is arithmetic over 85 stored daily returns.

The halves matter here too: the widest disagreement in the set is 0.14, which is inside the ~0.12
standard error of a correlation on this window. The number is stable enough to act on, and the
report says so rather than leaving the reader to assume it.

## Criterion 6 needed care, and I nearly got it wrong

The universe measured **16.6 effective bets** against a docstring that has said "closer to nine"
since 9D-1. The obvious move was to declare the docstring wrong and replace the number.

**That would have been a mistake, and the two figures answer different questions.**

- **Nine is the rank of the return space** — how many independent factors drive forty-four pairs
  built from ten currencies. It is fixed by the construction and the docstring's reasoning is right.
- **16.6 is the diversification of an equally weighted set**, `N² / ΣΣρ`. It rises whenever
  correlations are negative and **can exceed the rank outright**: two perfectly opposed positions
  are driven by one factor and hedge to nothing, which this project's own measure reports as
  `FULLY_HEDGED` rather than as a number.

So the docstring was corrected by making the distinction explicit rather than by swapping one right
answer for a right answer to a different question. Measuring the rank itself would need an
eigendecomposition — deliberately avoided in this slice so that no new dependency and no inexact
arithmetic entered the project to answer a question about diversification. A test now pins the
distinction so nobody conflates the two later.

## One structural fault, found and closed mid-build

`read_concentration` first accepted **flat sequences** of returns. Alignment is a property of each
*pair* — two instruments share whichever days both were priced — so flat lists of equal length could
have described different days, and the correlation returned would have been real arithmetic over
mismatched dates with nothing in the output to show it. `aligned_returns` existed to prevent exactly
that and was being bypassed by the signature above it.

The function now takes returns **keyed by moment** and aligns each pair internally. A test asserts
it end to end: a holiday in one instrument shortens the overlap to 59 days rather than shifting the
series against each other.

## What the live universe showed

```
CADNOK/USDNOK: +0.91 (половины +0.93 и +0.91)
EURNZD/NZDCAD: -0.89 (половины -0.89 и -0.89)
AUDUSD/EURJPY: +0.05 (половины +0.61 и -0.29)
```

That last line is the argument for the halves in one row. The coefficient reads **+0.05 —
"unrelated"**. The halves read **+0.61 then −0.29**: strongly related, then inversely related. A
single number would have told a reader those two instruments have nothing to do with each other,
which is the opposite of what the window contains.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` / `ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 140 source files |
| `uv run pytest` | Passed; **947 passed**, 9 skipped (19 new) |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |
| Live, three instruments | 1.2 effective bets, widest half-gap 0.14 |
| Live, whole universe | 16.6 effective bets over 946 pairs, 4 seconds |

No new dependency: `Decimal.sqrt()` throughout, and the measure was chosen partly because it needs
no eigendecomposition. No schema change and no migration.

## What this settles

Nothing about markets. It settles that the project can tell somebody how concentrated a set of
positions actually is, with no forecast anywhere in the answer, and that when the measurement
disagreed with a long-standing claim the disagreement turned out to be two questions rather than an
error — which is only visible because both were written down.

10-4 is COT positioning: the one remaining source that would let the report say **what participants
hold** rather than **what the price did**. Its value here is descriptive; as a predictor it would
almost certainly be the eighth null.
