from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.core import constants
from app.domain.analysis_engine import AnalysisEngine
from app.domain.entities import Candle, Timeframe
from app.domain.entities.signal_contract import (
    SignalActionability,
    SignalDirection,
    SignalLifecycleStatus,
)
from app.domain.signal_price_plan import (
    DEFAULT_MULTIPLIERS,
    LevelMultipliers,
    build_draft_contract,
    build_price_plan,
)
from app.domain.strategy_decision_composer import StrategyDecisionComposer
from app.domain.value_objects import CurrencyPair

PAIR = CurrencyPair(value="EURUSD")
JPY_PAIR = CurrencyPair(value="USDJPY")
BASE_TIME = datetime(2026, 7, 20, 8, 0, tzinfo=UTC)
CREATED_AT = datetime(2026, 8, 5, 12, 0, tzinfo=UTC)
STEP = timedelta(minutes=15)


def _candle(
    index: int,
    *,
    pair: CurrencyPair = PAIR,
    base: Decimal = Decimal("1.10000"),
    tick: Decimal = Decimal("0.00013"),
    scale: Decimal = Decimal("1"),
) -> Candle:
    open_time = BASE_TIME + (index * STEP)
    close = base + (tick * Decimal(index) * scale)
    half_range = tick * Decimal("2") * scale
    return Candle(
        provider="price-plan-test",
        pair=pair,
        timeframe=Timeframe.M15,
        open_time=open_time,
        close_time=open_time + STEP,
        open=close,
        high=close + half_range,
        low=close - half_range,
        close=close,
        volume=Decimal("100"),
        is_closed=True,
    )


def _snapshot(
    *,
    candle_count: int = 12,
    pair: CurrencyPair = PAIR,
    base: Decimal = Decimal("1.10000"),
    tick: Decimal = Decimal("0.00013"),
    scale: Decimal = Decimal("1"),
):
    candles = [
        _candle(index, pair=pair, base=base, tick=tick, scale=scale)
        for index in range(candle_count)
    ]
    as_of = BASE_TIME + (candle_count * STEP)
    return AnalysisEngine().build_snapshot(
        pair=pair,
        timeframe=Timeframe.M15,
        window_start=BASE_TIME,
        window_end=as_of,
        as_of=as_of,
        candles=candles,
        economic_events=[],
        moving_average_windows=(3,),
    )


def _atr(snapshot) -> Decimal:
    assert snapshot.feature_snapshot is not None
    average_true_range = snapshot.feature_snapshot.candle_summary.average_true_range
    assert average_true_range is not None
    return average_true_range


def _anchor(snapshot) -> Decimal:
    assert snapshot.feature_snapshot is not None
    latest_close = snapshot.feature_snapshot.candle_summary.latest_close
    assert latest_close is not None
    return latest_close


@pytest.mark.parametrize("direction", [SignalDirection.LONG, SignalDirection.SHORT])
def test_geometry_satisfies_the_phase4a_contract(direction: SignalDirection) -> None:
    """The Phase 4A validator is the referee: it rejects a stop on the wrong side outright."""
    snapshot = _snapshot()

    contract = build_draft_contract(direction, snapshot, created_at=CREATED_AT)

    assert contract is not None
    plan = contract.price_plan
    assert plan.entry_min <= plan.entry_max
    if direction == SignalDirection.LONG:
        assert plan.stop_loss < plan.entry_min
        assert plan.take_profit_1 > plan.entry_max
        assert plan.take_profit_2 is not None
        assert plan.take_profit_2 > plan.take_profit_1
    else:
        assert plan.stop_loss > plan.entry_max
        assert plan.take_profit_1 < plan.entry_min
        assert plan.take_profit_2 is not None
        assert plan.take_profit_2 < plan.take_profit_1


