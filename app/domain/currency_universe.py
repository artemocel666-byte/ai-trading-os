"""The set of currencies this project compares against each other, and the pairs they imply.

Phase 9D-1. Every measurement before it asked a question about **one series through time**: what
follows a window on EURUSD. Five phases answered nothing. The question changes here to a comparison
**across instruments at one moment**, which needs more than two of them.

**The currencies are the pre-registered choice; the pairs are derived.** Listing pairs directly
would let one be added or dropped later to suit a result. Deriving them from a fixed currency set
means the universe can only change by changing that set, which is a visible decision.

**Pairs are not independent observations, and this module cannot fix that.** Ten currencies give
forty-five pairs, but every pair is a ratio of two members of the same small set, so the number of
genuinely independent dimensions is closer to nine. Anything bucketing these pairs is bucketing
correlated things, and the report that does it has to say so.

**Order within a pair is a market convention, not a preference.** `EURUSD` is quoted and `USDEUR`
is not, and a provider asked for the wrong direction returns nothing. The convention is a precedence
list, encoded below.
"""

from itertools import combinations

from app.domain.value_objects import CurrencyPair

#: Conventional quoting precedence: the earlier currency is the base. This ordering is what makes
#: `EURUSD`, `USDJPY`, `NOKSEK` and `CHFJPY` come out the way the market writes them.
QUOTE_PRECEDENCE: tuple[str, ...] = (
    "EUR",
    "GBP",
    "AUD",
    "NZD",
    "USD",
    "CAD",
    "CHF",
    "NOK",
    "SEK",
    "JPY",
)

#: The pre-registered universe: the eight currencies the majors are built from, plus the two the
#: project already stores history for. Fixed before any measurement, and changed only deliberately.
UNIVERSE_CURRENCIES: frozenset[str] = frozenset(QUOTE_PRECEDENCE)


def universe_pairs(currencies: frozenset[str] = UNIVERSE_CURRENCIES) -> tuple[CurrencyPair, ...]:
    """Every pair the universe implies, each written the way the market quotes it.

    Deterministic and sorted, so two runs request the same symbols in the same order — a report
    that lists which pairs a provider refused is only comparable if the asking order is stable.

    Whether a provider actually quotes a given pair is an **observation**, not something this
    module can know. The caller records the refusals rather than quietly shrinking the universe.
    """
    unknown = sorted(currencies - set(QUOTE_PRECEDENCE))
    if unknown:
        raise ValueError(f"no quoting precedence is defined for: {', '.join(unknown)}")

    rank = {currency: index for index, currency in enumerate(QUOTE_PRECEDENCE)}
    ordered = sorted(currencies, key=lambda currency: rank[currency])
    return tuple(CurrencyPair(value=f"{base}{quote}") for base, quote in combinations(ordered, 2))
