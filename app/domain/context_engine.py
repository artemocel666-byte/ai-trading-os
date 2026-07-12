from collections import Counter
from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal

from app.core.time import normalize_to_utc
from app.domain.entities.context import (
    CandleShapeSummary,
    ContextCurrencyCount,
    ContextImpactCount,
    ContextIssue,
    ContextIssueCode,
    EventContextSummary,
    IndicatorWindow,
    MarketContextSnapshot,
    MovingAverageSeries,
    MovingAverageSummary,
    RangeContextSummary,
    ReturnDistributionSummary,
    TimeContextSummary,
)
from app.domain.entities.features import FeatureIssue
from app.domain.entities.market_data import Candle, EconomicEvent, Timeframe
from app.domain.feature_engine import MarketFeatureEngine
from app.domain.value_objects import CurrencyPair


class MarketContextEngine:
    def __init__(self, *, feature_engine: MarketFeatureEngine | None = None) -> None:
        self._feature_engine = feature_engine or MarketFeatureEngine()

    def build_snapshot(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        window_start: datetime,
        window_end: datetime,
        as_of: datetime,
        candles: Sequence[Candle],
        economic_events: Sequence[EconomicEvent] = (),
        moving_average_windows: Sequence[int] = (3, 5),
    ) -> MarketContextSnapshot:
        window = IndicatorWindow(
            pair=pair,
            timeframe=timeframe,
            window_start=window_start,
            window_end=window_end,
            as_of=as_of,
        )
        normalized_windows = _normalize_windows(moving_average_windows)
        feature_snapshot = self._feature_engine.build_snapshot(
            pair=pair,
            timeframe=timeframe,
            window_start=window.window_start,
            window_end=window.window_end,
            as_of=window.as_of,
            candles=candles,
            economic_events=economic_events,
            rolling_window_size=min(normalized_windows),
        )
        usable_candles = _select_candles(
            pair=pair,
            timeframe=timeframe,
            start_at=window.window_start,
            end_at=window.window_end,
            as_of=window.as_of,
            candles=candles,
        )
        usable_events = _select_events(
            start_at=window.window_start,
            end_at=window.window_end,
            as_of=window.as_of,
            events=economic_events,
        )
        context_issues = tuple(_context_issue(issue) for issue in feature_snapshot.quality_issues)
        return MarketContextSnapshot(
            window=window,
            feature_snapshot=feature_snapshot,
            return_distribution=_return_distribution(usable_candles),
            moving_average_summary=_moving_average_summary(
                candles=usable_candles,
                windows=normalized_windows,
            ),
            range_context=_range_context(usable_candles),
            candle_shape=_candle_shape(usable_candles),
            event_context=_event_context(
                input_event_count=len(economic_events),
                events=usable_events,
                as_of=window.as_of,
            ),
            time_context=_time_context(window=window, candle_count=len(usable_candles)),
            context_issues=context_issues,
        )


def _normalize_windows(windows: Sequence[int]) -> tuple[int, ...]:
    if not windows:
        raise ValueError("at least one moving average window is required")
    unique = tuple(sorted(set(windows)))
    if any(window < 1 for window in unique):
        raise ValueError("moving average windows must be positive")
    return unique


def _context_issue(issue: FeatureIssue) -> ContextIssue:
    return ContextIssue(
        code=ContextIssueCode[issue.code.name],
        description=issue.description,
        timestamp=issue.timestamp,
    )


def _select_candles(
    *,
    pair: CurrencyPair,
    timeframe: Timeframe,
    start_at: datetime,
    end_at: datetime,
    as_of: datetime,
    candles: Sequence[Candle],
) -> tuple[Candle, ...]:
    start_utc = normalize_to_utc(start_at)
    end_utc = normalize_to_utc(end_at)
    as_of_utc = normalize_to_utc(as_of)
    selected: dict[datetime, Candle] = {}
    for candle in sorted(candles, key=lambda item: (item.open_time, item.provider)):
        if (
            candle.is_closed
            and candle.pair == pair
            and candle.timeframe == timeframe
            and candle.open_time >= start_utc
            and candle.close_time <= end_utc
            and candle.close_time <= as_of_utc
        ):
            selected.setdefault(candle.open_time, candle)
    return tuple(selected[open_time] for open_time in sorted(selected))


