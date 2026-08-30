"""Assemble the market page once, so that a script and a route cannot drift apart.

Phase 11-4. Until now the whole document lived inside `scripts/render_market_page.py`, which was
right while a file was the only way to see it. A route that rebuilt the same sections would be
Phase 11-3 happening one level up — and the second copy is the one that drifts.

**This module decides nothing and measures nothing.** Every number it draws has already been
measured, tested and named in a phase report; every mark it draws comes from the four primitives in
`app/presentation/charts.py`. What lives here is the choice of *which* readings go on the page and
in *what order* — plumbing first, then the content, then the sentence about what the page is not.

It takes readings from `MarketReadingService` and returns a string. It opens no connection and
writes no file: a script owns its engine lifecycle and a route owns neither, so both are the
caller's business.
"""

from datetime import datetime, timedelta
from decimal import Decimal

from app.domain.concentration import read_concentration
from app.domain.currency_universe import UNIVERSE_CURRENCIES, universe_pairs
from app.domain.entities.concentration import ConcentrationStatus
from app.domain.entities.market_data import Candle
from app.domain.entities.positioning import PositioningReading
from app.domain.market_state import currency_strength, daily_returns, read_against_history
from app.domain.price_series import forward_return, latest_close_at
from app.presentation.charts import distribution_strip, matrix_grid, plain_rows, ranked_bars
from app.presentation.page import build_page
from app.services.market_reading_service import MarketReadingService

#: The windows the page is drawn over. They live here rather than in the script, because the route
#: needs the same defaults and a second copy of a default is how two surfaces quietly disagree.
DEFAULT_WINDOW_DAYS = 5
DEFAULT_HISTORY_DAYS = 730
DEFAULT_CORRELATION_DAYS = 90

#: How many pairs the correlation grid shows. Forty-four names would be unreadable at any size, and
#: an unreadable grid is decoration. The most concentrated set is what a reader actually wants.
GRID_SIZE = 8

#: How many daily bars a pair needs before its range gets a percentile. Below this a percentile is
#: arithmetic without meaning, and the pair is left off rather than shown with a weak one.
MINIMUM_RANGE_OBSERVATIONS = 30

#: How many of the most unusual ranges are drawn. The rest are not hidden — they are simply less
#: unusual, and a strip per pair would be forty-four strips nobody reads.
UNUSUAL_LIMIT = 6


class MarketPageService:
    """One document, assembled from stored readings and nothing else."""

    def __init__(self, *, readings: MarketReadingService) -> None:
        self._readings = readings

    async def document(
        self,
        *,
        as_of: datetime,
        window_days: int = DEFAULT_WINDOW_DAYS,
        history_days: int = DEFAULT_HISTORY_DAYS,
        correlation_days: int = DEFAULT_CORRELATION_DAYS,
    ) -> str | None:
        """The page, or `None` when there is nothing stored to draw.

        `None` rather than an empty page: a caller that writes a file turns it into a non-zero exit
        and a caller that serves it turns it into a status, and neither should have to guess from
        the length of a string.
        """
        candles = await self._readings.daily_candles()
        if not candles:
            return None
        positioning = await self._readings.positioning()

        correlation_since = as_of - timedelta(days=correlation_days)
        returns: dict[str, dict[str, Decimal]] = {}
        for symbol, rows in candles.items():
            series = daily_returns([row for row in rows if row.close_time >= correlation_since])
            if series:
                returns[symbol] = series

        sections: list[tuple[str, str]] = [
            (
                "Проводка",
                _plumbing_section(
                    candles,
                    positioning,
                    as_of=as_of,
                    window_days=window_days,
                    history_days=history_days,
                    correlation_days=correlation_days,
                ),
            )
        ]

        strength = _strength_section(candles, as_of, window_days)
        if strength:
            sections.append(("Это движение пары или движение валюты", strength))

        unusual = _unusual_sections(candles, as_of, history_days)
        if unusual:
            sections.append(("Насколько необычен размах последнего дня", "".join(unusual)))

        grid = _grid_section(returns, correlation_days)
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


def _plumbing_section(
    candles: dict[str, list[Candle]],
    positioning: dict[str, list[PositioningReading]],
    *,
    as_of: datetime,
    window_days: int,
    history_days: int,
    correlation_days: int,
) -> str:
    """Plumbing first, on the page as in every report since 9D-1."""
    return plain_rows(
        label="Что под этой страницей",
        rows=(
            ("Пар с дневной историей", f"{len(candles)} из {len(universe_pairs())}"),  # noqa: RUF001
            ("Валют с позициями CFTC", f"{len(positioning)} из {len(UNIVERSE_CURRENCIES)}"),  # noqa: RUF001
            ("Окно движения", f"{window_days} дн."),
            ("История для перцентилей", f"{history_days} дн."),
            ("Окно корреляций", f"{correlation_days} дн."),
            ("Собрано", as_of.isoformat(timespec="seconds")),
        ),
    )


def _strength_section(candles: dict[str, list[Candle]], as_of: datetime, window_days: int) -> str:
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
    candles: dict[str, list[Candle]],
    as_of: datetime,
    history_days: int,
    limit: int = UNUSUAL_LIMIT,
) -> list[str]:
    history_start = as_of - timedelta(days=history_days)
    readings = []
    for symbol, rows in candles.items():
        recent = [c for c in rows if c.close_time >= history_start and c.open > 0]
        ranges = [(c.high - c.low) / c.open for c in recent]
        if len(ranges) < MINIMUM_RANGE_OBSERVATIONS:
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
