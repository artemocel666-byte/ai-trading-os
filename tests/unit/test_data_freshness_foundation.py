import time
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from pydantic import ValidationError

from app.adapters.twelve_data import TwelveDataMarketDataAdapter
from app.core import constants
from app.domain.data_freshness import build_freshness_report, expected_newest_close, read_freshness
from app.domain.entities.data_freshness import (
    FreshnessReading,
    FreshnessReport,
    FreshnessStatus,
)
from app.domain.entities.data_quality import TIMEFRAME_TO_DELTA
from app.domain.entities.market_data import Timeframe
from app.domain.readiness_engine import latest_closed_boundary

# 2026-08-18 is a Tuesday; 2026-08-22 a Saturday; 2026-08-23 a Sunday.
TUESDAY = datetime(2026, 8, 18, 14, 0, tzinfo=UTC)
SATURDAY = datetime(2026, 8, 22, 10, 0, tzinfo=UTC)
SUNDAY = datetime(2026, 8, 23, 10, 0, tzinfo=UTC)


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_10_1_live_universe"


def test_a_timeframe_cannot_be_half_added_to_the_boundary_either() -> None:
    """The 9D-1 fault, recurring in a sibling function, now closed at the root.

    `latest_closed_boundary` branched per timeframe and raised for anything it had not been told
    about, so D1 entering `TIMEFRAME_TO_DELTA` in Phase 9D-1 left it behind: every daily ingestion
    item would have failed here, before a request went out. Reading the delta map means a timeframe
    added there is answered here for free, and this asserts that for **every** member of the enum
    rather than for the three that exist today.
    """
    for timeframe in Timeframe:
        boundary = latest_closed_boundary(timeframe=timeframe, as_of=TUESDAY)
        delta = TIMEFRAME_TO_DELTA[timeframe]
        assert boundary <= TUESDAY
        assert TUESDAY - boundary < delta
        # Lands on the grid, not merely somewhere in the last bar.
        assert (boundary - datetime(1970, 1, 1, tzinfo=UTC)) % delta == timedelta(0)


def test_the_daily_boundary_is_the_start_of_today_in_utc() -> None:
    assert latest_closed_boundary(timeframe=Timeframe.D1, as_of=TUESDAY) == datetime(
        2026, 8, 18, tzinfo=UTC
    )


def test_the_weekend_expectation_is_fridays_bar() -> None:
    """Criterion 3: the alarm must stay silent on a weekend.

    A Friday daily bar closes at Saturday 00:00 UTC. Naively subtracting one day from "now" would
    call every pair a day stale from Saturday morning until Monday night — an alarm that cries every
    weekend is an alarm nobody reads by the second month.
    """
    friday_close = datetime(2026, 8, 22, tzinfo=UTC)

    assert expected_newest_close(timeframe=Timeframe.D1, as_of=SATURDAY) == friday_close
    assert expected_newest_close(timeframe=Timeframe.D1, as_of=SUNDAY) == friday_close


def _reading(newest: datetime | None, *, as_of: datetime = TUESDAY) -> FreshnessReading:
    return read_freshness(
        instrument="EURUSD",
        timeframe=Timeframe.D1,
        newest_close=newest,
        as_of=as_of,
    )


def test_a_series_holding_what_the_calendar_expects_is_fresh() -> None:
    assert _reading(datetime(2026, 8, 18, tzinfo=UTC)).status is FreshnessStatus.FRESH


def test_a_series_that_is_behind_is_reported_stale_with_its_gap() -> None:
    """Criterion 4, and the one that decides the slice.

    Every other criterion checks that the alarm stays quiet. A check that has never been seen to
    fire is not a check, so this stales a series deliberately and requires the report to say so and
    to say by how much.
    """
    reading = _reading(datetime(2026, 8, 10, tzinfo=UTC))

    assert reading.status is FreshnessStatus.STALE
    assert reading.behind == timedelta(days=8)


def test_a_series_that_never_existed_is_absent_rather_than_stale() -> None:
    """One of the forty-five derived pairs has never been quoted. It is not late; it is not there.

    Folding the two together would make the report complain every single day about a pair no
    provider offers, and the complaint would train its reader to ignore the real ones.
    """
    reading = _reading(None)

    assert reading.status is FreshnessStatus.ABSENT
    assert reading.behind is None


def test_one_bar_of_slack_is_allowed_and_two_are_not() -> None:
    """The threshold is named rather than buried: a provider publishes on its clock, not ours."""
    assert _reading(datetime(2026, 8, 17, tzinfo=UTC)).status is FreshnessStatus.FRESH
    assert _reading(datetime(2026, 8, 16, tzinfo=UTC)).status is FreshnessStatus.STALE


def test_a_gap_belongs_only_to_a_stale_reading() -> None:
    with pytest.raises(ValidationError):
        FreshnessReading(
            instrument="EURUSD",
            timeframe=Timeframe.D1,
            newest_close=TUESDAY,
            expected_close=TUESDAY,
            status=FreshnessStatus.FRESH,
            behind=timedelta(days=3),
        )
    with pytest.raises(ValidationError):
        FreshnessReading(
            instrument="EURUSD",
            timeframe=Timeframe.D1,
            newest_close=TUESDAY,
            expected_close=TUESDAY,
            status=FreshnessStatus.STALE,
        )


