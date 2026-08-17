from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.entities.field_outcome import FieldDecile, FieldOutcomeProfile
from app.domain.entities.outcome import OutcomeKind, WindowOutcome
from app.domain.entities.signal_contract import SignalDirection
from app.domain.field_outcome_profile import FieldObservation, build_field_outcome_profile
from app.domain.outcome_measurement import aggregate_outcomes


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_9d4_carry_measurement"


def _outcome(kind: OutcomeKind, direction: SignalDirection) -> WindowOutcome:
    resolved = kind not in (OutcomeKind.TIMEOUT, OutcomeKind.NO_DATA)
    return WindowOutcome(
        direction=direction,
        entry_price=Decimal("1.10000"),
        stop_loss=Decimal("1.09800"),
        take_profit=Decimal("1.10300"),
        kind=kind,
        bars_to_resolution=2 if resolved else None,
    )


def _observation(value: str | None, kind: OutcomeKind) -> FieldObservation:
    return FieldObservation(
        value=None if value is None else Decimal(value),
        outcomes={direction: _outcome(kind, direction) for direction in SignalDirection},
    )


def _profile(observations: list[FieldObservation]) -> FieldOutcomeProfile:
    return build_field_outcome_profile(
        observations,
        pair="EURUSD",
        timeframe="M15",
        field_ref="market_context.volatility_ratio",
    )


def _monotone(count_per_decile: int = 4) -> list[FieldObservation]:
    """Low values always stop, high values always reach the target."""
    observations: list[FieldObservation] = []
    for decile in range(10):
        kind = OutcomeKind.TARGET_FIRST if decile >= 5 else OutcomeKind.STOP_FIRST
        for item in range(count_per_decile):
            observations.append(_observation(f"{decile}.{item}", kind))
    return observations


def _u_shaped(count_per_decile: int = 4) -> list[FieldObservation]:
    """Both tails always stop, the middle always reaches the target.

    The hypothesis a band rule encodes, and the reason a monotone reading is not enough on its own.
    """
    observations: list[FieldObservation] = []
    for decile in range(10):
        kind = OutcomeKind.STOP_FIRST if decile in (0, 9) else OutcomeKind.TARGET_FIRST
        for item in range(count_per_decile):
            observations.append(_observation(f"{decile}.{item}", kind))
    return observations


def test_a_monotone_relationship_shows_up_in_the_gradient() -> None:
    profile = _profile(_monotone())

    assert len(profile.deciles) == 10
    assert profile.gradient_edge == Decimal("1")


def test_a_u_shape_is_invisible_to_the_gradient_and_caught_by_the_band() -> None:
    """The whole reason both readings exist, stated as a test.

    A band rule assumes both tails are bad. Comparing the top decile with the bottom compares two
    tails against each other, finds them alike, and reports nothing.
    """
    profile = _profile(_u_shaped())

    assert profile.gradient_edge == Decimal("0")
    assert profile.band_edge == Decimal("1")


def test_a_field_that_separates_nothing_reports_no_edge_either_way() -> None:
    """The expected result for a real field, and the one that would close the question."""
    observations = [
        _observation(f"{decile}.{item}", kind)
        for decile in range(10)
        for item, kind in enumerate((OutcomeKind.TARGET_FIRST, OutcomeKind.STOP_FIRST))
    ]

    profile = _profile(observations)

    assert profile.gradient_edge == Decimal("0")
    assert profile.band_edge == Decimal("0")


def test_deciles_hold_equal_numbers_of_windows() -> None:
    """Equal counts are what make the ten shares comparable at all."""
    profile = _profile(_monotone(count_per_decile=7))

    assert {decile.window_count for decile in profile.deciles} == {7}
    assert sum(decile.window_count for decile in profile.deciles) == 70


def test_an_unavailable_value_is_counted_apart_rather_than_bucketed_as_zero() -> None:
    """A missing reading placed at the bottom of the range becomes an observation of a low value."""
    observations = [
        *_monotone(),
        _observation(None, OutcomeKind.TARGET_FIRST),
        _observation(None, OutcomeKind.STOP_FIRST),
    ]

    profile = _profile(observations)

    assert profile.total_window_count == 42
    assert profile.unavailable_count == 2
    assert sum(decile.window_count for decile in profile.deciles) == 40
    # The unavailable pair would have dragged the bottom decile's share had it been bucketed.
    assert profile.deciles[0].statistics.target_first_share == Decimal("0")


def test_values_are_ordered_before_bucketing_regardless_of_arrival_order() -> None:
    ascending = _profile(_monotone())
    descending = _profile(list(reversed(_monotone())))

    assert [decile.lower_bound for decile in ascending.deciles] == [
        decile.lower_bound for decile in descending.deciles
    ]
    assert ascending.gradient_edge == descending.gradient_edge


def test_deciles_are_ordered_and_their_bounds_do_not_run_backwards() -> None:
    profile = _profile(_monotone())

    bounds = [(decile.lower_bound, decile.upper_bound) for decile in profile.deciles]
    for lower, upper in bounds:
        assert lower <= upper
    assert bounds == sorted(bounds)


def test_a_sample_smaller_than_the_bucket_count_drops_empty_deciles() -> None:
    """An empty decile at an extreme would put a zero-window share into both readings."""
    profile = _profile([_observation("1", OutcomeKind.TARGET_FIRST)] * 3)

    assert len(profile.deciles) == 3
    assert [decile.index for decile in profile.deciles] == [1, 2, 3]


def test_a_decile_cannot_claim_statistics_that_miss_a_direction() -> None:
    with pytest.raises(ValidationError):
        FieldDecile(
            index=1,
            lower_bound=Decimal("0"),
            upper_bound=Decimal("1"),
            window_count=5,
            statistics=aggregate_outcomes(
                [_outcome(OutcomeKind.TARGET_FIRST, SignalDirection.LONG)] * 5
            ),
        )


def test_every_window_must_be_bucketed_or_counted_unavailable() -> None:
    with pytest.raises(ValidationError):
        FieldOutcomeProfile(
            pair="EURUSD",
            timeframe="M15",
            field_ref="market_context.volatility_ratio",
            total_window_count=10,
            unavailable_count=0,
            deciles=(),
            pooled_statistics=aggregate_outcomes([]),
        )


def test_the_band_reading_pools_counts_rather_than_averaging_shares() -> None:
    """Averaging would let a thinly resolved decile weigh as much as a heavily resolved one."""
    thin_middle = [
        _observation("5.0", OutcomeKind.TIMEOUT),
        _observation("5.1", OutcomeKind.TARGET_FIRST),
    ]
    observations = (
        [_observation("0.0", OutcomeKind.STOP_FIRST)] * 2
        + [_observation(f"{decile}.0", OutcomeKind.TARGET_FIRST) for decile in range(1, 9)]
        + thin_middle
        + [_observation("9.0", OutcomeKind.STOP_FIRST)] * 2
    )

    profile = _profile(observations)

    # Both extremes stopped, so whatever the middle did, the band edge must be strictly positive.
    assert profile.band_edge is not None
    assert profile.band_edge > Decimal("0")
