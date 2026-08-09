"""Price levels for a signal contract, expressed in average candle ranges.

This is the first module in the project allowed to compute an entry, a protective level, or a
target: the Phase 4 term ban is lifted here and nowhere else. What replaces it is stricter than
what it removes.

**This module contains no strategy.** `direction` is an argument, never a conclusion. Nothing here
reads the market and decides "up" or "down", and a safety test asserts that no module in the project
does. Where a direction could legitimately come from — and how anyone would know it beats a coin
toss — is a separate question that needs outcome measurement the project does not yet have.

**The multipliers below are conventions, not calibrations.** Every threshold elsewhere in this
codebase was derived from observed distributions; these could not be, because judging a stop
distance requires knowing whether the stop or the target was reached first, which nothing here
measures. They are honest defaults, and `docs/phase9a-verification-report.md` says so plainly.

Distances are multiples of the window's average true range rather than fixed prices. A stop twenty
pips away is tight on one instrument and absurd on another; a stop one and a half average candle
ranges away means the same thing on any instrument and any timeframe.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from pydantic import ValidationError

from app.core.constants import DEFAULT_STRATEGY_VERSION
from app.core.time import normalize_to_utc
from app.domain.entities.analysis import AnalysisSnapshot
from app.domain.entities.data_quality import TIMEFRAME_TO_DELTA
from app.domain.entities.pipeline_decision import PipelineDecisionReport, PipelineDecisionStatus
from app.domain.entities.signal_contract import (
    SignalActionability,
    SignalContract,
    SignalDirection,
    SignalLifecycleStatus,
    SignalPricePlan,
)

PRICE_PLAN_CONTRACT_VERSION = "phase9a-price-plan-v1"

# How long a draft stays meaningful: one window width, the same span the snapshot describes.
DEFAULT_VALIDITY_CANDLES = 12


@dataclass(frozen=True)
class LevelMultipliers:
    """Distances from the anchor, counted in average true ranges.

    Conventional values, not measured ones. `target_1` is deliberately further than `stop` so a
    plan never seeks less than it risks — that ratio is the one property here that can be asserted
    without knowing the future.
    """

    #: Half-width of the entry zone around the anchor. It does **not** move the protective level or
    #: the targets: those are measured from the anchor, so `stop` and `target_1` below mean exactly
    #: what they say. Until 2026-08-08 they did not — the band was added to each distance, and
    #: 1.5/2.0 behaved as 1.6/2.1 in every measurement the project made.
    entry_band: Decimal = Decimal("0.10")
    stop: Decimal = Decimal("1.5")
    target_1: Decimal = Decimal("2.0")
    target_2: Decimal | None = Decimal("3.0")

    def __post_init__(self) -> None:
        if self.entry_band < 0:
            raise ValueError("entry_band must not be negative")
        if self.stop <= 0 or self.target_1 <= 0:
            raise ValueError("stop and target_1 must be positive")
        if self.target_1 < self.stop:
            raise ValueError("target_1 must not be closer than stop")
        if self.target_2 is not None and self.target_2 <= self.target_1:
            raise ValueError("target_2 must be further than target_1")


DEFAULT_MULTIPLIERS = LevelMultipliers()


def build_price_plan(
    direction: SignalDirection,
    snapshot: AnalysisSnapshot,
    *,
    multipliers: LevelMultipliers = DEFAULT_MULTIPLIERS,
) -> SignalPricePlan | None:
    """Levels around the latest close, or `None` when the window cannot support them.

    Returns `None` rather than a plan built on substituted numbers: without an average true range
    there is no scale to place levels on, and a fabricated distance would read as a measured one.
    """
    anchor = _anchor_price(snapshot)
    average_true_range = _average_true_range(snapshot)
    if anchor is None or average_true_range is None:
        return None

    decimals = _quoted_decimals(snapshot)
    band = average_true_range * multipliers.entry_band
    entry_min = _quantize(anchor - band, decimals)
    entry_max = _quantize(anchor + band, decimals)
    stop_distance = average_true_range * multipliers.stop
    target_1_distance = average_true_range * multipliers.target_1
    target_2_distance = (
        average_true_range * multipliers.target_2 if multipliers.target_2 is not None else None
    )

    # Distances are measured from the anchor, not from the edge of the entry band. Measuring from
    # the edge made `stop=1.5` behave as 1.6 and `target_1=2.0` as 2.1, because the band added its
    # own 0.1 on each side — so every break-even figure in the project was computed for multipliers
    # nobody had configured. The band is an entry zone; it is not a modifier of the risk geometry.
    if direction == SignalDirection.LONG:
        stop_loss = _quantize(anchor - stop_distance, decimals)
        take_profit_1 = _quantize(anchor + target_1_distance, decimals)
        take_profit_2 = (
            _quantize(anchor + target_2_distance, decimals)
            if target_2_distance is not None
            else None
        )
    else:
        stop_loss = _quantize(anchor + stop_distance, decimals)
        take_profit_1 = _quantize(anchor - target_1_distance, decimals)
        take_profit_2 = (
            _quantize(anchor - target_2_distance, decimals)
            if target_2_distance is not None
            else None
        )

    if stop_loss <= 0 or take_profit_1 <= 0 or (take_profit_2 is not None and take_profit_2 <= 0):
        # A price cannot be zero or negative; a window that would produce one gets no plan.
        return None

    try:
        return SignalPricePlan(
            entry_min=entry_min,
            entry_max=entry_max,
            stop_loss=stop_loss,
            take_profit_1=take_profit_1,
            take_profit_2=take_profit_2,
        )
    except ValidationError:
        return None


def build_draft_contract(
    direction: SignalDirection,
    snapshot: AnalysisSnapshot,
    *,
    created_at: datetime,
    decision: PipelineDecisionReport | None = None,
    multipliers: LevelMultipliers = DEFAULT_MULTIPLIERS,
) -> SignalContract | None:
    """A draft contract carrying the levels, permanently non-actionable.

    `risk_plan` stays `None`: position size needs an account balance, which this project does not
    have and will not invent. A decision that is not ready to review is recorded as a warning on the
    contract, so a plan built over an untrustworthy window says so on its face.
    """
    price_plan = build_price_plan(direction, snapshot, multipliers=multipliers)
    if price_plan is None:
        return None

    created_at_utc = normalize_to_utc(created_at)
    validity = DEFAULT_VALIDITY_CANDLES * TIMEFRAME_TO_DELTA[snapshot.window.timeframe]
    warnings = _decision_warnings(decision)

    try:
        return SignalContract(
            contract_version=PRICE_PLAN_CONTRACT_VERSION,
            pair=snapshot.window.pair,
            timeframe=snapshot.window.timeframe,
            direction=direction,
            status=SignalLifecycleStatus.DRAFT,
            actionability=SignalActionability.NOT_ACTIONABLE,
            created_at=created_at_utc,
            valid_until=created_at_utc + validity,
            strategy_version=DEFAULT_STRATEGY_VERSION,
            price_plan=price_plan,
            risk_plan=None,
            source_snapshot_id=snapshot.metadata.snapshot_id,
            warnings=warnings,
        )
    except ValidationError:
        return None


def _anchor_price(snapshot: AnalysisSnapshot) -> Decimal | None:
    if snapshot.feature_snapshot is None:
        return None
    latest_close = snapshot.feature_snapshot.candle_summary.latest_close
    if latest_close is None or latest_close <= 0:
        return None
    return latest_close


def _average_true_range(snapshot: AnalysisSnapshot) -> Decimal | None:
    if snapshot.feature_snapshot is None:
        return None
    average_true_range = snapshot.feature_snapshot.candle_summary.average_true_range
    if average_true_range is None or average_true_range <= 0:
        return None
    return average_true_range


def _decision_warnings(decision: PipelineDecisionReport | None) -> tuple[str, ...]:
    if decision is None:
        return ()
    if decision.status == PipelineDecisionStatus.READY_FOR_REVIEW:
        return ()
    # READY_WITH_WARNINGS reaches here too, and should: a plan built over a window that failed a
    # warning is still a plan built over a flawed window, and the contract says so on its face.
    return (f"pipeline_status:{decision.status.value}",)


def _quoted_decimals(snapshot: AnalysisSnapshot) -> int | None:
    """How many decimals this instrument appears to quote, read from its own price.

    Deliberately not the storage precision: PostgreSQL hands back `1.1385200000` for a price quoted
    as `1.13852`, and rounding to that would produce ten-decimal levels no venue would accept. The
    trailing zeros are stripped first.

    A heuristic, and knowingly so, with one visible edge: a close that genuinely ends in zero
    (`1.13850`) reads as four decimals, so that window's levels come out one digit coarser. Harmless
    — a real tick size belongs to an instrument specification the project does not have, and when
    one arrives it should replace this.
    """
    if snapshot.feature_snapshot is None:
        return None
    latest_close = snapshot.feature_snapshot.candle_summary.latest_close
    if latest_close is None:
        return None
    exponent = latest_close.normalize().as_tuple().exponent
    if not isinstance(exponent, int):
        return None
    return -exponent if exponent < 0 else 0


def _quantize(value: Decimal, decimals: int | None) -> Decimal:
    if decimals is None:
        return value
    return value.quantize(Decimal(1).scaleb(-decimals))
