from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.entities import Timeframe
from app.domain.entities.signal_contract import (
    SignalActionability,
    SignalContract,
    SignalDirection,
    SignalLifecycleStatus,
    SignalPricePlan,
    SignalRiskPlan,
)
from app.domain.value_objects import CurrencyPair

PAIR = CurrencyPair(value="EURUSD")
CREATED_AT = datetime(2026, 7, 18, 9, 0, tzinfo=UTC)
VALID_UNTIL = CREATED_AT + timedelta(minutes=30)


def _long_price_plan() -> SignalPricePlan:
    return SignalPricePlan(
        entry_min=Decimal("1.1000"),
        entry_max=Decimal("1.1010"),
        stop_loss=Decimal("1.0950"),
        take_profit_1=Decimal("1.1060"),
        take_profit_2=Decimal("1.1100"),
    )


def _short_price_plan() -> SignalPricePlan:
    return SignalPricePlan(
        entry_min=Decimal("1.1000"),
        entry_max=Decimal("1.1010"),
        stop_loss=Decimal("1.1060"),
        take_profit_1=Decimal("1.0950"),
        take_profit_2=Decimal("1.0910"),
    )


def _contract(**overrides: object) -> SignalContract:
    values: dict[str, object] = {
        "contract_version": "phase4a-contract-v1",
        "pair": PAIR,
        "timeframe": Timeframe.M15,
        "direction": SignalDirection.LONG,
        "created_at": CREATED_AT,
        "valid_until": VALID_UNTIL,
        "strategy_version": "future-strategy-contract-v1",
        "price_plan": _long_price_plan(),
        "evidence_ids": ("snapshot-b", "snapshot-a", "snapshot-a"),
        "warnings": ("contract only",),
        "source_snapshot_id": "a" * 64,
    }
    values.update(overrides)
    return SignalContract(**values)


def test_project_phase_has_advanced_to_phase4e_disabled_pipeline_report_shell_foundation() -> None:
    assert constants.PROJECT_PHASE == "phase_5_manual_review_layer_foundation"


def test_signal_contract_models_are_immutable() -> None:
    contract = _contract()

    with pytest.raises(ValidationError):
        contract.status = SignalLifecycleStatus.VALIDATED
    with pytest.raises(ValidationError):
        contract.price_plan.entry_min = Decimal("1.0990")


def test_signal_contract_normalizes_timestamps_to_utc() -> None:
    offset = timezone(timedelta(hours=2))
    contract = _contract(
        created_at=datetime(2026, 7, 18, 11, 0, tzinfo=offset),
        valid_until=datetime(2026, 7, 18, 11, 30, tzinfo=offset),
    )

    assert contract.created_at == CREATED_AT
    assert contract.valid_until == VALID_UNTIL


def test_signal_contract_requires_valid_until_after_created_at() -> None:
    with pytest.raises(ValidationError):
        _contract(valid_until=CREATED_AT)


def test_signal_price_plan_requires_ordered_entry_range() -> None:
    with pytest.raises(ValidationError):
        SignalPricePlan(
            entry_min=Decimal("1.1020"),
            entry_max=Decimal("1.1010"),
            stop_loss=Decimal("1.0950"),
            take_profit_1=Decimal("1.1060"),
        )


def test_signal_contract_validates_long_price_plan() -> None:
    assert _contract(direction=SignalDirection.LONG, price_plan=_long_price_plan()).direction == (
        SignalDirection.LONG
    )

    with pytest.raises(ValidationError):
        _contract(
            direction=SignalDirection.LONG,
            price_plan=_long_price_plan().model_copy(update={"stop_loss": Decimal("1.1000")}),
        )
    with pytest.raises(ValidationError):
        _contract(
            direction=SignalDirection.LONG,
            price_plan=_long_price_plan().model_copy(update={"take_profit_1": Decimal("1.1010")}),
        )
    with pytest.raises(ValidationError):
        _contract(
            direction=SignalDirection.LONG,
            price_plan=_long_price_plan().model_copy(update={"take_profit_2": Decimal("1.1060")}),
        )


def test_signal_contract_validates_short_price_plan() -> None:
    assert _contract(direction=SignalDirection.SHORT, price_plan=_short_price_plan()).direction == (
        SignalDirection.SHORT
    )

    with pytest.raises(ValidationError):
        _contract(
            direction=SignalDirection.SHORT,
            price_plan=_short_price_plan().model_copy(update={"stop_loss": Decimal("1.1010")}),
        )
    with pytest.raises(ValidationError):
        _contract(
            direction=SignalDirection.SHORT,
            price_plan=_short_price_plan().model_copy(update={"take_profit_1": Decimal("1.1000")}),
        )
    with pytest.raises(ValidationError):
        _contract(
            direction=SignalDirection.SHORT,
            price_plan=_short_price_plan().model_copy(update={"take_profit_2": Decimal("1.0950")}),
        )


def test_signal_risk_plan_rejects_invalid_values() -> None:
    with pytest.raises(ValidationError):
        SignalRiskPlan(risk_percent=Decimal("5.1"))
    with pytest.raises(ValidationError):
        SignalRiskPlan(max_loss_amount=Decimal("0"))
    with pytest.raises(ValidationError):
        SignalRiskPlan(position_size=Decimal("0"))


def test_signal_contract_defaults_to_not_actionable() -> None:
    contract = _contract()
    risk_plan = SignalRiskPlan()

    assert contract.actionability == SignalActionability.NOT_ACTIONABLE
    assert risk_plan.actionability == SignalActionability.NOT_ACTIONABLE
    assert contract.is_actionable is False


def test_signal_contract_serializes_deterministically_and_round_trips() -> None:
    contract = _contract()
    same_contract = _contract(evidence_ids=("snapshot-a", "snapshot-b"))

    assert contract.evidence_ids == ("snapshot-a", "snapshot-b")
    assert contract.deterministic_json() == same_contract.deterministic_json()
    assert SignalContract.model_validate_json(contract.deterministic_json()) == contract


def test_signal_contract_fingerprint_is_deterministic() -> None:
    contract = _contract()
    same_contract = _contract(evidence_ids=("snapshot-b", "snapshot-a"))

    assert contract.fingerprint_sha256() == same_contract.fingerprint_sha256()
    assert len(contract.fingerprint_sha256()) == 64


def test_signal_contract_fingerprint_changes_when_key_fields_change() -> None:
    contract = _contract()
    changed = _contract(direction=SignalDirection.SHORT, price_plan=_short_price_plan())

    assert contract.fingerprint_sha256() != changed.fingerprint_sha256()
