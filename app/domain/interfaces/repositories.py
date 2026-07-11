from collections.abc import Mapping
from datetime import datetime
from typing import Any, Protocol

from app.domain.entities import Candle, EconomicEvent, Timeframe
from app.domain.entities.data_quality import UpsertResult
from app.domain.value_objects import CurrencyPair


class SystemStateRepository(Protocol):
    async def get(self, key: str) -> Any | None:
        """Return one state value by key."""

    async def set(self, key: str, value: Any) -> None:
        """Persist one state value by key."""

    async def get_all(self) -> dict[str, Any]:
        """Return all persisted system state values."""


class AuditLogRepository(Protocol):
    async def add(
        self,
        *,
        event_type: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        actor: str | None = None,
        before_json: Mapping[str, Any] | None = None,
        after_json: Mapping[str, Any] | None = None,
    ) -> None:
        """Append an audit log event."""


class ErrorEventRepository(Protocol):
    async def add(
        self,
        *,
        error_code: str,
        severity: str,
        component: str,
        message_ru: str,
        technical_details: str | None = None,
        context_json: Mapping[str, Any] | None = None,
        resolved: bool = False,
    ) -> None:
        """Append a structured error event."""


class CandleRepository(Protocol):
    async def upsert_many(self, candles: list[Candle]) -> UpsertResult:
        """Insert or update normalized closed candles without creating duplicates."""

    async def list_range(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        start_at: datetime,
        end_at: datetime,
        provider: str | None = None,
    ) -> list[Candle]:
        """Return closed candles fully contained in the requested UTC window."""


class EconomicEventRepository(Protocol):
    async def upsert_many(self, events: list[EconomicEvent]) -> UpsertResult:
        """Insert or update normalized economic events without creating duplicates."""

    async def list_window(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
        currencies: list[str] | None = None,
        provider: str | None = None,
    ) -> list[EconomicEvent]:
        """Return economic events satisfying start_at <= scheduled_at < end_at."""
