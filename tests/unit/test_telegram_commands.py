from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.core.config import Settings
from app.domain.entities import Candle, Timeframe
from app.domain.value_objects import CurrencyPair
from app.services.analysis_service import AnalysisService
from app.telegram import commands
from app.telegram.commands import scan_now_command, snapshot_command, start_scan_command
from app.telegram.formatter import TelegramFormatter
from tests.fakes import FakeUnitOfWorkFactory

PAIR = CurrencyPair(value="EURUSD")
BASE_TIME = datetime(2026, 7, 13, 9, 0, tzinfo=UTC)


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
            "analysis_service": AnalysisService(factory),
            "formatter": TelegramFormatter(),
        }
    )


def _candle(index: int) -> Candle:
    open_time = BASE_TIME + timedelta(minutes=15 * index)
    open_price = Decimal("1.1000") + (Decimal("0.0005") * Decimal(index))
    close_price = open_price + Decimal("0.0002")
    return Candle(
        provider="telegram-test",
        pair=PAIR,
        timeframe=Timeframe.M15,
        open_time=open_time,
        close_time=open_time + timedelta(minutes=15),
        open=open_price,
        high=close_price + Decimal("0.0003"),
        low=open_price - Decimal("0.0003"),
        close=close_price,
        volume=Decimal("100"),
        is_closed=True,
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


@pytest.mark.asyncio
async def test_snapshot_command_returns_readiness_report(monkeypatch: pytest.MonkeyPatch) -> None:
    factory = FakeUnitOfWorkFactory(candles=[_candle(index) for index in range(12)])
    context = _context(factory)
    update = FakeUpdate(user_id=1, chat_id=2, text="/snapshot EURUSD M15")
    monkeypatch.setattr(commands, "utc_now", lambda: BASE_TIME + timedelta(hours=3))

    await snapshot_command(update, context)

    assert len(update.effective_message.replies) == 1
    reply = update.effective_message.replies[0]
    assert reply.startswith("📊 ")
    assert "Отчёт готовности EURUSD M15" in reply
    assert "Статус: готово" in reply
    assert "Свечей использовано: 12 из 12" in reply
    forbidden_terms = (
        "LONG",
        "SHORT",
        "buy",
        "sell",
        "рекомендую",
        "войти",
        "шортить",
    )
    assert not any(term in reply for term in forbidden_terms)


@pytest.mark.asyncio
async def test_snapshot_command_rejects_invalid_arguments() -> None:
    factory = FakeUnitOfWorkFactory()
    context = _context(factory)
    update = FakeUpdate(user_id=1, chat_id=2, text="/snapshot EURUSD M5")

    await snapshot_command(update, context)

    assert update.effective_message.replies == [
        "❌ Формат команды: /snapshot EURUSD M15. Поддерживаются M15 и H1."
    ]
