from collections.abc import Mapping
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import redact_text
from app.core.time import normalize_to_utc, utc_now
from app.domain.entities import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.entities.data_quality import UpsertResult
from app.domain.entities.forward_outcome import ForwardOutcomeRecord
from app.domain.entities.interest_rate import InterestRate
from app.domain.entities.outcome import OutcomeKind
from app.domain.entities.pipeline_decision import PipelineDecisionStatus
from app.domain.entities.readiness import SnapshotDigestStatus, SnapshotNotificationDedupKey
from app.domain.entities.scheduled_digest import ScheduledDigestDeliveryRecord
from app.domain.entities.signal_contract import SignalDirection
from app.domain.value_objects import CurrencyPair
from app.persistence.models import (
    AuditLogModel,
    CandleModel,
    EconomicEventModel,
    ErrorEventModel,
    ForwardOutcomeRecordModel,
    InterestRateModel,
    ScheduledDigestDeliveryModel,
    SystemStateModel,
)


def _candle_from_model(row: CandleModel) -> Candle:
    return Candle(
        provider=row.provider,
        pair=CurrencyPair(value=row.pair),
        timeframe=Timeframe(row.timeframe),
        open_time=row.open_time,
        close_time=row.close_time,
        open=row.open,
        high=row.high,
        low=row.low,
        close=row.close,
        volume=row.volume,
        is_closed=row.is_closed,
    )


def _event_from_model(row: EconomicEventModel) -> EconomicEvent:
    return EconomicEvent(
        provider=row.provider,
        provider_event_id=row.provider_event_id,
        title=row.title,
        currency=row.currency,
        country=row.country,
        impact=EconomicImpact(row.impact),
        scheduled_at=row.scheduled_at,
        actual=row.actual,
        forecast=row.forecast,
        previous=row.previous,
        actual_raw=row.actual_raw,
        forecast_raw=row.forecast_raw,
        previous_raw=row.previous_raw,
        fetched_at=row.fetched_at,
    )


def _forward_outcome_from_model(row: ForwardOutcomeRecordModel) -> ForwardOutcomeRecord:
    return ForwardOutcomeRecord(
        pair=CurrencyPair(value=row.pair),
        timeframe=Timeframe(row.timeframe),
        as_of=row.as_of,
        direction=SignalDirection(row.direction),
        anchor_price=row.anchor_price,
        entry_min=row.entry_min,
        entry_max=row.entry_max,
        stop_loss=row.stop_loss,
        take_profit_1=row.take_profit_1,
        decision_status=PipelineDecisionStatus(row.decision_status),
        market_open=row.market_open,
        failed_rule_ids=tuple(row.failed_rule_ids_json or ()),
        pipeline_version=row.pipeline_version,
        ruleset_versions=tuple(row.ruleset_versions_json or ()),
        decision_fingerprint=row.decision_fingerprint,
        entry_band_multiplier=row.entry_band_multiplier,
        stop_multiplier=row.stop_multiplier,
        target_multiplier=row.target_multiplier,
        horizon_candles=row.horizon_candles,
        project_phase=row.project_phase,
        recorded_at=row.recorded_at,
        outcome_kind=OutcomeKind(row.outcome_kind) if row.outcome_kind is not None else None,
        bars_to_resolution=row.bars_to_resolution,
        resolved_at=row.resolved_at,
    )


def _delivery_from_model(row: ScheduledDigestDeliveryModel) -> ScheduledDigestDeliveryRecord:
    return ScheduledDigestDeliveryRecord(
        project_phase=row.project_phase,
        dedup_key=SnapshotNotificationDedupKey(value=row.dedup_key),
        delivered_at=row.delivered_at,
        sender_name=row.sender_name,
        readiness_status=(
            SnapshotDigestStatus(row.readiness_status) if row.readiness_status is not None else None
        ),
        item_count=row.item_count,
        ready_count=row.ready_count,
        incomplete_count=row.incomplete_count,
        blocked_count=row.blocked_count,
        items_summary=row.items_summary,
        payload_preview=row.payload_preview,
    )


class SqlAlchemySystemStateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, key: str) -> Any | None:
        row = await self._session.get(SystemStateModel, key)
        return None if row is None else row.value_json

    async def set(self, key: str, value: Any) -> None:
        row = await self._session.get(SystemStateModel, key)
        if row is None:
            self._session.add(SystemStateModel(key=key, value_json=value))
            return
        row.value_json = value
        row.updated_at = utc_now()

    async def get_all(self) -> dict[str, Any]:
        result = await self._session.execute(select(SystemStateModel))
        rows = result.scalars().all()
        return {row.key: row.value_json for row in rows}


class SqlAlchemyAuditLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(
        self,
        *,
        event_type: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        actor: str | None = None,
        before_json: Mapping[str, Any] | None = None,
        after_json: Mapping[str, Any] | None = None,
    ) -> None:
        self._session.add(
            AuditLogModel(
                event_type=event_type,
                entity_type=entity_type,
                entity_id=entity_id,
                actor=actor,
                before_json=dict(before_json) if before_json is not None else None,
                after_json=dict(after_json) if after_json is not None else None,
            )
        )


class SqlAlchemyErrorEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(
        self,
        *,
        error_code: str,
        severity: str,
        component: str,
        message_ru: str,
        technical_details: str | None = None,
        context_json: Mapping[str, Any] | None = None,
        resolved: bool = False,
    ) -> None:
        self._session.add(
            ErrorEventModel(
                error_code=error_code,
                severity=severity,
                component=component,
                message_ru=message_ru,
                technical_details=redact_text(technical_details) if technical_details else None,
                context_json=dict(context_json) if context_json is not None else None,
                resolved=resolved,
            )
        )


class SqlAlchemyCandleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_many(self, candles: list[Candle]) -> UpsertResult:
        inserted = 0
        updated = 0
        for candle in candles:
            result = await self._session.execute(
                select(CandleModel).where(
                    CandleModel.provider == candle.provider,
                    CandleModel.pair == candle.pair.value,
                    CandleModel.timeframe == candle.timeframe.value,
                    CandleModel.open_time == candle.open_time,
                )
            )
            row = result.scalar_one_or_none()
            if row is None:
                self._session.add(
                    CandleModel(
                        provider=candle.provider,
                        pair=candle.pair.value,
                        timeframe=candle.timeframe.value,
                        open_time=candle.open_time,
                        close_time=candle.close_time,
                        open=candle.open,
                        high=candle.high,
                        low=candle.low,
                        close=candle.close,
                        volume=candle.volume,
                        is_closed=True,
                    )
                )
                inserted += 1
                continue
            row.close_time = candle.close_time
            row.open = candle.open
            row.high = candle.high
            row.low = candle.low
            row.close = candle.close
            row.volume = candle.volume
            row.is_closed = True
            updated += 1
        return UpsertResult(inserted=inserted, updated=updated)

    async def list_range(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        start_at: datetime,
        end_at: datetime,
        provider: str | None = None,
    ) -> list[Candle]:
        start_utc = normalize_to_utc(start_at)
        end_utc = normalize_to_utc(end_at)
        query = select(CandleModel).where(
            CandleModel.pair == pair.value,
            CandleModel.timeframe == timeframe.value,
            CandleModel.open_time >= start_utc,
            CandleModel.close_time <= end_utc,
            CandleModel.is_closed.is_(True),
        )
        if provider is not None:
            query = query.where(CandleModel.provider == provider)
        result = await self._session.execute(
            query.order_by(CandleModel.open_time.asc(), CandleModel.provider.asc())
        )
        return [_candle_from_model(row) for row in result.scalars().all()]

    async def newest_close_times(
        self,
        *,
        timeframe: Timeframe,
        provider: str | None = None,
    ) -> dict[str, datetime]:
        query = (
            select(CandleModel.pair, func.max(CandleModel.close_time))
            .where(
                CandleModel.timeframe == timeframe.value,
                CandleModel.is_closed.is_(True),
            )
            .group_by(CandleModel.pair)
        )
        if provider is not None:
            query = query.where(CandleModel.provider == provider)
        result = await self._session.execute(query)
        return {pair: normalize_to_utc(newest) for pair, newest in result.all()}


class SqlAlchemyEconomicEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_many(self, events: list[EconomicEvent]) -> UpsertResult:
        inserted = 0
        updated = 0
        for event in events:
            result = await self._session.execute(
                select(EconomicEventModel).where(
                    EconomicEventModel.provider == event.provider,
                    EconomicEventModel.provider_event_id == event.provider_event_id,
                )
            )
            row = result.scalar_one_or_none()
            if row is None:
                self._session.add(
                    EconomicEventModel(
                        provider=event.provider,
                        provider_event_id=event.provider_event_id,
                        title=event.title,
                        currency=event.currency,
                        country=event.country,
                        impact=event.impact.value,
                        scheduled_at=event.scheduled_at,
                        actual=event.actual,
                        forecast=event.forecast,
                        previous=event.previous,
                        actual_raw=event.actual_raw,
                        forecast_raw=event.forecast_raw,
                        previous_raw=event.previous_raw,
                        fetched_at=event.fetched_at,
                    )
                )
                inserted += 1
                continue
            row.title = event.title
            row.currency = event.currency
            row.country = event.country
            row.impact = event.impact.value
            row.scheduled_at = event.scheduled_at
            row.actual = event.actual
            row.forecast = event.forecast
            row.previous = event.previous
            row.actual_raw = event.actual_raw
            row.forecast_raw = event.forecast_raw
            row.previous_raw = event.previous_raw
            row.fetched_at = event.fetched_at
            updated += 1
        return UpsertResult(inserted=inserted, updated=updated)

    async def list_window(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
        currencies: list[str] | None = None,
        provider: str | None = None,
    ) -> list[EconomicEvent]:
        start_utc = normalize_to_utc(start_at)
        end_utc = normalize_to_utc(end_at)
        query = select(EconomicEventModel).where(
            EconomicEventModel.scheduled_at >= start_utc,
            EconomicEventModel.scheduled_at < end_utc,
        )
        if currencies is not None:
            query = query.where(EconomicEventModel.currency.in_(currencies))
        if provider is not None:
            query = query.where(EconomicEventModel.provider == provider)
        result = await self._session.execute(
            query.order_by(
                EconomicEventModel.scheduled_at.asc(),
                EconomicEventModel.currency.asc(),
                EconomicEventModel.provider_event_id.asc(),
            )
        )
        return [_event_from_model(row) for row in result.scalars().all()]


