# Phase 9A-7 Verification Report — Three Measurement Gaps

Generated: 2026-08-08

`PROJECT_PHASE = "phase_9a7_measurement_gaps_foundation"`

The fourth remediation item. None of these was a crash or a failing test — each was a number that
quietly meant something other than what it was read as, which is the harder kind to notice.

Two of the three fixes needed a calibration run to finish. The Docker engine stopped mid-session, so
the code landed first with the outstanding measurements named rather than left to be discovered; both
were completed once it came back and are recorded below.

## 1. The drawdown only ever looked one way

`_max_close_to_close_drawdown` measures the fall from a running peak and nothing else. A window that
climbed steeply and never pulled back reports a drawdown of **zero** — genuinely true, and read by a
warning rule as "this window was calm".

That made the rule directional in a project that has no direction: it treats a falling market as
risky and a rising one as untroubled. It also interacted badly with Phase 9A-3, whose candidate
proposed SHORT on rising windows — exactly the windows this rule could never flag.

Added: `max_close_to_close_runup` on the context entity, the exact mirror (trough for peak, rise for
fall), and a resolver `market_context.max_close_excursion_atr` taking the larger of the two and
normalising it the same way.

A mirrored move lands about one percent apart rather than exactly equal: the fall divides by its
running peak while the rise divides by its running trough, and both are ratios of price rather than
logs. Small at these prices, asserted with a tolerance, and written down so nobody later reads the
asymmetry as a bug.

## 2. The entry band was silently widening the risk geometry

`stop=1.5` and `target_1=2.0` were measured from the **edge of the entry band**, which sits 0.1 ATR
from the anchor. So the configured 1.5 behaved as 1.6 and the configured 2.0 as 2.1.

Every break-even figure this project has published was therefore computed for multipliers nobody had
set — 43.2% rather than the 42.86% the configuration actually implied. The 9A report even noted the
1.60 and 2.09 readings and called them "arithmetic, not drift", which was true and missed the point:
the arithmetic meant the constants did not say what they meant.

Distances are now measured from the anchor. The band is an entry zone and nothing else, and a test
asserts that widening it eight-fold leaves the protective level and the target untouched.

## 3. A rule called "often firing" on 0.4% of the sample

`event_context.minutes_since_latest_event` was reported as `OFTEN_FIRES` over six months. The
underlying counts: **60 passed, 8 failed, 17,010 unavailable.** The verdict divided 8 by 68 and never
asked how often 68 was.

`RuleBehaviour` gains `RARELY_OBSERVED`, judged **before** the firing rate, when a rule could be
evaluated on less than 5% of windows. It counts as a finding, so `replay_rules.py` exits non-zero on
it exactly as it does for a rule that never fires — a rate computed over a handful of windows
describes the handful rather than the rule.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 115 source files |
| `uv run pytest` | Passed; 698 passed, 9 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

Ten new tests, including the defect itself stated as a passing observation — a steady climb really
does report a drawdown of zero — so the reason the symmetric field exists stays visible.

One test tripped the project's own Phase 3C term ban: a comment explaining the run-up used the words
for the two sides of a position, which context files may not contain. Reworded rather than exempted.

## The excursion bound, calibrated

Traded candles only, six months of EURUSD: 11,813 M15 and 2,770 H1 observations.

| | p50 | p75 | p90 | p95 | p97 | p99 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| M15 | 2.5832 | 3.3179 | 4.1463 | 4.6979 | 5.0903 | 5.7505 |
| H1 | 2.5598 | 3.3141 | 4.0850 | 4.4806 | 4.8364 | 5.5860 |

| bound | M15 fires | H1 fires | spread |
| ---: | ---: | ---: | ---: |
| 4.0 | 11.89% | 11.55% | 0.34 |
| 4.5 | 6.53% | 4.87% | 1.65 |
| **5.0** | **3.43%** | **2.56%** | **0.87** |
| 5.5 | 1.51% | 1.34% | 0.17 |

**5.0 is the only bound that satisfies both acceptance criteria with margin** — inside the 1–10%
corridor and under the one-point convergence criterion. Keeping 4.0 would have pushed the rule to
nearly 12%, which is what should be expected: the symmetric field is by construction never smaller
than the one-sided one it replaces.

Worth noting against the volatility band, which could not meet both criteria at any setting: this
field converges *better* than the one-sided drawdown did at the same percentiles. Taking the larger
of two measurements of the same window is less noisy than taking one of them and calling the other
side calm.

Verified after the edit: **3.43% and 2.56%**, matching the sweep exactly.

## The baseline, re-measured with the corrected geometry

The stop is now 1.5 ATR from the anchor rather than an effective 1.6, and the target 2.0 rather than
2.1. Break-even moves from 43.2% to **42.86%**.

| | windows | LONG target% | SHORT target% | ambiguous% | timeout% |
| --- | ---: | ---: | ---: | ---: | ---: |
| M15, old geometry (9A-6) | 11,974 | 38.88% | 44.90% | 0.63% | 13.60% |
| **M15, corrected** | 11,814 | **38.50%** | **44.38%** | 0.63% | 11.71% |
| H1, old geometry (9A-6) | 2,802 | 39.30% | 45.59% | 0.54% | 13.78% |
| **H1, corrected** | 2,771 | **39.06%** | **45.53%** | 0.62% | 12.41% |

The shares moved by a few tenths, as expected from a 6% change in both distances. Timeouts fell by
about 1.5 points, which is the arithmetic showing up honestly: both levels are nearer, so more windows
resolve inside the horizon.

Everything that mattered survived the correction. The two timeframes still agree — 0.56 points apart
on LONG and 1.15 on SHORT — and the sample's drift is still about six points in favour of SHORT (5.88
on M15, 6.47 on H1). **That drift is the period, not skill**, and it is the number a directional
candidate has to beat on its own windows.

One reading to be careful with: SHORT now sits *above* break-even on both timeframes, by 1.5 and 2.7
points. That is not an edge. It is a six-month downtrend measured gross of costs, available to
anybody who decided in advance to only ever sell.

## What this changes elsewhere

Nothing that has been concluded. The Phase 9A-3 retraction stands, no directional claim is affected,
and the Phase 9A-2 and 9A-6 baselines are superseded in the small, known way recorded above.
