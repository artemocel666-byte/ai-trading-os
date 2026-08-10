# Phase 8D Verification Report — A Local Explainer

Generated: 2026-08-10

`PROJECT_PHASE = "phase_8d_local_explainer_foundation"`

Phase 8 reopens on purpose. 8A defined what an explainer may see and say, 8B gave it a provider, 8C
delivered it through `/explain`. All three work and all three cost money on every call to a service
that also sees the data. This slice lets a model on the user's own machine answer instead — and,
more importantly, makes it measurable whether a given model *can*.

## One transport, not one vendor

LM Studio, Ollama, llama.cpp and vLLM all serve `/v1/chat/completions` with the request and response
shape the 8B adapter already spoke. So the adapter was **generalised, not copied**:
`openai_explanations.py` → `chat_completions_explanations.py`, `OpenAIExplanationAdapter` →
`ChatCompletionsExplanationAdapter`, gaining a `provider_name` and an **optional** `api_key`.

Writing a second adapter would have duplicated two hundred lines of retry and error handling to
reach the same endpoint, and doubled the surface that has to stay honest. What actually differs
between a remote and a local model is an address, a credential and a latency — arguments, not
algorithms.

**The Phase 8B boundary is unchanged**: exactly one module in the project can reach a model, and the
test that says so now names a file honest about what it is.

## No credential travels to a local endpoint

`api_key=None` means the `Authorization` header is **not built**, rather than sent empty. An empty
credential is indistinguishable in a server log from a broken one, and a real one handed to whatever
is listening on port 1234 would be worse than useless. A contract test constructs the local provider
with an OpenAI key configured and asserts the header is absent.

## The replaced flag fails loudly

`OPENAI_ENABLED` became `EXPLANATION_PROVIDER=disabled|openai|local` — an explainer is one choice,
and two booleans can be set to a combination that means nothing.

The old flag is **read and refused at startup**, not ignored. It was set in `.env` and in four
places in `compose.yaml`; had it been dropped silently, an operator would have been left believing
the explainer was configured when it was not. The refusal fired immediately on this machine's own
`.env` during verification, which is the behaviour working rather than a nuisance.

`enabled_integrations()` gains a `local_llm` key rather than reusing `openai`. That key has always
meant "something leaves this machine", and a local model does not.

## Measuring a model instead of forming an impression

`scripts/evaluate_explanations.py` walks real windows — the same `iter_replay_windows` the rules
see — asks the model to explain each, and reports the share the Phase 8A validator accepted plus a
histogram of why it rejected the rest.

That histogram is the deliverable. The validator is strict on purpose, and the *kind* of failure
decides what to do:

| dominant code | what it means | verdict |
| --- | --- | --- |
| `UNKNOWN_NUMBER` | the model invents figures | disqualifying; no prompt fixes this |
| `ACTIONABLE_TEXT` | it gives trading advice it was told not to | disqualifying |
| `TOO_LONG`, `EMOJI_FOUND` | prompt problems | usually fixable |
| `NOT_RUSSIAN` | the language instruction was ignored | model-dependent |

Read-only twice over: it writes nothing to storage, and it calls `explain_validated`, so rejected
text is dropped before it could be printed. Both are asserted by contract tests — one on the source,
one on the AST, because "never calls `explain` directly" is a property of the call graph.

The adapter is built inside the script rather than through the factory, so measuring a candidate
model does not require pointing the bot at it first. Retries are off: a retry would hide a model
that is simply too slow, which is the thing most worth learning about a local one.

## Latency is the one real behavioural difference

`EXPLANATION_BUDGET_SECONDS` defaults to 20 and the HTTP read timeout now follows it rather than
being pinned at 30 — a read timeout shorter than the budget would fail the call before the budget it
was given had run out. Past the budget, 8C's existing design sends the deterministic report alone
with one line saying why there is no explanation. On a small CPU model that path will fire often;
`docs/operations.md` says so, so it is not mistaken for a fault.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 117 source files |
| `uv run pytest` | Passed; 739 passed, 9 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |
| `EXPLANATION_PROVIDER` unset | disabled provider, no HTTP client opened |
| `OPENAI_ENABLED` present | startup refused, message names the replacement |
| local provider with a key configured | no `Authorization` header |
| openai provider | `Authorization: Bearer …` still sent |

## Against a real model

*Pending: LM Studio was not yet listening on port 1234 when the code landed. This section records
the model, the acceptance rate, the rejection histogram and the latency spread once measured.*

## What this does not change

- **Not what the explainer may see or say.** The Phase 8A contract and validator are untouched. A
  local model gets exactly the same input and is held to exactly the same standard as a hosted one —
  a cheaper model is not a reason to accept looser output.
- **Not the delivery gate.** `EXPLANATION_DELIVERY_ENABLED` is still separate and still off by
  default: a provider may exist and still not be allowed to answer a user.
- **Nothing about direction, the ledger, or trading.** This is the explanation layer only.

## Noted while reading, not fixed here

`EXPLAINABLE_FIELD_REFS` still lists `market_context.max_close_drawdown_atr` and
`time_filter.utc_weekday`, from before Phases 9A-4 and 9A-7. Both still resolve, so nothing is
broken — but the explainer is **not** shown `market_context.max_close_excursion_atr` or
`data_quality.market_open`, the two fields behind the rules that now actually fail. It can therefore
describe a rejection without being able to quote the number that caused it. Worth its own slice.
