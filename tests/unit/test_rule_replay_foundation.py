from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.domain.entities import Candle, Timeframe
from app.domain.entities.analysis import AnalysisSnapshot
from app.domain.entities.calibration import (
    FieldDistribution,
    RuleBehaviour,
    RuleOutcomeTally,
)
from app.domain.entities.features import FeatureIssueCode
from app.domain.entities.rule_evaluation import RuleEvaluationStatus
from app.domain.entities.strategy_rules import StrategyRuleSeverity
from app.domain.rule_calibration import summarize_field
from app.domain.rule_replay import replay_windows
from app.domain.strategy_decision_composer import StrategyDecisionComposer
from app.domain.value_objects import CurrencyPair
from scripts.replay_rules import load_history
from tests.fakes import FakeUnitOfWorkFactory

PAIR = CurrencyPair(value="EURUSD")
STEP = timedelta(minutes=15)
# A Monday inside the London session, so the time-filter rules pass and do not mask the rules
# this file is actually measuring.
SERIES_START = datetime(2026, 3, 2, 8, 0, tzinfo=UTC)


def _candle(
    open_time: datetime,
    *,
    close: Decimal = Decimal("1.1000"),
    half_range: Decimal = Decimal("0.0005"),
) -> Candle:
    return Candle(
        provider="replay-test",
        pair=PAIR,
        timeframe=Timeframe.M15,
        open_time=open_time,
        close_time=open_time + STEP,
        open=close,
        high=close + half_range,
        low=close - half_range,
        close=close,
        volume=Decimal("100"),
        is_closed=True,
    )


def _series(count: int) -> list[Candle]:
    return [_candle(SERIES_START + (index * STEP)) for index in range(count)]


class RecordingComposer(StrategyDecisionComposer):
    """Delegates to the real composer while keeping every snapshot it was handed."""

    def __init__(self) -> None:
        super().__init__()
        self.snapshots: list[AnalysisSnapshot] = []

    def compose(self, snapshot: AnalysisSnapshot, evaluated_at: datetime):  # type: ignore[no-untyped-def]
        self.snapshots.append(snapshot)
        return super().compose(snapshot, evaluated_at)


def _tally(**counts: int) -> RuleOutcomeTally:
    return RuleOutcomeTally(
        rule_id="market_context.volatility_ratio",
        field_ref="market_context.volatility_ratio",
        severity=StrategyRuleSeverity.WARNING,
        **counts,
    )


def test_percentiles_use_nearest_rank_over_the_observed_sample() -> None:
    values = [Decimal(index) for index in range(1, 11)]

    distribution = summarize_field("market_context.volatility_ratio", values)

    assert distribution.observed_count == 10
    assert distribution.minimum == Decimal("1")
    assert distribution.p05 == Decimal("1")
    assert distribution.p25 == Decimal("3")
    assert distribution.median == Decimal("5")
    assert distribution.p75 == Decimal("8")
    assert distribution.p95 == Decimal("10")
    assert distribution.maximum == Decimal("10")


def test_empty_sample_reports_no_percentiles_rather_than_zeroes() -> None:
    distribution = summarize_field("market_context.volatility_ratio", [], unavailable_count=7)

    assert distribution.observed_count == 0
    assert distribution.unavailable_count == 7
    assert distribution.percentiles == (None,) * 7


def test_single_observation_reports_that_value_everywhere() -> None:
    distribution = summarize_field("data_quality.completeness_ratio", [Decimal("0.5")])

    assert distribution.percentiles == (Decimal("0.5"),) * 7


def test_distribution_rejects_percentiles_without_observations() -> None:
    with pytest.raises(ValueError, match="must not report percentiles"):
        FieldDistribution(field_ref="x", observed_count=0, median=Decimal("1"))


def test_behaviour_is_derived_from_the_counts() -> None:
    assert _tally(passed_count=0, failed_count=0).behaviour == RuleBehaviour.NOT_OBSERVED
    assert _tally(passed_count=100, failed_count=0).behaviour == RuleBehaviour.NEVER_FIRES
    assert _tally(passed_count=0, failed_count=100).behaviour == RuleBehaviour.ALWAYS_FIRES
    assert _tally(passed_count=999, failed_count=1).behaviour == RuleBehaviour.RARELY_FIRES
    # Exactly at the boundary the rule still counts as quiet; one window past it does not.
    assert _tally(passed_count=90, failed_count=10).behaviour == RuleBehaviour.RARELY_FIRES
    assert _tally(passed_count=89, failed_count=11).behaviour == RuleBehaviour.OFTEN_FIRES


def test_replay_never_lets_a_candle_close_after_as_of_enter_a_window() -> None:
    """Re-proves the Phase 3D no-future-data invariant on the replay path."""
    composer = RecordingComposer()

    replay_windows(pair=PAIR, timeframe=Timeframe.M15, candles=_series(30), composer=composer)

    assert composer.snapshots
    for snapshot in composer.snapshots:
        assert snapshot.feature_snapshot is not None
        for candle in snapshot.feature_snapshot.candle_summary.used_candle_open_times:
            assert candle + STEP <= snapshot.window.as_of
        assert all(
            issue.code != FeatureIssueCode.CANDLE_AFTER_AS_OF
            for issue in snapshot.feature_snapshot.quality_issues
        )


def test_step_candles_subsamples_the_walk() -> None:
    candles = _series(30)

    every_candle = replay_windows(pair=PAIR, timeframe=Timeframe.M15, candles=candles)
    every_fourth = replay_windows(
        pair=PAIR,
        timeframe=Timeframe.M15,
        candles=candles,
        step_candles=4,
    )

    assert every_candle.window_count == 19
    assert every_fourth.window_count == 5
    assert every_fourth.step_candles == 4


