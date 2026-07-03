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
