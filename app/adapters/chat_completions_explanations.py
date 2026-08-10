"""Chat-completions adapter for Russian explanations of an already-decided report.

Disabled by default: the factory returns the disabled provider unless `EXPLANATION_PROVIDER` names
one, and no service, route, or job may call this — only `/explain`.

**One transport, not one vendor.** OpenAI, LM Studio, Ollama, llama.cpp and vLLM all serve
`/v1/chat/completions` with the same request and response shape, so Phase 8D parameterised this
module rather than copying two hundred lines of retry and error handling beside it. What differs
between a remote and a local model is an address, whether an API key is sent, and how long an answer
takes — arguments, not algorithms.

That keeps the property Phase 8B actually cared about: **exactly one module in the project can reach
a model**, and a safety test says so. A second adapter would have doubled the surface that has to
stay honest.

Three properties matter more than the HTTP details:

* **The model cannot reach anything.** Its whole input is the Phase 8A `ExplanationInput` — our own
  rule ids, statuses, and numbers, serialized. Nothing a stranger wrote goes into the prompt, so
  there is no injection surface here to defend.
* **Unvalidated text cannot escape.** `explain_validated` runs the Phase 8A validator and returns an
  outcome that carries text only when the answer was accepted. A caller cannot skip the check by
  forgetting to call it, because the rejected text is not in the result at all.
* **A local endpoint is sent no credential at all.** `api_key` is optional, and when it is absent
  the `Authorization` header is not built — rather than sent empty, or sent with whatever key
  happened to be configured for somebody else's service.
"""

import asyncio
import json
from datetime import datetime
from typing import Any

import httpx

from app.core.exceptions import (
    ProviderAuthenticationError,
    ProviderInvalidPayloadError,
    ProviderMalformedJsonError,
    ProviderPlanRestrictedError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ProviderUnsupportedRequestError,
)
from app.domain.entities.explanation import ExplanationInput, ExplanationOutcome
from app.domain.explanation_contract import validate_explanation_text

OPENAI_PROVIDER_NAME = "openai"
LOCAL_PROVIDER_NAME = "local_llm"

SYSTEM_PROMPT_RU = (
    "Ты объясняешь по-русски уже готовый детерминированный отчёт анализа рынка. "
    "Твоя задача — описать, что показали правила, и ничего больше.\n"
    "Строгие ограничения:\n"
    "1. Используй только те числа, которые есть во входных данных. Не вычисляй новых.\n"  # noqa: RUF001
    "2. Не давай торговых указаний и оценок направления. Никаких покупок, продаж, "  # noqa: RUF001
    "уровней входа, целей и защитных уровней.\n"
    "3. Не меняй статус решения и не спорь с ним.\n"  # noqa: RUF001
    "4. Не добавляй эмодзи.\n"  # noqa: RUF001
    "5. Пиши коротко: три-четыре предложения обычным русским языком.\n"
    "Если данных мало, так и скажи — это нормальный ответ."
)


