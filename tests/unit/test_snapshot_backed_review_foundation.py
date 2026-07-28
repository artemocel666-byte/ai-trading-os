from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.domain.analysis_engine import AnalysisEngine
from app.domain.entities import Candle, Timeframe
from app.domain.entities.manual_review import ManualReviewReport
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
    assert "Reviewed rule-set reports: 3" in joined


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
    """Without this the reply looks identical whether nine real rules ran or three placeholders."""
    result = build_snapshot_backed_review(_snapshot(12), BASE_TIME)

    body = format_snapshot_review_body(result, PAIR, Timeframe.M15)

    assert "Правила: пройдено 9 из 9" in body
    assert "качество данных: 4 из 4" in body
    assert "рыночный контекст: 3 из 3" in body
    assert "временной фильтр: 2 из 2" in body
    assert "свечей 12 из 12" in body


def test_formatter_makes_a_degraded_window_visibly_different() -> None:
    healthy = format_snapshot_review_body(
        build_snapshot_backed_review(_snapshot(12), BASE_TIME), PAIR, Timeframe.M15
    )
    degraded = format_snapshot_review_body(
        build_snapshot_backed_review(_snapshot(3), BASE_TIME), PAIR, Timeframe.M15
    )

    assert healthy != degraded
    assert "Правила: пройдено 9 из 9" in healthy
    assert "Правила: пройдено 9 из 9" not in degraded
    assert "не пройдено: " in degraded
    assert "data_quality.used_candle_count" in degraded
