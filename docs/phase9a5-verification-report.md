# Phase 9A-5 Verification Report — Provenance, and a Purge

Generated: 2026-08-07

`PROJECT_PHASE = "phase_9a5_market_data_provenance_foundation"`

The second remediation item from the full project review. Where 9A-4 stopped the pipeline trusting
data the market never produced, this one stops it trusting data *we* produced.

## What was in the database

| table | provider | rows | what it was |
| --- | --- | ---: | --- |
| candles | `local-seed` | 30 | demo seeder, EURUSD M15, 2026-07-13 and 07-22 |
| candles | `phase7a-proof` | 4 | GBPUSD stubs from the Phase 7A verification run |
| economic_events | `local-seed` | 3 | demo seeder |
| economic_events | `phase7b-proof` | 2 | CPI and NFP stubs from the Phase 7B verification run |

Two things make this worse than clutter.

**The seed candles collided with real ones.** All 30 sat on timestamps that `twelve_data` had also
filled, quoting **1.1005 where the market was at 1.1441** — four hundred pips out.
`MarketFeatureEngine` de-duplicates by `(open_time, provider)` and keeps the first; `local-seed`
sorts before `twelve_data`; so on every one of those thirty timestamps **the invented candle replaced
the real observation**. The only trace was a `DUPLICATE_CANDLE` issue, which nobody read as "a
fabricated price is being used".

**All five stored events were invented, and two of them were mine.** The `phase7b-proof` stubs were
HIGH impact and fired `event_context.high_impact_event_count` twelve times over six months of
calibration. Verification artefacts from one phase were shaping the thresholds of another.

## Two changes

### The rule: provenance decides, not plausibility

`REAL_MARKET_DATA_PROVIDERS` in `app/core/constants.py` names the providers whose rows are records of
a market. Everything else is fabricated by definition.

That is deliberately a whitelist keyed on the `provider` column rather than any check on the values.
No value check would have caught this: the seed candles were well-formed OHLC with sane highs and
lows, correctly ordered, in a plausible price range for a currency pair. They were simply not true.
A test ties the set to the adapters that exist, so a new provider must be declared or its rows read
as invented — failing in the direction of refusing rather than trusting.

### The guard: one door, closed by default

`load_history` in `scripts/replay_rules.py` is the single function every calibration this project has
ever run passed through. It now **refuses fabricated rows**, listing what it found. Replay, outcome
measurement and direction evaluation inherit it; test fixtures and deliberate experiments pass
`--allow-synthetic`, so nothing gets it by accident.

`scripts/purge_synthetic_data.py` removes the rows. Dry run by default, printing every provider it
would delete and how many fabricated candles collide with real ones.

## Verification

| Check | Result |
| --- | --- |
| `uv run ruff format .` | Passed |
| `uv run ruff check .` | Passed |
| `uv run mypy app` | Passed; no issues in 115 source files |
| `uv run pytest` | Passed; 684 passed, 9 skipped |
| `uv run python scripts/security_check.py` | Passed; exit code 0 |

A database dump was taken before the deletion. The purge removed 39 rows and a re-run reports
`nothing fabricated` in both tables.

### What moved, over six months of EURUSD M15

| measurement | before purge | after purge |
| --- | ---: | ---: |
| windows replayed | 17,082 | 17,053 |
| `market_data_complete` failures | 258 (1.51%) | 176 (1.03%) |
| `volatility_ratio` maximum | 10.798 | 9.348 |
| `volatility_ratio` fires | 5.70% | 5.33% |
| `max_close_drawdown_atr` p95 | 4.089 | 4.042 |
| `max_close_drawdown_atr` fires | 5.51% | 5.26% |
| `high_impact_event_count` fires | 12 windows | 0 — `NEVER_FIRES` |
| `minutes_since_latest_event` | 68 observed | 0 — `NOT_OBSERVED` |

Every line is a consequence worth naming:

- **29 fewer windows.** The duplicates were extra rows in the ordered series, so the replay had been
  walking thirty windows twice — once anchored on the real candle and once on the invented one.
- **82 fewer completeness failures.** A third of what looked like gaps in the provider's history was
  our own seeder colliding with it.
- **The volatility maximum fell by 13%.** The old extreme was the artificial jump between a real
  1.1441 and a seeded 1.1005 — a fabricated spike, sitting at the top of the distribution the
  volatility band was calibrated against.
- **Both event rules are now dead**, and honestly so: the calendar holds nothing. `replay_rules.py`
  exits non-zero and needs an explicit `--allow-quiet` for each, which is the acknowledgement
  mechanism Phase 7D-2 built for exactly this.

## What this does not fix

- **The thresholds still carry the contamination.** `volatility_ratio` and `max_close_drawdown_atr`
  were calibrated on the distribution that included the fabricated spike, and both distributions have
  now moved. Re-deriving them is the next item, not this one.
- **The demo seeder still writes to the same database.** It is a documented local tool and its rows
  are now detectable and refusable, which is the smaller of the two problems it caused. Giving it a
  separate database would be the larger fix.
- **`/review GBPUSD M15` still accepts any six uppercase letters.** With the four stray GBPUSD
  candles gone it now returns an empty BLOCKED report rather than a partial one, which is better but
  still not a validation.
