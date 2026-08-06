"""Build what a Chief AI may see, and check what it hands back.

Pure domain code: no clock, no network, no persistence, and not wired to anything in Phase 8A. The
validator returns findings instead of raising, because the caller's correct reaction is always the
same — drop the model's answer and use the deterministic text.

Two checks carry the weight:

* the existing Phase 5 detector for actionable English text, plus a Russian list added here. The
  Phase 5 detector alone would miss a Russian model entirely: it matches "buy", not "покупай", and
  this project's user-facing language is Russian.
* an allowed-number set derived from the input itself. A model may repeat any number it was given
  and no other, so a fabricated figure cannot survive, whatever wording surrounds it.
"""

import re
from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal, InvalidOperation

from app.domain.entities.analysis import AnalysisSnapshot
from app.domain.entities.explanation import (
    MAXIMUM_EXPLANATION_LENGTH,
    ExplanationInput,
    ExplanationIssue,
    ExplanationIssueCode,
    ExplanationReading,
    ExplanationRulesetFacts,
    ExplanationValidationReport,
)
from app.domain.entities.manual_review import contains_actionable_trading_text
from app.domain.entities.pipeline_decision import PipelineDecisionReport
from app.domain.entities.rule_evaluation import RuleEvaluationStatus, RuleSetEvaluationReport
from app.domain.strategy_field_resolver import resolve_field

# Readings the explainer may describe. Every one is already computed and already shown by /review,
# so the model sees the same numbers a person does — no new maths enters through this door.
EXPLAINABLE_FIELD_REFS: tuple[str, ...] = (
    "data_quality.completeness_ratio",
    "data_quality.latest_candle_age_minutes",
    "data_quality.used_candle_count",
    "event_context.high_impact_event_count",
    "event_context.minutes_since_latest_event",
    "market_context.max_close_drawdown",
    "market_context.max_close_drawdown_atr",
    "market_context.volatility_ratio",
    "time_filter.utc_weekday",
)

_CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")  # noqa: RUF001
_NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)?")
# Domain code must not import the Telegram emoji table, and does not need to: the body must carry
# no emoji at all, so the formatter stays the only thing that adds one.
_EMOJI_RE = re.compile("[\U0001f300-\U0001faff☀-➿⬀-⯿️]")
_ACTIONABLE_RUSSIAN_PATTERNS = (
    re.compile(r"\bпоку?па\w*", re.IGNORECASE),  # noqa: RUF001
    re.compile(r"\bпродава?\w*|\bпродать\b|\bпродажа\b", re.IGNORECASE),  # noqa: RUF001
    re.compile(r"\bлонг\w*|\bшорт\w*", re.IGNORECASE),  # noqa: RUF001
    re.compile(r"\bсигнал\w*", re.IGNORECASE),  # noqa: RUF001
    re.compile(r"\bрекоменд\w*|\bсовет\w*", re.IGNORECASE),  # noqa: RUF001
    re.compile(r"\bвход\w*\s+(?:в\s+)?(?:рынок|сделк\w*|позици\w*)", re.IGNORECASE),  # noqa: RUF001
    re.compile(r"\bстоп[-\s]?лосс\w*|\bтейк[-\s]?профит\w*", re.IGNORECASE),  # noqa: RUF001
    re.compile(r"\bцель\b|\bцели\b|\bтаргет\w*", re.IGNORECASE),  # noqa: RUF001
    re.compile(r"\bсделк\w*|\bпозици\w*|\bордер\w*|\bброкер\w*", re.IGNORECASE),  # noqa: RUF001
    re.compile(r"\bприбыл\w*|\bубыт\w*|\bриск\w*\s+на\s+сделку", re.IGNORECASE),  # noqa: RUF001
)


def contains_actionable_russian_text(value: str) -> bool:
    return any(pattern.search(value) for pattern in _ACTIONABLE_RUSSIAN_PATTERNS)


def build_explanation_input(
    decision: PipelineDecisionReport,
    snapshot: AnalysisSnapshot,
    *,
    field_refs: Sequence[str] = EXPLAINABLE_FIELD_REFS,
) -> ExplanationInput:
    """Project a composed decision into the facts an explainer may receive.

    Nothing here computes anything: rule outcomes come from the Phase 4G report and readings from
    the Phase 4F resolvers. The result holds values only — no snapshot, no report, no callable — so
    an explainer cannot reach back into the pipeline that produced it.
    """
    expected_candle_count = (
        snapshot.feature_snapshot.candle_summary.expected_candle_count
        if snapshot.feature_snapshot is not None
        else 0
    )
    return ExplanationInput(
        pair=snapshot.window.pair,
        timeframe=snapshot.window.timeframe,
        as_of=snapshot.window.as_of,
        decision_status=decision.status,
        source_snapshot_id=snapshot.metadata.snapshot_id,
        used_candle_count=snapshot.input_audit.used_candle_count,
        expected_candle_count=expected_candle_count,
        ruleset_facts=tuple(_ruleset_facts(report) for report in decision.ruleset_reports),
        readings=tuple(
            ExplanationReading(field_ref=field_ref, value=_numeric_reading(field_ref, snapshot))
            for field_ref in field_refs
        ),
    )


