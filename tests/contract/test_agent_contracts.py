from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.core.enums import AgentVerdict, ConfidenceLevel, Direction
from app.domain.value_objects import CurrencyPair
from app.schemas.agents import AgentReport, ChiefAIRequest, EvidenceReference


def _evidence() -> EvidenceReference:
    return EvidenceReference(
        evidence_type="candle",
        timeframe="M15",
        candle_timestamp=datetime.now(UTC),
        metric_name="close",
        metric_value=Decimal("1.0812"),
        source="test",
    )


def _agent_report(score: int = 85) -> AgentReport:
    return AgentReport(
        report_id=uuid4(),
        scan_id=uuid4(),
        agent_name="structure_agent",
        pair=CurrencyPair(value="EURUSD"),
        direction=Direction.NEUTRAL,
        verdict=AgentVerdict.CANDIDATE,
        score=score,
        confidence=ConfidenceLevel.MEDIUM,
        summary_ru="Рынок требует дополнительного подтверждения.",
        reasons_for_ru=["Есть структурный импульс."],
        reasons_against_ru=["Подтверждение старшего таймфрейма отсутствует."],
        invalid_if_ru=["Цена закрепится ниже локального уровня."],
        evidence=[_evidence()],
        data_timestamp=datetime.now(UTC),
        rule_version="foundation-v1",
        model_version=None,
        created_at=datetime.now(UTC),
    )


def test_agent_report_requires_explanations_and_evidence() -> None:
    report = _agent_report()

    assert report.reasons_for_ru
    assert report.reasons_against_ru
    assert report.invalid_if_ru
    assert report.evidence


@pytest.mark.parametrize("score", [-1, 101])
def test_agent_report_score_bounds(score: int) -> None:
    with pytest.raises(ValidationError):
        _agent_report(score=score)


def test_agent_report_requires_timezone_aware_timestamps() -> None:
    with pytest.raises(ValidationError):
        AgentReport(
            report_id=uuid4(),
            scan_id=uuid4(),
            agent_name="structure_agent",
            pair=CurrencyPair(value="EURUSD"),
            direction=Direction.NEUTRAL,
            verdict=AgentVerdict.CANDIDATE,
            score=85,
            confidence=ConfidenceLevel.MEDIUM,
            summary_ru="Рынок требует дополнительного подтверждения.",
            reasons_for_ru=["Есть структурный импульс."],
            reasons_against_ru=["Подтверждение отсутствует."],
            invalid_if_ru=["Цена сломает уровень."],
            evidence=[_evidence()],
            data_timestamp=datetime.now(),
            rule_version="foundation-v1",
            created_at=datetime.now(UTC),
        )


def test_evidence_reference_rejects_naive_timestamp() -> None:
    with pytest.raises(ValidationError):
        EvidenceReference(
            evidence_type="candle",
            timeframe="H1",
            candle_timestamp=datetime.now(),
            metric_name="close",
            metric_value=Decimal("1.0812"),
            source="test",
        )


def test_chief_ai_request_preserves_deterministic_inputs_contract() -> None:
    request = ChiefAIRequest(
        deterministic_decision="NO_TRADE",
        setup_score=80,
        risk_percent=Decimal("0.5"),
        agent_reports=[_agent_report()],
    )

    assert request.deterministic_decision == "NO_TRADE"
    assert request.setup_score == 80
    assert request.risk_percent == Decimal("0.5")
