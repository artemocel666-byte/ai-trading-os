from collections.abc import Mapping
from datetime import UTC, datetime
from decimal import Decimal
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
    expected_value: object | None = None,
    lower_bound: object | None = None,
    upper_bound: object | None = None,
    allowed_values: tuple[str, ...] | None = None,
) -> StrategyRuleSpec:
    return StrategyRuleSpec(
        rule_id=rule_id,
        category=category,
        severity=severity,
        condition=StrategyRuleCondition(
            field_ref=field_ref,
            operator=operator,
            expected_value=(
                StrategyRuleValue(value=expected_value) if expected_value is not None else None
            ),
            lower_bound=(StrategyRuleValue(value=lower_bound) if lower_bound is not None else None),
            upper_bound=(StrategyRuleValue(value=upper_bound) if upper_bound is not None else None),
            allowed_values=(
                StrategyRuleValue(value=allowed_values) if allowed_values is not None else None
            ),
        ),
        description=description,
        enabled=False,
    )


MINIMUM_USED_CANDLE_COUNT = Decimal("8")
MINIMUM_COMPLETENESS_RATIO = Decimal("0.8")
MAXIMUM_LATEST_CANDLE_AGE_MINUTES = Decimal("90")
# Recalibrated 2026-08-09 over **two instruments**, traded candles only: EURUSD and NOKSEK, M15 and
# H1, roughly 12 000 and 2 800 windows each. NOKSEK was chosen precisely because it is unlike EURUSD
# — no dollar on either side, about 1.8x the relative volatility per candle, and a different session
# profile — so a threshold that survives the move is evidence rather than a coincidence.
#
# Share of windows outside each candidate band:
#                     EURUSD M15   EURUSD H1   NOKSEK M15   NOKSEK H1
#   0.35 - 2.3             3.32%       7.69%        7.19%      10.88%   <- previous, fails H1
#   0.30 - 2.5             1.91%       4.66%        4.77%       6.79%   <- taken
#   0.28 - 2.8             1.32%       2.82%        3.33%       5.03%
#   0.25 - 3.0             1.02%       2.06%        2.55%       3.34%   <- too near the floor
#
# 0.30/2.5 keeps all four inside the 1-10% corridor with the most room at the floor, which is the
# constraint that bit last time: the pre-2026-08-08 band had fallen to 0.99% on clean EURUSD M15.
#
# **The convergence criterion still cannot be met, and now for a second reason.** 9A-6 found this
# field is only partly timeframe-neutral; adding a second instrument shows it is not
# instrument-neutral either, leaving a 4.88 percentage-point spread across the four series that no
# band removes. Two independent confirmations of the same weakness. Compare
# `max_close_excursion_atr`, whose bound of 5.0 transfers across both instruments untouched.
MINIMUM_VOLATILITY_RATIO = Decimal("0.30")
MAXIMUM_VOLATILITY_RATIO = Decimal("2.5")
# Measured in typical candle ranges, not in price: the raw drawdown is divided by the window's
# own average true range (itself expressed as a fraction of the latest close). Calibrated
# 2026-08-05 over six months of EURUSD — 16 508 M15 and 4 153 H1 observations — where p95 was
# 4.1100 (M15) and 4.0061 (H1). At 4.0 the rule fires on 5.65% of M15 and 5.03% of H1 windows.
#
# The 0.62 percentage-point gap is the point of the change. The previous absolute bound (0.004 of
# price) fired on 1.19% of M15 and 7.14% of H1 windows — a six-fold spread — because a 12-candle
# window spans 3 hours on M15 and 12 hours on H1, and price covers more ground in 12 hours. The
# normalised field asks "how many ordinary candle ranges deep was this decline", which means the
# same thing on any timeframe.
#
# Re-measured 2026-08-08 on traded candles only: p95 is 4.1403 (M15) and 4.1149 (H1), and at 4.0 the
# rule fired on 5.98% and 5.96% — a 0.02 percentage-point spread. The field is retained for its
# distribution, but **no rule reads it any more**: it measures declines only, so a window that
# climbed steeply and never pulled back reported zero, and a warning rule read that as calm. That
# made the rule directional in a project with no direction. See the excursion bound below.
MAXIMUM_CLOSE_DRAWDOWN_ATR = Decimal("4.0")
# The largest one-sided move in **either** direction, in typical candle ranges. Calibrated
# 2026-08-08 over traded candles only — 11 813 M15 and 2 770 H1 observations.
#
# Clean percentiles:        p50     p75     p90     p95     p97     p99
#   M15                  2.5832  3.3179  4.1463  4.6979  5.0903  5.7505
#   H1                   2.5598  3.3141  4.0850  4.4806  4.8364  5.5860
#
# Firing rates by bound:   4.0 -> 11.89% / 11.55%   (above the 1-10% corridor)
#                          4.5 ->  6.53% /  4.87%   (spread 1.65, over the convergence criterion)
#                          5.0 ->  3.43% /  2.56%   (spread 0.87 — both criteria met)
#                          5.5 ->  1.51% /  1.34%   (bottom of the corridor)
#
# 5.0 is the only bound that satisfies both acceptance criteria with margin, so it is the one taken.
# Note how much better this field converges than the one-sided drawdown did at the same percentiles:
# taking the larger of two measurements of the same window is less noisy than taking one of them.
#
# **Confirmed on a second instrument, 2026-08-09, without changing the number.** On NOKSEK the same
# bound fires on 2.86% (M15) and 2.19% (H1), against 3.43% and 2.56% on EURUSD — a spread of 0.57
# points across instruments on M15 and 0.37 on H1, over a pair with about 1.8x the relative
# volatility per candle. This is the strongest evidence in the project that normalising by the
# window's own average true range makes a threshold mean the same thing somewhere else: M15 against
# H1 is one market seen twice, EURUSD against NOKSEK is two markets.
MAXIMUM_CLOSE_EXCURSION_ATR = Decimal("5.0")
LAST_WEEKDAY_INDEX = Decimal("4")
MAXIMUM_HIGH_IMPACT_EVENT_COUNT = Decimal("0")
MINIMUM_MINUTES_SINCE_LATEST_EVENT = Decimal("30")

