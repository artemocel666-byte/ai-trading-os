from datetime import datetime

from app.core import constants
from app.core.time import normalize_to_utc
from app.domain.entities.analysis import AnalysisSnapshot
from app.domain.entities.pipeline_decision import (
    PipelineDecisionReport,
    PipelineDecisionStatus,
    SkippedRuleset,
    SkippedRulesetReason,
)
from app.domain.entities.rule_evaluation import RuleSetEvaluationReport, RuleSetEvaluationStatus
from app.domain.entities.strategy_validation import StrategyRuleSetValidationStatus
from app.domain.strategy_rule_evaluator import StrategyRuleEvaluator
from app.domain.strategy_ruleset_registry import StrategyRuleSetRegistry

COMPOSER_PIPELINE_VERSION = "phase4g-strategy-decision-composition-v1"


class StrategyDecisionComposer:
    def __init__(
        self,
        registry: StrategyRuleSetRegistry | None = None,
        evaluator: StrategyRuleEvaluator | None = None,
    ) -> None:
        self._registry = registry or StrategyRuleSetRegistry()
        self._evaluator = evaluator or StrategyRuleEvaluator()

    def compose(
        self,
        snapshot: AnalysisSnapshot,
        evaluated_at: datetime,
    ) -> PipelineDecisionReport:
        normalized_evaluated_at = normalize_to_utc(evaluated_at)
        registry_snapshot = self._registry.load_builtin_rulesets(normalized_evaluated_at)

        ruleset_reports: list[RuleSetEvaluationReport] = []
        skipped_rulesets: list[SkippedRuleset] = []
        for item in registry_snapshot.items:
            if item.validation_report.status != StrategyRuleSetValidationStatus.VALID:
                skipped_rulesets.append(
                    SkippedRuleset(
                        registry_key=item.registry_key,
                        reason=SkippedRulesetReason.INVALID_VALIDATION,
                    )
                )
                continue
            ruleset_reports.append(
                self._evaluator.evaluate_ruleset(item.ruleset, snapshot, normalized_evaluated_at)
            )

        blocked_count = sum(
            1 for report in ruleset_reports if report.status == RuleSetEvaluationStatus.BLOCKED
        )
        not_ready_count = sum(
            1 for report in ruleset_reports if report.status == RuleSetEvaluationStatus.NOT_READY
        )
        return PipelineDecisionReport(
            pipeline_version=COMPOSER_PIPELINE_VERSION,
            project_phase=constants.PROJECT_PHASE,
            status=_status_for(blocked_count, not_ready_count),
            evaluated_at=normalized_evaluated_at,
            source_snapshot_id=snapshot.metadata.snapshot_id,
            ruleset_reports=tuple(ruleset_reports),
            skipped_rulesets=tuple(skipped_rulesets),
            evaluated_ruleset_count=len(ruleset_reports),
            blocked_ruleset_count=blocked_count,
            not_ready_ruleset_count=not_ready_count,
            is_actionable=False,
        )


def _status_for(blocked_count: int, not_ready_count: int) -> PipelineDecisionStatus:
    if blocked_count > 0:
        return PipelineDecisionStatus.BLOCKED
    if not_ready_count > 0:
        return PipelineDecisionStatus.NOT_READY
    return PipelineDecisionStatus.READY_FOR_REVIEW
