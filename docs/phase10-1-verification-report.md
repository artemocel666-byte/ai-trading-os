# Phase 10-1 Verification Report — Keeping the Universe Alive

Generated: 2026-08-20

`PROJECT_PHASE = "phase_10_1_live_universe"`

Pre-registered in [`docs/phase10-1-preregistration.md`](phase10-1-preregistration.md), **committed
before any code** (`8297a95`). Every criterion below was fixed in that document first.

## The eight criteria

| | criterion | result |
| --- | --- | --- |
| 1 | All 45 pairs requested; ≥44 return data; refusals named by pair and exception type | **Pass** — 45 requested, 44 stored, `NZDSEK → ProviderUnsupportedRequestError` |
| 2 | ≥44 pairs hold the newest expected bar, via `expected_open_times` | **Pass** — 44 fresh, 0 stale |
| 3 | Alarm silent on a weekday **and** on a weekend | **Pass** — asserted for Saturday and Sunday |
| 4 | **Alarm fires on a deliberately staled series** | **Pass** — in test, and on live data |
| 5 | A 45-pair sweep takes at least `44 × interval` | **Pass** — 353.1 s against a 352.0 s floor |
| 6 | 10 of 10 currencies refreshed by the scheduled path | **Pass** — 5,855 rows, 10 currencies |
| 7 | Cron trigger at a fixed UTC hour, unaffected by restarts | **Pass** — asserted on registration |
| 8 | The one-concept test covers pacing | **Pass** — and two more entries besides |

## Criterion 4, on real data rather than in a fixture

The pre-registration said the slice is not done without this one, because a check that has never
been seen to fire is not a check. It fired twice — once in a test, and once against production
state, where the before-and-after is the whole argument:

```
before   fresh=0   stale=44  absent=1   BEHIND
after    fresh=44  stale=0   absent=1   HEALTHY
```

Forty-four pairs were **five days behind** and nothing in the system had noticed, because until this
slice nothing was looking. `NZDSEK` is reported as **absent**, not stale, in both runs — it is the
pair the provider does not quote, and folding it into the stale list would have made the report
complain every day about a permanent fact until its reader stopped believing it.

## Checked before planning, and all four findings were real

**1. `latest_closed_boundary` raised `ValueError` for D1** — the daily job would have crashed before
its first request. This was the 9D-1 fault recurring in a sibling function: D1 had been added to
`TIMEFRAME_TO_DELTA` and not to the function that answers where the current candle ends.

Fixed at the root rather than patched: the boundary is now **derived from the delta map** instead of
branching per timeframe, so a timeframe added there is answered here for free. The test asserts it
for **every** member of the enum rather than for the three that exist today.

**2. No wall-clock gate in the ingestion service** — cadence belongs entirely to the trigger, so the
sweep runs on **cron at a fixed UTC hour**. A 1440-minute interval on a worker restarted daily by a
deploy or a closing laptop could go its whole life without firing, and the failure would look exactly
like nothing happening.

**3. No pacing between requests** — added, as one setting read in one place.

**4. `expected_open_times` already knew D1 is traded-days-only** — reused, so the weekend rule still
exists exactly once. Its deliberate over-exclusion of the whole weekend works in our favour: the
expected newest bar is never later than the newest that can exist, so a conservative expectation can
only stay quiet, never cry wrongly.

## What the live runs actually found

**8 seconds of pacing was not enough.** A full sweep at 8.0 s still drew two `ProviderRateLimitError`
refusals — 7.5 requests a minute against a limit of eight is no margin, and the retry path makes it
worse, since a retried request takes a second turn and briefly doubles the local rate.

**Raised to 12 seconds — deliberately not to just above the observed failure.** Nudging a threshold
past the worst sample is fitting it to the data it must judge, which is the mistake Phase 9D-1 named
when a malformed-row tolerance was set barely above the worst pair it had seen. Twelve seconds is
five a minute against a limit of eight, and costs a sweep of about nine minutes instead of six on a
job that runs at two in the morning.

The second sweep also showed the overlap working as designed: `inserted: 0, updated: 168` — every
bar re-asked for and none duplicated.

## Three faults repaired that the plan did not anticipate

- **`UnitOfWorkFactory` was written out identically in nine places** — eight service modules and one
  script. Harmless only while all nine agreed, which was true of every duplication this project has
  had to repair. It now has one home beside the thing it produces, and criterion 8's test pins it
  there.
- **The `UnitOfWork` protocol never declared `interest_rates`.** Phase 9D-3 gave the implementation
  the slot and left the interface without it; the only caller was a script, and `mypy` checks `app`
  alone, so nothing said the two had drifted. The first service to need rates found it immediately.
- **`MarketDataIngestionItemResult` had no `failure_reason`.** Criterion 1 requires a refusal to be
  named, so it gained the field the backfill result received in 9D-1 — the exception's **type name**
  only, never its message, because a provider message can quote a URL carrying the API key.

## Two safety rules changed, both deliberately

**The rate rule moved from existence to delivery**, the same move Phase 9D-2 made when a
cross-section legitimately needed to produce a direction. 9D-3 banned the word from four layers
because only a script fetched rates; putting the refresh on a schedule made ingestion a genuine
requirement in a service and in the scheduler. **Telegram and the API stay absolutely closed**, and
inside the service and scheduler layers only the named ingestion path may mention rates — a
formatter or a digest that started reading them still fails, which is the case that mattered.

**A substring ban matched ordinary English again.** "long" inside "belongs", exactly as "carry"
inside "carrying" did in 9D-4. Reworded rather than narrowing the matcher mid-phase, since making a
safety check narrower is a decision worth taking on its own. **Worth doing deliberately later**: these
term bans should match whole words.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` / `ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 134 source files |
| `uv run pytest` | Passed; **911 passed**, 9 skipped (16 new) |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |
| Live sweep | 45 requested, 44 stored, 353.1 s, floor 352.0 s |
| Live freshness | 44 fresh, 0 stale, 1 absent, HEALTHY |
| Live rate refresh | 10 of 10 currencies, 5,855 rows |

No schema change and no migration: freshness is computed, never stored.

## What this settles

Nothing about markets. The universe now refills itself daily, the rates weekly, and **something is
watching** — which was the precondition for a descriptive report to be worth writing at all. A report
on five-day-old data would have been worse than no report.

Phase 10-2 is the descriptive report itself, and it opens by making the honesty policy executable —
types that cannot render a median without its dispersion — and by reconciling `/review`, which still
shows a person a verdict from rules 9C-2 measured to separate nothing.
