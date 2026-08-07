# Phase 9A-3 Verification Report — A Market View, and What It Is Worth

Generated: 2026-08-07

## Scope

This is the slice where the project takes a market view for the first time. Every safety test since
Phase 4 asserted that nothing here decides "up" or "down"; Phase 9A made it mechanical — no function
anywhere may return a `SignalDirection` — and wrote down that the day the test failed, somebody would
be adding a strategy and would have to say so out loud.

`PROJECT_PHASE = "phase_9a3_market_view_candidate_foundation"`

The deliverable was defined in advance as **a verdict, not a strategy**: a candidate, acceptance
criteria fixed before any run, and an honest report of whether they were cleared. They were. That
outcome deserves more scepticism than a failure would have, and most of this document is that
scepticism.

## The candidate

`app/domain/direction_candidate.py`, the one module exempted from the anti-strategy invariant.

**Efficiency-gated reversion.** A new descriptive field measures how *straight* a window moved, as
opposed to how far: `|Σ returns| / Σ|returns|`, bounded to `[0, 1]` by the triangle inequality. One
is a straight line, zero is a sawtooth ending where it began. When that ratio clears 0.60, the
candidate proposes a direction **against** the window's own move. Below it, and on any window the
pipeline does not consider ready for review, it returns `None`.

This filled a real gap rather than adding another indicator: every existing measurement — average
true range, candle ranges, drawdown — answers *how far*, and none answered *how straight*. Two
windows with an identical average true range could be a clean climb and a pointless chop, and until
now they were indistinguishable to every rule in the project. The ratio is also normalised by
construction, which shows: its distribution is nearly identical on both timeframes (median 0.282 on
M15 and 0.282 on H1, p75 0.467 and 0.461), the same signature the drawdown work went looking for.

**Abstention is first-class and enforced.** The return type is optional, and a safety test requires
it to stay optional. At threshold 0.60 the candidate speaks about roughly an eighth of windows and
says nothing about the rest.

**The direction of the hypothesis was chosen by measurement, not taste.** The module was written the
intuitive way first — a straight move continues — and the in-sample sweep contradicted it at every
threshold on both timeframes. It was turned around before the held-out data was touched.

## The measurement, and why it is not the 9A-2 baseline

Comparing against the Phase 9A-2 baseline would have been wrong: that baseline carries the sample's
own drift, so a candidate leaning short would have inherited 4.6 to 10.9 percentage points it did not
earn.

The benchmark is instead computed **on the candidate's own windows** — what a coin toss would have
produced on exactly the subset it chose to speak about. Both directions are measured for every
window anyway, so this costs nothing and holds window selection constant. `edge` is the candidate's
target-first share minus that benchmark.

One consequence worth stating: because the benchmark pools both sides of each window, the inverted
candidate's edge is always exactly the negative of the candidate's. **Continuation and reversion are
one signed result, not two chances to find something** — which is why the multiple-comparison count
for this slice is five thresholds, not ten configurations. A test asserts the identity.

## Acceptance criteria, fixed before any run

Recorded in the plan and unchanged since:

1. out-of-sample `edge ≥ 3 п.п.`, 2. on **both** timeframes, 3. coverage **≥ 10%** on both,
4. out-of-sample edge **≥ half** the in-sample edge.

Split: first 60% of windows in-sample, last 40% held out and run **once**.

## The in-sample sweep

EURUSD, 180 days, window 12, horizon 24 candles, gated on pipeline readiness. In-sample only — the
held-out part was not looked at while choosing.

| threshold | coverage | M15 trend edge | M15 reversion edge | H1 trend edge | H1 reversion edge |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.20 | ~62% | −4.95 | +4.95 | −3.26 | +3.26 |
| 0.30 | ~46% | −5.30 | +5.30 | −4.30 | +4.30 |
| 0.40 | ~32% | −5.51 | +5.51 | −4.47 | +4.47 |
| 0.50 | ~21% | −6.68 | +6.68 | −3.78 | +3.78 |
| **0.60** | **~12%** | −8.26 | **+8.26** | −4.80 | **+4.80** |

The sign is the same in all ten cells, and on M15 the magnitude grows monotonically with the
threshold. That gradient is the most reassuring feature of the whole slice: the effect tracks the
variable it is supposed to track, which an accounting error would have no reason to do.

Selection rule — highest edge with coverage at or above the 10% floor — picks **reversion at 0.60**
on both timeframes.

## The held-out run

