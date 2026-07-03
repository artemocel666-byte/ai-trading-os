from dataclasses import dataclass

from app.core.config import Settings


@dataclass(frozen=True)
class TelegramIdentity:
    user_id: int | None
    chat_id: int | None


def is_authorized(settings: Settings, identity: TelegramIdentity) -> bool:
    return (
        identity.user_id is not None
        and identity.chat_id is not None
        and identity.user_id == settings.telegram_allowed_user_id
        and identity.chat_id == settings.telegram_allowed_chat_id
    )
