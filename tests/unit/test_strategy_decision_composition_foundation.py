from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.domain.analysis_engine import AnalysisEngine
from app.domain.entities import Candle, Timeframe
from app.domain.entities.pipeline_decision import PipelineDecisionStatus, SkippedRulesetReason
from app.domain.entities.strategy_rules import (
    StrategyRuleCategory,
    StrategyRuleCondition,
    StrategyRuleOperator,
    StrategyRuleSet,
    StrategyRuleSeverity,
    StrategyRuleSpec,
)
from app.domain.strategy_decision_composer import StrategyDecisionComposer
from app.domain.strategy_ruleset_registry import (
    BUILTIN_STRATEGY_RULESET_FIXTURES,
    StrategyRuleSetRegistry,
)
from app.domain.value_objects import CurrencyPair

PAIR = CurrencyPair(value="EURUSD")
BASE_TIME = datetime(2026, 7, 20, 8, 0, tzinfo=UTC)


def _candle(index: int) -> Candle:
    step = timedelta(minutes=15)
    open_time = BASE_TIME + (index * step)
    open_price = Decimal("1.1000") + (Decimal("0.0001") * Decimal(index))
    close_price = open_price + Decimal("0.0001")
    return Candle(
        provider="decision-composition-test",
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


def _snapshot(candle_count: int):
    candles = [_candle(index) for index in range(candle_count)]
    window_end = BASE_TIME + timedelta(minutes=15 * candle_count)
    return AnalysisEngine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=BASE_TIME,
        window_end=window_end,
        as_of=window_end,
        candles=candles,
        economic_events=[],
        moving_average_windows=(3,),
    )


def test_compose_all_builtin_rulesets_ready_for_review() -> None:
    snapshot = _snapshot(3)

    report = StrategyDecisionComposer().compose(snapshot, BASE_TIME)

    assert report.evaluated_ruleset_count == len(BUILTIN_STRATEGY_RULESET_FIXTURES)
    assert report.skipped_rulesets == ()
    assert report.status == PipelineDecisionStatus.READY_FOR_REVIEW
    assert report.is_actionable is False


def test_compose_reports_not_ready_when_required_rule_fails() -> None:
    empty_snapshot = _snapshot(0)

    report = StrategyDecisionComposer().compose(empty_snapshot, BASE_TIME)

    assert report.status in (PipelineDecisionStatus.BLOCKED, PipelineDecisionStatus.NOT_READY)


def test_compose_reports_blocked_for_blocking_severity_failure() -> None:
    empty_snapshot = _snapshot(0)
    blocking_ruleset = StrategyRuleSet(
        ruleset_version="test-v1",
        strategy_version="test-v1",
        name="blocking severity test",
        created_at=BASE_TIME,
        rules=(
            StrategyRuleSpec(
                rule_id="market_context.snapshot_ready",
                category=StrategyRuleCategory.MARKET_CONTEXT,
                severity=StrategyRuleSeverity.BLOCKING,
                condition=StrategyRuleCondition(
                    field_ref="market_context.snapshot_ready",
                    operator=StrategyRuleOperator.EXISTS,
                ),
                description="blocking severity fixture",
                enabled=False,
            ),
        ),
        enabled=False,
    )
    registry = StrategyRuleSetRegistry(fixtures={"custom.blocking": blocking_ruleset})

    report = StrategyDecisionComposer(registry=registry).compose(empty_snapshot, BASE_TIME)

    assert report.status == PipelineDecisionStatus.BLOCKED
    assert report.blocked_ruleset_count == 1


def test_compose_skips_invalid_rulesets_instead_of_evaluating_them() -> None:
    snapshot = _snapshot(3)
    invalid_ruleset = StrategyRuleSet(
        ruleset_version="test-v1",
        strategy_version="test-v1",
        name="invalid fixture",
        created_at=BASE_TIME,
        rules=(
            StrategyRuleSpec(
                rule_id="data_quality.closed_candles_available",
                category=StrategyRuleCategory.DATA_QUALITY,
                severity=StrategyRuleSeverity.REQUIRED,
                condition=StrategyRuleCondition(
                    field_ref="data_quality.closed_candles_available",
                    operator=StrategyRuleOperator.EXISTS,
                ),
                description="enabled rule makes this ruleset structurally invalid",
                enabled=True,
            ),
        ),
        enabled=False,
    )
    registry = StrategyRuleSetRegistry(fixtures={"custom.invalid": invalid_ruleset})

    report = StrategyDecisionComposer(registry=registry).compose(snapshot, BASE_TIME)

    assert report.evaluated_ruleset_count == 0
    assert len(report.skipped_rulesets) == 1
    assert report.skipped_rulesets[0].registry_key == "custom.invalid"
    assert report.skipped_rulesets[0].reason == SkippedRulesetReason.INVALID_VALIDATION
    assert report.status == PipelineDecisionStatus.READY_FOR_REVIEW


def test_compose_is_deterministic_for_identical_inputs() -> None:
    snapshot = _snapshot(3)
    composer = StrategyDecisionComposer()

    first = composer.compose(snapshot, BASE_TIME)
    second = composer.compose(snapshot, BASE_TIME)

    assert first.deterministic_json() == second.deterministic_json()
    assert first.fingerprint_sha256() == second.fingerprint_sha256()
