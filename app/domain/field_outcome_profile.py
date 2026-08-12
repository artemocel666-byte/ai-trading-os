"""Bucket windows by field value and report what happened after each bucket.

Pure domain: values and outcomes in, a profile out. No candles, no session, no query — the caller
that walks history is the one place any of that lives, as in `rule_value.py` and
`direction_evaluation.py`.

**Nothing here chooses a threshold.** Deciles are cut at ranks the sample itself supplies, so there
is no parameter that could be tuned to the data and then reported as a finding. That is the whole
reason this exists rather than a sweep: Phase 9A-3 swept a parameter, cleared its criteria, and was
retracted the same day.

**Buckets are equal in size, not equal in value range.** Cutting at percentile *values* would
leave wildly uneven buckets wherever a field clusters, and a decile holding twenty windows would
post a share that says more about its size than about the market. Equal counts make the ten
shares comparable, which is the only reason to draw them side by side.

The cost is that windows sharing one value can straddle a boundary. Harmless for the continuous
fields measured here, and preferable to buckets that cannot be compared.
"""

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal

from app.domain.entities.field_outcome import DECILE_COUNT, FieldDecile, FieldOutcomeProfile
from app.domain.entities.outcome import WindowOutcome
from app.domain.entities.signal_contract import SignalDirection
from app.domain.outcome_measurement import aggregate_outcomes


@dataclass(frozen=True)
class FieldObservation:
    """One window: where the field landed, and what both directions then did.

    `value` is `None` when the field did not resolve. Such a window is counted apart rather than
    bucketed: a missing reading placed at the bottom of the range would become an observation of a
    low value, which is exactly the substitution the Phase 7C resolvers refuse to make.
    """

    value: Decimal | None
    outcomes: Mapping[SignalDirection, WindowOutcome]


def build_field_outcome_profile(
    observations: Iterable[FieldObservation],
    *,
    pair: str,
    timeframe: str,
    field_ref: str,
    decile_count: int = DECILE_COUNT,
) -> FieldOutcomeProfile:
    """Ten ordered buckets over the observed values, each carrying its own pooled outcomes."""
    if decile_count < 1:
        raise ValueError("decile_count must be at least one bucket")

    materialised = list(observations)
    observed = [item for item in materialised if item.value is not None]
    unavailable = len(materialised) - len(observed)

    # Sorted by value, then bucketed by position rather than by value range. Equal-sized buckets
    # keep every decile's share resting on the same number of windows, so a flat-looking tail
    # cannot be an artefact of that tail holding twenty windows.
    observed.sort(key=_value_of)
    deciles: list[FieldDecile] = []
    for index in range(decile_count):
        start = (index * len(observed)) // decile_count
        end = ((index + 1) * len(observed)) // decile_count
        bucket = observed[start:end]
        if not bucket:
            # Fewer windows than buckets, or a field with almost no distinct values. Reporting an
            # empty decile would put a zero-window share into the extremes the readings compare.
            continue
        deciles.append(
            FieldDecile(
                index=len(deciles) + 1,
                lower_bound=_value_of(bucket[0]),
                upper_bound=_value_of(bucket[-1]),
                window_count=len(bucket),
                statistics=aggregate_outcomes(_pooled(bucket)),
            )
        )

    return FieldOutcomeProfile(
        pair=pair,
        timeframe=timeframe,
        field_ref=field_ref,
        total_window_count=len(materialised),
        unavailable_count=unavailable,
        deciles=tuple(deciles),
        pooled_statistics=aggregate_outcomes(_pooled(observed)),
    )


def _value_of(observation: FieldObservation) -> Decimal:
    """The value, for an observation already known to have one."""
    if observation.value is None:  # pragma: no cover - guarded by the caller's filter
        raise ValueError("an unavailable observation cannot be ordered by value")
    return observation.value


def _pooled(observations: Sequence[FieldObservation]) -> list[WindowOutcome]:
    return [outcome for observation in observations for outcome in observation.outcomes.values()]
