from dataclasses import dataclass
from datetime import timedelta

import httpx

from app.adapters.chat_completions_explanations import (
    LOCAL_PROVIDER_NAME,
    OPENAI_PROVIDER_NAME,
    ChatCompletionsExplanationAdapter,
    build_completion_timeout,
)
from app.adapters.disabled import (
    DisabledEconomicCalendarProvider,
    DisabledExplanationProvider,
    DisabledMarketDataProvider,
)
from app.adapters.fmp_calendar import FMPEconomicCalendarAdapter
from app.adapters.twelve_data import TwelveDataMarketDataAdapter
from app.core.config import ExplanationProviderKind, Settings
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
    #: Phase 10-1. Its own client rather than borrowing the market-data one: FRED is a different
    #: host, needs no key, and is not governed by `market_data_enabled` — sharing a client built for
    #: a keyed provider would tie rates to a switch that has nothing to do with them.
    interest_rates: httpx.AsyncClient | None = None

    async def aclose(self) -> None:
        for client in (
            self.market_data,
            self.economic_calendar,
            self.explanation,
            self.interest_rates,
        ):
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
            httpx.AsyncClient(timeout=build_explanation_timeout(settings))
            if settings.explanation_provider_configured()
            else None
        ),
        interest_rates=(
            httpx.AsyncClient(timeout=timeout) if settings.interest_rate_ingestion_enabled else None
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
        min_request_interval_seconds=settings.provider_min_request_interval_seconds,
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


def build_explanation_timeout(settings: Settings) -> httpx.Timeout:
    """The HTTP read timeout follows the explanation budget rather than the generic provider one.

    `/explain` gives up at `explanation_budget_seconds` and sends the deterministic report alone, so
    a read timeout shorter than the budget would fail the call before the budget it was given had
    run out. A model on this machine can need most of that budget.
    """
    return build_completion_timeout(
        max(settings.provider_read_timeout_seconds, settings.explanation_budget_seconds)
    )


def create_explanation_provider(
    settings: Settings,
    *,
    client: httpx.AsyncClient | None = None,
) -> ExplanationProvider:
    """The configured explainer, or the disabled one, which costs nothing.

    Reachable only from `/explain`: no service, scheduler job, or API route may call this, and a
    safety test keeps it that way.
    """
    kind = settings.explanation_provider
    if kind is ExplanationProviderKind.DISABLED:
        return DisabledExplanationProvider()
    if client is None:
        raise ConfigurationInvalidError("Для включённого объяснителя требуется HTTP-клиент.")

    timeout = build_explanation_timeout(settings)
    if kind is ExplanationProviderKind.LOCAL:
        # No API key, on purpose. The endpoint is a process on this machine, and handing it a paid
        # credential would be worse than useless.
        return ChatCompletionsExplanationAdapter(
            client=client,
            provider_name=LOCAL_PROVIDER_NAME,
            api_key=None,
            base_url=settings.local_llm_base_url,
            model=settings.local_llm_model,
            timeout=timeout,
            retry_count=settings.provider_retry_count,
            retry_backoff_seconds=settings.provider_retry_backoff_seconds,
            max_output_tokens=settings.local_llm_max_output_tokens,
        )
    if settings.openai_api_key is None:
        raise ConfigurationInvalidError("Для OpenAI требуется API-ключ.")
    return ChatCompletionsExplanationAdapter(
        client=client,
        provider_name=OPENAI_PROVIDER_NAME,
        api_key=settings.openai_api_key.get_secret_value(),
        base_url=settings.openai_base_url,
        model=settings.openai_model,
        timeout=timeout,
        retry_count=settings.provider_retry_count,
        retry_backoff_seconds=settings.provider_retry_backoff_seconds,
        max_output_tokens=settings.openai_max_output_tokens,
    )