Once, at that configuration.

| | windows | coverage | resolved | rule | benchmark | inverted | edge |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| M15 in-sample | 9,954 | 12.02% | 969 | 50.77% | 42.52% | 34.26% | +8.26 |
| **M15 held out** | 6,637 | 13.29% | 548 | 47.26% | 40.42% | 33.58% | **+6.84** |
| H1 in-sample | 2,522 | 11.58% | 229 | 45.41% | 40.61% | 35.81% | +4.80 |
| **H1 held out** | 1,682 | 11.18% | 126 | 52.38% | 36.90% | 21.43% | **+15.48** |

**All four criteria are met**: edge ≥ 3 on both (6.84, 15.48), coverage ≥ 10% on both (13.3%, 11.2%),
and the held-out edge exceeds half the in-sample edge on both (6.84 vs 4.13, 15.48 vs 2.40).

### Robustness, run after the verdict and labelled as such

| variation | M15 held-out edge | H1 held-out edge |
| --- | ---: | ---: |
| as specified | +6.84 | +15.48 |
| without the readiness gate | +6.22 | +15.00 |
| horizon 96 instead of 24 | +9.62 | — |

The readiness gate is not doing the work — removing it changes almost nothing, which means the
result belongs to the efficiency filter rather than to the eleven rules. At a 96-candle horizon the
in-sample and held-out edges converge to +9.64 and +9.62, so the horizon is not carrying it either.

## What this does **not** establish

The criteria were deliberately written about effect size, not statistical significance, because
**this data cannot support a significance claim and no reading of it should imply one.**

- **The samples are far smaller than they look.** Windows step one candle at a time and their forward
  paths overlap across the whole horizon, so 548 resolved M15 windows are perhaps a few dozen
  independent observations, and 126 resolved H1 windows are perhaps a handful. The H1 figure of
  +15.48 is the least trustworthy number in this report precisely because it is the largest: it rests
  on 126 heavily overlapping windows, and the gap between it and the in-sample +4.80 is far more
  likely to be noise than a discovery.
- **Everything is gross of costs.** The candidate's held-out M15 share of 47.26% sits about 4
  percentage points above the 43.2% break-even implied by the Phase 9A geometry. On M15 the target is
  roughly 8 pips and the protective level roughly 6; a spread of half a pip on each side is a
  material fraction of both. **Whether anything survives costs is unknown and this project cannot
  currently compute it**, because no spread data is stored.
- **One instrument, one six-month period, one regime.** The held-out part is simply the most recent
  40% of that period, not an independent sample of market conditions.
- **The mechanism is a story fitted to a result.** A conspicuously straight twelve-candle push being
  more often exhaustion than initiation is plausible and well-worn, but it was written down after the
  numbers, not before, and it is not evidence.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 114 source files |
| `uv run pytest` | Passed; 669 passed, 8 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

### The invariant that was replaced

`test_phase9a_no_function_returns_a_direction` now exempts exactly one module, the same shape the
`calculate_*` ban took in Phase 9A. Four tests replace what was lost:

- the exempted module's directional functions must return an **optional** direction, so a candidate
  cannot be made to have an opinion on every window;
- it may not import the outcome measurement that judges it — a candidate able to reach Phase 9A-2
  could propose whichever direction happened to work, and the numbers would look excellent;
- it imports no persistence, adapter, Telegram, API, or scheduler code;
- no service, route, command, or job references it.

A fifth test asserts that `market_context.move_efficiency` reports the same value for a window and
its mirror. The descriptive half is public to every rule; only the sign is confined, and without that
test the module boundary would be decorative.

### Unit coverage

Straight climb and its mirror, a sawtooth that travels just as far and abstains, a window below the
threshold, a flat window that abstains rather than dividing by zero, scale invariance, a distrusted
window rejected by the real composer, the arithmetic ceiling of a perfect candidate (+50, not +100),
the inverted-edge identity, ambiguity never becoming a win, and a window resolved on only one side
being dropped from both.

## Where this leaves the project

Phase 9B — delivery — is unblocked in the sense that a direction now exists and has cleared a bar set
in advance. Nothing is wired: the candidate is unreferenced by any service, command, route, or job,
and whether to put a market view in front of a person is a decision for the project's owner, not a
consequence of a passing test.

If it does go forward, three things should go with it: the coverage figure (it is silent on seven
windows in eight), the ambiguity and cost caveats, and the fact that the strongest number here rests
on the smallest sample.
