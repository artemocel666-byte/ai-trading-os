"""Separate the pair from the currency, and give every number a scale.

Pure domain: prices and rates in, readings out. No session, no query — the caller that reads storage
is the one place any of that lives, as in `cross_section.py`, `carry.py` and `data_freshness.py`.

**The percentile machinery is read, never rewritten.** `summarize_field` and `nearest_rank` in
`rule_calibration.py` are the single definition of a percentile in this project — the docstring
there records that `nearest_rank` was made public, reverted the same day, and made public again only
when a second caller genuinely needed it. `percentile_rank` below is its **inverse**, not a second
copy: `nearest_rank` maps a percent to a value, this maps a value to a percent, and neither can be
expressed in terms of the other without doing the other's work.

**Nothing here forecasts.** Every function answers a question about what is or was, and the report
that renders them may not phrase any of it as an expectation.
"""

from collections.abc import Mapping, Sequence
from decimal import Decimal
from itertools import pairwise

from app.domain.entities.calibration import FieldDistribution
from app.domain.entities.market_data import Candle
from app.domain.entities.market_state import CurrencyStrengthReading, HistoricalReading
from app.domain.rule_calibration import summarize_field


def percentile_rank(sorted_values: Sequence[Decimal], value: Decimal) -> int:
    """Where `value` sits in a sorted sample, as a whole percent of observations at or below it.

    The inverse of `nearest_rank`, and floored rather than interpolated for the same reason: an
    interpolated rank would report a position the sample never occupied. A value at or above the
    maximum reads 100; one below the minimum reads 0.
    """
    count = len(sorted_values)
    if count == 0:
        raise ValueError("a rank needs a sample to be ranked against")
    at_or_below = sum(1 for observed in sorted_values if observed <= value)
    return (at_or_below * 100) // count


def read_against_history(
    *,
    instrument: str,
    field_ref: str,
    current: Decimal,
    history: Sequence[Decimal],
) -> HistoricalReading | None:
    """Today's value, its position in the instrument's own history, and that history's shape.

    `None` when there is no history to judge against — an absence named rather than a percentile
    invented from nothing.
    """
    if not history:
        return None
    ordered = sorted(history)
    distribution: FieldDistribution = summarize_field(field_ref, ordered)
    return HistoricalReading(
        instrument=instrument,
        field_ref=field_ref,
        current=current,
        percentile=percentile_rank(ordered, current),
        distribution=distribution,
    )


def currency_strength(
    moves_by_pair: Mapping[str, Decimal],
) -> tuple[CurrencyStrengthReading, ...]:
    """Each currency's move against every counterpart it is quoted with, from pair moves alone.

    A pair's move is a statement about **two** currencies at once: `EURUSD` up 1% is the euro up
    against the dollar, which is the dollar down against the euro. Splitting every pair move into
    its two halves and averaging per currency is what separates a rising euro from a falling dollar
    — the question a single chart cannot answer, and the reason this function exists.

    Each reading carries the range it was averaged over, because a mean of nine moves that were all
    positive is a different fact from a mean of nine that cancelled, and one number cannot tell them
    apart.
    """
    collected: dict[str, list[Decimal]] = {}
    for symbol, move in moves_by_pair.items():
        if len(symbol) != 6:
            raise ValueError(f"a pair symbol must be six letters: {symbol}")
        base, quote = symbol[:3], symbol[3:]
        collected.setdefault(base, []).append(move)
        collected.setdefault(quote, []).append(-move)

    readings = [
        CurrencyStrengthReading(
            currency=currency,
            observation_count=len(moves),
            mean_move=sum(moves, Decimal("0")) / Decimal(len(moves)),
            lowest_move=min(moves),
            highest_move=max(moves),
        )
        for currency, moves in collected.items()
    ]
    # Sorted by name so two runs read the same way; the caller orders by strength when it wants to.
    return tuple(sorted(readings, key=lambda reading: reading.currency))


def daily_returns(candles: Sequence[Candle]) -> dict[str, Decimal]:
    """Close-to-close returns keyed by the closing bar's moment.

    Phase 11-3 brought this here from two scripts that had written it identically. It is arithmetic
    on candles rather than loading, so it belongs beside the other pure functions — a service that
    quietly derives is how a number ends up with two definitions.

    **Keyed rather than a flat list**, because the only consumers correlate pairs against each
    other, and alignment is a property of each pair: two instruments share whichever days both were
    priced. A list would let equal-length series describing different days be compared as though
    they matched.

    A bar whose predecessor closed at or below zero contributes nothing — there is no return to
    compute from it, and a substituted zero would read as "it did not move".
    """
    series: dict[str, Decimal] = {}
    for previous, current in pairwise(candles):
        if previous.close > 0:
            series[current.close_time.isoformat()] = (
                current.close - previous.close
            ) / previous.close
    return series
