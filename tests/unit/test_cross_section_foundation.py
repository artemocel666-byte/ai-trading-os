from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.cross_section import (
    build_cross_section_profile,
    forward_return,
    latest_close_at,
    rank_into_buckets,
)
from app.domain.entities import Candle, Timeframe
from app.domain.entities.cross_section import (
    MINIMUM_T_STATISTIC,
    CrossSectionBucket,
    CrossSectionObservation,
    CrossSectionPeriod,
    CrossSectionProfile,
)
from app.domain.value_objects import CurrencyPair

JANUARY = datetime(2020, 1, 1, tzinfo=UTC)
FEBRUARY = datetime(2020, 2, 1, tzinfo=UTC)
MARCH = datetime(2020, 3, 1, tzinfo=UTC)


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_9d4_carry_measurement"


def _observation(
    as_of: datetime, instrument: str, field: str, ahead: str
) -> CrossSectionObservation:
    return CrossSectionObservation(
        as_of=as_of,
        instrument=instrument,
        field_value=Decimal(field),
        forward_return=Decimal(ahead),
    )


def _period(as_of: datetime, *, bottom: str, top: str) -> CrossSectionPeriod:
    return CrossSectionPeriod(
        as_of=as_of,
        instrument_count=2,
        buckets=(
            CrossSectionBucket(
                index=1,
                instrument_count=1,
                lower_bound=Decimal("0"),
                upper_bound=Decimal("0"),
                mean_forward_return=Decimal(bottom),
            ),
            CrossSectionBucket(
                index=2,
                instrument_count=1,
                lower_bound=Decimal("1"),
                upper_bound=Decimal("1"),
                mean_forward_return=Decimal(top),
            ),
        ),
    )


def test_ranking_happens_inside_a_date_not_across_the_whole_sample() -> None:
    """The correction this phase rests on, asserted directly.

    The Phase 9C-3 profiler sorts every observation together, which here would rank a January
    reading against a March one — a comparison through time wearing cross-sectional clothes.
    `EURUSD` holds the same field value on both dates: top of one, bottom of the other. A global
    ordering would place it in the middle of both and report nothing.
    """
    january = [
        _observation(JANUARY, "EURUSD", "0.10", "1"),
        _observation(JANUARY, "GBPUSD", "0.05", "0"),
    ]
    march = [
        _observation(MARCH, "EURUSD", "0.10", "1"),
        _observation(MARCH, "GBPUSD", "0.50", "0"),
    ]

    first = rank_into_buckets(january, bucket_count=2)
    second = rank_into_buckets(march, bucket_count=2)

    assert first is not None
    assert second is not None
    assert first.spread == Decimal("1")
    assert second.spread == Decimal("-1")


def test_observations_from_several_dates_are_refused() -> None:
    """Mixing dates would be invisible in the output, so it is refused rather than averaged."""
    with pytest.raises(ValueError, match="one moment"):
        rank_into_buckets(
            [
                _observation(JANUARY, "EURUSD", "0.10", "1"),
                _observation(MARCH, "GBPUSD", "0.05", "0"),
            ],
            bucket_count=2,
        )


def test_a_date_too_thin_to_rank_is_dropped_rather_than_forced() -> None:
    """An empty extreme would put a zero-instrument mean straight into the spread."""
    assert rank_into_buckets([_observation(JANUARY, "EURUSD", "0.1", "1")], bucket_count=3) is None


def test_buckets_are_equal_in_count_and_ordered_by_field_value() -> None:
    period = rank_into_buckets(
        [
            _observation(JANUARY, "A", "0.9", "0.03"),
            _observation(JANUARY, "B", "0.1", "0.01"),
            _observation(JANUARY, "C", "0.5", "0.02"),
        ],
        bucket_count=3,
    )

    assert period is not None
    assert [bucket.instrument_count for bucket in period.buckets] == [1, 1, 1]
    assert [bucket.mean_forward_return for bucket in period.buckets] == [
        Decimal("0.01"),
        Decimal("0.02"),
        Decimal("0.03"),
    ]
    assert period.spread == Decimal("0.02")


def test_the_statistic_is_computed_over_periods_not_over_instruments() -> None:
    """Hand-computed: spreads of 2% and 4% give a mean of 3%, a standard error of 1%, and t = 3.

    Pooling instrument-months instead would count forty-four correlated pairs in one month as
    forty-four independent facts, which is how a cross-sectional study inflates its own confidence.
    """
    profile = CrossSectionProfile(
        field_ref="trailing_return_3m",
        bucket_count=2,
        periods=(
            _period(JANUARY, bottom="0", top="0.02"),
            _period(FEBRUARY, bottom="0", top="0.04"),
        ),
    )

    assert profile.mean_spread == Decimal("0.03")
    assert profile.standard_error == Decimal("0.01")
    assert profile.t_statistic == Decimal("3")


