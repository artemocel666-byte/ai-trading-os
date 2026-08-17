from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.entities.outcome import OutcomeKind, OutcomeStatistics, WindowOutcome
from app.domain.entities.pipeline_decision import PipelineDecisionReport, PipelineDecisionStatus
from app.domain.entities.rule_evaluation import (
    RuleEvaluationResult,
    RuleEvaluationStatus,
    RuleSetEvaluationReport,
    RuleSetEvaluationStatus,
)
from app.domain.entities.rule_value import RuleValueComparison, RuleValueReport
from app.domain.entities.signal_contract import SignalDirection
from app.domain.entities.strategy_rules import StrategyRuleCategory, StrategyRuleSeverity
from app.domain.outcome_measurement import aggregate_outcomes
from app.domain.rule_value import (
    MARKET_FACING_RULE_IDS,
    PLUMBING_RULE_IDS,
    WindowObservation,
    evaluate_rule_value,
)

EVALUATED_AT = datetime(2026, 8, 11, tzinfo=UTC)
SNAPSHOT_ID = "a" * 64
MARKET_RULE = "market_context.volatility_ratio"


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_9d3_interest_rate_ingestion"


def _outcome(kind: OutcomeKind, direction: SignalDirection) -> WindowOutcome:
    resolved = kind not in (OutcomeKind.TIMEOUT, OutcomeKind.NO_DATA)
    return WindowOutcome(
        direction=direction,
        entry_price=Decimal("1.10000"),
        stop_loss=Decimal("1.09800"),
        take_profit=Decimal("1.10300"),
        kind=kind,
        bars_to_resolution=2 if resolved else None,
    )


def _result(rule_id: str, status: RuleEvaluationStatus) -> RuleEvaluationResult:
    return RuleEvaluationResult(
        rule_id=rule_id,
        category=StrategyRuleCategory.MARKET_CONTEXT,
        severity=StrategyRuleSeverity.WARNING,
        field_ref=rule_id,
        status=status,
        resolved_value_present=status != RuleEvaluationStatus.UNAVAILABLE,
    )


def _decision(statuses: dict[str, RuleEvaluationStatus]) -> PipelineDecisionReport:
    """A report carrying exactly the rule verdicts a test cares about.

    Built by hand rather than through the composer: the point here is the partitioning, and a real
    composer run would make the test depend on today's thresholds.
    """
    results = tuple(_result(rule_id, status) for rule_id, status in statuses.items())
    failed = sum(1 for result in results if result.status == RuleEvaluationStatus.FAILED)
    report = RuleSetEvaluationReport(
        ruleset_version="test-v1",
        strategy_version="test",
        ruleset_name="test",
        status=(
            RuleSetEvaluationStatus.READY_WITH_WARNINGS
            if failed
            else RuleSetEvaluationStatus.READY_FOR_REVIEW
        ),
        evaluated_at=EVALUATED_AT,
        source_snapshot_id=SNAPSHOT_ID,
        results=results,
        blocking_failure_count=0,
        required_failure_count=0,
        warning_failure_count=failed,
    )
    return PipelineDecisionReport(
        pipeline_version="test-pipeline",
        project_phase=constants.PROJECT_PHASE,
        status=(
            PipelineDecisionStatus.READY_WITH_WARNINGS
            if failed
            else PipelineDecisionStatus.READY_FOR_REVIEW
        ),
        evaluated_at=EVALUATED_AT,
        source_snapshot_id=SNAPSHOT_ID,
        ruleset_reports=(report,),
        evaluated_ruleset_count=1,
        blocked_ruleset_count=0,
        not_ready_ruleset_count=0,
        warned_ruleset_count=1 if failed else 0,
    )


def _observation(
    *,
    market_rule: RuleEvaluationStatus,
    kind: OutcomeKind,
    plumbing_passes: bool = True,
) -> WindowObservation:
    statuses = dict.fromkeys(
        PLUMBING_RULE_IDS,
        RuleEvaluationStatus.PASSED if plumbing_passes else RuleEvaluationStatus.FAILED,
    )
    statuses[MARKET_RULE] = market_rule
    return WindowObservation(
        decision=_decision(statuses),
        outcomes={direction: _outcome(kind, direction) for direction in SignalDirection},
    )


def _report(observations: list[WindowObservation]) -> RuleValueReport:
    return evaluate_rule_value(
        observations,
        pair="EURUSD",
        timeframe="M15",
        total_window_count=len(observations),
        market_facing_rule_ids=(MARKET_RULE,),
    )


# --- the entity ------------------------------------------------------------------------------


def _statistics(target_first: int, stop_first: int) -> OutcomeStatistics:
    return aggregate_outcomes(
        [_outcome(OutcomeKind.TARGET_FIRST, SignalDirection.LONG)] * target_first
        + [_outcome(OutcomeKind.STOP_FIRST, SignalDirection.LONG)] * stop_first
    )


