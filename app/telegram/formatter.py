import re

from app.core.enums import MessageType
from app.core.exceptions import MessageFormatInvalidError, RussianTextInvalidError
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
