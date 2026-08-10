from collections.abc import Mapping
from datetime import datetime
from typing import Any, Protocol

from app.domain.entities import Candle, EconomicEvent, Timeframe
from app.domain.entities.data_quality import UpsertResult
from app.domain.entities.forward_outcome import ForwardOutcomeRecord
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


class ForwardOutcomeRepository(Protocol):
    """Append-then-settle storage for pre-registered plans.

    Deliberately not an upsert. A plan that can be rewritten after the fact is not a pre-registered
    plan, and pre-registration is the only thing this ledger has that an offline replay does not.
    Existing rows are left exactly as they were; only the outcome columns are ever written twice,
    and only from `None`.
    """

    async def add_missing(self, records: list[ForwardOutcomeRecord]) -> int:
        """Insert records whose identity is not stored yet; return how many were new."""

    async def list_pending(
        self,
        *,
        limit: int,
        as_of_at_or_before: datetime | None = None,
    ) -> list[ForwardOutcomeRecord]:
        """Return unresolved records, oldest `as_of` first."""

    async def apply_outcomes(self, records: list[ForwardOutcomeRecord]) -> int:
        """Write the outcome of already-stored records; return how many were settled."""

    async def list_recorded(
        self,
        *,
        pair: CurrencyPair | None = None,
        timeframe: Timeframe | None = None,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> list[ForwardOutcomeRecord]:
        """Return stored records in the requested window, oldest `as_of` first."""
