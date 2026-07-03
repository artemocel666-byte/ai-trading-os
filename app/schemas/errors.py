from pydantic import BaseModel, Field


class ErrorBody(BaseModel):
    code: str
    message_ru: str
    request_id: str
    details: dict[str, object] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorBody
