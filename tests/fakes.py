from types import TracebackType
from typing import Any, Self

from app.domain.entities import Candle, EconomicEvent, Timeframe
from app.domain.entities.data_quality import UpsertResult
from app.domain.interfaces.repositories import (
    AuditLogRepository,
    CandleRepository,
    EconomicEventRepository,
    ErrorEventRepository,
    SystemStateRepository,
)
from app.domain.value_objects import CurrencyPair


class FakeSystemStateRepository:
    def __init__(self, state: dict[str, Any]) -> None:
        self._state = state

    async def get(self, key: str) -> Any | None:
        return self._state.get(key)

    async def set(self, key: str, value: Any) -> None:
        self._state[key] = value

    async def get_all(self) -> dict[str, Any]:
        return dict(self._state)


class FakeAuditLogRepository:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    async def add(
        self,
        *,
        event_type: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        actor: str | None = None,
        before_json: dict[str, Any] | None = None,
        after_json: dict[str, Any] | None = None,
    ) -> None:
        self.events.append(
            {
                "event_type": event_type,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "actor": actor,
                "before_json": before_json,
                "after_json": after_json,
            }
        )


class FakeErrorEventRepository:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    async def add(
        self,
        *,
        error_code: str,
        severity: str,
        component: str,
        message_ru: str,
        technical_details: str | None = None,
        context_json: dict[str, Any] | None = None,
        resolved: bool = False,
    ) -> None:
        self.events.append(
            {
                "error_code": error_code,
                "severity": severity,
                "component": component,
                "message_ru": message_ru,
                "technical_details": technical_details,
                "context_json": context_json,
                "resolved": resolved,
            }
        )


class FakeCandleRepository:
    def __init__(self, candles: list[Candle]) -> None:
        self._candles = candles

    async def upsert_many(self, candles: list[Candle]) -> UpsertResult:
        self._candles.extend(candles)
        return UpsertResult(inserted=len(candles), updated=0)

    async def list_range(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        start_at: Any,
        end_at: Any,
        provider: str | None = None,
    ) -> list[Candle]:
        return [
            candle
            for candle in self._candles
            if candle.pair == pair
            and candle.timeframe == timeframe
            and candle.open_time >= start_at
            and candle.close_time <= end_at
            and (provider is None or candle.provider == provider)
        ]


class FakeEconomicEventRepository:
    def __init__(self, events: list[EconomicEvent]) -> None:
        self._events = events

    async def upsert_many(self, events: list[EconomicEvent]) -> UpsertResult:
        self._events.extend(events)
        return UpsertResult(inserted=len(events), updated=0)

    async def list_window(
        self,
        *,
        start_at: Any,
        end_at: Any,
        currencies: list[str] | None = None,
        provider: str | None = None,
    ) -> list[EconomicEvent]:
        return [
            event
            for event in self._events
            if start_at <= event.scheduled_at < end_at
            and (currencies is None or event.currency in currencies)
            and (provider is None or event.provider == provider)
        ]


class FakeUnitOfWork:
    def __init__(
        self,
        state: dict[str, Any],
        candles: list[Candle],
        events: list[EconomicEvent],
    ) -> None:
        self.system_state: SystemStateRepository = FakeSystemStateRepository(state)
        self.audit_logs: AuditLogRepository = FakeAuditLogRepository()
        self.error_events: ErrorEventRepository = FakeErrorEventRepository()
        self.candles: CandleRepository = FakeCandleRepository(candles)
        self.economic_events: EconomicEventRepository = FakeEconomicEventRepository(events)
        self.committed = False
        self.rolled_back = False

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None or not self.committed:
            self.rolled_back = True

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class FakeUnitOfWorkFactory:
    def __init__(
        self,
        state: dict[str, Any] | None = None,
        candles: list[Candle] | None = None,
        events: list[EconomicEvent] | None = None,
    ) -> None:
        self.state = state or {}
        self.candles = candles or []
        self.events = events or []
        self.instances: list[FakeUnitOfWork] = []

    def __call__(self) -> FakeUnitOfWork:
        uow = FakeUnitOfWork(self.state, self.candles, self.events)
        self.instances.append(uow)
        return uow
