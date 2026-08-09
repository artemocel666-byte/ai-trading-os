# Phase 9A Verification Report

Generated: 2026-08-05

## Scope

Phase 9A builds the price levels deferred since Phase 4: entry band, protective level, and targets.
It is the first module allowed to compute them — the `calculate_entry`/`calculate_stop`/
`calculate_target` term ban has stood since Phase 4 and is lifted here and nowhere else.

`PROJECT_PHASE = "phase_9a_price_plan_foundation"`

## The slice was scoped down during planning, for a reason

The roadmap said 9A would "assemble a `SignalContract` from a `PipelineDecisionReport`". That is not
possible. `SignalContract` requires `direction`; `PipelineDecisionReport` has no directional field,
because all eleven rules are descriptive by design — "can this window be trusted", "what regime is
this". Nothing in this project decides up or down.

The same review found `PLANS.md` still listing "No strategy logic" and "No indicators or signal
generation" under Explicit Non-Goals, directly contradicting Phase 9. Those entries were written
when the project was foundation-only and had gone stale; they are corrected in this slice.

Decision taken with the user: **9A builds the level machinery with direction as an input.** Where a
direction could come from is a separate question, and it now blocks 9B.

## Implementation

`app/domain/signal_price_plan.py`, pure domain, wired to nothing:

- `build_price_plan(direction, snapshot, *, multipliers)` — the anchor is the latest close, and each
  level sits a multiple of the window's average true range away from it.
- `build_draft_contract(...)` — wraps the plan in a `SignalContract` that is `DRAFT`,
  `NOT_ACTIONABLE`, and carries `risk_plan=None`. Position size needs an account balance the project
  does not have and will not invent. A decision that is not `READY_FOR_REVIEW` is recorded as a
  warning, so a plan built over an untrustworthy window says so on its face.
- `None` rather than a fabricated plan when the snapshot, the close, or the ATR is missing or zero —
  a flat window has no scale to place levels on.

**Distances are ATR multiples, not prices.** A protective level twenty pips away is tight on one
instrument and absurd on another; one placed 1.5 average candle ranges away means the same thing
anywhere. This is the drawdown-normalisation lesson applied where it matters most.

## The multipliers are conventions, not calibrations

Stated plainly because it matters: `entry_band=0.10`, `stop=1.5`, `target_1=2.0`, `target_2=3.0` are
conventional defaults. **No evidence in this project supports them.**

Every other threshold here was derived from an observed distribution. These could not be, because
judging a protective distance requires knowing whether that level or the target was reached first —
and nothing in this project measures what happened *after* a window. `HistoricalReplay` walks
windows and evaluates rules; it scores no outcomes.

The one property that can be asserted without knowing the future is the ratio: `target_1` is never
closer than `stop`, enforced in `LevelMultipliers.__post_init__` and covered by a test, so a plan
never seeks less than it risks.

## The boundary that replaces the term ban

Lifting a ban is only acceptable if something stricter replaces it. Three invariants were added:

**The term ban became real.** Until now `calculate_entry` and friends appeared only in per-phase file
lists, so a brand new file anywhere could have defined one and nothing would have failed. This slice
scans every module in `app/` and exempts exactly one file. The exempted module contains none of those
names either — the levels are built without a function called `calculate_entry` — so the guard is
about the future, not the present.

**No function anywhere returns a `SignalDirection`.** A strategy has to hand a direction back to
someone, so a function annotated as returning one is its mechanical signature. The test walks the AST
of every module in `app/` and asserts none exists. 9A takes direction as an argument and never
produces it; the day this test fails, somebody is adding a strategy and is made to notice.

**Nothing is wired.** No service, command, route, or job references the module, and it imports no
persistence, adapter, Telegram, API, or scheduler code.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 109 source files |
| `uv run pytest` | Passed; 625 passed, 7 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

### Levels over real stored candles

`EURUSD`, `as_of` 2026-07-29 11:30Z, both directions on both timeframes:

```text
===== EURUSD M15 =====        anchor 1.13861   ATR 0.00038750   status READY_FOR_REVIEW
  LONG    entry 1.13857 .. 1.13865   stop 1.13799 (1.60 ATR)   target1 1.13942 (2.09 ATR)
  SHORT   entry 1.13857 .. 1.13865   stop 1.13969 (1.60 ATR)   target1 1.13699 (2.09 ATR)

===== EURUSD H1 =====         anchor 1.13852   ATR 0.00073167   status READY_FOR_REVIEW
  LONG    entry 1.13845 .. 1.13859   stop 1.13735 (1.60 ATR)   target1 1.14005 (2.09 ATR)
  SHORT   entry 1.13845 .. 1.13859   stop 1.13969 (1.60 ATR)   target1 1.13699 (2.09 ATR)
```

Reward-to-risk is 1.31 in every case, and every contract reports `NOT_ACTIONABLE`, `DRAFT`, and
`risk_plan = None`. The distances measured from the entry midpoint are 1.60 and 2.09 ATR rather than
the configured 1.5 and 2.0 because the entry band adds its own 0.1 ATR on each side — arithmetic, not
drift.

> **Corrected 2026-08-08 (Phase 9A-7).** That paragraph was true and missed the point: the arithmetic
> meant the constants did not say what they meant, and every break-even figure the project published
> was computed for multipliers nobody had configured. Distances are now measured from the anchor, so
> 1.5 is 1.5 and reward-to-risk is 1.33. See `docs/phase9a7-verification-report.md`.

### A defect the synthetic tests missed

The first live run produced levels like `1.1385712500` — ten decimals, which no venue would accept.

Rounding was taken from the anchor's own exponent, and PostgreSQL returns `1.1385200000` for a price
quoted as `1.13852`: the *storage* precision, not the instrument's. Unit tests built candles as
`Decimal("1.10000")` and so never saw it.

Fixed by stripping trailing zeros before reading the precision, plus a regression test built from
database-shaped values that would have caught it. The heuristic has one visible edge, documented in
the code: a close genuinely ending in zero reads as one decimal fewer, making that window's levels
one digit coarser. A real tick size belongs to an instrument specification the project does not have.

### Unit coverage

Sixteen tests: LONG and SHORT geometry against the Phase 4A validator, distances as exact ATR
multiples, invariance when the whole series is scaled three-fold, the reward-to-risk property,
quantisation on five- and three-decimal instruments, the storage-precision regression, four
unavailability cases, the warning on an untrustworthy window, and the multiplier guards.

## Remaining risks / notes

- **The multipliers have no evidence.** Repeated here because it is the most important sentence in
  this report. They are placeholders that look like decisions.
- **Outcome measurement is the missing capability**, and it blocks two things at once: calibrating
  these multipliers, and showing that any future direction beats a coin toss. Concretely: for each
  historical window, walk forward and record whether the protective level or the target was reached
  first. The replay already walks windows; it needs to look forward instead of only backward.
- The entry band is symmetric around the last close, which assumes entry at roughly the current
  price. A plan that waits for a pullback would place the band elsewhere — a strategy decision, not a
  levels decision.
- Nothing here has been shown to a user, and cannot be: the module is unwired and the contract is
  permanently non-actionable.
