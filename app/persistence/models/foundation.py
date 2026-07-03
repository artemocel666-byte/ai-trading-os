import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.core.time import utc_now
from app.persistence.database import Base

JSONB_TYPE = postgresql.JSONB().with_variant(JSON(), "sqlite")
UUID_PK = Uuid(as_uuid=True)


class SystemStateModel(Base):
    __tablename__ = "system_state"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    value_json: Mapped[Any] = mapped_column(JSONB_TYPE, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID_PK, primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    entity_type: Mapped[str | None] = mapped_column(String(120))
    entity_id: Mapped[str | None] = mapped_column(String(120))
    actor: Mapped[str | None] = mapped_column(String(120))
    before_json: Mapped[Any | None] = mapped_column(JSONB_TYPE)
    after_json: Mapped[Any | None] = mapped_column(JSONB_TYPE)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )


class ErrorEventModel(Base):
    __tablename__ = "error_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID_PK, primary_key=True, default=uuid.uuid4)
    error_code: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    component: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    message_ru: Mapped[str] = mapped_column(String(500), nullable=False)
    technical_details: Mapped[str | None] = mapped_column(String(2000))
    context_json: Mapped[Any | None] = mapped_column(JSONB_TYPE)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )


class CandleModel(Base):
    __tablename__ = "candles"
    __table_args__ = (
        UniqueConstraint("provider", "pair", "timeframe", "open_time", name="uq_candle_identity"),
        CheckConstraint("open > 0", name="ck_candles_open_positive"),
        CheckConstraint("high > 0", name="ck_candles_high_positive"),
        CheckConstraint("low > 0", name="ck_candles_low_positive"),
        CheckConstraint("close > 0", name="ck_candles_close_positive"),
        CheckConstraint("close_time > open_time", name="ck_candles_close_after_open"),
        CheckConstraint("volume IS NULL OR volume >= 0", name="ck_candles_volume_non_negative"),
        CheckConstraint("is_closed = true", name="ck_candles_is_closed"),
        Index("ix_candles_pair_timeframe_close_time", "pair", "timeframe", "close_time"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID_PK, primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    pair: Mapped[str] = mapped_column(String(6), nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    open_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    close_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    open: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    volume: Mapped[Decimal | None] = mapped_column(Numeric(24, 8))
    is_closed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class EconomicEventModel(Base):
    __tablename__ = "economic_events"
    __table_args__ = (
        UniqueConstraint("provider", "provider_event_id", name="uq_economic_events_provider_event"),
        Index("ix_economic_events_currency_scheduled", "currency", "scheduled_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID_PK, primary_key=True, default=uuid.uuid4)
    provider_event_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    country: Mapped[str | None] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    impact: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    actual: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    forecast: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    previous: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    actual_raw: Mapped[str | None] = mapped_column(String(200))
    forecast_raw: Mapped[str | None] = mapped_column(String(200))
    previous_raw: Mapped[str | None] = mapped_column(String(200))
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ScanModel(Base):
    __tablename__ = "scans"
    __table_args__ = (
        UniqueConstraint("pair", "m15_close_time", "strategy_version", name="uq_scan_identity"),
        Index("ix_scans_status_started", "status", "started_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID_PK, primary_key=True, default=uuid.uuid4)
    pair: Mapped[str] = mapped_column(String(6), nullable=False, index=True)
    m15_close_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    snapshot_id: Mapped[uuid.UUID | None] = mapped_column(UUID_PK)
    strategy_version: Mapped[str] = mapped_column(String(80), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_code: Mapped[str | None] = mapped_column(String(80))


class AgentReportModel(Base):
    __tablename__ = "agent_reports"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="ck_agent_reports_score_range"),
        Index("ix_agent_reports_scan_agent", "scan_id", "agent_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID_PK, primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scans.id"), nullable=False, index=True)
    agent_name: Mapped[str] = mapped_column(String(120), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    verdict: Mapped[str] = mapped_column(String(40), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[str] = mapped_column(String(20), nullable=False)
    summary_ru: Mapped[str] = mapped_column(String(2000), nullable=False)
    reasons_for_json: Mapped[Any] = mapped_column(JSONB_TYPE, nullable=False)
    reasons_against_json: Mapped[Any] = mapped_column(JSONB_TYPE, nullable=False)
    invalid_if_json: Mapped[Any] = mapped_column(JSONB_TYPE, nullable=False)
    evidence_json: Mapped[Any] = mapped_column(JSONB_TYPE, nullable=False)
    rule_version: Mapped[str] = mapped_column(String(80), nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class SignalModel(Base):
    __tablename__ = "signals"
    __table_args__ = (
        Index("uq_signals_fingerprint", "fingerprint", unique=True),
        Index("ix_signals_pair_status_valid_until", "pair", "status", "valid_until"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID_PK, primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scans.id"), nullable=False, index=True)
    fingerprint: Mapped[str] = mapped_column(String(160), nullable=False)
    pair: Mapped[str] = mapped_column(String(6), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    setup_score: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[str] = mapped_column(String(20), nullable=False)
    entry_min: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    entry_max: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    invalidation_price: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    stop_loss: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    take_profit_1: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    take_profit_2: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    valid_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancel_reason_ru: Mapped[str | None] = mapped_column(String(1000))
    strategy_version: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class PaperPositionModel(Base):
    __tablename__ = "paper_positions"
    __table_args__ = (Index("ix_paper_positions_status_created", "status", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID_PK, primary_key=True, default=uuid.uuid4)
    signal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("signals.id"), nullable=False, index=True
    )
    account_balance_before: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    risk_percent: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    risk_amount_eur: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    position_size: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    entry_price: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    entered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    stop_loss: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    take_profit_1: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    take_profit_2: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    status: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    result_eur: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    result_percent: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    result_r: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    spread_cost: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    slippage_cost: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
