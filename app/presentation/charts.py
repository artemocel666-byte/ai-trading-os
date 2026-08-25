"""The only module allowed to emit markup, and the closed set of shapes it may emit.

Phase 11-1. Phase 10-2 made the honesty policy executable in text: one renderer, a banned
vocabulary, no central tendency without its spread. **None of that reaches a picture.** A line
rising to the right edge of a canvas implies continuation without a single word, and no list of
forbidden stems can catch it — the eye completes the line whether or not the caption says not to.

So the rule here is about **form**. Four primitives exist, the set is closed, and a test pins it: a
fifth shape becomes a visible decision in a diff rather than something that appears because it
looked good.

**What is forbidden, and why each.**

- **A price line over time.** The one chart everybody draws, and the reason this module has no
  polyline over dates. A line ending at the right edge reads as a beginning. Seven pre-registered
  measurements say we cannot complete it, so we do not draw the invitation.
- **Trend lines, channels, arrows, projections.** Every one extends past the data by construction.
- **Smoothing that reaches beyond the last observation.**
- **Gauges and dials.** A needle inside a coloured zone says where the value *should* be.
- **Colour keyed to quality.** See `SIGN_POSITIVE` below.

**Every primitive draws its own sample size and window inside the image**, never in a caption
outside it, because a crop or a screenshot loses the caption and keeps the picture.
"""

from decimal import Decimal
from html import escape

from app.domain.entities.calibration import FieldDistribution

#: The closed set. A test pins these names; adding one is a deliberate, visible change.
PRIMITIVES: tuple[str, ...] = (
    "distribution_strip",
    "ranked_bars",
    "matrix_grid",
    "plain_rows",
)

#: Colour encodes **sign**, never quality — and green and red are avoided precisely because in this
#: domain they already mean good and bad. Using them for direction would smuggle approval into a
#: stylesheet — the same move the banned vocabulary of Phase 10-2 makes in a sentence, and named
#: there rather than quoted here, since a safety test scans this file for those words. Blue and
#: amber carry direction with no verdict attached.
SIGN_POSITIVE = "#2f6fb2"
SIGN_NEGATIVE = "#b26a2f"
NEUTRAL_INK = "var(--ink)"
GRID_LINE = "var(--grid)"

_STRIP_HEIGHT = 46
_BAR_HEIGHT = 22
_LEFT_GUTTER = 96
_RIGHT_GUTTER = 16
_WIDTH = 720


def _sign_colour(value: Decimal) -> str:
    return SIGN_POSITIVE if value >= 0 else SIGN_NEGATIVE


def _text(x: float, y: float, body: str, *, anchor: str = "start", klass: str = "lbl") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" class="{klass}">'
        f"{escape(body)}</text>"
    )


def _scale(value: Decimal, low: Decimal, high: Decimal, *, left: float, right: float) -> float:
    """Map a value onto the drawing area. Coordinates are floats; the data stays `Decimal`."""
    span = high - low
    if span <= 0:
        return (left + right) / 2
    share = float((value - low) / span)
    return left + share * (right - left)


def _share(value: Decimal) -> str:
    return f"{value * 100:+.2f}%"


def distribution_strip(
    *,
    label: str,
    distribution: FieldDistribution,
    current: Decimal,
    window: str,
) -> str:
    """The whole sample as a strip, with the current value marked on it.

    The literal picture of "94th percentile": the reader sees the spread the number is a position
    within, so the sample *is* the chart rather than something summarised away.

    Reads `median` together with `p05` and `p95` in this same function, which is what the Phase
    11-1 amendment to the 10-2 safety test requires — a primitive drawing only the middle cannot
    get past it.
    """
    low = distribution.minimum
    high = distribution.maximum
    p05 = distribution.p05
    p95 = distribution.p95
    median = distribution.median
    if low is None or high is None or p05 is None or p95 is None or median is None:
        return _empty(label)

    left = float(_LEFT_GUTTER)
    right = float(_WIDTH - _RIGHT_GUTTER)
    mid = _STRIP_HEIGHT / 2

    def x(value: Decimal) -> float:
        return _scale(value, low, high, left=left, right=right)

    parts = [
        f'<svg viewBox="0 0 {_WIDTH} {_STRIP_HEIGHT}" class="chart" role="img" '
        f'aria-label="{escape(label)}">',
        _text(0, mid + 4, label),
        f'<line x1="{left:.1f}" y1="{mid:.1f}" x2="{right:.1f}" y2="{mid:.1f}" class="axis"/>',
        f'<rect x="{x(p05):.1f}" y="{mid - 7:.1f}" width="{max(x(p95) - x(p05), 1):.1f}" '
        f'height="14" class="band"/>',
        f'<line x1="{x(median):.1f}" y1="{mid - 10:.1f}" x2="{x(median):.1f}" '
        f'y2="{mid + 10:.1f}" class="mid-tick"/>',
        f'<circle cx="{x(current):.1f}" cy="{mid:.1f}" r="5" fill="{_sign_colour(current)}"/>',
        _text(left, _STRIP_HEIGHT - 2, _share(low), klass="tick"),
        _text(right, _STRIP_HEIGHT - 2, _share(high), anchor="end", klass="tick"),
        # n and window live inside the image: a crop keeps the picture and loses a caption.
        _text(
            (left + right) / 2,
            12,
            f"сейчас {_share(current)} · медиана {_share(median)} · "
            f"наблюдений {distribution.observed_count} · {window}",
            anchor="middle",
            klass="tick",
        ),
        "</svg>",
    ]
    return "".join(parts)


