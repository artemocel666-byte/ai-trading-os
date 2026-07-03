from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core.enums import Direction, MessageType
from app.domain.value_objects import CurrencyPair, EntryZone, Money, Percentage, Price


def test_currency_pair_splits_base_and_quote() -> None:
    pair = CurrencyPair(value="EURUSD")

    assert pair.base_currency == "EUR"
    assert pair.quote_currency == "USD"


def test_financial_value_objects_reject_binary_floats() -> None:
    with pytest.raises(ValidationError):
        Price(value=1.2345)
    with pytest.raises(ValidationError):
        Money(amount=100.0, currency="EUR")
    with pytest.raises(ValidationError):
        Percentage(value=0.5)


def test_entry_zone_requires_ordered_prices() -> None:
    zone = EntryZone(
        minimum=Price(value=Decimal("1.0800")),
        maximum=Price(value=Decimal("1.0810")),
    )
    assert zone.minimum.value <= zone.maximum.value

    with pytest.raises(ValidationError):
        EntryZone(
            minimum=Price(value=Decimal("1.0820")),
            maximum=Price(value=Decimal("1.0810")),
        )


def test_enum_serialization_is_stable() -> None:
    assert Direction.LONG.value == "LONG"
    assert MessageType.SYSTEM_STATUS.value == "SYSTEM_STATUS"
