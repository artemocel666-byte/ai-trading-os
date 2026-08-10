"""The forward ledger: a plan written down before its outcome exists.

Every figure this project has published came from replaying stored history, and a replay can always
be re-run with different multipliers until something looks good. A row here cannot be: it is written
at the moment the window closes, before any candle that could resolve it has arrived, and the
outcome is filled in later by a separate tick reading separate data.

That is the whole value of the shape below. Not the numbers — the order in which they are allowed
to be written.

Three things are deliberately absent, and their absence is the point:

- **No direction is chosen.** Both are recorded for every window, exactly as
  `scripts/measure_outcomes.py` measures both. The project has no candidate that survived
  inspection, and a ledger that picked one would be inventing it.
- **No account, balance, position size, or profit.** All four would have to be made up. The legacy
  `paper_positions` table has fields for them and has stood empty since Phase 1 for this reason.
- **No costs.** The project stores OHLC and no spread, so every figure a ledger row can support is
  gross. A zeroed cost column would read as a measured one.

A row has two lifetimes. Until `outcome_kind` is set it is a pending claim about the future; after,
it is a record. `None` there means "not yet", never "nothing happened" — the same distinction
`OutcomeStatistics` draws between a share of zero and a share that cannot be computed.
"""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core import constants
from app.core.time import normalize_to_utc
from app.domain.entities.market_data import Timeframe
from app.domain.entities.outcome import RESOLVED_KINDS, OutcomeKind
from app.domain.entities.pipeline_decision import PipelineDecisionStatus
from app.domain.entities.readiness import SnapshotScheduleItem
from app.domain.entities.signal_contract import SignalDirection
from app.domain.value_objects import CurrencyPair

#: The rule whose verdict says whether the window was built from traded candles. Read onto its own
#: column because Phase 9A-8 found that weekend filler is not visibly flat on every instrument: on
#: NOKSEK it carries a *wider* average range than a weekday. Nothing derived from the values can be
#: trusted to spot it, so the calendar's answer is stored rather than re-inferred later.
MARKET_OPEN_RULE_ID = "data_quality.market_open"


class ForwardOutcomeTickReason(StrEnum):
    DISABLED = "DISABLED"
    NO_ITEMS = "NO_ITEMS"
    COMPLETED = "COMPLETED"


class ForwardOutcomeConfig(BaseModel):
    """What the two ticks are allowed to do, and over which series.

    `horizon_candles` is carried onto every row rather than read from configuration at resolution
    time. A horizon changed halfway through would otherwise silently re-scope rows written under the
    old one, and the ledger would stop meaning one thing.
    """

    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    enabled: bool = False
    record_interval_minutes: int = Field(default=15, ge=1, le=1440)
    resolve_interval_minutes: int = Field(default=15, ge=1, le=1440)
    window_candles: int = Field(default=12, ge=2, le=500)
    horizon_candles: int = Field(default=24, ge=1, le=500)
    #: How many pending rows one resolve tick may look at. A bound, not a target: the ledger is
    #: small, but an unbounded query on a table that only grows is a defect waiting for a year.
    resolve_batch_size: int = Field(default=500, ge=1, le=10_000)
    items: tuple[SnapshotScheduleItem, ...] = ()

    model_config = ConfigDict(frozen=True)


