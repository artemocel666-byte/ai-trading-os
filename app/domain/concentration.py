"""Correlation of daily returns, and how many independent bets a set comes to.

Pure domain: returns in, readings out. No session, no query — the caller that reads storage is the
one place any of that lives, as in `cross_section.py`, `carry.py`, `data_freshness.py` and
`market_state.py`.

**In `Decimal`, with no new dependency.** `Decimal.sqrt()` has been the project's way since
`context_engine.py`, and the concentration measure below avoids eigendecomposition entirely, so
answering this question costs nothing in the dependency list and nothing in exactness.

**The honest limit, stated where it is computed.** A quarter is about sixty-four trading days, which
puts the standard error of a correlation near `1/√64 ≈ 0.12`. **0.3 and 0.5 are not reliably
distinguishable at this window.** That is why every reading carries its halves: the disagreement
between them is the visible part of an uncertainty the coefficient alone hides.
"""

from collections.abc import Mapping, Sequence
from decimal import Decimal
from itertools import combinations

from app.domain.entities.concentration import (
    MINIMUM_OVERLAP,
    ConcentrationReading,
    ConcentrationStatus,
    CorrelationReading,
)


def correlation(left: Sequence[Decimal], right: Sequence[Decimal]) -> Decimal | None:
    """Pearson correlation of two equal-length samples, or `None` when it does not exist.

    `None` rather than zero when either series never moves: a flat series has no variance to
    correlate, and zero would report independence where the question has no answer. That
    substitution is the one this whole module refuses to make.
    """
    count = len(left)
    if count != len(right):
        raise ValueError("a correlation needs two samples of the same length")
    if count < 2:
        return None

    n = Decimal(count)
    mean_left = sum(left, Decimal("0")) / n
    mean_right = sum(right, Decimal("0")) / n
    covariance = Decimal("0")
    variance_left = Decimal("0")
    variance_right = Decimal("0")
    for x, y in zip(left, right, strict=True):
        dx = x - mean_left
        dy = y - mean_right
        covariance += dx * dy
        variance_left += dx * dx
        variance_right += dy * dy
    if variance_left <= 0 or variance_right <= 0:
        return None

    coefficient = covariance / (variance_left * variance_right).sqrt()
    # Floating-free arithmetic still rounds at the 28th digit, so a perfect correlation can land a
    # hair outside the range the entity accepts. Clamping the last digit is honest; widening the
    # entity's bounds to admit an impossible correlation would not be.
    return min(max(coefficient, Decimal("-1")), Decimal("1"))


def read_correlation(
    *,
    left: str,
    right: str,
    left_returns: Sequence[Decimal],
    right_returns: Sequence[Decimal],
) -> CorrelationReading | None:
    """Two instruments over one window, with each half measured separately.

    `None` when the overlap is too short or either half has no answer — an absence, never a zero.
    """
    overlap = len(left_returns)
    if overlap != len(right_returns) or overlap < MINIMUM_OVERLAP:
        return None

    whole = correlation(left_returns, right_returns)
    midpoint = overlap // 2
    first = correlation(left_returns[:midpoint], right_returns[:midpoint])
    second = correlation(left_returns[midpoint:], right_returns[midpoint:])
    if whole is None or first is None or second is None:
        return None

    return CorrelationReading(
        left=left,
        right=right,
        overlap_count=overlap,
        coefficient=whole,
        first_half=first,
        second_half=second,
    )


def aligned_returns(
    left: Mapping[object, Decimal], right: Mapping[object, Decimal]
) -> tuple[list[Decimal], list[Decimal]]:
    """The two series restricted to the moments both were priced, in a stable order.

    Two instruments can only be correlated over days they share. Lining them up by position instead
    of by date would silently pair a Tuesday with a Wednesday whenever one had a holiday the other
    did not — a correlation computed from mismatched days, reported as though it were real.
    """
    shared = sorted(set(left) & set(right), key=str)
    return ([left[key] for key in shared], [right[key] for key in shared])


def read_concentration(
    instruments: Sequence[str],
    returns_by_instrument: Mapping[str, Mapping[object, Decimal]],
) -> ConcentrationReading:
    """How many independent bets a named set of instruments comes to.

    `effective_bets = N² / ΣΣρ`, where the matrix sum is `N` down the diagonal plus twice each
    distinct pair. Perfectly correlated instruments give exactly 1; uncorrelated ones give exactly
    `N`.

    **Every pair must be measurable or nothing is reported.** A set whose concentration was computed
    from the pairs that happened to have enough history would quietly answer a different question
    from the one asked, and the missing pairs are named so a reader knows which.

    **Returns arrive keyed by moment, not as flat sequences, and that is structural rather than
    stylistic.** Alignment is a property of each *pair* — two instruments share whichever days both
    were priced, and a third instrument's holiday is none of their business. Accepting flat lists
    here would let a caller hand over series of equal length that describe different days, and the
    correlation that came back would be real arithmetic over mismatched dates with nothing in the
    output to show it.
    """
    ordered = tuple(instruments)
    correlations: list[CorrelationReading] = []
    missing: list[str] = []
    for left, right in combinations(ordered, 2):
        left_returns, right_returns = aligned_returns(
            returns_by_instrument.get(left, {}), returns_by_instrument.get(right, {})
        )
        reading = read_correlation(
            left=left,
            right=right,
            left_returns=left_returns,
            right_returns=right_returns,
        )
        if reading is None:
            missing.append(f"{left}/{right}")
            continue
        correlations.append(reading)

    if missing:
        return ConcentrationReading(
            instruments=ordered,
            status=ConcentrationStatus.NOT_ENOUGH_OVERLAP,
            correlations=tuple(correlations),
            missing_pairs=tuple(missing),
        )

    count = Decimal(len(ordered))
    matrix_sum = count + 2 * sum((item.coefficient for item in correlations), Decimal("0"))
    if matrix_sum <= 0:
        # Not a large number of bets — no number at all. The correlations cancel, so there is no
        # variance left to divide by, and an enormous figure here would dress a division by zero as
        # a finding.
        return ConcentrationReading(
            instruments=ordered,
            status=ConcentrationStatus.FULLY_HEDGED,
            correlations=tuple(correlations),
        )

    return ConcentrationReading(
        instruments=ordered,
        status=ConcentrationStatus.MEASURED,
        effective_bets=count * count / matrix_sum,
        correlations=tuple(correlations),
    )
