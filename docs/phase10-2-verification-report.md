# Phase 10-2 Verification Report — The Honesty Policy, Made Executable

Generated: 2026-08-22

`PROJECT_PHASE = "phase_10_2_market_state"`

Pre-registered in [`docs/phase10-2-preregistration.md`](phase10-2-preregistration.md), committed
before any code (`a637e2d`).

## The eight criteria

| | criterion | result |
| --- | --- | --- |
| 1 | A central tendency cannot be rendered alone | **Pass** — one renderer, enforced by a source scan |
| 2 | Every rendered distribution carries `n` | **Pass** — asserted on the rendered text |
| 3 | No vocabulary of expectation, matched by whole word | **Pass** |
| 4 | `/review` shows no aggregate rule score, and states the 9C-2 null | **Pass** |
| 5 | The decomposition separates the pair from the currency | **Pass** — hand-built case, and live |
| 6 | Percentiles come from `nearest_rank` | **Pass** — one-concept test gained three entries |
| 7 | A live run over the current universe | **Pass** — 44 pairs, plumbing read first |
| 8 | Nothing new reaches Telegram or the API | **Pass** — the only change there is a removal |

## The plumbing check changed the design

**The honesty type already half-existed.** `FieldDistribution` has refused to *hold* a lonely central
tendency since Phase 4 — its validator reads *an observed field must report every percentile*. What
was missing is that nothing stopped a formatter from holding a complete distribution and printing
only its middle. **The data obeyed the rule; the rendering did not.**

So the slice became narrower and sharper than planned: not build a type, but close the gap between
the type and the text. One function renders a distribution, always emitting the sample size, the
spread and the middle together, and a source scan keeps a second one from appearing.

`nearest_rank` was likewise already the single definition of a percentile, with a docstring
recording that it was made public, reverted the same day, and made public again only when a second
caller genuinely needed it. `percentile_rank` is its **inverse** — a value to a percent rather than
a percent to a value — and the one-concept test now pins both.

## What the live run showed

Read before the content, as in every phase since 9D-1: **44 of 45 pairs, 10 of 10 currencies, 44
with a movement reading and 44 with a percentile.**

```
CHF: в среднем +1.15% против 9 валют, от +0.42% до +1.84% — в одну сторону против всех
...
USD: в среднем -0.92% против 9 валют, от -1.84% до -0.49% — в одну сторону против всех
```

**The decomposition does the thing it was built for.** A person watching `USDCHF` sees one line
rising and cannot tell which side moved. The universe says both did, in opposite directions and
against everything — a franc bid across the board and a dollar offered across the board.

**And the middle of the table is where the honesty rule pays for itself.** The euro's mean is
+0.14%, which alone would read as "roughly flat". Its range is −0.90% to +0.96%: it went both ways
depending on the counterpart. One number could not have told those apart, and the reading cannot be
constructed without the range.

**The absent pair surfaces honestly rather than silently.** `SEK` and `NZD` show *against 8
currencies* where everything else shows 9, because `NZDSEK` is the pair the provider does not quote.
Nothing had to special-case it: a smaller sample is simply reported as a smaller sample.

**The percentile gives the numbers a scale.** `USDCHF` at +1.96% is the 99th percentile of its own
631 observations, against a median of +0.58%. Before this slice the same fact was rendered as
`волатильность 1.23` — a number with no scale, which is decoration rather than description.

## One fault found by running it

The carry section first printed **"нет данных за нужный месяц"** — an absence reported but not
named, in a project whose standing habit is that absences are said out loud. A reader learned only
that something was wrong somewhere. It now reads:

> Разница ставок: не считаем. За 2026-06-01 нет ставок по EUR, GBP, JPY, а неполный набор дал бы
> таблицу без этих валют и без предупреждения об этом.

The refusal itself is correct and deliberate: EUR and GBP series stop in January 2026 and JPY in
May, so the all-or-nothing rule from 9D-4 applies — a ranking over the survivors would be a
different table wearing the same name, silently missing three currencies.

## What changed for a person

`/review` lost two lines. The aggregate `пройдено N из M` and the overall ruleset status are gone,
because an aggregate is the shape that reads as a verdict: *7 of 9 conditions met* invites *mostly
favourable*, and Phase 9C-2 measured those rules to separate nothing. The per-ruleset lines survive
— they are facts about which conditions held — but only in a message that now also says:

> Эти правила измерены в фазе 9C-2: они не разделяют исходы. Число выполненных условий ничего не
> предсказывает.

Ten tests asserted the old text. They were updated to assert the new contract rather than deleted:
the absence of an aggregate, and the presence of the null.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` / `ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 138 source files |
| `uv run pytest` | Passed; **927 passed**, 9 skipped (16 new) |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |
| Live run | 44 pairs, 10 currencies, plumbing read first |

Two small things worth recording. A comment in the review formatter quoting the removed strings kept
them alive in the file the safety test scans — reworded to describe rather than reproduce. And the
term ban is now matched **by whole word with a leading boundary**, which is the 10-1 lesson made
permanent after "long" matched inside "belongs" and "carry" inside "carrying" cost a round each.

No schema change and no migration.

## What this settles

Nothing about markets, and that is the point. It settles that the project can describe where things
stand without a single statement about what happens next, and that the rule against lonely central
tendencies is now a property of the code rather than a promise in a document.

10-3 is hidden concentration — the correlation state and the effective number of bets, so that
someone holding three positions can see whether they hold one at triple size. It contains no
forecast either, and it may be the most useful thing this project can offer.