def _select_events(
    *,
    start_at: datetime,
    end_at: datetime,
    as_of: datetime,
    events: Sequence[EconomicEvent],
) -> tuple[EconomicEvent, ...]:
    start_utc = normalize_to_utc(start_at)
    end_utc = normalize_to_utc(end_at)
    as_of_utc = normalize_to_utc(as_of)
    return tuple(
        event
        for event in sorted(
            events,
            key=lambda item: (item.scheduled_at, item.currency, item.provider_event_id),
        )
        if start_utc <= event.scheduled_at < end_utc and event.scheduled_at <= as_of_utc
    )


def _return_distribution(candles: Sequence[Candle]) -> ReturnDistributionSummary:
    close_values = tuple(candle.close for candle in candles)
    close_changes = tuple(
        close_values[index] - close_values[index - 1] for index in range(1, len(close_values))
    )
    per_candle_returns = tuple((candle.close - candle.open) / candle.open for candle in candles)
    deviation = _population_standard_deviation(per_candle_returns)
    return ReturnDistributionSummary(
        close_values=close_values,
        close_change_values=close_changes,
        per_candle_returns=per_candle_returns,
        cumulative_return=_cumulative_return(close_values),
        mean_return=_mean(per_candle_returns),
        median_return=_median(per_candle_returns),
        min_return=min(per_candle_returns) if per_candle_returns else None,
        max_return=max(per_candle_returns) if per_candle_returns else None,
        return_standard_deviation=deviation,
        realized_volatility=deviation,
        max_close_to_close_drawdown=_max_close_to_close_drawdown(close_values),
    )


def _moving_average_summary(
    *,
    candles: Sequence[Candle],
    windows: Sequence[int],
) -> MovingAverageSummary:
    close_values = tuple(candle.close for candle in candles)
    per_candle_returns = tuple((candle.close - candle.open) / candle.open for candle in candles)
    return MovingAverageSummary(
        close_mean_series=tuple(
            MovingAverageSeries(window_size=window, values=_moving_means(close_values, window))
            for window in windows
        ),
        return_mean_series=tuple(
            MovingAverageSeries(
                window_size=window,
                values=_moving_means(per_candle_returns, window),
            )
            for window in windows
        ),
    )


def _range_context(candles: Sequence[Candle]) -> RangeContextSummary:
    range_values = tuple(candle.high - candle.low for candle in candles)
    true_range_values = _true_ranges(candles)
    return RangeContextSummary(
        true_range_values=true_range_values,
        average_true_range=_mean(true_range_values),
        candle_range_values=range_values,
        average_candle_range=_mean(range_values),
        range_change_ratios=_range_change_ratios(range_values),
    )


def _candle_shape(candles: Sequence[Candle]) -> CandleShapeSummary:
    body_sizes = tuple(abs(candle.close - candle.open) for candle in candles)
    upper_wicks = tuple(candle.high - max(candle.open, candle.close) for candle in candles)
    lower_wicks = tuple(min(candle.open, candle.close) - candle.low for candle in candles)
    range_values = tuple(candle.high - candle.low for candle in candles)
    return CandleShapeSummary(
        body_sizes=body_sizes,
        average_body_size=_mean(body_sizes),
        upper_wick_sizes=upper_wicks,
        lower_wick_sizes=lower_wicks,
        average_upper_wick_size=_mean(upper_wicks),
        average_lower_wick_size=_mean(lower_wicks),
        body_to_range_ratios=tuple(
            None if range_value == 0 else body_size / range_value
            for body_size, range_value in zip(body_sizes, range_values, strict=True)
        ),
        close_location_in_range_values=tuple(
            None if range_value == 0 else (candle.close - candle.low) / range_value
            for candle, range_value in zip(candles, range_values, strict=True)
        ),
    )


