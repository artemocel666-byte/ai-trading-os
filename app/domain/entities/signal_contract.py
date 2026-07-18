import hashlib
import json
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.market_data import Timeframe
from app.domain.value_objects import CurrencyPair


class SignalDirection(StrEnum):
    LONG = "LONG"
    SHORT = "SHORT"


class SignalLifecycleStatus(StrEnum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class SignalActionability(StrEnum):
    NOT_ACTIONABLE = "NOT_ACTIONABLE"
    PAPER_ONLY = "PAPER_ONLY"
    LIVE_DISABLED = "LIVE_DISABLED"


def _reject_float(value: object, field_name: str) -> object:
    if isinstance(value, float):
        raise ValueError(f"{field_name} must use Decimal-compatible inputs, not float")
    return value


class SignalPricePlan(BaseModel):
    entry_min: Decimal = Field(gt=Decimal("0"))
    entry_max: Decimal = Field(gt=Decimal("0"))
    stop_loss: Decimal = Field(gt=Decimal("0"))
    take_profit_1: Decimal = Field(gt=Decimal("0"))
    take_profit_2: Decimal | None = Field(default=None, gt=Decimal("0"))

    model_config = ConfigDict(frozen=True)

    @field_validator(
        "entry_min", "entry_max", "stop_loss", "take_profit_1", "take_profit_2", mode="before"
    )
    @classmethod
    def reject_float_prices(cls, value: object) -> object:
        return _reject_float(value, "signal price")

    @model_validator(mode="after")
    def entry_range_must_be_ordered(self) -> Self:
        if self.entry_min > self.entry_max:
            raise ValueError("entry_min must be less than or equal to entry_max")
        return self


class SignalRiskPlan(BaseModel):
    risk_percent: Decimal | None = Field(default=None, gt=Decimal("0"), le=Decimal("5"))
    max_loss_amount: Decimal | None = Field(default=None, gt=Decimal("0"))
    position_size: Decimal | None = Field(default=None, gt=Decimal("0"))
    actionability: SignalActionability = SignalActionability.NOT_ACTIONABLE

    model_config = ConfigDict(frozen=True)

    @field_validator("risk_percent", "max_loss_amount", "position_size", mode="before")
    @classmethod
    def reject_float_risk_values(cls, value: object) -> object:
        return _reject_float(value, "signal risk value")


class SignalContract(BaseModel):
    contract_version: str = Field(min_length=1)
    pair: CurrencyPair
    timeframe: Timeframe
    direction: SignalDirection
    status: SignalLifecycleStatus = SignalLifecycleStatus.DRAFT
    actionability: SignalActionability = SignalActionability.NOT_ACTIONABLE
    created_at: datetime
    valid_until: datetime
    strategy_version: str = Field(min_length=1)
    price_plan: SignalPricePlan
    risk_plan: SignalRiskPlan | None = None
    rationale_summary: str | None = Field(default=None, max_length=1000)
    evidence_ids: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    source_snapshot_id: str | None = Field(default=None, min_length=64, max_length=64)
    fingerprint: str | None = Field(default=None, min_length=64, max_length=64)

    model_config = ConfigDict(frozen=True)

    @field_validator("created_at", "valid_until")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("evidence_ids", "warnings", mode="before")
    @classmethod
    def normalize_string_collections(cls, value: object) -> tuple[str, ...]:
        if value is None:
            return ()
        if isinstance(value, str):
            raw_items: tuple[object, ...] = (value,)
        elif isinstance(value, list | set | tuple):
            raw_items = tuple(value)
        else:
            raise ValueError("signal string collections must be lists, sets, tuples, or strings")
        return tuple(sorted({str(item).strip() for item in raw_items if str(item).strip()}))

    @model_validator(mode="after")
    def validate_contract(self) -> Self:
        if self.valid_until <= self.created_at:
            raise ValueError("valid_until must be after created_at")
        if self.direction == SignalDirection.LONG:
            if self.price_plan.stop_loss >= self.price_plan.entry_min:
                raise ValueError("LONG stop_loss must be below entry_min")
            if self.price_plan.take_profit_1 <= self.price_plan.entry_max:
                raise ValueError("LONG take_profit_1 must be above entry_max")
            if (
                self.price_plan.take_profit_2 is not None
                and self.price_plan.take_profit_2 <= self.price_plan.take_profit_1
            ):
                raise ValueError("LONG take_profit_2 must be above take_profit_1")
        else:
            if self.price_plan.stop_loss <= self.price_plan.entry_max:
                raise ValueError("SHORT stop_loss must be above entry_max")
            if self.price_plan.take_profit_1 >= self.price_plan.entry_min:
                raise ValueError("SHORT take_profit_1 must be below entry_min")
            if (
                self.price_plan.take_profit_2 is not None
                and self.price_plan.take_profit_2 >= self.price_plan.take_profit_1
            ):
                raise ValueError("SHORT take_profit_2 must be below take_profit_1")
        return self

    @property
    def is_actionable(self) -> bool:
        return False

    def canonical_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"fingerprint"})

    def deterministic_json(self) -> str:
        return json.dumps(
            self.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def fingerprint_sha256(self) -> str:
        canonical = json.dumps(
            self.canonical_payload(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
