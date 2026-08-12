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

## The measurement itself — outstanding

**Not yet run.** The Docker engine stopped before the four series could be measured, and this
section is left named rather than quietly absent. Required:

```
scripts/evaluate_rule_value.py --pair EURUSD --timeframe M15 --days 180 --exclude-closed-market
scripts/evaluate_rule_value.py --pair EURUSD --timeframe H1  --days 180 --exclude-closed-market
scripts/evaluate_rule_value.py --pair NOKSEK --timeframe M15 --days 180 --exclude-closed-market
scripts/evaluate_rule_value.py --pair NOKSEK --timeframe H1  --days 180 --exclude-closed-market
```

Before reading any of it: the pooled figures over EURUSD M15 must reproduce the 9A-7 baseline
(LONG 38.50% / SHORT 44.38%, pooled 41.4%). If they do not, the harness disagrees with the published
baseline and that is the first thing to fix — not the rules.

## Explicitly not in this slice

- **No threshold changes.** If a rule is shown not to help, retiring it or changing its severity is
  a separate decision with its own evidence. This slice measures; it does not act.
- **No direction.** Pooling is structural, not incidental.
- **Nothing user-facing.** Presenting base rates to a person as context is the slice after this one,
  and only for whatever survives.