@pytest.mark.parametrize("direction", [SignalDirection.LONG, SignalDirection.SHORT])
def test_distances_are_the_configured_atr_multiples(direction: SignalDirection) -> None:
    snapshot = _snapshot()
    anchor = _anchor(snapshot)
    average_true_range = _atr(snapshot)

    plan = build_price_plan(direction, snapshot)

    assert plan is not None
    step = anchor.normalize()
    band = average_true_range * DEFAULT_MULTIPLIERS.entry_band
    assert plan.entry_min == (anchor - band).quantize(step)
    assert plan.entry_max == (anchor + band).quantize(step)
    # Measured from the anchor, not from the edge of the band. Until 2026-08-08 the band was added
    # to each distance, so a configured 1.5 behaved as 1.6 and every break-even figure in the
    # project was computed for multipliers nobody had set.
    expected_stop_distance = average_true_range * DEFAULT_MULTIPLIERS.stop
    expected_target_distance = average_true_range * DEFAULT_MULTIPLIERS.target_1
    if direction == SignalDirection.LONG:
        assert plan.stop_loss == (anchor - expected_stop_distance).quantize(step)
        assert plan.take_profit_1 == (anchor + expected_target_distance).quantize(step)
    else:
        assert plan.stop_loss == (anchor + expected_stop_distance).quantize(step)
        assert plan.take_profit_1 == (anchor - expected_target_distance).quantize(step)


@pytest.mark.parametrize("direction", [SignalDirection.LONG, SignalDirection.SHORT])
def test_the_entry_band_does_not_move_the_risk_geometry(direction: SignalDirection) -> None:
    """Widening the entry zone must not quietly widen the stop and the target with it.

    The band describes where an order might sit; the multipliers describe what is risked and sought.
    Conflating them is how `stop=1.5` came to mean 1.6 everywhere.
    """
    snapshot = _snapshot()
    narrow = build_price_plan(
        direction, snapshot, multipliers=LevelMultipliers(entry_band=Decimal("0.05"))
    )
    wide = build_price_plan(
        direction, snapshot, multipliers=LevelMultipliers(entry_band=Decimal("0.40"))
    )

    assert narrow is not None
    assert wide is not None
    assert narrow.stop_loss == wide.stop_loss
    assert narrow.take_profit_1 == wide.take_profit_1
    assert wide.entry_max - wide.entry_min > narrow.entry_max - narrow.entry_min


@pytest.mark.parametrize("direction", [SignalDirection.LONG, SignalDirection.SHORT])
def test_the_first_target_is_never_closer_than_the_stop(direction: SignalDirection) -> None:
    """A plan must not seek less than it risks. This holds without knowing the future."""
    snapshot = _snapshot()

    plan = build_price_plan(direction, snapshot)

    assert plan is not None
    entry_mid = (plan.entry_min + plan.entry_max) / Decimal("2")
    risk = abs(entry_mid - plan.stop_loss)
    reward = abs(plan.take_profit_1 - entry_mid)
    assert reward >= risk


def test_distances_stay_the_same_in_atr_terms_when_volatility_scales() -> None:
    """Three times the movement is three times the distance, and the same number of ranges."""
    calm = _snapshot()
    wild = _snapshot(scale=Decimal("3"))

    calm_plan = build_price_plan(SignalDirection.LONG, calm)
    wild_plan = build_price_plan(SignalDirection.LONG, wild)

    assert calm_plan is not None
    assert wild_plan is not None
    calm_ranges = (_anchor(calm) - calm_plan.stop_loss) / _atr(calm)
    wild_ranges = (_anchor(wild) - wild_plan.stop_loss) / _atr(wild)
    assert abs(calm_ranges - wild_ranges) < Decimal("0.01")
    # The absolute distance did grow with the market.
    assert (_anchor(wild) - wild_plan.stop_loss) > (_anchor(calm) - calm_plan.stop_loss)


def test_levels_are_quantised_to_the_precision_the_instrument_quotes() -> None:
    five_decimals = _snapshot()
    three_decimals = _snapshot(
        pair=JPY_PAIR,
        base=Decimal("150.000"),
        tick=Decimal("0.013"),
    )

    fx_plan = build_price_plan(SignalDirection.LONG, five_decimals)
    jpy_plan = build_price_plan(SignalDirection.LONG, three_decimals)

    assert fx_plan is not None
    assert jpy_plan is not None
    assert fx_plan.stop_loss.as_tuple().exponent == -5
    assert jpy_plan.stop_loss.as_tuple().exponent == -3


def test_no_plan_without_a_scale_to_place_levels_on() -> None:
    """A flat window has a zero average true range; a fabricated distance would be a lie."""
    flat_candles = [
        Candle(
            provider="price-plan-test",
            pair=PAIR,
            timeframe=Timeframe.M15,
            open_time=BASE_TIME + (index * STEP),
            close_time=BASE_TIME + ((index + 1) * STEP),
            open=Decimal("1.10000"),
            high=Decimal("1.10000"),
            low=Decimal("1.10000"),
            close=Decimal("1.10000"),
            volume=Decimal("100"),
            is_closed=True,
        )
        for index in range(12)
    ]
    as_of = BASE_TIME + (12 * STEP)
    flat = AnalysisEngine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=BASE_TIME,
        window_end=as_of,
        as_of=as_of,
        candles=flat_candles,
        economic_events=[],
        moving_average_windows=(3,),
    )

    assert build_price_plan(SignalDirection.LONG, flat) is None
    assert build_draft_contract(SignalDirection.LONG, flat, created_at=CREATED_AT) is None


