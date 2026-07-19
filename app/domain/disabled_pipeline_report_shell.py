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
