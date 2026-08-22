import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.core.config import Settings
from app.core.exceptions import (
    IntegrationDisabledError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)
from app.domain.entities import Candle, Timeframe
from app.domain.entities.explanation import (
    ExplanationIssue,
    ExplanationIssueCode,
    ExplanationOutcome,
    ExplanationValidationReport,
)
from app.domain.value_objects import CurrencyPair
from app.services.analysis_service import AnalysisService
from app.services.readiness_digest_service import ReadinessDigestService
from app.telegram import commands
from app.telegram.commands import (
    digest_command,
    help_command,
    review_command,
    scan_now_command,
    snapshot_command,
    start_scan_command,
)
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


class FakeHandlerApplication:
    def __init__(self) -> None:
        self.handlers: list[FakeCommandHandler] = []

    def add_handler(self, handler: "FakeCommandHandler") -> None:
        self.handlers.append(handler)


class FakeCommandHandler:
    def __init__(self, command: str, callback: object) -> None:
        self.command = command
        self.callback = callback


def _context(
    factory: FakeUnitOfWorkFactory,
    *,
    explanation_provider: object | None = None,
    explanation_delivery_enabled: bool = False,
) -> FakeContext:
    settings = Settings(
        _env_file=None,
        telegram_enabled=True,
        telegram_bot_token="token",
        telegram_allowed_user_id=1,
        telegram_allowed_chat_id=2,
        explanation_delivery_enabled=explanation_delivery_enabled,
        explanation_budget_seconds=0.5,
    )
    analysis_service = AnalysisService(factory)
    return FakeContext(
        {
            "settings": settings,
            "explanation_provider": explanation_provider,
            "system_state_service": __import__(
                "app.services.system_state_service",
                fromlist=["SystemStateService"],
            ).SystemStateService(factory),
            "analysis_service": analysis_service,
            "readiness_digest_service": ReadinessDigestService(analysis_service),
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
    assert "готово" in reply
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


def test_add_handlers_keeps_snapshot_digest_and_registers_review(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    application = FakeHandlerApplication()
    monkeypatch.setattr(commands, "CommandHandler", FakeCommandHandler)

    commands.add_handlers(application)

    registered = {handler.command: handler.callback for handler in application.handlers}
    assert registered["snapshot"] is snapshot_command
    assert registered["digest"] is digest_command
    assert registered["review"] is review_command


@pytest.mark.asyncio
async def test_digest_command_returns_default_readiness_digest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    factory = FakeUnitOfWorkFactory(candles=[_candle(index) for index in range(12)])
    context = _context(factory)
    update = FakeUpdate(user_id=1, chat_id=2, text="/digest")
    monkeypatch.setattr(commands, "utc_now", lambda: BASE_TIME + timedelta(hours=3))

    await digest_command(update, context)

    assert len(update.effective_message.replies) == 1
    reply = update.effective_message.replies[0]
    assert reply.startswith("📊 ")
    assert "Системный отчёт готовности" in reply
    assert "EURUSD M15: READY" in reply
    assert "EURUSD H1: BLOCKED" in reply
    assert "Решений и указаний нет." in reply


@pytest.mark.asyncio
async def test_digest_command_accepts_single_snapshot_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    factory = FakeUnitOfWorkFactory(candles=[_candle(index) for index in range(12)])
    context = _context(factory)
    update = FakeUpdate(user_id=1, chat_id=2, text="/digest EURUSD M15")
    monkeypatch.setattr(commands, "utc_now", lambda: BASE_TIME + timedelta(hours=3))

    await digest_command(update, context)

    assert len(update.effective_message.replies) == 1
    reply = update.effective_message.replies[0]
    assert "EURUSD M15: READY" in reply
    assert "EURUSD H1" not in reply
    assert "Решений и указаний нет." in reply


@pytest.mark.asyncio
async def test_digest_command_rejects_invalid_arguments() -> None:
    factory = FakeUnitOfWorkFactory()
    context = _context(factory)
    update = FakeUpdate(user_id=1, chat_id=2, text="/digest EURUSD M5")

    await digest_command(update, context)

    assert update.effective_message.replies == [
        "❌ Формат команды: /digest или /digest EURUSD M15. Поддерживаются M15 и H1."
    ]


@pytest.mark.asyncio
async def test_review_command_returns_authorized_read_only_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    factory = FakeUnitOfWorkFactory()
    context = _context(factory)
    update = FakeUpdate(user_id=1, chat_id=2, text="/review")
    monkeypatch.setattr(commands, "utc_now", lambda: BASE_TIME)

    await review_command(update, context)

    assert len(update.effective_message.replies) == 1
    reply = update.effective_message.replies[0]
    assert reply.startswith("📊 ")
    assert "READ-ONLY" in reply
    assert "NO TRADING SIGNAL" in reply
    assert "NON-ACTIONABLE" in reply
    assert factory.state == {}
    forbidden_terms = (
        "LONG",
        "SHORT",
        "entry",
        "stop loss",
        "take profit",
        "position size",
        "setup score",
        "confidence score",
        "broker",
        "order",
    )
    assert not any(term in reply for term in forbidden_terms)


@pytest.mark.asyncio
async def test_review_command_blocks_unauthorized_user() -> None:
    factory = FakeUnitOfWorkFactory()
    context = _context(factory)
    update = FakeUpdate(user_id=99, chat_id=2, text="/review")

    await review_command(update, context)

    assert update.effective_message.replies == ["❌ Доступ запрещён."]


@pytest.mark.asyncio
async def test_review_command_with_args_returns_snapshot_backed_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    factory = FakeUnitOfWorkFactory(candles=[_candle(index) for index in range(12)])
    context = _context(factory)
    update = FakeUpdate(user_id=1, chat_id=2, text="/review EURUSD M15")
    monkeypatch.setattr(commands, "utc_now", lambda: BASE_TIME + timedelta(hours=3))

    await review_command(update, context)

    assert len(update.effective_message.replies) == 1
    reply = update.effective_message.replies[0]
    assert reply.startswith("📊 ")
    assert "EURUSD M15" in reply
    assert "Рыночный снапшот: используется" in reply
    assert "NO TRADING SIGNAL" in reply
    forbidden_terms = ("LONG", "SHORT", "buy", "sell", "войти", "шортить")
    assert not any(term in reply for term in forbidden_terms)


@pytest.mark.asyncio
async def test_review_command_with_bad_args_is_rejected() -> None:
    factory = FakeUnitOfWorkFactory()
    context = _context(factory)
    update = FakeUpdate(user_id=1, chat_id=2, text="/review EURUSD M5")

    await review_command(update, context)

    assert update.effective_message.replies == [
        "❌ Формат команды: /review EURUSD M15. Поддерживаются M15 и H1."
    ]


@pytest.mark.asyncio
async def test_help_command_includes_manual_review() -> None:
    factory = FakeUnitOfWorkFactory()
    context = _context(factory)
    update = FakeUpdate(user_id=1, chat_id=2, text="/help")

    await help_command(update, context)

    assert len(update.effective_message.replies) == 1
    assert "/review" in update.effective_message.replies[0]


class FakeExplanationProvider:
    """Answers with a prepared outcome, or raises what a real provider would raise."""

    def __init__(
        self,
        *,
        outcome: object | None = None,
        error: Exception | None = None,
        delay_seconds: float = 0.0,
    ) -> None:
        self._outcome = outcome
        self._error = error
        self._delay_seconds = delay_seconds
        self.calls = 0

    async def explain(self, explanation_input: object) -> str:
        raise NotImplementedError

    async def explain_validated(self, explanation_input: object, checked_at: datetime) -> object:
        self.calls += 1
        if self._delay_seconds:
            await asyncio.sleep(self._delay_seconds)
        if self._error is not None:
            raise self._error
        return self._outcome


def _accepted_outcome(text: str = "Окно данных полное, правила пройдены.") -> ExplanationOutcome:
    return ExplanationOutcome(
        model_name="test-model",
        text=text,
        validation=ExplanationValidationReport(checked_at=BASE_TIME, issues=(), accepted=True),
    )


def _rejected_outcome() -> ExplanationOutcome:
    return ExplanationOutcome(
        model_name="test-model",
        text=None,
        validation=ExplanationValidationReport(
            checked_at=BASE_TIME,
            issues=(
                ExplanationIssue(
                    code=ExplanationIssueCode.ACTIONABLE_TEXT,
                    detail="Текст содержит торговые указания.",
                ),
            ),
            accepted=False,
        ),
    )


def _explain_context(
    provider: object | None,
    *,
    delivery_enabled: bool = True,
) -> tuple[FakeUnitOfWorkFactory, FakeContext]:
    factory = FakeUnitOfWorkFactory(candles=[_candle(index) for index in range(12)])
    context = _context(
        factory,
        explanation_provider=provider,
        explanation_delivery_enabled=delivery_enabled,
    )
    return factory, context


def _assert_deterministic_report_intact(reply: str) -> None:
    """Whatever happened to the model, the report a user was owed is still there."""
    assert reply.startswith("📊 ")
    assert "READ-ONLY проверка по снапшоту." in reply
    assert "EURUSD M15" in reply
    # Phase 10-2: the aggregate score is gone; what proves the real review ran is a per-ruleset
    # line plus the 9C-2 null that must accompany it.
    assert "Правила: пройдено" not in reply
    assert "качество данных" in reply
    assert "9C-2" in reply
    assert "NO TRADING SIGNAL." in reply
    assert "NON-ACTIONABLE." in reply


@pytest.mark.asyncio
async def test_explain_appends_an_accepted_explanation_to_the_full_report(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = FakeExplanationProvider(outcome=_accepted_outcome())
    _factory, context = _explain_context(provider)
    update = FakeUpdate(user_id=1, chat_id=2, text="/explain EURUSD M15")
    monkeypatch.setattr(commands, "utc_now", lambda: BASE_TIME + timedelta(hours=3))

    await commands.explain_command(update, context)

    reply = update.effective_message.replies[0]
    _assert_deterministic_report_intact(reply)
    assert "Пояснение (ИИ, проверено):" in reply
    assert "Окно данных полное, правила пройдены." in reply
    assert "Пояснение не меняет решение выше." in reply
    assert provider.calls == 1
    # The formatter still owns the one and only emoji.
    assert reply.count("📊") == 1


@pytest.mark.asyncio
async def test_explain_reports_a_rejected_answer_without_showing_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = FakeExplanationProvider(outcome=_rejected_outcome())
    _factory, context = _explain_context(provider)
    update = FakeUpdate(user_id=1, chat_id=2, text="/explain EURUSD M15")
    monkeypatch.setattr(commands, "utc_now", lambda: BASE_TIME + timedelta(hours=3))

    await commands.explain_command(update, context)

    reply = update.effective_message.replies[0]
    _assert_deterministic_report_intact(reply)
    assert "Пояснение недоступно: ответ не прошёл проверку." in reply
    assert "ACTIONABLE_TEXT" in reply
    assert "Пояснение (ИИ, проверено):" not in reply


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("error", "expected_line"),
    [
        (IntegrationDisabledError("openai"), "провайдер выключен настройками"),
        (ProviderRateLimitError("openai"), "провайдер не ответил"),
        (ProviderUnavailableError("openai"), "провайдер не ответил"),
    ],
)
async def test_explain_survives_provider_failures(
    error: Exception,
    expected_line: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = FakeExplanationProvider(error=error)
    _factory, context = _explain_context(provider)
    update = FakeUpdate(user_id=1, chat_id=2, text="/explain EURUSD M15")
    monkeypatch.setattr(commands, "utc_now", lambda: BASE_TIME + timedelta(hours=3))

    await commands.explain_command(update, context)

    reply = update.effective_message.replies[0]
    _assert_deterministic_report_intact(reply)
    assert expected_line in reply


@pytest.mark.asyncio
async def test_explain_gives_up_on_a_slow_model_and_still_answers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A Telegram command must not hang on a provider; the budget ends the wait."""
    provider = FakeExplanationProvider(outcome=_accepted_outcome(), delay_seconds=5.0)
    _factory, context = _explain_context(provider)
    update = FakeUpdate(user_id=1, chat_id=2, text="/explain EURUSD M15")
    monkeypatch.setattr(commands, "utc_now", lambda: BASE_TIME + timedelta(hours=3))

    await commands.explain_command(update, context)

    reply = update.effective_message.replies[0]
    _assert_deterministic_report_intact(reply)
    assert "ответ не пришёл за отведённое время" in reply


@pytest.mark.asyncio
async def test_explain_with_the_layer_off_never_calls_the_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = FakeExplanationProvider(outcome=_accepted_outcome())
    _factory, context = _explain_context(provider, delivery_enabled=False)
    update = FakeUpdate(user_id=1, chat_id=2, text="/explain EURUSD M15")
    monkeypatch.setattr(commands, "utc_now", lambda: BASE_TIME + timedelta(hours=3))

    await commands.explain_command(update, context)

    reply = update.effective_message.replies[0]
    _assert_deterministic_report_intact(reply)
    assert "слой пояснений выключен настройками" in reply
    assert provider.calls == 0


@pytest.mark.asyncio
async def test_explain_without_a_provider_says_so(monkeypatch: pytest.MonkeyPatch) -> None:
    _factory, context = _explain_context(None)
    update = FakeUpdate(user_id=1, chat_id=2, text="/explain EURUSD M15")
    monkeypatch.setattr(commands, "utc_now", lambda: BASE_TIME + timedelta(hours=3))

    await commands.explain_command(update, context)

    reply = update.effective_message.replies[0]
    _assert_deterministic_report_intact(reply)
    assert "провайдер выключен настройками" in reply


@pytest.mark.asyncio
async def test_explain_without_arguments_is_rejected() -> None:
    _factory, context = _explain_context(None)
    update = FakeUpdate(user_id=1, chat_id=2, text="/explain")

    await commands.explain_command(update, context)

    assert update.effective_message.replies[0] == (
        "❌ Формат команды: /explain EURUSD M15. Поддерживаются M15 и H1."
    )


@pytest.mark.asyncio
async def test_explain_blocks_unauthorized_user() -> None:
    _factory, context = _explain_context(None)
    update = FakeUpdate(user_id=99, chat_id=2, text="/explain EURUSD M15")

    await commands.explain_command(update, context)

    assert update.effective_message.replies == ["❌ Доступ запрещён."]


@pytest.mark.asyncio
async def test_review_is_unchanged_by_the_explanation_layer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The cheap command stayed cheap: /review neither calls nor mentions a model."""
    provider = FakeExplanationProvider(outcome=_accepted_outcome())
    monkeypatch.setattr(commands, "utc_now", lambda: BASE_TIME + timedelta(hours=3))

    _factory, plain_context = _explain_context(None, delivery_enabled=False)
    plain_update = FakeUpdate(user_id=1, chat_id=2, text="/review EURUSD M15")
    await review_command(plain_update, plain_context)

    _factory2, wired_context = _explain_context(provider, delivery_enabled=True)
    wired_update = FakeUpdate(user_id=1, chat_id=2, text="/review EURUSD M15")
    await review_command(wired_update, wired_context)

    assert plain_update.effective_message.replies == wired_update.effective_message.replies
    assert "Пояснение" not in wired_update.effective_message.replies[0]
    assert provider.calls == 0


def test_add_handlers_registers_explain(monkeypatch: pytest.MonkeyPatch) -> None:
    application = FakeHandlerApplication()
    monkeypatch.setattr(commands, "CommandHandler", FakeCommandHandler)

    commands.add_handlers(application)

    registered = {handler.command: handler.callback for handler in application.handlers}
    assert registered["explain"] is commands.explain_command
