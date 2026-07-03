from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CurrencyPair(BaseModel):
    value: str = Field(pattern=r"^[A-Z]{6}$")

    model_config = ConfigDict(frozen=True)

    @property
    def base_currency(self) -> str:
        return self.value[:3]

    @property
    def quote_currency(self) -> str:
        return self.value[3:]


class Price(BaseModel):
    value: Decimal = Field(gt=Decimal("0"))

    model_config = ConfigDict(frozen=True)

    @field_validator("value", mode="before")
    @classmethod
    def reject_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("financial values must use Decimal-compatible inputs, not float")
        return value


class Money(BaseModel):
    amount: Decimal
    currency: str = Field(pattern=r"^[A-Z]{3}$")

    model_config = ConfigDict(frozen=True)

    @field_validator("amount", mode="before")
    @classmethod
    def reject_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("money must use Decimal-compatible inputs, not float")
        return value


class Percentage(BaseModel):
    value: Decimal = Field(ge=Decimal("0"), le=Decimal("100"))

    model_config = ConfigDict(frozen=True)

    @field_validator("value", mode="before")
    @classmethod
    def reject_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("percentage must use Decimal-compatible inputs, not float")
        return value


class EntryZone(BaseModel):
    minimum: Price
    maximum: Price

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def minimum_must_not_exceed_maximum(self) -> Self:
        if self.minimum.value > self.maximum.value:
            raise ValueError("entry zone minimum must be less than or equal to maximum")
        return self
