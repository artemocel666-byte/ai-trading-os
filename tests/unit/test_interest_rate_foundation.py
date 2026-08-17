from datetime import UTC, datetime
from decimal import Decimal

import httpx
import pytest
from pydantic import ValidationError

from app.adapters.fred_rates import CURRENCY_TO_SERIES, FredInterestRateAdapter
from app.core import constants
from app.core.exceptions import ProviderInvalidPayloadError, ProviderUnsupportedRequestError
from app.domain.currency_universe import UNIVERSE_CURRENCIES
from app.domain.entities.interest_rate import FRED_PROVIDER_NAME, InterestRate
from scripts.backfill_interest_rates import RATE_LAG_MONTHS, _missing_months, _usable_anchors

JANUARY = datetime(2020, 1, 1, tzinfo=UTC)
FEBRUARY = datetime(2020, 2, 1, tzinfo=UTC)
MARCH = datetime(2020, 3, 1, tzinfo=UTC)
APRIL = datetime(2020, 4, 1, tzinfo=UTC)


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_9d3_interest_rate_ingestion"


def _rate(as_of: datetime, value: str, currency: str = "USD") -> InterestRate:
    return InterestRate(
        provider=FRED_PROVIDER_NAME,
        source_series="IR3TIB01USM156N",
        currency=currency,
        as_of=as_of,
        annual_rate=Decimal(value),
    )


def test_a_negative_rate_is_accepted() -> None:
    """JPY, CHF and EUR all spent years below zero.

    A positivity validator would reject real observations, so there is none — and this test exists
    so nobody adds one later thinking its absence was an oversight.
    """
    rate = _rate(APRIL, "-0.00039", currency="JPY")

    assert rate.annual_rate < 0


def test_a_rate_must_sit_on_the_first_instant_of_a_month() -> None:
    """The source publishes one value per month; two rows for one month would defeat the key."""
    with pytest.raises(ValidationError):
        _rate(datetime(2020, 1, 15, tzinfo=UTC), "0.0384")


def test_a_rate_cannot_be_built_from_a_float() -> None:
    with pytest.raises(ValidationError):
        InterestRate(
            provider=FRED_PROVIDER_NAME,
            source_series="X",
            currency="USD",
            as_of=JANUARY,
            annual_rate=0.0384,  # type: ignore[arg-type]
        )


def _adapter() -> FredInterestRateAdapter:
    """`_parse_series` is pure — no request is made, so the client is never touched."""
    return FredInterestRateAdapter(client=httpx.AsyncClient())


def _csv(*rows: str) -> str:
    return "\n".join(("observation_date,IR3TIB01USM156N", *rows))


def test_percent_becomes_a_fraction_at_the_boundary() -> None:
    """The source says 3.84 meaning 3.84% per annum; everything downstream sees 0.0384."""
    rates = _adapter()._parse_series(
        _csv("2020-01-01,3.84"), currency="USD", series="IR3TIB01USM156N"
    )

    assert len(rates) == 1
    assert rates[0].annual_rate == Decimal("0.0384")


def test_an_empty_month_is_absent_rather_than_zero() -> None:
    """The USD series really does leave April 2020 blank.

    A zero there would state a rate that was never published, and would quietly drag any average
    that touched it — the same reason an unavailable field is counted apart rather than bucketed.
    """
    rates = _adapter()._parse_series(
        _csv("2020-03-01,1.10", "2020-04-01,", "2020-05-01,0.40"),
        currency="USD",
        series="IR3TIB01USM156N",
    )

    assert [rate.as_of for rate in rates] == [MARCH, datetime(2020, 5, 1, tzinfo=UTC)]
    assert all(rate.annual_rate != 0 for rate in rates)


def test_a_dot_placeholder_is_also_treated_as_absent() -> None:
    rates = _adapter()._parse_series(
        _csv("2020-01-01,.", "2020-02-01,1.00"), currency="USD", series="IR3TIB01USM156N"
    )

    assert [rate.as_of for rate in rates] == [FEBRUARY]


def test_a_series_with_no_observations_at_all_is_refused() -> None:
    """Silence is not data. An all-empty series is a broken fetch, not a currency without rates."""
    with pytest.raises(ProviderInvalidPayloadError):
        _adapter()._parse_series(
            _csv("2020-01-01,", "2020-02-01,"), currency="USD", series="IR3TIB01USM156N"
        )


def test_an_unexpected_header_is_refused_rather_than_guessed() -> None:
    with pytest.raises(ProviderInvalidPayloadError):
        _adapter()._parse_series(
            "date,value\n2020-01-01,1.0", currency="USD", series="IR3TIB01USM156N"
        )


def test_rows_come_back_oldest_first() -> None:
    rates = _adapter()._parse_series(
        _csv("2020-03-01,3.0", "2020-01-01,1.0", "2020-02-01,2.0"),
        currency="USD",
        series="IR3TIB01USM156N",
    )

    assert [rate.as_of for rate in rates] == [JANUARY, FEBRUARY, MARCH]


@pytest.mark.asyncio
async def test_a_currency_with_no_mapped_series_is_refused() -> None:
    with pytest.raises(ProviderUnsupportedRequestError):
        await _adapter().get_monthly_rates("XYZ")


def test_every_universe_currency_has_a_series() -> None:
    """A currency in the universe with no rate series would silently shrink the cross-section."""
    assert set(CURRENCY_TO_SERIES) >= UNIVERSE_CURRENCIES


def test_gaps_inside_a_series_are_found_and_edges_are_not() -> None:
    """A gap between two observations is an absence; the ends are where the data stops."""
    present = {JANUARY, MARCH}

    assert _missing_months(present, JANUARY, MARCH) == [FEBRUARY]
    assert _missing_months(present, JANUARY, JANUARY) == []


def test_an_anchor_is_complete_only_when_every_currency_has_the_lagged_month() -> None:
    """The figure Phase 9D-4 depends on, counted here rather than discovered there."""
    assert RATE_LAG_MONTHS == 2
    complete, total = _usable_anchors(
        {"USD": {JANUARY, FEBRUARY}, "EUR": {JANUARY}},
        first_anchor=MARCH,
        last_anchor=APRIL,
    )

    # March needs January (both have it); April needs February (EUR does not).
    assert (complete, total) == (1, 2)
