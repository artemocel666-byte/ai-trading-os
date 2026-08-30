"""Render the market state as one self-contained page.

Phase 11-1. The same readings `report_market_state.py` prints, drawn instead of typed — and drawn
only in the four forms `app/presentation/charts.py` permits. Nothing here computes anything new:
every number on the page has already been measured and tested.

Read-only apart from the single file it writes, and that file makes no network request when opened.
"""

import argparse
import asyncio
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from app.core.config import Settings
from app.core.time import normalize_to_utc, utc_now
from app.domain.concentration import read_concentration
from app.domain.currency_universe import UNIVERSE_CURRENCIES, universe_pairs
from app.domain.entities.concentration import ConcentrationStatus
from app.domain.entities.positioning import PositioningReading
from app.domain.market_state import currency_strength, daily_returns, read_against_history
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory
from app.presentation.charts import distribution_strip, matrix_grid, plain_rows, ranked_bars
from app.presentation.page import build_page
from app.services.market_reading_service import MarketReadingService

DEFAULT_WINDOW_DAYS = 5
DEFAULT_HISTORY_DAYS = 730
DEFAULT_CORRELATION_DAYS = 90
DEFAULT_OUTPUT = "market_state.html"

#: How many pairs the correlation grid shows. Forty-four names would be unreadable at any size, and
#: an unreadable grid is decoration. The most concentrated set is what a reader actually wants.
GRID_SIZE = 8


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render the market state as one self-contained HTML page. Read-only."
    )
    parser.add_argument("--window-days", type=int, default=DEFAULT_WINDOW_DAYS)
    parser.add_argument("--history-days", type=int, default=DEFAULT_HISTORY_DAYS)
    parser.add_argument("--correlation-days", type=int, default=DEFAULT_CORRELATION_DAYS)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


async def _load(database_url: str, *, correlation_since: datetime) -> dict[str, object]:
    """Everything the page draws, over one engine.

    Phase 11-3: the queries are `MarketReadingService` and the returns are `daily_returns`. The
    correlation window is applied here rather than in either, because it is a property of this
    page's question and not of the data.
    """
    engine = create_engine(database_url)
    try:
        service = MarketReadingService(
            uow_factory=build_uow_factory(create_session_factory(engine))
        )
        candles = await service.daily_candles()
        positioning = await service.positioning()
    finally:
        await engine.dispose()

    returns: dict[str, dict[str, Decimal]] = {}
    for symbol, rows in candles.items():
        series = daily_returns([row for row in rows if row.close_time >= correlation_since])
        if series:
            returns[symbol] = series
    return {"candles": candles, "returns": returns, "positioning": positioning}


def _strength_section(candles: dict[str, list], as_of: datetime, window_days: int) -> str:
    from app.domain.cross_section import forward_return, latest_close_at

    start = as_of - timedelta(days=window_days)
    moves: dict[str, Decimal] = {}
    for symbol, rows in candles.items():
        opened = latest_close_at(rows, start)
        if opened is None:
            continue
        move = forward_return([opened, rows[-1].close])
        if move is not None:
            moves[symbol] = move
    if not moves:
        return ""
    strengths = sorted(currency_strength(moves), key=lambda item: item.mean_move, reverse=True)
    return ranked_bars(
        label="Валюта против всех остальных",
        rows=tuple(
            (item.currency, item.mean_move, item.lowest_move, item.highest_move)
            for item in strengths
        ),
        window=f"окно {window_days} дн.",
        sample_note=f"пар с движением {len(moves)}",  # noqa: RUF001
    )


def _unusual_sections(
    candles: dict[str, list], as_of: datetime, history_days: int, limit: int = 6
) -> list[str]:
    history_start = as_of - timedelta(days=history_days)
    readings = []
    for symbol, rows in candles.items():
        recent = [c for c in rows if c.close_time >= history_start and c.open > 0]
        ranges = [(c.high - c.low) / c.open for c in recent]
        if len(ranges) < 30:
            continue
        reading = read_against_history(
            instrument=symbol,
            field_ref="daily_range",
            current=ranges[-1],
            history=ranges[:-1],
        )
        if reading is not None:
            readings.append(reading)
    readings.sort(key=lambda item: item.percentile, reverse=True)
    return [
        distribution_strip(
            label=item.instrument,
            distribution=item.distribution,
            current=item.current,
            window=f"история {history_days} дн.",
        )
        for item in readings[:limit]
    ]


