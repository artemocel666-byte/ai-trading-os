from collections.abc import Callable, Sequence
from datetime import datetime

from app.core.exceptions import NotImplementedFeatureError
from app.domain.analysis_engine import AnalysisEngine
from app.domain.entities import Timeframe
from app.domain.entities.analysis import AnalysisReport, AnalysisSnapshot
from app.domain.interfaces.unit_of_work import UnitOfWork
from app.domain.value_objects import CurrencyPair

UnitOfWorkFactory = Callable[[], UnitOfWork]


class AnalysisService:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory | None = None,
        *,
        engine: AnalysisEngine | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._engine = engine or AnalysisEngine()

    async def build_snapshot(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        window_start: datetime,
        window_end: datetime,
        as_of: datetime,
        currencies: Sequence[str] | None = None,
        provider: str | None = None,
        moving_average_windows: Sequence[int] = (3, 5),
    ) -> AnalysisSnapshot:
        event_currencies = (
            list(currencies)
            if currencies is not None
            else [
                pair.base_currency,
                pair.quote_currency,
            ]
        )
        if self._uow_factory is None:
            raise ValueError("unit of work factory is required")
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
            currencies=event_currencies,
            provider=provider,
            moving_average_windows=moving_average_windows,
        )

    async def build_report(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        window_start: datetime,
        window_end: datetime,
        as_of: datetime,
        currencies: Sequence[str] | None = None,
        provider: str | None = None,
        moving_average_windows: Sequence[int] = (3, 5),
    ) -> AnalysisReport:
        snapshot = await self.build_snapshot(
            pair=pair,
            timeframe=timeframe,
            window_start=window_start,
            window_end=window_end,
            as_of=as_of,
            currencies=currencies,
            provider=provider,
            moving_average_windows=moving_average_windows,
        )
        return AnalysisReport(
            snapshot=snapshot,
            ready_for_review=snapshot.readiness_status.value == "READY",
            issue_count=len(snapshot.readiness_issues),
            used_candle_count=snapshot.input_audit.used_candle_count,
            used_event_count=snapshot.input_audit.used_event_count,
            generated_at=snapshot.window.as_of,
        )

    async def scan_now(self) -> None:
        raise NotImplementedFeatureError("analysis_engine")
