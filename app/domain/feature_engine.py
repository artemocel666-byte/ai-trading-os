from collections import Counter
from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal

from app.core.time import normalize_to_utc
from app.domain.entities.data_quality import TIMEFRAME_TO_DELTA, build_feature_snapshot
from app.domain.entities.features import (
    CandleFeatureSummary,
    CurrencyEventCount,
    EconomicEventFeatureSummary,
    EconomicImpactCount,
    FeatureIssue,
    FeatureIssueCode,
    FeatureWindow,
    MarketFeatureSnapshot,
)
from app.domain.entities.market_data import Candle, EconomicEvent, Timeframe
from app.domain.value_objects import CurrencyPair


class MarketFeatureEngine:
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
        rolling_window_size: int = 3,
    ) -> MarketFeatureSnapshot:
        window = FeatureWindow(
            pair=pair,
            timeframe=timeframe,
            window_start=window_start,
            window_end=window_end,
            as_of=as_of,
        )
        if rolling_window_size < 1:
            raise ValueError("rolling_window_size must be at least 1")

        start_utc = window.window_start
        end_utc = window.window_end
        as_of_utc = window.as_of
        expected_open_times = _expected_open_times(
            timeframe=timeframe,
            window_start=start_utc,
            window_end=end_utc,
        )
        issues: list[FeatureIssue] = []
        if _is_unaligned_window(timeframe=timeframe, start_at=start_utc, end_at=end_utc):
            issues.append(
                FeatureIssue(
                    code=FeatureIssueCode.WINDOW_NOT_ALIGNED,
                    description="Feature window is not an exact multiple of the timeframe.",
                )
            )

        sorted_candles = sorted(candles, key=lambda candle: (candle.open_time, candle.provider))
        usable_candidates: list[Candle] = []
        for candle in sorted_candles:
            if not candle.is_closed:
                issues.append(
                    FeatureIssue(
                        code=FeatureIssueCode.CANDLE_NOT_CLOSED,
                        description="Open candle excluded from feature calculation.",
                        timestamp=candle.open_time,
                    )
                )
                continue
            if candle.pair != pair:
                issues.append(
                    FeatureIssue(
                        code=FeatureIssueCode.CANDLE_PAIR_MISMATCH,
                        description="Candle pair does not match the requested pair.",
                        timestamp=candle.open_time,
                    )
                )
                continue
            if candle.timeframe != timeframe:
                issues.append(
                    FeatureIssue(
                        code=FeatureIssueCode.CANDLE_TIMEFRAME_MISMATCH,
                        description="Candle timeframe does not match the requested timeframe.",
                        timestamp=candle.open_time,
                    )
                )
                continue
            if candle.open_time < start_utc or candle.close_time > end_utc:
                issues.append(
                    FeatureIssue(
                        code=FeatureIssueCode.CANDLE_OUT_OF_RANGE,
                        description="Candle is outside the requested feature window.",
                        timestamp=candle.open_time,
                    )
                )
                continue
            if candle.close_time > as_of_utc:
                issues.append(
                    FeatureIssue(
                        code=FeatureIssueCode.CANDLE_AFTER_AS_OF,
                        description="Candle closes after the feature as_of timestamp.",
                        timestamp=candle.close_time,
                    )
                )
                continue
            usable_candidates.append(candle)

        duplicate_open_times = _duplicate_open_times(usable_candidates)
        for open_time in duplicate_open_times:
            issues.append(
                FeatureIssue(
                    code=FeatureIssueCode.DUPLICATE_CANDLE,
                    description="Duplicate candle open time in feature window.",
                    timestamp=open_time,
                )
            )

        usable_candles = _dedupe_candles_by_open_time(usable_candidates)
        observed_open_times = {candle.open_time for candle in usable_candles}
        for expected_open_time in expected_open_times:
            if expected_open_time not in observed_open_times:
                issues.append(
                    FeatureIssue(
                        code=FeatureIssueCode.MISSING_CANDLE,
                        description="Expected candle is missing from feature window.",
                        timestamp=expected_open_time,
                    )
                )

        if not usable_candles:
            issues.append(
                FeatureIssue(
                    code=FeatureIssueCode.NO_CANDLES,
                    description="No usable closed candles are available for feature calculation.",
                )
            )
        elif len(usable_candles) < rolling_window_size:
            issues.append(
                FeatureIssue(
                    code=FeatureIssueCode.INSUFFICIENT_CANDLES,
                    description="Not enough candles are available for the rolling window.",
                    timestamp=usable_candles[-1].close_time,
                )
            )

        sorted_events = sorted(
            economic_events,
            key=lambda event: (event.scheduled_at, event.currency, event.provider_event_id),
        )
        usable_events: list[EconomicEvent] = []
        for event in sorted_events:
            if event.scheduled_at < start_utc or event.scheduled_at >= end_utc:
                issues.append(
                    FeatureIssue(
                        code=FeatureIssueCode.EVENT_OUT_OF_RANGE,
                        description="Economic event is outside the requested feature window.",
                        timestamp=event.scheduled_at,
                    )
                )
                continue
            if event.scheduled_at > as_of_utc:
                issues.append(
                    FeatureIssue(
                        code=FeatureIssueCode.EVENT_AFTER_AS_OF,
                        description=(
                            "Economic event is scheduled after the feature as_of timestamp."
                        ),
                        timestamp=event.scheduled_at,
                    )
                )
                continue
            usable_events.append(event)

        data_quality_snapshot = build_feature_snapshot(
            pair=pair,
            timeframe=timeframe,
            window_start=start_utc,
            window_end=end_utc,
            candles=candles,
            economic_events=economic_events,
        )
        return MarketFeatureSnapshot(
            window=window,
            candle_summary=_build_candle_summary(
                expected_candle_count=len(expected_open_times),
                input_candle_count=len(candles),
                candles=usable_candles,
                rolling_window_size=rolling_window_size,
                market_data_complete=_market_data_complete(issues),
            ),
            economic_event_summary=_build_event_summary(
                input_event_count=len(economic_events),
                events=usable_events,
            ),
            quality_issues=tuple(issues),
            data_quality_issues=data_quality_snapshot.quality_issues,
        )


