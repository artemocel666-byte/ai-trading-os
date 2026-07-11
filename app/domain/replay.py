from collections.abc import Sequence
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.core.time import normalize_to_utc
from app.domain.entities.data_quality import FeatureSnapshot, build_feature_snapshot
from app.domain.entities.market_data import Candle, EconomicEvent, Timeframe
from app.domain.value_objects import CurrencyPair


class HistoricalReplayFrame(BaseModel):
    as_of: datetime
    candles: tuple[Candle, ...]
    economic_events: tuple[EconomicEvent, ...]
    feature_snapshot: FeatureSnapshot

    model_config = ConfigDict(frozen=True)

    @field_validator("as_of")
    @classmethod
    def as_of_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)


class HistoricalReplay:
    def __init__(
        self,
        *,
        candles: Sequence[Candle],
        economic_events: Sequence[EconomicEvent] = (),
    ) -> None:
        self._candles = tuple(
            sorted(candles, key=lambda candle: (candle.open_time, candle.provider))
        )
        self._economic_events = tuple(
            sorted(
                economic_events,
                key=lambda event: (event.scheduled_at, event.currency, event.provider_event_id),
            )
        )

    def frame(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        window_start: datetime,
        window_end: datetime,
        as_of: datetime,
        currencies: Sequence[str] | None = None,
    ) -> HistoricalReplayFrame:
        start_utc = normalize_to_utc(window_start)
        end_utc = normalize_to_utc(window_end)
        as_of_utc = normalize_to_utc(as_of)
        currency_filter = set(currencies) if currencies is not None else None
        candles = tuple(
            candle
            for candle in self._candles
            if candle.pair == pair
            and candle.timeframe == timeframe
            and candle.open_time >= start_utc
            and candle.close_time <= end_utc
            and candle.close_time <= as_of_utc
        )
        economic_events = tuple(
            event
            for event in self._economic_events
            if event.scheduled_at >= start_utc
            and event.scheduled_at < end_utc
            and event.scheduled_at <= as_of_utc
            and (currency_filter is None or event.currency in currency_filter)
        )
        snapshot = build_feature_snapshot(
            pair=pair,
            timeframe=timeframe,
            window_start=start_utc,
            window_end=end_utc,
            candles=candles,
            economic_events=economic_events,
        )
        return HistoricalReplayFrame(
            as_of=as_of_utc,
            candles=candles,
            economic_events=economic_events,
            feature_snapshot=snapshot,
        )
