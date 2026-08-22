from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.carry import (
    RATE_LAG_MONTHS,
    CarryComponent,
    accrued_carry,
    build_carry_reading,
    carry_differential,
    lagged_rates_for_anchor,
    observations,
    rate_month_for_anchor,
)
from app.domain.cross_section import rank_into_buckets
from app.domain.entities.carry import CarryReading
from app.domain.entities.cross_section import (
    CrossSectionBucket,
    CrossSectionPeriod,
    CrossSectionProfile,
)
from app.domain.market_calendar import month_start, shift_months

ANCHOR = datetime(2020, 6, 1, tzinfo=UTC)
UNIVERSE = frozenset({"EUR", "USD", "JPY"})


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_10_2_market_state"


def test_a_long_position_earns_the_base_rate_and_pays_the_quote_rate() -> None:
    """Long EURUSD holds euros funded in dollars, so the sign follows the quote convention."""
    assert carry_differential(base_rate=Decimal("0.04"), quote_rate=Decimal("0.01")) == Decimal(
        "0.03"
    )
    assert carry_differential(base_rate=Decimal("0.01"), quote_rate=Decimal("0.04")) == Decimal(
        "-0.03"
    )


def test_only_a_month_of_an_annual_rate_is_earned_in_a_month() -> None:
    """Hand-computed: 6% a year is 0.5% a month, and three months is 1.5%."""
    assert accrued_carry(Decimal("0.06"), months=1) == Decimal("0.005")
    assert accrued_carry(Decimal("0.06"), months=3) == Decimal("0.015")


def test_a_holding_window_shorter_than_a_month_is_refused() -> None:
    with pytest.raises(ValueError, match="at least one month"):
        accrued_carry(Decimal("0.06"), months=0)


def test_the_lag_reaches_two_months_back_and_never_forward() -> None:
    assert rate_month_for_anchor(ANCHOR) == datetime(2020, 4, 1, tzinfo=UTC)
    assert RATE_LAG_MONTHS == 2
    with pytest.raises(ValueError, match="cannot reach forward"):
        rate_month_for_anchor(ANCHOR, lag_months=-1)


def test_a_rate_from_the_month_before_the_anchor_cannot_be_reached() -> None:
    """The point-in-time guard, stated as the leak it prevents.

    A monthly average for May is only complete once May has ended, and is published later still.
    Ranking on it at the start of June would be reading a number that did not yet exist — the quiet
    way a measurement borrows the future and reports it as skill. Only April is in reach.
    """
    may_only = {
        currency: {datetime(2020, 5, 1, tzinfo=UTC): Decimal("0.01")} for currency in UNIVERSE
    }

    assert lagged_rates_for_anchor(ANCHOR, may_only, UNIVERSE) is None


def test_an_anchor_missing_one_currency_is_dropped_whole() -> None:
    """Pre-registered in the Phase 9D-3 plan, and the reason it is all-or-nothing.

    One absent rate removes every pair that touches that currency — nine of forty-five — and every
    remaining bucket boundary shifts. Ranking the survivors would be a different measurement wearing
    the same name, so nothing at all comes back.
    """
    april = datetime(2020, 4, 1, tzinfo=UTC)
    complete = {currency: {april: Decimal("0.01")} for currency in UNIVERSE}
    holed = {**complete, "USD": {}}

    assert lagged_rates_for_anchor(ANCHOR, complete, UNIVERSE) == {
        "EUR": Decimal("0.01"),
        "USD": Decimal("0.01"),
        "JPY": Decimal("0.01"),
    }
    assert lagged_rates_for_anchor(ANCHOR, holed, UNIVERSE) is None


def _reading(instrument: str, differential: str, spot: str) -> CarryReading:
    return build_carry_reading(
        anchor=ANCHOR,
        instrument=instrument,
        base_currency=instrument[:3],
        quote_currency=instrument[3:],
        rates={
            instrument[:3]: Decimal(differential),
            instrument[3:]: Decimal("0"),
        },
        spot_return=Decimal(spot),
        holding_months=1,
    )


def test_the_total_is_the_price_move_plus_what_was_accrued() -> None:
    reading = _reading("EURUSD", "0.12", "-0.004")

    assert reading.differential == Decimal("0.12")
    assert reading.accrued_carry == Decimal("0.01")
    assert reading.total_return == Decimal("0.006")


def test_a_pair_cannot_be_a_currency_against_itself() -> None:
    with pytest.raises(ValidationError):
        CarryReading(
            as_of=ANCHOR,
            instrument="EUREUR",
            base_currency="EUR",
            quote_currency="EUR",
            differential=Decimal("0"),
            spot_return=Decimal("0"),
            accrued_carry=Decimal("0"),
        )


def test_the_three_components_are_ranked_over_identical_buckets() -> None:
    """What makes this a decomposition rather than three adjacent measurements.

    Every component is ordered by the same differential, so bucket membership and bounds cannot
    drift apart. If they could, the spot and carry lines would describe different portfolios and
    adding them up would mean nothing.
    """
    readings = [
        _reading("EURUSD", "0.12", "-0.004"),
        _reading("GBPUSD", "0.06", "0.020"),
        _reading("AUDUSD", "-0.03", "0.010"),
    ]

    periods = {
        component: rank_into_buckets(observations(readings, component), bucket_count=3)
        for component in CarryComponent
    }
    shapes = {
        component: [
            (bucket.instrument_count, bucket.lower_bound, bucket.upper_bound)
            for bucket in period.buckets
        ]
        for component, period in periods.items()
        if period is not None
    }

    assert len(shapes) == 3
    assert len(set(map(str, shapes.values()))) == 1


