from datetime import datetime, timedelta
from typing import Any, cast

from pydantic import ValidationError
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.core.config import Settings
from app.core.enums import MessageType
from app.core.exceptions import NotImplementedFeatureError
from app.core.time import normalize_to_utc, utc_now
from app.domain.entities import SnapshotScheduleItem, Timeframe
from app.domain.manual_review_report_builder import build_local_manual_review_report
from app.domain.value_objects import CurrencyPair
from app.services.analysis_service import AnalysisService
from app.services.readiness_digest_service import ReadinessDigestService
from app.services.system_state_service import SystemStateService
from app.telegram.authorization import TelegramIdentity, is_authorized
from app.telegram.formatter import TelegramFormatter
from app.telegram.manual_review_formatter import format_manual_review_body

DEFAULT_SNAPSHOT_CANDLE_COUNT = 12
DEFAULT_DIGEST_ITEMS = (
    SnapshotScheduleItem(
        pair=CurrencyPair(value="EURUSD"),
        timeframe=Timeframe.M15,
        lookback_candle_count=DEFAULT_SNAPSHOT_CANDLE_COUNT,
    ),
    SnapshotScheduleItem(
        pair=CurrencyPair(value="EURUSD"),
        timeframe=Timeframe.H1,
        lookback_candle_count=DEFAULT_SNAPSHOT_CANDLE_COUNT,
    ),
)


def _identity(update: Update) -> TelegramIdentity:
    user = update.effective_user
    chat = update.effective_chat
    return TelegramIdentity(
        user_id=user.id if user is not None else None,
        chat_id=chat.id if chat is not None else None,
    )


def _settings(context: ContextTypes.DEFAULT_TYPE) -> Settings:
    return cast(Settings, context.application.bot_data["settings"])


def _system_state_service(context: ContextTypes.DEFAULT_TYPE) -> SystemStateService:
    return cast(SystemStateService, context.application.bot_data["system_state_service"])


def _analysis_service(context: ContextTypes.DEFAULT_TYPE) -> AnalysisService:
    return cast(AnalysisService, context.application.bot_data["analysis_service"])


def _readiness_digest_service(context: ContextTypes.DEFAULT_TYPE) -> ReadinessDigestService:
    return cast(ReadinessDigestService, context.application.bot_data["readiness_digest_service"])


def _formatter(context: ContextTypes.DEFAULT_TYPE) -> TelegramFormatter:
    return cast(TelegramFormatter, context.application.bot_data["formatter"])


async def _reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    message_type: MessageType,
    body_ru: str,
) -> None:
    if update.effective_message is None:
        return
    await update.effective_message.reply_text(_formatter(context).format(message_type, body_ru))


