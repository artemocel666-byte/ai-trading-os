from decimal import Decimal
from enum import StrEnum

from app.domain.entities.explanation import ExplanationOutcome
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

    used_candles = snapshot.input_audit.used_candle_count
    expected_candles = (
        snapshot.feature_snapshot.candle_summary.expected_candle_count
        if snapshot.feature_snapshot is not None
        else 0
    )

    # Phase 10-2 removed two lines a person read as a verdict: the aggregate count of rules passed,
    # and the overall ruleset status. Phase 9C-2 measured these rules and found they separate
    # nothing, and two of them barely separate anything at all. An aggregate is the exact shape that
    # invites "mostly favourable" — a reading the project has measured to be empty. What remains is
    # per-ruleset and carries the null in the same message, so the count cannot be read apart from
    # what it was measured to be worth.
    #
    # The removed wording is deliberately not quoted here: a safety test scans this file for it, and
    # a comment reproducing the strings would keep them alive in exactly the place they were cut.
    lines = [
        "READ-ONLY проверка по снапшоту.",
        f"Пара/таймфрейм: {pair.value} {timeframe.value}.",
        f"Готовность данных: {review.status.value}.",
        "",
        f"Данные: свечей {used_candles} из {expected_candles}, "
        f"полнота {_percent(resolve_field('data_quality.completeness_ratio', snapshot))}, "
        f"возраст {_minutes(resolve_field('data_quality.latest_candle_age_minutes', snapshot))}.",
        "Условия правил, справочно:",
    ]
    lines.extend(_ruleset_line(report) for report in decision.ruleset_reports)
    lines.append(
        "Эти правила измерены в фазе 9C-2: они не разделяют исходы. "
        "Число выполненных условий ничего не предсказывает."
    )
    lines.extend(
        [
            f"Замеры: волатильность "
            f"{_decimal(resolve_field('market_context.volatility_ratio', snapshot))}, "
            f"просадка "
            f"{_percent(resolve_field('market_context.max_close_drawdown', snapshot), '0.01')} "
            f"({_decimal(resolve_field('market_context.max_close_drawdown_atr', snapshot))} ATR), "
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


class ExplanationUnavailableReason(StrEnum):
    """Why no explanation is attached. Each maps to one honest Russian line."""

    DELIVERY_DISABLED = "DELIVERY_DISABLED"
    PROVIDER_DISABLED = "PROVIDER_DISABLED"
    PROVIDER_FAILED = "PROVIDER_FAILED"
    TIMED_OUT = "TIMED_OUT"
    REJECTED = "REJECTED"


_REASON_LINES_RU = {
    ExplanationUnavailableReason.DELIVERY_DISABLED: (
        "Пояснение недоступно: слой пояснений выключен настройками."
    ),
    ExplanationUnavailableReason.PROVIDER_DISABLED: (
        "Пояснение недоступно: провайдер выключен настройками."
    ),
    ExplanationUnavailableReason.PROVIDER_FAILED: ("Пояснение недоступно: провайдер не ответил."),
    ExplanationUnavailableReason.TIMED_OUT: (
        "Пояснение недоступно: ответ не пришёл за отведённое время."
    ),
    ExplanationUnavailableReason.REJECTED: ("Пояснение недоступно: ответ не прошёл проверку."),
}


def format_explanation_section(
    outcome: ExplanationOutcome | None,
    *,
    reason: ExplanationUnavailableReason | None = None,
) -> str:
    """The appendix under a deterministic report.

    An accepted explanation is shown with an explicit note that it changes nothing above it. A
    refusal is stated with its codes rather than hidden: knowing that a model answered and was
    turned down is exactly the thing worth telling the reader.
    """
    if outcome is not None and outcome.accepted and outcome.text:
        return "\n".join(
            [
                "",
                "Пояснение (ИИ, проверено):",
                outcome.text,
                "Пояснение не меняет решение выше.",
            ]
        )
    if outcome is not None and not outcome.accepted:
        codes = ", ".join(code.value for code in outcome.validation.issue_codes) or "нет кода"
        return "\n".join(
            [
                "",
                _REASON_LINES_RU[ExplanationUnavailableReason.REJECTED],
                f"Причины: {codes}.",
            ]
        )
    resolved = reason or ExplanationUnavailableReason.PROVIDER_FAILED
    return "\n".join(["", _REASON_LINES_RU[resolved]])
