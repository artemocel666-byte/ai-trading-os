# AI Trading OS Foundation Implementation Plan

## Assumptions

- The repository is empty at the start of this task.
- The current task implements only the technical foundation for an analytical and paper-trading project.
- External integrations are disabled by default and must not make network calls unless explicitly enabled and configured.
- PostgreSQL is the only production persistence target for the foundation.
- The project uses Python 3.12, FastAPI, async SQLAlchemy, Alembic, APScheduler, python-telegram-bot, pytest, Ruff, mypy, Docker, Docker Compose, and uv.

## Safety Boundaries

- No real trading execution, broker order API, live position management, or automatic order placement will be implemented.
- Unsupported financial analysis paths will return explicit not-implemented or integration-disabled results.
- Scanning state can be toggled, but no market analysis engine is connected in this foundation phase.
- LLM-related interfaces are contracts only; no OpenAI calls are made.

## Implementation Sequence

1. Create project metadata, environment examples, Docker files, and Makefile.
2. Implement typed settings with conditional integration validation and secret redaction.
3. Implement core enums, value objects, exceptions, structured logging, and time helpers.
4. Implement async SQLAlchemy database setup, persistence models, repositories, unit of work, and Alembic migration.
5. Implement system state and health services.
6. Implement FastAPI app with liveness, readiness, system status, scanning state endpoints, request IDs, and JSON error handling.
7. Implement APScheduler worker with heartbeat and health-check jobs.
8. Implement Telegram authorization, Russian text validation, one-emoji formatting, disabled mode, and command handlers.
9. Add future provider and agent contracts without live external calls or strategy logic.
10. Add documentation, safety scripts, and meaningful unit, integration, and contract tests.
11. Run formatting, linting, typing, tests, Compose validation, Docker checks where available, migrations, API probes, and self-review.

## Risks

- Local tooling may be unavailable in the execution environment; verification will truthfully record any unavailable checks.
- Docker may be unavailable or unable to start services in this environment.
- Dependency locking requires network access or a preinstalled uv binary; if unavailable, the repository will still include uv-compatible metadata and the limitation will be recorded.

## Acceptance Criteria

- The local stack starts without external paid API keys.
- API health, readiness, and system status endpoints work.
- Worker heartbeat persists to PostgreSQL.
- Telegram disabled mode is healthy, and enabled mode uses Russian messages with exactly one leading semantic emoji.
- Scanning can be enabled and disabled without invoking strategy or market analysis.
- Database migrations create the foundation schema.
- Tests verify safety boundaries, settings, value objects, Telegram policy, system state, contracts, and API behavior.
- Documentation accurately describes the implemented foundation and its limitations.
