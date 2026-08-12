# Phase 9C-4 Verification Report — Execution Cost Against Outcomes

Generated: 2026-08-12

`PROJECT_PHASE = "phase_9c4_execution_cost_foundation"`

Every outcome figure this project has published is gross. `outcome_measurement.py` said so in its own
docstring, `scripts/measure_outcomes.py` printed it under each table, and `PLANS.md` has carried
spread data as an open item since Phase 9A-2. That was a caveat in prose. This makes it an axis.

It also settles a sentence 9C-3 asserted without measuring: that `volatility_ratio`'s one real
relationship "does not pay, because it settles the same coin flip sooner and every settlement pays a
spread". Half of that turns out to be wrong, and the half that is wrong is the reasoning.

## The cost is assumed, not observed

The project stores OHLC and no spread. Nothing was ingested and no provider was added, so what
follows is a model. The honest form of a model is the whole curve rather than one flattering point:
a reader with a broker's quote can locate their own cost on it. A safety test keeps an assumed cost
out of `app/services` and `app/persistence` entirely, so the Phase 9C-1 forward ledger goes on
recording gross outcomes — the only kind it can honestly hold.

## Cost moves the levels, and leaves the payoff alone

A long fills at the ask and exits at the bid, so a round-trip cost `c` is paid once. In mid-price
terms the intended gain arrives only when the mid reaches `target + c`, and the intended loss has
already happened when the mid reaches `stop + c`: **both levels move by `+c`**, and by `-c` for a
short.

What that does *not* change is the distance between the two levels. A win still pays what it paid
and a loss still costs what it cost; the entire effect lands on the probability of reaching the
target. That probability is `target_first_share`, which the project has been reporting since 9A-2,
and break-even stays 42.86% for the 1.5/2.0 geometry. So every number below is directly comparable
to every gross number already published — no new notion of profit was introduced to make the point.

## The curve

Target-first share, both directions pooled, 180 days, traded candles only. Cost in price units;
both instruments are quoted to five decimals.

| cost | cost/ATR (EU M15) | EURUSD M15 | EURUSD H1 | NOKSEK M15 | NOKSEK H1 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0.000 | 41.41% | 42.34% | 40.62% | 41.55% |
| 0.00002 | 0.041 | 40.08% | 41.85% | 39.57% | 41.22% |
| 0.00005 | 0.103 | 37.97% | 40.88% | 37.82% | 40.56% |
| 0.00010 | 0.205 | 34.76% | 39.46% | 35.29% | 39.35% |
| 0.00020 | 0.411 | 27.85% | 36.50% | 29.78% | 36.92% |
| 0.00050 | 1.027 | 11.71% | 28.00% | 16.04% | 30.06% |

Median average true range over each sample: **0.000487** (EU M15), **0.001054** (EU H1),
**0.000697** (NOK M15), **0.001467** (NOK H1).

Timeout share *falls* as cost rises — 12.19% to 7.47% on EURUSD M15 across the grid — because the
protective level moves closer and more windows resolve. Worth holding onto: charging for execution
makes windows resolve **more** often, which is the opposite of what a reader might expect and the
first crack in the 9C-3 sentence.

## Claim 1 — confirmed on all four series: no cost is small enough

The plan is below break-even before anything is charged, on every series: −1.45, −0.52, −2.24 and
−1.30 percentage points. The break-even cost is therefore not a number but a statement, and the
tooling reports it as one (`ALREADY_BELOW_AT_ZERO`) rather than interpolating a negative cost and
implying a cause.

**This is the arithmetic version of what 9C-2 and 9C-3 found in shares.** A driftless random walk
against levels at 1.5 and 2.0 breaks even at exactly `1.5 / 3.5` = 42.86%. The four measured gross
figures sit 0.5 to 2.2 points under that, and the shortfall is the ambiguity that 9A-2 chose to
count against the plan. To within the precision six months affords, **the market these levels are
walked through is a driftless random walk, and execution cost is what turns level into losing.**

