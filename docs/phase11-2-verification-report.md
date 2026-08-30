# Phase 11-2 Verification Report — The Forecast Guard

Generated: 2026-08-25

`PROJECT_PHASE = "phase_11_2_forecast_guard"`

Pre-registered in [`docs/phase11-2-preregistration.md`](phase11-2-preregistration.md), committed
before any code (`90e3b84`).

## The eight criteria

| | criterion | result |
| --- | --- | --- |
| 1 | The forecasting sentence is rejected | **Pass** |
| 2 | **The descriptive near miss is accepted** | **Pass** — a paired test per pattern |
| 3 | One judgement, one authority | **Pass** — and it landed differently; see below |
| 4 | `FORECAST_TEXT` distinct from `ACTIONABLE_TEXT` | **Pass** |
| 5 | The prompt asks for what is enforced | **Pass** |
| 6 | Acceptance measured before and after | **Not run — no model reachable.** See below |
| 7 | A drop below 50% reported as a problem | **Not applicable** — criterion 6 could not run |
| 8 | Nothing else changes | **Pass** |

## The gap, and what closes it

The Phase 8A validator required every number to come from the input and rejected a long list of
actionable Russian. It accepted this:

> «Волатильность в 94-м перцентиле. **Обычно** после такого движение замедляется.»

Every number from the input. No actionable word. A forecast in the middle of it. Meanwhile the
Phase 10-2 ban on that vocabulary ran only over **our own source files** and had never touched a
word a model produced.

`contains_forecast_russian_text` now runs inside the validator, and `FORECAST_TEXT` is a separate
issue code — advice and forecasting are different faults, and a report that filed them together
would teach nobody which rule was broken.

## Criterion 3 landed differently from how it was written, and that is the finding

The pre-registration expected **one list**. Building it showed **two strictnesses that must differ**:

- Over **our own prose** a stem is right. We control the text, so catching `обычная` beside `обычно`
  costs a rewrite and nothing else.
- Over **a model's answer** a stem is wrong. It would reject honest description, and Phase 8D
  measured what that costs: the same model went from 20% to 85% accepted, and that difference is the
  entire reason the feature is usable.

The resolution is better than either: the domain holds **one judgement**,
`_FORECAST_RUSSIAN_PATTERNS`, read through **one function**, `forecast_claims`. The validator and
the safety test both call it. There is no second list at all — an intermediate `FORECAST_VOCABULARY`
tuple was written, then deleted once the shared function made it a constant nobody read.

## A negated mention is not a claim

The rule as first written failed on the most honest sentence in the project. The Phase 11-1 page
footer refuses a forecast by naming the thing it refuses, and a ban that could not tell assertion
from refusal would have forced that sentence to be reworded around its own guard.

So `forecast_claims` skips a match preceded by a negation, and this is not a loophole — it is the
rule stated correctly. Saying "this is not a forecast" makes none.

## Criterion 6 could not be run, and the reason is stated rather than worked around

**No local model is reachable.** LM Studio's port is silent and Ollama answered a probe earlier in
the session but does not now; nothing is listening on 11434, 1234 or 8080. Without a model, the 8D
harness cannot generate answers, so the before-and-after acceptance rate has no measurement.

The pre-registration named this outcome in advance: *"If the model cannot be reached, the report
says so plainly rather than claiming the rule is free."* So it is said plainly. **The cost of this
rule to acceptance is unmeasured.**

What could be checked was checked. The rule was run against the answer Phase 8D published as
accepted, and against five lines taken verbatim from the current product surfaces:

| text | forecast claims found |
| --- | ---: |
| The answer 8D accepted from `gpt-oss-20b` | **0** |
| `Данные: свечей 12 из 12, полнота 100.0%…` | 0 |
| `EURUSD: сейчас +1.96%, это 99-й перцентиль…` | 0 |
| `CHF: в среднем +1.15% против 9 валют…` | 0 |
| `EUR: чистая спекулятивная позиция -7.3%…` | 0 |
| `EURUSD, GBPUSD, AUDUSD: позиций 3, независимых ставок примерно 1.2` | 0 |

**A sample of one accepted answer is a sample of one**, and it does not stand in for the twenty
windows the criterion asked for. It is evidence that the rule does not obviously break the feature,
and nothing more. The measurement remains owed, and the harness is ready for it:

```bash
uv run python scripts/evaluate_explanations.py --base-url http://localhost:11434 --model <name>
```

## One defect worth recording

**A literal backspace byte was written into a source file.** A heredoc turned `\b` into the control
character 0x08, so `_NEGATION_BEFORE` compiled with a backspace where a word boundary belonged and
silently never matched — which is why the page footer kept failing after the negation rule was
supposedly in place.

Two things followed. The repair, and a **sweep of every `.py` file in `app`, `scripts` and `tests`
for stray control characters**: exactly one existed, and it was this one. An invisible byte that
changes what a regular expression means is the quietest possible fault, and worth knowing the count
of rather than assuming.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` / `ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 144 source files |
| `uv run pytest` | Passed; **994 passed**, 9 skipped (13 new) |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |
| Control-character sweep | 1 found, 1 repaired, 0 remain |

Seven patterns, each with the sentence it must reject and the near miss it must let through:
`обычно` against `обычная`, `ожидается` against `предполагал`, `вероятно` against `сузился`,
`перекуплен` against `перцентиль`, `экстремальное` against `в третьем перцентиле`, `прогноз`
against `описание`, and `продолжит` against `выросла`.

`экстремальн` is the one entry with a legitimate descriptive use — «экстремальные значения выборки»
is ordinary statistics. It is kept because the phrase this project actually meets is «экстремальное
позиционирование», and a regular expression cannot see the difference. The over-rejection is named
rather than hidden.

## What this settles

The validator now refuses to pass a forecast, and the prompt asks for the same thing it enforces.
What it does **not** settle is the price: how often a real model trips the new rule is unmeasured,
and the honest position is that this rule is unpriced until a model is running.

The next two steps of the sequence are unchanged: lift the loaders into a service, then the route.
