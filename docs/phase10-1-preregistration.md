# Phase 10-1 Pre-registration — Keeping the Universe Alive

Written: 2026-08-18. **Committed before any code**, which is new. The seven measurement
pre-registrations lived in throwaway plan files and only their verification reports reached git; the
criteria below are therefore checkable against history rather than against memory.

## Context

Seven pre-registered measurements returned nothing, and 9D-4 explained why: what can be computed
from public data is already in the price. The product decision that followed is **context rather
than conclusion** — describe where things stand, never what they will do.

Every descriptive feature planned for 10-2 and 10-3 reads the daily universe. And the daily universe
is a **frozen snapshot**:

| timeframe | pairs | newest bar |
| --- | ---: | --- |
| D1 | 44 | **2026-08-15** — filled by hand, going stale daily |
| H1 | 2 | 2026-08-17 |
| M15 | 2 | 2026-08-17 |

The worker fetches one pair — `DEFAULT_INGESTION_PAIR = "EURUSD"` is hard-coded in
`app/scheduler/worker.py` — on M15 and H1. The 44 pairs and all 5,855 interest rates are manual
snapshots that depend on somebody remembering to run a script. **Nothing in the system notices when
they rot.**

A descriptive report on three-day-old data is worse than no report, so this slice comes first. It
adds no analytics and decides nothing about the product.

## Checked before planning, as 9D-1 taught

Four findings, and the first is a blocker that would have crashed the job before its first request.

**1. `latest_closed_boundary` raises `ValueError` for D1.** It handles M15 and H1 and nothing else
(`app/domain/readiness_engine.py:97`). `ingestion_window` calls it, so a daily item fails before any
network call. This is the **same half-addition as the `TIMEFRAME_TO_DELTA` fault in 9D-1**, in a
different function: D1 was added to the delta map and not to its sibling that answers "where does
the current candle end". The disease recurred because the two live in separate files.

**2. There is no wall-clock gate in the ingestion service.** `_decide` says so explicitly: cadence
is owned by the scheduler that calls `run_tick`, and every tick fetches. So the cadence is entirely
the scheduler's trigger, and a trigger that never fires is a silent, total failure.

**3. The adapter has retry and backoff but no pacing between requests.** Forty-four requests fired
back-to-back will hit a per-minute limit, and the failures will look like provider faults.

**4. `expected_open_times` in `app/domain/entities/data_quality.py` already knows D1 is
traded-days-only** (`TRADED_DAYS_ONLY_TIMEFRAMES`). The weekend rule exists once and must not be
written a second time.

## Design

**A second config and a second job, not more items on the existing one.** The existing tick fires
every 15 minutes; 44 daily items on it would be 4,224 requests a day. A separate
`MarketDataIngestionConfig` with its own trigger is 44. No new service class — `run_tick` already
loops over items and isolates a failing pair.

For scale: the universe costs **44 requests a day against the 192 the single-pair job already
spends**. The new work is cheaper than what is already running.

**A cron trigger at a fixed UTC hour, not an interval.** Given finding 2, a 1440-minute interval on
a worker that restarts daily — deploys, crashes, laptop sleep — may never fire at all. A cron
trigger fires regardless of when the process started. This is the first cron trigger in the project
and it is a deliberate addition, not an oversight in `register_jobs`.

**`latest_closed_boundary` gains D1 as truncation to UTC midnight, and the weekend stays out of it.**
A Friday bar closes at Saturday 00:00 UTC, so on any Saturday the truncation already lands on the
last real close. On a Sunday it lands one day past it, and that is **harmless for a window end**: we
request a range and store what comes back, and the lookback overlaps by design. The weekend belongs
in the freshness check, which is a question about what we hold, not about what to ask for.

**Pacing is one setting read by everyone.** A minimum interval between provider requests, in
`Settings`, applied inside the adapter, so the worker, the backfill script and any future caller
cannot disagree. The 9D-4 safety test that pins `RATE_LAG_MONTHS`, `shift_months` and `month_start`
to one file each gains a fourth entry.

