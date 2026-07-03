from collections.abc import Mapping, Sequence
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.core.enums import Decision
from app.core.exceptions import IntegrationDisabledError
from app.domain.entities import Candle, EconomicEvent, Timeframe
from app.domain.value_objects import CurrencyPair


class DisabledMarketDataProvider:
    async def get_closed_candles(
        self,
        pair: CurrencyPair,
        timeframe: Timeframe,
        start_at: datetime,
        end_at: datetime,
    ) -> Sequence[Candle]:
        raise IntegrationDisabledError("market_data")


class DisabledEconomicCalendarProvider:
    async def get_events(
        self,
        start_at: datetime,
        end_at: datetime,
        currencies: Sequence[str] | None = None,
    ) -> Sequence[EconomicEvent]:
        raise IntegrationDisabledError("calendar")


class DisabledLLMProvider:
    async def explain(
        self,
        deterministic_decision: Decision,
        evidence: Sequence[Mapping[str, Any]],
    ) -> str:
        raise IntegrationDisabledError("openai")


class DisabledChiefAIExplainer:
    async def summarize_decision(
        self,
        deterministic_decision: Decision,
        setup_score: Decimal,
        risk_percent: Decimal,
        agent_reports: Sequence[Mapping[str, Any]],
    ) -> str:
        raise IntegrationDisabledError("openai")
