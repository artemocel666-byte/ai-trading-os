# Phase 10-4 Verification Report — Positioning

Generated: 2026-08-25

`PROJECT_PHASE = "phase_10_4_positioning"`

Pre-registered in [`docs/phase10-4-preregistration.md`](phase10-4-preregistration.md), committed
before any code (`7fb9e6c`).

## The eight criteria

| | criterion | result |
| --- | --- | --- |
| 1 | Eight stored, NOK and SEK named as uncovered | **Pass** |
| 2 | **The rename is handled; NZD and USD reach before Feb 2022** | **Pass** — 1999 and 1992 |
| 3 | Every reading carries its Tuesday and its age | **Pass** — live: 7 days |
| 4 | The dollar index is labelled a basket | **Pass** |
| 5 | Share of open interest; a zero denominator yields an absence | **Pass** — entity and DB check |
| 6 | Percentiles from the existing machinery | **Pass** — no new definition |
| 7 | Live fetch, coverage read first | **Pass** — 13,775 rows |
| 8 | No claim that positioning predicts anything | **Pass** |

## The finding the phase turned on

Probing the source before planning — the 9D-1 habit — found that **both `NZ DOLLAR` and
`USD INDEX` were renamed in early 2022.** Their previous names stop dead on 2022-02-01:

```
NZ DOLLAR             latest 2026-08-18      NEW ZEALAND DOLLAR    latest 2022-02-01
USD INDEX             latest 2026-08-18      U.S. DOLLAR INDEX     latest 2022-02-01
```

A mapping keyed on today's names would have produced two series starting in February 2022 beside six
running for decades, and **every percentile taken against them would have been a percentile of the
wrong history** — a wrong answer wearing the shape of a real one, exactly as the half-added timeframe
did in 9D-1.

The fix turned out to be clean rather than laborious: **the contract code survives the rename.**
`112741` and `098662` return the full series under either name. So the project maps by code, and the
backfill proves it every run:

```
  ccy   code       rows         from           to  basket
  AUD   232741     1794   1987-01-30   2026-08-18      no
  CAD   090741     1931   1986-01-15   2026-08-18      no
  CHF   092741     1929   1986-01-15   2026-08-18      no
  EUR   099741     1452   1986-01-15   2026-08-18      no
  GBP   096742     1876   1988-04-29   2026-08-18      no
  JPY   097741     1931   1986-01-15   2026-08-18      no
  NZD   112741     1150   1999-01-05   2026-08-18      no
  USD   098662     1712   1992-05-29   2026-08-18     yes

  Every series reaches back before 2022-02-01, which is what mapping by
  contract code rather than by name buys.
```

**13,775 rows stored, eight currencies.** `NOK` has no contract at all and the only `SEK` one died
in 1998 on an exchange that no longer exists; both are named rather than zeroed.

## Live, in the market state report

```
AUD: чистая спекулятивная позиция -15.3% открытого интереса; данные за 2026-08-18, им 7 дн.;
     32-й перцентиль, недельных наблюдений 1793
CAD: ... -44.0% ...;  3-й перцентиль, недельных наблюдений 1930
NZD: ... -36.6% ...; 11-й перцентиль, недельных наблюдений 1149
USD: ... +39.8% ... (индекс против корзины, не двусторонний курс);
     72-й перцентиль, недельных наблюдений 1711
  Контракта нет вовсе, поэтому нет и данных: NOK, SEK. Это отсутствие, а не нулевая позиция.
```

Three things worth noting about that output.

**It is internally consistent.** Speculators are net short every bilateral currency and net long the
dollar basket — which is the same statement twice, and a useful check that the signs are right.

**The Canadian dollar sits at the 3rd percentile of 1,930 weekly observations.** In the vocabulary
this phase deliberately banned, that line would read "extreme short positioning". A percentile says
the same fact without the claim about what happens next, which is why `экстремальн` joined the
forbidden list beside `перекуплен`.

**Nothing says "now".** Every line carries the Tuesday it describes and how old that is — seven days
at the moment of reading. The CFTC publishes Friday for the preceding Tuesday, so a present-tense
line would be wrong by default.

## Design decisions worth recording

**Normalised by open interest, not counted in contracts.** The euro contract dwarfs the New Zealand
one and every contract has grown for forty years; raw counts compare neither across currencies nor
across decades.

**The all-or-nothing rule was refined, not excepted.** 9D-4 and 10-3 withhold an answer when a
member is missing, because a *ranking* that silently drops members answers a different question. A
*per-currency fact* does not: the euro's percentile against its own history is unaffected by NOK
having no contract. So per-currency readings stand alone with absences named — and any future table
ranking currencies against each other must say which two are not in it.

**`open_interest > 0` is checked at the entity and again in the database**, while the position
columns are not. A speculative long or short can legitimately be zero; the denominator cannot, and
a row that would become a division by zero is refused where the refusal is readable rather than
arriving downstream as a position of zero.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` / `ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 142 source files |
| `uv run pytest` | Passed; **967 passed**, 9 skipped (20 new) |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |
| Migration 0006 up, down and up again | Clean round-trip |
| Live fetch | 8 currencies, 13,775 rows, every series pre-2022 |

Five safety assertions, of which two are specific to this slice: **the contract codes are pinned and
`market_and_exchange_names` may not appear in the adapter at all**, so the name-keyed mapping cannot
come back; and **nothing in the positioning path may say `predicts`, `signal`, `forecast the` or
`leading indicator`**, because the slice measured nothing about prediction and may not imply it did.

## What this settles

Nothing about markets, and deliberately so. Positioning is now describable — what participants hold,
beside what the price did — and the project can say where it stands against forty years of its own
history without a word about what comes next.

Whether positioning predicts anything is a separate pre-registered question, and on the resolution
arithmetic from 9D-4 this design could not answer it: the documented effects are the same order as
carry, which needed 266 years of monthly data to confirm.

This closes the descriptive shortlist drawn up after 9D-4. **The content has now stopped adding new
*kinds* of reading** — the signal named in the 10-3 discussion for when the visual layer becomes the
right next step. That phase will need criteria about permitted *forms*: a chart can imply a trend
without a single word, and a vocabulary ban cannot reach it.
