"""Serve the market page, and nothing else.

Phase 11-4. One `GET`, returning the document `MarketPageService` assembles — the same bytes
`scripts/render_market_page.py` writes to a file, which is asserted rather than assumed.

**A document, not a feed.** This module adds no JSON endpoint for candles, positioning or rates,
and it never will: a document is read by a person, while a feed is consumed by a program, and a
program that consumes readings is the first half of something that acts. That distinction is what
the Phase 10-4 safety rule protects now that the API is no longer absolutely closed to a
description.

**Pull, not push.** A page a person opens is not a message a person receives. Telegram pushes, and
Telegram therefore stays absolutely closed — unchanged by this slice, with its rule untouched.

**No authentication here, and that is a decision rather than an omission.** The API is published to
`127.0.0.1` only, so the page is reachable where the operator already is. `X-Internal-API-Key` is a
header a browser cannot send, and a token in a URL would leak through history, logs and referrers.
The cost is named in the phase report and not solved here: another device cannot open this page.
"""

from fastapi import APIRouter, Depends, Response
from fastapi.responses import HTMLResponse

from app.api.dependencies import get_market_page_service
from app.core.time import normalize_to_utc, utc_now
from app.services.market_page_service import MarketPageService

router = APIRouter(prefix="/market", tags=["market"])

#: What is returned when the universe has no stored candles. `503` rather than `404`: the page is
#: not missing, the data behind it has not been ingested yet, and those are different problems for
#: whoever is reading. The wording matches what the script prints for the same condition.
_NOTHING_STORED = "Дневных свечей нет. Сначала запустите заливку вселенной фазы 9D-1."


@router.get("/page", response_class=HTMLResponse)
async def market_page(
    service: MarketPageService = Depends(get_market_page_service),
) -> Response:
    document = await service.document(as_of=normalize_to_utc(utc_now()))
    if document is None:
        return HTMLResponse(content=_NOTHING_STORED, status_code=503)
    return HTMLResponse(content=document)
