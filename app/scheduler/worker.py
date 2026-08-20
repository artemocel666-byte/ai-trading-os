import asyncio
import logging
import signal

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncEngine

from app.adapters.factories import (
    ProviderClients,
    create_economic_calendar_provider,
    create_market_data_provider,
    create_provider_clients,
)
from app.adapters.fred_rates import FredInterestRateAdapter
from app.core.config import Settings, get_settings
from app.core.exceptions import ConfigurationInvalidError
from app.core.logging import configure_logging
from app.domain.currency_universe import universe_pairs
from app.domain.entities import (
    CalendarIngestionConfig,
    ForwardOutcomeConfig,
    MarketDataIngestionConfig,
    SnapshotScheduleItem,
    Timeframe,
)
from app.domain.value_objects import CurrencyPair
from app.persistence.database import create_engine, create_session_factory
from app.persistence.database_health import SqlAlchemyDatabaseHealth
from app.persistence.session import build_uow_factory
from app.scheduler.jobs import register_jobs, update_worker_heartbeat_job
from app.services.data_freshness_service import DataFreshnessService
from app.services.economic_calendar_ingestion_service import EconomicCalendarIngestionService
from app.services.forward_outcome_service import ForwardOutcomeService
from app.services.health_service import HealthService
from app.services.interest_rate_ingestion_service import InterestRateIngestionService
from app.services.market_data_ingestion_service import MarketDataIngestionService
from app.services.system_state_service import SystemStateService

DEFAULT_INGESTION_PAIR = "EURUSD"

logger = logging.getLogger(__name__)


async def run_worker() -> None:
    settings = get_settings()
    configure_logging("worker", settings.log_level)
    engine: AsyncEngine = create_engine(settings.database_dsn())
    session_factory = create_session_factory(engine)
    uow_factory = build_uow_factory(session_factory)
    system_state_service = SystemStateService(uow_factory)
    health_service = HealthService(
        settings=settings,
        database_health=SqlAlchemyDatabaseHealth(engine),
        system_state_service=system_state_service,
    )

    market_data_wanted = settings.market_data_enabled and settings.market_data_ingestion_enabled
    calendar_wanted = settings.calendar_enabled and settings.calendar_ingestion_enabled

    provider_clients: ProviderClients | None = None
    ingestion_service: MarketDataIngestionService | None = None
    calendar_ingestion_service: EconomicCalendarIngestionService | None = None
    if market_data_wanted or calendar_wanted:
        provider_clients = create_provider_clients(settings)
    if market_data_wanted and provider_clients is not None:
        ingestion_service = MarketDataIngestionService(
            config=_build_ingestion_config(settings),
            provider=create_market_data_provider(
                settings,
                client=provider_clients.market_data,
            ),
            uow_factory=uow_factory,
            system_state_service=system_state_service,
        )
        logger.info("market_data_ingestion_enabled")
    if calendar_wanted and provider_clients is not None:
        calendar_ingestion_service = EconomicCalendarIngestionService(
            config=_build_calendar_ingestion_config(settings),
            provider=create_economic_calendar_provider(
                settings,
                client=provider_clients.economic_calendar,
            ),
            uow_factory=uow_factory,
            system_state_service=system_state_service,
        )
        logger.info("calendar_ingestion_enabled")

    universe_ingestion_service: MarketDataIngestionService | None = None
    freshness_service: DataFreshnessService | None = None
    universe_instruments: tuple[str, ...] = ()
    if (
        settings.market_data_enabled
        and settings.daily_universe_ingestion_enabled
        and provider_clients is not None
    ):
        universe_instruments = tuple(pair.value for pair in universe_pairs())
        universe_ingestion_service = MarketDataIngestionService(
            config=_build_universe_ingestion_config(settings),
            provider=create_market_data_provider(
                settings,
                client=provider_clients.market_data,
            ),
            uow_factory=uow_factory,
            system_state_service=system_state_service,
        )
        freshness_service = DataFreshnessService(
            uow_factory=uow_factory,
            system_state_service=system_state_service,
            tolerance_bars=settings.data_freshness_tolerance_bars,
        )
        logger.info(
            "daily_universe_ingestion_enabled",
            extra={"pairs": len(universe_instruments)},
        )

    interest_rate_service: InterestRateIngestionService | None = None
    if settings.interest_rate_ingestion_enabled:
        # Rates stand on their own rather than behind `market_data_enabled`: FRED needs no key and
        # is a different kind of observation with its own source, which is why
        # `REAL_MARKET_DATA_PROVIDERS` never learned about them.
        if provider_clients is None:
            provider_clients = create_provider_clients(settings)
        if provider_clients.interest_rates is None:
            raise ConfigurationInvalidError("Для загрузки ставок требуется HTTP-клиент.")
        interest_rate_service = InterestRateIngestionService(
            adapter=FredInterestRateAdapter(client=provider_clients.interest_rates),
            uow_factory=uow_factory,
        )
        logger.info("interest_rate_ingestion_enabled")

    forward_outcome_service: ForwardOutcomeService | None = None
    if settings.forward_outcome_recording_enabled:
        # No provider client: the ledger reads stored candles only, and never fetches. If ingestion
        # is off it simply finds nothing, which is the honest failure mode.
        forward_outcome_service = ForwardOutcomeService(
            config=_build_forward_outcome_config(settings),
            uow_factory=uow_factory,
            system_state_service=system_state_service,
        )
        logger.info("forward_outcome_recording_enabled")

    scheduler = AsyncIOScheduler(timezone=settings.app_timezone)
    register_jobs(
        scheduler,
        system_state_service=system_state_service,
        health_service=health_service,
        market_data_ingestion_service=ingestion_service,
        market_data_ingestion_interval_minutes=settings.market_data_ingestion_interval_minutes,
        daily_universe_ingestion_service=universe_ingestion_service,
        data_freshness_service=freshness_service,
        daily_universe_instruments=universe_instruments,
        daily_universe_hour_utc=settings.daily_universe_ingestion_hour_utc,
        interest_rate_ingestion_service=interest_rate_service,
        interest_rate_hour_utc=settings.interest_rate_ingestion_hour_utc,
        calendar_ingestion_service=calendar_ingestion_service,
        calendar_ingestion_interval_minutes=settings.calendar_ingestion_interval_minutes,
        forward_outcome_service=forward_outcome_service,
        forward_outcome_record_interval_minutes=(settings.forward_outcome_record_interval_minutes),
        forward_outcome_resolve_interval_minutes=(
            settings.forward_outcome_resolve_interval_minutes
        ),
    )

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    try:
        logger.info("worker_starting")
        await update_worker_heartbeat_job(system_state_service)
        scheduler.start()
        logger.info("worker_started")
        await stop_event.wait()
    finally:
        logger.info("worker_stopping")
        scheduler.shutdown(wait=False)
        if provider_clients is not None:
            await provider_clients.aclose()
        await engine.dispose()
        logger.info("worker_stopped")


