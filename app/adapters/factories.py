from dataclasses import dataclass
from datetime import timedelta

import httpx

from app.adapters.disabled import (
    DisabledEconomicCalendarProvider,
    DisabledExplanationProvider,
    DisabledMarketDataProvider,
)
from app.adapters.fmp_calendar import FMPEconomicCalendarAdapter
from app.adapters.openai_explanations import OpenAIExplanationAdapter, build_openai_timeout
from app.adapters.twelve_data import TwelveDataMarketDataAdapter
from app.core.config import Settings
from app.core.exceptions import ConfigurationInvalidError
from app.domain.interfaces.providers import (
    EconomicCalendarProvider,
    ExplanationProvider,
    MarketDataProvider,
)


def build_provider_timeout(settings: Settings) -> httpx.Timeout:
    return httpx.Timeout(
        connect=settings.provider_connect_timeout_seconds,
        read=settings.provider_read_timeout_seconds,
        write=settings.provider_write_timeout_seconds,
        pool=settings.provider_pool_timeout_seconds,
    )


@dataclass(slots=True)
class ProviderClients:
    market_data: httpx.AsyncClient | None = None
    economic_calendar: httpx.AsyncClient | None = None
    explanation: httpx.AsyncClient | None = None

    async def aclose(self) -> None:
        for client in (self.market_data, self.economic_calendar, self.explanation):
            if client is not None and not client.is_closed:
                await client.aclose()


def create_provider_clients(settings: Settings) -> ProviderClients:
    timeout = build_provider_timeout(settings)
    return ProviderClients(
        market_data=httpx.AsyncClient(timeout=timeout) if settings.market_data_enabled else None,
        economic_calendar=(
            httpx.AsyncClient(timeout=timeout) if settings.calendar_enabled else None
        ),
        explanation=(
            httpx.AsyncClient(timeout=build_openai_timeout(settings.provider_read_timeout_seconds))
            if settings.openai_enabled
            else None
        ),
    )


def create_market_data_provider(
    settings: Settings,
    *,
    client: httpx.AsyncClient | None = None,
) -> MarketDataProvider:
    if not settings.market_data_enabled:
        return DisabledMarketDataProvider()
    if settings.twelve_data_api_key is None:
        raise ConfigurationInvalidError("Для Twelve Data требуется API-ключ.")
    if client is None:
        raise ConfigurationInvalidError("Для включённого Twelve Data требуется HTTP-клиент.")
    return TwelveDataMarketDataAdapter(
        client=client,
        api_key=settings.twelve_data_api_key.get_secret_value(),
        base_url=settings.twelve_data_base_url,
        timeout=build_provider_timeout(settings),
        retry_count=settings.provider_retry_count,
        retry_backoff_seconds=settings.provider_retry_backoff_seconds,
        max_request_range=timedelta(days=settings.provider_max_request_range_days),
    )


def create_economic_calendar_provider(
    settings: Settings,
    *,
    client: httpx.AsyncClient | None = None,
) -> EconomicCalendarProvider:
    if not settings.calendar_enabled:
        return DisabledEconomicCalendarProvider()
    if settings.fmp_api_key is None:
        raise ConfigurationInvalidError("Для FMP требуется API-ключ.")
    if client is None:
        raise ConfigurationInvalidError("Для включённого FMP требуется HTTP-клиент.")
    return FMPEconomicCalendarAdapter(
        client=client,
        api_key=settings.fmp_api_key.get_secret_value(),
        base_url=settings.fmp_base_url,
        timeout=build_provider_timeout(settings),
        retry_count=settings.provider_retry_count,
        retry_backoff_seconds=settings.provider_retry_backoff_seconds,
        max_request_range=timedelta(days=settings.provider_max_request_range_days),
    )


def create_explanation_provider(
    settings: Settings,
    *,
    client: httpx.AsyncClient | None = None,
) -> ExplanationProvider:
    """Phase 8B explainer. Off unless `OPENAI_ENABLED` is true; the disabled provider costs nothing.

    Not called from anywhere yet: 8C does the wiring, and a safety test keeps it that way.
    """
    if not settings.openai_enabled:
        return DisabledExplanationProvider()
    if settings.openai_api_key is None:
        raise ConfigurationInvalidError("Для OpenAI требуется API-ключ.")
    if client is None:
        raise ConfigurationInvalidError("Для включённого OpenAI требуется HTTP-клиент.")
    return OpenAIExplanationAdapter(
        client=client,
        api_key=settings.openai_api_key.get_secret_value(),
        base_url=settings.openai_base_url,
        model=settings.openai_model,
        timeout=build_openai_timeout(settings.provider_read_timeout_seconds),
        retry_count=settings.provider_retry_count,
        retry_backoff_seconds=settings.provider_retry_backoff_seconds,
        max_output_tokens=settings.openai_max_output_tokens,
    )
