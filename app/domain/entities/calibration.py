from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

from app.core import constants
from app.core.time import normalize_to_utc
from app.domain.entities.market_data import Timeframe
from app.domain.entities.strategy_rules import StrategyRuleSeverity
from app.domain.value_objects import CurrencyPair

# A descriptive rule has to be quiet in normal conditions and still able to fire. Below this share
# of windows it is quiet; above it, it is firing often enough that nobody would read it.
RARE_FIRING_SHARE = Decimal("0.10")


class RuleBehaviour(StrEnum):
    """How a rule behaved across a replay.

    NEVER_FIRES is a defect, not a compliment: a rule that passed every window of real history
    cannot report anything, which is the Phase 7C `EXISTS` defect in a different shape.
    """

    NOT_OBSERVED = "NOT_OBSERVED"
    NEVER_FIRES = "NEVER_FIRES"
    RARELY_FIRES = "RARELY_FIRES"
    OFTEN_FIRES = "OFTEN_FIRES"
    ALWAYS_FIRES = "ALWAYS_FIRES"


class FieldDistribution(BaseModel):
    """Observed distribution of one resolved field across the replay.

    Every percentile is `None` when nothing resolved. An unavailable field is reported as
    unavailable rather than as a zero, the same rule the Phase 7C resolvers follow.
    """

    field_ref: str = Field(min_length=1)
    observed_count: int = Field(default=0, ge=0)
    unavailable_count: int = Field(default=0, ge=0)
    minimum: Decimal | None = None
    p05: Decimal | None = None
    p25: Decimal | None = None
    median: Decimal | None = None
    p75: Decimal | None = None
    p95: Decimal | None = None
    maximum: Decimal | None = None

    model_config = ConfigDict(frozen=True)

    @property
    def percentiles(self) -> tuple[Decimal | None, ...]:
        return (self.minimum, self.p05, self.p25, self.median, self.p75, self.p95, self.maximum)

    @model_validator(mode="after")
    def validate_distribution(self) -> Self:
        if self.observed_count == 0:
            if any(value is not None for value in self.percentiles):
                raise ValueError("a field with no observations must not report percentiles")
            return self
        if any(value is None for value in self.percentiles):
            raise ValueError("an observed field must report every percentile")
        previous: Decimal | None = None
        for value in self.percentiles:
            assert value is not None
            if previous is not None and value < previous:
                raise ValueError("field percentiles must not decrease")
            previous = value
        return self


class RuleOutcomeTally(BaseModel):
    """How one rule resolved across every replayed window."""

    rule_id: str = Field(min_length=1)
    field_ref: str = Field(min_length=1)
    severity: StrategyRuleSeverity
    passed_count: int = Field(default=0, ge=0)
    failed_count: int = Field(default=0, ge=0)
    unavailable_count: int = Field(default=0, ge=0)

    model_config = ConfigDict(frozen=True)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def evaluated_count(self) -> int:
        return self.passed_count + self.failed_count

    @computed_field  # type: ignore[prop-decorator]
    @property
    def failing_share(self) -> Decimal | None:
        if self.evaluated_count == 0:
            return None
        return Decimal(self.failed_count) / Decimal(self.evaluated_count)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def behaviour(self) -> RuleBehaviour:
        """Derived from the counts, never supplied, so the verdict cannot drift from the data."""
        failing_share = self.failing_share
        if failing_share is None:
            return RuleBehaviour.NOT_OBSERVED
        if self.failed_count == 0:
            return RuleBehaviour.NEVER_FIRES
        if self.passed_count == 0:
            return RuleBehaviour.ALWAYS_FIRES
        if failing_share <= RARE_FIRING_SHARE:
            return RuleBehaviour.RARELY_FIRES
        return RuleBehaviour.OFTEN_FIRES

    @property
    def sort_key(self) -> tuple[str, str]:
        return (self.rule_id, self.field_ref)


class RuleCalibrationReport(BaseModel):
    """Read-only measurement of how the built-in rules behaved over stored history.

    Descriptive only: it counts outcomes and summarises distributions. It produces no direction,
    price level, or recommendation, and stays non-actionable.
    """

    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    pair: CurrencyPair
    timeframe: Timeframe
    replay_start: datetime
    replay_end: datetime
    window_candles: int = Field(ge=1)
    step_candles: int = Field(ge=1)
    window_count: int = Field(default=0, ge=0)
    tallies: tuple[RuleOutcomeTally, ...] = ()
    distributions: tuple[FieldDistribution, ...] = ()
    ready_for_review_ruleset_count: int = Field(default=0, ge=0)
    not_ready_ruleset_count: int = Field(default=0, ge=0)
    blocked_ruleset_count: int = Field(default=0, ge=0)
    is_actionable: bool = False

    model_config = ConfigDict(frozen=True)

    @field_validator("replay_start", "replay_end")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("tallies")
    @classmethod
    def normalize_tallies(cls, value: tuple[RuleOutcomeTally, ...]) -> tuple[RuleOutcomeTally, ...]:
        return tuple(sorted(value, key=lambda tally: tally.sort_key))

    @field_validator("distributions")
    @classmethod
    def normalize_distributions(
        cls,
        value: tuple[FieldDistribution, ...],
    ) -> tuple[FieldDistribution, ...]:
        return tuple(sorted(value, key=lambda distribution: distribution.field_ref))

    @model_validator(mode="after")
    def validate_report(self) -> Self:
        if self.is_actionable:
            raise ValueError("calibration reports must remain non-actionable")
        if self.replay_end <= self.replay_start:
            raise ValueError("replay_end must be later than replay_start")
        for tally in self.tallies:
            observed = tally.passed_count + tally.failed_count + tally.unavailable_count
            if observed != self.window_count:
                raise ValueError(
                    f"{tally.rule_id} reports {observed} outcomes for {self.window_count} windows"
                )
        return self

    @property
    def dead_rules(self) -> tuple[RuleOutcomeTally, ...]:
        """Rules that could never report anything over this history."""
        return tuple(
            tally
            for tally in self.tallies
            if tally.behaviour in (RuleBehaviour.NEVER_FIRES, RuleBehaviour.NOT_OBSERVED)
        )
