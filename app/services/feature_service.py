from collections.abc import Callable, Sequence
from datetime import datetime

from app.domain.entities import Timeframe
from app.domain.entities.features import MarketFeatureSnapshot
from app.domain.feature_engine import MarketFeatureEngine
from app.domain.interfaces.unit_of_work import UnitOfWork
from app.domain.value_objects import CurrencyPair

UnitOfWorkFactory = Callable[[], UnitOfWork]


class FeatureService:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        *,
        engine: MarketFeatureEngine | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._engine = engine or MarketFeatureEngine()

    async def build_market_snapshot(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        window_start: datetime,
        window_end: datetime,
        as_of: datetime,
        currencies: Sequence[str] | None = None,
        provider: str | None = None,
        rolling_window_size: int = 3,
    ) -> MarketFeatureSnapshot:
        event_currencies = (
            list(currencies)
            if currencies is not None
            else [
                pair.base_currency,
                pair.quote_currency,
            ]
        )
        async with self._uow_factory() as uow:
            candles = await uow.candles.list_range(
                pair=pair,
                timeframe=timeframe,
                start_at=window_start,
                end_at=window_end,
                provider=provider,
            )
            events = await uow.economic_events.list_window(
                start_at=window_start,
                end_at=window_end,
                currencies=event_currencies,
                provider=provider,
            )
        return self._engine.build_snapshot(
            pair=pair,
            timeframe=timeframe,
            window_start=window_start,
            window_end=window_end,
            as_of=as_of,
            candles=candles,
            economic_events=events,
            rolling_window_size=rolling_window_size,
        )
