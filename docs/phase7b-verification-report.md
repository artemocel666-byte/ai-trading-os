# Phase 7B Verification Report

Generated: 2026-07-29

## Scope

Phase 7B adds economic-calendar ingestion and the two event rules that consume it. The calendar half
of the Phase 2 adapters had never been called: `CALENDAR_ENABLED=true` fetched nothing and
`last_successful_calendar_fetch` had never been populated. Phase 7C shipped no `event_context.*`
rule because there were no events to read.

`PROJECT_PHASE = "phase_7b_calendar_ingestion_foundation"`

The rules are part of this slice deliberately. Shipping ingestion without a consumer is the exact
defect this project hit with the Phase 2 adapters and fixed in 7A; repeating it would leave calendar
data sitting unused.

## Key design decision: ingest forward, evaluate backward

The obvious rule is "high-impact release within the next 30 minutes". It is **not** buildable here.
`AnalysisService.build_snapshot` fetches events with the same backward-looking window as candles, and
`_select_events` in `app/domain/context_engine.py` further filters `scheduled_at <= as_of`, because
the Phase 3D snapshot proves no post-`as_of` data was used.

Storing future events is legitimate — calendars are published in advance, so it is not lookahead
bias — but surfacing them into a snapshot would change a Phase 3D safety invariant. That is a
separate, deliberate decision, not something to slip into an ingestion slice.

So the ingestion window straddles the tick (default 24h back, 72h forward) while the rules read only
what the snapshot legitimately exposes.

## Implementation

- `app/domain/entities/calendar_ingestion.py` — config/tick/decision/result models. Flatter than the
  7A equivalents because `get_events` takes a currency list, so there is one call and no per-item
  loop.
- `app/services/economic_calendar_ingestion_service.py` — window straddling `as_of`, duplicate-safe
  `economic_events.upsert_many`, `record_integration_health("calendar")` on success, provider errors
  recorded through `record_system_error` rather than raised. **An empty response is a success**, as
  quiet calendar days are normal — the same principle as weekends for candles.
- No wall-clock gate, carrying forward the Phase 7A fix: cadence belongs to the scheduler. A
  regression test drives a ragged `as_of` to keep it that way.
- `app/scheduler/jobs.py` / `worker.py` — the job registers only when both `CALENDAR_ENABLED` and
  `CALENDAR_INGESTION_ENABLED` are true. `register_jobs` no longer returns early after the
  market-data job, so both ingestion jobs can register independently.
- Two resolvers plus `foundation.event_context.v1`: high-impact event count (`LTE 0`) and minutes
  since the latest event (`GTE 30`). Rule count 9 → 11 across four rulesets.

## The UNAVAILABLE case, on purpose

`minutes_since_latest_event` reports `UNAVAILABLE` when the window holds no event at all. There is
genuinely nothing to measure, and substituting a large sentinel would read as a real observation.
`high_impact_event_count` stays a number in that case, because zero *is* a real measurement.

Consequence: a healthy window with a quiet calendar reports **10 of 11 rules passed**, not 11 of 11.
That is correct, and `/review` renders `(нет данных)` distinctly from a failure.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 100 source files |
| `uv run pytest` (excluding two pre-existing `.env`-placeholder collection failures) | Passed; 434 passed |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

### Offline end-to-end proof (stub provider, real Postgres)

```text
tick1 succeeded=True fetched=2 inserted=2 updated=0
  window 2026-07-28 09:38 .. 2026-08-01 09:38  (as_of inside: True)
tick2 (overlapping) inserted=0 updated=2   <- dedup
last_successful_calendar_fetch = 2026-07-29T09:38:08Z
```

The window straddles `as_of` as designed, and the second overlapping tick updates rather than
duplicates.

Then the same events reaching the rules through `/review EURUSD M15`:

```text
- события: 1 из 2; не пройдено: event_context.high_impact_event_count
```

The stub placed a high-impact EUR release 40 minutes before `as_of`. The count rule correctly failed
(a release did fall inside the window) while the elapsed-time rule passed (40 ≥ 30). That is the full
path: fetched → stored → picked up by the snapshot → evaluated → surfaced in the Telegram text.

The candle rules failed in the same run because market-data ingestion had been idle for a day —
unrelated to this phase, and itself a demonstration that the Phase 7C data-quality rules work.

## Remaining risks / notes

- **Live FMP verification was not performed.** It needs an API key from the user. The FMP economic
  calendar is often restricted on the free plan; if it is, the tick records a provider error and
  reports `failed` while the worker keeps running — that path is covered by
  `test_provider_failure_is_recorded_and_not_raised`.
- Ingested currencies are derived from the default pair in `worker.py` (EUR, USD) rather than being
  configurable through settings, matching the equivalent 7A limitation.
- Phase 7D remains gated on accumulating history; as of this phase storage held roughly one day of
  M15 candles, too thin to re-derive the 7C thresholds.
