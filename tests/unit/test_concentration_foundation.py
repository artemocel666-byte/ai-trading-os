from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.concentration import (
    aligned_returns,
    correlation,
    read_concentration,
    read_correlation,
)
from app.domain.entities.concentration import (
    MINIMUM_OVERLAP,
    ConcentrationReading,
    ConcentrationStatus,
    CorrelationReading,
)
from app.presentation.readings import format_concentration, format_correlation


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_10_3_hidden_concentration"


def _series(count: int, *, step: Decimal = Decimal("0.001")) -> list[Decimal]:
    """A series that actually moves, so a correlation exists to be measured."""
    return [step * Decimal((index % 7) - 3) for index in range(count)]


def test_a_series_against_itself_is_perfectly_correlated() -> None:
    values = _series(60)

    assert correlation(values, values) == Decimal("1")


def test_a_mirrored_series_is_perfectly_anticorrelated() -> None:
    values = _series(60)
    mirrored = [-value for value in values]

    assert correlation(values, mirrored) == Decimal("-1")


def test_a_flat_series_has_no_correlation_rather_than_a_zero() -> None:
    """Zero would report independence where the question has no answer at all."""
    moving = _series(60)
    flat = [Decimal("0")] * 60

    assert correlation(moving, flat) is None


def test_samples_of_different_lengths_are_refused() -> None:
    with pytest.raises(ValueError, match="same length"):
        correlation(_series(10), _series(11))


def test_too_little_overlap_yields_no_reading() -> None:
    values = _series(MINIMUM_OVERLAP - 1)

    assert (
        read_correlation(left="EURUSD", right="GBPUSD", left_returns=values, right_returns=values)
        is None
    )


def test_a_reading_carries_both_halves_and_its_overlap() -> None:
    """Criterion 3. A single coefficient hides whether it held; the halves do not."""
    values = _series(60)

    reading = read_correlation(
        left="EURUSD", right="GBPUSD", left_returns=values, right_returns=values
    )

    assert reading is not None
    assert reading.overlap_count == 60
    assert reading.coefficient == Decimal("1")
    assert reading.first_half == Decimal("1")
    assert reading.second_half == Decimal("1")
    assert reading.half_gap == Decimal("0")


def test_an_instrument_cannot_be_correlated_with_itself() -> None:
    with pytest.raises(ValidationError):
        CorrelationReading(
            left="EURUSD",
            right="EURUSD",
            overlap_count=60,
            coefficient=Decimal("1"),
            first_half=Decimal("1"),
            second_half=Decimal("1"),
        )


def _dated(values: list[Decimal]) -> dict[object, Decimal]:
    """Keyed by day, because `read_concentration` aligns each pair on the days both were priced."""
    return {f"day-{index:04d}": value for index, value in enumerate(values)}


def _identical(names: tuple[str, ...]) -> dict[str, dict[object, Decimal]]:
    return dict.fromkeys(names, _dated(_series(60)))


def test_perfectly_correlated_instruments_are_exactly_one_bet() -> None:
    """Criterion 1, first boundary, hand-checkable: the matrix sums to N squared."""
    names = ("EURUSD", "GBPUSD", "AUDUSD")

    reading = read_concentration(names, _identical(names))

    assert reading.status is ConcentrationStatus.MEASURED
    assert reading.effective_bets == Decimal("1")


def test_uncorrelated_instruments_are_exactly_as_many_bets_as_positions() -> None:
    """Criterion 1, second boundary. Off-diagonals vanish, so the sum is N and N squared
    over N is N.

    Built from three series pairwise orthogonal by construction rather than by luck.
    """
    length = 60
    a = [Decimal(1) if index % 4 in (0, 1) else Decimal(-1) for index in range(length)]
    b = [Decimal(1) if index % 4 in (0, 3) else Decimal(-1) for index in range(length)]
    c = [Decimal(1) if index % 4 in (0, 2) else Decimal(-1) for index in range(length)]
    for left, right in ((a, b), (a, c), (b, c)):
        assert correlation(left, right) == Decimal("0")

    reading = read_concentration(("A", "B", "C"), {"A": _dated(a), "B": _dated(b), "C": _dated(c)})

    assert reading.status is ConcentrationStatus.MEASURED
    assert reading.effective_bets == Decimal("3")


def test_three_positions_at_high_correlation_are_close_to_one_bet() -> None:
    """Criterion 2, the case the whole phase exists for, hand-computed.

    Three instruments pairwise correlated at 0.85: the matrix sums to 3 + 2(3)(0.85) = 8.1, so the
    effective count is 9 / 8.1 = 1.11. Somebody holding all three believes they hold three
    positions and holds roughly one at triple size.
    """
    correlations = tuple(
        CorrelationReading(
            left=left,
            right=right,
            overlap_count=60,
            coefficient=Decimal("0.85"),
            first_half=Decimal("0.85"),
            second_half=Decimal("0.85"),
        )
        for left, right in (("EURUSD", "GBPUSD"), ("EURUSD", "AUDUSD"), ("GBPUSD", "AUDUSD"))
    )
    matrix_sum = Decimal(3) + 2 * sum((item.coefficient for item in correlations), Decimal("0"))

    assert matrix_sum == Decimal("8.1")
    assert (Decimal(9) / matrix_sum).quantize(Decimal("0.01")) == Decimal("1.11")


