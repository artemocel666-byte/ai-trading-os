"""foundation schema

Revision ID: 0001_foundation_schema
Revises:
Create Date: 2026-07-02 00:00:00.000000
"""

from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_foundation_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "system_state",
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("value_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )
    system_state = sa.table(
        "system_state",
        sa.column("key", sa.String),
        sa.column("value_json", postgresql.JSONB),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    op.bulk_insert(
        system_state,
        [{"key": "scan_enabled", "value_json": False, "updated_at": datetime.now(UTC)}],
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("entity_type", sa.String(length=120), nullable=True),
        sa.Column("entity_id", sa.String(length=120), nullable=True),
        sa.Column("actor", sa.String(length=120), nullable=True),
        sa.Column("before_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("after_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])
    op.create_index("ix_audit_logs_event_type", "audit_logs", ["event_type"])

    op.create_table(
        "error_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("error_code", sa.String(length=80), nullable=False),
        sa.Column("severity", sa.String(length=30), nullable=False),
        sa.Column("component", sa.String(length=120), nullable=False),
        sa.Column("message_ru", sa.String(length=500), nullable=False),
        sa.Column("technical_details", sa.String(length=2000), nullable=True),
        sa.Column("context_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("resolved", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_error_events_component", "error_events", ["component"])
    op.create_index("ix_error_events_created_at", "error_events", ["created_at"])
    op.create_index("ix_error_events_error_code", "error_events", ["error_code"])
    op.create_index("ix_error_events_resolved", "error_events", ["resolved"])
    op.create_index("ix_error_events_severity", "error_events", ["severity"])

    op.create_table(
        "candles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("pair", sa.String(length=6), nullable=False),
        sa.Column("timeframe", sa.String(length=20), nullable=False),
        sa.Column("open_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("close_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Numeric(20, 10), nullable=False),
        sa.Column("high", sa.Numeric(20, 10), nullable=False),
        sa.Column("low", sa.Numeric(20, 10), nullable=False),
        sa.Column("close", sa.Numeric(20, 10), nullable=False),
        sa.Column("volume", sa.Numeric(24, 8), nullable=True),
        sa.Column("is_closed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "provider", "pair", "timeframe", "open_time", name="uq_candle_identity"
        ),
    )
    op.create_index("ix_candles_close_time", "candles", ["close_time"])
    op.create_index("ix_candles_pair", "candles", ["pair"])
    op.create_index(
        "ix_candles_pair_timeframe_close_time",
        "candles",
        ["pair", "timeframe", "close_time"],
    )
    op.create_index("ix_candles_timeframe", "candles", ["timeframe"])

    op.create_table(
        "economic_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider_event_id", sa.String(length=120), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("impact", sa.String(length=40), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actual", sa.Numeric(20, 6), nullable=True),
        sa.Column("forecast", sa.Numeric(20, 6), nullable=True),
        sa.Column("previous", sa.Numeric(20, 6), nullable=True),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_economic_events_currency", "economic_events", ["currency"])
    op.create_index(
        "ix_economic_events_currency_scheduled",
        "economic_events",
        ["currency", "scheduled_at"],
    )
    op.create_index("ix_economic_events_impact", "economic_events", ["impact"])
    op.create_index(
        "ix_economic_events_provider_event_id", "economic_events", ["provider_event_id"]
    )
    op.create_index("ix_economic_events_scheduled_at", "economic_events", ["scheduled_at"])

    op.create_table(
        "scans",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pair", sa.String(length=6), nullable=False),
        sa.Column("m15_close_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("strategy_version", sa.String(length=80), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pair", "m15_close_time", "strategy_version", name="uq_scan_identity"),
    )
    op.create_index("ix_scans_pair", "scans", ["pair"])
    op.create_index("ix_scans_status", "scans", ["status"])
    op.create_index("ix_scans_status_started", "scans", ["status", "started_at"])

    op.create_table(
        "agent_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_name", sa.String(length=120), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False),
        sa.Column("verdict", sa.String(length=40), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.String(length=20), nullable=False),
        sa.Column("summary_ru", sa.String(length=2000), nullable=False),
        sa.Column("reasons_for_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("reasons_against_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("invalid_if_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("evidence_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("rule_version", sa.String(length=80), nullable=False),
        sa.Column("model_version", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("score >= 0 AND score <= 100", name="ck_agent_reports_score_range"),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_reports_scan_agent", "agent_reports", ["scan_id", "agent_name"])
    op.create_index("ix_agent_reports_scan_id", "agent_reports", ["scan_id"])

    op.create_table(
        "signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fingerprint", sa.String(length=160), nullable=False),
        sa.Column("pair", sa.String(length=6), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False),
        sa.Column("setup_score", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.String(length=20), nullable=False),
        sa.Column("entry_min", sa.Numeric(20, 10), nullable=False),
        sa.Column("entry_max", sa.Numeric(20, 10), nullable=False),
        sa.Column("invalidation_price", sa.Numeric(20, 10), nullable=False),
        sa.Column("stop_loss", sa.Numeric(20, 10), nullable=False),
        sa.Column("take_profit_1", sa.Numeric(20, 10), nullable=False),
        sa.Column("take_profit_2", sa.Numeric(20, 10), nullable=False),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancel_reason_ru", sa.String(length=1000), nullable=True),
        sa.Column("strategy_version", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_signals_pair", "signals", ["pair"])
    op.create_index(
        "ix_signals_pair_status_valid_until", "signals", ["pair", "status", "valid_until"]
    )
    op.create_index("ix_signals_scan_id", "signals", ["scan_id"])
    op.create_index("ix_signals_status", "signals", ["status"])
    op.create_index("ix_signals_valid_until", "signals", ["valid_until"])
    op.create_index("uq_signals_fingerprint", "signals", ["fingerprint"], unique=True)

    op.create_table(
        "paper_positions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("signal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_balance_before", sa.Numeric(20, 2), nullable=False),
        sa.Column("risk_percent", sa.Numeric(8, 4), nullable=False),
        sa.Column("risk_amount_eur", sa.Numeric(20, 2), nullable=False),
        sa.Column("position_size", sa.Numeric(24, 8), nullable=False),
        sa.Column("entry_price", sa.Numeric(20, 10), nullable=False),
        sa.Column("entered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("stop_loss", sa.Numeric(20, 10), nullable=False),
        sa.Column("take_profit_1", sa.Numeric(20, 10), nullable=False),
        sa.Column("take_profit_2", sa.Numeric(20, 10), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("result_eur", sa.Numeric(20, 2), nullable=True),
        sa.Column("result_percent", sa.Numeric(10, 4), nullable=True),
        sa.Column("result_r", sa.Numeric(10, 4), nullable=True),
        sa.Column("spread_cost", sa.Numeric(20, 2), nullable=True),
        sa.Column("slippage_cost", sa.Numeric(20, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["signal_id"], ["signals.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_paper_positions_signal_id", "paper_positions", ["signal_id"])
    op.create_index("ix_paper_positions_status", "paper_positions", ["status"])
    op.create_index(
        "ix_paper_positions_status_created",
        "paper_positions",
        ["status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_paper_positions_status_created", table_name="paper_positions")
    op.drop_index("ix_paper_positions_status", table_name="paper_positions")
    op.drop_index("ix_paper_positions_signal_id", table_name="paper_positions")
    op.drop_table("paper_positions")
    op.drop_index("uq_signals_fingerprint", table_name="signals")
    op.drop_index("ix_signals_valid_until", table_name="signals")
    op.drop_index("ix_signals_status", table_name="signals")
    op.drop_index("ix_signals_scan_id", table_name="signals")
    op.drop_index("ix_signals_pair_status_valid_until", table_name="signals")
    op.drop_index("ix_signals_pair", table_name="signals")
    op.drop_table("signals")
    op.drop_index("ix_agent_reports_scan_id", table_name="agent_reports")
    op.drop_index("ix_agent_reports_scan_agent", table_name="agent_reports")
    op.drop_table("agent_reports")
    op.drop_index("ix_scans_status_started", table_name="scans")
    op.drop_index("ix_scans_status", table_name="scans")
    op.drop_index("ix_scans_pair", table_name="scans")
    op.drop_table("scans")
    op.drop_index("ix_economic_events_scheduled_at", table_name="economic_events")
    op.drop_index("ix_economic_events_provider_event_id", table_name="economic_events")
    op.drop_index("ix_economic_events_impact", table_name="economic_events")
    op.drop_index("ix_economic_events_currency_scheduled", table_name="economic_events")
    op.drop_index("ix_economic_events_currency", table_name="economic_events")
    op.drop_table("economic_events")
    op.drop_index("ix_candles_timeframe", table_name="candles")
    op.drop_index("ix_candles_pair_timeframe_close_time", table_name="candles")
    op.drop_index("ix_candles_pair", table_name="candles")
    op.drop_index("ix_candles_close_time", table_name="candles")
    op.drop_table("candles")
    op.drop_index("ix_error_events_severity", table_name="error_events")
    op.drop_index("ix_error_events_resolved", table_name="error_events")
    op.drop_index("ix_error_events_error_code", table_name="error_events")
    op.drop_index("ix_error_events_created_at", table_name="error_events")
    op.drop_index("ix_error_events_component", table_name="error_events")
    op.drop_table("error_events")
    op.drop_index("ix_audit_logs_event_type", table_name="audit_logs")
    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_table("system_state")