def _event_context(
    *,
    input_event_count: int,
    events: Sequence[EconomicEvent],
    as_of: datetime,
) -> EventContextSummary:
    impact_counts = Counter(event.impact for event in events)
    currency_counts = Counter(event.currency for event in events)
    latest_event_time = max((event.scheduled_at for event in events), default=None)
    return EventContextSummary(
        input_event_count=input_event_count,
        used_event_count=len(events),
        counts_by_impact=tuple(
            ContextImpactCount(impact=impact, count=impact_counts[impact])
            for impact in sorted(impact_counts, key=lambda value: value.value)
        ),
        counts_by_currency=tuple(
            ContextCurrencyCount(currency=currency, count=currency_counts[currency])
            for currency in sorted(currency_counts)
        ),
        latest_event_time=latest_event_time,
        minutes_since_latest_event=_minutes_between(latest_event_time, as_of)
        if latest_event_time is not None
        else None,
    )


def _time_context(*, window: IndicatorWindow, candle_count: int) -> TimeContextSummary:
    return TimeContextSummary(
        as_of_utc_hour=window.as_of.hour,
        as_of_utc_weekday=window.as_of.weekday(),
        window_minutes=_minutes_between(window.window_start, window.window_end) or Decimal("0"),
        candle_count=candle_count,
    )


def _cumulative_return(close_values: Sequence[Decimal]) -> Decimal | None:
    if len(close_values) < 2:
        return None
    return (close_values[-1] - close_values[0]) / close_values[0]


def _mean(values: Sequence[Decimal]) -> Decimal | None:
    if not values:
        return None
    return sum(values, Decimal("0")) / Decimal(len(values))


def _median(values: Sequence[Decimal]) -> Decimal | None:
    if not values:
        return None
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / Decimal("2")


def _population_standard_deviation(values: Sequence[Decimal]) -> Decimal | None:
    mean = _mean(values)
    if mean is None:
        return None
    variance = sum(((value - mean) ** 2 for value in values), Decimal("0")) / Decimal(len(values))
    return variance.sqrt()


def _max_close_to_close_drawdown(close_values: Sequence[Decimal]) -> Decimal | None:
    if len(close_values) < 2:
        return None
    peak = close_values[0]
    largest = Decimal("0")
    for close_value in close_values[1:]:
        if close_value > peak:
            peak = close_value
            continue
        current = (peak - close_value) / peak
        if current > largest:
            largest = current
    return largest


def _moving_means(values: Sequence[Decimal], window_size: int) -> tuple[Decimal, ...]:
    means: list[Decimal] = []
    for index in range(window_size, len(values) + 1):
        window = values[index - window_size : index]
        means.append(sum(window, Decimal("0")) / Decimal(window_size))
    return tuple(means)


def _true_ranges(candles: Sequence[Candle]) -> tuple[Decimal, ...]:
    ranges: list[Decimal] = []
    previous_close: Decimal | None = None
    for candle in candles:
        high_low = candle.high - candle.low
        if previous_close is None:
            true_range = high_low
        else:
            true_range = max(
                high_low,
                abs(candle.high - previous_close),
                abs(candle.low - previous_close),
            )
        ranges.append(true_range)
        previous_close = candle.close
    return tuple(ranges)


def _range_change_ratios(values: Sequence[Decimal]) -> tuple[Decimal | None, ...]:
    if not values:
        return ()
    ratios: list[Decimal | None] = [None]
    for index in range(1, len(values)):
        previous = values[index - 1]
        ratios.append(None if previous == 0 else (values[index] - previous) / previous)
    return tuple(ratios)


def _minutes_between(start_at: datetime | None, end_at: datetime) -> Decimal | None:
    if start_at is None:
        return None
    delta = normalize_to_utc(end_at) - normalize_to_utc(start_at)
    microseconds = (delta.days * 86_400 + delta.seconds) * 1_000_000 + delta.microseconds
    return Decimal(microseconds) / Decimal("60000000")
