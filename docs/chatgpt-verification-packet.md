# ChatGPT Verification Packet - Phase 4E

Generated: 2026-07-18T14:52:43Z

## Current Scope

Phase 4E is disabled pipeline report shell foundation only.

`PROJECT_PHASE = "phase_4e_disabled_pipeline_report_shell_foundation"`

Phase 4E defines immutable disabled pipeline report/blocker models and a disabled shell that
consumes only Phase 4D registry snapshots. It summarizes registry item counts, registry validation
status, registry snapshot fingerprint, and blockers proving runtime behavior remains disabled.

Phase 4E does not evaluate rules against market data, candles, indicators, economic events, context
snapshots, analysis snapshots, or signal contracts. It is not a decision engine. It does not
generate signals, does not provide trading recommendations, does not calculate entries/stops/
targets, does not calculate position size, does not calculate setup score or confidence, does not
call AI/OpenAI/LLM services, does not send Telegram signals, does not use broker APIs, does not
execute orders, and does not enable paper or real trading.

Phase 3J was not created or restored. Phase 4F and later work was not started. Phase 4E is
uncommitted at packet generation time.

## Preflight

Preflight passed before edits:

```text
git status --short
<no output>

git log --oneline -5
e92ee78 Add Phase 4D strategy ruleset registry foundation
3f1cf6a Add Phase 4C strategy ruleset validation foundation
437e111  Phase 4B
a4c8f27  Phase 4A
bad58a4 Add Phase 3I persistent digest audit foundation

grep -n "PROJECT_PHASE" app/core/constants.py
1:PROJECT_PHASE = "phase_4d_strategy_ruleset_registry_foundation"

Phase 4D strategy_registry exists
Phase 4D registry exists
Phase 4C strategy_validation exists
Phase 4C validator exists
Phase 4B strategy_rules exists
Phase 4A signal_contract exists
Phase 3J API route absent
```

## Git Metadata

- Branch: `main`
- Current commit hash: `e92ee782c8a96f7f1924ebb29c43af85c0eaec27`
- Current commit short: `e92ee78 Add Phase 4D strategy ruleset registry foundation`

`git status --short` captured before final packet rewrite:

```text
 M AGENTS.md
 M PLANS.md
 M README.md
 M app/core/constants.py
 M app/domain/entities/__init__.py
 M docs/operations.md
 M tests/contract/test_safety_boundaries.py
 M tests/unit/test_signal_contract_foundation.py
 M tests/unit/test_strategy_rule_specification_foundation.py
 M tests/unit/test_strategy_ruleset_registry_foundation.py
 M tests/unit/test_strategy_ruleset_validation_foundation.py
?? app/domain/disabled_pipeline_report_shell.py
?? app/domain/entities/pipeline_report.py
?? tests/unit/test_disabled_pipeline_report_shell_foundation.py
```

`git diff --stat` captured before final packet rewrite:

```text
 AGENTS.md                                          |  26 +--
 PLANS.md                                           |  21 ++-
 README.md                                          |  19 ++-
 app/core/constants.py                              |   2 +-
 app/domain/entities/__init__.py                    |  10 ++
 docs/operations.md                                 |   8 +
 tests/contract/test_safety_boundaries.py           | 177 +++++++++++++++++++++
 tests/unit/test_signal_contract_foundation.py      |   4 +-
 .../test_strategy_rule_specification_foundation.py |   4 +-
 .../test_strategy_ruleset_registry_foundation.py   |   4 +-
 .../test_strategy_ruleset_validation_foundation.py |   4 +-
 11 files changed, 249 insertions(+), 30 deletions(-)
```

## Created Files

- `app/domain/disabled_pipeline_report_shell.py`
- `app/domain/entities/pipeline_report.py`
- `docs/phase4e-verification-report.md`
- `tests/unit/test_disabled_pipeline_report_shell_foundation.py`

## Modified Files

- `AGENTS.md`
- `PLANS.md`
- `README.md`
- `app/core/constants.py`
- `app/domain/entities/__init__.py`
- `docs/chatgpt-verification-packet.md`
- `docs/operations.md`
- `tests/contract/test_safety_boundaries.py`
- `tests/unit/test_signal_contract_foundation.py`
- `tests/unit/test_strategy_rule_specification_foundation.py`
- `tests/unit/test_strategy_ruleset_registry_foundation.py`
- `tests/unit/test_strategy_ruleset_validation_foundation.py`

## Migration Files

No migration files were created or modified for Phase 4E.

Current Docker Alembic head remained:

```text
0003_phase3i_digest_audit (head)
```

## Full Contents Of Changed Source Files

### `app/core/constants.py`

```python
PROJECT_PHASE = "phase_4e_disabled_pipeline_report_shell_foundation"
STRATEGY_IMPLEMENTED = False
REAL_TRADING_ENABLED = False

SYSTEM_STATE_SCAN_ENABLED = "scan_enabled"
SYSTEM_STATE_WORKER_HEARTBEAT = "worker_heartbeat"
SYSTEM_STATE_LAST_SUCCESSFUL_MARKET_FETCH = "last_successful_market_fetch"
SYSTEM_STATE_LAST_SUCCESSFUL_CALENDAR_FETCH = "last_successful_calendar_fetch"
SYSTEM_STATE_LAST_ERROR = "last_error"

DEFAULT_STRATEGY_VERSION = "foundation-v1"
```

### `app/domain/entities/pipeline_report.py`