def _is_unaligned_window(*, timeframe: Timeframe, start_at: datetime, end_at: datetime) -> bool:
    delta = TIMEFRAME_TO_DELTA[timeframe]
    expected_count = len(
        _expected_open_times(timeframe=timeframe, window_start=start_at, window_end=end_at)
    )
    return start_at + (expected_count * delta) != end_at


def _expected_open_times(
    *,
    timeframe: Timeframe,
    window_start: datetime,
    window_end: datetime,
) -> tuple[datetime, ...]:
    start_utc = normalize_to_utc(window_start)
    end_utc = normalize_to_utc(window_end)
    delta = TIMEFRAME_TO_DELTA[timeframe]
    expected: list[datetime] = []
    cursor = start_utc
    while cursor + delta <= end_utc:
        expected.append(cursor)
        cursor += delta
    return tuple(expected)


def _duplicate_open_times(candles: Sequence[Candle]) -> tuple[datetime, ...]:
    counts = Counter(candle.open_time for candle in candles)
    return tuple(sorted(open_time for open_time, count in counts.items() if count > 1))


def _dedupe_candles_by_open_time(candles: Sequence[Candle]) -> tuple[Candle, ...]:
    selected: dict[datetime, Candle] = {}
    for candle in sorted(candles, key=lambda item: (item.open_time, item.provider)):
        selected.setdefault(candle.open_time, candle)
    return tuple(selected[open_time] for open_time in sorted(selected))


