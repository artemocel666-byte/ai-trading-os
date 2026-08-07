# Phase 9A-4 Verification Report — The Market-Open Gate

Generated: 2026-08-07

`PROJECT_PHASE = "phase_9a4_market_open_gate_foundation"`

A remediation slice, not a new capability. It is the first item from the full project review of
2026-08-07, and it exists because of the worst finding in that review.

## The finding

The project already knew. Since Phase 7C the rule registry has held this:

```python
rule_id="time_filter.utc_weekday",
severity=StrategyRuleSeverity.WARNING,
description="The window ends on a weekday; at the weekend the currency
             market is closed and quotes are stale."
```

Over six months of EURUSD it failed on **28.08% of windows** — 4,795 of 17,078 — and that number was
printed in every replay since 2026-08-01. It matches, to a tenth of a point, the share of stored
candles that fall on a weekend and are carried-forward filler.

It changed nothing, because of this:

```python
warning_failure_count = _failure_count(results, StrategyRuleSeverity.WARNING)  # computed
...
status=_status_for(blocking_failure_count, required_failure_count)            # and dropped
```

`_status_for` never received it. A severity that cannot change any output is not a severity, it is a
comment. Every weekend window came out `READY_FOR_REVIEW` and fed the Phase 7C threshold calibration,
the Phase 9A-2 baseline, and the Phase 9A-3 readiness gate — whose verdict was retracted for exactly
this contamination, hours before this slice was written.

The failure mode is worth naming, because it is not a bug in a formula: **the system observed the
problem, reported it correctly, and had no path from observing to acting.**

## Two changes

### 1. Closed market is a data-quality fact, not a time preference

New `app/domain/market_calendar.py` with `is_market_open`, a new resolver
`data_quality.market_open`, and a **REQUIRED** rule in the data-quality ruleset. The old
`time_filter.utc_weekday` rule is retired; its resolver stays for its distribution.

The move matters as much as the severity. "The market was shut" belongs beside "candles are missing",
not beside "the window ends in a nice liquidity session". One is about whether the data means
anything; the other is about preference.

The resolver returns a boolean and **never `None`**. The moment is always known, so "the market was
shut" is an observation. Returning `None` would make the rule `UNAVAILABLE` rather than failed — the
precise mechanism by which the Phase 7D-2 session rule sat silent for six months.

Deliberately blunt: the whole of Saturday and Sunday, including the genuine Sunday-evening reopen.
The real boundary drifts with daylight saving and differs by venue, and this project has no venue
specification to read one from.

### 2. `READY_WITH_WARNINGS`

A fourth status on both `RuleSetEvaluationStatus` and `PipelineDecisionStatus`, with
`warned_ruleset_count` on the decision report and validators tying counts to status the way the
existing ones do. The headline can no longer say all is well while failures are listed underneath it.

**An unavailable warning is silence, not a finding.** This is the subtlety that nearly broke the
change: `_failure_count` counted `UNAVAILABLE` as failure, and
`event_context.minutes_since_latest_event` is unavailable in 99.6% of windows because the calendar
holds no real events. Counting it would have made every window in the project permanently warned and
the new status worthless. Warnings now count only `FAILED`; the two mandatory tiers still fail closed
on an unresolvable field, because a mandatory condition nobody could check has not been satisfied.
`unavailable_count` is recorded separately so nothing is lost.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 115 source files |
| `uv run pytest` | Passed; 679 passed, 9 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

Eight existing tests failed on the first run, every one of them asserting the old behaviour — a
warning producing `READY_FOR_REVIEW`, a data-quality ruleset of four rules, a time filter of two.
That is the correct signal: the tests had encoded the defect faithfully.

### Over six months of real history

```text
M15  17,082 windows   ready=54,210  warned=8,826  not_ready=5,285  blocked=7
H1    4,276 windows   ready=13,575  warned=2,210  not_ready=1,312  blocked=7

data_quality.market_open   REQUIRED   passed 12,287  failed 4,795   28.07%   (M15)
data_quality.market_open   REQUIRED   passed  3,079  failed 1,197   27.99%   (H1)
```

The same 28% the old warning found, now producing `NOT_READY` instead of nothing. The two timeframes
agree to within a tenth of a point, which is what a calendar-driven effect should look like.

Nothing else moved: `volatility_ratio` still fires on 5.70% and 5.66%, `max_close_drawdown_atr` on
5.51% and 4.89%. The gate changed which windows are trusted, not what the other rules measure.

## What this does not fix

- **The thresholds are still calibrated on contaminated data.** 7C was re-derived in 7D-2 over a
  sample that was 28% filler, and the 9A-2 baseline with it. Those numbers should be re-measured now
  that the pipeline can tell the difference. That is the next item on the review list, not this one.
- **The database still holds the filler.** The gate refuses to trust it rather than deleting it,
  which is the right order — deleting candles would splice Friday onto Monday and invent an adjacency
  that never existed. Any analysis that walks stored candles directly must still exclude weekends
  itself; `scripts/replay_rules.py` keeps `touches_closed_market` for that, now delegating to the
  domain.
- **Two test stubs and four stray GBPUSD candles remain in the database** from earlier verification
  runs, and they participate in calibration. Also on the review list.
- **Seven rules are still warnings**, and now that warnings are visible, `session_name_allowed` firing
  on 41.6% of windows means most trading windows will report `READY_WITH_WARNINGS`. That is honest
  rather than useful; whether a session filter deserves to be a warning at all is a separate
  question, and it should be answered with evidence rather than by adjusting it to feel better.
