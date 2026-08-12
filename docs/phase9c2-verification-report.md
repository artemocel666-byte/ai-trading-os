# Phase 9C-2 Verification Report — Do the Rules Earn Their Place?

Generated: 2026-08-11

`PROJECT_PHASE = "phase_9c2_rule_value_foundation"`

Eleven rules decide whether a window is `READY_FOR_REVIEW`. Every calibration this project has run —
7D-2, 9A-6, 9A-8 — measured **how often each rule fires**. None measured whether firing helps.
`scripts/measure_outcomes.py` knew what happened after a window and nothing about the verdict;
`scripts/replay_rules.py` knew the verdict and nothing about what happened. The two halves have sat
side by side for eight phases.

## Only three rules are on trial

Of the eleven, **three make a claim about the market**:

| rule | severity | fires on |
| --- | --- | ---: |
| `market_context.volatility_ratio` | WARNING | 1.9–6.8% |
| `market_context.max_close_excursion_atr` | WARNING | 2.2–3.4% |
| `time_filter.session_name_allowed` | WARNING | ~40% |

The other eight are about our own plumbing — enough candles, candle age, market open, snapshot
built — or are dead, because the database holds zero events. All three market rules are WARNING, so
none of them ever blocks: they are the entire difference between `READY_FOR_REVIEW` and
`READY_WITH_WARNINGS`. **The pipeline's headline verdict is almost entirely a verdict about our data
quality.**

Windows are eligible for comparison only when every plumbing rule passed. That removes data quality
from the comparison rather than controlling for it afterwards, so the two groups a market rule is
judged on differ in exactly one thing: that rule's own verdict.

## What is measured, and why it is directionless

Both directions are pooled and aggregated with the existing `aggregate_outcomes`. A window where
LONG reached its target and one where SHORT did are both windows that **moved cleanly**, and that is
the only property a rule with no direction can plausibly select for. Pooling is what keeps a
directional claim from being readable out of this at all — asserted by a contract test.

No new statistic is invented: target-first share, timeout share and ambiguity are the same figures
as the 9A-7 baseline, so they can be compared directly.

## The asymmetry that makes a biased test worth running

The thresholds were fitted on this very history. The test is therefore biased **in favour of the
rules**: it can disconfirm and it cannot confirm.

- A rule that separates outcomes here has shown only that its own fit is self-consistent.
- A rule that fails to separate outcomes **on the data it was tuned on** has no case left.

EURUSD is where the thresholds were fitted; NOKSEK is where they were only checked in 9A-8. A rule
that helps on EURUSD and not on NOKSEK is fitting, not skill.

## Acceptance criteria — fixed before the run

A rule is shown to help only if all three hold:

1. pooled target-first share is **≥ 5 percentage points** higher on the windows it passed
2. the sign is the **same on all four series** — EURUSD M15/H1 and NOKSEK M15/H1
3. it holds on **NOKSEK**

Five points, against the 3-point bar 9A-3 used for a directional edge, raised because this test is
biased in favour of the rules and gross of costs. Four-series consistency is the same convergence
discipline 9A-6 and 9A-8 apply to thresholds.

**A null result is the expected outcome and a successful slice.**

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 119 source files |
| `uv run pytest` | Passed; 762 passed, 9 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

Thirteen new tests. The partitioning is tested on hand-built decisions rather than composer output,
so the test does not depend on today's thresholds: a rule that separates perfectly, a rule that
separates nothing, a window whose plumbing failed being excluded before any comparison, and an
`UNAVAILABLE` rule counting on neither side.

Two validators exist to stop a partitioning bug from reaching a report and looking like a finding:
pooled statistics must contain exactly twice the window count, and a report cannot claim more
eligible windows than it measured.

## The harness agrees with the published baseline

Run first, before anything was read. `scripts/measure_outcomes.py` over the same 180 days of EURUSD
M15 gives **LONG 38.67% / SHORT 44.24%** against the 38.50% / 44.38% published in 9A-7. The window
has slid three days forward since that report, which is the size of difference three days of new
data at one end and three dropped at the other should produce. Pooled 41.4% either way, and
`evaluate_rule_value.py` reports 41.39% over its eligible subset. The two paths agree.

## The result: all three rules fail, and it is not close

`target_first_edge` in percentage points — passed minus failed, both directions pooled:

