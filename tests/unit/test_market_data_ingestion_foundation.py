from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.core import constants
from app.domain.entities import Candle, SnapshotScheduleItem, Timeframe
from app.domain.entities.ingestion import (
    MarketDataIngestionConfig,
    MarketDataIngestionDecisionReason,
)
from app.domain.value_objects import CurrencyPair
from app.services.market_data_ingestion_service import (
    MarketDataIngestionService,
    ingestion_window,
    is_market_data_ingestion_due,
)
from app.services.system_state_service import SystemStateService
from tests.fakes import FakeUnitOfWorkFactory

PAIR = CurrencyPair(value="EURUSD")
# 09:00 UTC is aligned to both the M15 boundary and a 15-minute ingestion interval.
DUE_TIME = datetime(2026, 7, 22, 9, 0, tzinfo=UTC)


class FakeMarketDataProvider:
    def __init__(
        self,
        *,
        candles_by_timeframe: dict[Timeframe, list[Candle]] | None = None,
        failing_timeframes: frozenset[Timeframe] = frozenset(),
    ) -> None:
        self._candles_by_timeframe = candles_by_timeframe or {}
        self._failing_timeframes = failing_timeframes
        self.calls: list[tuple[CurrencyPair, Timeframe, datetime, datetime]] = []

    async def get_closed_candles(
        self,
        pair: CurrencyPair,
        timeframe: Timeframe,
        start_at: datetime,
        end_at: datetime,
    ) -> Sequence[Candle]:
        self.calls.append((pair, timeframe, start_at, end_at))
        if timeframe in self._failing_timeframes:
            raise RuntimeError("provider unavailable")
        return self._candles_by_timeframe.get(timeframe, [])


def _candle(index: int, *, timeframe: Timeframe = Timeframe.M15) -> Candle:
    step = timedelta(minutes=15) if timeframe == Timeframe.M15 else timedelta(hours=1)
    open_time = DUE_TIME - ((index + 1) * step)
    open_price = Decimal("1.1000") + (Decimal("0.0001") * Decimal(index))
    close_price = open_price + Decimal("0.0001")
    return Candle(
        provider="ingestion-test",
        pair=PAIR,
        timeframe=timeframe,
        open_time=open_time,
        close_time=open_time + step,
        open=open_price,
        high=close_price + Decimal("0.0002"),
        low=open_price - Decimal("0.0002"),
        close=close_price,
        volume=Decimal("100"),
        is_closed=True,
    )


def _item(timeframe: Timeframe = Timeframe.M15) -> SnapshotScheduleItem:
    return SnapshotScheduleItem(pair=PAIR, timeframe=timeframe, lookback_candle_count=4)


def _config(
    *,
    enabled: bool = True,
    items: tuple[SnapshotScheduleItem, ...] = (),
    interval_minutes: int = 15,
    lookback_candles: int = 4,
) -> MarketDataIngestionConfig:
    return MarketDataIngestionConfig(
        enabled=enabled,
        interval_minutes=interval_minutes,
        lookback_candles=lookback_candles,
        items=items,
    )


def _service(
    *,
    config: MarketDataIngestionConfig,
    provider: FakeMarketDataProvider,
    factory: FakeUnitOfWorkFactory,
) -> MarketDataIngestionService:
    return MarketDataIngestionService(
        config=config,
        provider=provider,
        uow_factory=factory,
        system_state_service=SystemStateService(factory),
    )


@pytest.mark.asyncio
async def test_disabled_ingestion_skips_without_calling_provider() -> None:
    provider = FakeMarketDataProvider()
    factory = FakeUnitOfWorkFactory()
    service = _service(
        config=_config(enabled=False, items=(_item(),)),
        provider=provider,
        factory=factory,
    )

    result = await service.run_tick(as_of=DUE_TIME)

    assert result.skipped is True
    assert result.executed is False
    assert result.decision.reason == MarketDataIngestionDecisionReason.DISABLED
    assert provider.calls == []
    assert factory.candles == []


@pytest.mark.asyncio
async def test_ingestion_without_items_skips() -> None:
    provider = FakeMarketDataProvider()
    factory = FakeUnitOfWorkFactory()
    service = _service(config=_config(items=()), provider=provider, factory=factory)

    result = await service.run_tick(as_of=DUE_TIME)

    assert result.skipped is True
    assert result.decision.reason == MarketDataIngestionDecisionReason.NO_ITEMS
    assert provider.calls == []


@pytest.mark.asyncio
async def test_not_due_tick_skips_without_calling_provider() -> None:
    provider = FakeMarketDataProvider()
    factory = FakeUnitOfWorkFactory()
    service = _service(config=_config(items=(_item(),)), provider=provider, factory=factory)

    result = await service.run_tick(as_of=DUE_TIME + timedelta(minutes=7))

    assert result.skipped is True
    assert result.decision.reason == MarketDataIngestionDecisionReason.NOT_DUE
    assert provider.calls == []