```python
import hashlib
import json
from datetime import datetime
from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.strategy_rules import StrategyRuleSeverity


class DisabledPipelineStatus(StrEnum):
    DISABLED = "DISABLED"
    BLOCKED = "BLOCKED"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"


class DisabledPipelineBlockerCode(StrEnum):
    PIPELINE_DISABLED = "PIPELINE_DISABLED"
    REGISTRY_INVALID = "REGISTRY_INVALID"
    REGISTRY_EMPTY = "REGISTRY_EMPTY"
    ACTIONABLE_ITEM_FOUND = "ACTIONABLE_ITEM_FOUND"
    RUNTIME_NOT_ALLOWED = "RUNTIME_NOT_ALLOWED"


def _normalize_required_string(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be non-empty")
    return normalized


def _normalize_optional_string(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    return _normalize_required_string(value, field_name)


class DisabledPipelineBlocker(BaseModel):
    code: DisabledPipelineBlockerCode
    message: str = Field(min_length=1, max_length=1000)
    registry_key: str | None = None
    severity: StrategyRuleSeverity

    model_config = ConfigDict(frozen=True)

    @field_validator("message", mode="before")
    @classmethod
    def normalize_message(cls, value: object) -> str:
        return _normalize_required_string(value, "message")

    @field_validator("registry_key", mode="before")
    @classmethod
    def normalize_registry_key(cls, value: object) -> str | None:
        return _normalize_optional_string(value, "registry_key")

    @property
    def sort_key(self) -> tuple[str, str, str]:
        return (self.code.value, self.registry_key or "", self.message)


class DisabledPipelineReport(BaseModel):
    pipeline_version: str = Field(min_length=1)
    project_phase: str = Field(min_length=1)
    status: DisabledPipelineStatus
    created_at: datetime
    registry_item_count: int = Field(ge=0)
    valid_registry_item_count: int = Field(ge=0)
    invalid_registry_item_count: int = Field(ge=0)
    blockers: tuple[DisabledPipelineBlocker, ...] = ()
    registry_snapshot_fingerprint: str = Field(min_length=64, max_length=64)
    enabled_for_runtime: bool = False
    is_actionable: bool = False
    fingerprint: str | None = Field(default=None, min_length=64, max_length=64)

    model_config = ConfigDict(frozen=True)

    @field_validator("pipeline_version", "project_phase", mode="before")
    @classmethod
    def normalize_required_identifiers(cls, value: object) -> str:
        return _normalize_required_string(value, "disabled pipeline report identifier")

    @field_validator("created_at")
    @classmethod
    def created_at_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("blockers")
    @classmethod
    def normalize_blockers(
        cls,
        value: tuple[DisabledPipelineBlocker, ...],
    ) -> tuple[DisabledPipelineBlocker, ...]:
        return tuple(sorted(value, key=lambda blocker: blocker.sort_key))

    @model_validator(mode="after")
    def validate_counts_and_flags(self) -> Self:
        if self.valid_registry_item_count + self.invalid_registry_item_count != (
            self.registry_item_count
        ):
            raise ValueError("registry report counts must add up to registry_item_count")
        if self.enabled_for_runtime:
            raise ValueError("disabled pipeline reports must remain disabled for runtime use")
        if self.is_actionable:
            raise ValueError("disabled pipeline reports must remain non-actionable")
        if self.status == DisabledPipelineStatus.READY_FOR_REVIEW and self.blockers:
            raise ValueError("READY_FOR_REVIEW reports must not contain blockers")
        if self.status != DisabledPipelineStatus.READY_FOR_REVIEW and not self.blockers:
            raise ValueError("disabled or blocked reports must contain blockers")
        return self

    def canonical_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"fingerprint"})

    def deterministic_json(self) -> str:
        return json.dumps(
            self.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def fingerprint_sha256(self) -> str:
        canonical = json.dumps(
            self.canonical_payload(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

### `app/domain/disabled_pipeline_report_shell.py`

```python
from datetime import datetime

from app.core import constants
from app.domain.entities.pipeline_report import (
    DisabledPipelineBlocker,
    DisabledPipelineBlockerCode,
    DisabledPipelineReport,
    DisabledPipelineStatus,
)
from app.domain.entities.strategy_registry import StrategyRuleSetRegistrySnapshot
from app.domain.entities.strategy_rules import StrategyRuleSeverity
from app.domain.strategy_ruleset_registry import StrategyRuleSetRegistry

DISABLED_PIPELINE_VERSION = "phase4e-disabled-pipeline-report-shell-v1"


class DisabledPipelineReportShell:
    def __init__(
        self,
        registry: StrategyRuleSetRegistry | None = None,
        enabled: bool = False,
    ) -> None:
        self._registry = registry or StrategyRuleSetRegistry()
        self._requested_enabled = enabled

    def build_report(self, created_at: datetime) -> DisabledPipelineReport:
        registry_snapshot = self._registry.load_builtin_rulesets(created_at)
        blockers = self._build_blockers(registry_snapshot)
        return DisabledPipelineReport(
            pipeline_version=DISABLED_PIPELINE_VERSION,
            project_phase=constants.PROJECT_PHASE,
            status=self._status_for(blockers),
            created_at=created_at,
            registry_item_count=registry_snapshot.item_count,
            valid_registry_item_count=registry_snapshot.valid_count,
            invalid_registry_item_count=registry_snapshot.invalid_count,
            blockers=tuple(blockers),
            registry_snapshot_fingerprint=registry_snapshot.fingerprint_sha256(),
            enabled_for_runtime=False,
            is_actionable=False,
        )

    def _build_blockers(
        self,
        registry_snapshot: StrategyRuleSetRegistrySnapshot,
    ) -> list[DisabledPipelineBlocker]:
        blockers: list[DisabledPipelineBlocker] = []
        if self._requested_enabled:
            blockers.append(
                self._blocker(
                    DisabledPipelineBlockerCode.RUNTIME_NOT_ALLOWED,
                    "Runtime enablement was requested, but Phase 4E keeps the shell disabled.",
                )
            )
        else:
            blockers.append(
                self._blocker(
                    DisabledPipelineBlockerCode.PIPELINE_DISABLED,
                    "The Phase 4E pipeline report shell is disabled.",
                )
            )
        if registry_snapshot.item_count == 0:
            blockers.append(
                self._blocker(
                    DisabledPipelineBlockerCode.REGISTRY_EMPTY,
                    "The registry snapshot contains no items.",
                )
            )
        if registry_snapshot.invalid_count > 0:
            blockers.extend(
                self._blocker(
                    DisabledPipelineBlockerCode.REGISTRY_INVALID,
                    "The registry item has a non-valid validation report.",
                    registry_key=item.registry_key,
                )
                for item in registry_snapshot.items
                if item.validation_report.status.value != "VALID"
            )
        blockers.extend(
            self._blocker(
                DisabledPipelineBlockerCode.ACTIONABLE_ITEM_FOUND,
                "The registry snapshot contains a runtime-enabled or actionable item.",
                registry_key=registry_key,
            )
            for registry_key in self._actionable_registry_keys(registry_snapshot)
        )
        return blockers

    def _status_for(
        self,
        blockers: list[DisabledPipelineBlocker],
    ) -> DisabledPipelineStatus:
        if not self._requested_enabled:
            return DisabledPipelineStatus.DISABLED
        if blockers:
            return DisabledPipelineStatus.BLOCKED
        return DisabledPipelineStatus.READY_FOR_REVIEW

    @staticmethod
    def _actionable_registry_keys(
        registry_snapshot: StrategyRuleSetRegistrySnapshot,
    ) -> tuple[str, ...]:
        if registry_snapshot.is_actionable:
            return ("registry_snapshot",)
        return tuple(
            item.registry_key
            for item in registry_snapshot.items
            if item.enabled_for_runtime or item.is_actionable or item.ruleset.is_actionable
        )

    @staticmethod
    def _blocker(
        code: DisabledPipelineBlockerCode,
        message: str,
        registry_key: str | None = None,
    ) -> DisabledPipelineBlocker:
        return DisabledPipelineBlocker(
            code=code,
            message=message,
            registry_key=registry_key,
            severity=StrategyRuleSeverity.BLOCKING,
        )
