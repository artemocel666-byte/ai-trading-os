# Phase 11-3 Verification Report — Lift the Loaders

Generated: 2026-08-30

`PROJECT_PHASE = "phase_11_3_reading_service"`

Pre-registered in [`docs/phase11-3-preregistration.md`](phase11-3-preregistration.md), committed
before any code (`79ecbc0`).

## The eight criteria

| | criterion | result |
| --- | --- | --- |
| 1 | **Identical output before and after** | **Pass** — all three, byte for byte |
| 2 | Exactly one place loads universe daily candles | **Pass** |
| 3 | Exactly one place derives daily returns | **Pass** |
| 4 | `replay_rules.py` excluded on purpose, not by oversight | **Pass** — recorded in a test |
| 5 | The service computes nothing | **Pass** — asserted against the parsed syntax |
| 6 | The service is route-ready | **Pass** — same |
| 7 | The suite stays green, no test weakened | **Pass** — 1003 passed, 9 skipped |
| 8 | No new behaviour, no new surface, no schema change | **Pass** |

## Criterion 1 is the one that decides the slice

A refactor whose output moves has changed something nobody asked it to. Three scripts were captured
before the change and re-run after it, with the one embedded timestamp masked:

```
report_market_state.txt   IDENTICAL
report_concentration.txt  IDENTICAL
page.html                 IDENTICAL
```

Run twice: once when the service landed, and again after `PROJECT_PHASE` was bumped, since a phase
constant that leaked into a rendered page would be exactly the kind of quiet difference this
criterion exists to catch. It does not leak. Both runs are identical to the baseline.

`profile_carry.py` and `profile_cross_section.py` were converted too. Their output is a measurement
over the whole history rather than a description of today, so both were re-run to completion and
checked against the figures their own phase reports recorded: 44 pairs with daily history over
2007-06-19 .. 2026-08-20, **226** rebalance dates for the cross-section, **229** anchors with 5
excluded for an incomplete rate cross-section for carry, and `does not clear` from both. Every one
matches 9D-2 and 9D-4.

## What was actually duplicated

Five scripts each held their own copy of this:

```python
candles = await uow.candles.list_range(pair=..., timeframe=Timeframe.D1, start_at=..., end_at=...)
real = [c for c in candles if c.provider in REAL_MARKET_DATA_PROVIDERS]
real.sort(key=lambda candle: candle.close_time)
```

Only the window differed, and a window is a parameter. A served page would have been the **sixth**
copy. The sixth copy of anything in this project has historically been the one that disagreed with
the other five — the half-added timeframe map that made `latest_closed_boundary` raise on D1, the
request-range limit read from two places, nine copies of `UnitOfWorkFactory`.

The service is 90 lines and holds three reads: daily candles, interest rates, positioning.

## The second duplication, which the pre-registration found and the code confirmed

Close-to-close daily returns, keyed by close time, were written out **identically** in
`report_concentration.py` and `render_market_page.py`. That is arithmetic on candles, not loading,
so it went to `app/domain/market_state.py` as `daily_returns` — beside the other pure functions that
take candles and give back numbers.

Putting it in the service would have hidden a computation inside the one module whose whole job is
not to compute. The distinction is not cosmetic: it is what criterion 5 checks.

## `replay_rules.py` calls the same repository method and stays out

It loads **one** pair on **any** timeframe with a **lead-in window**, so its oldest windows are not
artificially incomplete, and it loads economic events beside them. A service built for "the universe,
daily" would have to grow three optional parameters to swallow it, and each one would be a way for
the two questions to drift apart while sharing a name.

This is the same refusal as declining to reuse the 9C-3 decile machinery for a cross-section, and as
declining to merge the 10-2 and 11-2 vocabularies when they turned out to need different strictness.
A test records the exclusion, so it reads as a decision rather than as something missed.

## Criteria 5 and 6 had to be checked against syntax, not text

Both were first written as substring scans. Both failed — on the service's **own docstring**, which
names `argparse` and `print` in order to say it uses neither.

That is the fourth time in this project that a rule has been tripped by the sentence describing it:
a comment quoting the strings it had removed, a docstring quoting a banned word, `прогноз` inside
«а не прогноз». Each was fixed by narrowing precisely rather than by weakening the rule, and this
one is narrowed the furthest: the tests now parse the module and inspect imports, calls and binary
operators.

One exclusion is named there. `ast.BitOr` is not counted as arithmetic, because `datetime | None` in
a type annotation parses as one. A union is not a calculation.

## Two safety rules were amended, and the closed doors stayed closed

The rules that pinned interest rates (9D-3) and positioning (10-4) to a single reading path now name
the service as that path. What did **not** change: neither can reach Telegram, the API or the
scheduler. Those remain absolutely closed, and the tests that say so were not touched.

## One defect found in passing, and it is this project's own disease

`AGENTS.md` and `README.md` each state the current phase in prose. Both still read
`phase_9d3_interest_rate_ingestion` — **four phases behind**, through 9D-4, 10-1 to 10-4, 11-1 and
11-2. One concept written in three places, and the two written in prose had quietly stopped agreeing
with the one written in code, in exactly the two files a partner's agent opens first to learn where
the project stands.

Both corrected, and a ninth test now pins them to `constants.PROJECT_PHASE` so the next phase bump
cannot leave them behind. Historical phase reports are deliberately excluded from that check: each
records the phase it was written in, and freezing that is what they are for.

## Verification run

```
uv run ruff format .            clean
uv run ruff check .             All checks passed
uv run mypy app                 no issues in 145 source files
uv run pytest                   1003 passed, 9 skipped
uv run python scripts/security_check.py   exit 0
```

No test was adjusted to accommodate the move. The nine added tests are new.

## What this slice deliberately did not do

No route. No served page. No authentication decision. The service is now callable from one, and
whether it should be — and behind what — is Phase 11-4's question, not this one's.
