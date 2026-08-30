import ast
import inspect
from pathlib import Path

from app.core import constants
from app.services import market_reading_service
from app.services.market_reading_service import MarketReadingService

SERVICE_FILE = Path("app/services/market_reading_service.py")

#: The scripts that read the universe. `replay_rules.py` is deliberately absent — see below.
DESCRIPTIVE_SCRIPTS = (
    Path("scripts/profile_carry.py"),
    Path("scripts/profile_cross_section.py"),
    Path("scripts/render_market_page.py"),
    Path("scripts/report_concentration.py"),
    Path("scripts/report_market_state.py"),
)


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_11_3_reading_service"


def test_only_one_place_loads_universe_daily_candles() -> None:
    """Criterion 2. Five scripts each had their own copy; a served page would have been the sixth.

    The sixth copy of anything in this project has historically been the one that disagreed with the
    other five — a half-added timeframe map, a request-range limit read from two places, month
    arithmetic in two scripts before a third needed it.
    """
    offenders = [
        str(path)
        for path in DESCRIPTIVE_SCRIPTS
        if "candles.list_range" in path.read_text(encoding="utf-8")
    ]

    assert offenders == []
    assert "candles.list_range" in SERVICE_FILE.read_text(encoding="utf-8")


def test_only_one_place_derives_daily_returns() -> None:
    """Criterion 3. The same derivation was written out identically in two scripts."""
    marker = "current.close - previous.close"
    offenders = [
        str(path)
        for path in tuple(Path("scripts").rglob("*.py")) + tuple(Path("app").rglob("*.py"))
        if marker in path.read_text(encoding="utf-8") and path != Path("app/domain/market_state.py")
    ]

    assert offenders == []


def test_replay_rules_is_excluded_on_purpose() -> None:
    """Criterion 4. It calls the same repository method and is not the same question.

    `replay_rules.py` loads **one** pair on **any** timeframe with a **lead-in window**, so its
    oldest windows are not artificially incomplete, and it loads economic events beside them.
    Folding it into a service built for "the universe, daily" would force unlike things together —
    the mistake this project avoided when it refused to reuse the 9C-3 decile machinery for a
    cross-section, and again when it refused to merge two vocabularies of different strictness.

    This test exists so the exclusion reads as a decision rather than an oversight.
    """
    source = Path("scripts/replay_rules.py").read_text(encoding="utf-8")

    assert "candles.list_range" in source
    assert "MarketReadingService" not in source
    assert "lead_in" in source


def test_the_service_computes_nothing() -> None:
    """Criterion 5. A service that quietly derives is how a number gets two definitions."""
    tree = ast.parse(SERVICE_FILE.read_text(encoding="utf-8"))
    modules = {
        node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module
    }

    for calculation in ("app.domain.market_state", "app.domain.concentration", "app.domain.carry"):
        assert calculation not in modules, calculation
    # No arithmetic anywhere in the module: it queries, filters and sorts, and nothing else.
    # `ast.BitOr` is excluded because `datetime | None` in an annotation parses as one, and a type
    # union is not a calculation — the same narrowing this project has made four times now, always
    # by naming the exception rather than by loosening the rule.
    arithmetic = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow)
    assert not [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.BinOp) and isinstance(node.op, arithmetic)
    ]


def test_the_service_is_route_ready() -> None:
    """Criterion 6. A route can call it without a rewrite, checked rather than intended.

    Read from the parsed syntax rather than the file text. The module's own docstring names
    `argparse` and `print` in order to explain that it uses neither, and a substring scan would call
    that a violation — the fourth time in this project that a rule has been tripped by the sentence
    describing it, after a comment quoting removed strings, a docstring quoting a banned word, and a
    test naming the constant it searches for.
    """
    tree = ast.parse(SERVICE_FILE.read_text(encoding="utf-8"))
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }

    assert "argparse" not in imported
    assert "sys" not in imported
    assert "print" not in called
    assert "create_engine" not in called


def test_every_read_returns_plain_data() -> None:
    """No `Namespace`, no generator, no lazily-bound session escaping the method."""
    for name in ("daily_candles", "interest_rates", "positioning"):
        method = getattr(MarketReadingService, name)
        annotation = inspect.signature(method).return_annotation
        assert "dict" in str(annotation), name


def test_the_module_names_why_replay_rules_stays_out() -> None:
    """The reasoning lives beside the code, not only in a phase report nobody opens twice."""
    source = market_reading_service.__doc__ or ""

    assert "replay_rules" in source
    assert "lead-in" in source


def test_the_declared_phase_matches_the_constant() -> None:
    """Found in passing, and it is this project's own recurring disease.

    `AGENTS.md` and `README.md` each state the current phase in prose, and both had been left at
    `phase_9d3_interest_rate_ingestion` while the constant moved on through 9D-4, 10-1 to 10-4, 11-1
    and 11-2 — four phases of silent disagreement, in the two files a partner's agent reads first to
    learn where the project stands.

    Historical phase reports are deliberately not checked: each records the phase it was written in,
    and freezing that is the point of them.
    """
    declared = {
        path: line.split("phase:")[1].strip().rstrip(".")
        for path in (Path("AGENTS.md"), Path("README.md"))
        for line in path.read_text(encoding="utf-8").splitlines()
        if "Current project phase:" in line
    }

    assert len(declared) == 2, declared
    for path, phase in declared.items():
        assert phase == constants.PROJECT_PHASE, path