## Claim 2 — refuted as written, and instructive about why

Pre-registered: *a cost of 0.00010 costs at least 5 points of target-first share on all four
series.* It does not.

| series | share lost to a cost of 0.00010 |
| --- | ---: |
| EURUSD M15 | −6.65 |
| NOKSEK M15 | −5.33 |
| EURUSD H1 | −2.88 |
| NOKSEK H1 | −2.20 |

It holds on M15 and fails on H1, by roughly a factor of two — which is roughly the ratio of the two
timeframes' average candle ranges. **The claim was stated in price units, and price units are not
comparable across timeframes.** `AGENTS.md` has carried a standing rule about exactly this since the
drawdown normalisation work: *a threshold on a raw magnitude is a defect waiting to surface, because
the timeframe, the instrument, and the period all change what "large" means.* The pre-registration
was written in breach of the project's own rule, and running it as written is what exposed that.

### Restated in the unit that travels, it is strikingly consistent

The cost worth five points of target-first share — the bar 9C-2 and 9C-3 required before calling a
field informative — expressed both ways:

| series | in price units | as a share of median ATR |
| --- | ---: | ---: |
| EURUSD M15 | 0.0000744 | 0.153 |
| EURUSD H1 | 0.0001718 | 0.163 |
| NOKSEK M15 | 0.0000935 | 0.134 |
| NOKSEK H1 | 0.0002163 | 0.147 |

Four series, two instruments, two timeframes, a spread of 0.029. Equivalently the slope is 30 to 37
points of target-first share per average candle range of cost, computed at the 0.00010 point and at
the five-point crossing alike.

**The whole standard of evidence this project has been applying is worth about a sixth of one
average candle range of execution cost.** On EURUSD M15 that is 0.74 in the fifth decimal place; on
EURUSD H1, 1.72. A reader who knows what their broker charges can compare directly.

### What a candidate would now have to clear

Break-even needs the gross shortfall closed *and* the cost paid. On EURUSD M15, at a cost of 0.15
ATR: 1.45 + 5 ≈ **6.5 percentage points of target-first share above the base rate**, before a
candidate is merely level.

Every effect 9C-2 and 9C-3 measured was under 4 points, most under 2, with signs that flipped
between series. The gap is not marginal.

## Claim 3 — refuted, and it takes a piece of the 9C-3 report with it

Pre-registered: *a fixed price cost costs the bottom `volatility_ratio` decile more target share
than the top, because the same cost is a larger fraction of a quiet window's ATR.* Criterion: a
difference of 5 points or more, same sign on all four series.

| series | decile 1 | decile 10 | difference |
| --- | ---: | ---: | ---: |
| EURUSD M15 | −6.72 | −6.22 | −0.50 |
| EURUSD H1 | −2.32 | −4.15 | +1.83 |
| NOKSEK M15 | −4.52 | −4.45 | −0.07 |
| NOKSEK H1 | −1.68 | −2.00 | +0.32 |

All four under two points, signs flipping. **The cost handicap is uniform across the volatility
deciles.**

The mechanism is visible in the definition. `volatility_ratio` is the latest candle's true range
over the window's *average* true range
([strategy_field_resolver.py:112](app/domain/strategy_field_resolver.py:112)) — a ratio, and
therefore nearly scale-free. Levels are placed from the average, so how much a fixed cost hurts a
window depends on that window's ATR. Bucketing on a ratio does not sort windows by ATR, so it cannot
sort them by cost sensitivity. The same effect that is invisible *within* a timeframe is plain
*between* them, in Claim 2's table: −6.65 on M15 against −2.88 on H1.

### The correction to 9C-3

That report concluded, correctly, that the timeout finding does not pay. The reason it gave was
wrong: *"the same wager settled more often, and every settlement pays a spread."* Per window the
cost is paid once whichever decile the window lands in, and this run shows the handicap is flat
across them. The frequency argument would need a strategy that re-enters, and this project has none.

