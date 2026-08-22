"""The only place a distribution becomes text.

Phase 10-2, and the whole point of the slice. `FieldDistribution` has refused to *hold* a lonely
central tendency since Phase 4 — its validator says an observed field must report every percentile —
but nothing stopped a formatter from holding a complete distribution and printing only its middle.
The data obeyed the rule; the rendering did not.

**So there is exactly one function that renders a distribution, and it always emits three things:
the sample size, the spread, and the middle.** A test searches every layer a person reads for
anything else formatting a median. The rule then holds by construction rather than by review.

**Why the rule at all.** Seven pre-registered measurements say the dispersion swamps the middle in
this data. Showing `n` and the spread is a description a reader can weigh; showing the middle alone
is a forecast whether or not that was the intent, because a lone central tendency invites the reader
to expect it.

**Where the rule does not apply.** A current observation is not a collapsed distribution. Today's
carry differential is one number because it *is* one number, and demanding a spread around it would
be cargo-culting the rule rather than applying it.

**No vocabulary of expectation.** Nothing here may say `обычно`, `ожидается`, `вероятно`,
`перекуплен` or `перепродан`: each smuggles a forecast into what is meant to be a description, and
`перекуплен` does it inside a single word. A test enforces the list.
"""

from decimal import Decimal

from app.domain.entities.calibration import FieldDistribution
from app.domain.entities.market_state import CurrencyStrengthReading, HistoricalReading

#: Rendered when a value is genuinely not there. Named, never substituted with a zero.
UNAVAILABLE_RU = "нет данных"


def _share(value: Decimal) -> str:
    return f"{value * 100:+.2f}%"


def format_distribution(distribution: FieldDistribution) -> str:
    """A sample rendered as its size, its spread and its middle — never fewer than all three.

    This is the function criterion 1 of the Phase 10-2 pre-registration is about. If a caller wants
    only the median, the answer is that it may not have it.
    """
    if distribution.observed_count == 0:
        return UNAVAILABLE_RU
    return (
        f"медиана {_share(_required(distribution.median))}, "
        f"разброс {_share(_required(distribution.p05))} .. "
        f"{_share(_required(distribution.p95))}, "
        f"наблюдений {distribution.observed_count}"
    )


def _required(value: Decimal | None) -> Decimal:
    """The entity guarantees these are present once anything was observed."""
    if value is None:  # pragma: no cover - forbidden by FieldDistribution's own validator
        raise ValueError("an observed distribution must carry every percentile")
    return value


def format_historical_reading(reading: HistoricalReading) -> str:
    """Today's value with the scale that makes it mean something."""
    return (
        f"{reading.instrument}: сейчас {_share(reading.current)}, "
        f"это {reading.percentile}-й перцентиль собственной истории; "
        f"{format_distribution(reading.distribution)}"
    )


def format_currency_strength(reading: CurrencyStrengthReading) -> str:
    """One currency against all its counterparts, with the range it was averaged over.

    The range is not decoration. A mean of nine moves that were all positive and a mean of nine that
    cancelled are different facts, and the reader is the one who decides what to make of that — this
    line does not decide for them.
    """
    breadth = (
        "в одну сторону против всех" if reading.is_broad else "разнонаправленно против разных валют"
    )
    return (
        f"{reading.currency}: в среднем {_share(reading.mean_move)} "
        f"против {reading.observation_count} валют, "
        f"от {_share(reading.lowest_move)} до {_share(reading.highest_move)} — {breadth}"
    )