def test_an_absent_series_cannot_claim_a_newest_bar() -> None:
    with pytest.raises(ValidationError):
        FreshnessReading(
            instrument="EURUSD",
            timeframe=Timeframe.D1,
            newest_close=TUESDAY,
            expected_close=TUESDAY,
            status=FreshnessStatus.ABSENT,
        )


def test_a_report_counts_each_kind_apart_and_ranks_the_worst_first() -> None:
    report = build_freshness_report(
        {
            "EURUSD": datetime(2026, 8, 18, tzinfo=UTC),
            "GBPUSD": datetime(2026, 8, 10, tzinfo=UTC),
            "AUDUSD": datetime(2026, 8, 14, tzinfo=UTC),
            "NOKSEK": None,
        },
        timeframe=Timeframe.D1,
        as_of=TUESDAY,
    )

    assert report.fresh_count == 1
    assert report.stale_count == 2
    assert report.absent_count == 1
    assert [reading.instrument for reading in report.stale] == ["GBPUSD", "AUDUSD"]
    assert report.worst_gap == timedelta(days=8)
    assert report.is_healthy is False


def test_an_absence_alone_is_not_ill_health() -> None:
    """A pair the provider does not quote must not hold the report in a permanent alarm state."""
    report = build_freshness_report(
        {"EURUSD": datetime(2026, 8, 18, tzinfo=UTC), "NOKSEK": None},
        timeframe=Timeframe.D1,
        as_of=TUESDAY,
    )

    assert report.absent_count == 1
    assert report.is_healthy is True


def test_a_report_with_nothing_stale_has_no_worst_gap() -> None:
    report = FreshnessReport(as_of=TUESDAY, readings=())

    assert report.worst_gap is None
    assert report.is_healthy is True


@pytest.mark.asyncio
async def test_requests_are_held_apart_by_the_configured_interval() -> None:
    """Criterion 5. A pacing setting that is silently ignored is worse than none.

    It reads as protection while inviting the request count to be raised behind it, so the interval
    is measured rather than assumed present.
    """
    interval = 0.05
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"values": [], "status": "ok"})
    )
    adapter = TwelveDataMarketDataAdapter(
        client=httpx.AsyncClient(transport=transport),
        api_key="unused",
        base_url="https://example.invalid",
        timeout=httpx.Timeout(1.0),
        retry_count=0,
        retry_backoff_seconds=0.0,
        max_request_range=timedelta(days=90),
        min_request_interval_seconds=interval,
    )

    started = time.monotonic()
    for _ in range(3):
        await adapter._wait_for_turn()
    elapsed = time.monotonic() - started

    # Three turns means two waits; the first is free.
    assert elapsed >= 2 * interval


class _RecordingScheduler:
    """Captures how each job was registered, not merely that it was."""

    def __init__(self) -> None:
        self.jobs: dict[str, tuple[str, dict[str, object]]] = {}

    def add_job(self, _func: object, trigger: str, **kwargs: object) -> None:
        self.jobs[str(kwargs["id"])] = (trigger, kwargs)


def test_the_daily_sweep_is_registered_on_a_clock_not_on_an_interval() -> None:
    """Criterion 7, and the reason the whole slice would fail silently without it.

    There is no wall-clock gate inside the ingestion service - cadence is owned entirely by the
    trigger. A 1440-minute interval starts counting when the worker starts, so a worker restarted
    daily by a deploy, a crash or a closing laptop could go its whole life without the sweep firing
    once, and the failure would look exactly like nothing happening. A cron trigger fires on the
    clock regardless of when the process began.
    """
    from typing import cast

    from app.scheduler.jobs import register_jobs
    from app.services.data_freshness_service import DataFreshnessService
    from app.services.health_service import HealthService
    from app.services.interest_rate_ingestion_service import InterestRateIngestionService
    from app.services.market_data_ingestion_service import MarketDataIngestionService
    from app.services.system_state_service import SystemStateService

    scheduler = _RecordingScheduler()
    register_jobs(
        scheduler,
        system_state_service=cast(SystemStateService, object()),
        health_service=cast(HealthService, object()),
        daily_universe_ingestion_service=cast(MarketDataIngestionService, object()),
        data_freshness_service=cast(DataFreshnessService, object()),
        daily_universe_instruments=("EURUSD",),
        daily_universe_hour_utc=2,
        interest_rate_ingestion_service=cast(InterestRateIngestionService, object()),
        interest_rate_hour_utc=3,
    )

    trigger, kwargs = scheduler.jobs["daily_universe_ingestion"]
    assert trigger == "cron"
    assert kwargs["hour"] == 2
    assert kwargs["minute"] == 0
    assert kwargs["timezone"] == "UTC"

    rates_trigger, rates_kwargs = scheduler.jobs["interest_rate_ingestion"]
    assert rates_trigger == "cron"
    assert rates_kwargs["day_of_week"] == "sun"


def test_neither_scheduled_job_appears_when_its_service_is_absent() -> None:
    """Off by default, like every other ingestion path in this project."""
    from typing import cast

    from app.scheduler.jobs import register_jobs
    from app.services.health_service import HealthService
    from app.services.system_state_service import SystemStateService

    scheduler = _RecordingScheduler()
    register_jobs(
        scheduler,
        system_state_service=cast(SystemStateService, object()),
        health_service=cast(HealthService, object()),
    )

    assert "daily_universe_ingestion" not in scheduler.jobs
    assert "interest_rate_ingestion" not in scheduler.jobs
