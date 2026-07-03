from collections.abc import Mapping, Sequence
from datetime import datetime
from decimal import Decimal
from typing import Any, Protocol

from app.core.enums import Decision
from app.domain.entities import Candle, EconomicEvent, Timeframe
from app.domain.value_objects import CurrencyPair


class MarketDataProvider(Protocol):
    """Future market-data adapter contract.

    Implementations must return only closed candles and must never fabricate market data.
    Disabled production adapters must raise IntegrationDisabledError before any network call.
    """

    async def get_closed_candles(
        self,
        pair: CurrencyPair,
        timeframe: Timeframe,
        start_at: datetime,
        end_at: datetime,
    ) -> Sequence[Candle]:
        """Return closed candles for the requested pair and timeframe."""


class EconomicCalendarProvider(Protocol):
    """Future economic-calendar adapter contract with no fabricated events."""

    async def get_events(
        self,
        start_at: datetime,
        end_at: datetime,
        currencies: Sequence[str] | None = None,
    ) -> Sequence[EconomicEvent]:
        """Return scheduled economic events for a bounded time range."""


class LLMProvider(Protocol):
    """Future LLM adapter contract.

    LLM output may explain deterministic results in Russian, but it must not change prices,
    scores, risks, or create a signal rejected by deterministic rules.
    """

    async def explain(
        self,
        deterministic_decision: Decision,
        evidence: Sequence[Mapping[str, Any]],
    ) -> str:
        """Return a Russian-language explanation for a deterministic decision."""


class MessageSender(Protocol):
    """Future outbound message contract."""

    async def send_message(self, chat_id: int, message: str) -> None:
        """Send an already validated user-facing message."""


class ChiefAIExplainer(Protocol):
    """Future Chief AI boundary.

    The Chief AI may summarize agent reports, explain agreement and disagreement,
    describe risks, and format Russian explanations. It must never modify deterministic
    calculations, bypass risk rules, fabricate evidence, or resurrect a rejected signal.
    """

    async def summarize_decision(
        self,
        deterministic_decision: Decision,
        setup_score: Decimal,
        risk_percent: Decimal,
        agent_reports: Sequence[Mapping[str, Any]],
    ) -> str:
        """Return a Russian explanation without changing deterministic inputs."""
