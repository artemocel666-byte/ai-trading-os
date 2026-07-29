from decimal import Decimal

from app.domain.entities.manual_review import ManualReviewReport
from app.domain.entities.market_data import Timeframe
from app.domain.entities.rule_evaluation import RuleEvaluationStatus, RuleSetEvaluationReport
from app.domain.snapshot_review import SnapshotBackedReview
from app.domain.strategy_field_resolver import resolve_field
from app.domain.value_objects import CurrencyPair

_RULESET_TITLES_RU = {
    "Foundation data quality": "качество данных",
    "Foundation market context": "рыночный контекст",
    "Foundation event context": "события",
    "Foundation time filter": "временной фильтр",
}

_UNAVAILABLE_RU = "нет данных"


def _percent(value: object, places: str = "1") -> str:
    if not isinstance(value, Decimal):
        return _UNAVAILABLE_RU
    return f"{(value * Decimal('100')).quantize(Decimal(places))}%"


def _decimal(value: object, places: str = "0.01") -> str:
    if not isinstance(value, Decimal):
        return _UNAVAILABLE_RU
    return str(value.quantize(Decimal(places)))


def _minutes(value: object) -> str:
    if not isinstance(value, Decimal):
        return _UNAVAILABLE_RU
    return f"{value.quantize(Decimal('1'))} мин"


def _ruleset_line(report: RuleSetEvaluationReport) -> str:
    passed = sum(1 for r in report.results if r.status == RuleEvaluationStatus.PASSED)
    title = _RULESET_TITLES_RU.get(report.ruleset_name, report.ruleset_name)
    line = f"- {title}: {passed} из {len(report.results)}"
    failures = tuple(r for r in report.results if r.status != RuleEvaluationStatus.PASSED)
    if not failures:
        return line
    detail = ", ".join(
        f"{r.rule_id}"
        + (f" ({_UNAVAILABLE_RU})" if r.status == RuleEvaluationStatus.UNAVAILABLE else "")
        for r in failures
    )
    return f"{line}; не пройдено: {detail}"


def format_snapshot_review_body(
    result: SnapshotBackedReview,
    pair: CurrencyPair,
    timeframe: Timeframe,
) -> str:
    review: ManualReviewReport = result.review
    decision = result.decision
    snapshot = result.snapshot

    total_rules = sum(len(report.results) for report in decision.ruleset_reports)
    passed_rules = sum(
        1
        for report in decision.ruleset_reports
        for rule_result in report.results
        if rule_result.status == RuleEvaluationStatus.PASSED
    )
    used_candles = snapshot.input_audit.used_candle_count
    expected_candles = (
        snapshot.feature_snapshot.candle_summary.expected_candle_count
        if snapshot.feature_snapshot is not None
        else 0
    )

    lines = [
        "READ-ONLY проверка по снапшоту.",
        f"Пара/таймфрейм: {pair.value} {timeframe.value}.",
        f"Статус: {review.status.value}. Итог правил: {decision.status.value}.",
        "",
        f"Данные: свечей {used_candles} из {expected_candles}, "
        f"полнота {_percent(resolve_field('data_quality.completeness_ratio', snapshot))}, "
        f"возраст {_minutes(resolve_field('data_quality.latest_candle_age_minutes', snapshot))}.",
        f"Правила: пройдено {passed_rules} из {total_rules}.",
    ]
    lines.extend(_ruleset_line(report) for report in decision.ruleset_reports)
    lines.extend(
        [
            f"Замеры: волатильность "
            f"{_decimal(resolve_field('market_context.volatility_ratio', snapshot))}, "
            f"просадка "
            f"{_percent(resolve_field('market_context.max_close_drawdown', snapshot), '0.01')}, "
            f"сессия {resolve_field('time_filter.session_name', snapshot) or _UNAVAILABLE_RU}.",
            "",
            f"Источник: {review.source_fingerprint[:12]} (отчёт решения Phase 4G).",
            "Рыночный снапшот: используется.",
            "Анализ пары/таймфрейма: выполнен.",
            "NO TRADING SIGNAL.",
            "NON-ACTIONABLE.",
            "Торговых указаний нет.",
        ]
    )
    return "\n".join(lines)
