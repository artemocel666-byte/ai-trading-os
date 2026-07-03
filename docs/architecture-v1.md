# Architecture v1

AI Trading OS is a modular monolith with three Python runtime processes and one PostgreSQL database.

## Runtime Processes

- `api`: FastAPI service for health, readiness, system status, and controlled scan-state changes.
- `worker`: APScheduler asyncio process for heartbeat and foundation health checks.
- `bot`: Telegram process. It remains alive in disabled mode and only polls Telegram when enabled.

## Dependency Direction

Adapters depend on application services. Application services depend on domain contracts. Domain contracts do not depend on frameworks, databases, or external providers.

```text
API / Telegram / external adapters
                ->
Application services
                ->
Domain
```

## Database

PostgreSQL stores system state, audit logs, error events, future candles, economic events, scans, reports, signals, and paper positions. SQLAlchemy uses the async API only.

## Future Data Pipeline

Future phases will collect closed candles and scheduled economic events, build deterministic features, run independent analytical agents, apply deterministic risk and decision rules, and format Russian explanations. The foundation has contracts for these pieces but no implementation.

## Phase 2 Provider Boundary

Market-data providers return `Candle` domain models for `M15` or `H1` only. Economic-calendar
providers return `EconomicEvent` domain models. Production Twelve Data and FMP adapters use injected
`httpx.AsyncClient` instances and are selected only through factories when integrations are enabled.
Live integrations remain disabled by default. Contract tests use `httpx.MockTransport`, not real
network calls.

## Deterministic vs LLM Responsibilities

Deterministic code owns prices, scores, risk, status transitions, and acceptance or rejection. Future LLM code may explain deterministic results in Russian, summarize evidence, and describe risk. It must not change calculated values, fabricate evidence, bypass risk rules, or create a rejected signal.

## Security Boundaries

- External integrations are disabled by default.
- Secrets are never returned through API responses.
- Logs redact secret-like fields.
- State-changing API endpoints require `X-Internal-API-Key`.
- The default development internal API key is rejected outside development.
- Telegram accepts only the configured user ID and chat ID.
- Real trading execution is forbidden.

## Failure Behavior

- Configuration errors stop affected services.
- Database unavailable means readiness fails and state-changing work cannot complete.
- Disabled integrations raise explicit typed errors before external calls.
- Unsupported analysis returns explicit not-implemented behavior.
- The system must not fabricate success.

## Observability

The foundation includes API liveness/readiness, database checks, worker heartbeat, integration-enabled state, and structured error recording. Prometheus or a full observability stack can be added later without changing domain boundaries.
