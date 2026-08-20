"""Write plans down before their outcomes exist, and settle them afterwards.

Two ticks, deliberately separate. `run_record_tick` builds a window, asks the rules what they think
of it, fixes the levels for both directions, and stores the row. `run_resolve_tick` reads rows that
are already stored and looks at candles that arrived later.

**The separation is the safety property, not a convenience.** Recording never reads a forward
candle because it never queries past its own `as_of`; resolution never influences a plan because
every plan it touches was fixed on an earlier tick. The Phase 3D invariant — nothing after `as_of`
may reach a decision — is here enforced by which tick owns which query, rather than by remembering.

This is the only service permitted to reach `build_price_plan` or `measure_outcome`, and safety
tests name it. It chooses no direction: both are recorded for every window, exactly as
`scripts/measure_outcomes.py` measures both. It computes no account, no size, and no cost.
"""

from collections.abc import Sequence
from datetime import datetime

from app.core.constants import REAL_MARKET_DATA_PROVIDERS
from app.core.exceptions import ApplicationError, ErrorCode, ProviderError
from app.domain.analysis_engine import AnalysisEngine
from app.domain.entities.analysis import AnalysisSnapshot
from app.domain.entities.data_quality import TIMEFRAME_TO_DELTA
from app.domain.entities.forward_outcome import (
    MARKET_OPEN_RULE_ID,
    ForwardOutcomeConfig,
    ForwardOutcomeRecord,
    ForwardOutcomeRecordResult,
    ForwardOutcomeResolveResult,
    ForwardOutcomeTickReason,
)
from app.domain.entities.market_data import Candle, Timeframe
from app.domain.entities.outcome import RESOLVED_KINDS
from app.domain.entities.pipeline_decision import PipelineDecisionReport
from app.domain.entities.readiness import SnapshotScheduleItem
from app.domain.entities.rule_evaluation import RuleEvaluationStatus
from app.domain.entities.signal_contract import SignalDirection, SignalPricePlan
from app.domain.interfaces.unit_of_work import UnitOfWorkFactory
from app.domain.outcome_measurement import measure_outcome
from app.domain.readiness_engine import latest_closed_boundary
from app.domain.signal_price_plan import LevelMultipliers, build_price_plan
from app.domain.snapshot_review import build_snapshot_backed_review
from app.domain.value_objects import CurrencyPair
from app.services.system_state_service import SystemStateService

FORWARD_OUTCOME_COMPONENT = "forward_outcome_ledger"


