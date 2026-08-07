"""What happened after a window, once its plan was already fixed.

This is the only place in the project where data *after* `as_of` is legitimate. Everywhere else the
Phase 3D invariant holds: nothing from the future may influence a decision. Measurement runs after
the fact and its results must never flow back into a snapshot, a rule, or a decision — the same
"ingest forward, evaluate backward" line Phase 7B drew for the calendar.

`AMBIGUOUS` exists because OHLC cannot answer the question it names. When one candle's range spans
both the protective level and the target, nothing in the data says which was touched first. Silently
picking the flattering answer is the classic way a backtest lies to its author, so the ambiguity is
counted in its own right and resolved conservatively for the headline number.
"""

from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.entities.signal_contract import SignalDirection


class OutcomeKind(StrEnum):
    TARGET_FIRST = "TARGET_FIRST"
    STOP_FIRST = "STOP_FIRST"
    AMBIGUOUS = "AMBIGUOUS"
    TIMEOUT = "TIMEOUT"
    NO_DATA = "NO_DATA"


#: Kinds that say something about direction of travel. TIMEOUT and NO_DATA do not.
RESOLVED_KINDS = (OutcomeKind.TARGET_FIRST, OutcomeKind.STOP_FIRST, OutcomeKind.AMBIGUOUS)


class WindowOutcome(BaseModel):
    """One window's plan, walked forward until something happened or the horizon ran out."""

    direction: SignalDirection
    entry_price: Decimal = Field(gt=Decimal("0"))
    stop_loss: Decimal = Field(gt=Decimal("0"))
    take_profit: Decimal = Field(gt=Decimal("0"))
    kind: OutcomeKind
    bars_to_resolution: int | None = Field(default=None, ge=1)

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def resolution_must_match_kind(self) -> Self:
        if self.kind in (OutcomeKind.TIMEOUT, OutcomeKind.NO_DATA):
            if self.bars_to_resolution is not None:
                raise ValueError("an unresolved outcome cannot report a resolution bar")
        elif self.bars_to_resolution is None:
            raise ValueError("a resolved outcome must report the bar that resolved it")
        return self

    @property
    def conservative_kind(self) -> OutcomeKind:
        """Ambiguity counted against the plan, which is the only defensible direction to lean."""
        if self.kind == OutcomeKind.AMBIGUOUS:
            return OutcomeKind.STOP_FIRST
        return self.kind


class OutcomeStatistics(BaseModel):
    """Counts over many windows, with shares reported as unavailable when nothing resolved."""

    measured_count: int = Field(default=0, ge=0)
    target_first_count: int = Field(default=0, ge=0)
    stop_first_count: int = Field(default=0, ge=0)
    ambiguous_count: int = Field(default=0, ge=0)
    timeout_count: int = Field(default=0, ge=0)
    no_data_count: int = Field(default=0, ge=0)
    average_bars_to_resolution: Decimal | None = None

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def counts_must_add_up(self) -> Self:
        total = (
            self.target_first_count
            + self.stop_first_count
            + self.ambiguous_count
            + self.timeout_count
            + self.no_data_count
        )
        if total != self.measured_count:
            raise ValueError("outcome counts must add up to the measured count")
        return self

    @property
    def resolved_count(self) -> int:
        return self.target_first_count + self.stop_first_count + self.ambiguous_count

    @property
    def target_first_share(self) -> Decimal | None:
        """Share of resolved windows that reached the target first, ambiguity counted against.

        `None` when nothing resolved: a share of zero would read as "never reached the target",
        which is a different statement from "there is nothing to divide by".
        """
        if self.resolved_count == 0:
            return None
        return Decimal(self.target_first_count) / Decimal(self.resolved_count)

    @property
    def ambiguous_share(self) -> Decimal | None:
        """How much of the sample the data simply cannot adjudicate.

        The single most important number here: a high value means every other figure is soft.
        """
        if self.resolved_count == 0:
            return None
        return Decimal(self.ambiguous_count) / Decimal(self.resolved_count)

    @property
    def conservative_stop_first_count(self) -> int:
        """Protective-level hits with every ambiguous window handed to them.

        The mirror of `target_first_share`: together the two account for the whole resolved sample,
        so the ambiguity is visible in one number and absorbed in the other, never in neither.
        """
        return self.stop_first_count + self.ambiguous_count

    @property
    def timeout_share(self) -> Decimal | None:
        if self.measured_count == 0:
            return None
        return Decimal(self.timeout_count) / Decimal(self.measured_count)