class ChatCompletionsExplanationAdapter:
    def __init__(
        self,
        *,
        client: httpx.AsyncClient,
        provider_name: str,
        api_key: str | None,
        base_url: str,
        model: str,
        timeout: httpx.Timeout,
        retry_count: int,
        retry_backoff_seconds: float,
        max_output_tokens: int,
    ) -> None:
        self._client = client
        self._provider_name = provider_name
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout
        self._retry_count = retry_count
        self._retry_backoff_seconds = retry_backoff_seconds
        self._max_output_tokens = max_output_tokens

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def provider_name(self) -> str:
        return self._provider_name

    def build_request_headers(self) -> dict[str, str]:
        """The exact headers sent. Exposed so a test can assert what a local endpoint receives.

        No key means no header. Sending an empty `Authorization` would be indistinguishable in a
        server log from a broken credential, and sending a real one to a local process would hand a
        paid key to whatever is listening on that port.
        """
        headers = {"Content-Type": "application/json"}
        if self._api_key is not None:
            # The key travels in a header, never a query parameter: URLs end up in logs and error
            # messages, and the redaction rules cannot save what a provider has already recorded.
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    async def explain(self, explanation_input: ExplanationInput) -> str:
        """Ask the model and return its raw answer.

        Present because the provider Protocol defines it. Prefer `explain_validated`: raw model
        text has not been checked and must never reach a user.
        """
        payload = await self._request_completion(explanation_input)
        return _message_content(payload, self._provider_name)

    async def explain_validated(
        self,
        explanation_input: ExplanationInput,
        checked_at: datetime,
    ) -> ExplanationOutcome:
        text = await self.explain(explanation_input)
        validation = validate_explanation_text(text, explanation_input, checked_at)
        return ExplanationOutcome(
            model_name=self._model,
            text=text.strip() if validation.accepted else None,
            validation=validation,
        )

    def build_request_body(self, explanation_input: ExplanationInput) -> dict[str, Any]:
        """The exact body sent to the provider.

        Exposed so tests can assert that nothing beyond the contract leaves the process.
        """
        return {
            "model": self._model,
            "temperature": 0,
            "max_tokens": self._max_output_tokens,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT_RU},
                {"role": "user", "content": explanation_input.deterministic_json()},
            ],
        }

    async def _request_completion(self, explanation_input: ExplanationInput) -> Any:
        url = f"{self._base_url}/v1/chat/completions"
        response = await self._send_with_retries(
            url,
            body=self.build_request_body(explanation_input),
            headers=self.build_request_headers(),
        )
        try:
            payload = json.loads(response.content)
        except ValueError as exc:
            raise ProviderMalformedJsonError(self._provider_name) from exc
        _raise_for_provider_payload_error(payload, self._provider_name)
        return payload

    async def _send_with_retries(
        self,
        url: str,
        *,
        body: dict[str, Any],
        headers: dict[str, str],
    ) -> httpx.Response:
        attempts = self._retry_count + 1
        last_timeout: httpx.TimeoutException | None = None
        last_transport_error: httpx.TransportError | None = None
        last_5xx_status: int | None = None
        for attempt in range(attempts):
            try:
                response = await self._client.post(
                    url,
                    json=body,
                    headers=headers,
                    timeout=self._timeout,
                )
            except httpx.TimeoutException as exc:
                last_timeout = exc
                if attempt < attempts - 1:
                    await self._sleep_before_retry()
                    continue
                break
            except httpx.TransportError as exc:
                last_transport_error = exc
                if attempt < attempts - 1:
                    await self._sleep_before_retry()
                    continue
                break
            if response.status_code in (401, 403):
                raise ProviderAuthenticationError(
                    self._provider_name, details={"status_code": response.status_code}
                )
            if response.status_code == 402:
                raise ProviderPlanRestrictedError(
                    self._provider_name, details={"status_code": response.status_code}
                )
            if response.status_code == 429:
                raise ProviderRateLimitError(
                    self._provider_name, details={"status_code": response.status_code}
                )
            if response.status_code >= 500:
                last_5xx_status = response.status_code
                if attempt < attempts - 1:
                    await self._sleep_before_retry()
                    continue
                break
            if response.status_code >= 400:
                raise ProviderUnsupportedRequestError(
                    self._provider_name, details={"status_code": response.status_code}
                )
            return response
        if last_timeout is not None:
            raise ProviderTimeoutError(self._provider_name) from None
        if last_transport_error is not None:
            raise ProviderUnavailableError(self._provider_name) from None
        raise ProviderUnavailableError(
            self._provider_name, details={"status_code": last_5xx_status}
        )

    async def _sleep_before_retry(self) -> None:
        if self._retry_backoff_seconds > 0:
            await asyncio.sleep(self._retry_backoff_seconds)


def _raise_for_provider_payload_error(payload: Any, provider_name: str) -> None:
    if isinstance(payload, dict) and payload.get("error"):
        error = payload["error"]
        code = error.get("code") if isinstance(error, dict) else None
        if code in ("invalid_api_key", "insufficient_quota"):
            raise ProviderAuthenticationError(provider_name, details={"provider_code": str(code)})
        raise ProviderInvalidPayloadError(provider_name, details={"provider_code": str(code)})


def _message_content(payload: Any, provider_name: str) -> str:
    """Pull the answer out, refusing anything that is not plainly there.

    An empty or missing message is a provider failure, not an empty explanation: returning "" would
    later look like a model that had nothing to say.
    """
    if not isinstance(payload, dict):
        raise ProviderInvalidPayloadError(provider_name, details={"reason": "payload_not_object"})
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ProviderInvalidPayloadError(provider_name, details={"reason": "no_choices"})
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise ProviderInvalidPayloadError(provider_name, details={"reason": "empty_content"})
    return content


def build_completion_timeout(read_timeout_seconds: float) -> httpx.Timeout:
    """A longer read timeout than the market-data providers need.

    A completion takes seconds, not milliseconds; the 10 second default would turn ordinary latency
    into a stream of timeouts. A model running locally on a CPU is slower again, which is why the
    caller passes the explanation budget here rather than the generic provider timeout.
    """
    return httpx.Timeout(
        connect=5.0,
        read=max(read_timeout_seconds, 30.0),
        write=5.0,
        pool=5.0,
    )
