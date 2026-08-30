"""How many bets a set of positions actually is.

Phase 10-3. Someone holding `EURUSD`, `GBPUSD` and `AUDUSD` believes they hold three positions. If
those three move together they hold roughly one position at triple size, and the loss that arrives
will arrive on all three at once. Saying so needs no forecast — it is arithmetic on stored prices.

Two modes:

- **`--instruments EURUSD,GBPUSD,AUDUSD`** — the set a person actually holds.
- **no arguments** — the whole stored universe, which also measures a claim
  `app/domain/currency_universe.py` has carried unmeasured since Phase 9D-1: that forty-five pairs
  drawn from ten currencies hold "closer to nine" independent dimensions.

Read-only: it evaluates and prints, and writes nothing.
"""

import argparse
import asyncio
import sys
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.config import Settings
from app.core.time import normalize_to_utc, utc_now
from app.domain.concentration import read_concentration
from app.domain.entities.concentration import MINIMUM_OVERLAP, ConcentrationStatus
from app.domain.market_state import daily_returns
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory
from app.presentation.readings import format_concentration, format_correlation
from app.services.market_reading_service import MarketReadingService

#: The window every correlation is taken over. A quarter is about sixty-four trading days, which
#: puts a correlation's standard error near 0.12 — stated in the output rather than hidden behind
#: two decimal places.
DEFAULT_WINDOW_DAYS = 90


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Say how many independent bets a set of instruments is. Read-only, and contains no "
            "forecast."
        )
    )
    parser.add_argument(
        "--instruments",
        default=None,
        help="comma-separated symbols, e.g. EURUSD,GBPUSD,AUDUSD; omit for the whole universe",
    )
    parser.add_argument("--window-days", type=int, default=DEFAULT_WINDOW_DAYS)
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


async def _load_returns(database_url: str, *, since: datetime) -> dict[str, dict[str, Decimal]]:
    """Daily close-to-close returns per pair, keyed by the bar's close time.

    Phase 11-3: the loading is `MarketReadingService` and the arithmetic is `daily_returns`. This
    function is now only the wiring between them, plus the engine lifecycle a script owns.
    """
    engine = create_engine(database_url)
    try:
        service = MarketReadingService(
            uow_factory=build_uow_factory(create_session_factory(engine))
        )
        candles = await service.daily_candles(since=since)
    finally:
        await engine.dispose()
    series = {symbol: daily_returns(rows) for symbol, rows in candles.items()}
    return {symbol: values for symbol, values in series.items() if values}


async def _main() -> int:
    args = _parse_args()
    if args.window_days < 1:
        raise ValueError("a window is at least one day")
    settings = Settings(_env_file=None)
    since = normalize_to_utc(utc_now()) - timedelta(days=args.window_days)
    returns = await _load_returns(args.database_url or settings.database_dsn(), since=since)

    if not returns:
        print("Дневных свечей нет. Сначала запустите заливку вселенной фазы 9D-1.")
        return 1

    if args.instruments:
        chosen = tuple(item.strip().upper() for item in args.instruments.split(",") if item.strip())
    else:
        chosen = tuple(sorted(returns))

    unknown = [symbol for symbol in chosen if symbol not in returns]
    lengths = sorted(len(returns[symbol]) for symbol in chosen if symbol in returns)

    # Plumbing before the content, as in every phase since 9D-1.
    print(f"Окно: {args.window_days} дн., минимум общих дней для корреляции: {MINIMUM_OVERLAP}")
    print(f"  инструментов запрошено: {len(chosen)}   с сохранённой историей: {len(lengths)}")  # noqa: RUF001
    if lengths:
        print(f"  дневных доходностей на инструмент: минимум {lengths[0]}, максимум {lengths[-1]}")
    if unknown:
        print(f"  нет в базе ({len(unknown)}): {', '.join(unknown)}")

    if len(chosen) < 2:
        print("\nВопрос о концентрации требует хотя бы двух инструментов.")  # noqa: RUF001
        return 1

    reading = read_concentration(chosen, returns)

    print(f"\n{format_concentration(reading)}")

    if reading.status is ConcentrationStatus.MEASURED and len(chosen) > 5:
        bets = reading.effective_bets
        assert bets is not None
        print(
            f"  То есть {len(chosen)} инструментов ведут себя примерно как {bets:.1f} независимых."  # noqa: RUF001
        )
        if not args.instruments:
            print(
                "  Это измерение того, что фаза 9D-1 записала в докстроку без проверки: "
                "сколько независимых измерений на самом деле у вселенной."  # noqa: RUF001
            )

    if reading.correlations:
        widest = reading.widest_half_gap
        strongest = sorted(
            reading.correlations, key=lambda item: abs(item.coefficient), reverse=True
        )[:10]
        print("\nСамые сильные связи в наборе:")  # noqa: RUF001
        for item in strongest:
            print(f"  {format_correlation(item)}")

        unstable = sorted(reading.correlations, key=lambda item: item.half_gap, reverse=True)[:5]
        print("\nСамые неустойчивые между половинами окна:")  # noqa: RUF001
        for item in unstable:
            print(f"  {format_correlation(item)}")
        if widest is not None:
            print(
                f"\n  Наибольшее расхождение половин: {widest:.2f}. "
                f"На таком окне стандартная ошибка корреляции около 0.12, "  # noqa: RUF001
                f"поэтому 0.3 и 0.5 здесь надёжно не различить."
            )

    print(
        "\nЭто описание состояния, а не прогноз. Корреляции меняются, и сказать, "  # noqa: RUF001
        "какими они станут, здесь нельзя."
    )
    return 0


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
