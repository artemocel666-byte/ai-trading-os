# Phase 8C Verification Report

Generated: 2026-08-01

## Scope

8A defined what a Chief AI may see and say; 8B built the provider. Neither could reach a person.
8C is that step — the first slice where a model's words can appear in a chat — and it closes Phase 8.

`PROJECT_PHASE = "phase_8c_explanation_delivery_foundation"`

Because it is that step, the whole slice is designed around the model being wrong, absent, or slow.

## Two decisions taken with the user

**A separate `/explain EURUSD M15` command, not an addition to `/review`.** Every model call costs
money, and `/review` is what you run repeatedly while watching data. Spending stays a deliberate act:
`/review` calls nothing and is byte-identical whether or not the explanation layer is configured — a
test asserts exactly that by running it both ways and comparing the replies.

**A failed explanation says so, in one line.** Silence would hide the event most worth knowing: that
a model answered and was refused.

## Implementation

- `app/telegram/snapshot_review_formatter.py` — `format_explanation_section` and
  `ExplanationUnavailableReason`. An accepted explanation is shown under
  `Пояснение (ИИ, проверено):` and closed with `Пояснение не меняет решение выше.` A rejection prints
  its issue codes. The section contains no emoji, so the formatter remains the only thing that adds
  one.
- `app/telegram/commands.py` — `explain_command`, reusing `_parse_snapshot_command`,
  `_default_snapshot_window`, `AnalysisService.build_snapshot`, and `build_snapshot_backed_review`,
  then 8A's `build_explanation_input` and 8B's `explain_validated`. `_request_explanation` catches
  `IntegrationDisabledError`, the `Provider*` family, timeouts, and cancellation, turning each into a
  reason. Nothing it can raise reaches the reply path.
- `app/telegram/bot.py` — the provider is built here and injected into `bot_data`, exactly as
  `AnalysisService` already is, and its client is closed in the existing `finally`. Wiring stays in
  the Telegram layer; `app/services` gained nothing, so the Phase 4G boundary is untouched.
- `app/core/config.py` — `explanation_delivery_enabled` (false) and `explanation_budget_seconds`
  (20, bounded). A Telegram command must not wait on retried provider timeouts.

The Phase 8A and 8B "not wired anywhere" safety tests were **narrowed, not deleted**: services,
scheduler, and API routes still may not reference any of it, and `commands.py` may call
`explain_validated` exactly once. An automatic path would spend money and show model text to someone
who never asked; a command a person types cannot.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 108 source files |
| `uv run pytest` | Passed; 600 passed, 7 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

### The four outcomes, rendered through the real formatter

Stored candles, `EURUSD M15`, `as_of` 2026-07-29 11:30Z, stub provider. Every reply below is what
Telegram would receive.

**Accepted** — the report, then the appendix:

```text
📊 READ-ONLY проверка по снапшоту.
...
Правила: пройдено 10 из 11.
- события: 1 из 2; не пройдено: event_context.high_impact_event_count
Замеры: волатильность 0.85, просадка 0.10%, сессия london.
...
NO TRADING SIGNAL.
NON-ACTIONABLE.
Торговых указаний нет.
Пояснение (ИИ, проверено):
Окно данных полное: использовано 12 свечей из 12. Проверки качества данных и рыночного контекста
пройдены. Одна проверка по событиям не пройдена.
Пояснение не меняет решение выше.
```

**Rejected** — the model said «Покупайте EURUSD, цель 1.25.»:

```text
...
NO TRADING SIGNAL.
NON-ACTIONABLE.
Торговых указаний нет.
Пояснение недоступно: ответ не прошёл проверку.
Причины: ACTIONABLE_TEXT, UNKNOWN_NUMBER.
```

The instruction and the invented price appear nowhere in the reply — only the codes.

**Delivery off** → `Пояснение недоступно: слой пояснений выключен настройками.`
**Timed out** → `Пояснение недоступно: ответ не пришёл за отведённое время.`

In all four: the deterministic report is intact (`NO TRADING SIGNAL.` and `NON-ACTIONABLE.` present)
and the reply carries exactly one emoji.

### Command tests

- accepted → report plus section, provider called once, one emoji
- rejected → report plus codes, and no model text anywhere
- `IntegrationDisabledError`, `ProviderRateLimitError`, `ProviderUnavailableError` → report plus the
  matching reason
- a provider sleeping past the budget → report plus the timeout line, without the command hanging
- flags off → report plus the disabled line, and the provider is never called (`calls == 0`)
- `/explain` without arguments → the same rejection shape as `/review`; unauthorized user → refused
- `/review` with and without the layer configured → identical replies, provider untouched

## Remaining risks / notes

- **A real model still has not answered.** Every result here came from a stub. `/explain` is now the
  way to find out, and it costs one request; the 8B report has the numbers.
- The reason lines say *what* failed, not the provider's own message. That is deliberate — provider
  errors can carry keys and URLs — but it means diagnosing a persistent failure means reading logs.
- An explanation is not persisted anywhere. If a model says something useful, it exists only in that
  one Telegram message. Storing them would be a new decision about retaining model output, not a
  detail to slip into a delivery slice.
- The budget is per command, not per day. Nothing yet limits how many `/explain` calls can be made
  in a row; the token cap bounds each one, but a spending ceiling belongs to whoever enables the key.
