import ast
import inspect
from pathlib import Path

from app.core import constants
from app.services.market_page_service import MarketPageService

SERVICE_FILE = Path("app/services/market_page_service.py")
SCRIPT_FILE = Path("scripts/render_market_page.py")
ROUTE_FILE = Path("app/api/routes/market.py")


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_11_4_market_page_route"


def test_the_document_is_assembled_in_exactly_one_place() -> None:
    """Criterion 1. The script held the whole document; the route would have been the second copy.

    Phase 11-3 removed the fifth copy of a loader. This is the same disease one level up, and the
    same answer: the section-building functions live once, and both callers ask for a document
    rather than building one.
    """
    service = SERVICE_FILE.read_text(encoding="utf-8")
    for section in ("_plumbing_section", "_strength_section", "_grid_section", "build_page"):
        assert section in service, section

    for caller in (SCRIPT_FILE, ROUTE_FILE):
        source = caller.read_text(encoding="utf-8")
        assert "MarketPageService" in source, caller
        for section in ("_plumbing_section", "_strength_section", "_grid_section", "build_page"):
            assert section not in source, (caller, section)


def test_both_callers_reach_the_same_method() -> None:
    """Criterion 3, structurally. The byte comparison is in the phase report; this is the guard.

    A comparison of output can only be run where a populated database exists. This runs everywhere,
    and it fails the moment either caller grows its own way of producing the page.
    """
    for caller in (SCRIPT_FILE, ROUTE_FILE):
        assert ".document(" in caller.read_text(encoding="utf-8"), caller


def test_the_windows_are_defined_once() -> None:
    """The route needs the same defaults the script offers; a second copy is how they diverge."""
    script = SCRIPT_FILE.read_text(encoding="utf-8")

    assert "from app.services.market_page_service import" in script
    for constant in ("DEFAULT_WINDOW_DAYS", "DEFAULT_HISTORY_DAYS", "DEFAULT_CORRELATION_DAYS"):
        assert f"{constant} =" not in script, constant
        assert f"{constant} = " in SERVICE_FILE.read_text(encoding="utf-8"), constant


def test_the_service_opens_no_connection_and_writes_no_file() -> None:
    """A script owns its engine lifecycle and a route owns neither; the assembly owns nothing.

    Checked against the parsed syntax rather than the file text, for the reason Phase 11-3 recorded:
    a module that explains what it does not do would otherwise be caught by the sentence saying so.
    """
    tree = ast.parse(SERVICE_FILE.read_text(encoding="utf-8"))
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    attributes = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }

    for forbidden in ("create_engine", "create_session_factory", "build_uow_factory", "open"):
        assert forbidden not in called, forbidden
    for forbidden in ("write_text", "write_bytes", "dispose"):
        assert forbidden not in attributes, forbidden


def test_the_page_is_returned_rather_than_printed() -> None:
    """`None` when nothing is stored, so each caller decides what an empty universe means to it."""
    annotation = inspect.signature(MarketPageService.document).return_annotation

    assert "str" in str(annotation)
    assert "None" in str(annotation)


def test_the_route_carries_no_authentication_and_says_why() -> None:
    """The absence is a decision, and a decision left unexplained reads as an oversight.

    The API is published to loopback only, which is what makes an unauthenticated read acceptable
    here; `test_phase11_4_the_api_binding_is_not_widened` is what keeps that true.
    """
    source = ROUTE_FILE.read_text(encoding="utf-8")

    assert "require_internal_api_key" not in source
    assert "127.0.0.1" in source


def test_the_price_helpers_left_the_cross_section_behind() -> None:
    """Found while building the route, and fixed by moving rather than by widening a rule.

    The page needs a move over a window and a price at a date. Both lived in `cross_section.py`
    because Phase 9D-2 needed them first, so importing them would have dragged the word
    `cross_section` into a service and forced the 9D-2 delivery rule to admit a module the page
    never touches. The ranking — the part that is structurally a direction — stayed behind.
    """
    price_series = Path("app/domain/price_series.py").read_text(encoding="utf-8")
    cross_section = Path("app/domain/cross_section.py").read_text(encoding="utf-8")

    for moved in ("def forward_return", "def latest_close_at"):
        assert moved in price_series, moved
        assert moved not in cross_section, moved

    # The ranking did not follow them out.
    assert "def build_cross_section_profile" in cross_section
    assert "bucket" not in price_series.lower()
