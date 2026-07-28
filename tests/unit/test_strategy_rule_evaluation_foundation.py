from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.domain.analysis_engine import AnalysisEngine
from app.domain.entities import Candle, Timeframe
from app.domain.entities.rule_evaluation import (
    RuleEvaluationStatus,
    RuleSetEvaluationStatus,
)
from app.domain.entities.strategy_rules import (
    StrategyRuleCategory,
    StrategyRuleCondition,
    StrategyRuleOperator,
    StrategyRuleSet,
    StrategyRuleSeverity,
    StrategyRuleSpec,
    StrategyRuleValue,
)
from app.domain.strategy_field_resolver import resolve_field
from app.domain.strategy_rule_evaluator import StrategyRuleEvaluator, evaluate_condition
from app.domain.strategy_ruleset_registry import BUILTIN_STRATEGY_RULESET_FIXTURES
from app.domain.value_objects import CurrencyPair

PAIR = CurrencyPair(value="EURUSD")
BASE_TIME = datetime(2026, 7, 20, 8, 0, tzinfo=UTC)


def _candle(index: int) -> Candle:
    step = timedelta(minutes=15)
    open_time = BASE_TIME + (index * step)
    open_price = Decimal("1.1000") + (Decimal("0.0001") * Decimal(index))
    close_price = open_price + Decimal("0.0001")
    return Candle(
        provider="rule-evaluation-test",
        pair=PAIR,
        timeframe=Timeframe.M15,
        open_time=open_time,
        close_time=open_time + step,
        open=open_price,
        high=close_price + Decimal("0.0002"),
        low=open_price - Decimal("0.0002"),
        close=close_price,
        volume=Decimal("100"),
        is_closed=True,
    )


def _snapshot(candle_count: int, *, as_of_hour: int = 8):
    candles = [_candle(index) for index in range(candle_count)]
    as_of = BASE_TIME.replace(hour=as_of_hour) + timedelta(minutes=15 * candle_count)
    return AnalysisEngine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=BASE_TIME.replace(hour=as_of_hour),
        window_end=as_of,
        as_of=as_of,
        candles=candles,
        economic_events=[],
        moving_average_windows=(3,),
    )


def test_closed_candles_available_resolver() -> None:
    ready = _snapshot(3)
    empty = _snapshot(0)

    assert resolve_field("data_quality.closed_candles_available", ready) is True
    # With zero candles the analysis engine does not build a feature_snapshot at all
    # (blocked before feature computation), so the resolver reports "unavailable", not False.
    assert resolve_field("data_quality.closed_candles_available", empty) is None


def test_market_context_snapshot_ready_resolver() -> None:
    ready = _snapshot(3)

    assert resolve_field("market_context.snapshot_ready", ready) is True


def test_time_filter_session_name_resolver() -> None:
    london = _snapshot(1, as_of_hour=9)
    overlap = _snapshot(1, as_of_hour=13)
    quiet = _snapshot(1, as_of_hour=2)

    assert resolve_field("time_filter.session_name", london) == "london"
    assert resolve_field("time_filter.session_name", overlap) == "london"
    assert resolve_field("time_filter.session_name", quiet) is None


def test_unknown_field_ref_resolves_to_none() -> None:
    snapshot = _snapshot(1)

    assert resolve_field("market_context.unknown_leaf", snapshot) is None


def test_data_quality_value_resolvers() -> None:
    ready = _snapshot(12)
    empty = _snapshot(0)

    assert resolve_field("data_quality.used_candle_count", ready) == Decimal("12")
    assert resolve_field("data_quality.completeness_ratio", ready) == Decimal("1")
    assert resolve_field("data_quality.market_data_complete", ready) is True
    assert resolve_field("data_quality.latest_candle_age_minutes", ready) == Decimal("0")

    # A window the engine could not build reports "unavailable" rather than a fabricated value.
    for field_ref in (
        "data_quality.used_candle_count",
        "data_quality.completeness_ratio",
        "data_quality.market_data_complete",
        "data_quality.latest_candle_age_minutes",
    ):
        assert resolve_field(field_ref, empty) is None