async def _ensure_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    identity = _identity(update)
    command = (
        update.effective_message.text
        if update.effective_message and update.effective_message.text
        else "unknown"
    )
    if is_authorized(_settings(context), identity):
        return True
    await _system_state_service(context).record_unauthorized_telegram_access(
        user_id=identity.user_id,
        chat_id=identity.chat_id,
        command=command.split()[0],
    )
    await _reply(update, context, MessageType.REJECTED, "Доступ запрещён.")
    return False


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    await _reply(
        update,
        context,
        MessageType.EDUCATION,
        "AI Trading OS находится в foundation-фазе и режиме разработки бумажной аналитики.",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    await _reply(
        update,
        context,
        MessageType.EDUCATION,
        (
            "Доступные команды: /start, /help, /status, /start_scan, "
            "/stop_scan, /scan_now, /snapshot, /digest, /review."
        ),
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    status = await _system_state_service(context).get_full_status()
    scan_text = "включено" if status["scan_enabled"] else "выключено"
    heartbeat = status["worker_heartbeat"] or "ещё не получен"
    await _reply(
        update,
        context,
        MessageType.SYSTEM_STATUS,
        (
            "Статус системы: foundation-фаза. "
            f"Сканирование: {scan_text}. "
            f"Пульс worker: {heartbeat}. "
            "Реальная торговля отключена."
        ),
    )


async def start_scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    await _system_state_service(context).enable_scanning(actor="telegram")
    await _reply(
        update,
        context,
        MessageType.APPROVED,
        "Состояние сканирования включено, но аналитическая стратегия ещё не подключена.",
    )


async def stop_scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    await _system_state_service(context).disable_scanning(actor="telegram")
    await _reply(update, context, MessageType.CANCELLED, "Состояние сканирования выключено.")


async def scan_now_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    try:
        await _analysis_service(context).scan_now()
    except NotImplementedFeatureError:
        await _reply(
            update,
            context,
            MessageType.DATA_UNAVAILABLE,
            "Аналитический движок не реализован в foundation-фазе. Результат не создан.",
        )


async def snapshot_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    try:
        pair, timeframe = _parse_snapshot_command(update)
    except (ValueError, ValidationError):
        await _reply(
            update,
            context,
            MessageType.REJECTED,
            "Формат команды: /snapshot EURUSD M15. Поддерживаются M15 и H1.",
        )
        return

    window_start, window_end, as_of = _default_snapshot_window(timeframe)
    try:
        snapshot = await _analysis_service(context).build_snapshot(
            pair=pair,
            timeframe=timeframe,
            window_start=window_start,
            window_end=window_end,
            as_of=as_of,
        )
    except Exception:
        await _reply(
            update,
            context,
            MessageType.DATA_UNAVAILABLE,
            "Отчёт готовности сейчас недоступен. Проверьте базу данных и настройки сервиса.",
        )
        return

    body = _formatter(context).format_analysis_readiness_body(snapshot)
    await _reply(update, context, MessageType.REPORT, body)


async def digest_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    try:
        items = _parse_digest_command(update)
    except (ValueError, ValidationError):
        await _reply(
            update,
            context,
            MessageType.REJECTED,
            "Формат команды: /digest или /digest EURUSD M15. Поддерживаются M15 и H1.",
        )
        return

    try:
        payload = await _readiness_digest_service(context).build_payload(
            items=items,
            as_of=normalize_to_utc(utc_now()),
        )
    except Exception:
        await _reply(
            update,
            context,
            MessageType.DATA_UNAVAILABLE,
            "Дайджест готовности сейчас недоступен. Проверьте базу данных и настройки сервиса.",
        )
        return

    await _reply(update, context, MessageType.REPORT, payload.text)


async def review_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    try:
        report = build_local_manual_review_report(normalize_to_utc(utc_now()))
    except Exception:
        await _reply(
            update,
            context,
            MessageType.DATA_UNAVAILABLE,
            "Отчёт ручной проверки сейчас недоступен.",
        )
        return

    body = format_manual_review_body(report)
    await _reply(update, context, MessageType.REPORT, body)


def _parse_snapshot_command(update: Update) -> tuple[CurrencyPair, Timeframe]:
    text = (
        update.effective_message.text
        if update.effective_message is not None and update.effective_message.text is not None
        else ""
    )
    parts = text.split()
    if len(parts) != 3:
        raise ValueError("snapshot command requires pair and timeframe")
    return CurrencyPair(value=parts[1].upper()), Timeframe(parts[2].upper())


def _parse_digest_command(update: Update) -> tuple[SnapshotScheduleItem, ...]:
    text = (
        update.effective_message.text
        if update.effective_message is not None and update.effective_message.text is not None
        else ""
    )
    parts = text.split()
    if len(parts) == 1:
        return DEFAULT_DIGEST_ITEMS
    if len(parts) != 3:
        raise ValueError("digest command expects no arguments or pair and timeframe")
    return (
        SnapshotScheduleItem(
            pair=CurrencyPair(value=parts[1].upper()),
            timeframe=Timeframe(parts[2].upper()),
            lookback_candle_count=DEFAULT_SNAPSHOT_CANDLE_COUNT,
        ),
    )


def _default_snapshot_window(timeframe: Timeframe) -> tuple[datetime, datetime, datetime]:
    as_of = normalize_to_utc(utc_now())
    if timeframe == Timeframe.M15:
        minute = (as_of.minute // 15) * 15
        window_end = as_of.replace(minute=minute, second=0, microsecond=0)
        step_minutes = 15
    else:
        window_end = as_of.replace(minute=0, second=0, microsecond=0)
        step_minutes = 60
    window_start = window_end - timedelta(minutes=DEFAULT_SNAPSHOT_CANDLE_COUNT * step_minutes)
    return window_start, window_end, window_end


def add_handlers(application: Application[Any, Any, Any, Any, Any, Any]) -> None:
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("start_scan", start_scan_command))
    application.add_handler(CommandHandler("stop_scan", stop_scan_command))
    application.add_handler(CommandHandler("scan_now", scan_now_command))
    application.add_handler(CommandHandler("snapshot", snapshot_command))
    application.add_handler(CommandHandler("digest", digest_command))
    application.add_handler(CommandHandler("review", review_command))
