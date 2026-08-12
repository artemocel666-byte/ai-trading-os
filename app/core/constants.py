PROJECT_PHASE = "phase_9c4_execution_cost_foundation"
STRATEGY_IMPLEMENTED = False
REAL_TRADING_ENABLED = False

FEATURE_SNAPSHOT_SCHEMA_VERSION = 1
CONTEXT_SNAPSHOT_SCHEMA_VERSION = 1
ANALYSIS_SNAPSHOT_SCHEMA_VERSION = 1

SYSTEM_STATE_SCAN_ENABLED = "scan_enabled"
SYSTEM_STATE_WORKER_HEARTBEAT = "worker_heartbeat"
SYSTEM_STATE_LAST_SUCCESSFUL_MARKET_FETCH = "last_successful_market_fetch"
SYSTEM_STATE_LAST_SUCCESSFUL_CALENDAR_FETCH = "last_successful_calendar_fetch"
SYSTEM_STATE_LAST_ERROR = "last_error"

DEFAULT_STRATEGY_VERSION = "foundation-v1"

#: Providers whose rows in `candles` and `economic_events` are records of a real market.
#:
#: The `provider` column is this project's provenance record, and it is the only thing separating an
#: observation from an invention. Seed and verification scripts write under their own names, so
#: anything outside this set is fabricated by definition — no heuristic on the values is needed.
#:
#: This exists because on 2026-08-07 the database was found holding 30 `local-seed` EURUSD candles
#: sitting on the same timestamps as real ones, quoting 1.1005 where the market was at 1.1441. The
#: de-duplication picks the alphabetically first provider, so the invented candle won every time.
REAL_MARKET_DATA_PROVIDERS = frozenset({"twelve_data", "fmp"})
