# Phase 8B Verification Report

Generated: 2026-08-01

## Scope

Phase 8A defined what a Chief AI may see and what it may answer, proven against hand-written
candidates. 8B supplies the provider behind that contract — a real OpenAI adapter, disabled by
default — and the adversarial tests that show a lying model cannot change a deterministic report.

`PROJECT_PHASE = "phase_8b_explanation_provider_foundation"`

Still wired to nothing: no service, command, route, or job references the adapter. 8C does that, and
a safety test keeps it true until then.

## Implementation

- `app/adapters/openai_explanations.py` — `OpenAIExplanationAdapter`, plain httpx against
  `POST /v1/chat/completions`, in the same shape as `twelve_data.py` and `fmp_calendar.py`: shared
  retry loop, shared exception vocabulary, key in the `Authorization` header, tested through
  `httpx.MockTransport`. No SDK dependency was added; the existing pattern already gives offline,
  keyless tests, which `PLANS.md` required for this slice.
- `app/domain/interfaces/providers.py` — `ExplanationProvider`, a Protocol shaped for
  `ExplanationInput`. Added beside the older `LLMProvider` rather than replacing it: that one speaks
  in `Decision` values (`LONG`/`SHORT`/`NO_TRADE`) this pipeline never produces, from the same era as
  the scored request Phase 8A refused.
- `app/domain/entities/explanation.py` — `ExplanationOutcome`, whose validator enforces that text
  exists if and only if the validation accepted it.
- `app/adapters/disabled.py`, `app/adapters/factories.py`, `app/core/config.py` — disabled provider,
  factory, `openai_base_url`, and `openai_max_output_tokens` (default 400, bounded 50–4000).

## The two properties that matter

**Unchecked text has no path out.** `explain_validated` runs the Phase 8A validator and builds an
outcome that carries text only on acceptance. A rejected answer leaves no readable prose behind, so
nothing downstream can print it, log it into a user-facing path, or try to repair it. The offending
*number* does survive inside the issue detail, deliberately: an operator needs to know which figure
was invented, and a bare token instructs nobody.

**Prompt injection is not a surface here.** The user message is the contract's own
`deterministic_json()` — our rule ids, our statuses, our numbers. No market text, no third-party
string, nothing a stranger could write. A test asserts the request body contains exactly
`model`, `temperature`, `max_tokens`, `messages` and nothing more.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 108 source files |
| `uv run pytest` | Passed; 585 passed, 7 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

### Adversarial run against a real decision

Stub transport, real stored candles (`EURUSD M15`, `as_of` 2026-07-29 11:30Z), decision composed by
the Phase 4G composer. Fingerprints taken before the call and compared after each answer:

```text
decision fingerprint before = b01e418c8da2cd91
input fingerprint before    = b3e7fa45a64d92cd

  honest          accepted=True  text=kept    report_unchanged=True  issues=-
  invented price  accepted=False text=dropped report_unchanged=True  issues=UNKNOWN_NUMBER
  buy instruction accepted=False text=dropped report_unchanged=True  issues=ACTIONABLE_TEXT
  invented count  accepted=False text=dropped report_unchanged=True  issues=UNKNOWN_NUMBER
  emoji           accepted=False text=dropped report_unchanged=True  issues=EMOJI_FOUND
  english         accepted=False text=dropped report_unchanged=True  issues=NOT_RUSSIAN
  runaway         accepted=False text=dropped report_unchanged=True  issues=TOO_LONG
```

Six lies, six rejections, and in every case the decision and the input are byte-for-byte what they
were before the model spoke. That is the claim this phase exists to support.

### Contract behaviour, through MockTransport

- the request carries the model, `temperature=0`, the token cap, and the key in the header — never
  in the URL
- 401/403 → authentication, 402 → plan restricted, 429 → rate limit, other 4xx → unsupported
  request; a 503 is retried the configured number of times and then reported unavailable (asserted
  by call count, not by timing)
- a read timeout is a timeout, not a generic failure
- malformed JSON, an empty `choices` list, a missing message, an empty string, and an unexpected
  shape are all failures — **not** an empty explanation. Returning `""` here would later read as a
  model that simply had nothing to say.
- an `error` payload arriving with HTTP 200 is still an error
- `OPENAI_ENABLED=false` yields a provider that raises before any network call; enabling it without
  a key fails settings validation, and without a client fails the factory

## What a live call would cost, and how to run it

Not performed: it needs the user's key and money, and nothing in the product calls it yet.

One explanation is one request: roughly 700–900 input tokens (the serialized contract plus the
system prompt) and at most 400 output tokens. At `gpt-4.1` list prices that is well under a cent per
call; the exact figure depends on the model chosen, which stays the user's decision.

To try it once enabled, in a Python shell inside the container: build a snapshot through
`AnalysisService`, compose it with `StrategyDecisionComposer`, project it with
`build_explanation_input`, then call `create_explanation_provider(settings, client=clients.explanation)`
and `explain_validated`. The 8C wiring will do exactly this behind `/review`.

## Remaining risks / notes

- **No real model has answered yet.** Every result above came from a stub. The first genuine answer
  arrives in 8C, and the validator is what stands between it and a user.
- `temperature=0` reduces variation but does not guarantee identical answers across calls; the
  deterministic report is unaffected either way.
- The adapter retries 5xx and timeouts but not a rejected explanation. Asking a model again after it
  broke the rules would be paying twice for the same risk; the deterministic text is the answer.
- `OPENAI_MODEL` still defaults to `gpt-4.1`, unchanged from before this slice. Picking a model is
  a cost decision for the user, not a default this phase should quietly set.