def test_a_pair_without_enough_history_stops_the_whole_answer() -> None:
    """Criterion 5, and the criterion that decides the slice.

    A concentration computed from the pairs that happened to have history would answer a different
    question from the one asked. Worse, a substituted zero would read as independence — telling
    somebody their positions are unrelated when nothing is known is the most dangerous thing this
    feature could do.
    """
    returns = {
        "EURUSD": _dated(_series(60)),
        "GBPUSD": _dated(_series(60)),
        "NZDSEK": _dated(_series(5)),
    }

    reading = read_concentration(("EURUSD", "GBPUSD", "NZDSEK"), returns)

    assert reading.status is ConcentrationStatus.NOT_ENOUGH_OVERLAP
    assert reading.effective_bets is None
    assert set(reading.missing_pairs) == {"EURUSD/NZDSEK", "GBPUSD/NZDSEK"}


def test_a_set_whose_correlations_cancel_has_no_number_rather_than_a_huge_one() -> None:
    values = _series(60)
    returns = {
        "LONGSIDE": _dated(values),
        "SHORTSIDE": _dated([-value for value in values]),
    }

    reading = read_concentration(("LONGSIDE", "SHORTSIDE"), returns)

    assert reading.status is ConcentrationStatus.FULLY_HEDGED
    assert reading.effective_bets is None


def test_an_effective_count_belongs_only_to_a_measured_reading() -> None:
    with pytest.raises(ValidationError):
        ConcentrationReading(
            instruments=("EURUSD", "GBPUSD"),
            status=ConcentrationStatus.FULLY_HEDGED,
            effective_bets=Decimal("2"),
        )
    with pytest.raises(ValidationError):
        ConcentrationReading(
            instruments=("EURUSD", "GBPUSD"),
            status=ConcentrationStatus.MEASURED,
        )


def test_concentration_is_a_question_about_two_instruments_or_more() -> None:
    with pytest.raises(ValidationError):
        ConcentrationReading(
            instruments=("EURUSD",),
            status=ConcentrationStatus.MEASURED,
            effective_bets=Decimal("1"),
        )


def test_returns_are_lined_up_by_date_not_by_position() -> None:
    """A holiday in one and not the other would otherwise pair a Tuesday with a Wednesday.

    The correlation that came back would be real arithmetic over mismatched days — a number with
    nothing behind it, and no way to see that from the output.
    """
    left = {"mon": Decimal("1"), "tue": Decimal("2"), "wed": Decimal("3")}
    right = {"mon": Decimal("10"), "wed": Decimal("30")}

    aligned_left, aligned_right = aligned_returns(left, right)

    assert aligned_left == [Decimal("1"), Decimal("3")]
    assert aligned_right == [Decimal("10"), Decimal("30")]


def test_an_unmeasurable_set_says_so_rather_than_showing_a_number() -> None:
    reading = read_concentration(
        ("EURUSD", "NZDSEK"), {"EURUSD": _dated(_series(60)), "NZDSEK": _dated(_series(5))}
    )

    text = format_concentration(reading)

    assert "не ноль" in text
    assert "EURUSD/NZDSEK" in text


def test_a_rendered_correlation_shows_its_halves_and_its_overlap() -> None:
    reading = CorrelationReading(
        left="EURUSD",
        right="GBPUSD",
        overlap_count=64,
        coefficient=Decimal("0.60"),
        first_half=Decimal("0.85"),
        second_half=Decimal("0.30"),
    )

    text = format_correlation(reading)

    assert "+0.60" in text
    assert "+0.85" in text
    assert "+0.30" in text
    assert "64" in text


def test_a_holiday_in_one_instrument_shortens_the_overlap_rather_than_shifting_it() -> None:
    """The fault the date keying exists to prevent, asserted end to end.

    Both series are 60 long, so a caller handing over flat lists would get a full-length
    correlation over days that do not line up. Keyed by day, the shared window is what it really
    is — 59 days — and the missing one is simply not in it.
    """
    values = _series(60)
    complete = _dated(values)
    with_a_holiday = {key: value for key, value in complete.items() if key != "day-0007"}

    reading = read_concentration(
        ("EURUSD", "GBPUSD"), {"EURUSD": complete, "GBPUSD": with_a_holiday}
    )

    assert reading.status is ConcentrationStatus.MEASURED
    assert reading.correlations[0].overlap_count == 59


def test_diversification_is_not_the_same_question_as_factor_rank() -> None:
    """The distinction Phase 10-3 nearly got wrong, pinned so nobody conflates them later.

    `currency_universe` says ten currencies give at most nine independent *directions*. The live
    universe measures about 16.6 effective bets, and the temptation is to call the docstring wrong.
    It is not: rank counts the factors driving the returns, while this measure counts how much an
    equally weighted set diversifies, and the second can exceed the first whenever correlations are
    negative.

    Two perfectly opposed instruments make it undeniable — one factor drives both, and the pair
    hedges to nothing.
    """
    values = _series(60)
    opposed = read_concentration(
        ("LONG", "SHORT"),
        {"LONG": _dated(values), "SHORT": _dated([-value for value in values])},
    )

    # One factor, and no measurable number of bets at all - which a rank of 1 would never say.
    assert opposed.status is ConcentrationStatus.FULLY_HEDGED
