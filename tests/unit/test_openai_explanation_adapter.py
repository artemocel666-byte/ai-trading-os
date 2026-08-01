"""Phase 8B: the adapter's contract, and proof that a lying model changes nothing.

Every test runs through `httpx.MockTransport` — no key, no network, no spend.
"""

import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import httpx
import pytest

from app.adapters.disabled import DisabledExplanationProvider
from app.adapters.factories import create_explanation_provider
from app.adapters.openai_explanations import (
    SYSTEM_PROMPT_RU,
    OpenAIExplanationAdapter,
)
from app.core.config import Settings
from app.core.exceptions import (
    ConfigurationInvalidError,
    IntegrationDisabledError,
    ProviderAuthenticationError,
    ProviderInvalidPayloadError,
    ProviderMalformedJsonError,
    ProviderPlanRestrictedError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ProviderUnsupportedRequestError,
)
from app.domain.analysis_engine import AnalysisEngine
from app.domain.entities import Candle, Timeframe
from app.domain.entities.explanation import ExplanationIssueCode, ExplanationOutcome
from app.domain.explanation_contract import build_explanation_input
from app.domain.strategy_decision_composer import StrategyDecisionComposer
from app.domain.value_objects import CurrencyPair

PAIR = CurrencyPair(value="EURUSD")
BASE_TIME = datetime(2026, 7, 20, 8, 0, tzinfo=UTC)
CHECKED_AT = datetime(2026, 8, 1, 12, 0, tzinfo=UTC)
STEP = timedelta(minutes=15)
API_KEY = "secret-openai-key"

HONEST_ANSWER = (
    "Окно данных полное: использовано 12 свечей из 12. "
    "Проверки качества данных пройдены. "
    "Часть проверок недоступна, потому что в окне нет экономических событий."
)


def _candle(index: int) -> Candle:
    open_time = BASE_TIME + (index * STEP)
    open_price = Decimal("1.1000") + (Decimal("0.0001") * Decimal(index))
    close_price = open_price + Decimal("0.0001")
    return Candle(
        provider="openai-adapter-test",
        pair=PAIR,
        timeframe=Timeframe.M15,
        open_time=open_time,
        close_time=open_time + STEP,
        open=open_price,
        high=close_price + Decimal("0.0002"),
        low=open_price - Decimal("0.0002"),
        close=close_price,
        volume=Decimal("100"),
        is_closed=True,
    )


def _decision_and_input(candle_count: int = 12):
    candles = [_candle(index) for index in range(candle_count)]
    as_of = BASE_TIME + (candle_count * STEP)
    snapshot = AnalysisEngine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=BASE_TIME,
        window_end=as_of,
        as_of=as_of,
        candles=candles,
        economic_events=[],
        moving_average_windows=(3,),
    )
    decision = StrategyDecisionComposer().compose(snapshot, as_of)
    return decision, build_explanation_input(decision, snapshot)


def _adapter(
    handler: Callable[[httpx.Request], httpx.Response],
    *,
    retry_count: int = 1,
) -> tuple[OpenAIExplanationAdapter, httpx.AsyncClient]:
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    adapter = OpenAIExplanationAdapter(
        client=client,
        api_key=API_KEY,
        base_url="https://openai.test",
        model="test-model",
        timeout=httpx.Timeout(connect=1, read=1, write=1, pool=1),
        retry_count=retry_count,
        retry_backoff_seconds=0,
        max_output_tokens=400,
    )
    return adapter, client


def _completion(content: str) -> httpx.Response:
    return httpx.Response(
        200,
        json={"choices": [{"message": {"role": "assistant", "content": content}}]},
    )


def _answering(content: str) -> Callable[[httpx.Request], httpx.Response]:
    return lambda request: _completion(content)


