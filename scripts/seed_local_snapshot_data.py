import argparse
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.config import Settings
from app.core.time import normalize_to_utc, utc_now
from app.domain.entities import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.value_objects import CurrencyPair
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory

DEFAULT_PROVIDER = "local-seed"
DEFAULT_COUNT = 12


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed local closed candles and one calendar event for Telegram readiness demos."
    )
    parser.add_argument("--pair", default="EURUSD")
    parser.add_argument("--timeframe", choices=[item.value for item in Timeframe], default="M15")
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT)
    parser.add_argument("--provider", default=DEFAULT_PROVIDER)
    parser.add_argument("--database-url", default=None)
    parser.add_argument("--skip-event", action="store_true")
    return parser.parse_args()


def _aligned_window(timeframe: Timeframe, count: int) -> tuple[datetime, datetime]:
    now = normalize_to_utc(utc_now())
    if timeframe == Timeframe.M15:
        minute = (now.minute // 15) * 15
        end_at = now.replace(minute=minute, second=0, microsecond=0)
        step = timedelta(minutes=15)
    else:
        end_at = now.replace(minute=0, second=0, microsecond=0)
        step = timedelta(hours=1)
    return end_at - (count * step), end_at


def _candles(
    *,
    pair: CurrencyPair,
    timeframe: Timeframe,
    start_at: datetime,
    count: int,
    provider: str,
) -> list[Candle]:
    step = timedelta(minutes=15) if timeframe == Timeframe.M15 else timedelta(hours=1)
    price = Decimal("1.1000")
    candles: list[Candle] = []
    for index in range(count):
        open_time = start_at + (index * step)
        close_time = open_time + step
        move = Decimal("0.0005") if index % 2 == 0 else Decimal("-0.0002")
        open_price = price
        close_price = open_price + move
        high_price = max(open_price, close_price) + Decimal("0.0003")
        low_price = min(open_price, close_price) - Decimal("0.0003")
        candles.append(
            Candle(
                provider=provider,
                pair=pair,
                timeframe=timeframe,
                open_time=open_time,
                close_time=close_time,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=Decimal("100"),
                is_closed=True,
            )
        )
        price = close_price
    return candles


def _events(
    *,
    pair: CurrencyPair,
    start_at: datetime,
    provider: str,
) -> list[EconomicEvent]:
    scheduled_at = start_at + timedelta(minutes=30)
    return [
        EconomicEvent(
            provider=provider,
            provider_event_id=f"{provider}-{pair.base_currency}-{scheduled_at.isoformat()}",
            title="Local readiness demo event",
            currency=pair.base_currency,
            country=None,
            impact=EconomicImpact.MEDIUM,
            scheduled_at=scheduled_at,
            actual=Decimal("2.1"),
            forecast=Decimal("2.0"),
            previous=Decimal("1.9"),
            fetched_at=start_at,
        )
    ]


async def _main() -> None:
    args = _parse_args()
    if args.count < 1:
        raise ValueError("--count must be at least 1")
    pair = CurrencyPair(value=args.pair.upper())
    timeframe = Timeframe(args.timeframe.upper())
    start_at, end_at = _aligned_window(timeframe, args.count)
    settings = Settings(_env_file=None)
    engine = create_engine(args.database_url or settings.database_dsn())
    try:
        uow_factory = build_uow_factory(create_session_factory(engine))
        candles = _candles(
            pair=pair,
            timeframe=timeframe,
            start_at=start_at,
            count=args.count,
            provider=args.provider,
        )
        events = (
            [] if args.skip_event else _events(pair=pair, start_at=start_at, provider=args.provider)
        )
        async with uow_factory() as uow:
            candle_result = await uow.candles.upsert_many(candles)
            event_result = await uow.economic_events.upsert_many(events)
            await uow.commit()
    finally:
        await engine.dispose()
    print(
        "Seeded readiness demo data: "
        f"pair={pair.value} timeframe={timeframe.value} "
        f"window={start_at.isoformat()}..{end_at.isoformat()} "
        f"candles={candle_result.total} events={event_result.total} provider={args.provider}"
    )


if __name__ == "__main__":
    asyncio.run(_main())
