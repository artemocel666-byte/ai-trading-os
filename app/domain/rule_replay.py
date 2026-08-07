"""Replay the built-in rules over stored history to measure how they behave.

Pure domain code: candles in, a calibration report out. It holds no session, performs no query,
and is never scheduled — replaying on a timer would recompute the same past forever. Loading the
history is the caller's job, which keeps this module free of persistence exactly as the Phase 4G
boundary requires of everything that touches the composer.

The walk deliberately uses the real evaluation path (`AnalysisEngine` plus the Phase 4G
`StrategyDecisionComposer`) rather than a parallel implementation. Pass rates measured against a
lookalike evaluator would say nothing about what `/review` actually reports.
"""

from bisect import bisect_left, bisect_right
from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from app.domain.analysis_engine import AnalysisEngine
from app.domain.entities.analysis import AnalysisSnapshot
from app.domain.entities.calibration import RuleCalibrationReport
from app.domain.entities.data_quality import TIMEFRAME_TO_DELTA
from app.domain.entities.market_data import Candle, EconomicEvent, Timeframe
from app.domain.rule_calibration import RuleCalibrationAccumulator
from app.domain.strategy_decision_composer import StrategyDecisionComposer
from app.domain.strategy_field_resolver import FIELD_RESOLVERS, FieldResolution
from app.domain.value_objects import CurrencyPair

# Matches DEFAULT_SNAPSHOT_CANDLE_COUNT in app/telegram/commands.py: the replay must measure the
# window shape production actually builds, not a more convenient one.
DEFAULT_WINDOW_CANDLES = 12
DEFAULT_STEP_CANDLES = 1


@dataclass(frozen=True)
class ReplayWindow:
    """One sampled moment: the snapshot as it stood, and where that moment sits in history.

    `candle_index` is the position of the candle whose close is this window's `as_of`, in the same
    ordered series the walk used. It exists so a caller that legitimately needs what came *after*
    the window — outcome measurement, and nothing else — can slice forward without re-deriving the
    ordering and risking a different one.
    """

    snapshot: AnalysisSnapshot
    candle_index: int


def iter_replay_windows(
    *,
    pair: CurrencyPair,
    timeframe: Timeframe,
    ordered_candles: Sequence[Candle],
    ordered_events: Sequence[EconomicEvent] = (),
    window_candles: int = DEFAULT_WINDOW_CANDLES,
    step_candles: int = DEFAULT_STEP_CANDLES,
    analysis_engine: AnalysisEngine | None = None,
) -> Iterator[ReplayWindow]:
    """Yield one snapshot per sampled moment, oldest first.

    Each stored candle close is one `as_of`, so the sampled moments are exactly the moments a
    window could have been requested with fresh data. The window itself is selected by time, the
    same way the production query does, so a gap in history produces a genuinely incomplete window
    instead of a silently back-filled one.

    Every snapshot ends at its own `as_of`; this walk never hands a window anything later than the
    moment it describes, which is the Phase 3D invariant expressed as code.
    """
    engine = analysis_engine or AnalysisEngine()
    step = TIMEFRAME_TO_DELTA[timeframe]
    open_times = [candle.open_time for candle in ordered_candles]
    event_times = [event.scheduled_at for event in ordered_events]

    for index in range(window_candles - 1, len(ordered_candles), step_candles):
        as_of = ordered_candles[index].close_time
        window_end = as_of
        window_start = window_end - (window_candles * step)
        window_candle_slice = ordered_candles[
            bisect_left(open_times, window_start) : bisect_right(open_times, window_end)
        ]
        window_candle_slice = [
            candle for candle in window_candle_slice if candle.close_time <= window_end
        ]
        window_events = ordered_events[
            bisect_left(event_times, window_start) : bisect_right(event_times, window_end)
        ]

        snapshot = engine.build_snapshot(
            pair=pair,
            timeframe=timeframe,
            window_start=window_start,
            window_end=window_end,
            as_of=as_of,
            candles=window_candle_slice,
            economic_events=window_events,
        )
        yield ReplayWindow(snapshot=snapshot, candle_index=index)


def order_candles(
    candles: Sequence[Candle], *, pair: CurrencyPair, timeframe: Timeframe
) -> list[Candle]:
    """The one ordering every walk uses: closed candles for this series, oldest first."""
    return sorted(
        (
            candle
            for candle in candles
            if candle.pair == pair and candle.timeframe == timeframe and candle.is_closed
        ),
        key=lambda candle: (candle.open_time, candle.provider),
    )


def replay_windows(
    *,
    pair: CurrencyPair,
    timeframe: Timeframe,
    candles: Sequence[Candle],
    economic_events: Sequence[EconomicEvent] = (),
    window_candles: int = DEFAULT_WINDOW_CANDLES,
    step_candles: int = DEFAULT_STEP_CANDLES,
    analysis_engine: AnalysisEngine | None = None,
    composer: StrategyDecisionComposer | None = None,
) -> RuleCalibrationReport:
    """Walk stored candles and evaluate every window with the real decision path."""
    if window_candles < 1:
        raise ValueError("window_candles must be at least one candle")
    if step_candles < 1:
        raise ValueError("step_candles must be at least one candle")

    decision_composer = composer or StrategyDecisionComposer()
    step = TIMEFRAME_TO_DELTA[timeframe]

    ordered = order_candles(candles, pair=pair, timeframe=timeframe)
    if len(ordered) < window_candles:
        raise ValueError("not enough stored candles to replay a single window")

    accumulator = RuleCalibrationAccumulator()
    for window in iter_replay_windows(
        pair=pair,
        timeframe=timeframe,
        ordered_candles=ordered,
        ordered_events=sorted(economic_events, key=lambda event: event.scheduled_at),
        window_candles=window_candles,
        step_candles=step_candles,
        analysis_engine=analysis_engine,
    ):
        snapshot = window.snapshot
        decision = decision_composer.compose(snapshot, snapshot.window.as_of)
        field_values: dict[str, FieldResolution] = {
            field_ref: resolver(snapshot) for field_ref, resolver in FIELD_RESOLVERS.items()
        }
        accumulator.observe(decision=decision, field_values=field_values)

    first_window_end = ordered[window_candles - 1].close_time
    return accumulator.build_report(
        pair=pair,
        timeframe=timeframe,
        replay_start=first_window_end - (window_candles * step),
        replay_end=ordered[-1].close_time,
        window_candles=window_candles,
        step_candles=step_candles,
    )