def validate_explanation_text(
    text: str,
    explanation_input: ExplanationInput,
    checked_at: datetime,
) -> ExplanationValidationReport:
    """Check a candidate explanation against everything it is not allowed to do.

    Every issue found is reported, not just the first, so a rejection is diagnosable.
    """
    issues: list[ExplanationIssue] = []
    body = text.strip()

    if not body:
        return ExplanationValidationReport(
            checked_at=checked_at,
            issues=(
                ExplanationIssue(
                    code=ExplanationIssueCode.EMPTY_TEXT,
                    detail="Пустой текст объяснения.",
                ),
            ),
            accepted=False,
        )

    if len(body) > MAXIMUM_EXPLANATION_LENGTH:
        issues.append(
            ExplanationIssue(
                code=ExplanationIssueCode.TOO_LONG,
                detail=f"Длина {len(body)} превышает предел {MAXIMUM_EXPLANATION_LENGTH}.",
            )
        )

    if not _CYRILLIC_RE.search(body):
        issues.append(
            ExplanationIssue(
                code=ExplanationIssueCode.NOT_RUSSIAN,
                detail="Текст не содержит кириллицы.",
            )
        )

    if contains_actionable_trading_text(body) or contains_actionable_russian_text(body):
        issues.append(
            ExplanationIssue(
                code=ExplanationIssueCode.ACTIONABLE_TEXT,
                detail="Текст содержит торговые указания.",
            )
        )

    emoji_matches = _EMOJI_RE.findall(body)
    if emoji_matches:
        issues.append(
            ExplanationIssue(
                code=ExplanationIssueCode.EMOJI_FOUND,
                detail=f"Текст содержит эмодзи: {''.join(sorted(set(emoji_matches)))[:50]}.",
            )
        )

    allowed_numbers = allowed_number_set(explanation_input)
    for token in _NUMBER_RE.findall(body):
        value = _decimal_or_none(token)
        if value is None or value not in allowed_numbers:
            issues.append(
                ExplanationIssue(
                    code=ExplanationIssueCode.UNKNOWN_NUMBER,
                    detail=f"Числа {token} нет во входных данных.",
                )
            )

    return ExplanationValidationReport(
        checked_at=checked_at,
        issues=tuple(issues),
        accepted=not issues,
    )


def allowed_number_set(explanation_input: ExplanationInput) -> frozenset[Decimal]:
    """Every number the explainer was given, plus each one written as a percentage.

    Derived from the serialized input rather than from a hand-listed set of fields, so a value can
    never be quotable without having actually been sent.
    """
    values: set[Decimal] = set()
    for token in _NUMBER_RE.findall(explanation_input.deterministic_json()):
        value = _decimal_or_none(token)
        if value is None:
            continue
        values.add(value)
        # A ratio of 0.1176 may legitimately be written as 11.76%.
        values.add(value * Decimal("100"))
    return frozenset(values)


def _ruleset_facts(report: RuleSetEvaluationReport) -> ExplanationRulesetFacts:
    passed = [
        result.rule_id for result in report.results if result.status == RuleEvaluationStatus.PASSED
    ]
    failed = [
        result.rule_id for result in report.results if result.status == RuleEvaluationStatus.FAILED
    ]
    unavailable = [
        result.rule_id
        for result in report.results
        if result.status == RuleEvaluationStatus.UNAVAILABLE
    ]
    return ExplanationRulesetFacts(
        ruleset_name=report.ruleset_name,
        status=report.status,
        passed_count=len(passed),
        failed_count=len(failed),
        unavailable_count=len(unavailable),
        failed_rule_ids=tuple(failed),
        unavailable_rule_ids=tuple(unavailable),
    )


def _numeric_reading(field_ref: str, snapshot: AnalysisSnapshot) -> Decimal | None:
    resolved = resolve_field(field_ref, snapshot)
    return resolved if isinstance(resolved, Decimal) else None


def _decimal_or_none(token: str) -> Decimal | None:
    try:
        return Decimal(token.replace(",", "."))
    except InvalidOperation:
        return None
