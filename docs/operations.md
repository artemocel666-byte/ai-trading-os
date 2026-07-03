# Operations

## Startup

Docker startup:

```bash
docker compose up --build
```

Compose reads `.env` as an optional local runtime override. `.env.example` is only a template.
The API is bound to `127.0.0.1:8000` by default, and PostgreSQL is not exposed to the host by
the default Compose stack.

Local startup:

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:create_app --factory --reload
```

## Shutdown

Use `Ctrl+C` for foreground Compose or:

```bash
docker compose down
```

The worker and Telegram process handle shutdown signals and dispose database resources.

## Migrations

Apply migrations:

```bash
uv run alembic upgrade head
```

Create a migration:

```bash
uv run alembic revision --autogenerate -m "message"
```

## Logs

Application processes emit structured JSON logs with service, component, event, level, timestamp, request IDs where available, and redacted secret-like fields.

## Health Checks

- `GET /health` checks API liveness only.
- `GET /ready` checks database connectivity and schema access.
- `GET /api/v1/system/status` reports phase, scan state, worker heartbeat, enabled integrations, database status, and safety flags.

## Disabled Integrations

The default `.env.example` disables Telegram, OpenAI, market data, calendar, and scanning. Disabled providers raise typed errors before external calls.

## Common Failure Cases

- Missing Telegram token while Telegram is enabled: configuration validation fails.
- PostgreSQL unavailable: readiness fails and state changes cannot persist.
- Migrations not applied: readiness returns not ready.
- Wrong internal API key: state-changing API calls return `UNAUTHORIZED`.

## Safe Recovery

1. Check `docker compose ps`.
2. Inspect `docker compose logs --no-color`.
3. Confirm PostgreSQL is healthy.
4. Run `uv run alembic upgrade head`.
5. Recheck `/ready` and `/api/v1/system/status`.