**Freshness is measured by the job that fills, and recorded where it is already visible.** A script
nobody runs is the same silent rot in a new place. The daily tick computes staleness and calls the
existing `record_system_error`, so the existing status surface shows it without a new surface being
invented.

**Absent is not stale.** One of the 45 derived pairs has never had data because the provider does not
quote it. That is an absence, named as such, and it must never be counted as staleness — an alarm
that cries every day stops being read. The project's standing habit: absences named, never
substituted.

**All 45 pairs are requested every day, not the 44 that worked once.** A provider can start quoting a
pair. Freezing the list to what was observed in August 2026 would bake one observation into a
permanent assumption, which is exactly what deriving the universe from a currency set was meant to
prevent.

**Rates go on the same footing.** FRED is free and keyless and the series are monthly; a weekly tick
costs ten requests and removes the dependency on somebody remembering.

## Acceptance criteria — fixed here, before the code

All of the following, checked after one live run:

1. **All 45 pairs are requested.** At least 44 return data; every refusal is named by pair and by
   exception type name, never by message.
2. **D1 freshness:** for at least 44 pairs the newest stored `close_time` equals the latest expected
   trading day, computed through `expected_open_times` rather than a second weekend rule.
3. **The alarm is silent when it should be:** zero stale pairs on a weekday run, and **also** zero on
   a weekend run, where the newest bar is correctly Friday's.
4. **The alarm fires when it should:** a pair deliberately staled in a test — its newest bars removed
   — is reported as stale. A check that has never been seen to fire is not a check.
5. **Pacing is observed:** a 45-pair sweep takes at least `44 x minimum_interval` seconds. A pacing
   setting that is silently ignored is worse than none, because it invites raising the request count.
6. **Rates:** 10 of 10 currencies refreshed by the scheduled path, with the coverage report unchanged
   from 9D-3 apart from months the source has since published.
7. **The cron trigger survives a restart:** the next fire time is a fixed UTC hour and does not move
   when the worker is restarted.
8. **The one-concept test covers pacing**, alongside the three constants it already pins.

If criterion 4 cannot be demonstrated, the slice is not done, whatever the other seven say.

## Changes

1. `app/domain/readiness_engine.py` — `latest_closed_boundary` gains D1, with a test that names the
   9D-1 recurrence so the next sibling function is checked rather than assumed.
2. `app/core/config.py` — `provider_min_request_interval_seconds`.
3. `app/adapters/twelve_data.py` — pacing applied around every request.
4. `app/scheduler/jobs.py` — a cron-triggered daily universe job and a weekly rate job.
5. `app/scheduler/worker.py` — the universe config built from `universe_pairs()` rather than a
   hard-coded pair; the existing single-pair config untouched.
6. `app/domain/data_freshness.py` — new, pure: given what is stored and the calendar, which pairs are
   stale, which are absent, and by how much. No session, no query.
7. `scripts/report_data_freshness.py` — read-only, for reading the same answer by hand.
8. Tests, including all eight criteria above.
9. `docs/phase10-1-verification-report.md`, AGENTS.md, PLANS.md, README.md, operations.md, Notion.

## Explicitly not in this slice

- **No analytics, no percentiles, no decomposition, no correlations.** This ends with fresh data and
  a check that complains. The descriptive report is 10-2.
- **No H1 or M15 for the universe** — 1,056 and 4,224 requests a day, needed by nothing built or
  planned.
- **No COT.** That is 10-4.
- **No user-facing surface.** Nothing new reaches Telegram or the API; the freshness signal travels
  through the existing system-state path.
- **`/review` is not touched here.** It renders a verdict from rules 9C-2 measured to separate
  nothing, and reconciling that belongs with 10-2, where the honesty policy becomes types and tests.
- **No schema change**, so no migration. Freshness is computed, never stored.
