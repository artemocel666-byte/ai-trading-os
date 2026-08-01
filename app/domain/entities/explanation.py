"""What a future Chief AI may be given, and what it is allowed to hand back.

The project rule this file exists to enforce: an explanation may describe a deterministic result
and nothing else. It may not change a number, invent one, or turn a report into advice. Everything
here is a frozen projection — no session, no provider, no composer, no way back into the pipeline.

Deliberately absent, and not by oversight: direction, price levels, position size, and any kind of
scoring. The older Chief AI request stub in `app/schemas/agents.py` requires two scored fields the
pipeline never produces and the safety tests ban outright; reusing it would have meant breaking the
project's own rules to satisfy a stub. The Phase 8A block in the safety-boundary tests names those
fields and keeps them out.
"""

import hashlib
import json
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core import constants
from app.core.time import normalize_to_utc
from app.domain.entities.market_data import Timeframe
from app.domain.entities.pipeline_decision import PipelineDecisionStatus
from app.domain.entities.rule_evaluation import RuleSetEvaluationStatus
from app.domain.value_objects import CurrencyPair

MAXIMUM_EXPLANATION_LENGTH = 2000


class ExplanationIssueCode(StrEnum):
    EMPTY_TEXT = "EMPTY_TEXT"
    NOT_RUSSIAN = "NOT_RUSSIAN"
    ACTIONABLE_TEXT = "ACTIONABLE_TEXT"
    EMOJI_FOUND = "EMOJI_FOUND"
    UNKNOWN_NUMBER = "UNKNOWN_NUMBER"
    TOO_LONG = "TOO_LONG"


class ExplanationRulesetFacts(BaseModel):
    """One ruleset's outcome, as the explainer may describe it."""

    ruleset_name: str = Field(min_length=1, max_length=120)
    status: RuleSetEvaluationStatus
    passed_count: int = Field(ge=0)
    failed_count: int = Field(ge=0)
    unavailable_count: int = Field(ge=0)
    failed_rule_ids: tuple[str, ...] = ()
    unavailable_rule_ids: tuple[str, ...] = ()

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def counts_must_match_named_rules(self) -> Self:
        if len(self.failed_rule_ids) != self.failed_count:
            raise ValueError("failed_rule_ids must name every failed rule")
        if len(self.unavailable_rule_ids) != self.unavailable_count:
            raise ValueError("unavailable_rule_ids must name every unavailable rule")
        return self


class ExplanationReading(BaseModel):
    """A numeric reading the pipeline already computed.

    `value` stays `None` when the field did not resolve. An unavailable reading is offered to the
    explainer as unavailable, never as a zero, because a substituted number would read as an
    observation.
    """

    field_ref: str = Field(min_length=1)
    value: Decimal | None = None

    model_config = ConfigDict(frozen=True)


class ExplanationInput(BaseModel):
    """Everything a Chief AI may see about one decision, and nothing else."""

    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    pair: CurrencyPair
    timeframe: Timeframe
    as_of: datetime
    decision_status: PipelineDecisionStatus
    source_snapshot_id: str = Field(min_length=64, max_length=64)
    used_candle_count: int = Field(ge=0)
    expected_candle_count: int = Field(ge=0)
    ruleset_facts: tuple[ExplanationRulesetFacts, ...] = ()
    readings: tuple[ExplanationReading, ...] = ()
    is_actionable: bool = False

    model_config = ConfigDict(frozen=True)

    @field_validator("as_of")
    @classmethod
    def as_of_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("ruleset_facts")
    @classmethod
    def normalize_ruleset_facts(
        cls,
        value: tuple[ExplanationRulesetFacts, ...],
    ) -> tuple[ExplanationRulesetFacts, ...]:
        return tuple(sorted(value, key=lambda facts: facts.ruleset_name))

    @field_validator("readings")
    @classmethod
    def normalize_readings(
        cls,
        value: tuple[ExplanationReading, ...],
    ) -> tuple[ExplanationReading, ...]:
        return tuple(sorted(value, key=lambda reading: reading.field_ref))

    @model_validator(mode="after")
    def must_stay_non_actionable(self) -> Self:
        if self.is_actionable:
            raise ValueError("explanation input must remain non-actionable")
        return self

    @property
    def total_rule_count(self) -> int:
        return sum(
            facts.passed_count + facts.failed_count + facts.unavailable_count
            for facts in self.ruleset_facts
        )

    @property
    def passed_rule_count(self) -> int:
        return sum(facts.passed_count for facts in self.ruleset_facts)

    def deterministic_json(self) -> str:
        return json.dumps(
            self.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def fingerprint_sha256(self) -> str:
        return hashlib.sha256(self.deterministic_json().encode("utf-8")).hexdigest()


class ExplanationIssue(BaseModel):
    code: ExplanationIssueCode
    detail: str = Field(min_length=1, max_length=500)

    model_config = ConfigDict(frozen=True)


class ExplanationValidationReport(BaseModel):
    """Outcome of checking one candidate explanation.

    Fail-closed by construction: `accepted` is true only when nothing was found. A caller that sees
    anything else must fall back to the deterministic text rather than repairing the model's answer.
    """

    checked_at: datetime
    issues: tuple[ExplanationIssue, ...] = ()
    accepted: bool = False

    model_config = ConfigDict(frozen=True)

    @field_validator("checked_at")
    @classmethod
    def checked_at_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @model_validator(mode="after")
    def acceptance_must_match_issues(self) -> Self:
        if self.accepted != (not self.issues):
            raise ValueError("an explanation is accepted only when no issue was found")
        return self

    @property
    def issue_codes(self) -> tuple[ExplanationIssueCode, ...]:
        return tuple(issue.code for issue in self.issues)


class ExplanationOutcome(BaseModel):
    """What a caller gets back after a model has been asked and its answer checked.

    `text` exists only when the validation accepted it. There is deliberately no field carrying the
    rejected text: a caller cannot log it into a user-facing path by accident, and cannot "fix it
    up" — the deterministic text is the fallback, not a repaired model answer.
    """

    model_name: str = Field(min_length=1, max_length=120)
    text: str | None = None
    validation: ExplanationValidationReport
    is_actionable: bool = False

    # `model_name` is the name of the LLM, not a Pydantic attribute; the protected namespace is
    # cleared so the field can keep the name a reader expects.
    model_config = ConfigDict(frozen=True, protected_namespaces=())

    @model_validator(mode="after")
    def text_presence_must_match_validation(self) -> Self:
        if self.is_actionable:
            raise ValueError("an explanation outcome must remain non-actionable")
        if self.validation.accepted and not self.text:
            raise ValueError("an accepted explanation must carry its text")
        if not self.validation.accepted and self.text is not None:
            raise ValueError("a rejected explanation must not carry text")
        return self

    @property
    def accepted(self) -> bool:
        return self.validation.accepted
