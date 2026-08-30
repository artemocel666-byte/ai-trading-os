"""Where the currency universe stands right now, against its own history.

Phase 10-2, and the first output in this project written for a person rather than for a
measurement. Seven pre-registered measurements returned nothing and 9D-4 explained why: what can be
computed from public data is already in the price. So this describes **where things stand** and
never what will happen next — no forecast, no ranking by expected return, no "usually".

Three things a person watching one chart cannot get:

- **Is it the pair or the currency?** `EURUSD` rising is either a stronger euro or a weaker dollar,
  and one line cannot tell them apart. Forty-four pairs can.
- **Is this move large?** A number with no scale is decoration; the same number at the 94th
  percentile of its own history is a fact.
- **What does each pair pay?** The current interest rate differential, ranked, which most people
  holding a position have never looked up.

Read-only: it evaluates and prints, and writes nothing.
"""

import argparse
import asyncio
import sys
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.config import Settings
from app.core.time import normalize_to_utc, utc_now
from app.domain.carry import RATE_LAG_MONTHS, carry_differential, lagged_rates_for_anchor
from app.domain.cross_section import forward_return, latest_close_at
from app.domain.currency_universe import UNIVERSE_CURRENCIES, universe_pairs
from app.domain.entities.market_data import Candle
from app.domain.entities.market_state import CarryReadingToday, MarketStateReport
from app.domain.entities.positioning import PositioningReading
from app.domain.market_calendar import month_start, shift_months
from app.domain.market_state import currency_strength, read_against_history
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory
from app.presentation.readings import (
    format_currency_strength,
    format_historical_reading,
    format_positioning,
)
from app.services.market_reading_service import MarketReadingService

#: How far back "recently" reaches for the currency decomposition. Five sessions is a week of
#: trading — long enough that one quiet day does not dominate, short enough to still be "now".
DEFAULT_WINDOW_DAYS = 5

#: How much history a percentile is taken against. Two years of daily bars is roughly 500
#: observations, enough that a percentile means something and recent enough to be the same market.
DEFAULT_HISTORY_DAYS = 730


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Describe where the currency universe stands against its own history. Read-only, and "
            "contains no forecast."
        )
    )
    parser.add_argument("--window-days", type=int, default=DEFAULT_WINDOW_DAYS)
    parser.add_argument("--history-days", type=int, default=DEFAULT_HISTORY_DAYS)
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


def _daily_ranges(candles: list[Candle]) -> list[Decimal]:
    """Each bar's high-to-low span as a share of its open — comparable across pairs and eras."""
    return [(candle.high - candle.low) / candle.open for candle in candles if candle.open > 0]


async def _load(
    database_url: str,
) -> tuple[
    dict[str, list[Candle]],
    dict[str, dict[datetime, Decimal]],
    dict[str, list[PositioningReading]],
]:
    """Everything this report reads, in one place and over one engine.

    Phase 11-3: the queries moved to `MarketReadingService`. What is left here is the engine
    lifecycle, which a script owns and a route does not.
    """
    engine = create_engine(database_url)
    try:
        service = MarketReadingService(
            uow_factory=build_uow_factory(create_session_factory(engine))
        )
        return (
            await service.daily_candles(),
            await service.interest_rates(),
            await service.positioning(),
        )
    finally:
        await engine.dispose()