async def _build_document(args: argparse.Namespace) -> str | None:
    """`None` when there is nothing to draw, which the caller turns into a non-zero exit."""
    settings = Settings(_env_file=None)
    as_of = normalize_to_utc(utc_now())
    loaded = await _load(
        args.database_url or settings.database_dsn(),
        correlation_since=as_of - timedelta(days=args.correlation_days),
    )
    candles: dict[str, list] = loaded["candles"]  # type: ignore[assignment]
    returns: dict[str, dict[str, Decimal]] = loaded["returns"]  # type: ignore[assignment]
    positioning: dict[str, list[PositioningReading]] = loaded["positioning"]  # type: ignore[assignment]

    if not candles:
        print("Дневных свечей нет. Сначала запустите заливку вселенной фазы 9D-1.")
        return None

    # Plumbing first, on the page as in every report since 9D-1.
    plumbing = plain_rows(
        label="Что под этой страницей",
        rows=(
            ("Пар с дневной историей", f"{len(candles)} из {len(universe_pairs())}"),  # noqa: RUF001
            ("Валют с позициями CFTC", f"{len(positioning)} из {len(UNIVERSE_CURRENCIES)}"),  # noqa: RUF001
            ("Окно движения", f"{args.window_days} дн."),
            ("История для перцентилей", f"{args.history_days} дн."),
            ("Окно корреляций", f"{args.correlation_days} дн."),
            ("Собрано", as_of.isoformat(timespec="seconds")),
        ),
    )

    sections: list[tuple[str, str]] = [("Проводка", plumbing)]

    strength = _strength_section(candles, as_of, args.window_days)
    if strength:
        sections.append(("Это движение пары или движение валюты", strength))

    unusual = _unusual_sections(candles, as_of, args.history_days)
    if unusual:
        sections.append(
            (
                "Насколько необычен размах последнего дня",
                "".join(unusual),
            )
        )

    grid = _grid_section(returns, args.correlation_days)
    if grid:
        sections.append(("Что с чем ходит вместе", grid))  # noqa: RUF001

    if positioning:
        sections.append(("Позиции спекулянтов", _positioning_section(positioning, as_of)))

    return build_page(
        title="Состояние валютной вселенной",
        subtitle=(
            f"на {as_of.date()} · описание, не прогноз · "
            f"{len(candles)} пар, {len(positioning)} валют с позициями"  # noqa: RUF001
        ),
        sections=tuple(sections),
    )


def main() -> None:
    """The file write lives here, not in the coroutine: it is a plain synchronous call."""
    args = _parse_args()
    document = asyncio.run(_build_document(args))
    if document is None:
        sys.exit(1)
    output = Path(args.output)
    output.write_text(document, encoding="utf-8")
    print(f"Написано: {output.resolve()}  ({len(document):,} байт)")
    sys.exit(0)


def _grid_section(returns: dict[str, dict[str, Decimal]], window_days: int) -> str:
    if len(returns) < 2:
        return ""
    names = tuple(sorted(returns))
    reading = read_concentration(names, returns)
    if reading.status is not ConcentrationStatus.MEASURED or not reading.correlations:
        return ""
    strongest = sorted(reading.correlations, key=lambda item: abs(item.coefficient), reverse=True)
    chosen: list[str] = []
    for item in strongest:
        for name in (item.left, item.right):
            if name not in chosen and len(chosen) < GRID_SIZE:
                chosen.append(name)
        if len(chosen) >= GRID_SIZE:
            break
    subset = tuple(sorted(chosen))
    values = {
        (item.left, item.right): item.coefficient
        for item in reading.correlations
        if item.left in subset and item.right in subset
    }
    overlap = min(item.overlap_count for item in reading.correlations)
    return matrix_grid(
        label="Корреляции самых связанных пар",
        names=subset,
        values=values,
        window=f"окно {window_days} дн.",
        sample_note=f"общих дней не менее {overlap}",
    )


def _positioning_section(positioning: dict[str, list[PositioningReading]], as_of: datetime) -> str:
    rows: list[tuple[str, Decimal, Decimal, Decimal]] = []
    oldest = 0
    for currency in sorted(positioning):
        series = positioning[currency]
        latest = series[-1]
        oldest = max(oldest, latest.age_in_days(as_of))
        shares = [row.net_share for row in series]
        rows.append((currency, latest.net_share, min(shares), max(shares)))
    absent = sorted(UNIVERSE_CURRENCIES - set(positioning))
    note = f"контракта нет: {', '.join(absent)}" if absent else "все валюты покрыты"
    return ranked_bars(
        label="Чистая позиция как доля открытого интереса",
        rows=tuple(sorted(rows, key=lambda item: item[1], reverse=True)),
        window=f"данным {oldest} дн.; полоса — весь диапазон за всю историю",
        sample_note=note,
    )


if __name__ == "__main__":
    main()
