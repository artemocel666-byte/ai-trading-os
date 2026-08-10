from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.entities import Candle, Timeframe
from app.domain.entities.forward_outcome import (
    ForwardOutcomeConfig,
    ForwardOutcomeRecord,
    ForwardOutcomeRecordResult,
    ForwardOutcomeResolveResult,
    ForwardOutcomeTickReason,
)
from app.domain.entities.outcome import OutcomeKind
from app.domain.entities.pipeline_decision import PipelineDecisionStatus
from app.domain.entities.readiness import SnapshotScheduleItem
from app.domain.entities.signal_contract import SignalDirection, SignalPricePlan
from app.domain.outcome_measurement import measure_outcome
from app.domain.value_objects import CurrencyPair
from app.services.forward_outcome_service import ForwardOutcomeService
from app.services.system_state_service import SystemStateService
from tests.fakes import FakeUnitOfWorkFactory

PAIR = CurrencyPair(value="EURUSD")
STEP = timedelta(minutes=15)
#: A Wednesday, so the market-open rule passes and the window is a real sample rather than filler.
BASE_TIME = datetime(2026, 7, 22, 8, 0, tzinfo=UTC)
WINDOW_CANDLES = 12
#: One minute past the close of the twelfth candle: the moment a 15-minute tick would fire.
FIRST_AS_OF = BASE_TIME + (WINDOW_CANDLES * STEP)


def _candle(index: int, *, base: Decimal, provider: str = "twelve_data") -> Candle:
    open_time = BASE_TIME + (index * STEP)
    return Candle(
        provider=provider,
        pair=PAIR,
        timeframe=Timeframe.M15,
        open_time=open_time,
        close_time=open_time + STEP,
        open=base,
        high=base + Decimal("0.00040"),
        low=base - Decimal("0.00040"),
        close=base + Decimal("0.00010"),
        volume=Decimal("100"),
        is_closed=True,
    )


def _window_candles(*, provider: str = "twelve_data") -> list[Candle]:
    """Twelve candles that drift gently upward, so the window has a usable average true range."""
    return [
        _candle(index, base=Decimal("1.10000") + (Decimal("0.00020") * index), provider=provider)
        for index in range(WINDOW_CANDLES)
    ]


def _quiet_forward(count: int, *, start_index: int = WINDOW_CANDLES) -> list[Candle]:
    """Candles after the window that touch neither level, so nothing resolves early."""
    return [_candle(start_index + offset, base=Decimal("1.10220")) for offset in range(count)]


def _service(
    *,
    candles: list[Candle],
    enabled: bool = True,
    horizon_candles: int = 4,
) -> tuple[ForwardOutcomeService, FakeUnitOfWorkFactory]:
    uow_factory = FakeUnitOfWorkFactory(candles=candles)
    config = ForwardOutcomeConfig(
        enabled=enabled,
        window_candles=WINDOW_CANDLES,
        horizon_candles=horizon_candles,
        items=(
            SnapshotScheduleItem(
                pair=PAIR,
                timeframe=Timeframe.M15,
                lookback_candle_count=WINDOW_CANDLES,
            ),
        ),
    )
    service = ForwardOutcomeService(
        config=config,
        uow_factory=uow_factory,
        system_state_service=SystemStateService(uow_factory),
    )
    return service, uow_factory


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_8d_local_explainer_foundation"


# --- the entity's two lifetimes -------------------------------------------------------------


def _record(**overrides: object) -> ForwardOutcomeRecord:
    fields: dict[str, object] = {
        "pair": PAIR,
        "timeframe": Timeframe.M15,
        "as_of": FIRST_AS_OF,
        "direction": SignalDirection.LONG,
        "anchor_price": Decimal("1.10000"),
        "entry_min": Decimal("1.09990"),
        "entry_max": Decimal("1.10010"),
        "stop_loss": Decimal("1.09800"),
        "take_profit_1": Decimal("1.10300"),
        "decision_status": PipelineDecisionStatus.READY_FOR_REVIEW,
        "pipeline_version": "test-pipeline-v1",
        "decision_fingerprint": "a" * 64,
        "entry_band_multiplier": Decimal("0.10"),
        "stop_multiplier": Decimal("1.5"),
        "target_multiplier": Decimal("2.0"),
        "horizon_candles": 24,
        "recorded_at": FIRST_AS_OF,
    }
    fields.update(overrides)
    return ForwardOutcomeRecord.model_validate(fields)


