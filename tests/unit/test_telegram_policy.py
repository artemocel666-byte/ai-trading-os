import pytest

from app.core.config import Settings
from app.core.enums import MessageType
from app.core.exceptions import MessageFormatInvalidError, RussianTextInvalidError
from app.telegram.authorization import TelegramIdentity, is_authorized
from app.telegram.emoji_policy import EMOJI_BY_MESSAGE_TYPE, validate_telegram_emoji
from app.telegram.formatter import TelegramFormatter, validate_russian_foundation_text


def test_formatter_adds_exactly_one_leading_semantic_emoji() -> None:
    formatter = TelegramFormatter()
    text = formatter.format(MessageType.SYSTEM_STATUS, "Система работает в foundation-фазе.")

    assert text.startswith(EMOJI_BY_MESSAGE_TYPE[MessageType.SYSTEM_STATUS])
    validate_telegram_emoji(MessageType.SYSTEM_STATUS, text)
    assert sum(text.count(emoji) for emoji in EMOJI_BY_MESSAGE_TYPE.values()) == 1


def test_formatter_rejects_empty_or_english_only_text() -> None:
    with pytest.raises(RussianTextInvalidError):
        validate_russian_foundation_text("")
    with pytest.raises(RussianTextInvalidError):
        validate_russian_foundation_text("System status is available")


def test_formatter_rejects_service_inserted_emoji() -> None:
    formatter = TelegramFormatter()

    with pytest.raises(MessageFormatInvalidError):
        formatter.format(MessageType.REPORT, "Отчёт готов ✅")


def test_emoji_must_match_message_type() -> None:
    with pytest.raises(MessageFormatInvalidError):
        validate_telegram_emoji(MessageType.REJECTED, "✅ Доступ запрещён.")


def test_authorization_requires_user_and_chat_match() -> None:
    settings = Settings(
        _env_file=None,
        telegram_enabled=True,
        telegram_bot_token="token",
        telegram_allowed_user_id=10,
        telegram_allowed_chat_id=20,
    )

    assert is_authorized(settings, TelegramIdentity(user_id=10, chat_id=20))
    assert not is_authorized(settings, TelegramIdentity(user_id=11, chat_id=20))
    assert not is_authorized(settings, TelegramIdentity(user_id=10, chat_id=21))
