from app.domain.entities.manual_review import ManualReviewReport
from app.domain.entities.market_data import Timeframe
from app.domain.value_objects import CurrencyPair


def format_snapshot_review_body(
    report: ManualReviewReport,
    pair: CurrencyPair,
    timeframe: Timeframe,
) -> str:
    return (
        "READ-ONLY проверка по снапшоту.\n"
        f"Пара/таймфрейм: {pair.value} {timeframe.value}.\n"
        f"Статус: {report.status.value}.\n"
        f"Разделов: {len(report.sections)}.\n"
        f"Замечаний: {len(report.issues)}.\n"
        f"Источник: {report.source_fingerprint[:12]}.\n"
        "Источник данных: отчёт решения Phase 4G.\n"
        "Рыночный снапшот: используется.\n"
        "Анализ пары/таймфрейма: выполнен.\n"
        "NO TRADING SIGNAL.\n"
        "NON-ACTIONABLE.\n"
        "Торговых указаний нет."
    )
