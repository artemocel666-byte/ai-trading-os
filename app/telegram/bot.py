import asyncio
import logging
import signal

from telegram.ext import ApplicationBuilder

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory
from app.services.analysis_service import AnalysisService
from app.services.system_state_service import SystemStateService
from app.telegram.commands import add_handlers
from app.telegram.formatter import TelegramFormatter

logger = logging.getLogger(__name__)


async def run_disabled_mode() -> None:
    settings = get_settings()
    configure_logging("bot", settings.log_level)
    logger.info("telegram_disabled_mode_started")
    await asyncio.Event().wait()


async def run_enabled_bot() -> None:
    settings = get_settings()
    configure_logging("bot", settings.log_level)
    token = settings.telegram_bot_token
    if token is None:
        raise RuntimeError("telegram token is required when Telegram is enabled")

    engine = create_engine(settings.database_dsn())
    session_factory = create_session_factory(engine)
    uow_factory = build_uow_factory(session_factory)
    application = ApplicationBuilder().token(token.get_secret_value()).build()
    application.bot_data["settings"] = settings
    application.bot_data["system_state_service"] = SystemStateService(uow_factory)
    application.bot_data["analysis_service"] = AnalysisService()
    application.bot_data["formatter"] = TelegramFormatter()
    add_handlers(application)

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    try:
        logger.info("telegram_bot_starting")
        await application.initialize()
        await application.start()
        if application.updater is None:
            raise RuntimeError("telegram updater is unavailable")
        await application.updater.start_polling()
        logger.info("telegram_bot_started")
        await stop_event.wait()
    finally:
        logger.info("telegram_bot_stopping")
        if application.updater is not None:
            await application.updater.stop()
        await application.stop()
        await application.shutdown()
        await engine.dispose()
        logger.info("telegram_bot_stopped")


def main() -> None:
    settings = get_settings()
    if settings.telegram_enabled:
        asyncio.run(run_enabled_bot())
    else:
        asyncio.run(run_disabled_mode())


if __name__ == "__main__":
    main()
