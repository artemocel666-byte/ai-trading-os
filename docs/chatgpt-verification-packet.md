# ChatGPT Verification Packet - Phase 4D

Generated: 2026-07-18T14:30:22Z

## Current Scope

Phase 4D is strategy ruleset registry and fixture foundation only.

`PROJECT_PHASE = "phase_4d_strategy_ruleset_registry_foundation"`

Phase 4D adds deterministic registry models and a built-in registry of disabled
`StrategyRuleSet` fixtures. Each fixture validates through the Phase 4C
`StrategyRuleSetValidator`.

Phase 4D does not evaluate rules against market data, candles, indicators, economic events,
context snapshots, analysis snapshots, or signal contracts. It does not generate signals, does not
provide trading recommendations, does not calculate entries/stops/targets, does not calculate
position size, does not calculate setup score or confidence, does not call AI/OpenAI/LLM services,
does not send Telegram signals, does not use broker APIs, does not execute orders, and does not
enable paper or real trading.

Phase 3J was not created or restored. Phase 4E and later work was not started. Phase 4D is
uncommitted at packet generation time.

## Git Metadata

- Branch: `main`
- Current commit hash: `3f1cf6aa55ea52469f27066364542577a07b110a`
- Current commit short: `3f1cf6a Add Phase 4C strategy ruleset validation foundation`

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
 M tests/unit/test_strategy_ruleset_validation_foundation.py
?? app/domain/entities/strategy_registry.py
?? app/domain/strategy_ruleset_registry.py
?? docs/phase4d-verification-report.md
?? tests/unit/test_strategy_ruleset_registry_foundation.py
```

`git diff --stat` captured before final packet rewrite:

```text
 AGENTS.md                                          |  25 ++--
 PLANS.md                                           |  21 ++-
 README.md                                          |  19 ++-
 app/core/constants.py                              |   2 +-
 app/domain/entities/__init__.py                    |   6 +
 docs/operations.md                                 |   9 ++
 tests/contract/test_safety_boundaries.py           | 164 ++++++++++++++++++++-
 tests/unit/test_signal_contract_foundation.py      |   4 +-
 .../test_strategy_rule_specification_foundation.py |   4 +-
 .../test_strategy_ruleset_validation_foundation.py |   4 +-
 10 files changed, 230 insertions(+), 28 deletions(-)
```

## Created Files

- `app/domain/entities/strategy_registry.py`
- `app/domain/strategy_ruleset_registry.py`
- `docs/phase4d-verification-report.md`
- `tests/unit/test_strategy_ruleset_registry_foundation.py`

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
- `tests/unit/test_strategy_ruleset_validation_foundation.py`

## Migration Files

No migration files were created or modified for Phase 4D.

Current Docker Alembic head remained:

```text
0003_phase3i_digest_audit (head)
```

## Full Contents Of Changed Source Files

### `app/core/constants.py`

```python
PROJECT_PHASE = "phase_4d_strategy_ruleset_registry_foundation"
STRATEGY_IMPLEMENTED = False
REAL_TRADING_ENABLED = False

SYSTEM_STATE_SCAN_ENABLED = "scan_enabled"
SYSTEM_STATE_WORKER_HEARTBEAT = "worker_heartbeat"
SYSTEM_STATE_LAST_SUCCESSFUL_MARKET_FETCH = "last_successful_market_fetch"
SYSTEM_STATE_LAST_SUCCESSFUL_CALENDAR_FETCH = "last_successful_calendar_fetch"
SYSTEM_STATE_LAST_ERROR = "last_error"

DEFAULT_STRATEGY_VERSION = "foundation-v1"
```

### `app/domain/entities/strategy_registry.py`

```python
import hashlib
import json
from datetime import datetime
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.strategy_rules import StrategyRuleSet
from app.domain.entities.strategy_validation import (
    StrategyRuleSetValidationReport,
    StrategyRuleSetValidationStatus,
)


