# Phase 11-2 Pre-registration — The Validator Blocks Advice but Not Forecasting

Written: 2026-08-25. **Committed before any code**, as 10-1 established.

## Context

Phase 8A's explanation validator is fail-closed and genuinely strong: every number in a model's
answer must come from the input, and a list of actionable Russian patterns rejects buying, selling,
long, short, signal, recommendation, entry, stop-loss, take-profit, target, trade, position, order,
broker, profit and loss.

**It does not reject forecasting.** A model can write:

> «Волатильность в 94-м перцентиле. **Обычно** после такого движение замедляется.»

Every number came from the input. No actionable word appears. **The validator accepts it.**

Meanwhile Phase 10-2 banned exactly that vocabulary — `обычно`, `ожидается`, `вероятно`,
`перекуплен`, and `экстремальн` since 10-4 — but that list lives in `tests/contract/`, runs only
over **our own source files**, and has never touched a single word a model produced.

So the project forbids forecasting in everything it writes itself and permits it in the one place
where the text is written by something that does not know the rule.

## Checked before planning — four findings, and the fourth changes the design

**1. The forbidden list is a test constant, and app code cannot import it.**
`PHASE_10_2_FORECAST_WORDS` lives in `tests/contract/test_safety_boundaries.py`. Tests may import
the app; the app must never import tests. So the list moves into the domain and **both** the
validator and the safety test read it from there — the one-concept rule this project has repaired
four times already.

**2. `ExplanationIssueCode` is a closed enum** of six codes. A rejection needs its own, so a
forecast rejection is diagnosable rather than filed under the actionable one — those are different
faults and a report that conflates them teaches nobody anything.

**3. The prompt already asks for more than the validator enforces.** `SYSTEM_PROMPT_RU` says
*«Не давай торговых указаний и оценок направления»* — no direction assessments, which is closer to
forbidding a forecast than anything the validator checks. **The prompt asks; the validator
guarantees; and today they disagree.** This slice makes the guarantee catch up with the request.

**4. A stem-based ban would over-reject, and over-rejection is a real cost.**
`обычно` (adverb, *usually*) is a forecast word. `обычный` (adjective, *ordinary*) frequently is not
— *«обычная волатильность»* describes the present. A ban on the stem `обычн` would reject both, and
**Phase 8D measured what acceptance is worth**: the same model went from 20% to 85% accepted, and
that difference is what made the feature usable at all. A rule that quietly returns it to 20% has
broken the feature while appearing to strengthen it.

So the patterns are written **precisely rather than by stem**, and the acceptance rate is measured
before and after with the existing 8D harness, `scripts/evaluate_explanations.py`.

## Design

**One list, in the domain, read by everything.** `app/domain/explanation_contract.py` already holds
`_ACTIONABLE_RUSSIAN_PATTERNS`; the forecast patterns join it as a sibling, and
`tests/contract/test_safety_boundaries.py` imports them instead of keeping its own copy.

**Precise patterns, not stems.** Each entry is written to catch the forecasting sense and to leave
the descriptive one alone, and each is accompanied by a test showing both — the sentence it must
reject and the sentence it must not.

**A separate issue code.** `FORECAST_TEXT`, so a rejected answer says *which* rule it broke.

**The prompt is updated in the same slice.** Asking for what is enforced costs nothing and raises
acceptance, which is the whole reason 8D's rewrite mattered. Enforcing a rule the prompt never
mentions is how a validator ends up rejecting most of what it sees.

## Acceptance criteria — fixed here, before the code

1. **The forecasting sentence is rejected.** *«Обычно после такого движение замедляется»* fails with
   `FORECAST_TEXT`, with every number valid and no actionable word present.
2. **The descriptive sentence is accepted.** *«Волатильность обычная для этой пары»* and
   *«сейчас 94-й перцентиль»* both pass. Each banned pattern carries a paired test: one sentence it
   must reject and one it must not.
3. **One list, one place.** The safety test imports the patterns from the domain; a test asserts the
   constant is defined in exactly one file.
4. **`FORECAST_TEXT` is distinct from `ACTIONABLE_TEXT`** and a text breaking both reports both,
   because the validator has always reported every issue rather than the first.
5. **The prompt asks for what is enforced**, asserted by checking the prompt names the constraint.
6. **The acceptance rate is measured before and after** on the same windows with the 8D harness, and
   **both numbers are published** — including if it fell. If the model cannot be reached, the report
   says so plainly rather than claiming the rule is free.
7. **A drop below 50% acceptance is reported as a problem, not a success.** A validator that rejects
   most of what it sees has removed the feature rather than secured it, and the honest response is
   to loosen a pattern and say which.
8. **Nothing else changes.** No new surface, no page changes, no measurement of markets.

If criterion 2 cannot be demonstrated, the slice is not done: a rule that rejects honest description
along with forecasting is worse than the gap it closes, because it will be switched off.

## Changes

1. `app/domain/explanation_contract.py` — the forecast patterns, the check, and the new issue path.
2. `app/domain/entities/explanation.py` — `FORECAST_TEXT`.
3. `app/adapters/chat_completions_explanations.py` — the prompt asks for what is enforced.
4. `tests/contract/test_safety_boundaries.py` — imports the list instead of holding a copy.
5. Tests, including a paired reject/accept sentence for every pattern.
6. `docs/phase11-2-verification-report.md`, AGENTS.md, PLANS.md, README.md, operations.md, Notion.

## Explicitly not in this slice

- **No page changes and no explanation on the page.** That needs this done first, and is a separate
  decision afterwards.
- **No service refactor and no route** — the next two steps, deliberately kept apart.
- **No change to the number rule or the actionable list**, both of which are working.
- **No schema change.**
