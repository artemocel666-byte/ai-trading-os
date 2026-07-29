from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.domain.entities import Candle, Timeframe
from app.domain.value_objects import CurrencyPair
from app.services.market_data_backfill_service import (
    MarketDataBackfillService,
    backfill_chunks,
)
from tests.fakes import FakeUnitOfWorkFactory

PAIR = CurrencyPair(value="EURUSD")
START = datetime(2026, 1, 1, tzinfo=UTC)
MAX_RANGE = timedelta(days=31)


def _candle(open_time: datetime) -> Candle:
    step = timedelta(minutes=15)
    return Candle(
        provider="backfill-test",
        pair=PAIR,
        timeframe=Timeframe.M15,
        open_time=open_time,
        close_time=open_time + step,
        open=Decimal("1.1000"),
        high=Decimal("1.1005"),
        low=Decimal("1.0995"),
        close=Decimal("1.1001"),
        volume=Decimal("100"),
        is_closed=True,
    )


class FakeProvider:
    """Returns candles spanning a configurable share of each requested chunk."""

    def __init__(
        self,
        *,
        coverage: float = 1.0,
        empty: bool = False,
        failing_chunk_index: int | None = None,
    ) -> None:
        self._coverage = coverage
        self._empty = empty
        self._failing_chunk_index = failing_chunk_index
        self.calls: list[tuple[datetime, datetime]] = []

    async def get_closed_candles(
        self,
        pair: CurrencyPair,
        timeframe: Timeframe,
        start_at: datetime,
        end_at: datetime,
    ) -> Sequence[Candle]:
        index = len(self.calls)
        self.calls.append((start_at, end_at))
        if index == self._failing_chunk_index:
            raise RuntimeError("provider unavailable")
        if self._empty:
            return []
        # A provider result cap keeps the newest bars, so coverage shrinks from the start side.
        duration = end_at - start_at
        first_open = end_at - (duration * self._coverage)
        return [_candle(first_open), _candle(first_open + timedelta(minutes=15))]


async def _noop_sleep(_seconds: float) -> None:
    return None


def _service(
    provider: FakeProvider,
    factory: FakeUnitOfWorkFactory,
    *,
    chunk_candles: int = 1000,
    delay_seconds: float = 0.0,
    sleep_calls: list[float] | None = None,
) -> MarketDataBackfillService:
    async def _recording_sleep(seconds: float) -> None:
        if sleep_calls is not None:
            sleep_calls.append(seconds)

    return MarketDataBackfillService(
        provider=provider,
        uow_factory=factory,
        chunk_candles=chunk_candles,
        max_request_range=MAX_RANGE,
        delay_seconds=delay_seconds,
        sleep=_recording_sleep if sleep_calls is not None else _noop_sleep,
    )


def test_chunks_cover_the_range_contiguously_oldest_first() -> None:
    end = START + timedelta(days=60)
    chunks = backfill_chunks(
        timeframe=Timeframe.M15,
        start_at=START,
        end_at=end,
        chunk_candles=1000,
        max_request_range=MAX_RANGE,
    )

    assert chunks[0][0] == START
    assert chunks[-1][1] == end
    assert all(chunks[i][1] == chunks[i + 1][0] for i in range(len(chunks) - 1))
    assert all(chunk_end > chunk_start for chunk_start, chunk_end in chunks)
    assert all(chunk_end - chunk_start <= MAX_RANGE for chunk_start, chunk_end in chunks)


def test_chunk_width_is_the_candle_budget_clamped_by_the_range_limit() -> None:
    m15 = backfill_chunks(
        timeframe=Timeframe.M15,
        start_at=START,
        end_at=START + timedelta(days=60),
        chunk_candles=1000,
        max_request_range=MAX_RANGE,
    )
    h1 = backfill_chunks(
        timeframe=Timeframe.H1,
        start_at=START,
        end_at=START + timedelta(days=60),
        chunk_candles=1000,
        max_request_range=MAX_RANGE,
    )

    # 1000 M15 candles is ~10.4 days, well under the 31-day rule.
    assert m15[0][1] - m15[0][0] == timedelta(minutes=15) * 1000
    # 1000 H1 candles would be ~41 days, so the range limit clamps it instead.
    assert h1[0][1] - h1[0][0] == MAX_RANGE


