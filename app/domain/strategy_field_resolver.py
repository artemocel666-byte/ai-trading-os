from collections.abc import Callable, Mapping
from decimal import Decimal

from app.core.time import normalize_to_utc
from app.domain.entities.analysis import AnalysisSnapshot
from app.domain.entities.market_data import EconomicImpact
from app.domain.market_calendar import is_market_open

FieldResolution = bool | Decimal | str | None

_LONDON_SESSION_START_UTC_HOUR = 7
_LONDON_SESSION_END_UTC_HOUR = 16
_NEW_YORK_SESSION_START_UTC_HOUR = 12
_NEW_YORK_SESSION_END_UTC_HOUR = 21
_OFF_SESSION = "off_session"


def _resolve_closed_candles_available(snapshot: AnalysisSnapshot) -> FieldResolution:
    if snapshot.feature_snapshot is None:
        return None
    return snapshot.feature_snapshot.candle_summary.used_candle_count > 0


def _resolve_market_context_snapshot_ready(snapshot: AnalysisSnapshot) -> FieldResolution:
    if snapshot.context_snapshot is None:
        return None
    return snapshot.context_snapshot.quality_ok


def _resolve_time_filter_session_name(snapshot: AnalysisSnapshot) -> FieldResolution:
    """Name the liquidity session the window ends in.

    Outside London and New York this reports `off_session` rather than nothing. The hour is
    known, so "neither session" is a real observation — returning None made the rule UNAVAILABLE
    instead of failing, which the Phase 7D-2 replay caught: over six months it could never fire.
    """
    as_of_utc_hour = (
        snapshot.context_snapshot.time_context.as_of_utc_hour
        if snapshot.context_snapshot is not None
        else snapshot.window.as_of.hour
    )
    if _LONDON_SESSION_START_UTC_HOUR <= as_of_utc_hour < _LONDON_SESSION_END_UTC_HOUR:
        return "london"
    if _NEW_YORK_SESSION_START_UTC_HOUR <= as_of_utc_hour < _NEW_YORK_SESSION_END_UTC_HOUR:
        return "new_york"
    return _OFF_SESSION


def _resolve_used_candle_count(snapshot: AnalysisSnapshot) -> FieldResolution:
    if snapshot.feature_snapshot is None:
        return None
    return Decimal(snapshot.feature_snapshot.candle_summary.used_candle_count)


def _resolve_completeness_ratio(snapshot: AnalysisSnapshot) -> FieldResolution:
    if snapshot.feature_snapshot is None:
        return None
    return snapshot.feature_snapshot.data_completeness_ratio


def _resolve_market_data_complete(snapshot: AnalysisSnapshot) -> FieldResolution:
    if snapshot.feature_snapshot is None:
        return None
    return snapshot.feature_snapshot.candle_summary.market_data_complete


def _resolve_latest_candle_age_minutes(snapshot: AnalysisSnapshot) -> FieldResolution:
    if snapshot.feature_snapshot is None:
        return None
    latest_close_time = snapshot.feature_snapshot.candle_summary.latest_candle_close_time
    if latest_close_time is None:
        return None
    delta = normalize_to_utc(snapshot.window.as_of) - normalize_to_utc(latest_close_time)
    total_seconds = (delta.days * 86_400) + delta.seconds
    return Decimal(total_seconds) / Decimal("60")


def _resolve_market_open(snapshot: AnalysisSnapshot) -> FieldResolution:
    """Whether the market was trading at the moment this window describes.

    A data-quality question, not a time preference. When the market is shut the provider still
    returns candles, and they are carried-forward prices rather than trades — see
    `app/domain/market_calendar.py`. A window built from them cannot be trusted for anything, which
    is why the rule reading this field is REQUIRED rather than a warning.

    Never unavailable: the moment is always known, so "the market was shut" is a real observation
    and not a missing value. That distinction is the Phase 7D-2 lesson — a resolver returning `None`
    makes its rule UNAVAILABLE instead of failed, and the case it exists for passes in silence.
    """
    return is_market_open(snapshot.window.as_of)


def _resolve_volatility_ratio(snapshot: AnalysisSnapshot) -> FieldResolution:
    """Latest true range against its own window average.

    Returns None when the average is missing or zero: a flat window carries no ratio, and
    an unavailable value is reported honestly rather than substituted.
    """
    if snapshot.feature_snapshot is None:
        return None
    candle_summary = snapshot.feature_snapshot.candle_summary
    average_true_range = candle_summary.average_true_range
    if not candle_summary.true_ranges or average_true_range is None:
        return None
    if average_true_range == 0:
        return None
    return candle_summary.true_ranges[-1] / average_true_range


def _resolve_max_close_drawdown(snapshot: AnalysisSnapshot) -> FieldResolution:
    if snapshot.context_snapshot is None:
        return None
    return snapshot.context_snapshot.return_distribution.max_close_to_close_drawdown