class ForwardOutcomeService:
    """The forward ledger's two ticks.

    Read-only with respect to market data: it never writes a candle or an event, and a safety test
    asserts it. The only table it writes is its own.
    """

    def __init__(
        self,
        *,
        config: ForwardOutcomeConfig,
        uow_factory: UnitOfWorkFactory,
        system_state_service: SystemStateService,
        multipliers: LevelMultipliers | None = None,
        analysis_engine: AnalysisEngine | None = None,
    ) -> None:
        self._config = config
        self._uow_factory = uow_factory
        self._system_state_service = system_state_service
        self._analysis_engine = analysis_engine or AnalysisEngine()
        # `target_2` is dropped: which level is reached first cannot depend on a level nothing
        # measures, and carrying the default would make a raised `target_1` fail validation.
        defaults = multipliers or LevelMultipliers()
        self._multipliers = LevelMultipliers(
            entry_band=defaults.entry_band,
            stop=defaults.stop,
            target_1=defaults.target_1,
            target_2=None,
        )

    async def run_record_tick(self, *, as_of: datetime) -> ForwardOutcomeRecordResult:
        reason = self._tick_reason()
        if reason is not ForwardOutcomeTickReason.COMPLETED:
            return ForwardOutcomeRecordResult(as_of=as_of, executed=False, reason=reason)

        considered = 0
        recorded = 0
        already_present = 0
        without_a_plan = 0
        without_data = 0
        failed_items = 0

        for item in self._config.items:
            try:
                snapshot = await self._snapshot(item=item, as_of=as_of)
            except Exception as error:  # one bad series must not stop the rest
                await self._record_failure(error, item=item)
                failed_items += 1
                continue
            if snapshot is None:
                # Nothing stored for this series at all. Counted apart from a flat window: one is
                # a market that said nothing, the other is an ingestion that fetched nothing, and
                # a single counter for both would make the ledger's own diagnostics lie.
                without_data += len(SignalDirection)
                continue
            records = self._records_for_snapshot(item=item, snapshot=snapshot, recorded_at=as_of)
            if records is None:
                without_a_plan += len(SignalDirection)
                continue
            considered += len(records)
            async with self._uow_factory() as uow:
                inserted = await uow.forward_outcomes.add_missing(records)
                await uow.commit()
            recorded += inserted
            already_present += len(records) - inserted

        return ForwardOutcomeRecordResult(
            as_of=as_of,
            executed=True,
            reason=ForwardOutcomeTickReason.COMPLETED,
            item_count=len(self._config.items),
            considered_count=considered,
            recorded_count=recorded,
            already_present_count=already_present,
            windows_without_a_plan=without_a_plan,
            windows_without_data=without_data,
            failed_item_count=failed_items,
        )

    async def run_resolve_tick(self, *, as_of: datetime) -> ForwardOutcomeResolveResult:
        reason = self._tick_reason()
        if reason is not ForwardOutcomeTickReason.COMPLETED:
            return ForwardOutcomeResolveResult(as_of=as_of, executed=False, reason=reason)

        async with self._uow_factory() as uow:
            pending = await uow.forward_outcomes.list_pending(
                limit=self._config.resolve_batch_size,
                as_of_at_or_before=as_of,
            )

        settled: list[ForwardOutcomeRecord] = []
        for (pair, timeframe), group in _grouped_by_series(pending).items():
            forward_candles = await self._forward_candles(
                pair=pair,
                timeframe=timeframe,
                earliest_as_of=min(record.as_of for record in group),
                as_of=as_of,
            )
            for record in group:
                resolved = _settle(record, forward_candles, resolved_at=as_of)
                if resolved is not None:
                    settled.append(resolved)

        applied = 0
        if settled:
            async with self._uow_factory() as uow:
                applied = await uow.forward_outcomes.apply_outcomes(settled)
                await uow.commit()

        return ForwardOutcomeResolveResult(
            as_of=as_of,
            executed=True,
            reason=ForwardOutcomeTickReason.COMPLETED,
            examined_count=len(pending),
            resolved_count=applied,
            still_pending_count=len(pending) - applied,
        )

    def _records_for_snapshot(
        self,
        *,
        item: SnapshotScheduleItem,
        snapshot: AnalysisSnapshot,
        recorded_at: datetime,
    ) -> list[ForwardOutcomeRecord] | None:
        window_end = snapshot.window.as_of
        review = build_snapshot_backed_review(snapshot, window_end)
        decision = review.decision

        records: list[ForwardOutcomeRecord] = []
        for direction in SignalDirection:
            plan = build_price_plan(direction, snapshot, multipliers=self._multipliers)
            if plan is None:
                # A flat or incomplete window has no scale to place levels on. Both directions are
                # dropped, not just this one: half a window would make the pooled benchmark — both
                # directions over the same windows — quietly stop being over the same windows.
                return None
            records.append(
                self._record(
                    item=item,
                    as_of=window_end,
                    direction=direction,
                    snapshot=snapshot,
                    decision=decision,
                    plan=plan,
                    recorded_at=recorded_at,
                )
            )
        return records

    async def _snapshot(
        self,
        *,
        item: SnapshotScheduleItem,
        as_of: datetime,
    ) -> AnalysisSnapshot | None:
        """The newest window the stored data can actually support, or `None` if there is none.

        **The window ends at the newest stored candle, not at the newest closed boundary.** Both
        this tick and market-data ingestion run on the same interval and fire in the same second,
        so asking the clock produced a window whose last candle had not been fetched yet — one
        short, every single time. Run live on 2026-08-10 that made `market_data_complete` fail on
        every row, and the ledger's whole point is the verdict stored beside the outcome.

        Reading the boundary off the data instead of the clock cannot race: it is behind by however
        much ingestion is behind, and no more. A window skipped this tick is recorded on the next
        one, because the identity it would be stored under has not changed.

        The candle query is filtered by provenance rather than trusted. On 2026-08-07 thirty
        fabricated rows were found sitting on the same timestamps as real ones and winning the
        de-duplication every time; `scripts/replay_rules.py` gained a hard guard for the offline
        path, and this is the same guard on the live one. A ledger row built over an invented price
        would be worse than a missing one, because it would look pre-registered.
        """
        pair = item.pair
        timeframe = item.timeframe
        step = TIMEFRAME_TO_DELTA[timeframe]
        boundary = latest_closed_boundary(timeframe=timeframe, as_of=as_of)
        # Twice the window, so ingestion can be a long way behind and the newest window it does
        # support is still fully covered by one query.
        search_start = boundary - (2 * self._config.window_candles * step)

        async with self._uow_factory() as uow:
            stored = _only_real(
                await uow.candles.list_range(
                    pair=pair,
                    timeframe=timeframe,
                    start_at=search_start,
                    end_at=boundary,
                )
            )
            if not stored:
                return None
            window_end = max(candle.close_time for candle in stored)
            window_start = window_end - (self._config.window_candles * step)
            events = await uow.economic_events.list_window(
                start_at=window_start,
                end_at=window_end,
                currencies=[pair.base_currency, pair.quote_currency],
            )

        candles = [
            candle
            for candle in stored
            if candle.open_time >= window_start and candle.close_time <= window_end
        ]
        return self._analysis_engine.build_snapshot(
            pair=pair,
            timeframe=timeframe,
            window_start=window_start,
            window_end=window_end,
            as_of=window_end,
            candles=candles,
            economic_events=events,
            currencies=[pair.base_currency, pair.quote_currency],
        )

    async def _forward_candles(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        earliest_as_of: datetime,
        as_of: datetime,
    ) -> list[Candle]:
        """Every stored candle after the oldest pending window, oldest first.

        The slice each record uses is taken from this series by `_settle`, using the same rule as
        `scripts/measure_outcomes.py`: strictly after the window's own `as_of`, so nothing the plan
        was built from can be measured as its own outcome.
        """
        async with self._uow_factory() as uow:
            candles = await uow.candles.list_range(
                pair=pair,
                timeframe=timeframe,
                start_at=earliest_as_of,
                end_at=as_of,
            )
        return sorted(
            _only_real(candles),
            key=lambda candle: (candle.open_time, candle.provider),
        )

    def _record(
        self,
        *,
        item: SnapshotScheduleItem,
        as_of: datetime,
        direction: SignalDirection,
        snapshot: AnalysisSnapshot,
        decision: PipelineDecisionReport,
        plan: SignalPricePlan,
        recorded_at: datetime,
    ) -> ForwardOutcomeRecord:
        anchor = (plan.entry_min + plan.entry_max) / 2
        return ForwardOutcomeRecord(
            pair=item.pair,
            timeframe=item.timeframe,
            as_of=as_of,
            direction=direction,
            anchor_price=anchor,
            entry_min=plan.entry_min,
            entry_max=plan.entry_max,
            stop_loss=plan.stop_loss,
            take_profit_1=plan.take_profit_1,
            decision_status=decision.status,
            market_open=_market_open(decision),
            failed_rule_ids=_failed_rule_ids(decision),
            pipeline_version=decision.pipeline_version,
            ruleset_versions=tuple(
                f"{report.ruleset_name}:{report.ruleset_version}"
                for report in decision.ruleset_reports
            ),
            decision_fingerprint=decision.fingerprint_sha256(),
            entry_band_multiplier=self._multipliers.entry_band,
            stop_multiplier=self._multipliers.stop,
            target_multiplier=self._multipliers.target_1,
            horizon_candles=self._config.horizon_candles,
            project_phase=snapshot.metadata.project_phase,
            recorded_at=recorded_at,
        )

    def _tick_reason(self) -> ForwardOutcomeTickReason:
        if not self._config.enabled:
            return ForwardOutcomeTickReason.DISABLED
        if not self._config.items:
            return ForwardOutcomeTickReason.NO_ITEMS
        return ForwardOutcomeTickReason.COMPLETED

    async def _record_failure(self, error: Exception, *, item: SnapshotScheduleItem) -> None:
        application_error = (
            error
            if isinstance(error, ApplicationError)
            else ProviderError(
                ErrorCode.PROVIDER_UNAVAILABLE,
                "Не удалось записать окно в журнал исходов.",  # noqa: RUF001
                details={"pair": item.pair.value, "timeframe": item.timeframe.value},
            )
        )
        await self._system_state_service.record_system_error(
            application_error,
            component=FORWARD_OUTCOME_COMPONENT,
            technical_details=f"{type(error).__name__}: {error}",
        )