BUILTIN_STRATEGY_RULESET_FIXTURES: Mapping[str, StrategyRuleSet] = MappingProxyType(
    {
        "foundation.data_quality.v1": StrategyRuleSet(
            ruleset_version="foundation-data-quality-v1",
            strategy_version=DEFAULT_STRATEGY_VERSION,
            name="Foundation data quality",
            description="Descriptive checks on whether the analysis window can be trusted.",
            created_at=BUILTIN_RULESET_CREATED_AT,
            rules=(
                _foundation_rule(
                    rule_id="data_quality.used_candle_count",
                    category=StrategyRuleCategory.DATA_QUALITY,
                    severity=StrategyRuleSeverity.BLOCKING,
                    field_ref="data_quality.used_candle_count",
                    operator=StrategyRuleOperator.GTE,
                    expected_value=MINIMUM_USED_CANDLE_COUNT,
                    description=(
                        "The window holds at least eight usable closed candles; fewer leaves "
                        "nothing meaningful to describe."
                    ),
                ),
                _foundation_rule(
                    rule_id="data_quality.completeness_ratio",
                    category=StrategyRuleCategory.DATA_QUALITY,
                    severity=StrategyRuleSeverity.REQUIRED,
                    field_ref="data_quality.completeness_ratio",
                    operator=StrategyRuleOperator.GTE,
                    expected_value=MINIMUM_COMPLETENESS_RATIO,
                    description=(
                        "At least eighty percent of the expected candles for the window are "
                        "present."
                    ),
                ),
                _foundation_rule(
                    rule_id="data_quality.market_data_complete",
                    category=StrategyRuleCategory.DATA_QUALITY,
                    severity=StrategyRuleSeverity.REQUIRED,
                    field_ref="data_quality.market_data_complete",
                    operator=StrategyRuleOperator.EQ,
                    expected_value=True,
                    description=(
                        "The window reports no missing, duplicated, or misaligned candles."
                    ),
                ),
                _foundation_rule(
                    rule_id="data_quality.latest_candle_age_minutes",
                    category=StrategyRuleCategory.DATA_QUALITY,
                    severity=StrategyRuleSeverity.WARNING,
                    field_ref="data_quality.latest_candle_age_minutes",
                    operator=StrategyRuleOperator.LTE,
                    expected_value=MAXIMUM_LATEST_CANDLE_AGE_MINUTES,
                    description=(
                        "The newest stored candle is recent enough that the feed appears live "
                        "rather than stalled."
                    ),
                ),
                _foundation_rule(
                    rule_id="data_quality.market_open",
                    category=StrategyRuleCategory.DATA_QUALITY,
                    severity=StrategyRuleSeverity.REQUIRED,
                    field_ref="data_quality.market_open",
                    operator=StrategyRuleOperator.EQ,
                    expected_value=True,
                    description=(
                        "The currency market was trading when this window ended. While it is shut "
                        "the provider still returns candles, and they carry the last price forward "
                        "instead of recording trades."
                    ),
                ),
            ),
            enabled=False,
        ),
        "foundation.market_context.v1": StrategyRuleSet(
            ruleset_version="foundation-market-context-v1",
            strategy_version=DEFAULT_STRATEGY_VERSION,
            name="Foundation market context",
            description="Descriptive checks on the computed context of the window.",
            created_at=BUILTIN_RULESET_CREATED_AT,
            rules=(
                _foundation_rule(
                    rule_id="market_context.snapshot_ready",
                    category=StrategyRuleCategory.MARKET_CONTEXT,
                    severity=StrategyRuleSeverity.REQUIRED,
                    field_ref="market_context.snapshot_ready",
                    operator=StrategyRuleOperator.EQ,
                    expected_value=True,
                    description=(
                        "The context snapshot computed without quality issues for this window."
                    ),
                ),
                _foundation_rule(
                    rule_id="market_context.volatility_ratio",
                    category=StrategyRuleCategory.MARKET_CONTEXT,
                    severity=StrategyRuleSeverity.WARNING,
                    field_ref="market_context.volatility_ratio",
                    operator=StrategyRuleOperator.BETWEEN,
                    lower_bound=MINIMUM_VOLATILITY_RATIO,
                    upper_bound=MAXIMUM_VOLATILITY_RATIO,
                    description=(
                        "The latest true range sits within a usual band around its own window "
                        "average; outside it the window is unusually calm or unusually wide."
                    ),
                ),
                _foundation_rule(
                    rule_id="market_context.max_close_excursion_atr",
                    category=StrategyRuleCategory.MARKET_CONTEXT,
                    severity=StrategyRuleSeverity.WARNING,
                    field_ref="market_context.max_close_excursion_atr",
                    operator=StrategyRuleOperator.LTE,
                    expected_value=MAXIMUM_CLOSE_EXCURSION_ATR,
                    description=(
                        "The largest one-sided close-to-close move inside the window, in either "
                        "direction, stays within a usual number of candle ranges. Measuring only "
                        "declines made this rule blind to a steep climb."
                    ),
                ),
            ),
            enabled=False,
        ),
        "foundation.event_context.v1": StrategyRuleSet(
            ruleset_version="foundation-event-context-v1",
            strategy_version=DEFAULT_STRATEGY_VERSION,
            name="Foundation event context",
            description="Descriptive checks on scheduled events inside the window.",
            created_at=BUILTIN_RULESET_CREATED_AT,
            rules=(
                _foundation_rule(
                    rule_id="event_context.high_impact_event_count",
                    category=StrategyRuleCategory.EVENT_CONTEXT,
                    severity=StrategyRuleSeverity.WARNING,
                    field_ref="event_context.high_impact_event_count",
                    operator=StrategyRuleOperator.LTE,
                    expected_value=MAXIMUM_HIGH_IMPACT_EVENT_COUNT,
                    description=(
                        "No high-impact scheduled release falls inside the window; when one does, "
                        "the observed values may still be settling."
                    ),
                ),
                _foundation_rule(
                    rule_id="event_context.minutes_since_latest_event",
                    category=StrategyRuleCategory.EVENT_CONTEXT,
                    severity=StrategyRuleSeverity.WARNING,
                    field_ref="event_context.minutes_since_latest_event",
                    operator=StrategyRuleOperator.GTE,
                    expected_value=MINIMUM_MINUTES_SINCE_LATEST_EVENT,
                    description=(
                        "Enough time has passed since the most recent release. Reported as "
                        "unavailable when the window holds no release at all, which is the calm "
                        "case rather than a failure."
                    ),
                ),
            ),
            enabled=False,
        ),
        "foundation.time_filter.v1": StrategyRuleSet(
            ruleset_version="foundation-time-filter-v1",
            strategy_version=DEFAULT_STRATEGY_VERSION,
            name="Foundation time filter",
            description="Descriptive checks on when the window was captured.",
            created_at=BUILTIN_RULESET_CREATED_AT,
            rules=(
                _foundation_rule(
                    rule_id="time_filter.session_name_allowed",
                    category=StrategyRuleCategory.TIME_FILTER,
                    severity=StrategyRuleSeverity.WARNING,
                    field_ref="time_filter.session_name",
                    operator=StrategyRuleOperator.IN,
                    allowed_values=("london", "new_york"),
                    description=("The window ends inside one of the two main liquidity sessions."),
                ),
                # `time_filter.utc_weekday` used to be a second rule here, saying almost exactly
                # what `data_quality.market_open` now says — and saying it as a WARNING, which the
                # status calculation ignored entirely. It fired on 28.08% of six months of
                # windows and changed nothing, so every calibration ran over data the project's own
                # rule was flagging as stale. The check moved to the data-quality ruleset, where a
                # failure has consequences, because a shut market is a fact about the data rather
                # than a preference about trading hours. The resolver stays in the registry for its
                # distribution; only the toothless rule is gone.
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