def test_a_volatility_spike_is_reported_by_the_volatility_rule_alone() -> None:
    candles = _series(24)
    spike_index = 20
    candles[spike_index] = _candle(
        candles[spike_index].open_time,
        half_range=Decimal("0.0050"),
    )

    report = replay_windows(pair=PAIR, timeframe=Timeframe.M15, candles=candles)

    by_rule = {tally.rule_id: tally for tally in report.tallies}
    assert by_rule["market_context.volatility_ratio"].failed_count > 0
    assert by_rule["market_context.volatility_ratio"].behaviour in (
        RuleBehaviour.RARELY_FIRES,
        RuleBehaviour.OFTEN_FIRES,
    )
    # The spike is a range event, not a data or timing event; nothing else may report it.
    for rule_id in (
        "data_quality.used_candle_count",
        "data_quality.completeness_ratio",
        "data_quality.market_data_complete",
        "data_quality.market_open",
        "time_filter.session_name_allowed",
    ):
        assert by_rule[rule_id].failed_count == 0


def test_every_rule_reports_one_outcome_per_window() -> None:
    report = replay_windows(pair=PAIR, timeframe=Timeframe.M15, candles=_series(24))

    assert report.window_count == 13
    assert len(report.tallies) == 11
    for tally in report.tallies:
        observed = tally.passed_count + tally.failed_count + tally.unavailable_count
        assert observed == report.window_count


def test_without_stored_events_the_event_rules_cannot_be_calibrated() -> None:
    """Documents the known gap: no calendar history means no event calibration."""
    report = replay_windows(pair=PAIR, timeframe=Timeframe.M15, candles=_series(24))

    by_rule = {tally.rule_id: tally for tally in report.tallies}
    # Zero high-impact releases is a real measurement, so the count rule still resolves...
    assert by_rule["event_context.high_impact_event_count"].failed_count == 0
    # ...but elapsed time since a release cannot be measured when there is no release at all.
    assert (
        by_rule["event_context.minutes_since_latest_event"].unavailable_count == report.window_count
    )
    assert (
        by_rule["event_context.minutes_since_latest_event"].behaviour == RuleBehaviour.NOT_OBSERVED
    )
    assert by_rule["event_context.minutes_since_latest_event"] in report.dead_rules


def test_distributions_cover_numeric_fields_only() -> None:
    report = replay_windows(pair=PAIR, timeframe=Timeframe.M15, candles=_series(24))

    field_refs = {distribution.field_ref for distribution in report.distributions}
    assert "market_context.volatility_ratio" in field_refs
    assert "data_quality.completeness_ratio" in field_refs
    # Booleans and session names have no percentiles; their rule tallies carry the story.
    assert "data_quality.market_data_complete" not in field_refs
    assert "time_filter.session_name" not in field_refs


def test_replay_rejects_nonsense_inputs() -> None:
    with pytest.raises(ValueError, match="window_candles"):
        replay_windows(
            pair=PAIR,
            timeframe=Timeframe.M15,
            candles=_series(20),
            window_candles=0,
        )
    with pytest.raises(ValueError, match="step_candles"):
        replay_windows(pair=PAIR, timeframe=Timeframe.M15, candles=_series(20), step_candles=0)
    with pytest.raises(ValueError, match="not enough stored candles"):
        replay_windows(pair=PAIR, timeframe=Timeframe.M15, candles=_series(5))


@pytest.mark.asyncio
async def test_loading_history_reads_once_and_writes_nothing() -> None:
    candles = _series(30)
    factory = FakeUnitOfWorkFactory(candles=list(candles))

    loaded_candles, loaded_events = await load_history(
        factory,
        pair=PAIR,
        timeframe=Timeframe.M15,
        start_at=SERIES_START,
        end_at=SERIES_START + (40 * STEP),
        window_candles=12,
    )
    report = replay_windows(pair=PAIR, timeframe=Timeframe.M15, candles=loaded_candles)

    assert loaded_events == []
    assert report.window_count > 0
    assert report.is_actionable is False
    # Replay is a measurement, not an ingestion path: storage must be untouched.
    assert len(factory.candles) == len(candles)
    assert len(factory.instances) == 1


@pytest.mark.asyncio
async def test_loading_history_rejects_an_inverted_range() -> None:
    factory = FakeUnitOfWorkFactory(candles=_series(30))

    with pytest.raises(ValueError, match="later than start_at"):
        await load_history(
            factory,
            pair=PAIR,
            timeframe=Timeframe.M15,
            start_at=SERIES_START,
            end_at=SERIES_START,
            window_candles=12,
        )


def test_replay_uses_the_same_evaluation_path_as_review() -> None:
    """A lookalike evaluator would measure something other than what /review reports."""
    composer = RecordingComposer()

    report = replay_windows(
        pair=PAIR,
        timeframe=Timeframe.M15,
        candles=_series(20),
        composer=composer,
    )

    assert len(composer.snapshots) == report.window_count
    decision = StrategyDecisionComposer().compose(
        composer.snapshots[-1],
        composer.snapshots[-1].window.as_of,
    )
    assert decision.evaluated_ruleset_count == 4
    assert all(
        result.status
        in (
            RuleEvaluationStatus.PASSED,
            RuleEvaluationStatus.FAILED,
            RuleEvaluationStatus.UNAVAILABLE,
        )
        for ruleset in decision.ruleset_reports
        for result in ruleset.results
    )
