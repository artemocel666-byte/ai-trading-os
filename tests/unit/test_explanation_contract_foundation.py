from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.analysis_engine import AnalysisEngine
from app.domain.entities import Candle, Timeframe
from app.domain.entities.explanation import (
    MAXIMUM_EXPLANATION_LENGTH,
    ExplanationInput,
    ExplanationIssueCode,
    ExplanationValidationReport,
)
from app.domain.explanation_contract import (
    allowed_number_set,
    build_explanation_input,
    contains_actionable_russian_text,
    validate_explanation_text,
)
from app.domain.strategy_decision_composer import StrategyDecisionComposer
from app.domain.value_objects import CurrencyPair

PAIR = CurrencyPair(value="EURUSD")
BASE_TIME = datetime(2026, 7, 20, 8, 0, tzinfo=UTC)
CHECKED_AT = datetime(2026, 8, 1, 12, 0, tzinfo=UTC)
STEP = timedelta(minutes=15)


def _candle(index: int) -> Candle:
    open_time = BASE_TIME + (index * STEP)
    open_price = Decimal("1.1000") + (Decimal("0.0001") * Decimal(index))
    close_price = open_price + Decimal("0.0001")
    return Candle(
        provider="explanation-test",
        pair=PAIR,
        timeframe=Timeframe.M15,
        open_time=open_time,
        close_time=open_time + STEP,
        open=open_price,
        high=close_price + Decimal("0.0002"),
        low=open_price - Decimal("0.0002"),
        close=close_price,
        volume=Decimal("100"),
        is_closed=True,
    )


def _explanation_input(candle_count: int = 12) -> ExplanationInput:
    candles = [_candle(index) for index in range(candle_count)]
    as_of = BASE_TIME + (candle_count * STEP)
    snapshot = AnalysisEngine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=BASE_TIME,
        window_end=as_of,
        as_of=as_of,
        candles=candles,
        economic_events=[],
        moving_average_windows=(3,),
    )
    decision = StrategyDecisionComposer().compose(snapshot, as_of)
    return build_explanation_input(decision, snapshot)


def _validate(text: str, explanation_input: ExplanationInput | None = None):
    return validate_explanation_text(
        text,
        explanation_input or _explanation_input(),
        CHECKED_AT,
    )


def test_input_carries_rule_outcomes_and_readings() -> None:
    explanation_input = _explanation_input()

    assert explanation_input.pair == PAIR
    assert explanation_input.timeframe == Timeframe.M15
    assert explanation_input.project_phase == constants.PROJECT_PHASE
    assert len(explanation_input.ruleset_facts) == 4
    assert explanation_input.total_rule_count == 11
    assert explanation_input.used_candle_count == 12
    field_refs = {reading.field_ref for reading in explanation_input.readings}
    assert "market_context.volatility_ratio" in field_refs
    assert "data_quality.completeness_ratio" in field_refs


def test_input_exposes_no_direction_price_or_scoring_field() -> None:
    """The Phase 8 warning in PLANS.md, enforced: this is not ChiefAIRequest."""
    fields = set(ExplanationInput.model_fields)

    for forbidden in (
        "direction",
        "entry_price",
        "stop_loss",
        "take_profit",
        "position_size",
        "setup_score",
        "risk_percent",
        "confidence",
    ):
        assert forbidden not in fields


def test_unavailable_reading_stays_unavailable() -> None:
    explanation_input = _explanation_input()

    by_field = {reading.field_ref: reading for reading in explanation_input.readings}
    # No calendar events exist in this window, so elapsed time since a release is unmeasurable.
    assert by_field["event_context.minutes_since_latest_event"].value is None


def test_input_cannot_be_marked_actionable() -> None:
    explanation_input = _explanation_input()

    with pytest.raises(ValidationError):
        explanation_input.model_copy(update={"is_actionable": True}).model_validate(
            {**explanation_input.model_dump(), "is_actionable": True}
        )
    with pytest.raises(ValidationError):
        ExplanationInput(
            pair=PAIR,
            timeframe=Timeframe.M15,
            as_of=BASE_TIME,
            decision_status=explanation_input.decision_status,
            source_snapshot_id=explanation_input.source_snapshot_id,
            used_candle_count=1,
            expected_candle_count=1,
            is_actionable=True,
        )


