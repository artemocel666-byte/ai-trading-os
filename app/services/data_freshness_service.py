"""Read what is stored, judge it against the calendar, and complain where it will be seen.

Phase 10-1. The domain decides what stale means; this reads storage and routes the answer. The
split is the same one every other service here keeps: `app/domain/data_freshness.py` has no session
and no query, and this has no calendar arithmetic.

**It complains through the existing error path on purpose.** A freshness script nobody runs is the
same silent rot in a new place — the failure Phase 9D-1 paid a day for, where a fill reported
success on holed data and only a hand check found it. Recording a `MarketDataStaleError` puts the
condition on a surface that is already watched, without inventing a surface to watch.
"""

import logging

from app.core.exceptions import MarketDataStaleError
from app.core.time import utc_now
from app.domain.data_freshness import build_freshness_report
from app.domain.entities.data_freshness import DEFAULT_TOLERANCE_BARS, FreshnessReport
from app.domain.entities.market_data import Timeframe
from app.domain.interfaces.unit_of_work import UnitOfWorkFactory
from app.services.system_state_service import SystemStateService

logger = logging.getLogger(__name__)


class DataFreshnessService:
    def __init__(
        self,
        *,
        uow_factory: UnitOfWorkFactory,
        system_state_service: SystemStateService,
        tolerance_bars: int = DEFAULT_TOLERANCE_BARS,
    ) -> None:
        self._uow_factory = uow_factory
        self._system_state_service = system_state_service
        self._tolerance_bars = tolerance_bars

    async def check(
        self,
        *,
        timeframe: Timeframe,
        instruments: tuple[str, ...],
        provider: str | None = None,
    ) -> FreshnessReport:
        """Judge every named instrument and record a system error if any is behind.

        `instruments` is passed in rather than discovered from storage, so a pair that has never
        been stored still appears — as `ABSENT`. Reading the list off the candles table instead
        would make a series that vanished entirely look like a series that was never asked for.
        """
        as_of = utc_now()
        async with self._uow_factory() as uow:
            newest = await uow.candles.newest_close_times(timeframe=timeframe, provider=provider)

        report = build_freshness_report(
            {instrument: newest.get(instrument) for instrument in instruments},
            timeframe=timeframe,
            as_of=as_of,
            tolerance_bars=self._tolerance_bars,
        )

        logger.info(
            "data_freshness_checked",
            extra={
                "timeframe": timeframe.value,
                "fresh": report.fresh_count,
                "stale": report.stale_count,
                "absent": report.absent_count,
                "undetermined": report.undetermined_count,
            },
        )
        if not report.is_healthy:
            await self._record(report, timeframe=timeframe)
        return report

    async def _record(self, report: FreshnessReport, *, timeframe: Timeframe) -> None:
        worst = report.worst_gap
        # Only the worst few are named. A message that lists forty-five pairs is a message nobody
        # finishes reading, and the count carries the scale.
        offenders = ", ".join(reading.instrument for reading in report.stale[:5])
        await self._system_state_service.record_system_error(
            MarketDataStaleError(
                "Исторические данные отстали от ожидаемых.",
                details={
                    "timeframe": timeframe.value,
                    "stale_count": report.stale_count,
                    "undetermined_count": report.undetermined_count,
                    "absent_count": report.absent_count,
                    "worst_gap_hours": None if worst is None else worst.total_seconds() / 3600,
                    "worst_offenders": offenders,
                },
            ),
            component="data_freshness",
        )