def _settle(
    record: ForwardOutcomeRecord,
    series: Sequence[Candle],
    *,
    resolved_at: datetime,
) -> ForwardOutcomeRecord | None:
    """The record with its outcome written, or `None` while it is still too early to say.

    A plan whose horizon has not elapsed is left pending. Writing `TIMEOUT` because candles had not
    arrived yet would turn a gap in ingestion into a measured result, which is exactly the confusion
    the stored history was found to contain in Phase 9A-5.
    """
    forward = [candle for candle in series if candle.close_time > record.as_of]
    if not forward:
        return None

    outcome = measure_outcome(
        record.direction,
        SignalPricePlan(
            entry_min=record.entry_min,
            entry_max=record.entry_max,
            stop_loss=record.stop_loss,
            take_profit_1=record.take_profit_1,
        ),
        forward,
        horizon_candles=record.horizon_candles,
    )
    if outcome.kind not in RESOLVED_KINDS and len(forward) < record.horizon_candles:
        return None

    # Rebuilt rather than copied, so the entity's own rules about the two lifetimes run again.
    # `model_copy` skips validation, and the one place a record changes shape is the one place that
    # can least afford to.
    return ForwardOutcomeRecord.model_validate(
        record.model_dump()
        | {
            "outcome_kind": outcome.kind,
            "bars_to_resolution": outcome.bars_to_resolution,
            "resolved_at": resolved_at,
        }
    )