```

### `app/domain/entities/__init__.py`

```python
from app.domain.entities.analysis import (
    AnalysisInputAudit,
    AnalysisIssue,
    AnalysisIssueCode,
    AnalysisIssueCount,
    AnalysisNumericSummary,
    AnalysisReadinessStatus,
    AnalysisReport,
    AnalysisSnapshot,
    AnalysisSnapshotMetadata,
    AnalysisWindow,
)
from app.domain.entities.context import (
    CandleShapeSummary,
    ContextCurrencyCount,
    ContextImpactCount,
    ContextIssue,
    ContextIssueCode,
    EventContextSummary,
    IndicatorWindow,
    MarketContextSnapshot,
    MovingAverageSeries,
    MovingAverageSummary,
    RangeContextSummary,
    ReturnDistributionSummary,
    TimeContextSummary,
)
from app.domain.entities.data_quality import (
    CandleAvailability,
    DataQualityIssue,
    DataQualityIssueCode,
    EconomicEventAvailability,
    FeatureSnapshot,
    UpsertResult,
    build_feature_snapshot,
)
from app.domain.entities.features import (
    CandleFeatureSummary,
    CurrencyEventCount,
    EconomicEventFeatureSummary,
    EconomicImpactCount,
    FeatureIssue,
    FeatureIssueCode,
    FeatureWindow,
    MarketFeatureSnapshot,
)
from app.domain.entities.market_data import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.entities.pipeline_report import (
    DisabledPipelineBlocker,
    DisabledPipelineBlockerCode,
    DisabledPipelineReport,
    DisabledPipelineStatus,
)
from app.domain.entities.readiness import (
    SnapshotDigest,
    SnapshotDigestIssueCount,
    SnapshotDigestItem,
    SnapshotDigestStatus,
    SnapshotNotificationDedupKey,
    SnapshotNotificationPayload,
    SnapshotScheduleItem,
    SnapshotSchedulePlan,
    SnapshotWindow,
    digest_status_from_analysis,
)
from app.domain.entities.scheduled_digest import (
    ScheduledDigestConfig,
    ScheduledDigestDecision,
    ScheduledDigestDecisionReason,
    ScheduledDigestDeliveryRecord,
    ScheduledDigestDeliveryResult,
    ScheduledDigestTick,
)
from app.domain.entities.signal_contract import (
    SignalActionability,
    SignalContract,
    SignalDirection,
    SignalLifecycleStatus,
    SignalPricePlan,
    SignalRiskPlan,
)
from app.domain.entities.strategy_registry import (
    StrategyRuleSetRegistryItem,
    StrategyRuleSetRegistrySnapshot,
)
from app.domain.entities.strategy_rules import (
    StrategyRuleCategory,
    StrategyRuleCondition,
    StrategyRuleOperator,
    StrategyRuleSet,
    StrategyRuleSeverity,
    StrategyRuleSpec,
    StrategyRuleValue,
)
from app.domain.entities.strategy_validation import (
    StrategyRuleSetValidationIssue,
    StrategyRuleSetValidationIssueCode,
    StrategyRuleSetValidationReport,
    StrategyRuleSetValidationStatus,
)

__all__ = [
    "AnalysisInputAudit",
    "AnalysisIssue",
    "AnalysisIssueCode",
    "AnalysisIssueCount",
    "AnalysisNumericSummary",
    "AnalysisReadinessStatus",
    "AnalysisReport",
    "AnalysisSnapshot",
    "AnalysisSnapshotMetadata",
    "AnalysisWindow",
    "Candle",
    "CandleAvailability",
    "CandleFeatureSummary",
    "CandleShapeSummary",
    "ContextCurrencyCount",
    "ContextImpactCount",
    "ContextIssue",
    "ContextIssueCode",
    "CurrencyEventCount",
    "DataQualityIssue",
    "DataQualityIssueCode",
    "DisabledPipelineBlocker",
    "DisabledPipelineBlockerCode",
    "DisabledPipelineReport",
    "DisabledPipelineStatus",
    "EconomicEvent",
    "EconomicEventAvailability",
    "EconomicEventFeatureSummary",
    "EconomicImpact",
    "EconomicImpactCount",
    "EventContextSummary",
    "FeatureIssue",
    "FeatureIssueCode",
    "FeatureSnapshot",
    "FeatureWindow",
    "IndicatorWindow",
    "MarketContextSnapshot",
    "MarketFeatureSnapshot",
    "MovingAverageSeries",
    "MovingAverageSummary",
    "RangeContextSummary",
    "ReturnDistributionSummary",
    "ScheduledDigestConfig",
    "ScheduledDigestDecision",
    "ScheduledDigestDecisionReason",
    "ScheduledDigestDeliveryRecord",
    "ScheduledDigestDeliveryResult",
    "ScheduledDigestTick",
    "SignalActionability",
    "SignalContract",
    "SignalDirection",
    "SignalLifecycleStatus",
    "SignalPricePlan",
    "SignalRiskPlan",
    "SnapshotDigest",
    "SnapshotDigestIssueCount",
    "SnapshotDigestItem",
    "SnapshotDigestStatus",
    "SnapshotNotificationDedupKey",
    "SnapshotNotificationPayload",
    "SnapshotScheduleItem",
    "SnapshotSchedulePlan",
    "SnapshotWindow",
    "StrategyRuleCategory",
    "StrategyRuleCondition",
    "StrategyRuleOperator",
    "StrategyRuleSet",
    "StrategyRuleSetRegistryItem",
    "StrategyRuleSetRegistrySnapshot",
    "StrategyRuleSetValidationIssue",
    "StrategyRuleSetValidationIssueCode",
    "StrategyRuleSetValidationReport",
    "StrategyRuleSetValidationStatus",
    "StrategyRuleSeverity",
    "StrategyRuleSpec",
    "StrategyRuleValue",
    "TimeContextSummary",
    "Timeframe",
    "UpsertResult",
    "build_feature_snapshot",
    "digest_status_from_analysis",
]
```

## New Tests

### `tests/unit/test_disabled_pipeline_report_shell_foundation.py`

```python
from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.disabled_pipeline_report_shell import DisabledPipelineReportShell
from app.domain.entities.pipeline_report import (
    DisabledPipelineBlocker,
    DisabledPipelineBlockerCode,
    DisabledPipelineReport,
    DisabledPipelineStatus,
)
from app.domain.entities.strategy_registry import (
    StrategyRuleSetRegistryItem,
    StrategyRuleSetRegistrySnapshot,
)
from app.domain.entities.strategy_rules import StrategyRuleSet, StrategyRuleSeverity
from app.domain.strategy_ruleset_registry import (
    BUILTIN_STRATEGY_RULESET_FIXTURES,
    StrategyRuleSetRegistry,
)

CREATED_AT = datetime(2026, 7, 18, 11, 0, tzinfo=UTC)


class StaticSnapshotRegistry(StrategyRuleSetRegistry):
    def __init__(self, snapshot: StrategyRuleSetRegistrySnapshot) -> None:
        self.snapshot = snapshot

    def load_builtin_rulesets(self, _checked_at: datetime) -> StrategyRuleSetRegistrySnapshot:
        return self.snapshot


def _report(
    shell: DisabledPipelineReportShell | None = None,
    created_at: datetime = CREATED_AT,
) -> DisabledPipelineReport:
    return (shell or DisabledPipelineReportShell()).build_report(created_at)


def _blocker_codes(report: DisabledPipelineReport) -> tuple[DisabledPipelineBlockerCode, ...]:
    return tuple(blocker.code for blocker in report.blockers)


def _fixture_with_changed_description() -> dict[str, StrategyRuleSet]:
    fixtures = dict(BUILTIN_STRATEGY_RULESET_FIXTURES)
    base_ruleset = fixtures["foundation.data_quality.minimum"]
    changed_rule = base_ruleset.rules[0].model_copy(
        update={"description": "Validate a changed disabled report-shell fixture."}
    )
    fixtures["foundation.data_quality.minimum"] = base_ruleset.model_copy(
        update={"rules": (changed_rule,)}
    )
    return fixtures


def _snapshot_from_registry(
    registry: StrategyRuleSetRegistry | None = None,
) -> StrategyRuleSetRegistrySnapshot:
    return (registry or StrategyRuleSetRegistry()).load_builtin_rulesets(CREATED_AT)


