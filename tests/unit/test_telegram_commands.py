import pytest

from app.core.config import Settings
from app.services.analysis_service import AnalysisService
from app.telegram.commands import scan_now_command, start_scan_command
from app.telegram.formatter import TelegramFormatter
from tests.fakes import FakeUnitOfWorkFactory


class FakeUser:
    def __init__(self, user_id: int) -> None:
        self.id = user_id


class FakeChat:
    def __init__(self, chat_id: int) -> None:
        self.id = chat_id


class FakeMessage:
    def __init__(self, text: str) -> None:
        self.text = text
        self.replies: list[str] = []

    async def reply_text(self, text: str) -> None:
        self.replies.append(text)


class FakeUpdate:
    def __init__(self, *, user_id: int, chat_id: int, text: str) -> None:
        self.effective_user = FakeUser(user_id)
        self.effective_chat = FakeChat(chat_id)
        self.effective_message = FakeMessage(text)


class FakeApplication:
    def __init__(self, bot_data: dict[str, object]) -> None:
        self.bot_data = bot_data


class FakeContext:
    def __init__(self, bot_data: dict[str, object]) -> None:
        self.application = FakeApplication(bot_data)


def _context(factory: FakeUnitOfWorkFactory) -> FakeContext:
    settings = Settings(
        _env_file=None,
        telegram_enabled=True,
        telegram_bot_token="token",
        telegram_allowed_user_id=1,
        telegram_allowed_chat_id=2,
    )
    return FakeContext(
        {
            "settings": settings,
            "system_state_service": __import__(
                "app.services.system_state_service",
                fromlist=["SystemStateService"],
            ).SystemStateService(factory),
            "analysis_service": AnalysisService(),
            "formatter": TelegramFormatter(),
        }
    )


@pytest.mark.asyncio
async def test_unauthorized_user_cannot_change_scan_state() -> None:
    factory = FakeUnitOfWorkFactory()
    context = _context(factory)
    update = FakeUpdate(user_id=99, chat_id=2, text="/start_scan")

    await start_scan_command(update, context)

    assert "scan_enabled" not in factory.state
    assert update.effective_message.replies == ["❌ Доступ запрещён."]


@pytest.mark.asyncio
async def test_scan_now_command_reports_not_implemented_without_fabrication() -> None:
    factory = FakeUnitOfWorkFactory()
    context = _context(factory)
    update = FakeUpdate(user_id=1, chat_id=2, text="/scan_now")

    await scan_now_command(update, context)

    assert len(update.effective_message.replies) == 1
    assert "Аналитический движок не реализован" in update.effective_message.replies[0]
    assert "LONG" not in update.effective_message.replies[0]
    assert "SHORT" not in update.effective_message.replies[0]
