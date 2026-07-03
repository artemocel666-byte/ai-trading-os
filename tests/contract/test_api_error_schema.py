from app.api.error_handlers import error_content


def test_api_error_schema_contains_required_fields() -> None:
    content = error_content(
        code="NOT_IMPLEMENTED",
        message_ru="Функция ещё не реализована.",
        request_id="req-1",
        details={"database_url": "postgresql://secret"},
    )

    assert set(content) == {"error"}
    assert content["error"]["code"] == "NOT_IMPLEMENTED"
    assert content["error"]["message_ru"] == "Функция ещё не реализована."
    assert content["error"]["request_id"] == "req-1"
    assert content["error"]["details"]["database_url"] == "***REDACTED***"