def test_project_phase_is_phase4e_disabled_pipeline_report_shell_foundation() -> None:
    assert constants.PROJECT_PHASE == "phase_4e_disabled_pipeline_report_shell_foundation"


def test_blocker_and_report_models_are_immutable() -> None:
    report = _report()

    with pytest.raises(ValidationError):
        report.status = DisabledPipelineStatus.READY_FOR_REVIEW
    with pytest.raises(ValidationError):
        report.blockers[0].message = "changed"


def test_report_normalizes_created_at_to_utc() -> None:
    offset = timezone(timedelta(hours=2))
    report = _report(created_at=datetime(2026, 7, 18, 13, 0, tzinfo=offset))

    assert report.created_at == CREATED_AT


def test_default_shell_is_disabled_and_contains_disabled_blocker() -> None:
    report = _report()

    assert report.status == DisabledPipelineStatus.DISABLED
    assert DisabledPipelineBlockerCode.PIPELINE_DISABLED in _blocker_codes(report)
    assert report.enabled_for_runtime is False
    assert report.is_actionable is False


def test_enabled_shell_request_still_blocks_runtime_behavior() -> None:
    report = _report(DisabledPipelineReportShell(enabled=True))

    assert report.status == DisabledPipelineStatus.BLOCKED
    assert DisabledPipelineBlockerCode.RUNTIME_NOT_ALLOWED in _blocker_codes(report)
    assert DisabledPipelineBlockerCode.PIPELINE_DISABLED not in _blocker_codes(report)
    assert report.enabled_for_runtime is False
    assert report.is_actionable is False


def test_report_includes_registry_counts_and_snapshot_fingerprint() -> None:
    registry = StrategyRuleSetRegistry()
    snapshot = _snapshot_from_registry(registry)
    report = _report(DisabledPipelineReportShell(registry=registry))

    assert report.registry_item_count == snapshot.item_count
    assert report.valid_registry_item_count == snapshot.valid_count
    assert report.invalid_registry_item_count == snapshot.invalid_count
    assert report.registry_snapshot_fingerprint == snapshot.fingerprint_sha256()


def test_empty_registry_snapshot_adds_empty_blocker() -> None:
    empty_snapshot = StrategyRuleSetRegistrySnapshot(
        created_at=CREATED_AT,
        items=(),
        item_count=0,
        valid_count=0,
        invalid_count=0,
    )
    report = _report(DisabledPipelineReportShell(registry=StaticSnapshotRegistry(empty_snapshot)))

    assert DisabledPipelineBlockerCode.REGISTRY_EMPTY in _blocker_codes(report)


def test_invalid_registry_snapshot_adds_invalid_blocker() -> None:
    fixtures = dict(BUILTIN_STRATEGY_RULESET_FIXTURES)
    fixtures["foundation.data_quality.minimum"] = fixtures[
        "foundation.data_quality.minimum"
    ].model_copy(update={"enabled": True})
    snapshot = _snapshot_from_registry(StrategyRuleSetRegistry(fixtures=fixtures))

    report = _report(DisabledPipelineReportShell(registry=StaticSnapshotRegistry(snapshot)))

    assert DisabledPipelineBlockerCode.REGISTRY_INVALID in _blocker_codes(report)
    assert any(
        blocker.registry_key == "foundation.data_quality.minimum"
        for blocker in report.blockers
        if blocker.code == DisabledPipelineBlockerCode.REGISTRY_INVALID
    )


def test_actionable_registry_item_adds_actionable_blocker() -> None:
    snapshot = _snapshot_from_registry()
    item = snapshot.items[0]
    actionable_item = StrategyRuleSetRegistryItem.model_construct(
        registry_key=item.registry_key,
        ruleset=item.ruleset,
        validation_report=item.validation_report,
        enabled_for_runtime=True,
        is_actionable=False,
    )
    unsafe_snapshot = StrategyRuleSetRegistrySnapshot.model_construct(
        created_at=snapshot.created_at,
        items=(actionable_item, *snapshot.items[1:]),
        item_count=snapshot.item_count,
        valid_count=snapshot.valid_count,
        invalid_count=snapshot.invalid_count,
        fingerprint=snapshot.fingerprint,
        is_actionable=False,
    )

    report = _report(DisabledPipelineReportShell(registry=StaticSnapshotRegistry(unsafe_snapshot)))

    assert DisabledPipelineBlockerCode.ACTIONABLE_ITEM_FOUND in _blocker_codes(report)
    assert any(
        blocker.registry_key == item.registry_key
        for blocker in report.blockers
        if blocker.code == DisabledPipelineBlockerCode.ACTIONABLE_ITEM_FOUND
    )


def test_report_deterministic_json_round_trips() -> None:
    report = _report()
    same_report = _report()

    assert report.deterministic_json() == same_report.deterministic_json()
    assert DisabledPipelineReport.model_validate_json(report.deterministic_json()) == report


def test_report_fingerprint_is_deterministic_for_same_content() -> None:
    report = _report()
    same_report = _report()

    assert report.fingerprint_sha256() == same_report.fingerprint_sha256()
    assert len(report.fingerprint_sha256()) == 64


def test_report_fingerprint_changes_when_registry_snapshot_content_changes() -> None:
    report = _report()
    changed_registry = StrategyRuleSetRegistry(fixtures=_fixture_with_changed_description())
    changed_report = _report(DisabledPipelineReportShell(registry=changed_registry))

    assert report.fingerprint_sha256() != changed_report.fingerprint_sha256()


def test_blocker_ordering_is_deterministic() -> None:
    blockers = (
        DisabledPipelineBlocker(
            code=DisabledPipelineBlockerCode.RUNTIME_NOT_ALLOWED,
            message="b",
            severity=StrategyRuleSeverity.BLOCKING,
        ),
        DisabledPipelineBlocker(
            code=DisabledPipelineBlockerCode.REGISTRY_EMPTY,
            message="a",
            severity=StrategyRuleSeverity.BLOCKING,
        ),
    )
    report = DisabledPipelineReport(
        pipeline_version="phase4e-test",
        project_phase=constants.PROJECT_PHASE,
        status=DisabledPipelineStatus.BLOCKED,
        created_at=CREATED_AT,
        registry_item_count=0,
        valid_registry_item_count=0,
        invalid_registry_item_count=0,
        blockers=blockers,
        registry_snapshot_fingerprint="a" * 64,
    )

    assert _blocker_codes(report) == (
        DisabledPipelineBlockerCode.REGISTRY_EMPTY,
        DisabledPipelineBlockerCode.RUNTIME_NOT_ALLOWED,
    )


def test_shell_does_not_mutate_registry_fixtures() -> None:
    fixtures = dict(BUILTIN_STRATEGY_RULESET_FIXTURES)
    before = {key: ruleset.deterministic_json() for key, ruleset in fixtures.items()}

    DisabledPipelineReportShell(registry=StrategyRuleSetRegistry(fixtures=fixtures)).build_report(
        CREATED_AT
    )

    assert {key: ruleset.deterministic_json() for key, ruleset in fixtures.items()} == before


