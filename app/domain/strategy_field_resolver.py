from collections.abc import Callable, Mapping
from decimal import Decimal

from app.domain.entities.analysis import AnalysisSnapshot

FieldResolution = bool | Decimal | str | None

_LONDON_SESSION_START_UTC_HOUR = 7
_LONDON_SESSION_END_UTC_HOUR = 16
_NEW_YORK_SESSION_START_UTC_HOUR = 12
_NEW_YORK_SESSION_END_UTC_HOUR = 21


def _resolve_closed_candles_available(snapshot: AnalysisSnapshot) -> FieldResolution:
    if snapshot.feature_snapshot is None:
        return None
    return snapshot.feature_snapshot.candle_summary.used_candle_count > 0


def _resolve_market_context_snapshot_ready(snapshot: AnalysisSnapshot) -> FieldResolution:
    if snapshot.context_snapshot is None:
        return None
    return snapshot.context_snapshot.quality_ok


def _resolve_time_filter_session_name(snapshot: AnalysisSnapshot) -> FieldResolution:
    as_of_utc_hour = (
        snapshot.context_snapshot.time_context.as_of_utc_hour
        if snapshot.context_snapshot is not None
        else snapshot.window.as_of.hour
    )
    if _LONDON_SESSION_START_UTC_HOUR <= as_of_utc_hour < _LONDON_SESSION_END_UTC_HOUR:
        return "london"
    if _NEW_YORK_SESSION_START_UTC_HOUR <= as_of_utc_hour < _NEW_YORK_SESSION_END_UTC_HOUR:
        return "new_york"
    return None


FIELD_RESOLVERS: Mapping[str, Callable[[AnalysisSnapshot], FieldResolution]] = {
    "data_quality.closed_candles_available": _resolve_closed_candles_available,
    "market_context.snapshot_ready": _resolve_market_context_snapshot_ready,
    "time_filter.session_name": _resolve_time_filter_session_name,
}


def resolve_field(field_ref: str, snapshot: AnalysisSnapshot) -> FieldResolution:
    resolver = FIELD_RESOLVERS.get(field_ref)
    if resolver is None:
        return None
    return resolver(snapshot)
