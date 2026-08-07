"""Aggregation of replayed rule outcomes into a calibration report.

Pure domain code: no clock, no I/O, no persistence. It counts what the real evaluator produced and
summarises the resolved field values so thresholds can be derived from observations instead of
guesses. It never decides anything.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from app.domain.entities.calibration import (
    FieldDistribution,
    RuleCalibrationReport,
    RuleOutcomeTally,
)
from app.domain.entities.market_data import Timeframe
from app.domain.entities.pipeline_decision import PipelineDecisionReport
from app.domain.entities.rule_evaluation import RuleEvaluationStatus, RuleSetEvaluationStatus
from app.domain.entities.strategy_rules import StrategyRuleSeverity
from app.domain.strategy_field_resolver import FieldResolution
from app.domain.value_objects import CurrencyPair

_PERCENTILES: tuple[tuple[str, int], ...] = (
    ("p05", 5),
    ("p25", 25),
    ("median", 50),
    ("p75", 75),
    ("p95", 95),
)


def _nearest_rank(sorted_values: Sequence[Decimal], percent: int) -> Decimal:
    """Nearest-rank percentile: returns a value the sample actually contained.

    Interpolating would invent a number that was never observed, and doing it in binary floating
    point would also lose exactness on prices. Integer arithmetic on the rank avoids both.
    """
    count = len(sorted_values)
    rank = (percent * count + 99) // 100
    index = min(max(rank - 1, 0), count - 1)
    return sorted_values[index]


def summarize_field(
    field_ref: str,
    values: Sequence[Decimal],
    unavailable_count: int = 0,
) -> FieldDistribution:
    if not values:
        return FieldDistribution(
            field_ref=field_ref,
            observed_count=0,
            unavailable_count=unavailable_count,
        )
    ordered = sorted(values)
    percentiles = {name: _nearest_rank(ordered, percent) for name, percent in _PERCENTILES}
    return FieldDistribution(
        field_ref=field_ref,
        observed_count=len(ordered),
        unavailable_count=unavailable_count,
        minimum=ordered[0],
        maximum=ordered[-1],
        **percentiles,
    )


@dataclass
class _RuleCounts:
    field_ref: str
    severity: StrategyRuleSeverity
    passed: int = 0
    failed: int = 0
    unavailable: int = 0


@dataclass
class _FieldSample:
    values: list[Decimal] = field(default_factory=list)
    unavailable: int = 0


class RuleCalibrationAccumulator:
    """Folds one replayed window at a time into per-rule tallies and per-field samples.

    Numeric fields build a distribution; boolean and session-name fields do not, because a
    percentile over them would be meaningless — their rule tally already carries the whole story.
    """

    def __init__(self) -> None:
        self._window_count = 0
        self._rules: dict[str, _RuleCounts] = {}
        self._fields: dict[str, _FieldSample] = {}
        self._ready_for_review = 0
        self._warned = 0
        self._not_ready = 0
        self._blocked = 0

    @property
    def window_count(self) -> int:
        return self._window_count

    def observe(
        self,
        *,
        decision: PipelineDecisionReport,
        field_values: Mapping[str, FieldResolution],
    ) -> None:
        self._window_count += 1
        for ruleset_report in decision.ruleset_reports:
            if ruleset_report.status == RuleSetEvaluationStatus.BLOCKED:
                self._blocked += 1
            elif ruleset_report.status == RuleSetEvaluationStatus.NOT_READY:
                self._not_ready += 1
            elif ruleset_report.status == RuleSetEvaluationStatus.READY_WITH_WARNINGS:
                self._warned += 1
            else:
                self._ready_for_review += 1
            for result in ruleset_report.results:
                counts = self._rules.setdefault(
                    result.rule_id,
                    _RuleCounts(field_ref=result.field_ref, severity=result.severity),
                )
                if result.status == RuleEvaluationStatus.PASSED:
                    counts.passed += 1
                elif result.status == RuleEvaluationStatus.FAILED:
                    counts.failed += 1
                else:
                    counts.unavailable += 1

        for field_ref, value in field_values.items():
            sample = self._fields.setdefault(field_ref, _FieldSample())
            if value is None:
                sample.unavailable += 1
            elif isinstance(value, Decimal):
                sample.values.append(value)

    def build_report(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        replay_start: datetime,
        replay_end: datetime,
        window_candles: int,
        step_candles: int,
    ) -> RuleCalibrationReport:
        tallies = tuple(
            RuleOutcomeTally(
                rule_id=rule_id,
                field_ref=counts.field_ref,
                severity=counts.severity,
                passed_count=counts.passed,
                failed_count=counts.failed,
                unavailable_count=counts.unavailable,
            )
            for rule_id, counts in self._rules.items()
        )
        distributions = tuple(
            summarize_field(field_ref, sample.values, sample.unavailable)
            for field_ref, sample in self._fields.items()
            if sample.values
        )
        return RuleCalibrationReport(
            pair=pair,
            timeframe=timeframe,
            replay_start=replay_start,
            replay_end=replay_end,
            window_candles=window_candles,
            step_candles=step_candles,
            window_count=self._window_count,
            tallies=tallies,
            distributions=distributions,
            ready_for_review_ruleset_count=self._ready_for_review,
            warned_ruleset_count=self._warned,
            not_ready_ruleset_count=self._not_ready,
            blocked_ruleset_count=self._blocked,
        )
