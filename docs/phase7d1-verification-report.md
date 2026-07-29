# Phase 7D-1 Verification Report

Generated: 2026-07-29

## Scope

Phase 7D-1 adds a manual historical market-data backfill. Phase 7D must re-derive the Phase 7C
thresholds from a real distribution, and the Phase 7C report flags the two-window calibration as the
weakest part of that slice. Storage held roughly one day of M15 candles, so replaying it would have
reproduced the same thin sample with more ceremony. Waiting for the 15-minute ingestion job to
accumulate months of history was the slow path; backfill is the fast one, deferred in Phase 7A with
the note that replay work would show how much was needed. It has.

`PROJECT_PHASE = "phase_7d1_historical_backfill_foundation"`

Phase 7D is therefore two slices: **7D-1 backfill** (this report) and **7D-2 replay validation**,
still pending.

## Implementation

- `app/domain/entities/backfill.py` — `BackfillChunkResult` and `BackfillResult`, frozen, with the
  same validator discipline as the 7A ingestion models: a failed chunk reports no stored counts,
  stored counts never exceed fetched, and `succeeded` is only true when no chunk failed and none
  looked truncated.
- `app/services/market_data_backfill_service.py` — `backfill_chunks()` is a pure function returning
  ordered, contiguous, oldest-first chunk bounds, so the chunking maths is testable without a
  provider or a clock. Chunk width is `min(chunk_candles × TIMEFRAME_TO_DELTA[timeframe],
  provider_max_request_range)`. Per-chunk failure isolation carries over from 7A; `sleep` is injected
  so tests do not wait.
- `scripts/backfill_market_data.py` — argparse CLI with `--dry-run`, exiting non-zero when any chunk
  failed or was flagged.
- Never scheduled. `test_phase7d1_backfill_is_never_scheduled` asserts backfill is not referenced
  from `app/scheduler/`; on a timer it would spend provider quota repeatedly for data already stored.

## The risk this slice was built around: silent truncation

`app/adapters/twelve_data.py` sends no `outputsize`, so a provider-side result cap could return only
the newest bars of a chunk and drop the oldest. The backfill would then "succeed", the database would
look fuller, and 7D-2 would calibrate on data with invisible holes.

Detection is by **range coverage, not by count**. A cap drops the oldest bars, so the first returned
candle lands well after the requested chunk start; a chunk is flagged when that leading gap exceeds a
quarter of the chunk duration. Counting alone would produce false alarms, since a chunk spanning a
weekend legitimately returns fewer candles. An empty chunk is a success and is never flagged — a
closed market returns nothing, which is no evidence either way.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed; 150 files left unchanged |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 102 source files |
| `uv run pytest` | Passed; 507 passed, 7 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

### Offline proof (stub provider, real Postgres)

Four M15 chunks over an 8-day range, run three times against the Dockerized database:

```text
run1 succeeded=True chunks=4 fetched=768 inserted=768 updated=0 truncated=0
  rows in db = 768
run2 (re-run) succeeded=True inserted=0 updated=768  <- dedup
  rows in db = 768
run3 (truncating stub) succeeded=False truncated_chunks=4 of 4
cleanup: rows in db = 0
```

Candles land, a re-run of the same range updates instead of duplicating, and a stub that withholds
the oldest 60% of each chunk is caught on every chunk and makes the run not-succeeded (the CLI exits
non-zero on that result).

### Live measurement — does `outputsize` truncation actually occur?

This is the measurement Phase 7D-2 depends on. Real Twelve Data key, EURUSD.

30 days of M15 at the default chunk size (10.4-day chunks):

```text
Plan: EURUSD M15 2026-06-29T11:42Z..2026-07-29T11:42Z -> 3 request(s), delay 8.0s between them
  [1] ... fetched=999 inserted=999 updated=0
  [2] ... fetched=999 inserted=999 updated=0
  [3] ... fetched=879 inserted=724 updated=155
Total: fetched=2877 inserted=2722 updated=155 failed_chunks=0 truncated_chunks=0
```

999 per chunk looks like a round-number cap, so coverage was checked directly rather than trusted:

```text
chunk 1  stored min=2026-06-29 11:45Z  max=2026-07-09 21:15Z  count=999
chunk 2  stored min=2026-07-09 21:45Z  max=2026-07-20 07:15Z
chunk 3  stored min=2026-07-20 07:45Z  max=2026-07-29 11:15Z
```

Each chunk's oldest stored candle sits at the requested start, not after it. 999 is simply what a
10.4-day window holds: 10.4 days × 96 candles/day ≈ 999. **No truncation.**

A deliberate probe of a much larger single request — one 31-day chunk, the adapter's maximum range:

```text
  [1] 2026-06-28T11:44Z .. 2026-07-29T11:44Z fetched=2975 inserted=98 updated=2877
```

2 975 of a possible 2 976. So there is no cap anywhere near the default chunk size, and the whole
allowed range can be requested in one call if a future slice needs it. The conservative default stays
as-is: the detector is cheap, and a cap that appears later must not pass silently.

### History now stored

```text
Plan: EURUSD M15 2026-01-30..2026-07-29 -> 18 request(s)
Total: fetched=17171 inserted=14199 updated=2972 failed_chunks=0 truncated_chunks=0

Plan: EURUSD H1 2026-01-30..2026-07-29 -> 6 request(s)
Total: fetched=4292 inserted=4205 updated=87 failed_chunks=0 truncated_chunks=0
```

| Timeframe | Rows | Range |
| --- | --- | --- |
| M15 | 17 174 | 2026-01-30 11:45Z .. 2026-07-29 11:15Z |
| H1 | 4 292 | 2026-01-30 12:00Z .. 2026-07-29 10:00Z |

`candles` total relation size: 8 224 kB. Six months of both timeframes cost 24 requests against a
free tier of roughly 800 per day, and about 8 MB of disk. Neither quota nor storage is a constraint
on going further back.

Gap histogram for the stored twelve_data EURUSD M15 series: 2 874 gaps of 15 minutes and 2 of 30
minutes — no weekend discontinuities. The provider returns a continuous series for this pair, which
is worth knowing before 7D-2 reasons about session structure; the truncation detector does not depend
on it, since it measures coverage rather than counts.

## Remaining risks / notes

- The truncation threshold (a leading gap over 25% of the chunk) was not exercised against a real
  provider cap, because no cap appeared. It is proven only against the stub. If a cap is introduced
  later, the first evidence will be a flagged chunk — which is the intended behaviour, but the exact
  threshold has no live calibration behind it.
- Backfill covers EURUSD only, as passed on the command line. Other pairs need separate runs.
- Chunk 1 of the 180-day M15 run fetched 912 rather than 999. That is the edge of the provider's
  available history for the range, not a failure, and it was correctly not flagged.
- 7C thresholds are unchanged by this slice. Re-deriving them from the now-stored six months is
  Phase 7D-2.
