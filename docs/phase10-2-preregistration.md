# Phase 10-2 Pre-registration — The Honesty Policy, Made Executable

Written: 2026-08-20. **Committed before any code**, as 10-1 established.

## Context

Seven pre-registered measurements returned nothing, and 9D-4 said why: what can be computed from
public data is already in the price. The product decision that followed is **context rather than
conclusion** — describe where things stand, never what they will do. 10-1 made the data live so a
description would be worth writing.

Two rules were agreed and now have to become code rather than intentions:

1. **Never collapse a distribution into a direction.** Show `n` and the spread and it is a
   description; show a lone median and it is a forecast, whether or not that was the intent. Our
   seven nulls *are* the measurement that the spread swamps the middle.
2. **No "обычно" about the future** — not of the market, not of traders. Saying "usually people take
   profit here" is a forecast about behaviour and, through it, about price; social proof persuades
   harder than a direct signal, not softer.

## Checked before planning, as 10-1 taught

**1. The honesty type already half-exists, and that changes the design.** `FieldDistribution`
(`app/domain/entities/calibration.py`) already refuses to hold a lonely central tendency:

> `an observed field must report every percentile`

So a median cannot **exist** without its spread. What is missing is that the *renderer* is under no
such obligation — a formatter can hold a complete distribution and print only its middle. **10-2's
job is therefore narrower and sharper than planned: make the rendering obey the rule the data
already obeys.**

**2. `nearest_rank` exists and is already the single definition of a percentile** in this project,
with a docstring recording that it was made public, reverted, and made public again only when a
second caller genuinely needed it. It is reused, never re-implemented.

**3. `/review` shows a person an aggregate rule score.** Today it renders:

```
Статус: … Итог правил: …
Правила: пройдено 7 из 9.
- качество данных: 3 из 3
- рыночный контекст: 2 из 3; не пройдено: …
Замеры: волатильность 1.23, просадка 0.45% (0.8 ATR), сессия …
```

Phase 9C-2 measured those rules and found they separate nothing, and two of them barely separate
anything at all. Nothing in the message says so. **An aggregate count is the exact shape that reads
as a verdict** — "7 of 9 conditions met" invites "mostly favourable", which is a claim the project
has measured to be empty.

The `Замеры:` line has a second, quieter problem: `волатильность 1.23` gives a reader no way to
know whether 1.23 is high or low. A raw number with no scale is not description; it is decoration.

**4. Telegram output must pass the emoji policy and the Russian-text validator.** Any new line is
subject to both, so the renderer is tested through them rather than around them.

## Design

**One renderer, and it is the only thing that may format a distribution.** A single function turns a
`FieldDistribution` into text and always emits `n`, the spread and the middle together. Everything
that wants to show a percentile calls it. The rule then holds by construction rather than by
review, and the test that enforces it is a search for anything else formatting `.median`.

**Percentiles are of the instrument against its own history**, so "today's range" is answered with
"in the 94th percentile for this pair over N days" rather than with a number nobody can scale.

**The currency decomposition answers a question a single chart cannot.** A person watching EURUSD
sees one line and cannot tell a strong euro from a weak dollar. Across 44 pairs the two are
separable: for each currency, its mean move against every other universe currency it is quoted
with. It is arithmetic on stored prices, contains no forecast, and is the single feature most
clearly worth more than watching the market yourself.

**`/review` keeps facts and loses the score.** The data-completeness lines describe *our own data*
and stay. The aggregate `Правила: пройдено N из M` goes, because an aggregate is a verdict. The
per-ruleset lines stay only if they carry the 9C-2 null in the same message — a person must not be
able to read the count without reading what it was measured to be worth.

**A script, not a Telegram command.** 10-2 produces the content and the policy on a read-only CLI,
the way every measurement phase has. Which of these lines ever reaches a person is a separate
decision, taken once the content has stopped moving.

## Acceptance criteria — fixed here, before the code

1. **A central tendency cannot be rendered alone.** One renderer formats distributions; a test finds
   no other user-facing or report code formatting `.median` or a mean directly.
2. **Every rendered distribution carries `n`.** A statement about the past without its sample size
   is refused by the renderer, not by a reviewer.
3. **Banned vocabulary.** A test over the new report and every user-facing layer rejects `обычно`,
   `ожидается`, `вероятно`, `перекуплен`, `перепродан`, `сигнал`, `рекомендуем` — matched as whole
   words, so the 10-1 lesson about "long" inside "belongs" is not repeated.
4. **`/review` no longer renders an aggregate rule score**, and any surviving rule line appears in a
   message that also states the 9C-2 null.
5. **The decomposition separates the pair from the currency**, asserted on a hand-built case where
   one currency rises against all nine others and the ordering must come out unambiguous.
6. **Percentiles come from `nearest_rank`** — the one-concept test gains an entry, so a second
   percentile definition cannot appear.
7. **A live run over the current universe**: the report renders for 44 pairs on real data, and the
   plumbing block is read before the content, as in every phase since 9D-1.
8. **Nothing new reaches Telegram or the API** beyond the `/review` subtraction in criterion 4.

If criterion 1 cannot be demonstrated mechanically, the slice is not done: it is the one that makes
the policy a property of the code rather than a promise in a document.

## Changes

1. `app/domain/market_state.py` — new, pure: currency decomposition and own-history percentiles from
   stored candles and rates. No session, no query.
2. `app/domain/entities/market_state.py` — new: the frozen readings, each carrying its own `n`.
3. `app/presentation/readings.py` — new: the single distribution renderer.
4. `app/telegram/snapshot_review_formatter.py` — the aggregate score removed; the 9C-2 null stated.
5. `scripts/report_market_state.py` — new, read-only.
6. Tests, including all eight criteria; the one-concept and vocabulary tests extended.
7. `docs/phase10-2-verification-report.md`, AGENTS.md, PLANS.md, README.md, operations.md, Notion.

## Explicitly not in this slice

- **No correlations and no concentration** — that is 10-3, and it needs its own care.
- **No COT** — 10-4.
- **No forecast, no ranking by expected return, no "what usually happens".**
- **No new Telegram or API surface.** The only user-facing change is a removal.
- **No two-level rendering.** Building two renderers over content that has not settled would double
  the work on unstable ground; the split comes when the content stops moving.
- **No schema change**, so no migration. Everything is computed from what 10-1 keeps current.