@pytest.mark.asyncio
async def test_request_carries_the_contract_and_the_key_stays_in_the_header() -> None:
    captured: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured
        captured = request
        return _completion(HONEST_ANSWER)

    _decision, explanation_input = _decision_and_input()
    adapter, client = _adapter(handler)
    async with client:
        await adapter.explain(explanation_input)

    assert captured is not None
    assert captured.url.path == "/v1/chat/completions"
    assert captured.headers["Authorization"] == f"Bearer {API_KEY}"
    assert API_KEY not in str(captured.url)

    body = json.loads(captured.content)
    assert body["model"] == "test-model"
    assert body["temperature"] == 0
    assert body["max_tokens"] == 400
    assert body["messages"][0]["content"] == SYSTEM_PROMPT_RU
    # The user message is the contract and nothing else: no snapshot internals, no raw candles.
    assert body["messages"][1]["content"] == explanation_input.deterministic_json()
    assert set(body) == {"model", "temperature", "max_tokens", "messages"}


@pytest.mark.asyncio
async def test_prompt_never_carries_price_series_or_scoring_fields() -> None:
    _decision, explanation_input = _decision_and_input()
    adapter, client = _adapter(_answering(HONEST_ANSWER))
    async with client:
        body = adapter.build_request_body(explanation_input)
    user_message = body["messages"][1]["content"].lower()

    for forbidden in ("open_time", "close_price", "setup", "risk_percent", "direction"):
        assert forbidden not in user_message


@pytest.mark.asyncio
async def test_honest_answer_is_returned_and_accepted() -> None:
    _decision, explanation_input = _decision_and_input()
    adapter, client = _adapter(_answering(HONEST_ANSWER))
    async with client:
        outcome = await adapter.explain_validated(explanation_input, CHECKED_AT)

    assert isinstance(outcome, ExplanationOutcome)
    assert outcome.accepted is True
    assert outcome.text == HONEST_ANSWER
    assert outcome.model_name == "test-model"
    assert outcome.is_actionable is False


@pytest.mark.parametrize(
    ("label", "lie", "expected_code"),
    [
        (
            "buy instruction with an invented target",
            "ПОКУПАЙ EURUSD прямо сейчас, цель 1.25.",
            ExplanationIssueCode.ACTIONABLE_TEXT,
        ),
        (
            "invented pass count",
            "Правила пройдены полностью: 47 из 11.",
            ExplanationIssueCode.UNKNOWN_NUMBER,
        ),
        (
            "emoji",
            "Окно данных полное 📈 замеры в норме.",
            ExplanationIssueCode.EMOJI_FOUND,
        ),
        (
            "english only",
            "The window is complete and every rule passed.",
            ExplanationIssueCode.NOT_RUSSIAN,
        ),
        (
            "runaway length",
            "Окно данных полное. " * 200,
            ExplanationIssueCode.TOO_LONG,
        ),
    ],
)
@pytest.mark.asyncio
async def test_a_lying_model_is_rejected_and_changes_nothing(
    label: str,
    lie: str,
    expected_code: ExplanationIssueCode,
) -> None:
    """The point of Phase 8B: whatever the model says, the deterministic report is untouched."""
    decision, explanation_input = _decision_and_input()
    decision_fingerprint = decision.fingerprint_sha256()
    input_fingerprint = explanation_input.fingerprint_sha256()

    adapter, client = _adapter(_answering(lie))
    async with client:
        outcome = await adapter.explain_validated(explanation_input, CHECKED_AT)

    assert outcome.accepted is False, label
    assert outcome.text is None, label
    assert expected_code in outcome.validation.issue_codes, label
    # Byte-for-byte identical: the model cannot rewrite what it was asked to describe.
    assert decision.fingerprint_sha256() == decision_fingerprint
    assert explanation_input.fingerprint_sha256() == input_fingerprint