def test_a_fresh_record_is_pending_and_carries_no_outcome() -> None:
    record = _record()

    assert record.is_pending is True
    assert record.outcome_kind is None
    assert record.resolved_at is None


def test_a_pending_record_cannot_carry_a_resolution() -> None:
    with pytest.raises(ValidationError):
        _record(bars_to_resolution=3)


def test_a_settled_record_must_report_when_it_was_settled() -> None:
    with pytest.raises(ValidationError):
        _record(outcome_kind=OutcomeKind.TARGET_FIRST, bars_to_resolution=3)


def test_a_settled_outcome_must_report_the_bar_that_resolved_it() -> None:
    with pytest.raises(ValidationError):
        _record(
            outcome_kind=OutcomeKind.TARGET_FIRST,
            resolved_at=FIRST_AS_OF + STEP,
        )


def test_a_timeout_is_settled_without_a_resolution_bar() -> None:
    """TIMEOUT is an answer, not an absence, and it is the one settled kind with no bar."""
    record = _record(outcome_kind=OutcomeKind.TIMEOUT, resolved_at=FIRST_AS_OF + STEP)

    assert record.is_pending is False
    assert record.bars_to_resolution is None


def test_the_anchor_must_lie_inside_its_own_entry_band() -> None:
    with pytest.raises(ValidationError):
        _record(anchor_price=Decimal("1.10500"))


def test_a_window_cannot_be_recorded_before_the_moment_it_describes() -> None:
    with pytest.raises(ValidationError):
        _record(recorded_at=FIRST_AS_OF - STEP)


def test_a_settled_result_must_account_for_every_examined_record() -> None:
    with pytest.raises(ValidationError):
        ForwardOutcomeResolveResult(
            as_of=FIRST_AS_OF,
            executed=True,
            reason=ForwardOutcomeTickReason.COMPLETED,
            examined_count=5,
            resolved_count=1,
            still_pending_count=1,
        )


def test_a_tick_that_did_not_execute_cannot_claim_completion() -> None:
    with pytest.raises(ValidationError):
        ForwardOutcomeRecordResult(
            as_of=FIRST_AS_OF,
            executed=False,
            reason=ForwardOutcomeTickReason.COMPLETED,
        )


# --- recording -------------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_recording_writes_both_directions_with_no_outcome_yet() -> None:
    service, uow_factory = _service(candles=_window_candles())

    result = await service.run_record_tick(as_of=FIRST_AS_OF)

    assert result.executed is True
    assert result.recorded_count == 2
    stored = list(uow_factory.forward_outcomes.values())
    assert {record.direction for record in stored} == {
        SignalDirection.LONG,
        SignalDirection.SHORT,
    }
    assert all(record.is_pending for record in stored)
    assert all(record.as_of == FIRST_AS_OF for record in stored)


@pytest.mark.asyncio
async def test_recording_stores_what_the_rules_said_about_the_window() -> None:
    service, uow_factory = _service(candles=_window_candles())

    await service.run_record_tick(as_of=FIRST_AS_OF)

    stored = next(iter(uow_factory.forward_outcomes.values()))
    assert stored.decision_status in tuple(PipelineDecisionStatus)
    assert stored.market_open is True
    assert stored.ruleset_versions
    assert len(stored.decision_fingerprint) == 64
    assert stored.horizon_candles == 4


@pytest.mark.asyncio
async def test_recording_the_same_window_twice_writes_one_row_per_direction() -> None:
    """The overlapping worker cadence must not be able to double-register a window."""
    service, uow_factory = _service(candles=_window_candles())

    first = await service.run_record_tick(as_of=FIRST_AS_OF)
    second = await service.run_record_tick(as_of=FIRST_AS_OF + timedelta(minutes=1))

    assert first.recorded_count == 2
    assert second.recorded_count == 0
    assert second.already_present_count == 2
    assert len(uow_factory.forward_outcomes) == 2


