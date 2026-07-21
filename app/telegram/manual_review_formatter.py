from app.domain.entities.manual_review import ManualReviewReport


def format_manual_review_body(report: ManualReviewReport) -> str:
    return (
        "READ-ONLY ручная проверка.\n"
        f"Статус: {report.status.value}.\n"
        f"Разделов: {len(report.sections)}.\n"
        f"Замечаний: {len(report.issues)}.\n"
        f"Источник: {report.source_fingerprint[:12]}.\n"
        "NO TRADING SIGNAL.\n"
        "NON-ACTIONABLE.\n"
        "Торговых указаний нет."
    )