@pytest.mark.asyncio
async def test_a_rejected_answer_cannot_be_read_back_out_of_the_outcome() -> None:
    """The rejected prose is gone, so nothing downstream can print or "repair" it.

    The offending number itself does survive, inside the issue detail. That is deliberate: an
    operator needs to know which figure was invented, and a bare token instructs no one.
    """
    _decision, explanation_input = _decision_and_input()
    adapter, client = _adapter(_answering("ПОКУПАЙ сейчас, цель 1.25."))
    async with client:
        outcome = await adapter.explain_validated(explanation_input, CHECKED_AT)

    serialized = outcome.model_dump_json()
    assert outcome.text is None
    assert "ПОКУПАЙ" not in serialized
    assert "цель" not in serialized
    assert ExplanationIssueCode.UNKNOWN_NUMBER in outcome.validation.issue_codes


@pytest.mark.parametrize(
    ("status_code", "expected_error"),
    [
        (401, ProviderAuthenticationError),
        (403, ProviderAuthenticationError),
        (402, ProviderPlanRestrictedError),
        (429, ProviderRateLimitError),
        (400, ProviderUnsupportedRequestError),
        (404, ProviderUnsupportedRequestError),
    ],
)
@pytest.mark.asyncio
async def test_status_codes_map_to_provider_errors(
    status_code: int,
    expected_error: type[Exception],
) -> None:
    _decision, explanation_input = _decision_and_input()
    adapter, client = _adapter(lambda request: httpx.Response(status_code, json={}))
    async with client:
        with pytest.raises(expected_error):
            await adapter.explain(explanation_input)


@pytest.mark.asyncio
async def test_server_errors_are_retried_then_reported_unavailable() -> None:
    calls: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        return httpx.Response(503, json={})

    _decision, explanation_input = _decision_and_input()
    adapter, client = _adapter(handler, retry_count=2)
    async with client:
        with pytest.raises(ProviderUnavailableError):
            await adapter.explain(explanation_input)

    assert len(calls) == 3


@pytest.mark.asyncio
async def test_timeout_is_reported_as_a_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("too slow", request=request)

    _decision, explanation_input = _decision_and_input()
    adapter, client = _adapter(handler)
    async with client:
        with pytest.raises(ProviderTimeoutError):
            await adapter.explain(explanation_input)


@pytest.mark.asyncio
async def test_malformed_json_is_rejected() -> None:
    _decision, explanation_input = _decision_and_input()
    adapter, client = _adapter(lambda request: httpx.Response(200, content=b"{not json"))
    async with client:
        with pytest.raises(ProviderMalformedJsonError):
            await adapter.explain(explanation_input)


@pytest.mark.parametrize(
    "payload",
    [
        {"choices": []},
        {"choices": [{"message": {"content": ""}}]},
        {"choices": [{"message": {}}]},
        {"result": "unexpected shape"},
    ],
)
@pytest.mark.asyncio
async def test_a_missing_answer_is_a_failure_not_an_empty_explanation(payload: dict) -> None:
    """Returning "" here would later look like a model that simply had nothing to say."""
    _decision, explanation_input = _decision_and_input()
    adapter, client = _adapter(lambda request: httpx.Response(200, json=payload))
    async with client:
        with pytest.raises(ProviderInvalidPayloadError):
            await adapter.explain(explanation_input)


@pytest.mark.asyncio
async def test_provider_error_payload_with_ok_status_is_rejected() -> None:
    _decision, explanation_input = _decision_and_input()
    adapter, client = _adapter(
        lambda request: httpx.Response(200, json={"error": {"code": "invalid_api_key"}})
    )
    async with client:
        with pytest.raises(ProviderAuthenticationError):
            await adapter.explain(explanation_input)


@pytest.mark.asyncio
async def test_disabled_provider_refuses_before_any_network_call() -> None:
    _decision, explanation_input = _decision_and_input()
    provider = create_explanation_provider(Settings(_env_file=None))

    assert isinstance(provider, DisabledExplanationProvider)
    with pytest.raises(IntegrationDisabledError):
        await provider.explain(explanation_input)


def test_enabled_provider_requires_a_key_and_a_client() -> None:
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        Settings(_env_file=None, openai_enabled=True)

    settings = Settings(_env_file=None, openai_enabled=True, openai_api_key="test-key")
    with pytest.raises(ConfigurationInvalidError):
        create_explanation_provider(settings)
