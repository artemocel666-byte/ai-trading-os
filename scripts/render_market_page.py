"""Write the market state to one self-contained file.

Phase 11-1 drew the page; Phase 11-4 moved the drawing into `MarketPageService`, so that the file
and the served route cannot come apart. What is left here is what a script owns and a route does
not: argument parsing, the engine lifecycle, and the write.

Read-only apart from the single file it writes, and that file makes no network request when opened.
"""

import argparse
import asyncio
import sys
from pathlib import Path

from app.core.config import Settings
from app.core.time import normalize_to_utc, utc_now
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory
from app.services.market_page_service import (
    DEFAULT_CORRELATION_DAYS,
    DEFAULT_HISTORY_DAYS,
    DEFAULT_WINDOW_DAYS,
    MarketPageService,
)
from app.services.market_reading_service import MarketReadingService

DEFAULT_OUTPUT = "market_state.html"

#: The newline the file is written with, named rather than inlined so the reason survives beside it.
LINE_ENDING = "\n"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render the market state as one self-contained HTML page. Read-only."
    )
    parser.add_argument("--window-days", type=int, default=DEFAULT_WINDOW_DAYS)
    parser.add_argument("--history-days", type=int, default=DEFAULT_HISTORY_DAYS)
    parser.add_argument("--correlation-days", type=int, default=DEFAULT_CORRELATION_DAYS)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


async def _build_document(args: argparse.Namespace) -> str | None:
    """`None` when there is nothing to draw, which the caller turns into a non-zero exit."""
    settings = Settings(_env_file=None)
    engine = create_engine(args.database_url or settings.database_dsn())
    try:
        service = MarketPageService(
            readings=MarketReadingService(
                uow_factory=build_uow_factory(create_session_factory(engine))
            )
        )
        return await service.document(
            as_of=normalize_to_utc(utc_now()),
            window_days=args.window_days,
            history_days=args.history_days,
            correlation_days=args.correlation_days,
        )
    finally:
        await engine.dispose()


def main() -> None:
    """The file write lives here, not in the coroutine: it is a plain synchronous call."""
    args = _parse_args()
    document = asyncio.run(_build_document(args))
    if document is None:
        print("Дневных свечей нет. Сначала запустите заливку вселенной фазы 9D-1.")
        sys.exit(1)
    output = Path(args.output)
    # An explicit newline so the file holds the document's own bytes. Text mode translates every
    # newline to CRLF on Windows, which made the written file 42 bytes longer than the identical
    # page the route served — the same document, but not the same file, and Phase 11-4's decisive
    # criterion is about bytes. It also stops a page written here and one written inside the
    # container from differing for a reason no reader could see on the page.
    output.write_text(document, encoding="utf-8", newline=LINE_ENDING)
    print(f"Написано: {output.resolve()}  ({len(document):,} байт)")
    sys.exit(0)


if __name__ == "__main__":
    main()
