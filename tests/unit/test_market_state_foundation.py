from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.entities.calibration import FieldDistribution
from app.domain.entities.market_state import CurrencyStrengthReading, HistoricalReading
from app.domain.market_state import (
    currency_strength,
    percentile_rank,
    read_against_history,
)
from app.domain.rule_calibration import nearest_rank, summarize_field
from app.presentation.readings import (
    UNAVAILABLE_RU,
    format_currency_strength,
    format_distribution,
    format_historical_reading,
)

NOW = datetime(2026, 8, 20, tzinfo=UTC)


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_10_3_hidden_concentration"


def test_a_rank_is_the_inverse_of_the_percentile_helper_not_a_second_copy() -> None:
    """Hand-computed. `nearest_rank` maps a percent to a value; this maps a value to a percent.

    Neither can be written in terms of the other without doing the other's work, which is why this
    is an inverse rather than the duplication this project keeps having to repair.
    """
    history = [Decimal(n) for n in (1, 2, 3, 4, 5)]

    assert percentile_rank(history, Decimal("3")) == 60
    assert percentile_rank(history, Decimal("5")) == 100
    assert percentile_rank(history, Decimal("0")) == 0
    assert nearest_rank(history, 60) == Decimal("3")


def test_a_rank_needs_something_to_rank_against() -> None:
    with pytest.raises(ValueError, match="needs a sample"):
        percentile_rank([], Decimal("1"))


def test_a_reading_carries_the_history_that_gives_it_a_scale() -> None:
    """`волатильность 1.23` says nothing; the same number at the 94th percentile says something."""
    history = [Decimal(n) / Decimal(1000) for n in range(1, 101)]

    reading = read_against_history(
        instrument="EURUSD",
        field_ref="daily_range",
        current=Decimal("0.094"),
        history=history,
    )

    assert reading is not None
    assert reading.percentile == 94
    assert reading.observation_count == 100


def test_no_history_yields_no_reading_rather_than_an_invented_percentile() -> None:
    assert (
        read_against_history(
            instrument="EURUSD", field_ref="daily_range", current=Decimal("1"), history=[]
        )
        is None
    )


def test_a_percentile_without_observations_is_refused_by_the_type() -> None:
    with pytest.raises(ValidationError):
        HistoricalReading(
            instrument="EURUSD",
            field_ref="daily_range",
            current=Decimal("1"),
            percentile=50,
            distribution=FieldDistribution(field_ref="daily_range", observed_count=0),
        )


def test_a_pair_move_is_a_statement_about_two_currencies_at_once() -> None:
    """Criterion 5, hand-computed, and chosen so a lone mean would mislead.

    EURUSD +2%, EURJPY +4%, USDJPY +2%. The euro rose against both counterparts and the yen fell
    against both — each moved one way against everything. **The dollar's mean is exactly zero while
    it moved two percent in each direction**, which is precisely the case a single average hides and
    the reason the range travels with it.
    """
    readings = {
        reading.currency: reading
        for reading in currency_strength(
            {
                "EURUSD": Decimal("0.02"),
                "EURJPY": Decimal("0.04"),
                "USDJPY": Decimal("0.02"),
            }
        )
    }

    assert readings["EUR"].mean_move == Decimal("0.03")
    assert (readings["EUR"].lowest_move, readings["EUR"].highest_move) == (
        Decimal("0.02"),
        Decimal("0.04"),
    )
    assert readings["EUR"].is_broad is True

    assert readings["JPY"].mean_move == Decimal("-0.03")
    assert readings["JPY"].is_broad is True

    assert readings["USD"].mean_move == Decimal("0")
    assert (readings["USD"].lowest_move, readings["USD"].highest_move) == (
        Decimal("-0.02"),
        Decimal("0.02"),
    )
    assert readings["USD"].is_broad is False


def test_a_malformed_symbol_is_refused_rather_than_split_wrongly() -> None:
    with pytest.raises(ValueError, match="six letters"):
        currency_strength({"EUR": Decimal("0.01")})


def test_a_mean_outside_the_range_it_averages_is_impossible() -> None:
    with pytest.raises(ValidationError):
        CurrencyStrengthReading(
            currency="EUR",
            observation_count=2,
            mean_move=Decimal("0.10"),
            lowest_move=Decimal("0.01"),
            highest_move=Decimal("0.02"),
        )


def test_a_distribution_is_never_rendered_as_its_middle_alone() -> None:
    """Criterion 1, at the one function that is allowed to do the rendering.

    The entity has refused to *hold* a lonely median since Phase 4. Nothing stopped a formatter from
    printing one out of a complete distribution, and that gap is what this slice closes.
    """
    distribution = summarize_field("daily_range", [Decimal(n) for n in range(1, 21)])

    text = format_distribution(distribution)

    assert "медиана" in text
    assert "разброс" in text
    assert "наблюдений 20" in text


def test_an_empty_distribution_says_so_rather_than_reporting_a_zero() -> None:
    text = format_distribution(FieldDistribution(field_ref="daily_range", observed_count=0))

    assert text == UNAVAILABLE_RU
    assert "0.00%" not in text


def test_a_rendered_reading_states_its_sample_size() -> None:
    """Criterion 2. A statement about the past without its n is refused by the renderer."""
    reading = read_against_history(
        instrument="EURUSD",
        field_ref="daily_range",
        current=Decimal("0.05"),
        history=[Decimal(n) / Decimal(100) for n in range(1, 11)],
    )
    assert reading is not None

    text = format_historical_reading(reading)

    assert "наблюдений 10" in text
    assert "перцентиль" in text


def test_a_currency_line_shows_the_range_it_averaged() -> None:
    text = format_currency_strength(
        CurrencyStrengthReading(
            currency="USD",
            observation_count=2,
            mean_move=Decimal("0"),
            lowest_move=Decimal("-0.02"),
            highest_move=Decimal("0.02"),
        )
    )

    assert "в среднем" in text
    assert "-2.00%" in text
    assert "+2.00%" in text
    assert "разнонаправленно" in text