def test_market_context_value_resolvers() -> None:
    ready = _snapshot(12)
    empty = _snapshot(0)

    volatility_ratio = resolve_field("market_context.volatility_ratio", ready)
    assert isinstance(volatility_ratio, Decimal)
    assert volatility_ratio > Decimal("0")
    assert isinstance(resolve_field("market_context.max_close_drawdown", ready), Decimal)

    assert resolve_field("market_context.volatility_ratio", empty) is None
    assert resolve_field("market_context.max_close_drawdown", empty) is None


def test_volatility_ratio_never_divides_by_zero() -> None:
    """A perfectly flat window has a zero average true range; the ratio must be unavailable."""
    flat_price = Decimal("1.1000")
    flat_candles = [
        Candle(
            provider="flat-window-test",
            pair=PAIR,
            timeframe=Timeframe.M15,
            open_time=BASE_TIME + (index * timedelta(minutes=15)),
            close_time=BASE_TIME + ((index + 1) * timedelta(minutes=15)),
            open=flat_price,
            high=flat_price,
            low=flat_price,
            close=flat_price,
            volume=Decimal("100"),
            is_closed=True,
        )
        for index in range(12)
    ]
    snapshot = AnalysisEngine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=BASE_TIME,
        window_end=BASE_TIME + timedelta(minutes=180),
        as_of=BASE_TIME + timedelta(minutes=180),
        candles=flat_candles,
        economic_events=[],
        moving_average_windows=(3,),
    )

    assert resolve_field("market_context.volatility_ratio", snapshot) is None


def test_time_filter_weekday_resolver() -> None:
    # BASE_TIME is 2026-07-20, a Monday -> weekday index 0.
    assert resolve_field("time_filter.utc_weekday", _snapshot(12)) == Decimal("0")


def test_evaluator_passes_builtin_data_quality_fixture() -> None:
    # A healthy window needs at least the BLOCKING minimum of eight usable candles.
    snapshot = _snapshot(12)
    ruleset = BUILTIN_STRATEGY_RULESET_FIXTURES["foundation.data_quality.v1"]

    report = StrategyRuleEvaluator().evaluate_ruleset(ruleset, snapshot, BASE_TIME)

    assert report.status == RuleSetEvaluationStatus.READY_FOR_REVIEW
    assert all(result.status == RuleEvaluationStatus.PASSED for result in report.results)
    assert report.is_actionable is False


def test_evaluator_blocks_a_window_with_too_few_candles() -> None:
    """The BLOCKING data-quality rule is what makes a thin window visibly different."""
    snapshot = _snapshot(3)
    ruleset = BUILTIN_STRATEGY_RULESET_FIXTURES["foundation.data_quality.v1"]

    report = StrategyRuleEvaluator().evaluate_ruleset(ruleset, snapshot, BASE_TIME)

    assert report.status == RuleSetEvaluationStatus.BLOCKED
    assert report.blocking_failure_count == 1


def test_evaluator_reports_unavailable_when_snapshot_has_no_feature_data() -> None:
    empty = _snapshot(0)
    ruleset = BUILTIN_STRATEGY_RULESET_FIXTURES["foundation.market_context.v1"]

    report = StrategyRuleEvaluator().evaluate_ruleset(ruleset, empty, BASE_TIME)

    assert report.results[0].status in (
        RuleEvaluationStatus.FAILED,
        RuleEvaluationStatus.UNAVAILABLE,
    )
    assert report.status in (RuleSetEvaluationStatus.BLOCKED, RuleSetEvaluationStatus.NOT_READY)


