# Phase 11-3 Pre-registration — Lift the Loaders

Written: 2026-08-25. **Committed before any code**, as 10-1 established.

## Context

Every descriptive script opens its own database connection and writes its own `_load`. That was
right while each was a one-off measurement. It stops being right at the route: a served page would
be the **sixth** copy, and the sixth copy of anything in this project has historically been the one
that disagreed with the other five.

This slice is a refactor. **Nothing it produces should look different afterwards**, which is what
makes its acceptance criteria unusual: they are about output *not* changing.

## Checked before planning — three findings

**1. Five scripts load universe daily candles, and the loading half is the same thing.**
`profile_cross_section.py`, `profile_carry.py`, `report_market_state.py`,
`report_concentration.py` and `render_market_page.py` each run the same query with the same
provider filter and the same sort:

```python
candles = await uow.candles.list_range(pair=..., timeframe=Timeframe.D1, start_at=..., end_at=...)
real = [c for c in candles if c.provider in REAL_MARKET_DATA_PROVIDERS]
real.sort(key=lambda candle: candle.close_time)
```

Only `start_at` differs, and a window is a parameter rather than a difference in kind.

**2. `replay_rules.py` also calls `candles.list_range`, and is deliberately left alone.** It loads
**one** pair on **any** timeframe with a **lead-in window** so the oldest windows are not
artificially incomplete, and it loads economic events beside them. That is a different question
wearing a similar call, and merging it would be forcing unlike things together — the mistake this
project has avoided by refusing to reuse the 9C-3 decile machinery for a cross-section.

**3. A second duplication nobody has named.** Daily close-to-close returns, keyed by close time, are
derived **identically** in `report_concentration.py` and `render_market_page.py`. That is arithmetic
on candles, not loading, so it belongs in the **domain** rather than in the service — putting it in
the service would hide a computation inside something whose whole job is not to compute.

## Design

**One service, three reads, no arithmetic.** Universe daily candles, interest rates, positioning.
It opens the connection, runs the queries, filters by provider, sorts, and returns entities. It
computes nothing — a service that quietly derives is how a number ends up with two definitions.

**The returns derivation goes to the domain**, beside the other pure functions that already take
candles and give back numbers.

**Scripts keep their own argument parsing and printing.** The service takes plain arguments and
returns plain data: no `argparse.Namespace`, no `print`. That is what makes it callable from a route
without a sixth rewrite, and it is checkable rather than aspirational.

## Acceptance criteria — fixed here, before the code

1. **Every affected script produces identical output before and after**, compared against captured
   runs. For the rendered page, identical after masking the one timestamp it embeds. This is the
   criterion that decides the slice: for a refactor, anything else is a rewrite in disguise.
2. **Exactly one place loads universe daily candles.** A test finds `candles.list_range` for `D1`
   in the service and nowhere else in `scripts/`.
3. **Exactly one place derives daily returns**, asserted the same way.
4. **`replay_rules.py` is untouched**, and a test records that its loader is excluded on purpose
   rather than overlooked.
5. **The service computes nothing.** Its module imports no domain calculation, and a test asserts
   the absence.
6. **The service is route-ready**: no `argparse`, no `print`, no `sys.exit` anywhere in it.
7. **The full suite stays green**, and no test is weakened to accommodate the move.
8. **No new behaviour, no new surface, no schema change.**

If criterion 1 cannot be demonstrated, the slice is not done — a refactor that changes output has
changed something nobody asked it to.

## Changes

1. `app/services/market_reading_service.py` — new: three reads, no arithmetic.
2. `app/domain/market_state.py` — the returns derivation, once.
3. The five scripts call the service and lose their `_load` functions.
4. Tests, including the one-place assertions and the exclusion note for `replay_rules.py`.
5. `docs/phase11-3-verification-report.md`, AGENTS.md, PLANS.md, README.md, operations.md, Notion.

## Explicitly not in this slice

- **No route.** That is 11-4, and it is the reason this exists rather than the same step.
- **No change to `replay_rules.py`**, for the reason above.
- **No new readings, no new data, no forecast.**
- **No schema change and no migration.**
