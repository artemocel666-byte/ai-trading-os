# Phase 11-4 Verification Report — The Route

Generated: 2026-08-30

`PROJECT_PHASE = "phase_11_4_market_page_route"`

Pre-registered in [`docs/phase11-4-preregistration.md`](phase11-4-preregistration.md), committed
before any code (`7fe3415`).

## The eight criteria

| | criterion | result |
| --- | --- | --- |
| 1 | The document is assembled in exactly one place | **Pass** |
| 2 | **The script's output is unchanged** | **Pass** — identical, re-checked after the bump |
| 3 | **The route serves the same bytes the script writes** | **Pass** — on raw bytes against the live container, after a defect that had hidden itself |
| 4 | The route does not exist when the flag is off | **Pass** — and the first two ways of checking it were vacuous; see below |
| 5 | Telegram stays absolutely closed | **Pass** — its rule untouched, plus a new test |
| 6 | A document, not a feed | **Pass** |
| 7 | The bind is not widened | **Pass** — asserted against `compose.yaml` |
| 8 | No new auth, no new dependency, no schema change, suite green | **Pass** — 1017 passed, 9 skipped |

## Criterion 3 is the one that decides the slice

Two renderings of the same readings that differ are the sixth copy arriving by another door. The
route was called against the live database and its response compared with the file the script had
just written, with the one embedded timestamp masked:

```
status        200
content-type  text/html; charset=utf-8
served bytes  22,988   file bytes 22,988
VERDICT: IDENTICAL
```

Both this and criterion 2 were run twice — once when the assembly moved, and again after
`PROJECT_PHASE` was bumped, for the reason 11-3 recorded: a constant that leaked into a rendered
page is exactly the quiet difference these criteria exist to catch.

### The first measurement of this criterion had normalised away the thing it was measuring

The run above used an in-process client, comparing `response.text` against `Path.read_text()`. It
reported 22,988 = 22,988 and it was **not wrong about the document** — but it could not have seen a
difference in bytes, because `read_text` uses text mode and translates newlines on the way in.

Run again against the container over HTTP, the raw bytes differed:

```
script file : 20,808 bytes   CR 42
served page : 20,766 bytes   CR 0
```

Forty-two carriage returns. `Path.write_text` is text mode too, so on Windows every newline in the
written file became CRLF while the route served the document's own bytes. **The same document, but
not the same file** — and this criterion is about bytes, which is the whole reason it was chosen to
decide the slice.

`scripts/render_market_page.py` now writes with an explicit newline, and the comparison holds on raw
bytes with nothing normalised:

```
script file : 20,766 bytes   CR 0
served page : 20,766 bytes   CR 0
VERDICT (raw bytes, timestamp masked): IDENTICAL
```

The lesson is not about Windows. **A check run through the same abstraction as the code it checks
cannot see what that abstraction hides.** The in-process client shared Python's text mode with the
script; only stepping outside to HTTP and raw bytes made the difference visible. A ninth unit test
pins the newline so the fix cannot be lost, and it is written with a raw string — a normal literal
would put an actual newline in the expectation and never match, which is the sixth time in this
project that a check has been defeated by the escaping in its own expectation.

## The safety question, answered by narrowing rather than dodging

The page contains positioning, and `test_phase10_4_positioning_reaches_no_user_facing_layer` said
the API stays absolutely closed to it. The available dodge was cheap: have the route import a
function that returns a string, never name `PositioningReading`, and leave the test passing while
the data reached a person exactly as before.

Refused, and the reason is written into the rule itself. **A rule that passes while its purpose is
defeated is worse than no rule, because it then certifies the thing it was written to prevent.**

So the rule now states what it actually protects, which is not "a person must never see
positioning" — 10-2 settled that deliberately and the net-position table has been printed to a
person ever since. It protects:

- **The channel: pull, not push.** A page a person opens is not a message a person receives.
  `app/telegram` stays in the closed list, its own rules untouched, and a new test says so directly.
- **The shape: a document, not a feed.** The route returns HTML; `response_model` and `JSONResponse`
  are asserted absent; and no other file under `app/api` may reach the page or reading services.

