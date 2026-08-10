# Phase 9C-1 Verification Report — The Forward Outcome Ledger

Generated: 2026-08-10

`PROJECT_PHASE = "phase_9c1_forward_outcome_ledger_foundation"`

The first slice of Phase 9C, and the first time this project writes something down *before* it can
be checked. Every number published so far came from replaying stored history, which can always be
re-run with different settings until it flatters its author. A row in this ledger cannot be.

## What it does, and what it deliberately does not

On every closed window the worker fixes the levels for **both** directions and stores them with the
pipeline's verdict attached. A second tick, later and separately, reads candles that arrived
afterwards and settles the outcome onto the row.

- **No direction is chosen.** Both are recorded for every window, exactly as
  `scripts/measure_outcomes.py` measures both. The 9A-3 candidate is disproved and nothing has
  replaced it; a ledger that picked a side would be recording a strategy nobody has evidence for
  while looking pre-registered.
- **No account, balance, position size, or profit.** The unused `paper_positions` table from
  Phase 1 has fields for all four; filling them would mean inventing all four. It is left untouched
  and a safety test asserts the new table never grows those column names.
- **No costs.** OHLC is stored and spread is not, so every figure the ledger can support is gross. A
  zeroed cost column would read as a measured one.

## Why this is not a slower `measure_outcomes.py`

The fair objection is that a replay could compute the same numbers once the candles arrive. Three
things a stored forward record has that a replay never can:

1. **Pre-registration**, and it is checkable per row: `recorded_at` and `as_of` are both stored, so
   a genuine row shows a gap of at most one interval. A row written after its own future is
   self-identifying.
2. **What the live pipeline actually decided** — the verdict, the rules that failed, the ruleset
   versions, a fingerprint of the whole decision. A replay reconstructs that approximately at best:
   calendar rows arrive and get revised afterwards, and candles can be restated.
3. **A configuration change becomes a break in the data** rather than a silent rewrite of the past,
   because each row carries its own multipliers and horizon.

## The two ticks are separate on purpose

Recording never reads a forward candle, because it never queries past its own `as_of`. Resolution
never influences a plan, because every plan it touches was fixed on an earlier tick. The Phase 3D
invariant is enforced here by which tick owns which query rather than by remembering — and a safety
test asserts that both jobs are registered, never merged into one.

## Two guards carried over from earlier failures

**Provenance.** The candle query is filtered to `REAL_MARKET_DATA_PROVIDERS` before a window is
built. `scripts/replay_rules.py` got this guard offline in Phase 9A-5, after thirty fabricated rows
were found sitting on the same timestamps as real ones and winning the de-duplication every time.
The ledger is a new door onto the same data, and it gets the same lock. A test records a window
built entirely from `local-seed` candles and asserts nothing is written.

**Never settle early.** A plan whose horizon has not elapsed stays pending. Writing `TIMEOUT`
because candles had not arrived yet would turn a gap in ingestion into a measured result. Both the
entity and a `CHECK` constraint refuse a row that is half-settled.

Worth noting against `scripts/measure_outcomes.py`, which does not have this problem to solve and so
never solved it: its last `horizon_candles` windows are reported as `TIMEOUT` when in truth there
was no data to resolve them. About 5% of a five-day run. Not corrected here — it belongs to that
script — but recorded so the two are not read as identical.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed; 181 files unchanged |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 117 source files |
| `uv run pytest` | Passed; 727 passed, 9 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |
| `alembic upgrade head` → `downgrade -1` → `upgrade head` | Passed; reversible |
| jobs registered with the flag off | none — only `worker_heartbeat` and `application_health_check` |

Twenty-two new tests. The migration adds one table and drops nothing.

## Against real data

Run on a **throwaway database** seeded with real EURUSD M15 candles, not the project's own. Writing
verification rows into the real ledger would have put 384 records in it whose `recorded_at` sits days
after their `as_of` — indistinguishable at a glance from pre-registered ones, and exactly the kind of
quiet contamination Phase 9A-5 was about. The real `forward_outcome_records` table is empty.

192 record ticks over 2026-08-05 to 2026-08-07, then one resolve tick:

| | |
| --- | ---: |
| rows written | 384 (192 windows × 2 directions) |
| windows with no plan | 0 |
| settled by one resolve tick | 384 |
| still pending | 0 |
| **mismatches against a freshly computed `measure_outcome`** | **0** |

Zero is the number that matters. Both paths share `measure_outcome`, so what this tests is the thing
that could still drift: which candles each one calls "after the window". Strictly after `as_of`, in
both, on 384 real windows.

| verdict | rows |
| --- | ---: |
| READY_FOR_REVIEW | 224 |
| READY_WITH_WARNINGS | 160 |

41.7% warned, which matches `time_filter.session_name_allowed` firing at 40.3% in Phase 9A-8. The
warning tier is doing what 9A-4 built it to do: visible in the headline rather than buried.

| direction | settled | target% | ambiguous% | timeout% |
| --- | ---: | ---: | ---: | ---: |
| LONG | 192 | 31.54% | 0.00% | 22.40% |
| SHORT | 192 | 43.42% | 0.00% | 20.83% |

**These are two days and they mean nothing yet.** SHORT leading LONG is the same direction as the
six-month drift, which is the period rather than skill; the timeout rate is roughly double the
six-month figure; and zero ambiguity over 384 windows is consistent with the 0.63% rate but proves
nothing at this size. The ledger exists to accumulate a sample, and it has not accumulated one.

## What this opens, and does not answer

Recording every window with its verdict makes one comparison possible for the first time: **do
windows the rules accept resolve better than windows they block?** The eleven rules have been
calibrated on how often they fire, never on whether firing helps. That question needs a sample this
slice has only started to collect, and it is out of scope here.

## What it does not settle

- No direction. `direction_candidate.py` stays unwired, and a safety test asserts the ledger cannot
  import it.
- No delivery. Nothing about the ledger reaches Telegram or the API; that is 9B, and only if there
  is ever something worth delivering.
- No costs, still. Every figure above and every figure the ledger will ever produce is gross.
