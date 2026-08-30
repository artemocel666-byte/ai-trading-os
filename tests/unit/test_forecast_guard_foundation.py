from pathlib import Path

import pytest

from app.adapters.chat_completions_explanations import SYSTEM_PROMPT_RU
from app.core import constants
from app.domain.entities.explanation import ExplanationIssueCode
from app.domain.explanation_contract import (
    contains_actionable_russian_text,
    contains_forecast_russian_text,
)


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_11_4_market_page_route"


#: Criterion 2, and the criterion that decides the slice: each pattern carries the sentence it must
#: reject **and** the near miss it must let through. A rule that rejects honest description along
#: with forecasting is worse than the gap it closes, because it will be switched off.
REJECT_AND_ACCEPT = (
    (
        "Обычно после такого движение замедляется.",
        "Волатильность обычная для этой пары.",
    ),
    (
        "Ожидается снижение волатильности.",
        "Отчёт вышел позже, чем предполагал график публикаций.",
    ),
    (
        "Вероятно, диапазон сузится.",
        "Диапазон сузился по сравнению с медианой.",  # noqa: RUF001
    ),
    (
        "Пара выглядит перекупленной.",
        "Пара находится в 94-м перцентиле собственной истории.",
    ),
    (
        "Позиционирование экстремальное.",
        "Позиционирование в третьем перцентиле за 1930 наблюдений.",
    ),
    (
        "Прогноз по паре нейтральный.",
        "Описание состояния на сегодняшнюю дату.",
    ),
    (
        "Цена продолжит движение вверх.",
        "Цена выросла за последние пять дней.",
    ),
)


@pytest.mark.parametrize(("forecast", "description"), REJECT_AND_ACCEPT)
def test_a_forecast_is_caught_and_its_near_miss_is_not(forecast: str, description: str) -> None:
    assert contains_forecast_russian_text(forecast), forecast
    assert not contains_forecast_russian_text(description), description


def test_the_adverb_is_the_forecast_word_and_the_adjective_is_not() -> None:
    """The distinction the whole design turns on.

    A ban on the stem `обычн` would reject both of these. Phase 8D measured what that costs: the
    same model went from 20% to 85% accepted, and a rule that quietly undoes that has removed the
    feature rather than secured it.
    """
    assert contains_forecast_russian_text("Обычно волатильность падает.")
    assert not contains_forecast_russian_text("Обычная волатильность для этой пары.")
    assert not contains_forecast_russian_text("Это обычное значение.")


def test_advice_and_forecasting_are_different_faults() -> None:
    """`ACTIONABLE_TEXT` and `FORECAST_TEXT` exist apart because they are not the same mistake.

    "Покупайте" tells a person what to do and was already refused. "Обычно после такого движение
    замедляется" advises nothing at all and forecasts everything.
    """
    advice = "Покупайте на откате."
    forecast = "Обычно после такого движение замедляется."

    assert contains_actionable_russian_text(advice)
    assert not contains_forecast_russian_text(advice)
    assert contains_forecast_russian_text(forecast)
    assert not contains_actionable_russian_text(forecast)


def test_the_issue_codes_stay_distinct() -> None:
    assert ExplanationIssueCode.FORECAST_TEXT != ExplanationIssueCode.ACTIONABLE_TEXT
    assert ExplanationIssueCode.FORECAST_TEXT.value == "FORECAST_TEXT"


def test_the_prompt_asks_for_what_the_validator_enforces() -> None:
    """Criterion 5. Enforcing a rule the prompt never mentions is how acceptance collapses.

    Phase 8D measured that asking properly is what took the same model from 20% to 85%.
    """
    assert "будущем" in SYSTEM_PROMPT_RU
    for word in ("обычно", "ожидается", "вероятно", "прогноз"):
        assert word in SYSTEM_PROMPT_RU, word


def test_the_forbidden_list_lives_in_exactly_one_place() -> None:
    """Criterion 3, and it landed differently from how it was written.

    The pre-registration expected one list. Building it showed two strictnesses that must differ: a
    stem is right over our own prose, where a false catch costs a rewrite, and wrong over a model's
    answer, where 8D measured that over-rejection takes acceptance back toward 20%. So the domain
    holds the *judgement* once — `_FORECAST_RUSSIAN_PATTERNS`, read through `forecast_claims` — and
    both the validator and the safety test call it, rather than one list serving two jobs badly.

    Four repairs of the real fault are on record: the delta map, the request-range limit, the month
    arithmetic, and nine copies of a unit-of-work alias.
    """
    # This file names the constant in order to search for it, so it excludes itself. Otherwise the
    # check fails on its own text — the third self-reference trap in this project, after a comment
    # that quoted the strings it had just removed and a docstring that quoted a banned word.
    myself = Path(__file__).resolve()
    searched = [
        path
        for path in tuple(Path("app").rglob("*.py")) + tuple(Path("tests").rglob("*.py"))
        if path.resolve() != myself
    ]
    marker = "_FORECAST_RUSSIAN" + "_PATTERNS = ("
    homes = [path for path in searched if marker in path.read_text(encoding="utf-8")]

    assert homes == [Path("app/domain/explanation_contract.py")]
