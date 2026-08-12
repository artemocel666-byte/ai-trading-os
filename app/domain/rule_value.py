"""Partition windows by what each market-facing rule said, and compare what happened next.

Pure domain: decisions and outcomes in, a report out. No candles, no session, no query — the caller
that walks history is the one place any of that lives, exactly as `direction_evaluation.py` does.

Two choices carry the result.

**Only rules that claim something about the market are compared.** Of the eleven, eight are about
our own plumbing — whether enough candles arrived, how old the newest one is, whether the market was
open, whether the snapshot built — or are dead because the database holds no events. Those fail
precisely when the data is bad, and outcomes measured over bad data are strange for reasons that
have nothing to do with the market. Comparing them would measure the ingestion pipeline and report
it as a finding about rules.

**Windows are eligible only when every plumbing rule passed.** That removes data quality from the
comparison instead of controlling for it afterwards, so the two groups a market rule is judged on
differ in one thing: that rule's own verdict.
"""

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

from app.domain.entities.outcome import WindowOutcome
from app.domain.entities.pipeline_decision import PipelineDecisionReport
from app.domain.entities.rule_evaluation import RuleEvaluationStatus
from app.domain.entities.rule_value import RuleValueComparison, RuleValueReport
from app.domain.entities.signal_contract import SignalDirection
from app.domain.outcome_measurement import aggregate_outcomes

#: The rules that say something about the market rather than about our data pipeline. Named here
#: rather than derived from severity: all three happen to be WARNING today, but a rule's severity is
#: a policy choice and could change without changing what the rule is *about*.
MARKET_FACING_RULE_IDS: tuple[str, ...] = (
    "market_context.volatility_ratio",
    "market_context.max_close_excursion_atr",
    "time_filter.session_name_allowed",
)

#: A window is eligible when all of these passed. They are the project's own health checks, and a
#: window that fails one is not a sample of the market — it is a sample of a gap in ingestion.
#: `snapshot_ready` belongs here rather than with the market rules: it reports whether the snapshot
#: could be built at all, not what the snapshot then showed.
PLUMBING_RULE_IDS: tuple[str, ...] = (
    "data_quality.used_candle_count",
    "data_quality.completeness_ratio",
    "data_quality.market_data_complete",
    "data_quality.market_open",
    "market_context.snapshot_ready",
)


@dataclass(frozen=True)
class WindowObservation:
    """One window: what the rules said, and what both directions then did.

    Both outcomes are required. A window measured for one direction only would quietly weight the
    pooled statistics toward whichever direction happened to produce a plan.
    """

    decision: PipelineDecisionReport
    outcomes: Mapping[SignalDirection, WindowOutcome]


def evaluate_rule_value(
    observations: Iterable[WindowObservation],
    *,
    pair: str,
    timeframe: str,
    total_window_count: int,
    windows_without_a_plan: int = 0,
    market_facing_rule_ids: Sequence[str] = MARKET_FACING_RULE_IDS,
    plumbing_rule_ids: Sequence[str] = PLUMBING_RULE_IDS,
) -> RuleValueReport:
    """Compare each market-facing rule's two groups over the windows it was allowed to judge."""
    eligible = [
        observation
        for observation in observations
        if _every_rule_passed(observation.decision, plumbing_rule_ids)
    ]
    pooled = [outcome for observation in eligible for outcome in observation.outcomes.values()]

    comparisons: list[RuleValueComparison] = []
    for rule_id in market_facing_rule_ids:
        passed: list[WindowObservation] = []
        failed: list[WindowObservation] = []
        for observation in eligible:
            status = _rule_status(observation.decision, rule_id)
            if status == RuleEvaluationStatus.PASSED:
                passed.append(observation)
            elif status == RuleEvaluationStatus.FAILED:
                failed.append(observation)
            # UNAVAILABLE is neither: the rule could not be evaluated, so it said nothing about this
            # window and counting it on either side would put an absence into a comparison.
        comparisons.append(
            RuleValueComparison(
                rule_id=rule_id,
                passed_window_count=len(passed),
                failed_window_count=len(failed),
                passed_statistics=aggregate_outcomes(_pooled(passed)),
                failed_statistics=aggregate_outcomes(_pooled(failed)),
            )
        )

    return RuleValueReport(
        pair=pair,
        timeframe=timeframe,
        total_window_count=total_window_count,
        eligible_window_count=len(eligible),
        windows_without_a_plan=windows_without_a_plan,
        comparisons=tuple(comparisons),
        pooled_statistics=aggregate_outcomes(pooled),
    )


def _pooled(observations: Sequence[WindowObservation]) -> list[WindowOutcome]:
    return [outcome for observation in observations for outcome in observation.outcomes.values()]


def _rule_status(decision: PipelineDecisionReport, rule_id: str) -> RuleEvaluationStatus | None:
    for report in decision.ruleset_reports:
        for result in report.results:
            if result.rule_id == rule_id:
                return result.status
    return None


def _every_rule_passed(decision: PipelineDecisionReport, rule_ids: Sequence[str]) -> bool:
    """A missing rule counts as not passed.

    Fail-closed: a rule id that no longer exists in the registry would otherwise silently widen the
    eligible population, and the widening would look like a change in the market.
    """
    return all(
        _rule_status(decision, rule_id) == RuleEvaluationStatus.PASSED for rule_id in rule_ids
    )
