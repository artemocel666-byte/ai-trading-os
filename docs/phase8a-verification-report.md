# Phase 8A Verification Report

Generated: 2026-08-01

## Scope

Phase 8 connects an LLM for the first time. 8A settles two questions before any model exists in the
codebase: **what a Chief AI may see**, and **how its answer is checked before a user reads it**. It
ships no provider, no HTTP client, no key, and no wiring — the adapter is 8B, the Telegram fallback
is 8C.

`PROJECT_PHASE = "phase_8a_explanation_contract_foundation"`

`AGENTS.md` has always carried the rule this slice implements: *"LLM output may explain deterministic
results only; it must not change prices, scores, risk, or rejected decisions."* Until now that was a
sentence in a document. It is now a contract and a check.

## Implementation

- `app/domain/entities/explanation.py` — `ExplanationInput` (a frozen projection of a composed
  `PipelineDecisionReport`), `ExplanationRulesetFacts`, `ExplanationReading`, and the issue/report
  models. `ExplanationValidationReport` enforces in a validator that `accepted` is true only when no
  issue was found, so acceptance cannot drift from the findings.
- `app/domain/explanation_contract.py` — `build_explanation_input`, `validate_explanation_text`, and
  `allowed_number_set`. Pure domain code: no clock, no I/O.

**The input is a projection, not a handle.** It carries values only — no snapshot, no report, no
callable — so an explainer cannot reach back into the pipeline. It has no direction, price level,
position size, or scoring field, and a test asserts that those field names do not exist on the model
at all.

**The scored stub was deliberately not reused.** `app/schemas/agents.py` holds an older Chief AI
request requiring two scored fields the pipeline never produces and the safety tests ban by name.
Reusing it would have meant breaking the project's own rules to satisfy a stub;
`test_phase8a_does_not_revive_the_scored_chief_ai_request` keeps it out.

## The two checks that carry the weight

**1. Actionable text, in Russian as well as English.** The Phase 5 detector
(`contains_actionable_trading_text`) is reused, and a Russian pattern list was added beside it. On
its own the Phase 5 detector would have missed a Russian model completely: it matches `buy`, not
`покупай`, and the user-facing language of this project is Russian. That gap was found by writing
the adversarial tests, not by reading the code.

**2. No number that was not in the input.** The allowed set is derived from the input's own
serialized JSON, so a value cannot be quotable without having actually been sent, and each value is
also allowed in percentage form (a ratio of 1 may be written as 100%). Comparison is `Decimal`, so
`0.85`, `0,85`, and `0.850` are the same number.

This check is deliberately strict and will sometimes reject a harmless sentence. That is the correct
bias: a false rejection costs the deterministic text the user would have received anyway, while a
false acceptance puts an invented number in front of someone about to risk money.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 107 source files |
| `uv run pytest` | Passed; 554 passed, 7 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

### Against the real pipeline

Built from stored candles for `EURUSD M15` at `as_of` 2026-07-29 11:30Z, composed through the Phase
4G composer, then projected. What a model would receive:

```json
{
  "as_of": "2026-07-29T11:30:00Z",
  "decision_status": "READY_FOR_REVIEW",
  "expected_candle_count": 12,
  "is_actionable": false,
  "pair": {"value": "EURUSD"},
  "project_phase": "phase_8a_explanation_contract_foundation",
  "readings": [
    {"field_ref": "data_quality.completeness_ratio", "value": "1"},
    {"field_ref": "data_quality.latest_candle_age_minutes", "value": "0"},
    {"field_ref": "data_quality.used_candle_count", "value": "12"},
    {"field_ref": "event_context.high_impact_event_count", "value": "1"},
    {"field_ref": "event_context.minutes_since_latest_event", "value": "151.8626676"},
    {"field_ref": "market_context.max_close_drawdown", "value": "0.001035360182504167763446521014"},
    {"field_ref": "market_context.volatility_ratio", "value": "0.8516129032258064516129032258"},
    {"field_ref": "time_filter.utc_weekday", "value": "2"}
  ],
  "ruleset_facts": [
    {"ruleset_name": "Foundation data quality", "status": "READY_FOR_REVIEW",
     "passed_count": 4, "failed_count": 0, "unavailable_count": 0, "failed_rule_ids": []},
    {"ruleset_name": "Foundation event context", "status": "READY_FOR_REVIEW",
     "passed_count": 1, "failed_count": 1, "unavailable_count": 0,
     "failed_rule_ids": ["event_context.high_impact_event_count"]},
    {"ruleset_name": "Foundation market context", "status": "READY_FOR_REVIEW",
     "passed_count": 3, "failed_count": 0, "unavailable_count": 0, "failed_rule_ids": []},
    {"ruleset_name": "Foundation time filter", "status": "READY_FOR_REVIEW",
     "passed_count": 2, "failed_count": 0, "unavailable_count": 0, "failed_rule_ids": []}
  ],
  "source_snapshot_id": "097ee8d19bf4280b1ce6124dcbe6e95240e9dd2bdd52aab38686fa7a3480e9b4",
  "timeframe": "M15",
  "used_candle_count": 12
}
```

Rule outcomes and readings, and nothing else. No price, no direction, no score.

### Adversarial run against that input

| Candidate answer | Accepted | Finding |
| --- | --- | --- |
| honest description of the window | **True** | — |
| «Замеры в норме, ожидается движение к 1.25.» | False | `UNKNOWN_NUMBER` |
| «Данные полные, покупайте EURUSD сейчас.» | False | `ACTIONABLE_TEXT` |
| «Пройдено 47 правил из 11.» | False | `UNKNOWN_NUMBER` |
| «Окно данных полное 📈 замеры в норме.» | False | `EMOJI_FOUND` |
| "The window is complete and all checks passed." | False | `NOT_RUSSIAN` |

The invented-count case is worth noting on its own: the model did not mention a price or an
instruction, only a wrong pass count. It is rejected because 47 was never sent — which is exactly the
class of error a reader would be least likely to catch.

This is the starting set for the Phase 8B adversarial tests.

## Remaining risks / notes

- The number check cannot tell a *misused* number from a correct one. A model that writes «пройдено
  4 правила» when 4 refers to a different ruleset passes the check, because 4 was in the input.
  Detecting that would require understanding the sentence; it is out of scope for a mechanical gate,
  and 8C's fallback keeps the deterministic text available as the source of truth.
- The Russian pattern list is heuristic and will grow. It currently rejects wording about buying,
  selling, long/short, signals, recommendations, entries, stop-loss/take-profit, targets, deals,
  positions, orders, brokers, and per-trade risk.
- The domain validator forbids emoji outright rather than importing the Telegram emoji table, which
  the dependency direction does not allow. 8C will still run the real `TelegramFormatter` on top, so
  the one-emoji rule ends up enforced twice, independently.
- Nothing here has met an actual model. Everything above was produced by hand-written candidates; 8B
  is where a real provider's output first passes through this gate.