def ranked_bars(
    *,
    label: str,
    rows: tuple[tuple[str, Decimal, Decimal, Decimal], ...],
    window: str,
    sample_note: str,
) -> str:
    """A ranking where every bar carries the low-to-high range it was averaged over.

    A mean without its range is the Phase 10-2 failure drawn instead of written: a bar near zero
    over a wide range and a bar near zero over a narrow one are different facts, and a bar alone
    cannot tell them apart.

    Each row is `(name, mean, lowest, highest)`.
    """
    if not rows:
        return _empty(label)

    lows = [row[2] for row in rows]
    highs = [row[3] for row in rows]
    low = min(min(lows), Decimal("0"))
    high = max(max(highs), Decimal("0"))
    left = float(_LEFT_GUTTER)
    right = float(_WIDTH - _RIGHT_GUTTER)
    height = _BAR_HEIGHT * len(rows) + 34

    def x(value: Decimal) -> float:
        return _scale(value, low, high, left=left, right=right)

    zero = x(Decimal("0"))
    parts = [
        f'<svg viewBox="0 0 {_WIDTH} {height}" class="chart" role="img" '
        f'aria-label="{escape(label)}">',
        _text(
            (left + right) / 2,
            12,
            f"{label} · {sample_note} · {window}",
            anchor="middle",
            klass="tick",
        ),
        f'<line x1="{zero:.1f}" y1="20" x2="{zero:.1f}" y2="{height - 14}" class="axis"/>',
    ]
    for index, (name, mean, lowest, highest) in enumerate(rows):
        top = 20 + index * _BAR_HEIGHT
        centre = top + _BAR_HEIGHT / 2
        bar_left = min(zero, x(mean))
        bar_width = max(abs(x(mean) - zero), 1)
        parts.extend(
            [
                _text(0, centre + 4, name),
                f'<line x1="{x(lowest):.1f}" y1="{centre:.1f}" x2="{x(highest):.1f}" '
                f'y2="{centre:.1f}" class="whisker"/>',
                f'<rect x="{bar_left:.1f}" y="{centre - 6:.1f}" width="{bar_width:.1f}" '
                f'height="12" fill="{_sign_colour(mean)}"/>',
                _text(right, centre + 4, _share(mean), anchor="end", klass="tick"),
            ]
        )
    parts.extend(
        [
            _text(left, height - 2, _share(low), klass="tick"),
            _text(right, height - 2, _share(high), anchor="end", klass="tick"),
            "</svg>",
        ]
    )
    return "".join(parts)


def matrix_grid(
    *,
    label: str,
    names: tuple[str, ...],
    values: dict[tuple[str, str], Decimal],
    window: str,
    sample_note: str,
) -> str:
    """A labelled grid whose colour is redundant rather than load-bearing.

    Every cell shows its number, so the shading adds speed and never carries meaning by itself. A
    reader who ignores colour entirely loses nothing, which is the test a heatmap should pass and
    usually does not.
    """
    if not names:
        return _empty(label)

    cell = 34
    gutter = 54
    size = gutter + cell * len(names) + 24
    parts = [
        f'<svg viewBox="0 0 {size} {size}" class="chart" role="img" aria-label="{escape(label)}">',
        _text(gutter, 12, f"{label} · {sample_note} · {window}", klass="tick"),
    ]
    for row, left_name in enumerate(names):
        y = gutter + row * cell
        parts.append(_text(gutter - 6, y + cell / 2 + 4, left_name, anchor="end", klass="tick"))
        parts.append(
            _text(
                gutter + row * cell + cell / 2, gutter - 6, left_name, anchor="middle", klass="tick"
            )
        )
        for column, right_name in enumerate(names):
            if row == column:
                continue
            value = values.get((left_name, right_name)) or values.get((right_name, left_name))
            if value is None:
                continue
            x = gutter + column * cell
            opacity = min(abs(float(value)), 1.0) * 0.55
            parts.extend(
                [
                    f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                    f'fill="{_sign_colour(value)}" fill-opacity="{opacity:.2f}"/>',
                    _text(
                        x + cell / 2,
                        y + cell / 2 + 4,
                        f"{value:+.2f}",
                        anchor="middle",
                        klass="cell",
                    ),
                ]
            )
    parts.append("</svg>")
    return "".join(parts)


def plain_rows(*, label: str, rows: tuple[tuple[str, str], ...]) -> str:
    """The plumbing block. Read first here too, as in every phase since 9D-1."""
    body = "".join(
        f'<tr><th scope="row">{escape(name)}</th><td>{escape(value)}</td></tr>'
        for name, value in rows
    )
    return f'<table class="rows"><caption>{escape(label)}</caption><tbody>{body}</tbody></table>'


def _empty(label: str) -> str:
    """An absence drawn as an absence. Never an empty axis, which reads as a measured zero."""
    return f'<p class="absent">{escape(label)}: нет данных</p>'