def _normalize_registry_key(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("registry_key must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError("registry_key must be non-empty")
    return normalized


class StrategyRuleSetRegistryItem(BaseModel):
    registry_key: str = Field(pattern=r"^[a-z0-9](?:[a-z0-9_.-]*[a-z0-9])?$")
    ruleset: StrategyRuleSet
    validation_report: StrategyRuleSetValidationReport
    enabled_for_runtime: bool = False
    is_actionable: bool = False

    model_config = ConfigDict(frozen=True)

    @field_validator("registry_key", mode="before")
    @classmethod
    def normalize_key(cls, value: object) -> str:
        return _normalize_registry_key(value)

    @model_validator(mode="after")
    def require_non_actionable_item(self) -> Self:
        if self.enabled_for_runtime:
            raise ValueError("registry items must remain disabled for runtime use")
        if self.is_actionable:
            raise ValueError("registry items must remain non-actionable")
        return self


class StrategyRuleSetRegistrySnapshot(BaseModel):
    created_at: datetime
    items: tuple[StrategyRuleSetRegistryItem, ...] = ()
    item_count: int = Field(ge=0)
    valid_count: int = Field(ge=0)
    invalid_count: int = Field(ge=0)
    fingerprint: str | None = Field(default=None, min_length=64, max_length=64)
    is_actionable: bool = False

    model_config = ConfigDict(frozen=True)

    @field_validator("created_at")
    @classmethod
    def created_at_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("items")
    @classmethod
    def normalize_items(
        cls,
        value: tuple[StrategyRuleSetRegistryItem, ...],
    ) -> tuple[StrategyRuleSetRegistryItem, ...]:
        return tuple(sorted(value, key=lambda item: item.registry_key))

    @model_validator(mode="after")
    def validate_counts_and_flags(self) -> Self:
        keys = [item.registry_key for item in self.items]
        if len(keys) != len(set(keys)):
            raise ValueError("registry snapshot item keys must be unique")
        valid_count = sum(
            1
            for item in self.items
            if item.validation_report.status == StrategyRuleSetValidationStatus.VALID
        )
        invalid_count = len(self.items) - valid_count
        if self.item_count != len(self.items):
            raise ValueError("item_count must match registry snapshot item length")
        if self.valid_count != valid_count:
            raise ValueError("valid_count must match VALID registry items")
        if self.invalid_count != invalid_count:
            raise ValueError("invalid_count must match non-VALID registry items")
        if self.is_actionable:
            raise ValueError("registry snapshots must remain non-actionable")
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

### `app/domain/strategy_ruleset_registry.py`

```python
from collections.abc import Mapping
from datetime import UTC, datetime
from types import MappingProxyType

from app.core.constants import DEFAULT_STRATEGY_VERSION
from app.core.time import normalize_to_utc
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
from app.domain.entities.strategy_validation import StrategyRuleSetValidationStatus
from app.domain.strategy_ruleset_validator import StrategyRuleSetValidator

BUILTIN_RULESET_CREATED_AT = datetime(2026, 7, 18, 0, 0, tzinfo=UTC)


def _foundation_rule(
    *,
    rule_id: str,
    category: StrategyRuleCategory,
    severity: StrategyRuleSeverity,
    field_ref: str,
    operator: StrategyRuleOperator,
    description: str,
    allowed_values: tuple[str, ...] | None = None,
) -> StrategyRuleSpec:
    return StrategyRuleSpec(
        rule_id=rule_id,
        category=category,
        severity=severity,
        condition=StrategyRuleCondition(
            field_ref=field_ref,
            operator=operator,
            allowed_values=(
                StrategyRuleValue(value=allowed_values) if allowed_values is not None else None
            ),
        ),
        description=description,
        enabled=False,
    )


BUILTIN_STRATEGY_RULESET_FIXTURES: Mapping[str, StrategyRuleSet] = MappingProxyType(
    {
        "foundation.data_quality.minimum": StrategyRuleSet(
            ruleset_version="foundation-data-quality-v1",
            strategy_version=DEFAULT_STRATEGY_VERSION,
            name="Foundation data-quality minimum",
            description="Disabled structural fixture for data-quality references.",
            created_at=BUILTIN_RULESET_CREATED_AT,
            rules=(
                _foundation_rule(
                    rule_id="data_quality.closed_candles_available",
                    category=StrategyRuleCategory.DATA_QUALITY,
                    severity=StrategyRuleSeverity.REQUIRED,
                    field_ref="data_quality.closed_candles_available",
                    operator=StrategyRuleOperator.EXISTS,
                    description=(
                        "Validate that closed-candle availability can be referenced by a "
                        "disabled rule specification."
                    ),
                ),
            ),
            enabled=False,
        ),
        "foundation.market_context.minimum": StrategyRuleSet(
            ruleset_version="foundation-market-context-v1",
            strategy_version=DEFAULT_STRATEGY_VERSION,
            name="Foundation market-context minimum",
            description="Disabled structural fixture for market-context references.",
            created_at=BUILTIN_RULESET_CREATED_AT,
            rules=(
                _foundation_rule(
                    rule_id="market_context.snapshot_ready",
                    category=StrategyRuleCategory.MARKET_CONTEXT,
                    severity=StrategyRuleSeverity.REQUIRED,
                    field_ref="market_context.snapshot_ready",
                    operator=StrategyRuleOperator.EXISTS,
                    description=(
                        "Validate that market-context readiness can be referenced by a "
                        "disabled rule specification."
                    ),
                ),
            ),
            enabled=False,
        ),
        "foundation.time_filter.session": StrategyRuleSet(
            ruleset_version="foundation-time-filter-v1",
            strategy_version=DEFAULT_STRATEGY_VERSION,
            name="Foundation time-filter session",
            description="Disabled structural fixture for session label references.",
            created_at=BUILTIN_RULESET_CREATED_AT,
            rules=(
                _foundation_rule(
                    rule_id="time_filter.session_name_allowed",
                    category=StrategyRuleCategory.TIME_FILTER,
                    severity=StrategyRuleSeverity.WARNING,
                    field_ref="time_filter.session_name",
                    operator=StrategyRuleOperator.IN,
                    allowed_values=("london", "new_york"),
                    description=(
                        "Validate that allowed session labels can be referenced by a "
                        "disabled rule specification."
                    ),
                ),
            ),
            enabled=False,
        ),
    }
)


class StrategyRuleSetRegistry:
    def __init__(
        self,
        fixtures: Mapping[str, StrategyRuleSet] | None = None,
        validator: StrategyRuleSetValidator | None = None,
    ) -> None:
        fixture_source = fixtures if fixtures is not None else BUILTIN_STRATEGY_RULESET_FIXTURES
        self._fixtures = MappingProxyType(dict(fixture_source))
        self._validator = validator or StrategyRuleSetValidator()

    def list_keys(self) -> tuple[str, ...]:
        return tuple(sorted(self._fixtures))

    def get_by_key(
        self,
        key: str,
        checked_at: datetime,
    ) -> StrategyRuleSetRegistryItem | None:
        ruleset = self._fixtures.get(key.strip())
        if ruleset is None:
            return None
        return self._build_item(key.strip(), ruleset, checked_at)

    def load_builtin_rulesets(self, checked_at: datetime) -> StrategyRuleSetRegistrySnapshot:
        normalized_checked_at = normalize_to_utc(checked_at)
        items = tuple(
            self._build_item(key, self._fixtures[key], normalized_checked_at)
            for key in self.list_keys()
        )
        valid_count = sum(
            1
            for item in items
            if item.validation_report.status == StrategyRuleSetValidationStatus.VALID
        )
        return StrategyRuleSetRegistrySnapshot(
            created_at=normalized_checked_at,
            items=items,
            item_count=len(items),
            valid_count=valid_count,
            invalid_count=len(items) - valid_count,
        )

    def _build_item(
        self,
        key: str,
        ruleset: StrategyRuleSet,
        checked_at: datetime,
    ) -> StrategyRuleSetRegistryItem:
        validation_report = self._validator.validate(ruleset, checked_at)
        return StrategyRuleSetRegistryItem(
            registry_key=key,
            ruleset=ruleset,
            validation_report=validation_report,
            enabled_for_runtime=False,
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

### `tests/unit/test_strategy_ruleset_registry_foundation.py`

```python
from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.entities.strategy_registry import (
    StrategyRuleSetRegistryItem,
    StrategyRuleSetRegistrySnapshot,
)
from app.domain.entities.strategy_rules import StrategyRuleSet
from app.domain.entities.strategy_validation import StrategyRuleSetValidationStatus
from app.domain.strategy_ruleset_registry import (
    BUILTIN_STRATEGY_RULESET_FIXTURES,
    StrategyRuleSetRegistry,
)
from app.domain.strategy_ruleset_validator import StrategyRuleSetValidator

CHECKED_AT = datetime(2026, 7, 18, 10, 0, tzinfo=UTC)
EXPECTED_KEYS = (
    "foundation.data_quality.minimum",
    "foundation.market_context.minimum",
    "foundation.time_filter.session",
)


def _snapshot(
    registry: StrategyRuleSetRegistry | None = None,
    checked_at: datetime = CHECKED_AT,
) -> StrategyRuleSetRegistrySnapshot:
    return (registry or StrategyRuleSetRegistry()).load_builtin_rulesets(checked_at)


def _fixture_with_changed_description() -> dict[str, StrategyRuleSet]:
    fixtures = dict(BUILTIN_STRATEGY_RULESET_FIXTURES)
    base_ruleset = fixtures["foundation.data_quality.minimum"]
    changed_rule = base_ruleset.rules[0].model_copy(
        update={"description": "Validate an alternate disabled structural fixture."}
    )
    fixtures["foundation.data_quality.minimum"] = base_ruleset.model_copy(
        update={"rules": (changed_rule,)}
    )
    return fixtures


def test_project_phase_is_phase4d_strategy_ruleset_registry_foundation() -> None:
    assert constants.PROJECT_PHASE == "phase_4d_strategy_ruleset_registry_foundation"


def test_registry_item_and_snapshot_models_are_immutable() -> None:
    snapshot = _snapshot()
    item = snapshot.items[0]

    with pytest.raises(ValidationError):
        item.registry_key = "changed"
    with pytest.raises(ValidationError):
        snapshot.item_count = 0


def test_registry_snapshot_normalizes_created_at_to_utc() -> None:
    offset = timezone(timedelta(hours=2))
    snapshot = _snapshot(checked_at=datetime(2026, 7, 18, 12, 0, tzinfo=offset))

    assert snapshot.created_at == CHECKED_AT
    assert {item.validation_report.checked_at for item in snapshot.items} == {CHECKED_AT}


def test_builtin_registry_keys_are_deterministic() -> None:
    registry = StrategyRuleSetRegistry()

    assert registry.list_keys() == EXPECTED_KEYS
    assert (
        StrategyRuleSetRegistry(
            fixtures=dict(reversed(BUILTIN_STRATEGY_RULESET_FIXTURES.items()))
        ).list_keys()
        == EXPECTED_KEYS
    )


def test_load_builtin_rulesets_returns_deterministic_item_ordering() -> None:
    snapshot = _snapshot()

    assert tuple(item.registry_key for item in snapshot.items) == EXPECTED_KEYS


def test_all_builtin_fixtures_and_rules_are_disabled() -> None:
    snapshot = _snapshot()

    assert all(item.enabled_for_runtime is False for item in snapshot.items)
    assert all(item.ruleset.enabled is False for item in snapshot.items)
    assert all(rule.enabled is False for item in snapshot.items for rule in item.ruleset.rules)


def test_all_builtin_fixtures_validate_valid_through_phase4c_validator() -> None:
    snapshot = _snapshot()

    assert snapshot.item_count == 3
    assert snapshot.valid_count == 3
    assert snapshot.invalid_count == 0
    assert {item.validation_report.status for item in snapshot.items} == {
        StrategyRuleSetValidationStatus.VALID
    }


def test_registry_item_and_snapshot_are_not_actionable() -> None:
    snapshot = _snapshot()

    assert snapshot.is_actionable is False
    assert all(item.is_actionable is False for item in snapshot.items)


def test_get_by_key_returns_expected_item() -> None:
    item = StrategyRuleSetRegistry().get_by_key(
        "foundation.time_filter.session",
        CHECKED_AT,
    )

    assert item is not None
    assert item.registry_key == "foundation.time_filter.session"
    assert item.ruleset == BUILTIN_STRATEGY_RULESET_FIXTURES["foundation.time_filter.session"]
    assert item.validation_report.status == StrategyRuleSetValidationStatus.VALID


def test_get_by_key_unknown_key_returns_none() -> None:
    assert StrategyRuleSetRegistry().get_by_key("unknown.key", CHECKED_AT) is None


def test_registry_snapshot_deterministic_json_round_trips() -> None:
    snapshot = _snapshot()
    same_snapshot = _snapshot()

    assert snapshot.deterministic_json() == same_snapshot.deterministic_json()
    assert (
        StrategyRuleSetRegistrySnapshot.model_validate_json(snapshot.deterministic_json())
        == snapshot
    )


def test_registry_snapshot_fingerprint_is_deterministic_for_same_content() -> None:
    snapshot = _snapshot()
    same_snapshot = _snapshot()

    assert snapshot.fingerprint_sha256() == same_snapshot.fingerprint_sha256()
    assert len(snapshot.fingerprint_sha256()) == 64


def test_registry_snapshot_fingerprint_changes_when_fixture_content_changes() -> None:
    snapshot = _snapshot()
    changed_snapshot = _snapshot(
        StrategyRuleSetRegistry(fixtures=_fixture_with_changed_description())
    )

    assert snapshot.fingerprint_sha256() != changed_snapshot.fingerprint_sha256()


def test_registry_does_not_mutate_rulesets() -> None:
    fixtures = dict(BUILTIN_STRATEGY_RULESET_FIXTURES)
    before = {key: ruleset.deterministic_json() for key, ruleset in fixtures.items()}

    StrategyRuleSetRegistry(fixtures=fixtures).load_builtin_rulesets(CHECKED_AT)

    assert {key: ruleset.deterministic_json() for key, ruleset in fixtures.items()} == before


def test_invalid_fixture_still_appears_with_invalid_report() -> None:
    fixtures = dict(BUILTIN_STRATEGY_RULESET_FIXTURES)
    invalid_ruleset = fixtures["foundation.data_quality.minimum"].model_copy(
        update={"enabled": True}
    )
    fixtures["foundation.data_quality.minimum"] = invalid_ruleset

    snapshot = _snapshot(StrategyRuleSetRegistry(fixtures=fixtures))

    invalid_item = snapshot.items[0]
    assert invalid_item.registry_key == "foundation.data_quality.minimum"
    assert invalid_item.validation_report.status == StrategyRuleSetValidationStatus.INVALID
    assert snapshot.invalid_count == 1
    assert snapshot.valid_count == 2


def test_registry_rejects_actionable_models() -> None:
    snapshot = _snapshot()
    item = snapshot.items[0]

    with pytest.raises(ValidationError):
        StrategyRuleSetRegistryItem(
            registry_key=item.registry_key,
            ruleset=item.ruleset,
            validation_report=item.validation_report,
            enabled_for_runtime=True,
        )
    with pytest.raises(ValidationError):
        StrategyRuleSetRegistrySnapshot(
            created_at=snapshot.created_at,
            items=snapshot.items,
            item_count=snapshot.item_count,
            valid_count=snapshot.valid_count,
            invalid_count=snapshot.invalid_count,
            is_actionable=True,
        )


def test_registry_uses_strategy_ruleset_validator_without_market_inputs() -> None:
    class RecordingValidator(StrategyRuleSetValidator):
        def __init__(self) -> None:
            self.seen_rulesets: list[StrategyRuleSet] = []

        def validate(
            self,
            ruleset: StrategyRuleSet,
            checked_at: datetime,
        ):
            self.seen_rulesets.append(ruleset)
            return super().validate(ruleset, checked_at)

    validator = RecordingValidator()
    StrategyRuleSetRegistry(validator=validator).load_builtin_rulesets(CHECKED_AT)

    assert len(validator.seen_rulesets) == len(EXPECTED_KEYS)
    assert all(isinstance(ruleset, StrategyRuleSet) for ruleset in validator.seen_rulesets)
```

## Modified Test Coverage

- Phase assertion tests now expect `phase_4d_strategy_ruleset_registry_foundation`.
- Safety boundaries now include Phase 4D checks proving:
  - registry objects are domain-only;
  - registry signatures accept only keys and timestamps, not market/context/runtime inputs;
  - registry module imports no FastAPI, SQLAlchemy, Telegram, scheduler, provider, OpenAI, or
    signal-contract runtime dependencies;
  - no API routes, Telegram handlers, scheduler jobs, strategy registry services, rule evaluation,
    signal generation, scoring, broker behavior, order execution, paper trading, or real trading
    were added.

## Exact Verification Command Outputs

Note: `uv` is installed at `/Users/artem.otsel/.local/bin/uv`. The Codex shell PATH did not include
that directory, so the commands below were executed through that installed binary while preserving
the requested command semantics.

### `uv lock --check`

Exit code: `0`

```text
Resolved 46 packages in 27ms
```

### `uv sync`

Exit code: `0`

```text
Resolved 46 packages in 28ms
Checked 43 packages in 10ms
```

### `uv run ruff format --check .`

Exit code: `0`

```text
119 files already formatted
```

### `uv run ruff check .`

Exit code: `0`

```text
All checks passed!
```

### `uv run mypy app`

Exit code: `0`

```text
Success: no issues found in 83 source files
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
collected 319 items

tests/contract/test_agent_contracts.py ......                            [  1%]
tests/contract/test_api_error_schema.py .                                [  2%]
tests/contract/test_architecture_boundaries.py ..                        [  2%]
tests/contract/test_provider_contracts.py .............................. [ 12%]
...............................                                          [ 21%]
tests/contract/test_safety_boundaries.py ............................... [ 31%]
..........                                                               [ 34%]
tests/integration/test_database_and_api.py sssssss                       [ 36%]
tests/unit/test_analysis_snapshot_foundation.py ..........               [ 40%]
tests/unit/test_context_engine_foundation.py .............               [ 44%]
tests/unit/test_data_quality_foundation.py ...                           [ 45%]
tests/unit/test_domain_market_models.py ..................               [ 50%]
tests/unit/test_errors_and_redaction.py .......                          [ 52%]
tests/unit/test_feature_engine_foundation.py ...........                 [ 56%]
tests/unit/test_internal_api_key.py ....                                 [ 57%]
tests/unit/test_readiness_scheduler_foundation.py .........              [ 60%]
tests/unit/test_scheduled_digest_delivery_foundation.py ...........      [ 63%]
tests/unit/test_settings.py .........                                    [ 66%]
tests/unit/test_signal_contract_foundation.py ............               [ 70%]
tests/unit/test_strategy_rule_specification_foundation.py .............. [ 74%]
...........                                                              [ 78%]
tests/unit/test_strategy_ruleset_registry_foundation.py ................ [ 83%]
.                                                                        [ 83%]
tests/unit/test_strategy_ruleset_validation_foundation.py .............. [ 88%]
.......                                                                  [ 90%]
tests/unit/test_system_state_service.py .....                            [ 91%]
tests/unit/test_telegram_commands.py ........                            [ 94%]
tests/unit/test_telegram_policy.py .....                                 [ 95%]
tests/unit/test_time.py ...                                              [ 96%]
tests/unit/test_unit_of_work_lifecycle.py ......                         [ 98%]
tests/unit/test_value_objects_and_enums.py ....                          [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /Users/artem.otsel/Documents/ai-trading-os/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================== 312 passed, 7 skipped, 1 warning in 1.01s ===================
```

### `uv run python scripts/security_check.py`

Exit code: `0`

```text
<no output>
```

### `docker compose build`

Exit code: `0`

```text
 Image ai-trading-os-api Building 
 Image ai-trading-os-worker Building 
 Image ai-trading-os-bot Building 
 Image ai-trading-os-migrate Building 
#1 [internal] load local bake definitions
#1 reading from stdin 1.91kB done
#1 DONE 0.0s

#2 [worker internal] load build definition from Dockerfile
#2 transferring dockerfile: 411B 0.0s done
#2 DONE 0.0s

#3 [api internal] load metadata for ghcr.io/astral-sh/uv:python3.12-bookworm-slim
#3 DONE 1.0s

#4 [worker internal] load .dockerignore
#4 transferring context: 143B done
#4 DONE 0.0s

#5 [migrate 1/5] FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58
#5 resolve ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58 0.0s done
#5 DONE 0.0s

#6 [worker internal] load build context
#6 transferring context: 485.09kB 0.0s done
#6 DONE 0.0s

#7 [worker 2/5] WORKDIR /app
#7 CACHED

#8 [worker 3/5] COPY pyproject.toml uv.lock* ./
#8 CACHED

#9 [worker 4/5] RUN uv sync --frozen --no-dev
#9 CACHED

#10 [migrate 5/5] COPY . .
#10 DONE 0.1s

#11 [bot] exporting to image
#11 exporting layers 0.1s done
#11 exporting manifest sha256:58d3d166d96db041e4bf68d6d0634848eb0f99274620b7bbea13a7d53db61c09 done
#11 exporting config sha256:ea431391735f56f78b252828110cc0259771da0314a20ee5c0f2443ee9b4d718 done
#11 exporting attestation manifest sha256:c24fe3a05a2dfd786b1984aa721cd24db9d6032307daf2622f91749062b39f84 0.0s done
#11 exporting manifest list sha256:30505c27f730d4c09330cf175c5a42c68d94ae2c356d7dd4f192ed0c577e2450
#11 exporting manifest list sha256:30505c27f730d4c09330cf175c5a42c68d94ae2c356d7dd4f192ed0c577e2450 done
#11 naming to docker.io/library/ai-trading-os-bot:latest done
#11 unpacking to docker.io/library/ai-trading-os-bot:latest 0.0s done
#11 DONE 0.2s

#12 [worker] exporting to image
#12 exporting layers 0.1s done
#12 exporting manifest sha256:9dee3f4d18b5fb7a04778b498d039bbe6a5349120f4276da6b9cbb7f19a688f5 done
#12 exporting config sha256:6f9ab32a6ff6d127950e587a8071829fc1ac2f2f6b892a4e1e0280a35b0869e3 done
#12 exporting attestation manifest sha256:7808785f58d4cccd6fe647d4f007c75c8aac790c732799e180a1f9887dfaf93b 0.0s done
#12 exporting manifest list sha256:cc8df437ab9f23d58b91794385943ca19e11dcb33149fa83681c42aa4b35b199 done
#12 naming to docker.io/library/ai-trading-os-worker:latest done
#12 unpacking to docker.io/library/ai-trading-os-worker:latest 0.0s done
#12 DONE 0.2s

#13 [migrate] exporting to image
#13 exporting layers 0.1s done
#13 exporting manifest sha256:1f97eb7c088dd1ea4406f0853a49174cda3db5c15a67a7c83ab8fb31cb04d362 done
#13 exporting config sha256:b41f1e3f0382891da52c5831fd73bb88e02901e8f382c0747148a613724fc5e8 done
#13 exporting attestation manifest sha256:09aeb705629bbb8720c85d44d5ca7d7bbc94f94c5c92c2f04fdeaa23be17b092 0.0s done
#13 exporting manifest list sha256:7a0a40b3307354e3538cc432603590a507fc5fecffa1d2edfd065676677047a9 done
#13 naming to docker.io/library/ai-trading-os-migrate:latest done
#13 unpacking to docker.io/library/ai-trading-os-migrate:latest 0.0s done
#13 DONE 0.2s

#14 [api] exporting to image
#14 exporting layers 0.1s done
#14 exporting manifest sha256:1db27134bc24a52afbe669fc012afad96f5a5159057a069a29b893d2193b533d done
#14 exporting config sha256:e4fe1e17c228cedc9b55067c735b0ce60cd3a4b442b6d202d6dbfe3c919718bb done
#14 exporting attestation manifest sha256:76ce323ed674a78abe8ab040ad8358552003e2bfb636d436482853df8f69a313 0.0s done
#14 exporting manifest list sha256:7851cc94fd34a37a875fac62cbb2c89814bfb9b1ddfa27ac448278763583fc30 done
#14 naming to docker.io/library/ai-trading-os-api:latest done
#14 unpacking to docker.io/library/ai-trading-os-api:latest 0.0s done
#14 DONE 0.2s

#15 [worker] resolving provenance for metadata file
#15 DONE 0.0s

#16 [bot] resolving provenance for metadata file
#16 DONE 0.0s

#17 [migrate] resolving provenance for metadata file
#17 DONE 0.0s

#18 [api] resolving provenance for metadata file
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
 Container ai-trading-os-migrate-run-9c8909e2f6a4 Creating 
 Container ai-trading-os-migrate-run-9c8909e2f6a4 Created 
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
 Container ai-trading-os-migrate-run-31fdba8abe84 Creating 
 Container ai-trading-os-migrate-run-31fdba8abe84 Created 
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
 Container ai-trading-os-migrate-run-38decc40080b Creating 
 Container ai-trading-os-migrate-run-38decc40080b Created 
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
 Container ai-trading-os-migrate-run-6b7e329addc7 Creating 
 Container ai-trading-os-migrate-run-6b7e329addc7 Created 
Downloading pygments (1.2MiB)
Downloading ruff (10.5MiB)
Downloading mypy (13.1MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 89ms
Bytecode compiled 1963 files in 561ms
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
========================= 7 passed, 1 warning in 0.43s =========================
```

### Docker integration tests run 2

Command:
`docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-5fd3a13a874f Creating 
 Container ai-trading-os-migrate-run-5fd3a13a874f Created 
Downloading pygments (1.2MiB)
Downloading mypy (13.1MiB)
Downloading ruff (10.5MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 63ms
Bytecode compiled 1963 files in 442ms
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

- None for the requested Phase 4D verification set. Docker, PostgreSQL, Alembic, host checks, and
  Docker integration checks all ran.

## Remaining Risks

- Phase 4D intentionally exposes no API route or runtime service for the registry. The registry is a
  domain foundation and is only exercised through tests in this phase.
- Existing compose configuration still contains disabled future configuration keys. Phase 4D did
  not activate them.

## Explicit Safety Confirmations

- Phase 4D is registry/fixture-only.
- Phase 3J API route is absent.
- Phase 4E and later phases were not started.
- No rule evaluation against market data was added.
- No strategy engine was added.
- No signal generation was added.
- No setup scoring or confidence scoring was added.
- No AI agents, OpenAI calls, or LLM calls were added.
- No Telegram signal delivery was added.
- No broker APIs were added.
- No paper trading, order execution, live trading, or real trading was added.
- Built-in rule specs, rule sets, registry items, and registry snapshots remain
  disabled/non-actionable.

## Traceability

| Requirement | Implementation file | Test file | Verification result |
| --- | --- | --- | --- |
| Update project phase to Phase 4D | `app/core/constants.py` | `tests/unit/test_strategy_ruleset_registry_foundation.py` and phase assertion updates | Passed in `uv run pytest` |
| Immutable registry item/snapshot models | `app/domain/entities/strategy_registry.py` | `tests/unit/test_strategy_ruleset_registry_foundation.py` | Passed |
| UTC snapshot timestamp normalization | `app/domain/entities/strategy_registry.py` | `tests/unit/test_strategy_ruleset_registry_foundation.py` | Passed |
| Deterministic built-in keys/order | `app/domain/strategy_ruleset_registry.py` | `tests/unit/test_strategy_ruleset_registry_foundation.py` | Passed |
| All built-in fixtures disabled | `app/domain/strategy_ruleset_registry.py` | `tests/unit/test_strategy_ruleset_registry_foundation.py` | Passed |
| All built-in rules disabled | `app/domain/strategy_ruleset_registry.py` | `tests/unit/test_strategy_ruleset_registry_foundation.py` | Passed |
| Built-ins validate through Phase 4C validator | `app/domain/strategy_ruleset_registry.py` | `tests/unit/test_strategy_ruleset_registry_foundation.py` | Passed |
| Invalid fixture appears with invalid report | `app/domain/strategy_ruleset_registry.py` | `tests/unit/test_strategy_ruleset_registry_foundation.py` | Passed |
| Non-actionable item/snapshot | `app/domain/entities/strategy_registry.py` | `tests/unit/test_strategy_ruleset_registry_foundation.py` | Passed |
| `get_by_key` known and unknown behavior | `app/domain/strategy_ruleset_registry.py` | `tests/unit/test_strategy_ruleset_registry_foundation.py` | Passed |
| Deterministic JSON and SHA-256 fingerprint | `app/domain/entities/strategy_registry.py` | `tests/unit/test_strategy_ruleset_registry_foundation.py` | Passed |
| Fingerprint changes when fixture content changes | `app/domain/entities/strategy_registry.py`, `app/domain/strategy_ruleset_registry.py` | `tests/unit/test_strategy_ruleset_registry_foundation.py` | Passed |
| Registry does not mutate rulesets | `app/domain/strategy_ruleset_registry.py` | `tests/unit/test_strategy_ruleset_registry_foundation.py` | Passed |
| Domain-only registry dependencies | `app/domain/entities/strategy_registry.py`, `app/domain/strategy_ruleset_registry.py` | `tests/contract/test_safety_boundaries.py` | Passed |
| No API routes, Telegram handlers, scheduler jobs, services, broker/order/paper/live behavior | No runtime files added | `tests/contract/test_safety_boundaries.py`, `scripts/security_check.py` | Passed |
| Existing Phase 4A/4B/4C tests still pass | Existing domain files | Existing unit tests | Passed |
| Existing `/snapshot`, `/digest`, readiness/digest foundations still pass | Existing Telegram/readiness files | Existing unit and integration tests | Passed |