def _resolve_max_close_drawdown_atr(snapshot: AnalysisSnapshot) -> FieldResolution:
    """The window's deepest drawdown, measured in typical candle ranges.

    The raw drawdown is a fraction of price, while the average true range is an absolute price
    amount, so dividing one by the other directly would be dimensionally meaningless. The ATR is
    first expressed as a fraction of the latest close, and the result is the honest question:
    *how many ordinary candle ranges deep was this decline?*

    That makes the reading comparable across timeframes, which the raw drawdown is not: a 12-candle
    window spans 3 hours on M15 and 12 hours on H1, and price covers more ground in 12 hours.
    """
    if snapshot.context_snapshot is None or snapshot.feature_snapshot is None:
        return None
    drawdown = snapshot.context_snapshot.return_distribution.max_close_to_close_drawdown
    candle_summary = snapshot.feature_snapshot.candle_summary
    average_true_range = candle_summary.average_true_range
    latest_close = candle_summary.latest_close
    if drawdown is None or average_true_range is None or latest_close is None:
        return None
    if average_true_range == 0 or latest_close == 0:
        return None
    average_true_range_ratio = average_true_range / latest_close
    if average_true_range_ratio == 0:
        return None
    return drawdown / average_true_range_ratio


def _resolve_move_efficiency(snapshot: AnalysisSnapshot) -> FieldResolution:
    """How one-sided the window's movement was, on a scale of nothing to a straight line.

    Net displacement divided by distance travelled: `|Σ returns| / Σ|returns|`, which the triangle
    inequality bounds to `[0, 1]`. One means every candle pushed the same way; zero means the window
    sawed back and forth and finished where it started.

    This fills a real gap. Everything else here measures **how far** price moved — average true
    range, candle ranges, drawdown — and nothing measured **how straight**. Two windows with an
    identical average true range can be a clean climb and a pointless chop, and until now they were
    indistinguishable to every rule in the project.

    Normalised by construction, which is the Phase 7D-2 lesson arriving for free: it is a ratio of
    two quantities in the same units, so it compares across timeframes and instruments without a
    conversion step.

    **Magnitude only, never sign.** Whether the window went up or down is deliberately not returned:
    that is a direction, and directions live in exactly one module elsewhere. This field answers
    "was this a trend or a chop", which is a description, not a view.
    """
    if snapshot.feature_snapshot is None:
        return None
    returns = snapshot.feature_snapshot.candle_summary.per_candle_returns
    if not returns:
        return None
    distance_travelled = sum((abs(value) for value in returns), Decimal("0"))
    if distance_travelled == 0:
        # A window of perfectly flat candles has no movement to judge the straightness of.
        return None
    net_displacement = abs(sum(returns, Decimal("0")))
    return net_displacement / distance_travelled


def _resolve_high_impact_event_count(snapshot: AnalysisSnapshot) -> FieldResolution:
    """Count high-impact events the window actually used.

    A quiet window legitimately measures zero, which is a real observation rather than a
    substituted value, so this stays a number instead of becoming unavailable.
    """
    if snapshot.context_snapshot is None:
        return None
    counts = snapshot.context_snapshot.event_context.counts_by_impact
    return Decimal(sum(entry.count for entry in counts if entry.impact == EconomicImpact.HIGH))


def _resolve_minutes_since_latest_event(snapshot: AnalysisSnapshot) -> FieldResolution:
    """Minutes since the most recent event in the window.

    Returns None when the window holds no event at all: there is nothing to measure, and a
    fabricated large number would read as a real observation.
    """
    if snapshot.context_snapshot is None:
        return None
    return snapshot.context_snapshot.event_context.minutes_since_latest_event


def _resolve_utc_weekday(snapshot: AnalysisSnapshot) -> FieldResolution:
    as_of_utc_weekday = (
        snapshot.context_snapshot.time_context.as_of_utc_weekday
        if snapshot.context_snapshot is not None
        else normalize_to_utc(snapshot.window.as_of).weekday()
    )
    return Decimal(as_of_utc_weekday)


FIELD_RESOLVERS: Mapping[str, Callable[[AnalysisSnapshot], FieldResolution]] = {
    "data_quality.closed_candles_available": _resolve_closed_candles_available,
    "data_quality.used_candle_count": _resolve_used_candle_count,
    "data_quality.completeness_ratio": _resolve_completeness_ratio,
    "data_quality.market_data_complete": _resolve_market_data_complete,
    "data_quality.latest_candle_age_minutes": _resolve_latest_candle_age_minutes,
    "data_quality.market_open": _resolve_market_open,
    "market_context.snapshot_ready": _resolve_market_context_snapshot_ready,
    "market_context.volatility_ratio": _resolve_volatility_ratio,
    "market_context.max_close_drawdown": _resolve_max_close_drawdown,
    "market_context.max_close_drawdown_atr": _resolve_max_close_drawdown_atr,
    "market_context.move_efficiency": _resolve_move_efficiency,
    "event_context.high_impact_event_count": _resolve_high_impact_event_count,
    "event_context.minutes_since_latest_event": _resolve_minutes_since_latest_event,
    "time_filter.session_name": _resolve_time_filter_session_name,
    "time_filter.utc_weekday": _resolve_utc_weekday,
}


def resolve_field(field_ref: str, snapshot: AnalysisSnapshot) -> FieldResolution:
    resolver = FIELD_RESOLVERS.get(field_ref)
    if resolver is None:
        return None
    return resolver(snapshot)
