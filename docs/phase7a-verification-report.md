# Phase 7A Verification Report

Generated: 2026-07-27

## Scope

Phase 7A adds the market-data ingestion service — the first code in the project that performs an
outbound provider call and stores the result. It closes the first of the two gaps found on
2026-07-22: production adapters existed since Phase 2 and providers were constructed in
`app/main.py`, but nothing ever called `get_closed_candles`, so enabling `MARKET_DATA_ENABLED`
fetched nothing and `last_successful_market_fetch` was permanently empty.

`PROJECT_PHASE = "phase_7a_market_data_ingestion_foundation"`

## Deliberate departure from the Phase 3H precedent

Phase 3H established "a worker callable exists, but no automatic loop is registered." Phase 7A
**registers the job**, because repeating that precedent would recreate the exact defect this phase
exists to fix. Safety is preserved by two independent gates instead: `MARKET_DATA_ENABLED` and
`MARKET_DATA_INGESTION_ENABLED`, both `false` by default. With either off, the worker registers no
ingestion job and the disabled provider raises before any network call.

## Design decisions

- **Rolling overlapping window.** `end = latest_closed_boundary(timeframe, as_of)`,
  `start = end - lookback_candles × TIMEFRAME_TO_DELTA`. Successive ticks deliberately overlap so
  short provider gaps heal on the next run; `candles.upsert_many` makes the overlap harmless.
- **An empty provider response is a success, not a failure.** The forex market is closed on weekends
  and an up-to-date window legitimately returns nothing. This is the single most important
  correctness rule in the slice and has a dedicated test.
- **Per-item failure isolation.** One failing pair must not abort the tick; it is recorded with
  `failed=True` and the remaining items still ingest. The tick counts as successful if at least one
  item succeeded, and only then is `record_integration_health("market_data")` called.
- **Provider errors are recorded, never raised into the scheduler**, via the existing
  `SystemStateService.record_system_error` path.
- **No first-run backfill.** The rolling window covers roughly the last 12 hours at defaults; deep
  history is a separate concern that 7D's replay work will size properly.

## Reuse

Almost everything already existed; this slice is wiring:
`MarketDataProvider` protocol (the service never depends on a concrete adapter),
`candles.upsert_many`, `latest_closed_boundary`, `TIMEFRAME_TO_DELTA`, `SnapshotScheduleItem` as the
ingestion item, `SystemStateService.record_integration_health`/`record_system_error`, and the Phase
3H `ScheduledDigestDeliveryService` Config/Tick/Decision/Result shape as the structural template.

## Files

Created:

- `app/domain/entities/ingestion.py`
- `app/services/market_data_ingestion_service.py`
- `tests/unit/test_market_data_ingestion_foundation.py`
- `docs/phase7a-verification-report.md`

Modified:

- `app/core/config.py`, `.env.example` (three new settings, all disabled/conservative by default)
- `app/core/constants.py` (phase bump), `app/domain/entities/__init__.py` (exports)
- `app/scheduler/jobs.py` (job + optional registration), `app/scheduler/worker.py` (construction,
  flag gate, provider-client cleanup in the existing `finally`)
- `AGENTS.md`, `PLANS.md`, `README.md`, `docs/operations.md`
- `tests/contract/test_safety_boundaries.py` (Phase 7A block) and the seven unit tests asserting the
  literal project-phase string

No migration was created: ingestion writes through the existing candles table.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed; 143 files unchanged |
| `uv run ruff check .` | Passed; all checks passed |
| `uv run mypy app` | Passed; no issues in 98 source files |
| `uv run pytest` (excluding two pre-existing `.env`-placeholder collection failures) | Passed; 405 passed |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

### Offline end-to-end proof (no API key, no network)

Ran the real `MarketDataIngestionService` with a stub provider against the Dockerized PostgreSQL,
using GBPUSD to keep it unambiguous against previously seeded EURUSD demo data:

```text
tick1 executed=True succeeded=True fetched=4 inserted=4 updated=0 failed=0
tick2 (overlap) inserted=0 updated=4  <- dedup proof
last_successful_market_fetch = 2026-07-27T18:20:53.079216+00:00
snapshot readiness=READY used_candles=4
```

This proves the full path: provider → service → duplicate-safe storage → system-state health marker →
readable back through the real `AnalysisService.build_snapshot`. The second tick confirms the
overlapping-window design updates rather than duplicates.

## Remaining risks / notes

- **Real-provider verification was not performed.** It requires a Twelve Data API key and is left to
  the user. Everything above is proven with a stub provider; the adapter itself has been covered by
  MockTransport contract tests since Phase 2.
- The default ingestion item list (EURUSD M15 + H1) is currently constructed in `worker.py` rather
  than being configurable through settings. If more pairs are needed, that is the place to change,
  and it may deserve promoting to configuration in a later slice.
- Docker integration tests were not re-run for this phase; host-level `pytest`/`ruff`/`mypy` plus the
  end-to-end proof above were used.
- Phase 7B (calendar ingestion) and 7C (real analytical rules) are the next tasks and may run in
  parallel.
