from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str
    service: str


class ReadinessResponse(BaseModel):
    status: str
    service: str
    database: str
    schema_status: str = Field(alias="schema")
    configuration: str

    model_config = ConfigDict(populate_by_name=True)


class SystemStatusResponse(BaseModel):
    app_environment: str
    current_utc_time: str
    user_timezone: str
    scan_enabled: bool
    worker_heartbeat: str | None
    last_successful_market_fetch: str | None
    last_successful_calendar_fetch: str | None
    last_error: dict[str, object] | None
    enabled_integrations: dict[str, bool]
    database_status: str
    project_phase: str
    strategy_implementation_status: str
    trading_strategy_implemented: bool
    real_trading_enabled: bool


class ScanningStateResponse(BaseModel):
    scan_enabled: bool
    message_ru: str
