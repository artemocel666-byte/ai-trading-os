# Phase 10-4 Pre-registration — Positioning

Written: 2026-08-22. **Committed before any code**, as 10-1 established.

## Context

Every reading this project produces describes **what the price did**. Positioning is the one
obtainable source that describes **what participants hold** — a different kind of fact, and the last
one on the shortlist drawn up after 9D-4.

Its value here is descriptive. As a *predictor* it would almost certainly be the eighth null: the
documented effects are the same order of magnitude as carry, and the resolution arithmetic from
9D-4 applies unchanged. **This slice does not measure whether positioning predicts anything, and the
report may not imply that it does.**

## Checked before planning — four findings, and the second decides the slice

The CFTC publishes the Commitments of Traders report through a public Socrata endpoint,
**free and without a key**, 133 fields per row including `noncomm_positions_long_all`,
`noncomm_positions_short_all` and `open_interest_all`.

**1. Eight of our ten currencies are covered**, all current as of the 2026-08-18 report:

| currency | contract | |
| --- | --- | --- |
| EUR | EURO FX — CME | ✓ |
| JPY | JAPANESE YEN — CME | ✓ |
| GBP | BRITISH POUND — CME | ✓ |
| CHF | SWISS FRANC — CME | ✓ |
| CAD | CANADIAN DOLLAR — CME | ✓ |
| AUD | AUSTRALIAN DOLLAR — CME | ✓ |
| NZD | NZ DOLLAR — CME | ✓ |
| USD | USD INDEX — ICE | ✓ *(see finding 3)* |
| **NOK** | — | **no contract** |
| **SEK** | SWEDISH KRONA/DMARK — NY Cotton Exchange | **dead since 1998** |

**2. The contract names changed, and a mapping built from today's names would silently lose years.**

```
NZ DOLLAR             latest 2026-08-18
NEW ZEALAND DOLLAR    latest 2022-02-01
USD INDEX             latest 2026-08-18
U.S. DOLLAR INDEX     latest 2022-02-01
```

Both series were renamed in early 2022. Mapping by the current name alone yields NZD and USD history
**starting in February 2022** while the other six run for decades — and the report would look
entirely healthy while two of its eight series were holed. This is the same shape as the 9D-1 fault
where a half-added timeframe produced a wrong answer that looked like a real one, and it is the
reason this check exists.

**3. The dollar entry is an index, not a bilateral rate.** USD INDEX positioning is against a
basket, mostly the euro. "Speculators are net long the euro against the dollar" and "speculators are
net long a dollar basket" are different observations, and putting them in one column would compare
unlike things.

**4. The data is never "now".** The report describes **Tuesday** and is published **Friday
afternoon**, so it is three days old on arrival and up to ten before the next one. A product line
saying "участники держат" implies the present tense and would be wrong by default.

## Design

**Stored faithfully, with the report date as the anchor** — the 9D-3 rule. The row records the
Tuesday the positions describe, not the day we fetched it. How stale a reading may be before it is
worth showing is a presentation choice and stays out of the table.

**Mapped by contract code as well as name.** Finding 2 makes name-only mapping unsafe, so each
currency carries the set of names it has been published under, and the backfill reports the earliest
and latest date per currency so a truncated series is visible immediately rather than later.

**Normalised by open interest.** Raw contract counts are not comparable between currencies or across
decades. Net speculative position as a share of open interest is.

**Per-currency facts do not need the whole universe — but a ranking does.** This is a refinement of
the all-or-nothing rule from 9D-4 and 10-3, not an exception to it. "Speculators are net long the
euro at the 92nd percentile of their own history" stands alone and is unaffected by NOK having no
contract. **Any table that ranks currencies against each other must state which two are not in it**,
because a ranking silently missing members answers a different question.

**Percentile against its own history**, through `read_against_history` and therefore through
`nearest_rank` — the existing definitions, not new ones.

## Acceptance criteria — fixed here, before the code

1. **Eight currencies stored; NOK and SEK named as uncovered**, never as zero positioning.
2. **The rename is handled**: NZD and USD history reaches back before February 2022, demonstrated
   against the stored data. If either series starts in 2022 the mapping is wrong and the slice is
   not done.
3. **Every reading carries the Tuesday it describes**, and the report states how many days old that
   is at the moment of reading.
4. **The dollar index is labelled as a basket**, in the output, wherever it appears beside bilateral
   currencies.
5. **Positioning is expressed as a share of open interest**, and a row whose open interest is zero or
   missing yields an absence rather than a division.
6. **Percentiles come from the existing machinery** — the one-concept test gains no new percentile
   definition, and would fail if one appeared.
7. **A live fetch and store**, with coverage read before anything else: earliest and latest date per
   currency, and gaps named.
8. **No claim that positioning predicts anything**, and nothing new reaches Telegram or the API.

If criterion 2 cannot be demonstrated, the slice is not done: a series quietly starting in 2022
would make every percentile in the report a percentile of the wrong history.

## Changes

1. `app/domain/entities/positioning.py` — new: the stored reading, currency, report date, net share.
2. `app/adapters/cftc_positioning.py` — new: the Socrata fetch and the name-and-code mapping.
3. `migrations/versions/0006_…` — one table, unique on `(currency, report_date)`, drops nothing.
4. `app/persistence/` — model, repository, UoW slot, exports.
5. `scripts/backfill_positioning.py` — new; coverage reported before storing, as in 9D-3.
6. `app/presentation/readings.py` — rendering, in the one renderer module.
7. `scripts/report_market_state.py` — a positioning section, with the staleness stated.
8. Tests, including all eight criteria; a safety block keeping positioning out of user-facing layers.
9. `docs/phase10-4-verification-report.md`, AGENTS.md, PLANS.md, README.md, operations.md, Notion.

## Explicitly not in this slice

- **No measurement of whether positioning predicts returns.** That is a separate pre-registered
  question and, on the resolution arithmetic from 9D-4, one this design could not answer.
- **No "extreme positioning" language.** "Extreme" is a claim about what should happen next dressed
  as a description, exactly like `перекуплен` in 10-2. A percentile is the honest form.
- **No new user-facing surface**, and no forecast anywhere.
- **No scheduled job in this slice.** The data moves weekly; scheduling it belongs with the other
  scheduled fetches once the shape is settled.