def test_shell_does_not_mutate_registry_snapshot() -> None:
    snapshot = _snapshot_from_registry()
    before = snapshot.deterministic_json()

    DisabledPipelineReportShell(registry=StaticSnapshotRegistry(snapshot)).build_report(CREATED_AT)

    assert snapshot.deterministic_json() == before


def test_report_model_has_no_decision_signal_price_or_scoring_fields() -> None:
    fields = set(DisabledPipelineReport.model_fields)

    assert fields.isdisjoint(
        {
            "decision",
            "recommendation",
            "signal_direction",
            "direction",
            "entry",
            "entry_price",
            "stop_loss",
            "take_profit",
            "target",
            "position_size",
            "setup_score",
            "confidence",
            "confidence_score",
            "broker",
            "paper_trade",
            "live_trade",
        }
    )


def test_report_rejects_runtime_enabled_or_actionable_flags() -> None:
    report = _report()
    enabled_values = report.model_dump()
    enabled_values["enabled_for_runtime"] = True
    actionable_values = report.model_dump()
    actionable_values["is_actionable"] = True

    with pytest.raises(ValidationError):
        DisabledPipelineReport(**enabled_values)
    with pytest.raises(ValidationError):
        DisabledPipelineReport(**actionable_values)
```

## Modified Test Coverage

- Phase assertion tests now expect `phase_4e_disabled_pipeline_report_shell_foundation`.
- Safety boundaries now include Phase 4E checks proving:
  - report shell objects are domain-only;
  - report shell signatures accept no market/context/runtime inputs;
  - report shell imports no FastAPI, SQLAlchemy, Telegram, scheduler, provider, OpenAI, or signal
    contract runtime dependencies;
  - report model has no decision, signal direction, price, entry/stop/target, setup score, or
    confidence fields;
  - no API routes, Telegram handlers, scheduler jobs, pipeline services, rule evaluation, signal
    generation, scoring, broker behavior, order execution, paper trading, or real trading were added.

## Exact Verification Command Outputs

Note: `uv` is installed at `/Users/artem.otsel/.local/bin/uv`. The Codex shell PATH did not include
that directory, so the commands below were executed through that installed binary while preserving
the requested command semantics.

### `uv lock --check`

Exit code: `0`

```text
Resolved 46 packages in 23ms
```

### `uv sync`

Exit code: `0`

```text
Resolved 46 packages in 3ms
Checked 43 packages in 10ms
```

### `uv run ruff format --check .`

Exit code: `0`

```text
122 files already formatted
```

### `uv run ruff check .`

Exit code: `0`

```text
All checks passed!
```

### `uv run mypy app`

Exit code: `0`

```text
Success: no issues found in 85 source files
```

### `uv run pytest`

Exit code: `0`

```text
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/artem.otsel/Documents/ai-trading-os
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.14.1, asyncio-0.26.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 345 items

