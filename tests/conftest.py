import httpx
import pytest


@pytest.fixture(autouse=True)
def block_real_http_network(monkeypatch: pytest.MonkeyPatch) -> None:
    async def blocked_request(*args: object, **kwargs: object) -> httpx.Response:
        raise AssertionError("Real network access is blocked in tests; use httpx.MockTransport.")

    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", blocked_request)
