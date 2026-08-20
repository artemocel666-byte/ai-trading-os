from collections.abc import Sequence
from datetime import datetime

from app.core.exceptions import ApplicationError, ErrorCode, ProviderError
from app.domain.entities.data_quality import TIMEFRAME_TO_DELTA
from app.domain.entities.ingestion import (
    MarketDataIngestionConfig,
    MarketDataIngestionDecision,
    MarketDataIngestionDecisionReason,
    MarketDataIngestionItemResult,
    MarketDataIngestionResult,
    MarketDataIngestionTick,
)
from app.domain.entities.market_data import Candle, Timeframe
from app.domain.entities.readiness import SnapshotScheduleItem
from app.domain.interfaces.providers import MarketDataProvider
from app.domain.interfaces.unit_of_work import UnitOfWorkFactory
from app.domain.readiness_engine import latest_closed_boundary
from app.services.system_state_service import SystemStateService

INGESTION_COMPONENT = "market_data_ingestion"


class MarketDataIngestionService:
    """Fetches closed candles from the market-data provider and stores them.

    This is read-only with respect to the provider and append/update-only with respect to
    storage. It never produces trading output: no directions, no price levels, no scoring,
    no AI calls, and no user-facing messages.
    """

    def __init__(
        self,
        *,
        config: MarketDataIngestionConfig,
        provider: MarketDataProvider,
        uow_factory: UnitOfWorkFactory,
        system_state_service: SystemStateService,
    ) -> None:
        self._config = config
        self._provider = provider
        self._uow_factory = uow_factory
        self._system_state_service = system_state_service

    async def run_tick(self, *, as_of: datetime) -> MarketDataIngestionResult:
        tick = MarketDataIngestionTick(as_of=as_of)
        decision = self._decide(tick)
        if not decision.should_fetch:
            return _skipped_result(tick=tick, decision=decision)

        item_results: list[MarketDataIngestionItemResult] = []
        for item in self._config.items:
            item_results.append(await self._ingest_item(item=item, as_of=tick.as_of))

        failed_item_count = sum(1 for result in item_results if result.failed)
        succeeded = failed_item_count < len(item_results)
        if succeeded:
            await self._system_state_service.record_integration_health("market_data")

        return MarketDataIngestionResult(
            tick=tick,
            decision=_decision(
                config=self._config,
                tick=tick,
                reason=MarketDataIngestionDecisionReason.COMPLETED,
                should_fetch=True,
            ),
            executed=True,
            skipped=False,
            succeeded=succeeded,
            item_results=tuple(item_results),
            total_fetched=sum(result.fetched_count for result in item_results),
            total_inserted=sum(result.inserted_count for result in item_results),
            total_updated=sum(result.updated_count for result in item_results),
            failed_item_count=failed_item_count,
        )

    async def _ingest_item(
        self,
        *,
        item: SnapshotScheduleItem,
        as_of: datetime,
    ) -> MarketDataIngestionItemResult:
        window_start, window_end = ingestion_window(
            timeframe=item.timeframe,
            as_of=as_of,
            lookback_candles=self._config.lookback_candles,
        )
        try:
            candles = await self._provider.get_closed_candles(
                item.pair,
                item.timeframe,
                window_start,
                window_end,
            )
            stored = await self._store_candles(candles)
        except Exception as error:
            await self._record_failure(error, item=item)
            return MarketDataIngestionItemResult(
                pair=item.pair,
                timeframe=item.timeframe,
                window_start=window_start,
                window_end=window_end,
                failed=True,
                failure_reason=type(error).__name__,
            )

        # An empty provider response is a normal outcome, not a failure: the forex market is
        # closed on weekends and holidays, and a fully up-to-date window returns nothing new.
        return MarketDataIngestionItemResult(
            pair=item.pair,
            timeframe=item.timeframe,
            window_start=window_start,
            window_end=window_end,
            fetched_count=len(candles),
            inserted_count=stored[0],
            updated_count=stored[1],
        )

    async def _store_candles(self, candles: Sequence[Candle]) -> tuple[int, int]:
        if not candles:
            return (0, 0)
        async with self._uow_factory() as uow:
            result = await uow.candles.upsert_many(list(candles))
            await uow.commit()
        return (result.inserted, result.updated)

    async def _record_failure(self, error: Exception, *, item: SnapshotScheduleItem) -> None:
        application_error = (
            error
            if isinstance(error, ApplicationError)
            else ProviderError(
                ErrorCode.PROVIDER_UNAVAILABLE,
                "Загрузка рыночных данных не удалась.",
                details={"pair": item.pair.value, "timeframe": item.timeframe.value},
            )
        )
        await self._system_state_service.record_system_error(
            application_error,
            component=INGESTION_COMPONENT,
            technical_details=f"{type(error).__name__}: {error}",
        )

    def _decide(self, tick: MarketDataIngestionTick) -> MarketDataIngestionDecision:
        # Cadence is owned by the scheduler that calls run_tick. Deliberately no wall-clock
        # gate here: ingestion windows overlap, so the exact firing moment is irrelevant, and
        # a clock-alignment check would silently skip every scheduler-driven tick.
        if not self._config.enabled:
            return _decision(
                config=self._config,
                tick=tick,
                reason=MarketDataIngestionDecisionReason.DISABLED,
                should_fetch=False,
            )
        if not self._config.items:
            return _decision(
                config=self._config,
                tick=tick,
                reason=MarketDataIngestionDecisionReason.NO_ITEMS,
                should_fetch=False,
            )
        return _decision(
            config=self._config,
            tick=tick,
            reason=MarketDataIngestionDecisionReason.COMPLETED,
            should_fetch=True,
        )


def ingestion_window(
    *,
    timeframe: Timeframe,
    as_of: datetime,
    lookback_candles: int,
) -> tuple[datetime, datetime]:
    """Return the rolling closed-candle window for one ingestion item.

    Windows deliberately overlap between ticks so that short provider gaps heal on the next
    run; duplicate-safe storage makes the overlap harmless.
    """
    if lookback_candles < 1:
        raise ValueError("lookback_candles must be at least one candle")
    window_end = latest_closed_boundary(timeframe=timeframe, as_of=as_of)
    window_start = window_end - (lookback_candles * TIMEFRAME_TO_DELTA[timeframe])
    return (window_start, window_end)


def _decision(
    *,
    config: MarketDataIngestionConfig,
    tick: MarketDataIngestionTick,
    reason: MarketDataIngestionDecisionReason,
    should_fetch: bool,
) -> MarketDataIngestionDecision:
    return MarketDataIngestionDecision(
        enabled=config.enabled,
        should_fetch=should_fetch,
        reason=reason,
        item_count=len(config.items),
        tick_as_of=tick.as_of,
    )


def _skipped_result(
    *,
    tick: MarketDataIngestionTick,
    decision: MarketDataIngestionDecision,
) -> MarketDataIngestionResult:
    return MarketDataIngestionResult(
        tick=tick,
        decision=decision,
        executed=False,
        skipped=True,
        succeeded=False,
    )
