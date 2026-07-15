import re

from app.core.enums import MessageType
from app.core.exceptions import MessageFormatInvalidError, RussianTextInvalidError
from app.domain.entities.analysis import AnalysisReadinessStatus, AnalysisSnapshot
from app.domain.entities.readiness import SnapshotDigest
from app.services.readiness_digest_service import readiness_digest_text
from app.telegram.emoji_policy import EMOJI_BY_MESSAGE_TYPE, validate_telegram_emoji

CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")  # noqa: RUF001


def validate_russian_foundation_text(text: str) -> None:
    body = text.strip()
    if not body:
        raise RussianTextInvalidError("Текст сообщения не должен быть пустым.")
    if not CYRILLIC_RE.search(body):
        raise RussianTextInvalidError("Сообщение выглядит как английский-only текст.")


class TelegramFormatter:
    def format(self, message_type: MessageType, body_ru: str) -> str:
        validate_russian_foundation_text(body_ru)
        if any(emoji in body_ru for emoji in EMOJI_BY_MESSAGE_TYPE.values()):
            raise MessageFormatInvalidError("Сервисы не должны вставлять эмодзи в тело сообщения.")
        text = f"{EMOJI_BY_MESSAGE_TYPE[message_type]} {body_ru.strip()}"
        validate_telegram_emoji(message_type, text)
        return text

    def format_analysis_readiness_body(self, snapshot: AnalysisSnapshot) -> str:
        status_ru = {
            AnalysisReadinessStatus.READY: "готово",
            AnalysisReadinessStatus.INCOMPLETE: "неполные данные",
            AnalysisReadinessStatus.BLOCKED: "заблокировано",
        }[snapshot.readiness_status]
        audit = snapshot.input_audit
        future_data_status = (
            "пройдена"
            if audit.no_candles_after_as_of_used and audit.no_events_after_as_of_used
            else "требует проверки"
        )
        issue_summary = _issue_summary(snapshot)
        return (
            f"Отчёт готовности {snapshot.window.pair.value} {snapshot.window.timeframe.value}.\n"
            f"Статус: {status_ru}.\n"
            f"Свечей использовано: {audit.used_candle_count} из {audit.input_candle_count}.\n"
            f"Событий календаря: {audit.used_event_count} из {audit.input_event_count}.\n"
            f"Проверка будущих данных: {future_data_status}.\n"
            f"Проблемы: {issue_summary}.\n"
            f"Снимок: {snapshot.metadata.snapshot_id[:12]}.\n"
            "Только отчёт готовности; торговых действий нет."
        )

    def format_snapshot_digest_body(self, digest: SnapshotDigest) -> str:
        return readiness_digest_text(digest)


def _issue_summary(snapshot: AnalysisSnapshot) -> str:
    if not snapshot.input_audit.excluded_issue_counts:
        return "не обнаружены"
    return "; ".join(
        f"{item.source}/{item.code.value}: {item.count}"
        for item in snapshot.input_audit.excluded_issue_counts[:5]
    )