def test_no_plan_without_a_feature_snapshot() -> None:
    empty = _snapshot(candle_count=0)

    assert build_price_plan(SignalDirection.SHORT, empty) is None
    assert build_draft_contract(SignalDirection.SHORT, empty, created_at=CREATED_AT) is None


def test_draft_contract_is_permanently_non_actionable() -> None:
    snapshot = _snapshot()

    contract = build_draft_contract(SignalDirection.LONG, snapshot, created_at=CREATED_AT)

    assert contract is not None
    assert contract.status == SignalLifecycleStatus.DRAFT
    assert contract.actionability == SignalActionability.NOT_ACTIONABLE
    assert contract.is_actionable is False
    # Position size needs an account balance this project does not have and will not invent.
    assert contract.risk_plan is None
    assert contract.valid_until > contract.created_at
    assert contract.source_snapshot_id == snapshot.metadata.snapshot_id


def test_a_plan_over_an_untrustworthy_window_says_so() -> None:
    thin = _snapshot(candle_count=3)
    decision = StrategyDecisionComposer().compose(thin, thin.window.as_of)

    contract = build_draft_contract(
        SignalDirection.LONG,
        thin,
        created_at=CREATED_AT,
        decision=decision,
    )

    assert contract is not None
    assert decision.status.value != "READY_FOR_REVIEW"
    assert contract.warnings == (f"pipeline_status:{decision.status.value}",)


def test_a_ready_window_carries_no_warning() -> None:
    snapshot = _snapshot()
    decision = StrategyDecisionComposer().compose(snapshot, snapshot.window.as_of)

    contract = build_draft_contract(
        SignalDirection.SHORT,
        snapshot,
        created_at=CREATED_AT,
        decision=decision,
    )

    assert contract is not None
    assert contract.warnings == ()


def test_multipliers_reject_a_plan_that_risks_more_than_it_seeks() -> None:
    with pytest.raises(ValueError, match="target_1 must not be closer than stop"):
        LevelMultipliers(stop=Decimal("3.0"), target_1=Decimal("1.0"))
    with pytest.raises(ValueError, match="target_2 must be further"):
        LevelMultipliers(target_1=Decimal("2.0"), target_2=Decimal("1.5"))
    with pytest.raises(ValueError, match="must be positive"):
        LevelMultipliers(stop=Decimal("0"))


def test_precision_survives_the_trailing_zeros_storage_adds() -> None:
    """PostgreSQL returns `1.1385200000` for a price quoted as `1.13852`.

    Rounding to the storage exponent produced ten-decimal levels no venue would accept — found by
    running the builder against the real database, not by the synthetic tests above.
    """
    stored_like = [
        Candle(
            provider="price-plan-test",
            pair=PAIR,
            timeframe=Timeframe.M15,
            open_time=BASE_TIME + (index * STEP),
            close_time=BASE_TIME + ((index + 1) * STEP),
            open=Decimal("1.1385200000") + (Decimal("0.0001300000") * index),
            high=Decimal("1.1388200000") + (Decimal("0.0001300000") * index),
            low=Decimal("1.1382200000") + (Decimal("0.0001300000") * index),
            close=Decimal("1.1385200000") + (Decimal("0.0001300000") * index),
            volume=Decimal("100"),
            is_closed=True,
        )
        for index in range(12)
    ]
    as_of = BASE_TIME + (12 * STEP)
    snapshot = AnalysisEngine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=BASE_TIME,
        window_end=as_of,
        as_of=as_of,
        candles=stored_like,
        economic_events=[],
        moving_average_windows=(3,),
    )

    plan = build_price_plan(SignalDirection.LONG, snapshot)

    assert plan is not None
    for level in (plan.entry_min, plan.entry_max, plan.stop_loss, plan.take_profit_1):
        assert level.as_tuple().exponent == -5


def test_project_phase_is_phase9a_price_plan_foundation() -> None:
    assert constants.PROJECT_PHASE == "phase_10_2_market_state"