def test_the_spot_and_carry_spreads_add_up_to_the_total() -> None:
    """Three instruments into three buckets means one each, so no division rounds the identity."""
    readings = [
        _reading("EURUSD", "0.12", "-0.004"),
        _reading("GBPUSD", "0.06", "0.020"),
        _reading("AUDUSD", "-0.03", "0.010"),
    ]

    spreads = {}
    for component in CarryComponent:
        period = rank_into_buckets(observations(readings, component), bucket_count=3)
        assert period is not None
        spreads[component] = period.spread

    assert (
        spreads[CarryComponent.SPOT] + spreads[CarryComponent.CARRY]
        == spreads[CarryComponent.TOTAL]
    )


def _period(as_of: datetime, spread: str) -> CrossSectionPeriod:
    return CrossSectionPeriod(
        as_of=as_of,
        instrument_count=2,
        buckets=(
            CrossSectionBucket(
                index=1,
                instrument_count=1,
                lower_bound=Decimal("0"),
                upper_bound=Decimal("0"),
                mean_forward_return=Decimal("0"),
            ),
            CrossSectionBucket(
                index=2,
                instrument_count=1,
                lower_bound=Decimal("1"),
                upper_bound=Decimal("1"),
                mean_forward_return=Decimal(spread),
            ),
        ),
    )


def _four_month_profile(*, cost_per_leg: str = "0") -> CrossSectionProfile:
    """Spreads of +2%, -5%, -3%, +4% across four consecutive months."""
    return CrossSectionProfile(
        field_ref="carry_differential",
        bucket_count=2,
        cost_per_leg=Decimal(cost_per_leg),
        periods=(
            _period(datetime(2020, 1, 1, tzinfo=UTC), "0.02"),
            _period(datetime(2020, 2, 1, tzinfo=UTC), "-0.05"),
            _period(datetime(2020, 3, 1, tzinfo=UTC), "-0.03"),
            _period(datetime(2020, 4, 1, tzinfo=UTC), "0.04"),
        ),
    )


def test_the_worst_stretch_is_searched_rather_than_centred_on_the_worst_month() -> None:
    """Hand-computed, and deliberately a case where the two answers differ.

    Over +2, -5, -3, +4 the worst single month is February. The worst three-month stretch is
    January to March at -6%, which *starts on a positive month* — a window search finds it and
    "the months either side of the worst one" does not.
    """
    profile = _four_month_profile()

    worst_month = profile.worst_run(length=1)
    assert worst_month is not None
    assert worst_month.cumulative_spread == Decimal("-0.05")
    assert worst_month.started_at == datetime(2020, 2, 1, tzinfo=UTC)

    worst_pair = profile.worst_run(length=2)
    assert worst_pair is not None
    assert worst_pair.cumulative_spread == Decimal("-0.08")

    worst_triple = profile.worst_run(length=3)
    assert worst_triple is not None
    assert worst_triple.cumulative_spread == Decimal("-0.06")
    assert worst_triple.started_at == datetime(2020, 1, 1, tzinfo=UTC)
    assert worst_triple.ended_at == datetime(2020, 3, 1, tzinfo=UTC)


def test_the_tail_is_read_after_costs_like_everything_else() -> None:
    """1% a period off both legs turns the worst month from -5% into -6%."""
    charged = _four_month_profile(cost_per_leg="0.005")

    worst = charged.worst_run(length=1)
    assert worst is not None
    assert worst.cumulative_spread == Decimal("-0.06")


def test_a_stretch_longer_than_the_history_has_no_answer() -> None:
    """`None` rather than a shorter window silently substituted."""
    assert _four_month_profile().worst_run(length=12) is None
    with pytest.raises(ValueError, match="at least one period"):
        _four_month_profile().worst_run(length=0)


def test_a_positive_mean_can_hide_a_ruinous_year() -> None:
    """Why the tail is reported at all, as a case rather than a claim.

    Eleven months of +2% and one of -20% average positive, and no criterion in this project would
    notice the twelfth. The tail reading is the only line that shows it.
    """
    profile = CrossSectionProfile(
        field_ref="carry_differential",
        bucket_count=2,
        periods=tuple(
            _period(datetime(2020, month, 1, tzinfo=UTC), "-0.20" if month == 12 else "0.02")
            for month in range(1, 13)
        ),
    )

    assert profile.mean_spread > 0
    worst = profile.worst_run(length=1)
    assert worst is not None
    assert worst.cumulative_spread == Decimal("-0.20")


def test_month_arithmetic_lands_on_month_starts_in_both_directions() -> None:
    middle = datetime(2020, 3, 17, 13, 45, tzinfo=UTC)

    assert month_start(middle) == datetime(2020, 3, 1, tzinfo=UTC)
    assert shift_months(middle, 1) == datetime(2020, 4, 1, tzinfo=UTC)
    assert shift_months(middle, -3) == datetime(2019, 12, 1, tzinfo=UTC)
    assert shift_months(datetime(2020, 12, 31, tzinfo=UTC), 1) == datetime(2021, 1, 1, tzinfo=UTC)
