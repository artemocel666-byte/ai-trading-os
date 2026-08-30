from datetime import UTC, datetime
from decimal import Decimal

import httpx
import pytest
from pydantic import ValidationError

from app.adapters.cftc_positioning import (
    BASKET_CURRENCIES,
    CURRENCY_TO_CONTRACT,
    CftcPositioningAdapter,
)
from app.core import constants
from app.core.exceptions import ProviderInvalidPayloadError, ProviderUnsupportedRequestError
from app.domain.currency_universe import UNIVERSE_CURRENCIES
from app.domain.entities.positioning import PositioningReading
from app.domain.market_state import read_against_history
from app.presentation.readings import format_positioning

TUESDAY = datetime(2026, 8, 18, tzinfo=UTC)
SATURDAY = datetime(2026, 8, 22, tzinfo=UTC)


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_11_2_forecast_guard"


def _reading(
    *, currency: str = "EUR", long_side: int = 60_000, short_side: int = 40_000, oi: int = 200_000
) -> PositioningReading:
    return PositioningReading(
        provider="cftc",
        contract_code=CURRENCY_TO_CONTRACT.get(currency, "099741"),
        currency=currency,
        report_date=TUESDAY,
        noncommercial_long=long_side,
        noncommercial_short=short_side,
        open_interest=oi,
        is_basket=currency in BASKET_CURRENCIES,
    )


def test_eight_currencies_are_mapped_and_two_are_not() -> None:
    """Criterion 1. There is no Norwegian krone contract, and the Swedish one died in 1998."""
    assert set(CURRENCY_TO_CONTRACT) == {"EUR", "JPY", "GBP", "CHF", "CAD", "AUD", "NZD", "USD"}
    assert UNIVERSE_CURRENCIES - set(CURRENCY_TO_CONTRACT) == {"NOK", "SEK"}


def test_the_mapping_is_by_contract_code_not_by_name() -> None:
    """Criterion 2, and the criterion the whole phase turned on.

    `NZ DOLLAR` and `USD INDEX` were renamed in early 2022; their previous names stop on
    2022-02-01 while the codes below run unchanged since 1999 and 1992. A name-keyed mapping would
    have produced two truncated series beside six complete ones, and every percentile taken against
    them would have been a percentile of the wrong history.

    The values are pinned because they are the identity that survived the rename — changing one
    silently repoints a series at a different contract.
    """
    assert CURRENCY_TO_CONTRACT["NZD"] == "112741"
    assert CURRENCY_TO_CONTRACT["USD"] == "098662"
    for code in CURRENCY_TO_CONTRACT.values():
        assert code.isdigit(), code


@pytest.mark.asyncio
async def test_an_unmapped_currency_is_refused_rather_than_guessed() -> None:
    adapter = CftcPositioningAdapter(client=httpx.AsyncClient())

    with pytest.raises(ProviderUnsupportedRequestError):
        await adapter.get_positioning("NOK")


def test_position_is_a_share_of_open_interest_not_a_contract_count() -> None:
    """Hand-computed: 60,000 long against 40,000 short over 200,000 open interest is +10%.

    Raw counts compare neither between currencies nor across decades — the euro contract dwarfs the
    New Zealand one, and every contract has grown.
    """
    assert _reading().net_share == Decimal("0.1")


def test_open_interest_of_zero_is_refused_by_the_type() -> None:
    """Criterion 5. A zero denominator would arrive downstream as a position of zero."""
    with pytest.raises(ValidationError):
        _reading(oi=0)


def test_a_reading_knows_how_old_it_is() -> None:
    """Criterion 3. The report describes Tuesday and is published Friday; it is never "now"."""
    assert _reading().age_in_days(SATURDAY) == 4


def test_a_report_date_is_a_whole_day() -> None:
    with pytest.raises(ValidationError):
        PositioningReading(
            provider="cftc",
            contract_code="099741",
            currency="EUR",
            report_date=datetime(2026, 8, 18, 13, 30, tzinfo=UTC),
            noncommercial_long=1,
            noncommercial_short=1,
            open_interest=10,
        )


def test_the_dollar_is_marked_as_a_basket() -> None:
    """Criterion 4. Net long the euro against the dollar and net long a dollar basket differ."""
    assert set(BASKET_CURRENCIES) == {"USD"}
    assert _reading(currency="USD").is_basket is True
    assert _reading(currency="EUR").is_basket is False


def _payload(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return rows


def _row(date: str, long_side: str, short_side: str, oi: str) -> dict[str, str]:
    return {
        "report_date_as_yyyy_mm_dd": date,
        "noncomm_positions_long_all": long_side,
        "noncomm_positions_short_all": short_side,
        "open_interest_all": oi,
    }


def _adapter_returning(rows: list[dict[str, str]]) -> CftcPositioningAdapter:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=rows))
    return CftcPositioningAdapter(client=httpx.AsyncClient(transport=transport))


@pytest.mark.asyncio
async def test_a_row_without_open_interest_is_skipped_not_divided() -> None:
    adapter = _adapter_returning(
        _payload(
            [
                _row("2020-01-07T00:00:00.000", "100", "50", "1000"),
                _row("2020-01-14T00:00:00.000", "100", "50", "0"),
                _row("2020-01-21T00:00:00.000", "100", "50", "2000"),
            ]
        )
    )

    readings = await adapter.get_positioning("EUR")

    assert len(readings) == 2
    assert [r.report_date.date().isoformat() for r in readings] == ["2020-01-07", "2020-01-21"]


@pytest.mark.asyncio
async def test_a_series_that_is_empty_throughout_is_refused() -> None:
    """Silence is not data — the same rule the FRED adapter settled on in 9D-3."""
    adapter = _adapter_returning(_payload([_row("2020-01-07T00:00:00.000", "100", "50", "0")]))

    with pytest.raises(ProviderInvalidPayloadError):
        await adapter.get_positioning("EUR")


@pytest.mark.asyncio
async def test_a_malformed_row_is_skipped_rather_than_destroying_the_series() -> None:
    adapter = _adapter_returning(
        _payload(
            [
                _row("2020-01-07T00:00:00.000", "100", "50", "1000"),
                {"report_date_as_yyyy_mm_dd": "not-a-date"},
                _row("2020-01-21T00:00:00.000", "100", "50", "2000"),
            ]
        )
    )

    readings = await adapter.get_positioning("EUR")

    assert len(readings) == 2


def test_a_positioning_percentile_uses_the_existing_machinery() -> None:
    """Criterion 6. No new percentile definition appears; `read_against_history` is reused."""
    history = [Decimal(n) / Decimal(100) for n in range(1, 101)]

    reading = read_against_history(
        instrument="EUR",
        field_ref="net_positioning_share",
        current=Decimal("0.75"),
        history=history,
    )

    assert reading is not None
    assert reading.percentile == 75
    assert reading.observation_count == 100


def test_a_rendered_reading_states_its_date_and_its_age() -> None:
    text = format_positioning(_reading(), as_of=SATURDAY)

    assert "+10.0%" in text
    assert "2026-08-18" in text
    assert "4 дн." in text


def test_the_dollar_line_says_it_is_a_basket() -> None:
    text = format_positioning(_reading(currency="USD"), as_of=SATURDAY)

    assert "корзины" in text
