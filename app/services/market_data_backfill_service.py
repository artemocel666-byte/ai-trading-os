import asyncio
from collections.abc import Awaitable, Callable, Sequence
from datetime import datetime, timedelta

from app.core.time import normalize_to_utc
from app.domain.entities.backfill import BackfillChunkResult, BackfillResult
from app.domain.entities.data_quality import TIMEFRAME_TO_DELTA
from app.domain.entities.market_data import Candle, Timeframe
from app.domain.interfaces.providers import MarketDataProvider
from app.domain.interfaces.unit_of_work import UnitOfWork
from app.domain.value_objects import CurrencyPair

UnitOfWorkFactory = Callable[[], UnitOfWork]
SleepCallable = Callable[[float], Awaitable[None]]

DEFAULT_CHUNK_CANDLES = 1000
DEFAULT_DELAY_SECONDS = 8.0

# A provider result cap drops the oldest bars, so the first returned candle lands well after the
# requested start. Anything beyond this share of the chunk counts as a suspected truncation.
_TRUNCATION_LEADING_GAP_SHARE = 0.25


def backfill_chunks(
    *,
    timeframe: Timeframe,
    start_at: datetime,
    end_at: datetime,
    chunk_candles: int,
    max_request_range: timedelta,
) -> tuple[tuple[datetime, datetime], ...]:
    """Split a range into ordered, contiguous chunks, oldest first.

    Chunk width is the candle budget clamped by the adapter's maximum request range, so requests
    stay inside both the provider's range rule and a size where a result cap is unlikely.
    """
    if chunk_candles < 1:
        raise ValueError("chunk_candles must be at least one candle")
    if max_request_range <= timedelta(0):
        raise ValueError("max_request_range must be positive")
    start_utc = normalize_to_utc(start_at)
    end_utc = normalize_to_utc(end_at)
    if end_utc <= start_utc:
        raise ValueError("backfill end_at must be later than start_at")

    width = min(chunk_candles * TIMEFRAME_TO_DELTA[timeframe], max_request_range)
    chunks: list[tuple[datetime, datetime]] = []
    cursor = start_utc
    while cursor < end_utc:
        chunk_end = min(cursor + width, end_utc)
        chunks.append((cursor, chunk_end))
        cursor = chunk_end
    return tuple(chunks)


class MarketDataBackfillService:
    """Fills historical candles chunk by chunk.

    This is a deliberate, manual operation rather than a scheduled job: it exists so later
    calibration has a real distribution to work from. It stores candles only and produces no
    trading output.
    """

    def __init__(
        self,
        *,
        provider: MarketDataProvider,
        uow_factory: UnitOfWorkFactory,
        chunk_candles: int = DEFAULT_CHUNK_CANDLES,
        max_request_range: timedelta = timedelta(days=31),
        delay_seconds: float = DEFAULT_DELAY_SECONDS,
        sleep: SleepCallable | None = None,
    ) -> None:
        self._provider = provider
        self._uow_factory = uow_factory
        self._chunk_candles = chunk_candles
        self._max_request_range = max_request_range
        self._delay_seconds = delay_seconds
        self._sleep = sleep or asyncio.sleep

    async def backfill(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        start_at: datetime,
        end_at: datetime,
    ) -> BackfillResult:
        chunks = backfill_chunks(
            timeframe=timeframe,
            start_at=start_at,
            end_at=end_at,
            chunk_candles=self._chunk_candles,
            max_request_range=self._max_request_range,
        )
        chunk_results: list[BackfillChunkResult] = []
        for index, (chunk_start, chunk_end) in enumerate(chunks):
            if index > 0 and self._delay_seconds > 0:
                await self._sleep(self._delay_seconds)
            chunk_results.append(
                await self._backfill_chunk(
                    pair=pair,
                    timeframe=timeframe,
                    chunk_start=chunk_start,
                    chunk_end=chunk_end,
                )
            )

        failed_chunk_count = sum(1 for chunk in chunk_results if chunk.failed)
        truncated_chunk_count = sum(1 for chunk in chunk_results if chunk.possibly_truncated)
        return BackfillResult(
            pair=pair,
            timeframe=timeframe,
            requested_start=start_at,
            requested_end=end_at,
            chunk_results=tuple(chunk_results),
            total_fetched=sum(chunk.fetched_count for chunk in chunk_results),
            total_inserted=sum(chunk.inserted_count for chunk in chunk_results),
            total_updated=sum(chunk.updated_count for chunk in chunk_results),
            failed_chunk_count=failed_chunk_count,
            truncated_chunk_count=truncated_chunk_count,
            succeeded=(
                bool(chunk_results) and failed_chunk_count == 0 and truncated_chunk_count == 0
            ),
        )

    async def _backfill_chunk(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        chunk_start: datetime,
        chunk_end: datetime,
    ) -> BackfillChunkResult:
        try:
            candles = await self._provider.get_closed_candles(
                pair,
                timeframe,
                chunk_start,
                chunk_end,
            )
            inserted, updated = await self._store_candles(candles)
        except Exception as error:
            # The type name, not the message: a provider message can quote the request URL, and the
            # request URL carries the API key. The name is enough to separate a rate limit from a
            # timeout from a restricted plan, which is the whole question when a fill comes back
            # holed.
            return BackfillChunkResult(
                chunk_start=chunk_start,
                chunk_end=chunk_end,
                failed=True,
                failure_reason=type(error).__name__,
            )

        open_times = sorted(candle.open_time for candle in candles)
        first_open_time = open_times[0] if open_times else None
        return BackfillChunkResult(
            chunk_start=chunk_start,
            chunk_end=chunk_end,
            fetched_count=len(candles),
            inserted_count=inserted,
            updated_count=updated,
            first_candle_open_time=first_open_time,
            last_candle_open_time=open_times[-1] if open_times else None,
            possibly_truncated=_looks_truncated(
                chunk_start=chunk_start,
                chunk_end=chunk_end,
                first_candle_open_time=first_open_time,
            ),
        )

    async def _store_candles(self, candles: Sequence[Candle]) -> tuple[int, int]:
        if not candles:
            return (0, 0)
        async with self._uow_factory() as uow:
            result = await uow.candles.upsert_many(list(candles))
            await uow.commit()
        return (result.inserted, result.updated)


def _looks_truncated(
    *,
    chunk_start: datetime,
    chunk_end: datetime,
    first_candle_open_time: datetime | None,
) -> bool:
    if first_candle_open_time is None:
        # An empty chunk carries no evidence either way; a closed market returns nothing.
        return False
    leading_gap = normalize_to_utc(first_candle_open_time) - normalize_to_utc(chunk_start)
    chunk_duration = normalize_to_utc(chunk_end) - normalize_to_utc(chunk_start)
    return leading_gap > (chunk_duration * _TRUNCATION_LEADING_GAP_SHARE)
