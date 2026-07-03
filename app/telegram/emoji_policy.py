from app.core.enums import MessageType
from app.core.exceptions import MessageFormatInvalidError

EMOJI_BY_MESSAGE_TYPE: dict[MessageType, str] = {
    MessageType.LONG_SIGNAL: "📈",
    MessageType.SHORT_SIGNAL: "📉",
    MessageType.NO_TRADE: "⏸️",
    MessageType.APPROVED: "✅",
    MessageType.REJECTED: "❌",
    MessageType.CANCELLED: "🚫",
    MessageType.WARNING: "⚠️",
    MessageType.REPORT: "📊",
    MessageType.EDUCATION: "🎓",
    MessageType.CRITICAL_ERROR: "🛑",
    MessageType.DATA_UNAVAILABLE: "📡",
    MessageType.SYSTEM_STATUS: "⚙️",
}


def validate_telegram_emoji(message_type: MessageType, text: str) -> None:
    expected = EMOJI_BY_MESSAGE_TYPE[message_type]
    if not text.startswith(expected):
        raise MessageFormatInvalidError("Сообщение должно начинаться с корректного эмодзи.")  # noqa: RUF001
    matches = [emoji for emoji in EMOJI_BY_MESSAGE_TYPE.values() if text.startswith(emoji)]
    if matches != [expected]:
        raise MessageFormatInvalidError("Сообщение содержит некорректный начальный эмодзи.")
    body = text[len(expected) :].strip()
    if not body:
        raise MessageFormatInvalidError("Тело сообщения не должно быть пустым.")
    configured_emoji_count = sum(text.count(emoji) for emoji in EMOJI_BY_MESSAGE_TYPE.values())
    if configured_emoji_count != 1:
        raise MessageFormatInvalidError("Сообщение должно содержать ровно один разрешённый эмодзи.")
    if any(emoji in body for emoji in EMOJI_BY_MESSAGE_TYPE.values()):
        raise MessageFormatInvalidError("Тело сообщения не должно содержать эмодзи.")