class SqlAlchemyForwardOutcomeRepository:
    """Append-then-settle storage. A stored plan is never rewritten, only settled."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_missing(self, records: list[ForwardOutcomeRecord]) -> int:
        inserted = 0
        for record in records:
            existing = await self._session.execute(self._identity_query(record))
            if existing.scalar_one_or_none() is not None:
                # Deliberately not an update. The plan was registered before its outcome existed,
                # and overwriting it on a later tick would quietly destroy the one property that
                # makes this ledger worth more than a replay.
                continue
            self._session.add(
                ForwardOutcomeRecordModel(
                    pair=record.pair.value,
                    timeframe=record.timeframe.value,
                    as_of=record.as_of,
                    direction=record.direction.value,
                    anchor_price=record.anchor_price,
                    entry_min=record.entry_min,
                    entry_max=record.entry_max,
                    stop_loss=record.stop_loss,
                    take_profit_1=record.take_profit_1,
                    decision_status=record.decision_status.value,
                    market_open=record.market_open,
                    failed_rule_ids_json=list(record.failed_rule_ids),
                    pipeline_version=record.pipeline_version,
                    ruleset_versions_json=list(record.ruleset_versions),
                    decision_fingerprint=record.decision_fingerprint,
                    entry_band_multiplier=record.entry_band_multiplier,
                    stop_multiplier=record.stop_multiplier,
                    target_multiplier=record.target_multiplier,
                    horizon_candles=record.horizon_candles,
                    project_phase=record.project_phase,
                    recorded_at=record.recorded_at,
                    outcome_kind=(
                        record.outcome_kind.value if record.outcome_kind is not None else None
                    ),
                    bars_to_resolution=record.bars_to_resolution,
                    resolved_at=record.resolved_at,
                )
            )
            inserted += 1
        return inserted

    async def list_pending(
        self,
        *,
        limit: int,
        as_of_at_or_before: datetime | None = None,
    ) -> list[ForwardOutcomeRecord]:
        query = select(ForwardOutcomeRecordModel).where(
            ForwardOutcomeRecordModel.outcome_kind.is_(None)
        )
        if as_of_at_or_before is not None:
            query = query.where(
                ForwardOutcomeRecordModel.as_of <= normalize_to_utc(as_of_at_or_before)
            )
        result = await self._session.execute(
            query.order_by(
                ForwardOutcomeRecordModel.as_of.asc(),
                ForwardOutcomeRecordModel.pair.asc(),
                ForwardOutcomeRecordModel.timeframe.asc(),
                ForwardOutcomeRecordModel.direction.asc(),
            ).limit(limit)
        )
        return [_forward_outcome_from_model(row) for row in result.scalars().all()]

    async def apply_outcomes(self, records: list[ForwardOutcomeRecord]) -> int:
        settled = 0
        for record in records:
            if record.outcome_kind is None:
                continue
            result = await self._session.execute(self._identity_query(record))
            row = result.scalar_one_or_none()
            if row is None or row.outcome_kind is not None:
                # Already settled by an earlier tick, or gone. Either way the stored answer stands:
                # an outcome written twice would be a second look at the same future.
                continue
            row.outcome_kind = record.outcome_kind.value
            row.bars_to_resolution = record.bars_to_resolution
            row.resolved_at = record.resolved_at
            settled += 1
        return settled

    async def list_recorded(
        self,
        *,
        pair: CurrencyPair | None = None,
        timeframe: Timeframe | None = None,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> list[ForwardOutcomeRecord]:
        query = select(ForwardOutcomeRecordModel)
        if pair is not None:
            query = query.where(ForwardOutcomeRecordModel.pair == pair.value)
        if timeframe is not None:
            query = query.where(ForwardOutcomeRecordModel.timeframe == timeframe.value)
        if start_at is not None:
            query = query.where(ForwardOutcomeRecordModel.as_of >= normalize_to_utc(start_at))
        if end_at is not None:
            query = query.where(ForwardOutcomeRecordModel.as_of <= normalize_to_utc(end_at))
        result = await self._session.execute(
            query.order_by(
                ForwardOutcomeRecordModel.as_of.asc(),
                ForwardOutcomeRecordModel.pair.asc(),
                ForwardOutcomeRecordModel.timeframe.asc(),
                ForwardOutcomeRecordModel.direction.asc(),
            )
        )
        return [_forward_outcome_from_model(row) for row in result.scalars().all()]

    @staticmethod
    def _identity_query(record: ForwardOutcomeRecord) -> Any:
        return select(ForwardOutcomeRecordModel).where(
            ForwardOutcomeRecordModel.pair == record.pair.value,
            ForwardOutcomeRecordModel.timeframe == record.timeframe.value,
            ForwardOutcomeRecordModel.as_of == record.as_of,
            ForwardOutcomeRecordModel.direction == record.direction.value,
        )


class SqlAlchemyScheduledDigestDeliveryStore:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists(self, dedup_key: SnapshotNotificationDedupKey) -> bool:
        result = await self._session.execute(
            select(ScheduledDigestDeliveryModel.dedup_key).where(
                ScheduledDigestDeliveryModel.dedup_key == dedup_key.value
            )
        )
        return result.scalar_one_or_none() is not None

    async def record(self, record: ScheduledDigestDeliveryRecord) -> None:
        statement = (
            postgresql_insert(ScheduledDigestDeliveryModel)
            .values(
                dedup_key=record.dedup_key.value,
                project_phase=record.project_phase,
                delivered_at=record.delivered_at,
                sender_name=record.sender_name,
                readiness_status=(
                    record.readiness_status.value if record.readiness_status is not None else None
                ),
                item_count=record.item_count,
                ready_count=record.ready_count,
                incomplete_count=record.incomplete_count,
                blocked_count=record.blocked_count,
                items_summary=record.items_summary,
                payload_preview=record.payload_preview,
            )
            .on_conflict_do_nothing(index_elements=[ScheduledDigestDeliveryModel.dedup_key])
        )
        await self._session.execute(statement)

    async def get(
        self,
        dedup_key: SnapshotNotificationDedupKey,
    ) -> ScheduledDigestDeliveryRecord | None:
        result = await self._session.execute(
            select(ScheduledDigestDeliveryModel).where(
                ScheduledDigestDeliveryModel.dedup_key == dedup_key.value
            )
        )
        row = result.scalar_one_or_none()
        return None if row is None else _delivery_from_model(row)


class SqlAlchemyInterestRateRepository:
    """Phase 9D-3. Duplicate-safe by currency and month, like every other store here.

    A month arriving twice is the source revising one observation, not publishing a second one, so
    it updates rather than inserts.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_many(self, rates: list[InterestRate]) -> UpsertResult:
        inserted = 0
        updated = 0
        for rate in rates:
            result = await self._session.execute(
                select(InterestRateModel).where(
                    InterestRateModel.currency == rate.currency,
                    InterestRateModel.as_of == rate.as_of,
                )
            )
            row = result.scalar_one_or_none()
            if row is None:
                self._session.add(
                    InterestRateModel(
                        provider=rate.provider,
                        source_series=rate.source_series,
                        currency=rate.currency,
                        as_of=rate.as_of,
                        annual_rate=rate.annual_rate,
                    )
                )
                inserted += 1
                continue
            row.provider = rate.provider
            row.source_series = rate.source_series
            row.annual_rate = rate.annual_rate
            updated += 1
        return UpsertResult(inserted=inserted, updated=updated)

    async def list_range(
        self,
        *,
        currency: str | None = None,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> list[InterestRate]:
        statement = select(InterestRateModel)
        if currency is not None:
            statement = statement.where(InterestRateModel.currency == currency.strip().upper())
        if start_at is not None:
            statement = statement.where(InterestRateModel.as_of >= normalize_to_utc(start_at))
        if end_at is not None:
            statement = statement.where(InterestRateModel.as_of <= normalize_to_utc(end_at))
        statement = statement.order_by(InterestRateModel.as_of, InterestRateModel.currency)
        result = await self._session.execute(statement)
        return [
            InterestRate(
                provider=row.provider,
                source_series=row.source_series,
                currency=row.currency,
                as_of=normalize_to_utc(row.as_of),
                annual_rate=row.annual_rate,
            )
            for row in result.scalars().all()
        ]