def _build_candle_summary(
    *,
    expected_candle_count: int,
    input_candle_count: int,
    candles: Sequence[Candle],
    rolling_window_size: int,
    market_data_complete: bool,
) -> CandleFeatureSummary:
    candle_ranges = tuple(candle.high - candle.low for candle in candles)
    body_sizes = tuple(abs(candle.close - candle.open) for candle in candles)
    per_candle_returns = tuple((candle.close - candle.open) / candle.open for candle in candles)
    volumes = tuple(candle.volume for candle in candles if candle.volume is not None)
    true_ranges = _true_ranges(candles)
    return CandleFeatureSummary(
        expected_candle_count=expected_candle_count,
        input_candle_count=input_candle_count,
        used_candle_count=len(candles),
        latest_close=candles[-1].close if candles else None,
        first_candle_open_time=candles[0].open_time if candles else None,
        latest_candle_close_time=candles[-1].close_time if candles else None,
        simple_return=((candles[-1].close - candles[0].open) / candles[0].open)
        if candles
        else None,
        per_candle_returns=per_candle_returns,
        rolling_close_mean_window=rolling_window_size,
        rolling_close_means=_rolling_close_means(candles, rolling_window_size),
        rolling_high_low_ranges=_rolling_high_low_ranges(candles, rolling_window_size),
        average_candle_range=_mean(candle_ranges),
        average_body_size=_mean(body_sizes),
        volume_observed_count=len(volumes),
        volume_sum=sum(volumes) if volumes else None,
        volume_average=_mean(volumes),
        true_ranges=true_ranges,
        average_true_range=_mean(true_ranges),
        market_data_complete=market_data_complete,
    )


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


def _rolling_close_means(candles: Sequence[Candle], window_size: int) -> tuple[Decimal, ...]:
    means: list[Decimal] = []
    for index in range(window_size, len(candles) + 1):
        window = candles[index - window_size : index]
        means.append(sum(candle.close for candle in window) / Decimal(window_size))
    return tuple(means)


def _rolling_high_low_ranges(candles: Sequence[Candle], window_size: int) -> tuple[Decimal, ...]:
    ranges: list[Decimal] = []
    for index in range(window_size, len(candles) + 1):
        window = candles[index - window_size : index]
        ranges.append(max(candle.high for candle in window) - min(candle.low for candle in window))
    return tuple(ranges)


def _mean(values: Sequence[Decimal]) -> Decimal | None:
    if not values:
        return None
    return sum(values) / Decimal(len(values))


def _build_event_summary(
    *,
    input_event_count: int,
    events: Sequence[EconomicEvent],
) -> EconomicEventFeatureSummary:
    impact_counts = Counter(event.impact for event in events)
    currency_counts = Counter(event.currency for event in events)
    return EconomicEventFeatureSummary(
        input_event_count=input_event_count,
        used_event_count=len(events),
        counts_by_impact=tuple(
            EconomicImpactCount(impact=impact, count=impact_counts[impact])
            for impact in sorted(impact_counts, key=lambda value: value.value)
        ),
        counts_by_currency=tuple(
            CurrencyEventCount(currency=currency, count=currency_counts[currency])
            for currency in sorted(currency_counts)
        ),
    )


def _market_data_complete(issues: Sequence[FeatureIssue]) -> bool:
    blocking_codes = {
        FeatureIssueCode.NO_CANDLES,
        FeatureIssueCode.INSUFFICIENT_CANDLES,
        FeatureIssueCode.WINDOW_NOT_ALIGNED,
        FeatureIssueCode.CANDLE_NOT_CLOSED,
        FeatureIssueCode.CANDLE_AFTER_AS_OF,
        FeatureIssueCode.CANDLE_OUT_OF_RANGE,
        FeatureIssueCode.CANDLE_PAIR_MISMATCH,
        FeatureIssueCode.CANDLE_TIMEFRAME_MISMATCH,
        FeatureIssueCode.DUPLICATE_CANDLE,
        FeatureIssueCode.MISSING_CANDLE,
    }
    return not any(issue.code in blocking_codes for issue in issues)
