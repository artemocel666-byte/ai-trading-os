from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.core import constants
from app.domain.analysis_engine import AnalysisEngine
from app.domain.entities import Candle, Timeframe
from app.domain.entities.analysis import AnalysisSnapshot
from app.domain.value_objects import CurrencyPair
from app.schemas.agents import AgentReport, AnalysisAgent

PAIR = CurrencyPair(value="EURUSD")
BASE_TIME = datetime(2026, 7, 15, 8, 0, tzinfo=UTC)


def _candle(index: int) -> Candle:
    step = timedelta(minutes=15)
    open_time = BASE_TIME + (index * step)
    open_price = Decimal("1.1000") + (Decimal("0.0001") * Decimal(index))
    close_price = open_price + Decimal("0.0001")
    return Candle(
        provider="versioning-test",
        pair=PAIR,
        timeframe=Timeframe.M15,
        open_time=open_time,
        close_time=open_time + step,
        open=open_price,
        high=close_price + Decimal("0.0002"),
        low=open_price - Decimal("0.0002"),
        close=close_price,
        volume=Decimal("100"),
        is_closed=True,
    )


def _snapshot(candle_count: int) -> AnalysisSnapshot:
    candles = [_candle(index) for index in range(candle_count)]
    return AnalysisEngine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=BASE_TIME,
        window_end=BASE_TIME + timedelta(minutes=15 * candle_count),
        as_of=BASE_TIME + timedelta(minutes=15 * candle_count),
        candles=candles,
        economic_events=[],
        moving_average_windows=(3,),
    )


def test_snapshot_metadata_carries_schema_version() -> None:
    snapshot = _snapshot(3)

    assert snapshot.metadata.schema_version == constants.ANALYSIS_SNAPSHOT_SCHEMA_VERSION
    assert snapshot.feature_snapshot is not None
    assert snapshot.feature_snapshot.schema_version == constants.FEATURE_SNAPSHOT_SCHEMA_VERSION
    assert snapshot.context_snapshot is not None
    assert snapshot.context_snapshot.schema_version == constants.CONTEXT_SNAPSHOT_SCHEMA_VERSION


def test_data_completeness_ratio_is_bounded_and_deterministic() -> None:
    first = _snapshot(3)
    second = _snapshot(3)

    assert first.feature_snapshot is not None
    assert Decimal("0") <= first.feature_snapshot.data_completeness_ratio <= Decimal("1")
    assert (
        first.feature_snapshot.data_completeness_ratio
        == second.feature_snapshot.data_completeness_ratio
    )
    assert first.context_snapshot is not None
    assert (
        first.context_snapshot.data_completeness_ratio
        == first.feature_snapshot.data_completeness_ratio
    )


def test_data_completeness_ratio_reflects_missing_candles() -> None:
    full = _snapshot(3)
    partial = AnalysisEngine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=BASE_TIME,
        window_end=BASE_TIME + timedelta(minutes=45),
        as_of=BASE_TIME + timedelta(minutes=45),
        candles=[_candle(0)],
        economic_events=[],
        moving_average_windows=(3,),
    )

    assert full.feature_snapshot is not None
    assert partial.feature_snapshot is not None
    assert (
        partial.feature_snapshot.data_completeness_ratio
        < full.feature_snapshot.data_completeness_ratio
    )


def test_candle_summary_records_used_candle_evidence_timestamps() -> None:
    snapshot = _snapshot(3)

    candle_summary = snapshot.feature_snapshot.candle_summary
    assert len(candle_summary.used_candle_open_times) == candle_summary.used_candle_count
    assert len(candle_summary.used_candle_close_times) == candle_summary.used_candle_count
    assert candle_summary.used_candle_open_times == tuple(
        sorted(candle_summary.used_candle_open_times)
    )


def test_analysis_agent_protocol_is_structurally_satisfiable() -> None:
    class _StubAgent:
        def evaluate(self, snapshot: AnalysisSnapshot) -> AgentReport:
            raise NotImplementedError

    agent: AnalysisAgent = _StubAgent()

    assert hasattr(agent, "evaluate")
