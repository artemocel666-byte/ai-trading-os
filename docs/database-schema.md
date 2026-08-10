# Database Schema

The initial schema is created by Alembic revision `0001_foundation_schema`.

## system_state

- Primary key: `key`.
- Fields: `value_json`, `updated_at`.
- Seed: `scan_enabled=false`.

## audit_logs

- Primary key: `id` UUID.
- Fields: `event_type`, `entity_type`, `entity_id`, `actor`, `before_json`, `after_json`, `created_at`.
- Indexes: `event_type`, `created_at`.

## error_events

- Primary key: `id` UUID.
- Fields: `error_code`, `severity`, `component`, `message_ru`, `technical_details`, `context_json`, `resolved`, `created_at`.
- Indexes: `error_code`, `severity`, `component`, `resolved`, `created_at`.

## candles

- Primary key: `id` UUID.
- Fields: provider, pair, timeframe, open/close times, OHLC, volume, closed flag, created time.
- Unique constraint: provider + pair + timeframe + open_time.
- Indexes: pair, timeframe, close time, pair + timeframe + close time.

## economic_events

- Primary key: `id` UUID.
- Fields: provider event ID, currency, country, title, impact, scheduled time, actual, forecast,
  previous, raw actual/forecast/previous values, provider, fetched time.
- Unique constraint from Phase 2 migration: provider + provider_event_id.
- Indexes: currency, impact, provider event ID, scheduled time, currency + scheduled time.

## scheduled_digest_deliveries

- Added by Alembic revision `0003_phase3i_digest_audit`.
- Primary key: `id` UUID.
- Fields: dedup key, project phase, delivered time, sender name, readiness status, item counts,
  ready/incomplete/blocked counts, item summary, neutral payload preview, created time.
- Unique constraint: dedup key.
- Indexes: delivered time, readiness status, project phase.
- Safety boundary: stores no Telegram tokens, chat IDs, provider secrets, strategy decisions,
  trading guidance, broker data, paper-trading records, or order execution data.

## scans

- Primary key: `id` UUID.
- Fields: pair, M15 close time, status, snapshot ID, strategy version, started/completed times, error code.
- Unique constraint: pair + m15_close_time + strategy_version.
- Indexes: pair, status, status + started_at.

## agent_reports

- Primary key: `id` UUID.
- Foreign key: `scan_id -> scans.id`.
- Fields: agent name, direction, verdict, score, confidence, Russian summary, reasons, invalidation rules, evidence, versions, created time.
- Constraint: score between 0 and 100.
- Indexes: scan ID, scan ID + agent name.

## signals

- Primary key: `id` UUID.
- Foreign key: `scan_id -> scans.id`.
- Fields: fingerprint, pair, direction, score, confidence, entry zone, invalidation, stop, targets, validity, status, delivery/cancel times, strategy version.
- Unique index: fingerprint.
- Indexes: pair, status, valid_until, scan ID, pair + status + valid_until.

## paper_positions

- Primary key: `id` UUID.
- Foreign key: `signal_id -> signals.id`.
- Fields: account balance, risk, paper position size, entry, stop, targets, status, result fields, costs, created time.
- Indexes: signal ID, status, status + created_at.
- **Unused since Phase 1, and deliberately so.** It assumes a direction, an account balance, a risk
  percentage and a spread cost — four things this project does not have and will not invent. Phase
  9C-1 added `forward_outcome_records` rather than fill it. Left in place because dropping a table
  is destructive and an empty one is harmless.

## forward_outcome_records

- Added by Alembic revision `0004_phase9c1_forward_outcomes`.
- Primary key: `id` UUID.
- Identity: pair, timeframe, `as_of`, direction — unique together, so an overlapping worker cadence
  cannot double-register a window.
- Plan, fixed at write time: anchor price, entry band, protective level, first target.
- What the pipeline said: decision status, `market_open` (nullable — the rule may be unevaluable),
  the ids of rules observed to fail.
- Provenance: pipeline version, ruleset versions, decision fingerprint, the multipliers and horizon
  in force, project phase, `recorded_at`.
- Outcome, written later and nullable until then: outcome kind, bars to resolution, `resolved_at`.
- Check constraints: the outcome kind and `resolved_at` are set together or not at all, and a
  pending row carries no resolution bar. A row cannot be half-settled.
- Indexes: pair, timeframe, `as_of`, decision status, (outcome kind + `as_of`) for the pending
  query, (pair + timeframe + `as_of`) for reading.
- Safety boundary: **no account, balance, position size, profit, or cost field**, and a contract
  test asserts none is ever added. A plan is never rewritten once stored; only the three outcome
  columns are ever written a second time, and only from `NULL`.