def _build_ingestion_config(settings: Settings) -> MarketDataIngestionConfig:
    pair = CurrencyPair(value=DEFAULT_INGESTION_PAIR)
    lookback = settings.market_data_ingestion_lookback_candles
    return MarketDataIngestionConfig(
        enabled=True,
        interval_minutes=settings.market_data_ingestion_interval_minutes,
        lookback_candles=lookback,
        items=(
            SnapshotScheduleItem(
                pair=pair,
                timeframe=Timeframe.M15,
                lookback_candle_count=lookback,
            ),
            SnapshotScheduleItem(
                pair=pair,
                timeframe=Timeframe.H1,
                lookback_candle_count=lookback,
            ),
        ),
    )


def _build_universe_ingestion_config(settings: Settings) -> MarketDataIngestionConfig:
    """Daily bars for every pair the universe implies, on one item each.

    **All forty-five are asked for, not the forty-four that worked once.** Whether a provider quotes
    a given pair is an observation rather than something we know, and freezing the list to what was
    seen in August 2026 would bake one afternoon's result into a permanent assumption — the thing
    deriving the universe from a currency set exists to prevent. A pair the provider still refuses
    costs one failed item, and `run_tick` isolates it so the other forty-four finish.
    """
    lookback = settings.daily_universe_lookback_candles
    return MarketDataIngestionConfig(
        enabled=True,
        interval_minutes=settings.market_data_ingestion_interval_minutes,
        lookback_candles=lookback,
        items=tuple(
            SnapshotScheduleItem(
                pair=pair,
                timeframe=Timeframe.D1,
                lookback_candle_count=lookback,
            )
            for pair in universe_pairs()
        ),
    )


def _build_forward_outcome_config(settings: Settings) -> ForwardOutcomeConfig:
    """The same two series the worker already ingests.

    Deliberately not a wider list. The ledger can only record windows the database actually holds,
    and pointing it at a pair nobody ingests would fill it with incomplete windows that say more
    about ingestion than about the market.
    """
    pair = CurrencyPair(value=DEFAULT_INGESTION_PAIR)
    window_candles = settings.forward_outcome_window_candles
    return ForwardOutcomeConfig(
        enabled=True,
        record_interval_minutes=settings.forward_outcome_record_interval_minutes,
        resolve_interval_minutes=settings.forward_outcome_resolve_interval_minutes,
        window_candles=window_candles,
        horizon_candles=settings.forward_outcome_horizon_candles,
        resolve_batch_size=settings.forward_outcome_resolve_batch_size,
        items=(
            SnapshotScheduleItem(
                pair=pair,
                timeframe=Timeframe.M15,
                lookback_candle_count=window_candles,
            ),
            SnapshotScheduleItem(
                pair=pair,
                timeframe=Timeframe.H1,
                lookback_candle_count=window_candles,
            ),
        ),
    )


def _build_calendar_ingestion_config(settings: Settings) -> CalendarIngestionConfig:
    pair = CurrencyPair(value=DEFAULT_INGESTION_PAIR)
    return CalendarIngestionConfig(
        enabled=True,
        interval_minutes=settings.calendar_ingestion_interval_minutes,
        lookback_hours=settings.calendar_ingestion_lookback_hours,
        horizon_hours=settings.calendar_ingestion_horizon_hours,
        currencies=(pair.base_currency, pair.quote_currency),
    )


def main() -> None:
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