def test_evaluator_is_deterministic_for_identical_inputs() -> None:
    snapshot = _snapshot(3)
    ruleset = BUILTIN_STRATEGY_RULESET_FIXTURES["foundation.data_quality.v1"]
    evaluator = StrategyRuleEvaluator()

    first = evaluator.evaluate_ruleset(ruleset, snapshot, BASE_TIME)
    second = evaluator.evaluate_ruleset(ruleset, snapshot, BASE_TIME)

    assert first.deterministic_json() == second.deterministic_json()
    assert first.fingerprint_sha256() == second.fingerprint_sha256()


def _condition(**overrides: object) -> StrategyRuleCondition:
    defaults: dict[str, object] = {
        "field_ref": "market_context.synthetic_metric",
        "operator": StrategyRuleOperator.GT,
        "expected_value": StrategyRuleValue(value=Decimal("1.1000")),
    }
    defaults.update(overrides)
    return StrategyRuleCondition(**defaults)


def test_evaluate_condition_ordered_operators() -> None:
    gt_condition = _condition(operator=StrategyRuleOperator.GT)
    lt_condition = _condition(operator=StrategyRuleOperator.LT)

    assert evaluate_condition(gt_condition, Decimal("1.2000")) is True
    assert evaluate_condition(gt_condition, Decimal("1.0000")) is False
    assert evaluate_condition(lt_condition, Decimal("1.0000")) is True


def test_evaluate_condition_between_operator() -> None:
    between_condition = _condition(
        operator=StrategyRuleOperator.BETWEEN,
        expected_value=None,
        lower_bound=StrategyRuleValue(value=Decimal("1.0")),
        upper_bound=StrategyRuleValue(value=Decimal("2.0")),
    )

    assert evaluate_condition(between_condition, Decimal("1.5")) is True
    assert evaluate_condition(between_condition, Decimal("2.5")) is False


def test_evaluate_condition_type_mismatch_fails_closed_instead_of_raising() -> None:
    gt_condition = _condition(operator=StrategyRuleOperator.GT)

    assert evaluate_condition(gt_condition, "not-a-decimal") is False


def _rule(
    *,
    rule_id: str,
    severity: StrategyRuleSeverity,
    field_ref: str,
) -> StrategyRuleSpec:
    return StrategyRuleSpec(
        rule_id=rule_id,
        category=StrategyRuleCategory.DATA_QUALITY,
        severity=severity,
        condition=StrategyRuleCondition(field_ref=field_ref, operator=StrategyRuleOperator.EXISTS),
        description="synthetic severity-aggregation rule",
        enabled=False,
    )


@pytest.mark.parametrize(
    ("severity", "expected_status"),
    [
        (StrategyRuleSeverity.BLOCKING, RuleSetEvaluationStatus.BLOCKED),
        (StrategyRuleSeverity.REQUIRED, RuleSetEvaluationStatus.NOT_READY),
        (StrategyRuleSeverity.WARNING, RuleSetEvaluationStatus.READY_FOR_REVIEW),
    ],
)
def test_severity_aggregation(
    severity: StrategyRuleSeverity,
    expected_status: RuleSetEvaluationStatus,
) -> None:
    snapshot = _snapshot(3)
    ruleset = StrategyRuleSet(
        ruleset_version="test-v1",
        strategy_version="test-v1",
        name="severity aggregation",
        created_at=BASE_TIME,
        rules=(_rule(rule_id="missing.field", severity=severity, field_ref="data_quality.absent"),),
        enabled=False,
    )

    report = StrategyRuleEvaluator().evaluate_ruleset(ruleset, snapshot, BASE_TIME)

    assert report.status == expected_status
    assert report.is_actionable is False


def test_rule_set_evaluation_report_rejects_actionable_true() -> None:
    snapshot = _snapshot(3)
    ruleset = BUILTIN_STRATEGY_RULESET_FIXTURES["foundation.data_quality.v1"]
    report = StrategyRuleEvaluator().evaluate_ruleset(ruleset, snapshot, BASE_TIME)

    with pytest.raises(ValidationError):
        report.__class__(**{**report.model_dump(), "is_actionable": True})
