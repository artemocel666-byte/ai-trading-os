import inspect
from decimal import Decimal
from pathlib import Path

import pytest

from app.core import constants
from app.domain.rule_calibration import summarize_field
from app.presentation import charts
from app.presentation.charts import (
    PRIMITIVES,
    SIGN_NEGATIVE,
    SIGN_POSITIVE,
    distribution_strip,
    matrix_grid,
    plain_rows,
    ranked_bars,
)
from app.presentation.page import build_page

WINDOW = "история 730 дн."


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_11_3_reading_service"


def test_the_primitive_set_is_closed() -> None:
    """Criterion 2. Adding a fifth shape must be a visible decision, not something that appears."""
    assert PRIMITIVES == ("distribution_strip", "ranked_bars", "matrix_grid", "plain_rows")
    public = {
        name
        for name, value in vars(charts).items()
        if callable(value) and not name.startswith("_") and value.__module__ == charts.__name__
    }
    assert public == set(PRIMITIVES)


def test_no_time_series_line_primitive_exists() -> None:
    """Criterion 3, and the criterion that decides the slice.

    A price line over time is the one chart everybody draws, and a line ending at the right edge is
    read as a beginning: the eye completes it. Seven pre-registered measurements say we cannot
    complete it, so the invitation is not drawn — there is no polyline, no path, and nothing keyed
    to a sequence of dates anywhere in the module.
    """
    source = Path("app/presentation/charts.py").read_text(encoding="utf-8")

    for forbidden in ("<polyline", "<path", 'd="M', "sparkline", "trendline"):
        assert forbidden not in source, forbidden
    assert not any("series" in name or "line_chart" in name for name in PRIMITIVES)


def test_a_drawn_middle_never_travels_without_its_edges() -> None:
    """Criterion 4, the Phase 11-1 amendment, checked against each function's own source."""
    for name in PRIMITIVES:
        source = inspect.getsource(getattr(charts, name))
        if ".median" in source:
            assert ".p05" in source, name
            assert ".p95" in source, name


def test_colour_is_keyed_to_sign_and_carries_no_verdict() -> None:
    """Criterion 5. Green and red are absent on purpose: here they already mean good and bad."""
    source = Path("app/presentation/charts.py").read_text(encoding="utf-8").lower()

    for forbidden in ("good", "bad", "bull", "bear", "success", "danger", "warning"):
        assert f'"{forbidden}"' not in source, forbidden
    for green_or_red in ("#0f0", "#f00", "green", "red"):
        assert green_or_red not in {SIGN_POSITIVE.lower(), SIGN_NEGATIVE.lower()}
    assert SIGN_POSITIVE != SIGN_NEGATIVE


def _distribution() -> object:
    return summarize_field("daily_range", [Decimal(n) / Decimal(1000) for n in range(1, 61)])


def test_a_strip_draws_its_sample_size_and_window_inside_the_image() -> None:
    """Criterion 6. A crop loses a caption and keeps the picture, so it lives in the picture."""
    markup = distribution_strip(
        label="EURUSD", distribution=_distribution(), current=Decimal("0.055"), window=WINDOW
    )

    assert "<svg" in markup
    assert "наблюдений 60" in markup
    assert WINDOW in markup
    assert "медиана" in markup


def test_a_bar_carries_the_range_it_was_averaged_over() -> None:
    markup = ranked_bars(
        label="Валюты",
        rows=(("USD", Decimal("0"), Decimal("-0.02"), Decimal("0.02")),),
        window=WINDOW,
        sample_note="пар 44",
    )

    # A mean of zero over a wide range must not look like a mean of zero over a narrow one.
    assert "whisker" in markup
    assert "пар 44" in markup


def test_an_absent_reading_is_drawn_as_an_absence_not_an_empty_axis() -> None:
    """An empty axis reads as a measured zero, which is the substitution this project refuses."""
    markup = ranked_bars(label="Валюты", rows=(), window=WINDOW, sample_note="")

    assert "<svg" not in markup
    assert "нет данных" in markup


def test_a_grid_labels_every_cell_so_colour_is_redundant() -> None:
    markup = matrix_grid(
        label="Корреляции",
        names=("EURUSD", "GBPUSD"),
        values={("EURUSD", "GBPUSD"): Decimal("0.81")},
        window=WINDOW,
        sample_note="общих дней 85",
    )

    assert "+0.81" in markup
    assert "общих дней 85" in markup


def test_markup_is_escaped() -> None:
    markup = plain_rows(label="<script>", rows=(("<b>", "&"),))

    assert "<script>" not in markup
    assert "&lt;script&gt;" in markup


def test_the_page_is_self_contained() -> None:
    """Criterion 7. A page that reaches out can be tracked, can break offline, and can change."""
    document = build_page(title="Тест", subtitle="описание", sections=(("Раздел", "<p>тело</p>"),))

    for forbidden in ("http://", "https://", "<script", "@import", "<iframe"):
        assert forbidden not in document, forbidden
    assert document.startswith("<!doctype html>")
    assert 'lang="ru"' in document


def test_the_page_says_what_it_is_not() -> None:
    document = build_page(title="Заголовок", subtitle="подпись", sections=())

    assert "не прогноз" in document
    assert "Цвет означает знак" in document


@pytest.mark.parametrize("value", [Decimal("0.01"), Decimal("-0.01")])
def test_sign_decides_colour(value: Decimal) -> None:
    markup = ranked_bars(
        label="X",
        rows=(("A", value, value, value),),
        window=WINDOW,
        sample_note="n 1",
    )
    expected = SIGN_POSITIVE if value > 0 else SIGN_NEGATIVE

    assert expected in markup
