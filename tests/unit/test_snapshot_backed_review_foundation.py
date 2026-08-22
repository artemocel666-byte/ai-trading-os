from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.domain.analysis_engine import AnalysisEngine
from app.domain.entities import Candle, Timeframe
from app.domain.entities.manual_review import ManualReviewReport
from app.domain.entities.rule_evaluation import RuleEvaluationStatus
from app.domain.snapshot_review import (
    build_snapshot_backed_manual_review_report,
    build_snapshot_backed_review,
)
from app.domain.value_objects import CurrencyPair
from app.telegram.snapshot_review_formatter import format_snapshot_review_body

PAIR = CurrencyPair(value="EURUSD")
BASE_TIME = datetime(2026, 7, 20, 9, 0, tzinfo=UTC)


def _candle(index: int) -> Candle:
    step = timedelta(minutes=15)
    open_time = BASE_TIME + (index * step)
    open_price = Decimal("1.1000") + (Decimal("0.0001") * Decimal(index))
    close_price = open_price + Decimal("0.0001")
    return Candle(
        provider="snapshot-review-test",
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


def test_snapshot_backed_review_is_read_only_and_non_actionable() -> None:
    report = build_snapshot_backed_manual_review_report(_snapshot(3), BASE_TIME)

    assert isinstance(report, ManualReviewReport)
    assert report.is_actionable is False
    assert report.enabled_for_runtime is False


def test_snapshot_backed_review_reflects_real_pipeline_decision() -> None:
    report = build_snapshot_backed_manual_review_report(_snapshot(3), BASE_TIME)

    pipeline_section = next(
        section for section in report.sections if section.code.value == "PIPELINE_STATE"
    )
    joined = " ".join(pipeline_section.details)
    # The 4G composer evaluated the three built-in rulesets against the real snapshot.
    assert "Reviewed rule-set reports: 4" in joined


def test_snapshot_backed_review_is_deterministic() -> None:
    snapshot = _snapshot(3)

    first = build_snapshot_backed_manual_review_report(snapshot, BASE_TIME)
    second = build_snapshot_backed_manual_review_report(snapshot, BASE_TIME)

    assert first.deterministic_json() == second.deterministic_json()
    assert first.fingerprint_sha256() == second.fingerprint_sha256()


def test_snapshot_review_formatter_states_snapshot_is_used_and_stays_neutral() -> None:
    result = build_snapshot_backed_review(_snapshot(12), BASE_TIME)

    body = format_snapshot_review_body(result, PAIR, Timeframe.M15)

    assert "EURUSD M15" in body
    assert "Рыночный снапшот: используется" in body
    assert "NO TRADING SIGNAL" in body
    assert "NON-ACTIONABLE" in body
    forbidden_terms = (
        "LONG",
        "SHORT",
        "entry",
        "stop loss",
        "take profit",
        "position size",
        "setup score",
        "confidence score",
        "broker",
    )
    assert not any(term in body for term in forbidden_terms)


def test_formatter_reports_the_actual_rule_outcomes() -> None:
    """Without this the reply looks identical whether real rules ran or placeholders did."""
    result = build_snapshot_backed_review(_snapshot(12), BASE_TIME)

    body = format_snapshot_review_body(result, PAIR, Timeframe.M15)

    # This window holds no scheduled event, so "time since the latest event" has nothing to
    # measure and is reported UNAVAILABLE rather than passed: 1 of 2 in the event ruleset.
    #
    # Phase 10-2 removed the aggregate "пройдено N из M" and the overall rule status. An aggregate
    # is the shape that reads as a verdict, and 9C-2 measured these rules to separate nothing. The
    # per-ruleset lines survive because they are facts about which conditions held, and they now
    # travel with the null in the same message.
    assert "Правила: пройдено" not in body
    assert "Итог правил" not in body
    assert "9C-2" in body
    assert "не разделяют исходы" in body
    assert "качество данных: 5 из 5" in body
    assert "рыночный контекст: 3 из 3" in body
    assert "события: 1 из 2" in body
    assert "временной фильтр: 1 из 1" in body
    assert "свечей 12 из 12" in body


def test_quiet_calendar_is_reported_as_unavailable_not_as_a_failure() -> None:
    result = build_snapshot_backed_review(_snapshot(12), BASE_TIME)

    event_report = next(
        report
        for report in result.decision.ruleset_reports
        if "event" in report.ruleset_name.lower()
    )
    by_rule = {item.rule_id: item.status for item in event_report.results}

    assert by_rule["event_context.high_impact_event_count"] == RuleEvaluationStatus.PASSED
    assert by_rule["event_context.minutes_since_latest_event"] == RuleEvaluationStatus.UNAVAILABLE


def test_formatter_makes_a_degraded_window_visibly_different() -> None:
    healthy = format_snapshot_review_body(
        build_snapshot_backed_review(_snapshot(12), BASE_TIME), PAIR, Timeframe.M15
    )
    degraded = format_snapshot_review_body(
        build_snapshot_backed_review(_snapshot(3), BASE_TIME), PAIR, Timeframe.M15
    )

    assert healthy != degraded
    # The difference must still be visible without an aggregate score to carry it.
    assert "качество данных: 5 из 5" in healthy
    assert "качество данных: 5 из 5" not in degraded
    assert "не пройдено: " in degraded
    assert "data_quality.used_candle_count" in degraded
