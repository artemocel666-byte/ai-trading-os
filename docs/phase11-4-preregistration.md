# Phase 11-4 Pre-registration — The Route

Written: 2026-08-30. **Committed before any code**, as 10-1 established.

## Context

11-3 made one place read the universe. The page is still produced only by running a script and
opening a file. This slice serves it over HTTP.

It also forces a decision this project has deferred twice: **`X-Internal-API-Key` is a header a
browser cannot send.** A page behind it is a page nobody can open.

## Checked before planning — four findings

**1. The assembly is in the script, and the route would be the second copy.** `_build_document` in
`render_market_page.py` holds the whole document: plumbing rows, currency strength, the unusual-range
strips, the correlation grid, the positioning bars, the title and the footer. A route that rebuilt
that would be 11-3 happening one level up, and the second copy would be the one that drifted.

**2. The page does not contain interest rates at all.** It draws candles and positioning. So the
9D-3 rule needs no amendment here — a fact worth stating, because the tempting move would have been
to amend it pre-emptively.

**3. The API is already bound to loopback.** `compose.yaml` publishes `127.0.0.1:8000:8000`.
Nothing on the network can reach it now, and nothing in this slice changes that.

**4. Unauthenticated GET routes already exist.** `/api/v1/system/status` has no key dependency; only
the two scanning mutations do. So an unauthenticated read is precedent, not novelty.

## The honest version of the safety question

`test_phase10_4_positioning_reaches_no_user_facing_layer` says Telegram and the API stay absolutely
closed to positioning. **A served page contains positioning.** There are two ways to proceed and
only one of them is honest.

**The dodge, which is refused.** The route can import a function that returns a string and never
name `PositioningReading`. The substring test passes. The data still reaches a person. A rule that
passes while its purpose is defeated is worse than no rule, because it now certifies the thing it
was written to prevent.

**The narrowing, which is what this slice does.** State what the boundary actually protects, which
is not "a person must never see positioning" — 10-2 settled that question deliberately, and the
report has printed the net-position table to a person ever since. What it protects is **the channel
and the shape**:

- **Pull, not push.** A page you open is not a message you receive. Telegram pushes, and Telegram
  therefore **stays absolutely closed**, unchanged, with its test untouched. This is the line, and
  it is a real one rather than a convenient one.
- **A document, not a feed.** The route returns the assembled page. It does not gain a JSON
  endpoint for positioning, candles or rates. A document is read by a person; a feed is consumed by
  a program, and a program that consumes it is the first half of something that acts.

Both halves get their own criterion below, so the narrowing is checked rather than promised.

## The exposure decision, and what it costs

**No new authentication, and no widening of the bind.**

The alternatives were considered and each is worse right now. A token in the URL leaks through
history, logs and referrers. A cookie session means a login form, password storage and a session
store — real surface, for a product with exactly one user. HTTP Basic without TLS sends the password
in the clear over the LAN.

So the page is reachable where the operator already is, and nowhere else.

**The cost, named rather than solved: a phone cannot open it.** `127.0.0.1` on the host is not
reachable from another device, and binding to the LAN address with no authentication would make the
page readable by anything on the network. Opening it to a phone requires real authentication first.
That is the next product decision, and it is deliberately **not** taken here — a slice that both
serves the page and invents an auth scheme would be two slices, and the auth half would be the one
written in a hurry.

**Off by default.** `MARKET_PAGE_ENABLED=false`, following the convention every other capability in
`Settings` uses. The route is not registered when the flag is off.

## Acceptance criteria — fixed here, before the code

1. **The document is assembled in exactly one place**, and both the script and the route call it. A
   test asserts the script no longer assembles and the service does.
2. **The script's output is unchanged**, compared against a captured run with the one timestamp
   masked. Same decisive criterion as 11-3: the refactor half of this slice must move nothing.
3. **The route serves the same bytes the script writes** for the same inputs, compared with the
   timestamp masked. Not "looks the same" — the same document.
4. **The route does not exist when the flag is off.** Asserted against the built application's
   actual route table, not against the settings object.
5. **Telegram stays absolutely closed.** Its rule is untouched and its test is not modified.
6. **A document, not a feed.** The response is `text/html`; no JSON schema for positioning, candles
   or rates is added; and no new route returns them as data.
7. **The bind is not widened.** A test reads `compose.yaml` and asserts the API is still published
   to `127.0.0.1` only. Promises about exposure are worth what they can be checked for.
8. **No new authentication mechanism**, no new dependency, no schema change, and the full suite stays
   green with no test weakened to accommodate the route.

If criterion 3 cannot be demonstrated, the slice is not done: two renderings of the same readings
that differ are the sixth copy arriving by another door.

## Changes

1. `app/services/market_page_service.py` — new. The assembly, taking a `MarketReadingService` and
   the window parameters, returning the document string. It joins the named path in the 10-4 rule.
2. `scripts/render_market_page.py` — keeps argument parsing, engine lifecycle and the file write,
   and loses `_build_document`.
3. `app/api/routes/market.py` — new. One `GET`, `HTMLResponse`, registered only when the flag is on.
4. `app/core/config.py` — `market_page_enabled: bool = False`.
5. `app/main.py` — conditional registration.
6. Safety block: the 10-4 rule narrowed as argued above, plus the new document-not-a-feed and
   bind-not-widened rules.
7. Tests, `docs/phase11-4-verification-report.md`, AGENTS.md, PLANS.md, README.md, operations.md,
   Notion, commit, push.

## Explicitly not in this slice

- **No authentication, no accounts, no login.** Named as the blocker for phone access.
- **No LAN or public exposure**, no tunnel, no TLS.
- **No JSON API for the readings.** A feed is a different product decision and a different risk.
- **No auto-refresh, no caching, no streaming.** The page is built per request from stored data.
- **Nothing about Telegram, `/explain`, the scheduler or ingestion.**