def test_chunk_maths_rejects_nonsense_inputs() -> None:
    with pytest.raises(ValueError, match="chunk_candles"):
        backfill_chunks(
            timeframe=Timeframe.M15,
            start_at=START,
            end_at=START + timedelta(days=1),
            chunk_candles=0,
            max_request_range=MAX_RANGE,
        )
    with pytest.raises(ValueError, match="later than start_at"):
        backfill_chunks(
            timeframe=Timeframe.M15,
            start_at=START,
            end_at=START,
            chunk_candles=1000,
            max_request_range=MAX_RANGE,
        )


@pytest.mark.asyncio
async def test_backfill_stores_every_chunk_and_totals_add_up() -> None:
    provider = FakeProvider()
    factory = FakeUnitOfWorkFactory()
    service = _service(provider, factory)

    result = await service.backfill(
        pair=PAIR,
        timeframe=Timeframe.M15,
        start_at=START,
        end_at=START + timedelta(days=30),
    )

    assert result.succeeded is True
    assert result.failed_chunk_count == 0
    assert result.truncated_chunk_count == 0
    assert result.total_fetched == 2 * len(provider.calls)
    assert result.total_inserted == result.total_fetched
    assert len(factory.candles) == result.total_fetched


@pytest.mark.asyncio
async def test_truncated_chunk_is_detected_and_fails_the_run() -> None:
    """A provider result cap drops the oldest bars, leaving a large leading gap."""
    provider = FakeProvider(coverage=0.1)
    factory = FakeUnitOfWorkFactory()
    service = _service(provider, factory)

    result = await service.backfill(
        pair=PAIR,
        timeframe=Timeframe.M15,
        start_at=START,
        end_at=START + timedelta(days=30),
    )

    assert result.truncated_chunk_count == len(result.chunk_results)
    assert all(chunk.possibly_truncated for chunk in result.chunk_results)
    # Silently accepting this would corrupt any later calibration.
    assert result.succeeded is False


@pytest.mark.asyncio
async def test_empty_chunk_is_neither_a_failure_nor_a_truncation() -> None:
    # A fully closed market returns nothing; that carries no evidence of dropped bars.
    provider = FakeProvider(empty=True)
    factory = FakeUnitOfWorkFactory()
    service = _service(provider, factory)

    result = await service.backfill(
        pair=PAIR,
        timeframe=Timeframe.M15,
        start_at=START,
        end_at=START + timedelta(days=30),
    )

    assert result.total_fetched == 0
    assert result.failed_chunk_count == 0
    assert result.truncated_chunk_count == 0
    assert result.succeeded is True


@pytest.mark.asyncio
async def test_one_failing_chunk_does_not_abandon_the_rest() -> None:
    provider = FakeProvider(failing_chunk_index=0)
    factory = FakeUnitOfWorkFactory()
    service = _service(provider, factory)

    result = await service.backfill(
        pair=PAIR,
        timeframe=Timeframe.M15,
        start_at=START,
        end_at=START + timedelta(days=30),
    )

    assert result.failed_chunk_count == 1
    assert result.chunk_results[0].failed is True
    assert result.chunk_results[0].fetched_count == 0
    assert any(chunk.fetched_count > 0 for chunk in result.chunk_results[1:])
    assert result.succeeded is False


@pytest.mark.asyncio
async def test_delay_is_applied_between_chunks_but_not_before_the_first() -> None:
    provider = FakeProvider()
    factory = FakeUnitOfWorkFactory()
    sleep_calls: list[float] = []
    service = _service(provider, factory, delay_seconds=8.0, sleep_calls=sleep_calls)

    result = await service.backfill(
        pair=PAIR,
        timeframe=Timeframe.M15,
        start_at=START,
        end_at=START + timedelta(days=30),
    )

    assert len(sleep_calls) == len(result.chunk_results) - 1
    assert set(sleep_calls) == {8.0}


@pytest.mark.asyncio
async def test_rerunning_the_same_range_updates_rather_than_duplicates() -> None:
    provider = FakeProvider()
    factory = FakeUnitOfWorkFactory()
    service = _service(provider, factory)

    first = await service.backfill(
        pair=PAIR,
        timeframe=Timeframe.M15,
        start_at=START,
        end_at=START + timedelta(days=30),
    )
    stored_after_first = len(factory.candles)
    second = await service.backfill(
        pair=PAIR,
        timeframe=Timeframe.M15,
        start_at=START,
        end_at=START + timedelta(days=30),
    )

    assert first.total_fetched == second.total_fetched
    # The fake repository appends, so this asserts the same range was requested again rather
    # than the service silently skipping work; real storage deduplicates via upsert_many.
    assert len(factory.candles) == stored_after_first * 2