**The conclusion survives and is now stronger than the argument that was offered for it.** Target
share in those deciles is flat gross (9C-3) and flat under cost (here), which is a measurement
rather than a story. The correction has been written into the 9C-3 report itself.

Worth noting that the replacement mechanism proposed in this phase's own pre-registration was also
wrong, and by the same amount. Pre-registration did not make the guess right. It made it cheap to
find out that it was not, which is the entire function.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 123 source files |
| `uv run pytest` | Passed; 806 passed, 9 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |
| zero-cost point against 9C-3 | reproduced, see below |

**Reproduction of 9C-3.** The zero-cost point of every sweep is the gross measurement, so it must
reproduce what the previous phase published. EURUSD M15 comes back identical to two decimals across
the board: decile-1 timeout 23.01%, decile-10 timeout 6.19%, gradient +1.68, pooled 41.41% against
41.42%. The other three series drift by up to 0.25 points, and the reason is not a bug: `--days 180`
is measured from the clock, the worker has ingested another day of EURUSD since 2026-08-11, and the
NOKSEK window start has rolled past its oldest stored candles. A rolling sample moves; saying so is
cheaper than pretending it does not.

**Twenty-four measurements from eight invocations** — four cost sweeps of six points each, and four
`volatility_ratio` decile profiles run twice, at zero cost and at 0.00010.

**Twenty-eight new tests.** The ones that carry the design: a cost of zero measures exactly what the
gross run measured, so no published figure moved when the parameter appeared under it; a cost moves
a long's target out of reach *and* brings its protective level within reach, tested separately
because forgetting the second half is how a cost model flatters; the shift is mirrored for a short;
and the distance between the levels is unchanged, which is the property the entire formulation rests
on. Plus the refusals: a negative cost is a rebate and is rejected, a curve must start from a free
measurement, points must be strictly ascending, and every point must cover the same windows — a
curve built from shifting populations compares samples rather than costs.

Four safety assertions, of which one matters more than the rest: **no file under `app/services`,
`app/persistence`, `app/telegram` or `app/api` may pass a cost.** Phase 9A-5 drew the line between
observation and invention with the `provider` column and paid for drawing it late — 30 seed candles
had been quietly replacing real ones. An assumed cost stored beside an observed candle would be that
mistake in a new place.

## What this settles

- **No execution cost is small enough.** All four series are below break-even before anything is
  charged. Cost is not what stands between this project and a viable plan; it is what stands behind
  it.
- **The project's bar for a finding is worth ~0.15 average candle ranges of cost**, consistently
  across four series. That is the most portable number this project has ever measured, and it is a
  fact about arithmetic rather than about markets.
- **A candidate must now clear roughly 6.5 points above the base rate** on EURUSD M15 to be level.
  Nothing measured in 9C-2 or 9C-3 came within a third of that.
- **`volatility_ratio` does not sort windows by cost sensitivity**, because it is a ratio and cost
  sensitivity is a matter of scale. The 9C-3 conclusion holds; its stated reason does not.
- **It does not say costs are unimportant.** It says they are not the binding constraint, because
  something upstream of them already binds.

## What it means for the product

Nothing here changes what a person is told, because there is still nothing to tell them. What it
changes is the standard for anything that might be told to them later: a base rate presented as
context now has a known price attached, and any future candidate can be measured against a bar that
is stated in the unit that gets paid rather than in percentage points that do not.

The open item that has stood since 9A-2 — "spread data, without which every outcome stays gross" —
can be retired in the form it was written. What replaces it is narrower and better posed: observing
a real spread is worth doing when a candidate exists whose margin is close enough to 0.15 ATR for
the precision to matter. None is.

The obvious next measurement, if there is one: bucket windows by `cost / ATR` itself. It is the one
quantity shown here to order cost sensitivity, it is comparable across instruments even though ATR
alone is not, and no field in the registry currently expresses it.