@pytest.mark.asyncio
async def test_a_registered_plan_is_not_rewritten_by_a_later_tick() -> None:
    service, uow_factory = _service(candles=_window_candles())
    await service.run_record_tick(as_of=FIRST_AS_OF)
    before = {key: record.stop_loss for key, record in uow_factory.forward_outcomes.items()}

    await service.run_record_tick(as_of=FIRST_AS_OF + timedelta(minutes=1))

    after = {key: record.stop_loss for key, record in uow_factory.forward_outcomes.items()}
    assert after == before


@pytest.mark.asyncio
async def test_recording_ignores_rows_no_real_provider_supplied() -> None:
    """The provenance guard `scripts/replay_rules.py` has offline, applied to the live path.

    A window built from seeded candles would look pre-registered while quoting invented prices,
    which is worse than no row at all.
    """
    service, uow_factory = _service(candles=_window_candles(provider="local-seed"))

    result = await service.run_record_tick(as_of=FIRST_AS_OF)

    assert result.recorded_count == 0
    # Counted as "no data" rather than "no plan": after the provenance filter there is nothing to
    # build a window from, which is a different thing from a market too flat to place levels on.
    assert result.windows_without_data == 2
    assert result.windows_without_a_plan == 0
    assert uow_factory.forward_outcomes == {}


@pytest.mark.asyncio
async def test_the_window_follows_the_stored_data_rather_than_the_clock() -> None:
    """A tick that fires before ingestion has stored the candle just closed must not be short.

    Both jobs run on the same interval and fire in the same second, so on 2026-08-10 every live
    row came out one candle short and `market_data_complete` failed on all of them — the verdict
    column, which is the reason the ledger stores a verdict at all, was recording a race rather
    than a market. The window now ends at the newest stored candle.
    """
    service, uow_factory = _service(candles=_window_candles())

    # One full interval past the window's own close: the clock says a newer window exists, and
    # ingestion has not stored a single candle of it.
    result = await service.run_record_tick(as_of=FIRST_AS_OF + STEP)

    assert result.recorded_count == 2
    stored = list(uow_factory.forward_outcomes.values())
    assert {record.as_of for record in stored} == {FIRST_AS_OF}
    assert all(
        record.decision_status == PipelineDecisionStatus.READY_FOR_REVIEW for record in stored
    )
    assert all(record.failed_rule_ids == () for record in stored)


@pytest.mark.asyncio
async def test_a_series_with_nothing_stored_records_nothing() -> None:
    service, uow_factory = _service(candles=[])

    result = await service.run_record_tick(as_of=FIRST_AS_OF)

    assert result.recorded_count == 0
    assert result.windows_without_data == 2
    assert uow_factory.forward_outcomes == {}


@pytest.mark.asyncio
async def test_a_window_skipped_this_tick_is_recorded_on_the_next_one() -> None:
    """Lagging ingestion delays a window; it does not lose one.

    The identity a row would be stored under does not depend on when the tick ran, so the later
    tick writes exactly the row the earlier one could not.
    """
    candles = _window_candles()
    service, uow_factory = _service(candles=candles)
    await service.run_record_tick(as_of=FIRST_AS_OF)
    assert {record.as_of for record in uow_factory.forward_outcomes.values()} == {FIRST_AS_OF}

    candles.append(_candle(WINDOW_CANDLES, base=Decimal("1.10240")))
    result = await service.run_record_tick(as_of=FIRST_AS_OF + (2 * STEP))

    assert result.recorded_count == 2
    assert {record.as_of for record in uow_factory.forward_outcomes.values()} == {
        FIRST_AS_OF,
        FIRST_AS_OF + STEP,
    }


@pytest.mark.asyncio
async def test_recording_is_skipped_while_disabled() -> None:
    service, uow_factory = _service(candles=_window_candles(), enabled=False)

    result = await service.run_record_tick(as_of=FIRST_AS_OF)

    assert result.executed is False
    assert result.reason == ForwardOutcomeTickReason.DISABLED
    assert uow_factory.forward_outcomes == {}


