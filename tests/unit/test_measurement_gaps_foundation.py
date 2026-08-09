"""Three measurement gaps the full project review of 2026-08-07 found.

None of them was a crash or a failing test. Each was a number that quietly meant something other
than what it was read as, which is the harder kind to notice and the kind this file now pins down.
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.domain.analysis_engine import AnalysisEngine
from app.domain.entities import Candle, Timeframe
from app.domain.entities.calibration import RuleBehaviour, RuleOutcomeTally
from app.domain.entities.strategy_rules import StrategyRuleSeverity
from app.domain.strategy_field_resolver import resolve_field
from app.domain.value_objects import CurrencyPair

PAIR = CurrencyPair(value="EURUSD")
BASE_TIME = datetime(2026, 8, 5, 8, 0, tzinfo=UTC)
STEP = timedelta(minutes=15)


def _snapshot(closes: list[Decimal]):
    candles = []
    previous = closes[0]
    for index, close in enumerate(closes):
        candles.append(
            Candle(
                provider="measurement-gap-test",
                pair=PAIR,
                timeframe=Timeframe.M15,
                open_time=BASE_TIME + (index * STEP),
                close_time=BASE_TIME + ((index + 1) * STEP),
                open=previous,
                high=max(previous, close) + Decimal("0.00020"),
                low=min(previous, close) - Decimal("0.00020"),
                close=close,
                volume=Decimal("100"),
                is_closed=True,
            )
        )
        previous = close
    as_of = BASE_TIME + (len(closes) * STEP)
    return AnalysisEngine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=BASE_TIME,
        window_end=as_of,
        as_of=as_of,
        candles=candles,
        economic_events=[],
        moving_average_windows=(3,),
    )


def _climb() -> list[Decimal]:
    return [Decimal("1.10000") + (Decimal("0.00050") * (index + 1)) for index in range(12)]


def _fall() -> list[Decimal]:
    return [Decimal("1.10600") - (Decimal("0.00050") * (index + 1)) for index in range(12)]


def test_a_steady_climb_reports_no_drawdown_at_all() -> None:
    """The defect, stated as a passing observation about the old field.

    Nothing here is broken — the drawdown is genuinely zero. The problem is that a warning rule read
    it as "this window was calm", which is only true for one side of a hypothetical position.
    """
    climbing = _snapshot(_climb())

    assert resolve_field("market_context.max_close_drawdown_atr", climbing) == Decimal("0")


def test_the_symmetric_field_sees_the_climb_the_drawdown_missed() -> None:
    climbing = _snapshot(_climb())

    excursion = resolve_field("market_context.max_close_excursion_atr", climbing)

    assert isinstance(excursion, Decimal)
    assert excursion > Decimal("0")


def test_a_climb_and_its_mirror_report_almost_the_same_excursion() -> None:
    """Direction-neutrality is the point, so it is asserted rather than assumed.

    Almost, and not exactly: the fall is divided by its running peak while the rise is divided by
    its running trough, and the whole thing is then normalised by the average true range as a
    fraction of a *different* latest close. Both are ratios of price rather than logs, so a mirrored
    move lands about one percent apart. Small enough to ignore at these prices, and stated here so
    nobody later reads the asymmetry as a bug.
    """
    climbing = resolve_field("market_context.max_close_excursion_atr", _snapshot(_climb()))
    falling = resolve_field("market_context.max_close_excursion_atr", _snapshot(_fall()))

    assert isinstance(climbing, Decimal)
    assert isinstance(falling, Decimal)
    assert abs(climbing - falling) / climbing < Decimal("0.02")


def test_the_excursion_is_never_smaller_than_the_drawdown() -> None:
    """It takes the larger of the two sides, so it can only ever be at least the decline."""
    for closes in (_climb(), _fall()):
        snapshot = _snapshot(closes)
        drawdown = resolve_field("market_context.max_close_drawdown_atr", snapshot)
        excursion = resolve_field("market_context.max_close_excursion_atr", snapshot)
        assert isinstance(drawdown, Decimal)
        assert isinstance(excursion, Decimal)
        assert excursion >= drawdown


def _tally(*, passed: int, failed: int, unavailable: int) -> RuleOutcomeTally:
    return RuleOutcomeTally(
        rule_id="event_context.minutes_since_latest_event",
        field_ref="event_context.minutes_since_latest_event",
        severity=StrategyRuleSeverity.WARNING,
        passed_count=passed,
        failed_count=failed,
        unavailable_count=unavailable,
    )


def test_a_rule_evaluated_on_almost_nothing_is_not_called_often_firing() -> None:
    """The real numbers from the 2026-08-01 replay: 60 passed, 8 failed, 17 010 unavailable.

    The old verdict divided 8 by 68 and announced OFTEN_FIRES over a 0.4% sample.
    """
    tally = _tally(passed=60, failed=8, unavailable=17_010)

    assert tally.failing_share is not None
    assert tally.failing_share > Decimal("0.10")
    assert tally.behaviour == RuleBehaviour.RARELY_OBSERVED


def test_a_rule_evaluated_everywhere_still_reports_its_firing_rate() -> None:
    tally = _tally(passed=9_000, failed=1_500, unavailable=0)

    assert tally.behaviour == RuleBehaviour.OFTEN_FIRES


def test_availability_is_judged_before_the_firing_rate() -> None:
    """A rule can be both rarely observed and never firing; the sample size is the first problem."""
    tally = _tally(passed=20, failed=0, unavailable=10_000)

    assert tally.observed_share is not None
    assert tally.observed_share < Decimal("0.05")
    assert tally.behaviour == RuleBehaviour.RARELY_OBSERVED


def test_a_rarely_observed_rule_counts_as_a_finding() -> None:
    """`dead_rules` is what makes the replay exit non-zero, so this must reach it."""
    from app.domain.entities.calibration import RuleCalibrationReport

    report = RuleCalibrationReport(
        pair=PAIR,
        timeframe=Timeframe.M15,
        replay_start=BASE_TIME,
        replay_end=BASE_TIME + timedelta(days=1),
        window_count=17_078,
        window_candles=12,
        step_candles=1,
        tallies=(_tally(passed=60, failed=8, unavailable=17_010),),
    )

    assert [tally.rule_id for tally in report.dead_rules] == [
        "event_context.minutes_since_latest_event"
    ]