Two files may name positioning at all — the reading service from 11-3 and the page service from
11-4. A formatter, a digest or an analysis service that started reading it still fails, which was
always the case that mattered.

## A rule kept at full strength by moving code instead of widening it

The 9D-2 rule — no `cross_section` anywhere in services, routes, handlers or jobs — fired
unexpectedly. The page needs a move over a window and a price at a date, and both helpers lived in
`cross_section.py` because 9D-2 needed them first.

They are not the cross-section. `forward_return` is a simple return between two closes and
`latest_close_at` is "what did this cost at that moment". The ranking is the part that is
structurally a direction, and it is what the rule was written about.

The cheap fix was an allow-list entry, which would have admitted the whole module —
`build_cross_section_profile` included — to a service that never touches it. Instead the two helpers
moved to `app/domain/price_series.py`, and the rule passes **unchanged and at full strength**. The
same lesson as `daily_returns` in 11-3: a derivation more than one question needs belongs where it
can be named, not inside the first module that happened to want it.

## Criterion 4 was checked two vacuous ways before it was checked correctly

The obvious check — `{route.path for route in app.routes}` — found only `/openapi.json`, `/docs`,
`/docs/oauth2-redirect` and `/redoc`. This FastAPI version keeps an included router as one opaque
`_IncludedRouter` entry that exposes neither `path` nor a nested `routes` list, so the recursive
version failed the same way.

Both would have **passed**. `"/market/page" not in off` is trivially true of a set that contains no
application routes at all, and the flag-on half would have been the only thing to fail — a check
that reports the right verdict for entirely the wrong reason is the kind that survives into a phase
where it matters.

What caught it was a guard assertion written before the result was read: `assert "/health" in off,
"no application routes were found; the check would be vacuous"`. **Plumbing before the result**, the
habit this project has kept since 9D-1, working exactly as intended one level away from where it was
learned. The check now reads the OpenAPI schema, which is the surface the application actually
declares, and the guard stays.

## The exposure decision, and the cost that was named rather than solved

**No new authentication and no widening of the bind.** `compose.yaml` publishes
`127.0.0.1:8000:8000`, so the page is reachable where the operator already is. `MARKET_PAGE_ENABLED`
defaults to off, and registration is conditional rather than a per-request flag check: an
unregistered route cannot be reached through a mistake in a dependency.

The alternatives were each worse for a product with one user. A token in the URL leaks through
history, logs and referrers. A cookie session means a login form, password storage and a session
store. Basic without TLS sends the password in clear over the LAN.

**The cost: another device cannot open this page.** Binding to the LAN address with no
authentication would make it readable by anything on the network. That is the next product decision
and it needs real authentication first — deliberately not taken here, because a slice that both
served the page and invented an auth scheme would have written the auth half in a hurry.

Criterion 7 makes this checkable rather than remembered: a test reads `compose.yaml` and asserts the
API is still published to loopback only. If it ever fails because the binding was widened on
purpose, the fix is not to edit the test.

## One line added to `compose.yaml` after the flag was switched on

The `api` service enumerates its capability flags in `environment:` with explicit defaults, and
`MARKET_PAGE_ENABLED` was not among them. It reached the container anyway through `env_file`, so
nothing was broken — but someone reading that block to learn what the container can do would not
have seen the page at all. Added with the same `false` default the code has.

## Verification run

```
uv run ruff format .            clean
uv run ruff check .             All checks passed
uv run mypy app                 no issues in 148 source files
uv run pytest                   1017 passed, 9 skipped
uv run python scripts/security_check.py   exit 0
```

Nine new unit tests and five new safety rules. No existing test was weakened; the 10-4 rule was
narrowed with its reasoning written into the docstring, and the 9D-2 rule was left untouched.

## What this slice deliberately did not do

No authentication, no accounts, no login. No LAN or public exposure, no tunnel, no TLS. No JSON API
for the readings. No auto-refresh, no caching, no streaming — the page is built per request from
stored data. Nothing about Telegram, `/explain`, the scheduler or ingestion.
