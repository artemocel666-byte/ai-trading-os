# Phase 9C-3 Verification Report — The Field Against the Outcome

Generated: 2026-08-11

`PROJECT_PHASE = "phase_9c3_field_outcome_profile_foundation"`

Phase 9C-2 showed the three market-facing rules separate nothing, and that two of them could barely
have: calibrated to fire on 1–10% of windows, a cut accepting 98% of a population cannot partition
it. That left the field itself untested. A band at 0.30/2.5 might be discarding information
`volatility_ratio` actually carries.

## Not a threshold sweep

Sweeping cuts and keeping the best is fitting, and 9A-3 already showed what that costs. Windows are
bucketed by **decile**, boundaries supplied by the sample, and the whole profile is printed rather
than a winning point. Buckets are equal in window count rather than in value range, so the ten
shares are comparable.

Two readings, both fixed before the run, because the rule under examination assumes a U-shape that a
monotone reading would miss:

- **gradient** — top decile against bottom
- **band** — the two extreme deciles against the middle eight

A field passes if either reading shows **≥5 п.п.** on target-first share, with the **same sign on all
four series**, holding on **NOKSEK** where nothing was ever fitted.

The harness agrees with 9C-2 before anything was read: pooled target-first on EURUSD M15 is 41.42%
against 41.39% there, the difference being that 9C-2 restricted to windows whose plumbing rules
passed.

## The pre-registered result: nothing, on all four fields

`target_first_edge` in percentage points, gradient / band:

| field | EURUSD M15 | EURUSD H1 | NOKSEK M15 | NOKSEK H1 |
| --- | ---: | ---: | ---: | ---: |
| `volatility_ratio` | +1.68 / +0.11 | +1.03 / −0.13 | +1.01 / −0.41 | −0.36 / +0.19 |
| `max_close_excursion_atr` | +1.65 / +0.81 | −1.45 / −1.35 | +2.79 / +1.31 | −3.81 / −1.19 |
| `max_close_drawdown_atr` | +0.54 / +0.07 | −3.01 / −0.17 | −0.14 / +0.22 | −1.85 / −1.05 |
| `move_efficiency` | +0.35 / −0.19 | −0.17 / −1.35 | +0.30 / −0.02 | +0.33 / −0.46 |

**Every one of the thirty-two numbers is under four points, and the signs flip between series.** The
largest magnitude, −3.81, sits opposite a +1.65 on the same field on another series. This is what no
relationship looks like.

`move_efficiency` deserves its own line: built in Phase 9A-3, read by no rule, never measured
against outcomes until now. Its four gradients are +0.35, −0.17, +0.30, +0.33 — the flattest field
in the table. **The 9A-3 candidate was built on the sign of this field's underlying sum, and the
magnitude carries nothing.** That is consistent with the retraction and independent of it.

**This test was not biased in favour of anything.** Unlike 9C-2, no threshold was fitted to produce
these buckets. The null is therefore stronger: it is not "these cuts fail", it is "these fields do
not order the outcome".

## What did move, and why it does not pay

`volatility_ratio` predicts **timeouts** with a clean, near-monotone gradient on every series:

| series | decile 1 timeout | decile 10 timeout | spread |
| --- | ---: | ---: | ---: |
| EURUSD M15 | 23.01% | 6.19% | 16.8 |
| EURUSD H1 | 20.18% | 5.07% | 15.1 |
| NOKSEK M15 | 25.74% | 6.71% | 19.0 |
| NOKSEK H1 | 21.61% | 5.29% | 16.3 |

Same direction, comparable magnitude, four series, two instruments, and the decline is ordered
across nearly all ten buckets in each. That is a real relationship, three times the size of the bar
set for target share.

The mechanism is not an artefact. `volatility_ratio` is the **latest** candle's true range over the
window's **average** true range ([strategy_field_resolver.py:112](app/domain/strategy_field_resolver.py:112)),
and the levels are placed from the average — numerator and denominator are different quantities. A
large recent candle predicting continued movement is volatility clustering, one of the most robust
facts about price series. Our data reproduces it, which is a good sign about the harness.

**And it does not pay.** In the same deciles, target-first share barely moves:

| series | decile 1 target | decile 10 target |
| --- | ---: | ---: |
| EURUSD M15 | 40.41% | 42.09% |
| EURUSD H1 | 41.91% | 42.94% |
| NOKSEK M15 | 40.39% | 41.40% |
| NOKSEK H1 | 41.59% | 41.23% |

Break-even is 42.86%. A high-volatility window resolves *sooner*, and resolves to the protective
level just as readily as to the target. **Resolving faster at a coin-flip hit rate is not an
advantage — it is the same wager settled more often, and every settlement pays a spread.** Gross of
costs it is neutral; net of costs it is worse.

### The discipline is what made this legible

This is the second time the timeout figures have looked like the interesting number — they were
recorded in the 9C-2 report as a named hypothesis, before this run, precisely so that noticing them
again would not be mistaken for discovering them.

Fixing the metric first is what makes the reading obvious now. Had the metric been chosen after the
data, the sixteen-point spread would have been the headline and the flat target share a footnote.
The pre-registration did not merely prevent a false claim; it identified which of two real numbers
is the one that matters.

**The timeout relationship is still not a confirmed finding.** Its criteria were never fixed in
advance. What it has earned is a test of its own, with a question that has to be answered first:
*what would knowing it be worth?* A measure that predicts motion without predicting direction has no
obvious use in a project with no direction.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 121 source files |
| `uv run pytest` | Passed; 778 passed, 9 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |
| pooled target-first against 9C-2 | 41.42% vs 41.39%, difference explained |

Sixteen runs: four fields across four series, 180 days, traded candles only.

Sixteen new tests. The two readings are tested against fabricated data where the answer is known: a
monotone relationship shows in the gradient; **a U-shape is invisible to the gradient and caught by
the band**, which is the entire reason both exist. Also: deciles hold equal window counts, an
unavailable value is counted apart rather than bucketed as zero, and arrival order does not change
the profile.

One contract test was rewritten during the slice. It banned the word "threshold" in the module
source, and failed on the sentence *"Nothing here chooses a threshold."* Banning a word forbids
explaining its absence; the test now asserts the function's signature accepts no cut to fit.

## What this settles

- **The four descriptive fields do not order the outcome.** Not through the rules' cuts, and not
  through any cut: the deciles are flat across the whole range. This closes a larger question than
  9C-2 did, and closes it without the in-sample caveat.
- **`move_efficiency` carries nothing**, measured for the first time.
- **`volatility_ratio` predicts whether a window resolves**, strongly and portably — and that is
  motion, not direction, and motion is not profit.
- **It does not say the project's data is worthless.** It says these four summary statistics of a
  twelve-candle window do not predict what the next twenty-four candles do. Twelve candles is a
  three-hour view on M15; it would be surprising if that were enough.

## What it means for the product

The "context rather than advice" reframe rested on telling a person what usually follows a window
like theirs. After 9C-2 that was doubtful; after this it is settled for these fields: **there is no
"window like theirs" that predicts what comes next.**

One honest sentence survives, and it is the timeout finding: *this window is unusually quiet — in
six months, a quarter of windows this quiet resolved nothing within six hours, against one in
sixteen of the most active.* True, measured, portable across two instruments — and useful only to
someone who already knows what they intend to do.