# --- resolution ------------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_resolution_leaves_a_record_pending_until_its_horizon_has_elapsed() -> None:
    """Writing TIMEOUT early would turn a gap in ingestion into a measured result."""
    candles = _window_candles() + _quiet_forward(2)
    service, uow_factory = _service(candles=candles, horizon_candles=4)
    await service.run_record_tick(as_of=FIRST_AS_OF)

    result = await service.run_resolve_tick(as_of=FIRST_AS_OF + (2 * STEP))

    assert result.examined_count == 2
    assert result.resolved_count == 0
    assert result.still_pending_count == 2
    assert all(record.is_pending for record in uow_factory.forward_outcomes.values())


@pytest.mark.asyncio
async def test_a_full_horizon_without_a_touch_settles_as_timeout() -> None:
    candles = _window_candles() + _quiet_forward(4)
    service, uow_factory = _service(candles=candles, horizon_candles=4)
    await service.run_record_tick(as_of=FIRST_AS_OF)

    result = await service.run_resolve_tick(as_of=FIRST_AS_OF + (4 * STEP))

    assert result.resolved_count == 2
    assert {record.outcome_kind for record in uow_factory.forward_outcomes.values()} == {
        OutcomeKind.TIMEOUT
    }


@pytest.mark.asyncio
async def test_resolution_matches_measuring_the_same_slice_by_hand() -> None:
    """The ledger and `scripts/measure_outcomes.py` must not be able to disagree.

    They share `measure_outcome`, so this asserts the thing that could still drift: which candles
    each one calls "after the window". Strictly after `as_of`, in both.
    """
    reaching = [
        _candle(WINDOW_CANDLES, base=Decimal("1.10220")),
        _candle(WINDOW_CANDLES + 1, base=Decimal("1.10600")),
        _candle(WINDOW_CANDLES + 2, base=Decimal("1.10620")),
        _candle(WINDOW_CANDLES + 3, base=Decimal("1.10640")),
    ]
    service, uow_factory = _service(candles=_window_candles() + reaching, horizon_candles=4)
    await service.run_record_tick(as_of=FIRST_AS_OF)

    await service.run_resolve_tick(as_of=FIRST_AS_OF + (4 * STEP))

    for record in uow_factory.forward_outcomes.values():
        expected = measure_outcome(
            record.direction,
            SignalPricePlan(
                entry_min=record.entry_min,
                entry_max=record.entry_max,
                stop_loss=record.stop_loss,
                take_profit_1=record.take_profit_1,
            ),
            [candle for candle in reaching if candle.close_time > record.as_of],
            horizon_candles=record.horizon_candles,
        )
        assert record.outcome_kind == expected.kind
        assert record.bars_to_resolution == expected.bars_to_resolution


@pytest.mark.asyncio
async def test_a_settled_record_is_never_settled_again() -> None:
    """A second look at the same future would be a second answer to a question already answered."""
    candles = _window_candles() + _quiet_forward(4)
    service, uow_factory = _service(candles=candles, horizon_candles=4)
    await service.run_record_tick(as_of=FIRST_AS_OF)
    await service.run_resolve_tick(as_of=FIRST_AS_OF + (4 * STEP))
    settled_at = {key: record.resolved_at for key, record in uow_factory.forward_outcomes.items()}

    again = await service.run_resolve_tick(as_of=FIRST_AS_OF + (8 * STEP))

    assert again.examined_count == 0
    assert again.resolved_count == 0
    assert {
        key: record.resolved_at for key, record in uow_factory.forward_outcomes.items()
    } == settled_at


@pytest.mark.asyncio
async def test_resolution_is_skipped_while_disabled() -> None:
    service, _ = _service(candles=_window_candles(), enabled=False)

    result = await service.run_resolve_tick(as_of=FIRST_AS_OF + (4 * STEP))

    assert result.executed is False
    assert result.reason == ForwardOutcomeTickReason.DISABLED


@pytest.mark.asyncio
async def test_recording_never_writes_a_candle() -> None:
    """The ledger reads market data and may not change it."""
    candles = _window_candles()
    service, uow_factory = _service(candles=candles)

    await service.run_record_tick(as_of=FIRST_AS_OF)
    await service.run_resolve_tick(as_of=FIRST_AS_OF + (4 * STEP))

    assert uow_factory.candles == candles
