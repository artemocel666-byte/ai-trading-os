"""Walk a fixed plan forward through history and record what happened first.

**This is the one module in the project permitted to look past `as_of`.** Everywhere else the Phase
3D invariant holds and a snapshot exposes only data at or before the moment it describes. Here the
plan is already fixed before the first forward candle is read, and the result is a measurement, not
an input: nothing produced here may flow back into a snapshot, a rule, or a decision. A safety test
enforces that by forbidding the analysis path from importing this module at all.

Pure domain: candles in, an outcome out. No session, no query, no schedule.

Three honesties are built into the shape of the result rather than left to a report to remember:

- **Ambiguity is a kind, not a coin flip.** A candle whose range spans both the protective level and
  the target cannot say which came first — OHLC records four prices, not their order. That case is
  counted as `AMBIGUOUS` in its own right, and folded into `STOP_FIRST` for the headline share via
  `WindowOutcome.conservative_kind`. Resolving it the flattering way is how a backtest lies.
- **Not resolving is a kind too.** A window where neither level was touched inside the horizon is
  `TIMEOUT`, never quietly dropped and never counted as a loss.
- **Outcomes are gross.** The project stores OHLC and no spread, so nothing here can subtract a
  cost. Real results are worse on both sides, and the report says so instead of implying an edge.

Entry is assumed filled at the entry-band midpoint on the first forward candle — a market entry at
the anchor. Waiting for a pullback into the band is a strategy decision, and this module has no
strategy in it.
"""

from collections.abc import Iterable, Sequence
from decimal import Decimal

from app.domain.entities.market_data import Candle
from app.domain.entities.outcome import OutcomeKind, OutcomeStatistics, WindowOutcome
from app.domain.entities.signal_contract import SignalDirection, SignalPricePlan

# Two windows' worth of candles. Long enough that a plan sized in average true ranges has a fair
# chance to resolve, short enough that "nothing happened" stays a distinguishable answer.
DEFAULT_HORIZON_CANDLES = 24


def measure_outcome(
    direction: SignalDirection,
    plan: SignalPricePlan,
    forward_candles: Sequence[Candle],
    *,
    horizon_candles: int = DEFAULT_HORIZON_CANDLES,
) -> WindowOutcome:
    """Which of the plan's levels the price reached first, over the candles after `as_of`.

    `forward_candles` must be ordered oldest first and must contain only candles strictly after the
    moment the plan was built — this module cannot check that, and the caller that slices history
    is the one place where the future/past boundary is visible.
    """
    if horizon_candles < 1:
        raise ValueError("horizon_candles must be at least one candle")

    entry_price = (plan.entry_min + plan.entry_max) / Decimal(2)
    target = plan.take_profit_1
    stop = plan.stop_loss

    kind = OutcomeKind.NO_DATA
    bars_to_resolution: int | None = None

    for offset, candle in enumerate(forward_candles[:horizon_candles], start=1):
        touched_target = _touched(candle, target)
        touched_stop = _touched(candle, stop)
        if touched_target and touched_stop:
            kind = OutcomeKind.AMBIGUOUS
        elif touched_target:
            kind = OutcomeKind.TARGET_FIRST
        elif touched_stop:
            kind = OutcomeKind.STOP_FIRST
        else:
            # Nothing decided on this candle; keep walking. `kind` stays NO_DATA only if the loop
            # never ran at all.
            kind = OutcomeKind.TIMEOUT
            continue
        bars_to_resolution = offset
        break

    return WindowOutcome(
        direction=direction,
        entry_price=entry_price,
        stop_loss=stop,
        take_profit=target,
        kind=kind,
        bars_to_resolution=bars_to_resolution,
    )


def aggregate_outcomes(outcomes: Iterable[WindowOutcome]) -> OutcomeStatistics:
    """Counts over many windows, keeping every kind separate.

    Ambiguity is never merged away here — `ambiguous_count` carries the raw rate so the size of the
    doubt stays visible. The leaning happens at the point of interpretation instead:
    `target_first_share` divides by all resolved windows, so an ambiguous window counts against the
    plan without pretending to be a loss.
    """
    counts = dict.fromkeys(OutcomeKind, 0)
    resolution_bars: list[int] = []

    for outcome in outcomes:
        counts[outcome.kind] += 1
        if outcome.bars_to_resolution is not None:
            resolution_bars.append(outcome.bars_to_resolution)

    measured = sum(counts.values())
    average_bars = (
        Decimal(sum(resolution_bars)) / Decimal(len(resolution_bars)) if resolution_bars else None
    )

    return OutcomeStatistics(
        measured_count=measured,
        target_first_count=counts[OutcomeKind.TARGET_FIRST],
        stop_first_count=counts[OutcomeKind.STOP_FIRST],
        ambiguous_count=counts[OutcomeKind.AMBIGUOUS],
        timeout_count=counts[OutcomeKind.TIMEOUT],
        no_data_count=counts[OutcomeKind.NO_DATA],
        average_bars_to_resolution=average_bars,
    )


def _touched(candle: Candle, level: Decimal) -> bool:
    """Whether a candle's range covers a price. Touching counts as reaching it."""
    return candle.low <= level <= candle.high