def test_cost_is_charged_on_both_legs_every_period() -> None:
    """A long and a short leg both rebalance, so the round trip is paid twice."""
    periods = (_period(JANUARY, bottom="0", top="0.02"), _period(FEBRUARY, bottom="0", top="0.04"))
    gross = CrossSectionProfile(field_ref="f", bucket_count=2, periods=periods)
    charged = CrossSectionProfile(
        field_ref="f", bucket_count=2, cost_per_leg=Decimal("0.005"), periods=periods
    )

    assert gross.mean_spread == Decimal("0.03")
    assert charged.mean_spread == Decimal("0.02")


def test_a_single_period_has_no_error_to_divide_by() -> None:
    """`None` rather than a substituted infinity, the habit `target_first_share` set."""
    profile = CrossSectionProfile(
        field_ref="f", bucket_count=2, periods=(_period(JANUARY, bottom="0", top="0.02"),)
    )

    assert profile.standard_error is None
    assert profile.t_statistic is None
    assert profile.clears_the_bar is False


def test_a_flat_spread_clears_nothing() -> None:
    profile = CrossSectionProfile(
        field_ref="f",
        bucket_count=2,
        periods=tuple(
            _period(datetime(2020, month, 1, tzinfo=UTC), bottom="0.01", top="0.01")
            for month in range(1, 9)
        ),
    )

    assert profile.mean_spread == Decimal("0")
    assert profile.clears_the_bar is False


def test_a_strong_and_stable_spread_clears_the_bar() -> None:
    profile = CrossSectionProfile(
        field_ref="f",
        bucket_count=2,
        periods=tuple(
            _period(
                datetime(2020, month, 1, tzinfo=UTC),
                bottom="0",
                top="0.02" if month % 2 else "0.03",
            )
            for month in range(1, 13)
        ),
    )

    statistic = profile.t_statistic
    assert statistic is not None
    assert statistic > MINIMUM_T_STATISTIC
    assert profile.clears_the_bar is True


def test_a_spread_that_only_works_in_one_half_does_not_clear() -> None:
    """The stability criterion, and this design's analogue of the four-series sign check."""
    profile = CrossSectionProfile(
        field_ref="f",
        bucket_count=2,
        periods=tuple(
            _period(
                datetime(2020, month, 1, tzinfo=UTC),
                bottom="0",
                top="0.08" if month <= 6 else "-0.02",
            )
            for month in range(1, 13)
        ),
    )

    assert profile.mean_spread > 0
    assert profile.half(first=True).mean_spread > 0
    assert profile.half(first=False).mean_spread < 0
    assert profile.clears_the_bar is False


def test_periods_must_be_ordered_and_distinct_in_time() -> None:
    with pytest.raises(ValidationError):
        CrossSectionProfile(
            field_ref="f",
            bucket_count=2,
            periods=(
                _period(MARCH, bottom="0", top="0.02"),
                _period(JANUARY, bottom="0", top="0.02"),
            ),
        )


def test_the_builder_orders_dates_and_drops_the_ones_it_cannot_rank() -> None:
    profile = build_cross_section_profile(
        [
            [_observation(MARCH, "A", "0.9", "0.03"), _observation(MARCH, "B", "0.1", "0.01")],
            [_observation(JANUARY, "A", "0.9", "0.02"), _observation(JANUARY, "B", "0.1", "0.01")],
            [_observation(FEBRUARY, "A", "0.9", "0.05")],
        ],
        field_ref="f",
        bucket_count=2,
    )

    assert profile is not None
    assert [period.as_of for period in profile.periods] == [JANUARY, MARCH]


def test_a_return_needs_two_prices_and_a_positive_start() -> None:
    assert forward_return([Decimal("1.0"), Decimal("1.1")]) == Decimal("0.1")
    assert forward_return([Decimal("1.0")]) is None
    assert forward_return([Decimal("0"), Decimal("1.1")]) is None


def _candle(day: int, close: str) -> Candle:
    open_time = datetime(2020, 1, day, tzinfo=UTC)
    return Candle(
        provider="cross-section-test",
        pair=CurrencyPair(value="EURUSD"),
        timeframe=Timeframe.D1,
        open_time=open_time,
        close_time=datetime(2020, 1, day + 1, tzinfo=UTC),
        # Bounds derived from the close so the fixture cannot build a bar the entity must refuse —
        # a close outside its own range is exactly what Phase 9D-1 found in the provider's data.
        open=close,
        high=close,
        low=close,
        close=close,
        volume="1",
        is_closed=True,
    )


def test_an_anchor_takes_the_last_close_before_it() -> None:
    """Trading calendars differ, so an anchor rarely lands on a bar for every instrument."""
    candles = [_candle(1, "1.10"), _candle(3, "1.20"), _candle(6, "1.30")]

    assert latest_close_at(candles, datetime(2020, 1, 5, tzinfo=UTC)) == Decimal("1.20")


def test_a_stale_anchor_price_is_refused_rather_than_used() -> None:
    """What stops a convenience from silently comparing this month's price with last quarter's."""
    candles = [_candle(1, "1.10")]

    assert latest_close_at(candles, datetime(2020, 1, 3, tzinfo=UTC)) == Decimal("1.10")
    assert latest_close_at(candles, datetime(2020, 2, 20, tzinfo=UTC)) is None
    assert latest_close_at(candles, datetime(2019, 12, 1, tzinfo=UTC)) is None