tests/contract/test_agent_contracts.py ......                            [  1%]
tests/contract/test_api_error_schema.py .                                [  2%]
tests/contract/test_architecture_boundaries.py ..                        [  2%]
tests/contract/test_provider_contracts.py .............................. [ 11%]
...............................                                          [ 20%]
tests/contract/test_safety_boundaries.py ............................... [ 29%]
...................                                                      [ 34%]
tests/integration/test_database_and_api.py sssssss                       [ 36%]
tests/unit/test_analysis_snapshot_foundation.py ..........               [ 39%]
tests/unit/test_context_engine_foundation.py .............               [ 43%]
tests/unit/test_data_quality_foundation.py ...                           [ 44%]
tests/unit/test_disabled_pipeline_report_shell_foundation.py ........... [ 47%]
......                                                                   [ 49%]
tests/unit/test_domain_market_models.py ..................               [ 54%]
tests/unit/test_errors_and_redaction.py .......                          [ 56%]
tests/unit/test_feature_engine_foundation.py ...........                 [ 59%]
tests/unit/test_internal_api_key.py ....                                 [ 60%]
tests/unit/test_readiness_scheduler_foundation.py .........              [ 63%]
tests/unit/test_scheduled_digest_delivery_foundation.py ...........      [ 66%]
tests/unit/test_settings.py .........                                    [ 69%]
tests/unit/test_signal_contract_foundation.py ............               [ 72%]
tests/unit/test_strategy_rule_specification_foundation.py .............. [ 76%]
...........                                                              [ 80%]
tests/unit/test_strategy_ruleset_registry_foundation.py ................ [ 84%]
.                                                                        [ 84%]
tests/unit/test_strategy_ruleset_validation_foundation.py .............. [ 88%]
.......                                                                  [ 91%]
tests/unit/test_system_state_service.py .....                            [ 92%]
tests/unit/test_telegram_commands.py ........                            [ 94%]
tests/unit/test_telegram_policy.py .....                                 [ 96%]
tests/unit/test_time.py ...                                              [ 97%]
tests/unit/test_unit_of_work_lifecycle.py ......                         [ 98%]
tests/unit/test_value_objects_and_enums.py ....                          [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /Users/artem.otsel/Documents/ai-trading-os/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================== 338 passed, 7 skipped, 1 warning in 1.00s ===================
```

### `uv run python scripts/security_check.py`

Exit code: `0`

```text
<no output>
```

### `docker compose build`

Exit code: `0`

```text
 Image ai-trading-os-migrate Building 
 Image ai-trading-os-api Building 
 Image ai-trading-os-worker Building 
 Image ai-trading-os-bot Building 
#1 [internal] load local bake definitions
#1 reading from stdin 1.91kB done
#1 DONE 0.0s

#2 [api internal] load build definition from Dockerfile
#2 transferring dockerfile: 411B done
#2 DONE 0.0s

#3 [worker internal] load metadata for ghcr.io/astral-sh/uv:python3.12-bookworm-slim
#3 DONE 1.0s

#4 [migrate internal] load .dockerignore
#4 transferring context: 143B done
#4 DONE 0.0s

#5 [worker 1/5] FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58
#5 resolve ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58 0.0s done
#5 DONE 0.0s

#6 [api internal] load build context
#6 transferring context: 485.22kB 0.0s done
#6 DONE 0.0s

#7 [bot 3/5] COPY pyproject.toml uv.lock* ./
#7 CACHED

#8 [bot 2/5] WORKDIR /app
#8 CACHED

#9 [bot 4/5] RUN uv sync --frozen --no-dev
#9 CACHED

#10 [api 5/5] COPY . .
#10 DONE 0.1s

#11 [api] exporting to image
#11 exporting layers 0.1s done
#11 exporting manifest sha256:b84ef2412ccd04431a3299f1ee4d83a987d3925a85fadc69bd5f3edb28152811 done
#11 exporting config sha256:7dc3773044d891b53b75abba1f484aeca7fe622235104bb229cee79deeca7130 0.0s done
#11 exporting attestation manifest sha256:738285be0a28cc7359b8e78fbae75b730140931a3d99f529cb7516f8244b0bba 0.0s done
#11 exporting manifest list sha256:cfe21bf52fde6e75564f44a1fbc8ad2138f18e4cc506fa2b6540cacc7656012c
#11 exporting manifest list sha256:cfe21bf52fde6e75564f44a1fbc8ad2138f18e4cc506fa2b6540cacc7656012c done
#11 naming to docker.io/library/ai-trading-os-api:latest done
#11 unpacking to docker.io/library/ai-trading-os-api:latest 0.0s done
#11 DONE 0.2s

#12 [bot] exporting to image
#12 exporting layers 0.1s done
#12 exporting manifest sha256:cb99e55cd22738fd5eca1f5ddbfaccb36088fedd40a9a578d2037dca939d24c3 done
#12 exporting config sha256:12980fd46d1aabbd1a03b0f85dea35e65d60e6a9cae2fb398546c9d14efff6f7 0.0s done
#12 exporting attestation manifest sha256:42ced77055d3173a1b982b52002a1cedbcd3e4c2337b94b035edfa21bb4cd306 0.0s done
#12 exporting manifest list sha256:a8366a891dc00aa68e6061e910f33d6041f93c13ade80ceee7982758fa7f9e3d done
#12 naming to docker.io/library/ai-trading-os-bot:latest done
#12 unpacking to docker.io/library/ai-trading-os-bot:latest 0.0s done
#12 DONE 0.2s

#13 [migrate] exporting to image
#13 exporting layers 0.1s done
#13 exporting manifest sha256:f8c13c1ef9cc0dd2ac0ac3434e6a05386338a91ba2f188fd81dc1103efbc0797 0.0s done
#13 exporting config sha256:264a60965caba7dd39c1eecff570d2b60841da55122898ef69b8ac8e3d5edb03 0.0s done
#13 exporting attestation manifest sha256:4b2e65f4e8ceb69122426c926a24f71b64f7c8b7a308073ee32012519b5327e3 0.0s done
#13 exporting manifest list sha256:0ef8187b9891ca3aa2731234d968bc3133f12d65c73381553ac5cc3d2fcab779 done
#13 naming to docker.io/library/ai-trading-os-migrate:latest done
#13 unpacking to docker.io/library/ai-trading-os-migrate:latest 0.0s done
#13 DONE 0.2s

#14 [worker] exporting to image
#14 exporting layers 0.1s done
#14 exporting manifest sha256:0814165dcb3a760c496e7dc1156363a7de75c772da06eb36e1fdd3cf38ac0a26 done
#14 exporting config sha256:9468bb5bdf1d87d99bddfd861cc6bf3df9240e3314a7cc5146c558833d6b4bd7 0.0s done
#14 exporting attestation manifest sha256:261245fa2818d0cf2fd3194606308e4c5b2ea6c0530262d9a023ba038491b7a8 0.0s done
#14 exporting manifest list sha256:9c8b48ea4808e2d82fc92f1006a6249b10db4cc2184d1635c89d2bf3bdf7054c done
#14 naming to docker.io/library/ai-trading-os-worker:latest done
#14 unpacking to docker.io/library/ai-trading-os-worker:latest 0.0s done
#14 DONE 0.2s

#15 [bot] resolving provenance for metadata file
#15 DONE 0.0s

#16 [api] resolving provenance for metadata file
#16 DONE 0.0s

#17 [worker] resolving provenance for metadata file
#17 DONE 0.0s

#18 [migrate] resolving provenance for metadata file
#18 DONE 0.0s
 Image ai-trading-os-worker Built 
 Image ai-trading-os-api Built 
 Image ai-trading-os-bot Built 
 Image ai-trading-os-migrate Built 
```

### `docker compose up -d postgres`

Exit code: `0`

```text
 Network ai-trading-os_default Creating 
 Network ai-trading-os_default Created 
 Container ai-trading-os-postgres-1 Creating 
 Container ai-trading-os-postgres-1 Created 
 Container ai-trading-os-postgres-1 Starting 
 Container ai-trading-os-postgres-1 Started 
```

### `docker compose run --rm migrate alembic current`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-2c374609f246 Creating 
 Container ai-trading-os-migrate-run-2c374609f246 Created 
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
0003_phase3i_digest_audit (head)
```

### `docker compose run --rm migrate alembic check`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-a3977064d816 Creating 
 Container ai-trading-os-migrate-run-a3977064d816 Created 
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.schemas
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.tables
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.types
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.constraints
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.defaults
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.comments
No new upgrade operations detected.
```

### Test database migration

Command:
`docker compose run --rm -e DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate alembic upgrade head`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-e815ae7e36b9 Creating 
 Container ai-trading-os-migrate-run-e815ae7e36b9 Created 
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

### Docker integration tests run 1

Command:
`docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-4b76ce93fbca Creating 
 Container ai-trading-os-migrate-run-4b76ce93fbca Created 
Downloading pygments (1.2MiB)
Downloading ruff (10.5MiB)
Downloading mypy (13.1MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 90ms
Bytecode compiled 1963 files in 529ms
============================= test session starts ==============================
platform linux -- Python 3.12.12, pytest-8.4.2, pluggy-1.6.0
rootdir: /app
configfile: pyproject.toml
plugins: anyio-4.14.1, asyncio-0.26.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 7 items

tests/integration/test_database_and_api.py .......                       [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /app/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
========================= 7 passed, 1 warning in 0.69s =========================
```

### Docker integration tests run 2

Command:
`docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-249ab3e9d5ef Creating 
 Container ai-trading-os-migrate-run-249ab3e9d5ef Created 
Downloading pygments (1.2MiB)
Downloading mypy (13.1MiB)
Downloading ruff (10.5MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 46ms
Bytecode compiled 1963 files in 453ms
============================= test session starts ==============================
platform linux -- Python 3.12.12, pytest-8.4.2, pluggy-1.6.0
rootdir: /app
configfile: pyproject.toml
plugins: anyio-4.14.1, asyncio-0.26.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 7 items

tests/integration/test_database_and_api.py .......                       [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /app/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
========================= 7 passed, 1 warning in 0.39s =========================
```

### `docker compose config`

Exit code: `0`

```text
name: ai-trading-os
services:
  api:
    build:
      context: /Users/artem.otsel/Documents/ai-trading-os
      dockerfile: Dockerfile
    command:
      - uvicorn
      - app.main:create_app
      - --factory
      - --host
      - 0.0.0.0
      - --port
      - "8000"
    depends_on:
      migrate:
        condition: service_completed_successfully
        required: true
      postgres:
        condition: service_healthy
        required: true
    environment:
      APP_ENV: development
      APP_NAME: AI Trading OS
      APP_TIMEZONE: Europe/Stockholm
      CALENDAR_ENABLED: "false"
      DATABASE_URL: postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os
      FMP_API_KEY: ""
      FMP_BASE_URL: https://financialmodelingprep.com
      INTERNAL_API_KEY: development-internal-key-change-me
      LOG_LEVEL: INFO
      MARKET_DATA_ENABLED: "false"
      MAX_CONSECUTIVE_LOSSES: "3"
      MAX_DAILY_LOSS_PERCENT: "1.5"
      MAX_OPEN_RISK_PERCENT: "1.0"
      MAX_WEEKLY_LOSS_PERCENT: "4.0"
      OPENAI_API_KEY: ""
      OPENAI_ENABLED: "false"
      OPENAI_MODEL: gpt-4.1
      PAPER_ACCOUNT_BALANCE: "10000"
      PAPER_ACCOUNT_CURRENCY: EUR
      PAPER_RISK_PERCENT: "0.5"
      PROVIDER_CONNECT_TIMEOUT_SECONDS: "5"
      PROVIDER_MAX_REQUEST_RANGE_DAYS: "31"
      PROVIDER_POOL_TIMEOUT_SECONDS: "5"
      PROVIDER_READ_TIMEOUT_SECONDS: "10"
      PROVIDER_RETRY_BACKOFF_SECONDS: "0.1"
      PROVIDER_RETRY_COUNT: "2"
      PROVIDER_WRITE_TIMEOUT_SECONDS: "5"
      REQUIRE_INTEGRATION_TESTS: "false"
      SCAN_ENABLED: "false"
      SERVICE_NAME: api
      SETUP_SCORE_THRESHOLD: "85"
      SIGNAL_VALID_MINUTES: "30"
      STORAGE_TIMEZONE: UTC
      TELEGRAM_ALLOWED_CHAT_ID: ""
      TELEGRAM_ALLOWED_USER_ID: ""
      TELEGRAM_BOT_TOKEN: ""
      TELEGRAM_ENABLED: "false"
      TEST_DATABASE_URL: postgresql+asyncpg://ai_trading_os:ai_trading_os@localhost:5432/ai_trading_os_test
      TWELVE_DATA_API_KEY: ""
      TWELVE_DATA_BASE_URL: https://api.twelvedata.com
    healthcheck:
      test:
        - CMD
        - python
        - -c
        - import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)
      timeout: 5s
      interval: 10s
      retries: 12
    networks:
      default: null
    ports:
      - mode: ingress
        host_ip: 127.0.0.1
        target: 8000
        published: "8000"
        protocol: tcp
  bot:
    build:
      context: /Users/artem.otsel/Documents/ai-trading-os
      dockerfile: Dockerfile
    command:
      - python
      - -m
      - app.telegram.bot
    depends_on:
      migrate:
        condition: service_completed_successfully
        required: true
      postgres:
        condition: service_healthy
        required: true
    environment:
      APP_ENV: development
      APP_NAME: AI Trading OS
      APP_TIMEZONE: Europe/Stockholm
      CALENDAR_ENABLED: "false"
      DATABASE_URL: postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os
      FMP_API_KEY: ""
      FMP_BASE_URL: https://financialmodelingprep.com
      INTERNAL_API_KEY: development-internal-key-change-me
      LOG_LEVEL: INFO
      MARKET_DATA_ENABLED: "false"
      MAX_CONSECUTIVE_LOSSES: "3"
      MAX_DAILY_LOSS_PERCENT: "1.5"
      MAX_OPEN_RISK_PERCENT: "1.0"
      MAX_WEEKLY_LOSS_PERCENT: "4.0"
      OPENAI_API_KEY: ""
      OPENAI_ENABLED: "false"
      OPENAI_MODEL: gpt-4.1
      PAPER_ACCOUNT_BALANCE: "10000"
      PAPER_ACCOUNT_CURRENCY: EUR
      PAPER_RISK_PERCENT: "0.5"
      PROVIDER_CONNECT_TIMEOUT_SECONDS: "5"
      PROVIDER_MAX_REQUEST_RANGE_DAYS: "31"
      PROVIDER_POOL_TIMEOUT_SECONDS: "5"
      PROVIDER_READ_TIMEOUT_SECONDS: "10"
      PROVIDER_RETRY_BACKOFF_SECONDS: "0.1"
      PROVIDER_RETRY_COUNT: "2"
      PROVIDER_WRITE_TIMEOUT_SECONDS: "5"
      REQUIRE_INTEGRATION_TESTS: "false"
      SCAN_ENABLED: "false"
      SERVICE_NAME: bot
      SETUP_SCORE_THRESHOLD: "85"
      SIGNAL_VALID_MINUTES: "30"
      STORAGE_TIMEZONE: UTC
      TELEGRAM_ALLOWED_CHAT_ID: ""
      TELEGRAM_ALLOWED_USER_ID: ""
      TELEGRAM_BOT_TOKEN: ""
      TELEGRAM_ENABLED: "false"
      TEST_DATABASE_URL: postgresql+asyncpg://ai_trading_os:ai_trading_os@localhost:5432/ai_trading_os_test
      TWELVE_DATA_API_KEY: ""
      TWELVE_DATA_BASE_URL: https://api.twelvedata.com
    healthcheck:
      test:
        - CMD
        - python
        - scripts/process_health.py
        - app.telegram.bot
      timeout: 5s
      interval: 30s
      retries: 3
    networks:
      default: null
  migrate:
    build:
      context: /Users/artem.otsel/Documents/ai-trading-os
      dockerfile: Dockerfile
    command:
      - alembic
      - upgrade
      - head
    depends_on:
      postgres:
        condition: service_healthy
        required: true
    environment:
      APP_ENV: development
      APP_NAME: AI Trading OS
      APP_TIMEZONE: Europe/Stockholm
      CALENDAR_ENABLED: "false"
      DATABASE_URL: postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os
      FMP_API_KEY: ""
      FMP_BASE_URL: https://financialmodelingprep.com
      INTERNAL_API_KEY: development-internal-key-change-me
      LOG_LEVEL: INFO
      MARKET_DATA_ENABLED: "false"
      MAX_CONSECUTIVE_LOSSES: "3"
      MAX_DAILY_LOSS_PERCENT: "1.5"
      MAX_OPEN_RISK_PERCENT: "1.0"
      MAX_WEEKLY_LOSS_PERCENT: "4.0"
      OPENAI_API_KEY: ""
      OPENAI_ENABLED: "false"
      OPENAI_MODEL: gpt-4.1
      PAPER_ACCOUNT_BALANCE: "10000"
      PAPER_ACCOUNT_CURRENCY: EUR
      PAPER_RISK_PERCENT: "0.5"
      PROVIDER_CONNECT_TIMEOUT_SECONDS: "5"
      PROVIDER_MAX_REQUEST_RANGE_DAYS: "31"
      PROVIDER_POOL_TIMEOUT_SECONDS: "5"
      PROVIDER_READ_TIMEOUT_SECONDS: "10"
      PROVIDER_RETRY_BACKOFF_SECONDS: "0.1"
      PROVIDER_RETRY_COUNT: "2"
      PROVIDER_WRITE_TIMEOUT_SECONDS: "5"
      REQUIRE_INTEGRATION_TESTS: "false"
      SCAN_ENABLED: "false"
      SERVICE_NAME: migrate
      SETUP_SCORE_THRESHOLD: "85"
      SIGNAL_VALID_MINUTES: "30"
      STORAGE_TIMEZONE: UTC
      TELEGRAM_ALLOWED_CHAT_ID: ""
      TELEGRAM_ALLOWED_USER_ID: ""
      TELEGRAM_BOT_TOKEN: ""
      TELEGRAM_ENABLED: "false"
      TEST_DATABASE_URL: postgresql+asyncpg://ai_trading_os:ai_trading_os@localhost:5432/ai_trading_os_test
      TWELVE_DATA_API_KEY: ""
      TWELVE_DATA_BASE_URL: https://api.twelvedata.com
    networks:
      default: null
  postgres:
    environment:
      POSTGRES_DB: ai_trading_os
      POSTGRES_PASSWORD: ai_trading_os
      POSTGRES_USER: ai_trading_os
    healthcheck:
      test:
        - CMD-SHELL
        - pg_isready -U ai_trading_os -d ai_trading_os
      timeout: 3s
      interval: 5s
      retries: 20
    image: postgres:16-alpine
    networks:
      default: null
    volumes:
      - type: volume
        source: postgres_data
        target: /var/lib/postgresql/data
        volume: {}
  worker:
    build:
      context: /Users/artem.otsel/Documents/ai-trading-os
      dockerfile: Dockerfile
    command:
      - python
      - -m
      - app.scheduler.worker
    depends_on:
      migrate:
        condition: service_completed_successfully
        required: true
      postgres:
        condition: service_healthy
        required: true
    environment:
      APP_ENV: development
      APP_NAME: AI Trading OS
      APP_TIMEZONE: Europe/Stockholm
      CALENDAR_ENABLED: "false"
      DATABASE_URL: postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os
      FMP_API_KEY: ""
      FMP_BASE_URL: https://financialmodelingprep.com
      INTERNAL_API_KEY: development-internal-key-change-me
      LOG_LEVEL: INFO
      MARKET_DATA_ENABLED: "false"
      MAX_CONSECUTIVE_LOSSES: "3"
      MAX_DAILY_LOSS_PERCENT: "1.5"
      MAX_OPEN_RISK_PERCENT: "1.0"
      MAX_WEEKLY_LOSS_PERCENT: "4.0"
      OPENAI_API_KEY: ""
      OPENAI_ENABLED: "false"
      OPENAI_MODEL: gpt-4.1
      PAPER_ACCOUNT_BALANCE: "10000"
      PAPER_ACCOUNT_CURRENCY: EUR
      PAPER_RISK_PERCENT: "0.5"
      PROVIDER_CONNECT_TIMEOUT_SECONDS: "5"
      PROVIDER_MAX_REQUEST_RANGE_DAYS: "31"
      PROVIDER_POOL_TIMEOUT_SECONDS: "5"
      PROVIDER_READ_TIMEOUT_SECONDS: "10"
      PROVIDER_RETRY_BACKOFF_SECONDS: "0.1"
      PROVIDER_RETRY_COUNT: "2"
      PROVIDER_WRITE_TIMEOUT_SECONDS: "5"
      REQUIRE_INTEGRATION_TESTS: "false"
      SCAN_ENABLED: "false"
      SERVICE_NAME: worker
      SETUP_SCORE_THRESHOLD: "85"
      SIGNAL_VALID_MINUTES: "30"
      STORAGE_TIMEZONE: UTC
      TELEGRAM_ALLOWED_CHAT_ID: ""
      TELEGRAM_ALLOWED_USER_ID: ""
      TELEGRAM_BOT_TOKEN: ""
      TELEGRAM_ENABLED: "false"
      TEST_DATABASE_URL: postgresql+asyncpg://ai_trading_os:ai_trading_os@localhost:5432/ai_trading_os_test
      TWELVE_DATA_API_KEY: ""
      TWELVE_DATA_BASE_URL: https://api.twelvedata.com
    networks:
      default: null
networks:
  default:
    name: ai-trading-os_default
volumes:
  postgres_data:
    name: ai-trading-os_postgres_data
```

## Skipped Checks

- Host `uv run pytest` skipped 7 integration tests because host integration tests require
  `REQUIRE_INTEGRATION_TESTS=true`. The same integration file was run twice in Docker against
  PostgreSQL and passed both times.

## Unavailable Checks

- None for the requested Phase 4E verification set. Docker, PostgreSQL, Alembic, host checks, and
  Docker integration checks all ran.

## Remaining Risks

- Phase 4E intentionally exposes no API route or runtime service. It is a domain report shell
  foundation exercised through tests in this phase.
- Existing compose configuration still contains disabled future configuration keys. Phase 4E did
  not activate them.

## Explicit Safety Confirmations

- Phase 4E is disabled report-shell-only.
- Phase 3J API route is absent.
- Phase 4F and later phases were not started.
- No rule evaluation against market data was added.
- No strategy engine or decision engine was added.
- No signal generation was added.
- No setup scoring or confidence scoring was added.
- No AI agents, OpenAI calls, or LLM calls were added.
- No Telegram signal delivery was added.
- No broker APIs were added.
- No paper trading, order execution, live trading, or real trading was added.
- Pipeline reports remain disabled/non-actionable.

## Traceability

| Requirement | Implementation file | Test file | Verification result |
| --- | --- | --- | --- |
| Update project phase to Phase 4E | `app/core/constants.py` | `tests/unit/test_disabled_pipeline_report_shell_foundation.py` and phase assertion updates | Passed in `uv run pytest` |
| Immutable blocker/report models | `app/domain/entities/pipeline_report.py` | `tests/unit/test_disabled_pipeline_report_shell_foundation.py` | Passed |
| UTC report timestamp normalization | `app/domain/entities/pipeline_report.py` | `tests/unit/test_disabled_pipeline_report_shell_foundation.py` | Passed |
| Default shell remains disabled | `app/domain/disabled_pipeline_report_shell.py` | `tests/unit/test_disabled_pipeline_report_shell_foundation.py` | Passed |
| Default report includes disabled blocker | `app/domain/disabled_pipeline_report_shell.py` | `tests/unit/test_disabled_pipeline_report_shell_foundation.py` | Passed |
| `enabled=True` request does not activate runtime behavior | `app/domain/disabled_pipeline_report_shell.py` | `tests/unit/test_disabled_pipeline_report_shell_foundation.py` | Passed |
| Report includes Phase 4D registry counts and fingerprint | `app/domain/disabled_pipeline_report_shell.py` | `tests/unit/test_disabled_pipeline_report_shell_foundation.py` | Passed |
| Empty, invalid, and actionable registry states become blockers | `app/domain/disabled_pipeline_report_shell.py` | `tests/unit/test_disabled_pipeline_report_shell_foundation.py` | Passed |
| Deterministic JSON and SHA-256 fingerprint | `app/domain/entities/pipeline_report.py` | `tests/unit/test_disabled_pipeline_report_shell_foundation.py` | Passed |
| Fingerprint changes when registry snapshot content changes | `app/domain/entities/pipeline_report.py`, `app/domain/disabled_pipeline_report_shell.py` | `tests/unit/test_disabled_pipeline_report_shell_foundation.py` | Passed |
| Shell does not mutate registry fixtures or snapshots | `app/domain/disabled_pipeline_report_shell.py` | `tests/unit/test_disabled_pipeline_report_shell_foundation.py` | Passed |
| Report model has no decision/signal/price/scoring fields | `app/domain/entities/pipeline_report.py` | `tests/unit/test_disabled_pipeline_report_shell_foundation.py`, `tests/contract/test_safety_boundaries.py` | Passed |
| Domain-only report shell dependencies | `app/domain/entities/pipeline_report.py`, `app/domain/disabled_pipeline_report_shell.py` | `tests/contract/test_safety_boundaries.py` | Passed |
| No API routes, Telegram handlers, scheduler jobs, services, broker/order/paper/live behavior | No runtime files added | `tests/contract/test_safety_boundaries.py`, `scripts/security_check.py` | Passed |
| Existing Phase 4A/4B/4C/4D tests still pass | Existing domain files | Existing unit tests | Passed |
| Existing `/snapshot`, `/digest`, readiness/digest foundations still pass | Existing Telegram/readiness files | Existing unit and integration tests | Passed |