async def _main() -> int:
    args = _parse_args()
    if args.window_days < 1 or args.history_days < args.window_days:
        raise ValueError("history must be at least as long as the window, and both positive")
    settings = Settings(_env_file=None)
    as_of = normalize_to_utc(utc_now())
    by_pair, by_currency, positioning = await _load(args.database_url or settings.database_dsn())

    if not by_pair:
        print("Дневных свечей нет. Сначала запустите заливку вселенной фазы 9D-1.")
        return 1

    window_start = as_of - timedelta(days=args.window_days)
    history_start = as_of - timedelta(days=args.history_days)

    moves: dict[str, Decimal] = {}
    readings = []
    thin: list[str] = []
    for symbol, candles in by_pair.items():
        opened = latest_close_at(candles, window_start)
        latest = candles[-1].close
        move = None if opened is None else forward_return([opened, latest])
        if move is not None:
            moves[symbol] = move

        recent = [c for c in candles if c.close_time >= history_start]
        ranges = _daily_ranges(recent)
        if len(ranges) < 30:
            thin.append(symbol)
            continue
        reading = read_against_history(
            instrument=symbol,
            field_ref="daily_range",
            current=ranges[-1],
            history=ranges[:-1],
        )
        if reading is not None:
            readings.append(reading)

    # Plumbing before the content, as in every phase since 9D-1: a description built on a thinned
    # universe is not the same description, and reading the content first makes that easy to miss.
    print(f"Состояние вселенной на {as_of.isoformat(timespec='seconds')}")
    print(
        f"  пар с дневной историей: {len(by_pair)} из {len(universe_pairs())}   "  # noqa: RUF001
        f"валют со ставками: {len(by_currency)} из {len(UNIVERSE_CURRENCIES)}"  # noqa: RUF001
    )
    print(
        f"  окно движения: {args.window_days} дн.   "
        f"история для перцентилей: {args.history_days} дн.   "
        f"пар с движением: {len(moves)}   с перцентилем: {len(readings)}"  # noqa: RUF001
    )
    if thin:
        print(f"  слишком мало истории для перцентиля ({len(thin)}): {', '.join(sorted(thin))}")

    if not moves:
        print("\nНи по одной паре не удалось посчитать движение; описывать нечего.")  # noqa: RUF001
        return 1

    strengths = currency_strength(moves)
    carry = _carry_today(by_currency, as_of)
    report = MarketStateReport(
        as_of=as_of,
        window_days=args.window_days,
        strengths=strengths,
        readings=tuple(readings),
        carry=carry,
    )

    print(f"\nВалюты за {args.window_days} дн. — это движение пары или движение валюты:")  # noqa: RUF001
    for reading in report.strongest_first:
        print(f"  {format_currency_strength(reading)}")

    print("\nРазмах последнего дня против собственной истории пары, десять самых необычных:")  # noqa: RUF001
    unusual = sorted(report.readings, key=lambda item: item.percentile, reverse=True)[:10]
    for reading in unusual:
        print(f"  {format_historical_reading(reading)}")

    if report.carry:
        month = report.carry[0].rate_month.date()
        print(f"\nРазница ставок на сегодня (ставки за {month}, лаг {RATE_LAG_MONTHS} мес.):")  # noqa: RUF001
        ranked = report.highest_carry_first
        for item in list(ranked[:5]) + list(ranked[-5:]):
            print(f"  {item.instrument:<8} {item.differential * 100:+.2f}% годовых")
    else:
        # Named, not merely reported missing. The project's standing habit is that an absence is
        # said out loud: a reader who knows it is EUR and GBP that stop in January can judge the
        # gap, while "нет данных" teaches them only that something is wrong somewhere.
        needed = shift_months(month_start(as_of), -RATE_LAG_MONTHS)
        missing = sorted(
            currency
            for currency in UNIVERSE_CURRENCIES
            if needed not in by_currency.get(currency, {})
        )
        print(
            f"\nРазница ставок: не считаем. За {needed.date()} нет ставок по "  # noqa: RUF001
            f"{', '.join(missing)}, а неполный набор дал бы таблицу без этих валют "  # noqa: RUF001
            f"и без предупреждения об этом."  # noqa: RUF001
        )

    if positioning:
        absent = sorted(UNIVERSE_CURRENCIES - set(positioning))
        print("\nПозиции спекулянтов по данным CFTC:")  # noqa: RUF001
        for currency in sorted(positioning):
            rows = positioning[currency]
            latest = rows[-1]
            standing = read_against_history(
                instrument=currency,
                field_ref="net_positioning_share",
                current=latest.net_share,
                history=[row.net_share for row in rows[:-1]],
            )
            line = format_positioning(latest, as_of=as_of)
            if standing is not None:
                # Noun before number, as `format_distribution` already does: Russian numeral
                # agreement changes with the last digit, and "1451 недель" is simply wrong.
                line += (
                    f"; {standing.percentile}-й перцентиль, "
                    f"недельных наблюдений {standing.observation_count}"
                )
            print(f"  {line}")
        if absent:
            # A currency with no contract has no position to report. Naming it keeps the table from
            # reading as though those two were flat.
            print(
                f"  Контракта нет вовсе, поэтому нет и данных: {', '.join(absent)}. "
                f"Это отсутствие, а не нулевая позиция."  # noqa: RUF001
            )

    print(
        "\nЭто описание состояния, а не прогноз. Здесь нет утверждений о том, что будет дальше, "  # noqa: RUF001
        "и семь предрегистрированных измерений проекта показали, почему их и не может быть."
    )
    return 0


def _carry_today(
    by_currency: dict[str, dict[datetime, Decimal]], as_of: datetime
) -> tuple[CarryReadingToday, ...]:
    """Every pair's current differential, or nothing at all if one currency is missing its rate.

    All-or-nothing for the same reason Phase 9D-4 gave: one absent rate silently removes nine of
    forty-five pairs, and a ranking over the survivors is a different table wearing the same name.
    """
    anchor = month_start(as_of)
    rates = lagged_rates_for_anchor(anchor, by_currency, UNIVERSE_CURRENCIES)
    if rates is None:
        return ()
    rate_month = shift_months(anchor, -RATE_LAG_MONTHS)
    return tuple(
        CarryReadingToday(
            instrument=pair.value,
            differential=carry_differential(
                base_rate=rates[pair.base_currency], quote_rate=rates[pair.quote_currency]
            ),
            rate_month=rate_month,
        )
        for pair in universe_pairs()
    )


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