def test_the_edge_is_computed_from_its_parts() -> None:
    comparison = RuleValueComparison(
        rule_id=MARKET_RULE,
        passed_window_count=5,
        failed_window_count=5,
        passed_statistics=_statistics(6, 4),
        failed_statistics=_statistics(4, 6),
    )

    assert comparison.passed_statistics.target_first_share == Decimal("0.6")
    assert comparison.failed_statistics.target_first_share == Decimal("0.4")
    assert comparison.target_first_edge == Decimal("0.2")
    assert comparison.failure_share == Decimal("0.5")


def test_statistics_must_pool_both_directions_of_every_window() -> None:
    """A partitioning bug must not reach a report and look like a finding."""
    with pytest.raises(ValidationError):
        RuleValueComparison(
            rule_id=MARKET_RULE,
            passed_window_count=5,
            failed_window_count=0,
            passed_statistics=_statistics(3, 2),  # five outcomes, not ten
            failed_statistics=aggregate_outcomes([]),
        )


def test_an_empty_group_leaves_the_edge_unavailable_rather_than_zero() -> None:
    """Zero would read as "no difference"; there is simply nothing to compare."""
    comparison = RuleValueComparison(
        rule_id=MARKET_RULE,
        passed_window_count=5,
        failed_window_count=0,
        passed_statistics=_statistics(6, 4),
        failed_statistics=aggregate_outcomes([]),
    )

    assert comparison.failed_statistics.target_first_share is None
    assert comparison.target_first_edge is None
    assert comparison.failure_share == Decimal("0")


def test_a_report_cannot_claim_more_eligible_windows_than_it_measured() -> None:
    with pytest.raises(ValidationError):
        RuleValueReport(
            pair="EURUSD",
            timeframe="M15",
            total_window_count=3,
            eligible_window_count=4,
            pooled_statistics=aggregate_outcomes([]),
        )


# --- partitioning ----------------------------------------------------------------------------


def test_a_rule_that_separates_outcomes_reports_a_positive_edge() -> None:
    observations = [
        _observation(market_rule=RuleEvaluationStatus.PASSED, kind=OutcomeKind.TARGET_FIRST)
    ] * 6 + [_observation(market_rule=RuleEvaluationStatus.FAILED, kind=OutcomeKind.STOP_FIRST)] * 4

    comparison = _report(observations).comparisons[0]

    assert comparison.passed_window_count == 6
    assert comparison.failed_window_count == 4
    assert comparison.target_first_edge == Decimal("1")


def test_a_rule_that_separates_nothing_reports_no_edge() -> None:
    """The expected result, and the one that would close the question."""
    observations = [
        _observation(market_rule=status, kind=kind)
        for status in (RuleEvaluationStatus.PASSED, RuleEvaluationStatus.FAILED)
        for kind in (OutcomeKind.TARGET_FIRST, OutcomeKind.STOP_FIRST)
    ]

    comparison = _report(observations).comparisons[0]

    assert comparison.target_first_edge == Decimal("0")


def test_windows_whose_plumbing_failed_are_excluded_before_any_comparison() -> None:
    """Otherwise the comparison measures our ingestion and reports it as a finding about rules."""
    good = [
        _observation(market_rule=RuleEvaluationStatus.PASSED, kind=OutcomeKind.TARGET_FIRST)
    ] * 3
    bad = [
        _observation(
            market_rule=RuleEvaluationStatus.PASSED,
            kind=OutcomeKind.STOP_FIRST,
            plumbing_passes=False,
        )
    ] * 7

    report = _report(good + bad)

    assert report.total_window_count == 10
    assert report.eligible_window_count == 3
    assert report.pooled_statistics.target_first_share == Decimal("1")


def test_an_unavailable_rule_counts_on_neither_side() -> None:
    """It said nothing about the window, and an absence must not enter a comparison."""
    observations = [
        _observation(market_rule=RuleEvaluationStatus.PASSED, kind=OutcomeKind.TARGET_FIRST),
        _observation(market_rule=RuleEvaluationStatus.FAILED, kind=OutcomeKind.STOP_FIRST),
        _observation(market_rule=RuleEvaluationStatus.UNAVAILABLE, kind=OutcomeKind.TARGET_FIRST),
    ]

    report = _report(observations)
    comparison = report.comparisons[0]

    assert report.eligible_window_count == 3
    assert comparison.passed_window_count == 1
    assert comparison.failed_window_count == 1


def test_the_market_facing_rules_are_the_three_that_describe_a_market() -> None:
    """Named rather than derived from severity: severity is policy, subject matter is not."""
    assert MARKET_FACING_RULE_IDS == (
        "market_context.volatility_ratio",
        "market_context.max_close_excursion_atr",
        "time_filter.session_name_allowed",
    )
    assert "data_quality.market_open" in PLUMBING_RULE_IDS
    assert "market_context.snapshot_ready" in PLUMBING_RULE_IDS
