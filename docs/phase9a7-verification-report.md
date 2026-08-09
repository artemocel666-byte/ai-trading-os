# Phase 9A-7 Verification Report — Three Measurement Gaps

Generated: 2026-08-08

`PROJECT_PHASE = "phase_9a7_measurement_gaps_foundation"`

The fourth remediation item. None of these was a crash or a failing test — each was a number that
quietly meant something other than what it was read as, which is the harder kind to notice.

**This slice is partial by necessity.** Two of the three fixes need a calibration run to finish, and
the Docker engine stopped mid-session. What is committed is correct and tested; what is outstanding
is named at the end rather than left to be discovered.

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

## What is outstanding, and why

**The rule still reads the one-sided field.** `market_context.max_close_excursion_atr` exists and is
measured; the warning rule still points at `max_close_drawdown_atr`, because swapping it needs a
threshold derived from the new field's distribution, and the symmetric field is by construction never
smaller than the drawdown — so 4.0 would fire more often than the 5.98% it was calibrated for. The
field was added without moving the rule on purpose: **a threshold moves only through a deliberate
edit that records its evidence**, and the evidence needs a database that is currently unavailable.

**The baselines were measured with the old geometry.** Phase 9A-2 and its 9A-6 re-measurement both
ran with the stop at 1.6 ATR and the target at 2.1. With the fix they are 1.5 and 2.0, break-even
moves from 43.2% to 42.86%, and every outcome share shifts slightly. The numbers in those reports are
now stale in a small, known way, and should be re-run rather than adjusted on paper.

Both are one calibration run away. Neither changes a conclusion that has been drawn: the 9A-3
retraction stands, and no directional claim is affected.