def test_honest_russian_explanation_is_accepted() -> None:
    report = _validate(
        "Окно данных полное: использовано 12 свечей из 12. "
        "Правила качества данных пройдены полностью. "
        "Часть проверок недоступна, потому что в окне нет экономических событий."
    )

    assert report.accepted is True
    assert report.issues == ()


def test_fabricated_number_is_rejected() -> None:
    """The check 8B's adversarial tests rest on: a model may repeat, never invent."""
    report = _validate("Ожидаемое движение до 1.25 по паре EURUSD.")

    assert report.accepted is False
    assert ExplanationIssueCode.UNKNOWN_NUMBER in report.issue_codes


def test_numbers_from_the_input_are_accepted_in_any_written_form() -> None:
    explanation_input = _explanation_input()
    allowed = allowed_number_set(explanation_input)

    assert Decimal("12") in allowed
    # A ratio may be written as a percentage: completeness 1 -> 100%.
    assert Decimal("100") in allowed

    report = _validate("Полнота окна 100%, свечей 12,0 из 12.000.", explanation_input)

    assert report.accepted is True


@pytest.mark.parametrize(
    "text",
    [
        "ПОКУПАЙ EURUSD прямо сейчас.",
        "Рекомендую открыть позицию по паре.",
        "Ставьте стоп-лосс ниже минимума окна.",
        "Открывается сигнал на вход в рынок.",
        "Это хороший момент для сделки.",
    ],
)
def test_russian_trading_instructions_are_rejected(text: str) -> None:
    report = _validate(text)

    assert report.accepted is False
    assert ExplanationIssueCode.ACTIONABLE_TEXT in report.issue_codes


def test_english_trading_instructions_are_rejected_by_the_phase5_detector() -> None:
    report = _validate("Данные в норме, но stop-loss стоит поставить ниже.")

    assert report.accepted is False
    assert ExplanationIssueCode.ACTIONABLE_TEXT in report.issue_codes


def test_russian_detector_does_not_fire_on_neutral_wording() -> None:
    assert contains_actionable_russian_text("Окно данных полное, замеры в норме.") is False
    assert contains_actionable_russian_text("Правила качества данных пройдены.") is False


def test_emoji_in_the_body_is_rejected() -> None:
    # The Telegram formatter owns the single leading emoji; a body emoji would break that rule.
    report = _validate("Окно данных полное 📊 замеры в норме.")

    assert report.accepted is False
    assert ExplanationIssueCode.EMOJI_FOUND in report.issue_codes


def test_english_only_text_is_rejected() -> None:
    report = _validate("The data window looks complete and the rules are fine.")

    assert report.accepted is False
    assert ExplanationIssueCode.NOT_RUSSIAN in report.issue_codes


def test_empty_text_is_rejected_and_reports_only_that() -> None:
    report = _validate("   ")

    assert report.accepted is False
    assert report.issue_codes == (ExplanationIssueCode.EMPTY_TEXT,)


def test_overlong_text_is_rejected() -> None:
    report = _validate("Окно данных полное. " * 200)

    assert report.accepted is False
    assert ExplanationIssueCode.TOO_LONG in report.issue_codes
    assert len("Окно данных полное. " * 200) > MAXIMUM_EXPLANATION_LENGTH


def test_every_issue_is_reported_not_just_the_first() -> None:
    report = _validate("BUY now at 1.25 📈")

    assert {
        ExplanationIssueCode.NOT_RUSSIAN,
        ExplanationIssueCode.ACTIONABLE_TEXT,
        ExplanationIssueCode.EMOJI_FOUND,
        ExplanationIssueCode.UNKNOWN_NUMBER,
    } <= set(report.issue_codes)


def test_validation_report_cannot_claim_acceptance_with_issues() -> None:
    rejected = _validate("Цель 1.25.")

    with pytest.raises(ValidationError):
        ExplanationValidationReport(
            checked_at=CHECKED_AT,
            issues=rejected.issues,
            accepted=True,
        )


def test_project_phase_is_phase8a_explanation_contract_foundation() -> None:
    assert constants.PROJECT_PHASE == "phase_9a6_clean_calibration_foundation"