class ForwardOutcomeRecord(BaseModel):
    """One window, one direction: the plan, what the rules said, and later what happened."""

    pair: CurrencyPair
    timeframe: Timeframe
    as_of: datetime
    direction: SignalDirection

    anchor_price: Decimal = Field(gt=Decimal("0"))
    entry_min: Decimal = Field(gt=Decimal("0"))
    entry_max: Decimal = Field(gt=Decimal("0"))
    stop_loss: Decimal = Field(gt=Decimal("0"))
    take_profit_1: Decimal = Field(gt=Decimal("0"))

    decision_status: PipelineDecisionStatus
    #: `None` when the rule could not be evaluated at all, which is not the same as a closed market.
    market_open: bool | None = None
    #: Rules observed to be wrong on this window. Rules that could not be evaluated are absent
    #: rather than listed as failures — the distinction Phase 9A-7 had to add to `RuleBehaviour`
    #: after a rule was called "often firing" on 0.4% of the sample.
    failed_rule_ids: tuple[str, ...] = ()

    pipeline_version: str = Field(min_length=1)
    ruleset_versions: tuple[str, ...] = ()
    decision_fingerprint: str = Field(min_length=64, max_length=64)
    entry_band_multiplier: Decimal = Field(ge=Decimal("0"))
    stop_multiplier: Decimal = Field(gt=Decimal("0"))
    target_multiplier: Decimal = Field(gt=Decimal("0"))
    horizon_candles: int = Field(ge=1)
    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    recorded_at: datetime

    outcome_kind: OutcomeKind | None = None
    bars_to_resolution: int | None = Field(default=None, ge=1)
    resolved_at: datetime | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("as_of", "recorded_at")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("resolved_at")
    @classmethod
    def resolved_at_must_be_utc(cls, value: datetime | None) -> datetime | None:
        return None if value is None else normalize_to_utc(value)

    @field_validator("failed_rule_ids", "ruleset_versions")
    @classmethod
    def normalize_identifier_tuple(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(sorted({item.strip() for item in value if item.strip()}))

    @model_validator(mode="after")
    def validate_record(self) -> Self:
        if self.entry_min > self.entry_max:
            raise ValueError("entry_min must not be above entry_max")
        if not (self.entry_min <= self.anchor_price <= self.entry_max):
            raise ValueError("the anchor must lie inside its own entry band")
        if self.target_multiplier < self.stop_multiplier:
            raise ValueError("target_multiplier must not be closer than stop_multiplier")
        if self.recorded_at < self.as_of:
            raise ValueError("a window cannot be recorded before the moment it describes")

        # The two lifetimes. Nothing here may be half-set: a resolution without a kind, or a kind
        # without the moment it was written, would leave a row that cannot be read either way.
        if self.outcome_kind is None:
            if self.bars_to_resolution is not None or self.resolved_at is not None:
                raise ValueError("a pending record must not carry a resolution")
            return self
        if self.resolved_at is None:
            raise ValueError("a resolved record must report when it was resolved")
        if self.resolved_at < self.as_of:
            raise ValueError("a record cannot be resolved before the moment it describes")
        if self.outcome_kind in RESOLVED_KINDS:
            if self.bars_to_resolution is None:
                raise ValueError("a resolved outcome must report the bar that resolved it")
        elif self.bars_to_resolution is not None:
            raise ValueError("an unresolved outcome cannot report a resolution bar")
        return self

    @property
    def is_pending(self) -> bool:
        return self.outcome_kind is None

    @property
    def identity(self) -> tuple[str, str, datetime, str]:
        """The four columns a row is unique on, so a re-run cannot double-record a window."""
        return (self.pair.value, self.timeframe.value, self.as_of, self.direction.value)


class ForwardOutcomeRecordResult(BaseModel):
    """What one recording tick wrote.

    `windows_without_a_plan` is counted rather than ignored: a flat or incomplete window genuinely
    has no scale to place levels on, and `build_price_plan` returns `None` instead of substituting
    one. A silent skip would make the ledger's coverage unknowable.

    `windows_without_data` is kept apart from it. A market that moved too little to place levels on
    and an ingestion that fetched nothing look identical in a single counter, and they call for
    opposite responses.
    """

    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    as_of: datetime
    executed: bool
    reason: ForwardOutcomeTickReason
    item_count: int = Field(default=0, ge=0)
    considered_count: int = Field(default=0, ge=0)
    recorded_count: int = Field(default=0, ge=0)
    already_present_count: int = Field(default=0, ge=0)
    windows_without_a_plan: int = Field(default=0, ge=0)
    windows_without_data: int = Field(default=0, ge=0)
    failed_item_count: int = Field(default=0, ge=0)

    model_config = ConfigDict(frozen=True)

    @field_validator("as_of")
    @classmethod
    def as_of_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        if not self.executed and self.reason == ForwardOutcomeTickReason.COMPLETED:
            raise ValueError("a tick that did not execute cannot report completion")
        if not self.executed and (self.recorded_count or self.considered_count):
            raise ValueError("a tick that did not execute cannot report written rows")
        if self.recorded_count + self.already_present_count > self.considered_count:
            raise ValueError("written rows must not exceed the rows considered")
        return self


class ForwardOutcomeResolveResult(BaseModel):
    """What one resolution tick settled, and what it deliberately left pending.

    `still_pending_count` is not a failure. A plan whose horizon has not elapsed has no outcome yet,
    and writing `TIMEOUT` because candles had not arrived would turn a gap in ingestion into a
    measured result — the exact confusion Phase 9A-5 found in the stored history.
    """

    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    as_of: datetime
    executed: bool
    reason: ForwardOutcomeTickReason
    examined_count: int = Field(default=0, ge=0)
    resolved_count: int = Field(default=0, ge=0)
    still_pending_count: int = Field(default=0, ge=0)

    model_config = ConfigDict(frozen=True)

    @field_validator("as_of")
    @classmethod
    def as_of_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        if not self.executed and self.reason == ForwardOutcomeTickReason.COMPLETED:
            raise ValueError("a tick that did not execute cannot report completion")
        if not self.executed and self.examined_count:
            raise ValueError("a tick that did not execute cannot report examined rows")
        if self.resolved_count + self.still_pending_count != self.examined_count:
            raise ValueError("every examined record must be either resolved or still pending")
        return self