@pytest.mark.asyncio
async def test_due_tick_fetches_and_stores_candles() -> None:
    candles = [_candle(index) for index in range(3)]
    provider = FakeMarketDataProvider(candles_by_timeframe={Timeframe.M15: candles})
    factory = FakeUnitOfWorkFactory()
    service = _service(config=_config(items=(_item(),)), provider=provider, factory=factory)

    result = await service.run_tick(as_of=DUE_TIME)

    assert result.executed is True
    assert result.succeeded is True
    assert result.decision.reason == MarketDataIngestionDecisionReason.COMPLETED
    assert result.total_fetched == 3
    assert result.total_inserted == 3
    assert result.failed_item_count == 0
    assert len(factory.candles) == 3
    assert len(provider.calls) == 1


@pytest.mark.asyncio
async def test_empty_provider_response_is_success_not_failure() -> None:
    # The forex market is closed on weekends; an empty window is normal, not an error.
    provider = FakeMarketDataProvider(candles_by_timeframe={Timeframe.M15: []})
    factory = FakeUnitOfWorkFactory()
    service = _service(config=_config(items=(_item(),)), provider=provider, factory=factory)

    result = await service.run_tick(as_of=DUE_TIME)

    assert result.succeeded is True
    assert result.failed_item_count == 0
    assert result.total_fetched == 0
    assert result.item_results[0].failed is False
    assert factory.candles == []


@pytest.mark.asyncio
async def test_one_failing_item_does_not_abort_the_other() -> None:
    provider = FakeMarketDataProvider(
        candles_by_timeframe={Timeframe.H1: [_candle(0, timeframe=Timeframe.H1)]},
        failing_timeframes=frozenset({Timeframe.M15}),
    )
    factory = FakeUnitOfWorkFactory()
    service = _service(
        config=_config(items=(_item(Timeframe.M15), _item(Timeframe.H1))),
        provider=provider,
        factory=factory,
    )

    result = await service.run_tick(as_of=DUE_TIME)

    assert result.executed is True
    assert result.succeeded is True
    assert result.failed_item_count == 1
    failed = next(item for item in result.item_results if item.timeframe == Timeframe.M15)
    succeeded = next(item for item in result.item_results if item.timeframe == Timeframe.H1)
    assert failed.failed is True
    assert failed.fetched_count == 0
    assert succeeded.failed is False
    assert succeeded.fetched_count == 1
    assert len(factory.candles) == 1


@pytest.mark.asyncio
async def test_successful_tick_records_integration_health() -> None:
    provider = FakeMarketDataProvider(candles_by_timeframe={Timeframe.M15: [_candle(0)]})
    factory = FakeUnitOfWorkFactory()
    service = _service(config=_config(items=(_item(),)), provider=provider, factory=factory)

    await service.run_tick(as_of=DUE_TIME)

    assert constants.SYSTEM_STATE_LAST_SUCCESSFUL_MARKET_FETCH in factory.state


@pytest.mark.asyncio
async def test_fully_failed_tick_does_not_record_integration_health() -> None:
    provider = FakeMarketDataProvider(failing_timeframes=frozenset({Timeframe.M15}))
    factory = FakeUnitOfWorkFactory()
    service = _service(config=_config(items=(_item(),)), provider=provider, factory=factory)

    result = await service.run_tick(as_of=DUE_TIME)

    assert result.succeeded is False
    assert result.failed_item_count == 1
    assert constants.SYSTEM_STATE_LAST_SUCCESSFUL_MARKET_FETCH not in factory.state
    assert constants.SYSTEM_STATE_LAST_ERROR in factory.state


@pytest.mark.asyncio
async def test_requested_window_is_aligned_and_covers_the_lookback() -> None:
    provider = FakeMarketDataProvider()
    factory = FakeUnitOfWorkFactory()
    service = _service(
        config=_config(items=(_item(),), lookback_candles=4),
        provider=provider,
        factory=factory,
    )

    await service.run_tick(as_of=DUE_TIME)

    _, _, start_at, end_at = provider.calls[0]
    assert end_at == DUE_TIME
    assert end_at - start_at == timedelta(minutes=60)


def test_ingestion_window_is_deterministic_and_rejects_empty_lookback() -> None:
    first = ingestion_window(timeframe=Timeframe.M15, as_of=DUE_TIME, lookback_candles=4)
    second = ingestion_window(timeframe=Timeframe.M15, as_of=DUE_TIME, lookback_candles=4)

    assert first == second
    # An unaligned as_of still resolves to the same closed boundary.
    unaligned = ingestion_window(
        timeframe=Timeframe.M15,
        as_of=DUE_TIME + timedelta(minutes=7),
        lookback_candles=4,
    )
    assert unaligned == first

    with pytest.raises(ValueError, match="lookback_candles"):
        ingestion_window(timeframe=Timeframe.M15, as_of=DUE_TIME, lookback_candles=0)


def test_due_check_requires_exact_interval_boundary() -> None:
    assert is_market_data_ingestion_due(as_of=DUE_TIME, interval_minutes=15) is True
    assert (
        is_market_data_ingestion_due(as_of=DUE_TIME + timedelta(minutes=7), interval_minutes=15)
        is False
    )
    assert (
        is_market_data_ingestion_due(as_of=DUE_TIME + timedelta(seconds=1), interval_minutes=15)
        is False
    )

    with pytest.raises(ValueError, match="at least one minute"):
        is_market_data_ingestion_due(as_of=DUE_TIME, interval_minutes=0)