def _grouped_by_series(
    records: Sequence[ForwardOutcomeRecord],
) -> dict[tuple[CurrencyPair, Timeframe], list[ForwardOutcomeRecord]]:
    grouped: dict[tuple[CurrencyPair, Timeframe], list[ForwardOutcomeRecord]] = {}
    for record in records:
        grouped.setdefault((record.pair, record.timeframe), []).append(record)
    return grouped


def _only_real(candles: Sequence[Candle]) -> list[Candle]:
    """Rows a real provider supplied. The `provider` column is the project's provenance record."""
    return [candle for candle in candles if candle.provider in REAL_MARKET_DATA_PROVIDERS]


def _market_open(decision: PipelineDecisionReport) -> bool | None:
    for report in decision.ruleset_reports:
        for result in report.results:
            if result.rule_id != MARKET_OPEN_RULE_ID:
                continue
            if result.status == RuleEvaluationStatus.UNAVAILABLE:
                return None
            return result.status == RuleEvaluationStatus.PASSED
    return None


def _failed_rule_ids(decision: PipelineDecisionReport) -> tuple[str, ...]:
    """Rules observed to be wrong on this window.

    `UNAVAILABLE` is not a failure and is deliberately absent: a rule that could not be evaluated
    said nothing, and listing it as a failure is the mistake Phase 9A-7 had to unpick after a rule
    was reported as "often firing" on 0.4% of the sample.
    """
    return tuple(
        result.rule_id
        for report in decision.ruleset_reports
        for result in report.results
        if result.status == RuleEvaluationStatus.FAILED
    )
