"""The slice that gave a warning consequences, and moved the closed-market check where it matters.

Before this, `time_filter.utc_weekday` failed on 28.08% of six months of windows and changed
nothing: `warning_failure_count` was computed by the evaluator and never passed to the status
calculation. The project knew its data was 28% weekend filler, said so in every replay, and built
three phases on top of it.
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.core import constants
from app.domain.analysis_engine import AnalysisEngine
from app.domain.entities import Candle, Timeframe
from app.domain.entities.pipeline_decision import (
    REVIEWABLE_PIPELINE_STATUSES,
    PipelineDecisionStatus,
)
from app.domain.entities.rule_evaluation import RuleEvaluationStatus, RuleSetEvaluationStatus
from app.domain.market_calendar import is_market_open
from app.domain.strategy_decision_composer import StrategyDecisionComposer
from app.domain.strategy_field_resolver import resolve_field
from app.domain.value_objects import CurrencyPair

PAIR = CurrencyPair(value="EURUSD")
STEP = timedelta(minutes=15)
# A Wednesday and the Saturday that follows it. The window ends three hours after it starts, so the
# weekend window is entirely inside a shut market rather than straddling the close.
TRADING_DAY = datetime(2026, 8, 5, 8, 0, tzinfo=UTC)
CLOSED_DAY = datetime(2026, 8, 8, 8, 0, tzinfo=UTC)


def _snapshot(base_time: datetime, *, candle_count: int = 12):
    candles = [
        Candle(
            provider="market-open-test",
            pair=PAIR,
            timeframe=Timeframe.M15,
            open_time=base_time + (index * STEP),
            close_time=base_time + ((index + 1) * STEP),
            open=Decimal("1.10000") + (Decimal("0.00013") * index),
            high=Decimal("1.10030") + (Decimal("0.00013") * index),
            low=Decimal("1.09970") + (Decimal("0.00013") * index),
            close=Decimal("1.10000") + (Decimal("0.00013") * (index + 1)),
            volume=Decimal("100"),
            is_closed=True,
        )
        for index in range(candle_count)
    ]
    as_of = base_time + (candle_count * STEP)
    return AnalysisEngine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=base_time,
        window_end=as_of,
        as_of=as_of,
        candles=candles,
        economic_events=[],
        moving_average_windows=(3,),
    )


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_9a5_market_data_provenance_foundation"


@pytest.mark.parametrize(
    ("moment", "expected"),
    [
        (datetime(2026, 8, 3, 12, 0, tzinfo=UTC), True),  # Monday
        (datetime(2026, 8, 7, 20, 0, tzinfo=UTC), True),  # Friday
        (datetime(2026, 8, 8, 12, 0, tzinfo=UTC), False),  # Saturday
        (datetime(2026, 8, 9, 22, 0, tzinfo=UTC), False),  # Sunday, including the real reopen
    ],
)
def test_market_calendar_covers_the_whole_weekend(moment: datetime, expected: bool) -> None:
    """Deliberately blunt: the genuine Sunday-evening reopen is excluded along with the filler."""
    assert is_market_open(moment) is expected


def test_the_closed_market_field_is_observed_rather_than_unavailable() -> None:
    """The Phase 7D-2 lesson: a resolver returning None makes its rule UNAVAILABLE, not failed.

    The moment is always known, so "the market was shut" is a real observation. Returning None here
    would restore exactly the silence this slice exists to remove.
    """
    assert resolve_field("data_quality.market_open", _snapshot(TRADING_DAY)) is True
    assert resolve_field("data_quality.market_open", _snapshot(CLOSED_DAY)) is False


def test_a_weekend_window_is_not_ready_instead_of_ready_for_review() -> None:
    snapshot = _snapshot(CLOSED_DAY)

    decision = StrategyDecisionComposer().compose(snapshot, snapshot.window.as_of)

    assert decision.status == PipelineDecisionStatus.NOT_READY
    assert decision.status not in REVIEWABLE_PIPELINE_STATUSES
    failed = {
        result.rule_id
        for report in decision.ruleset_reports
        for result in report.results
        if result.status == RuleEvaluationStatus.FAILED
    }
    assert "data_quality.market_open" in failed


def test_a_trading_window_still_passes_the_gate() -> None:
    snapshot = _snapshot(TRADING_DAY)

    decision = StrategyDecisionComposer().compose(snapshot, snapshot.window.as_of)

    assert decision.status in REVIEWABLE_PIPELINE_STATUSES


def test_a_failing_warning_now_reaches_the_headline() -> None:
    """The defect in one assertion: a warning used to fail while the verdict said all was well."""
    snapshot = _snapshot(TRADING_DAY, candle_count=12)

    decision = StrategyDecisionComposer().compose(snapshot, snapshot.window.as_of)

    warned = [
        report
        for report in decision.ruleset_reports
        if report.status == RuleSetEvaluationStatus.READY_WITH_WARNINGS
    ]
    if not warned:
        pytest.skip("this fixture happens to fail no warning, so it cannot exercise the headline")
    assert decision.status == PipelineDecisionStatus.READY_WITH_WARNINGS
    assert decision.warned_ruleset_count == len(warned)


def test_an_unavailable_warning_is_silence_and_not_a_finding() -> None:
    """Otherwise every window in the project would be warned forever.

    `event_context.minutes_since_latest_event` is unavailable in 99.6% of windows because the
    calendar holds no real events. If "could not check" counted as a warning, the new status would
    be permanently on and would carry no information.
    """
    snapshot = _snapshot(TRADING_DAY)

    decision = StrategyDecisionComposer().compose(snapshot, snapshot.window.as_of)
    event_report = next(
        report for report in decision.ruleset_reports if "event" in report.ruleset_name.lower()
    )

    assert event_report.unavailable_count > 0
    assert event_report.warning_failure_count == 0
    assert event_report.status == RuleSetEvaluationStatus.READY_FOR_REVIEW


def test_a_mandatory_rule_still_fails_closed_when_it_cannot_be_checked() -> None:
    """The asymmetry is deliberate, and only warnings get the benefit of the doubt."""
    thin = _snapshot(TRADING_DAY, candle_count=2)

    decision = StrategyDecisionComposer().compose(thin, thin.window.as_of)

    assert decision.status not in REVIEWABLE_PIPELINE_STATUSES