| rule | EURUSD M15 | EURUSD H1 | NOKSEK M15 | NOKSEK H1 |
| --- | ---: | ---: | ---: | ---: |
| `market_context.volatility_ratio` | +2.41 | +0.44 | **−0.92** | +0.37 |
| `market_context.max_close_excursion_atr` | **−1.00** | **−1.67** | **−2.78** | +1.70 |
| `time_filter.session_name_allowed` | **−1.01** | +0.04 | **−0.16** | **−0.48** |

**Not one rule meets even the sign-consistency criterion, let alone the five-point bar.** The
largest magnitude anywhere in the table is 2.78 points and it is *negative*: on NOKSEK M15, windows
`max_close_excursion_atr` rejected reached a target **more** often than the ones it accepted.

Eligible populations were 11,589 / 2,701 / 11,638 / 2,702 windows — 98.4–98.9% of all measured
windows, so nothing here rests on a thin sample of the accepted side.

### `session_name_allowed` is cleanly disproved

It is the only one of the three with real statistical power: it splits the data roughly 60/40, so
each comparison rests on 1,000–4,700 windows *on the rejected side*. Its edges are −1.01, +0.04,
−0.16, −0.48. That is as close to nothing as data gets.

**Which session a window falls in does not predict whether it resolves.** The rule fires on ~40% of
windows, was flagged in the open questions as "the severity is the question, not the threshold", and
now has no measured value at either severity.

### The other two could barely have separated anything

`volatility_ratio` and `max_close_excursion_atr` were calibrated to fire on **1–10% of windows** —
that corridor is the acceptance criterion 7D-2 introduced and 9A-6 and 9A-8 upheld. A rule that
rejects 2–5% of windows cannot partition a population, whatever the field underneath it is worth.

So this is two findings, and the second is the larger:

1. These rules, at these thresholds, do not separate outcomes.
2. **They were never calibrated to.** The corridor optimises for *rarity*, and rarity was never
   connected to usefulness by anything but assumption. Every threshold in this project was tuned to
   a target that has now been measured and found unrelated to what happens next.

That reframes 9A-8's headline result too. `max_close_excursion_atr` transferring untouched across
instruments — 2.86%/2.19% against 3.43%/2.56% — was real, and it was a statement about **firing
rate consistency**, not about value. A threshold can be perfectly portable and still describe
nothing. Portability was worth establishing; it was never evidence of usefulness, and the report
should not have been read as if it were.

## One observation that is not a finding

`timeout_edge` for `volatility_ratio` is positive on all four series: +3.96, +4.84, +12.21, +6.50.
Windows the band accepted timed out less often than the ones it rejected, consistently, and on
NOKSEK M15 by twelve points.

**This was not the pre-registered metric and is not being claimed as a result.** Switching to the
metric that happened to look good after seeing the data is exactly the failure this project has
guarded against since 9A-3. It is recorded as a hypothesis for a future test with its own criteria
fixed in advance: *does the volatility band select windows that resolve at all, even though it does
not select windows that resolve to target?*

## What this does and does not settle

- **It settles that the three market-facing rules do not select windows that resolve to target
  more often.** The test was biased in their favour — the thresholds were fitted on this history —
  and they failed anyway. That is the disconfirming direction, and it is conclusive.
- **It settles that "fires on 1–10% of windows" was the wrong calibration target**, or at least an
  unexamined one.
- **It does not condemn the data-quality rules.** They are excluded by design: they judge our
  ingestion, not the market, and 98.7% of windows pass them.
- **It does not say the underlying fields are worthless.** Volatility as a continuous quantity may
  separate outcomes even though a binary cut that accepts 98% of windows does not. Sweeping the
  threshold against outcomes rather than against firing rate is the obvious next test.
- **It has a direct product consequence.** The "context rather than advice" reframe rests on being
  able to tell a person what usually follows windows like this one. On this evidence the rules do
  not define a "like this one" that predicts anything, so base rates conditioned on the pipeline's
  verdict would be flat. There would be nothing to say.

## Explicitly not in this slice

- **No threshold changes.** If a rule is shown not to help, retiring it or changing its severity is
  a separate decision with its own evidence. This slice measures; it does not act.
- **No direction.** Pooling is structural, not incidental.
- **Nothing user-facing.** Presenting base rates to a person as context is the slice after this one,
  and only for whatever survives.
