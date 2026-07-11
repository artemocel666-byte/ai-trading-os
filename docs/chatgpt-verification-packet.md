# AI Trading OS - Phase 3A Verification Packet

Generated at: `2026-07-11T15:21:29Z`

## Scope

This packet documents the current uncommitted Phase 3A data-quality foundation work. Phase 3A is limited to deterministic closed-candle/economic-event storage, duplicate-safe upserts, read/query repositories, data-quality feature snapshots, and historical replay utilities.

Phase 3B was not started. No strategy, signals, AI agents, OpenAI calls, broker APIs, paper trading, order execution, or real trading were added or activated.

At packet generation time, Phase 3A is still uncommitted. Integration tests are now repeatable
against the same PostgreSQL test database without requiring manual `dropdb` or database cleanup
between runs.

## Final Phase 3A Verification Results

These are the latest successful Phase 3A verification results and supersede earlier environment
fallback notes.

- `uv run ruff format --check .`: `88 files already formatted`
- `uv run ruff check .`: `All checks passed!`
- `uv run mypy app`: `Success: no issues found in 63 source files`
- `uv run pytest`: `145 passed, 5 skipped, 1 warning`
- `uv run python scripts/security_check.py`: exit code `0`
- Docker integration tests were run twice against the same `ai_trading_os_test` PostgreSQL database
  without cleaning or dropping the database between runs; both runs passed with `5 passed, 1 warning`.
- `docker compose build` succeeded.
- `docker compose run --rm migrate alembic current` returned
  `0002_phase2_data_constraints (head)`.
- `docker compose run --rm migrate alembic check` returned
  `No new upgrade operations detected.`
- The test database migration to head succeeded.

Phase 3B was not started. No strategy, signals, AI agents, OpenAI calls, broker APIs, paper trading,
order execution, or real trading were added.

## Git Metadata

- Branch: `main`

- Current commit hash: `9d687096aeb5ab0b6586109b7e51a3b011d5aa90`

### `git status --short`

```text
 M AGENTS.md
 M PLANS.md
 M README.md
 M app/core/constants.py
 M app/domain/entities/__init__.py
 M app/domain/interfaces/repositories.py
 M app/domain/interfaces/unit_of_work.py
 M app/persistence/repositories/__init__.py
 M app/persistence/repositories/foundation.py
 M app/persistence/unit_of_work.py
 M docs/chatgpt-verification-packet.md
 M tests/integration/test_database_and_api.py
 M tests/unit/test_unit_of_work_lifecycle.py
?? app/domain/entities/data_quality.py
?? app/domain/replay.py
?? tests/unit/test_data_quality_foundation.py
```

## Repeatability Fix Addendum

Updated at: `2026-07-11T15:15:49Z`

### Scope

This addendum documents the Phase 3A integration test repeatability correction. The production
repository upsert logic was not changed. The repeatability issue was isolated to stale integration
test rows in `ai_trading_os_test` from a previous run.

The fix keeps duplicate-safe upsert behavior intact: the test still verifies first insert and then
update for the same candle and economic event identity. Test isolation now deletes only rows owned
by the dedicated integration fixture provider before and after the repository integration test.

Phase 3B was not started. No strategy, signals, AI agents, OpenAI calls, broker APIs, paper trading,
order execution, or real trading were added or activated.

### Files Updated By This Addendum

- `tests/integration/test_database_and_api.py`
- `docs/chatgpt-verification-packet.md`

### Current Integration Test Contents

```python
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.domain.entities import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.value_objects import CurrencyPair
from app.main import create_app
from app.persistence.database import create_engine, create_session_factory
from app.persistence.models import CandleModel, EconomicEventModel
from app.persistence.session import build_uow_factory
from app.services.system_state_service import SystemStateService

_MARKET_CALENDAR_TEST_PROVIDER = "integration-phase3a-repository-test"


async def _delete_market_calendar_test_rows(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        await session.execute(
            delete(CandleModel).where(CandleModel.provider == _MARKET_CALENDAR_TEST_PROVIDER)
        )
        await session.execute(
            delete(EconomicEventModel).where(
                EconomicEventModel.provider == _MARKET_CALENDAR_TEST_PROVIDER
            )
        )
        await session.commit()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_system_state_persists_in_postgresql(postgres_database_url: str) -> None:
    engine = create_engine(postgres_database_url)
    try:
        service = SystemStateService(build_uow_factory(create_session_factory(engine)))

        await service.enable_scanning(actor="integration-test")
        status = await service.get_full_status()

        assert status["scan_enabled"] is True
    finally:
        await engine.dispose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_unit_of_work_rolls_back_uncommitted_failure(postgres_database_url: str) -> None:
    engine = create_engine(postgres_database_url)
    key = f"rollback_{uuid4().hex}"
    try:
        uow_factory = build_uow_factory(create_session_factory(engine))

        async def fail_inside_unit_of_work() -> None:
            async with uow_factory() as uow:
                await uow.system_state.set(key, {"value": "should_not_persist"})
                raise RuntimeError("force rollback")

        with pytest.raises(RuntimeError):
            await fail_inside_unit_of_work()

        async with uow_factory() as uow:
            value = await uow.system_state.get(key)

        assert value is None
    finally:
        await engine.dispose()


@pytest.mark.integration
def test_api_health_readiness_status_and_scan_state(postgres_database_url: str) -> None:
    settings = Settings(_env_file=None, database_url=postgres_database_url)
    app = create_app(settings)

    with TestClient(app) as client:
        health = client.get("/health")
        ready = client.get("/ready")
        status = client.get("/api/v1/system/status")
        start = client.post(
            "/api/v1/system/scanning/start",
            headers={"X-Internal-API-Key": settings.internal_api_key.get_secret_value()},
        )
        stop = client.post(
            "/api/v1/system/scanning/stop",
            headers={"X-Internal-API-Key": settings.internal_api_key.get_secret_value()},
        )

    assert health.status_code == 200
    assert health.json() == {"status": "alive", "service": "api"}
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
    assert status.status_code == 200
    assert status.json()["project_phase"] == "phase_3a_data_quality_foundation"
    assert status.json()["trading_strategy_implemented"] is False
    assert status.json()["real_trading_enabled"] is False
    assert start.status_code == 200
    assert start.json()["scan_enabled"] is True
    assert stop.status_code == 200
    assert stop.json()["scan_enabled"] is False


@pytest.mark.integration
def test_state_changing_endpoint_requires_internal_api_key(postgres_database_url: str) -> None:
    settings = Settings(_env_file=None, database_url=postgres_database_url)
    app = create_app(settings)

    with TestClient(app) as client:
        response = client.post("/api/v1/system/scanning/start")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_market_and_calendar_repositories_upsert_and_query(
    postgres_database_url: str,
) -> None:
    engine = create_engine(postgres_database_url)
    session_factory = create_session_factory(engine)
    try:
        await _delete_market_calendar_test_rows(session_factory)
        uow_factory = build_uow_factory(session_factory)
        pair = CurrencyPair(value="EURUSD")
        candle = Candle(
            provider=_MARKET_CALENDAR_TEST_PROVIDER,
            pair=pair,
            timeframe=Timeframe.M15,
            open_time=datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
            close_time=datetime(2026, 7, 8, 8, 15, tzinfo=UTC),
            open=Decimal("1.1000"),
            high=Decimal("1.1050"),
            low=Decimal("1.0950"),
            close=Decimal("1.1020"),
            volume=Decimal("100"),
            is_closed=True,
        )
        updated_candle = candle.model_copy(update={"close": Decimal("1.1030")})
        event = EconomicEvent(
            provider=_MARKET_CALENDAR_TEST_PROVIDER,
            provider_event_id="phase3a-cpi-event",
            title="Consumer Price Index",
            currency="EUR",
            country="Eurozone",
            impact=EconomicImpact.HIGH,
            scheduled_at=datetime(2026, 7, 8, 8, 5, tzinfo=UTC),
            actual=Decimal("2.2"),
            forecast=Decimal("2.1"),
            previous=Decimal("2.0"),
            fetched_at=datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
        )
        updated_event = event.model_copy(update={"actual": Decimal("2.3")})

        async with uow_factory() as uow:
            candle_insert = await uow.candles.upsert_many([candle])
            candle_update = await uow.candles.upsert_many([updated_candle])
            event_insert = await uow.economic_events.upsert_many([event])
            event_update = await uow.economic_events.upsert_many([updated_event])
            await uow.commit()

        async with uow_factory() as uow:
            candles = await uow.candles.list_range(
                pair=pair,
                timeframe=Timeframe.M15,
                start_at=datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
                end_at=datetime(2026, 7, 8, 8, 15, tzinfo=UTC),
                provider=_MARKET_CALENDAR_TEST_PROVIDER,
            )
            events = await uow.economic_events.list_window(
                start_at=datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
                end_at=datetime(2026, 7, 8, 8, 15, tzinfo=UTC),
                currencies=["EUR"],
                provider=_MARKET_CALENDAR_TEST_PROVIDER,
            )

        assert candle_insert.inserted == 1
        assert candle_update.updated == 1
        assert event_insert.inserted == 1
        assert event_update.updated == 1
        assert [stored.close for stored in candles] == [Decimal("1.1030000000")]
        assert [stored.actual for stored in events] == [Decimal("2.300000")]
    finally:
        await _delete_market_calendar_test_rows(session_factory)
        await engine.dispose()
```

### Final Host Verification Commands

The final requested host `uv` commands completed successfully.

#### `uv run ruff format --check .`

Exit code: `0`

```text
88 files already formatted
```

#### `uv run ruff check .`

Exit code: `0`

```text
All checks passed!
```

#### `uv run mypy app`

Exit code: `0`

```text
Success: no issues found in 63 source files
```

#### `uv run pytest`

Exit code: `0`

```text
145 passed, 5 skipped, 1 warning
```

#### `uv run python scripts/security_check.py`

Exit code: `0`

```text
```

### Earlier Host Verification Fallback From `.venv`

These earlier fallback checks are retained for audit history. The final `uv run ...` results above
are the authoritative latest host verification results.

#### `.venv/bin/ruff format --check .`

Exit code: `0`

```text
88 files already formatted
```

#### `.venv/bin/ruff check .`

Exit code: `0`

```text
All checks passed!
```

#### `.venv/bin/mypy app`

Exit code: `0`

```text
Success: no issues found in 63 source files
```

#### `.venv/bin/pytest`

Exit code: `0`

```text
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/artem.otsel/Documents/ai-trading-os
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.14.1, asyncio-0.26.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 150 items

tests/contract/test_agent_contracts.py ......                            [  4%]
tests/contract/test_api_error_schema.py .                                [  4%]
tests/contract/test_architecture_boundaries.py ..                        [  6%]
tests/contract/test_provider_contracts.py .............................. [ 26%]
...............................                                          [ 46%]
tests/contract/test_safety_boundaries.py .........                       [ 52%]
tests/integration/test_database_and_api.py sssss                         [ 56%]
tests/unit/test_data_quality_foundation.py ...                           [ 58%]
tests/unit/test_domain_market_models.py ..................               [ 70%]
tests/unit/test_errors_and_redaction.py .......                          [ 74%]
tests/unit/test_internal_api_key.py ....                                 [ 77%]
tests/unit/test_settings.py .........                                    [ 83%]
tests/unit/test_system_state_service.py .....                            [ 86%]
tests/unit/test_telegram_commands.py ..                                  [ 88%]
tests/unit/test_telegram_policy.py .....                                 [ 91%]
tests/unit/test_time.py ...                                              [ 93%]
tests/unit/test_unit_of_work_lifecycle.py ......                         [ 97%]
tests/unit/test_value_objects_and_enums.py ....                          [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /Users/artem.otsel/Documents/ai-trading-os/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================== 145 passed, 5 skipped, 1 warning in 0.73s ===================
```

#### `.venv/bin/python scripts/security_check.py`

Exit code: `0`

```text
```

### Docker Verification Commands

#### `docker compose build`

Exit code: `0`

```text
 Image ai-trading-os-worker Building 
 Image ai-trading-os-bot Building 
 Image ai-trading-os-migrate Building 
 Image ai-trading-os-api Building 
#1 [internal] load local bake definitions
#1 reading from stdin 1.91kB done
#1 DONE 0.0s

#2 [bot internal] load build definition from Dockerfile
#2 transferring dockerfile: 411B done
#2 DONE 0.0s

#3 [bot internal] load metadata for ghcr.io/astral-sh/uv:python3.12-bookworm-slim
#3 DONE 1.1s

#4 [migrate internal] load .dockerignore
#4 transferring context: 143B done
#4 DONE 0.0s

#5 [api 1/5] FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58
#5 resolve ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58 0.0s done
#5 DONE 0.0s

#6 [bot internal] load build context
#6 transferring context: 44.51kB 0.0s done
#6 DONE 0.0s

#7 [worker 2/5] WORKDIR /app
#7 CACHED

#8 [worker 3/5] COPY pyproject.toml uv.lock* ./
#8 CACHED

#9 [worker 4/5] RUN uv sync --frozen --no-dev
#9 CACHED

#10 [bot 5/5] COPY . .
#10 DONE 0.0s

#11 [migrate] exporting to image
#11 exporting layers 0.0s done
#11 ...

#12 [bot] exporting to image
#12 exporting layers 0.0s done
#12 exporting manifest sha256:43aba66a9b2a447546bcf5dbecaba2095f268dfb9f33bfd35b727e4890d2bfa7 done
#12 exporting config sha256:687bec391bf8458b81d21001ff0e14aba7d3cee2da9afef0c0069968db2c147a done
#12 exporting attestation manifest sha256:02c26903953681046f55824474aa94d5f03a6b44c4a227662af0a190273eaa83 0.0s done
#12 exporting manifest list sha256:39e5764e31dbe94296a37a7ca9864a2810650b7f2eeaa759484de4aee64b472a done
#12 naming to docker.io/library/ai-trading-os-bot:latest done
#12 unpacking to docker.io/library/ai-trading-os-bot:latest 0.0s done
#12 DONE 0.1s

#11 [migrate] exporting to image
#11 exporting manifest sha256:a58c88bd001391cf776061538fb981b2337cdacc6e6a62d29dd7290aa5faa1ce done
#11 exporting config sha256:eae9ea615561564404e5f685694e57fa00760bfd9ed4caa886dbea39dfacddc0 done
#11 exporting attestation manifest sha256:9061b9afafd917c94b94b79ad8e4428989a2735dd47c1b9243fc9a8a7621d710 0.0s done
#11 exporting manifest list sha256:1805d71b4cf41f659f9d299b550bb65ff42f724086d199886d30913d28d77755 done
#11 naming to docker.io/library/ai-trading-os-migrate:latest done
#11 unpacking to docker.io/library/ai-trading-os-migrate:latest 0.0s done
#11 DONE 0.1s

#13 [worker] exporting to image
#13 exporting layers 0.0s done
#13 exporting manifest sha256:f4d92ad8dae11637a807b3bba8d5f9c1418efd861fdee9c8695af80cb350c114 done
#13 exporting config sha256:e2e4a34afcce9c1409a3ea26cb2b36ea58dbb2a2585dcefce4792610637d1527 done
#13 exporting attestation manifest sha256:a4be337dd09c4d6ed7c35590d27295320ba7e201d589d8758a604f08489c968b 0.0s done
#13 exporting manifest list sha256:2aa1c246eaff1c9ab9f2afc16b9d9e32d38d5a72a2649aab755d405b18ec5a07 done
#13 naming to docker.io/library/ai-trading-os-worker:latest done
#13 unpacking to docker.io/library/ai-trading-os-worker:latest 0.0s done
#13 DONE 0.1s

#14 [api] exporting to image
#14 exporting layers 0.0s done
#14 exporting manifest sha256:e02898c010daf10caf59d1e254ab2f58e689729998bb1e2036651aa74dfeb8fb done
#14 exporting config sha256:70eed906624a9de6558aaaa9b5f47182f76d7e05ef863c25096d3c6eab8544be done
#14 exporting attestation manifest sha256:52536710947363746606dcb2d6fd52a0aaabf703f24b592df27fe638fbf508c7 0.0s done
#14 exporting manifest list sha256:933c5a6591d8ad4c63d3311186c3c44fab8db81c757061271d5f178cd105899f done
#14 naming to docker.io/library/ai-trading-os-api:latest done
#14 unpacking to docker.io/library/ai-trading-os-api:latest 0.0s done
#14 DONE 0.1s

#15 [migrate] resolving provenance for metadata file
#15 DONE 0.0s

#16 [worker] resolving provenance for metadata file
#16 DONE 0.0s

#17 [api] resolving provenance for metadata file
#17 DONE 0.0s

#18 [bot] resolving provenance for metadata file
#18 DONE 0.0s
 Image ai-trading-os-api Built 
 Image ai-trading-os-bot Built 
 Image ai-trading-os-migrate Built 
 Image ai-trading-os-worker Built 
```

#### `docker compose up -d postgres`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
```

#### `docker compose run --rm migrate alembic current`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-28cc42cb064d Creating 
 Container ai-trading-os-migrate-run-28cc42cb064d Created 
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
0002_phase2_data_constraints (head)
```

#### `docker compose run --rm migrate alembic check`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-9fbfe34797b3 Creating 
 Container ai-trading-os-migrate-run-9fbfe34797b3 Created 
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.schemas
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.tables
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.types
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.constraints
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.defaults
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.comments
No new upgrade operations detected.
```

#### `docker compose run --rm -e DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate alembic upgrade head`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-da2eba432463 Creating 
 Container ai-trading-os-migrate-run-da2eba432463 Created 
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

#### First repeated integration run

Command:

```bash
docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py
```

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-4d129c8ff4af Creating 
 Container ai-trading-os-migrate-run-4d129c8ff4af Created 
Downloading ruff (10.5MiB)
Downloading pygments (1.2MiB)
Downloading mypy (13.1MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 88ms
Bytecode compiled 1963 files in 450ms
============================= test session starts ==============================
platform linux -- Python 3.12.12, pytest-8.4.2, pluggy-1.6.0
rootdir: /app
configfile: pyproject.toml
plugins: anyio-4.14.1, asyncio-0.26.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 5 items

tests/integration/test_database_and_api.py .....                         [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /app/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
========================= 5 passed, 1 warning in 0.32s =========================
```

#### Second repeated integration run

Command:

```bash
docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py
```

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-6ea94eb1656d Creating 
 Container ai-trading-os-migrate-run-6ea94eb1656d Created 
Downloading pygments (1.2MiB)
Downloading mypy (13.1MiB)
Downloading ruff (10.5MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 37ms
Bytecode compiled 1963 files in 429ms
============================= test session starts ==============================
platform linux -- Python 3.12.12, pytest-8.4.2, pluggy-1.6.0
rootdir: /app
configfile: pyproject.toml
plugins: anyio-4.14.1, asyncio-0.26.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 5 items

tests/integration/test_database_and_api.py .....                         [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /app/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
========================= 5 passed, 1 warning in 0.29s =========================
```

### Repeatability Result

Both Docker integration runs passed against the same `ai_trading_os_test` database without manual
database dropping between runs.

### `git diff --stat`

```text
 AGENTS.md                                  |    7 +-
 PLANS.md                                   |   15 +-
 README.md                                  |   11 +-
 app/core/constants.py                      |    2 +-
 app/domain/entities/__init__.py            |   23 +-
 app/domain/interfaces/repositories.py      |   36 +
 app/domain/interfaces/unit_of_work.py      |   12 +
 app/persistence/repositories/__init__.py   |    4 +
 app/persistence/repositories/foundation.py |  199 +-
 app/persistence/unit_of_work.py            |   22 +
 docs/chatgpt-verification-packet.md        | 4102 +++++++++++++++-------------
 tests/integration/test_database_and_api.py |   76 +-
 tests/unit/test_unit_of_work_lifecycle.py  |    6 +
 13 files changed, 2584 insertions(+), 1931 deletions(-)
```

### `git log --oneline -3`

```text
9d68709 Document Phase 2 runtime verification
0848243 Complete Phase 2 data adapters
```

## Created Files

- `app/domain/entities/data_quality.py`

- `app/domain/replay.py`

- `tests/unit/test_data_quality_foundation.py`


## Modified Files

- `AGENTS.md`

- `PLANS.md`

- `README.md`

- `app/core/constants.py`

- `app/domain/entities/__init__.py`

- `app/domain/interfaces/repositories.py`

- `app/domain/interfaces/unit_of_work.py`

- `app/persistence/repositories/__init__.py`

- `app/persistence/repositories/foundation.py`

- `app/persistence/unit_of_work.py`

- `tests/integration/test_database_and_api.py`

- `tests/unit/test_unit_of_work_lifecycle.py`

- `docs/chatgpt-verification-packet.md`


## Verification Command Outputs

This section reflects the latest successful Phase 3A verification results. Earlier environment
fallback notes are superseded by these final outputs.

### `uv run ruff format --check .`

Exit code: `0`

```text
88 files already formatted
```

### `uv run ruff check .`

Exit code: `0`

```text
All checks passed!
```

### `uv run mypy app`

Exit code: `0`

```text
Success: no issues found in 63 source files
```

### `uv run pytest`

Exit code: `0`

```text
145 passed, 5 skipped, 1 warning
```

### `uv run python scripts/security_check.py`

Exit code: `0`

```text
```

### Checks Not Repeated In The Final Update

`uv lock --check` and `uv sync` were not part of the final repeatability-update verification
request. Docker Alembic migration verification below remains the authoritative database migration
verification for this packet.

### `docker compose config`

Exit code: `0`

```text
name: ai-trading-os
services:
  api:
    build:
      context: /Users/artem.otsel/Documents/ai-trading-os
      dockerfile: Dockerfile
    command:
      - uvicorn
      - app.main:create_app
      - --factory
      - --host
      - 0.0.0.0
      - --port
      - "8000"
    depends_on:
      migrate:
        condition: service_completed_successfully
        required: true
      postgres:
        condition: service_healthy
        required: true
    environment:
      APP_ENV: development
      APP_NAME: AI Trading OS
      APP_TIMEZONE: Europe/Stockholm
      CALENDAR_ENABLED: "false"
      DATABASE_URL: postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os
      FMP_API_KEY: ""
      FMP_BASE_URL: https://financialmodelingprep.com
      INTERNAL_API_KEY: development-internal-key-change-me
      LOG_LEVEL: INFO
      MARKET_DATA_ENABLED: "false"
      MAX_CONSECUTIVE_LOSSES: "3"
      MAX_DAILY_LOSS_PERCENT: "1.5"
      MAX_OPEN_RISK_PERCENT: "1.0"
      MAX_WEEKLY_LOSS_PERCENT: "4.0"
      OPENAI_API_KEY: ""
      OPENAI_ENABLED: "false"
      OPENAI_MODEL: gpt-4.1
      PAPER_ACCOUNT_BALANCE: "10000"
      PAPER_ACCOUNT_CURRENCY: EUR
      PAPER_RISK_PERCENT: "0.5"
      PROVIDER_CONNECT_TIMEOUT_SECONDS: "5"
      PROVIDER_MAX_REQUEST_RANGE_DAYS: "31"
      PROVIDER_POOL_TIMEOUT_SECONDS: "5"
      PROVIDER_READ_TIMEOUT_SECONDS: "10"
      PROVIDER_RETRY_BACKOFF_SECONDS: "0.1"
      PROVIDER_RETRY_COUNT: "2"
      PROVIDER_WRITE_TIMEOUT_SECONDS: "5"
      REQUIRE_INTEGRATION_TESTS: "false"
      SCAN_ENABLED: "false"
      SERVICE_NAME: api
      SETUP_SCORE_THRESHOLD: "85"
      SIGNAL_VALID_MINUTES: "30"
      STORAGE_TIMEZONE: UTC
      TELEGRAM_ALLOWED_CHAT_ID: ""
      TELEGRAM_ALLOWED_USER_ID: ""
      TELEGRAM_BOT_TOKEN: ""
      TELEGRAM_ENABLED: "false"
      TEST_DATABASE_URL: postgresql+asyncpg://ai_trading_os:ai_trading_os@localhost:5432/ai_trading_os_test
      TWELVE_DATA_API_KEY: ""
      TWELVE_DATA_BASE_URL: https://api.twelvedata.com
    healthcheck:
      test:
        - CMD
        - python
        - -c
        - import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)
      timeout: 5s
      interval: 10s
      retries: 12
    networks:
      default: null
    ports:
      - mode: ingress
        host_ip: 127.0.0.1
        target: 8000
        published: "8000"
        protocol: tcp
  bot:
    build:
      context: /Users/artem.otsel/Documents/ai-trading-os
      dockerfile: Dockerfile
    command:
      - python
      - -m
      - app.telegram.bot
    depends_on:
      migrate:
        condition: service_completed_successfully
        required: true
      postgres:
        condition: service_healthy
        required: true
    environment:
      APP_ENV: development
      APP_NAME: AI Trading OS
      APP_TIMEZONE: Europe/Stockholm
      CALENDAR_ENABLED: "false"
      DATABASE_URL: postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os
      FMP_API_KEY: ""
      FMP_BASE_URL: https://financialmodelingprep.com
      INTERNAL_API_KEY: development-internal-key-change-me
      LOG_LEVEL: INFO
      MARKET_DATA_ENABLED: "false"
      MAX_CONSECUTIVE_LOSSES: "3"
      MAX_DAILY_LOSS_PERCENT: "1.5"
      MAX_OPEN_RISK_PERCENT: "1.0"
      MAX_WEEKLY_LOSS_PERCENT: "4.0"
      OPENAI_API_KEY: ""
      OPENAI_ENABLED: "false"
      OPENAI_MODEL: gpt-4.1
      PAPER_ACCOUNT_BALANCE: "10000"
      PAPER_ACCOUNT_CURRENCY: EUR
      PAPER_RISK_PERCENT: "0.5"
      PROVIDER_CONNECT_TIMEOUT_SECONDS: "5"
      PROVIDER_MAX_REQUEST_RANGE_DAYS: "31"
      PROVIDER_POOL_TIMEOUT_SECONDS: "5"
      PROVIDER_READ_TIMEOUT_SECONDS: "10"
      PROVIDER_RETRY_BACKOFF_SECONDS: "0.1"
      PROVIDER_RETRY_COUNT: "2"
      PROVIDER_WRITE_TIMEOUT_SECONDS: "5"
      REQUIRE_INTEGRATION_TESTS: "false"
      SCAN_ENABLED: "false"
      SERVICE_NAME: bot
      SETUP_SCORE_THRESHOLD: "85"
      SIGNAL_VALID_MINUTES: "30"
      STORAGE_TIMEZONE: UTC
      TELEGRAM_ALLOWED_CHAT_ID: ""
      TELEGRAM_ALLOWED_USER_ID: ""
      TELEGRAM_BOT_TOKEN: ""
      TELEGRAM_ENABLED: "false"
      TEST_DATABASE_URL: postgresql+asyncpg://ai_trading_os:ai_trading_os@localhost:5432/ai_trading_os_test
      TWELVE_DATA_API_KEY: ""
      TWELVE_DATA_BASE_URL: https://api.twelvedata.com
    healthcheck:
      test:
        - CMD
        - python
        - scripts/process_health.py
        - app.telegram.bot
      timeout: 5s
      interval: 30s
      retries: 3
    networks:
      default: null
  migrate:
    build:
      context: /Users/artem.otsel/Documents/ai-trading-os
      dockerfile: Dockerfile
    command:
      - alembic
      - upgrade
      - head
    depends_on:
      postgres:
        condition: service_healthy
        required: true
    environment:
      APP_ENV: development
      APP_NAME: AI Trading OS
      APP_TIMEZONE: Europe/Stockholm
      CALENDAR_ENABLED: "false"
      DATABASE_URL: postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os
      FMP_API_KEY: ""
      FMP_BASE_URL: https://financialmodelingprep.com
      INTERNAL_API_KEY: development-internal-key-change-me
      LOG_LEVEL: INFO
      MARKET_DATA_ENABLED: "false"
      MAX_CONSECUTIVE_LOSSES: "3"
      MAX_DAILY_LOSS_PERCENT: "1.5"
      MAX_OPEN_RISK_PERCENT: "1.0"
      MAX_WEEKLY_LOSS_PERCENT: "4.0"
      OPENAI_API_KEY: ""
      OPENAI_ENABLED: "false"
      OPENAI_MODEL: gpt-4.1
      PAPER_ACCOUNT_BALANCE: "10000"
      PAPER_ACCOUNT_CURRENCY: EUR
      PAPER_RISK_PERCENT: "0.5"
      PROVIDER_CONNECT_TIMEOUT_SECONDS: "5"
      PROVIDER_MAX_REQUEST_RANGE_DAYS: "31"
      PROVIDER_POOL_TIMEOUT_SECONDS: "5"
      PROVIDER_READ_TIMEOUT_SECONDS: "10"
      PROVIDER_RETRY_BACKOFF_SECONDS: "0.1"
      PROVIDER_RETRY_COUNT: "2"
      PROVIDER_WRITE_TIMEOUT_SECONDS: "5"
      REQUIRE_INTEGRATION_TESTS: "false"
      SCAN_ENABLED: "false"
      SERVICE_NAME: migrate
      SETUP_SCORE_THRESHOLD: "85"
      SIGNAL_VALID_MINUTES: "30"
      STORAGE_TIMEZONE: UTC
      TELEGRAM_ALLOWED_CHAT_ID: ""
      TELEGRAM_ALLOWED_USER_ID: ""
      TELEGRAM_BOT_TOKEN: ""
      TELEGRAM_ENABLED: "false"
      TEST_DATABASE_URL: postgresql+asyncpg://ai_trading_os:ai_trading_os@localhost:5432/ai_trading_os_test
      TWELVE_DATA_API_KEY: ""
      TWELVE_DATA_BASE_URL: https://api.twelvedata.com
    networks:
      default: null
  postgres:
    environment:
      POSTGRES_DB: ai_trading_os
      POSTGRES_PASSWORD: ai_trading_os
      POSTGRES_USER: ai_trading_os
    healthcheck:
      test:
        - CMD-SHELL
        - pg_isready -U ai_trading_os -d ai_trading_os
      timeout: 3s
      interval: 5s
      retries: 20
    image: postgres:16-alpine
    networks:
      default: null
    volumes:
      - type: volume
        source: postgres_data
        target: /var/lib/postgresql/data
        volume: {}
  worker:
    build:
      context: /Users/artem.otsel/Documents/ai-trading-os
      dockerfile: Dockerfile
    command:
      - python
      - -m
      - app.scheduler.worker
    depends_on:
      migrate:
        condition: service_completed_successfully
        required: true
      postgres:
        condition: service_healthy
        required: true
    environment:
      APP_ENV: development
      APP_NAME: AI Trading OS
      APP_TIMEZONE: Europe/Stockholm
      CALENDAR_ENABLED: "false"
      DATABASE_URL: postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os
      FMP_API_KEY: ""
      FMP_BASE_URL: https://financialmodelingprep.com
      INTERNAL_API_KEY: development-internal-key-change-me
      LOG_LEVEL: INFO
      MARKET_DATA_ENABLED: "false"
      MAX_CONSECUTIVE_LOSSES: "3"
      MAX_DAILY_LOSS_PERCENT: "1.5"
      MAX_OPEN_RISK_PERCENT: "1.0"
      MAX_WEEKLY_LOSS_PERCENT: "4.0"
      OPENAI_API_KEY: ""
      OPENAI_ENABLED: "false"
      OPENAI_MODEL: gpt-4.1
      PAPER_ACCOUNT_BALANCE: "10000"
      PAPER_ACCOUNT_CURRENCY: EUR
      PAPER_RISK_PERCENT: "0.5"
      PROVIDER_CONNECT_TIMEOUT_SECONDS: "5"
      PROVIDER_MAX_REQUEST_RANGE_DAYS: "31"
      PROVIDER_POOL_TIMEOUT_SECONDS: "5"
      PROVIDER_READ_TIMEOUT_SECONDS: "10"
      PROVIDER_RETRY_BACKOFF_SECONDS: "0.1"
      PROVIDER_RETRY_COUNT: "2"
      PROVIDER_WRITE_TIMEOUT_SECONDS: "5"
      REQUIRE_INTEGRATION_TESTS: "false"
      SCAN_ENABLED: "false"
      SERVICE_NAME: worker
      SETUP_SCORE_THRESHOLD: "85"
      SIGNAL_VALID_MINUTES: "30"
      STORAGE_TIMEZONE: UTC
      TELEGRAM_ALLOWED_CHAT_ID: ""
      TELEGRAM_ALLOWED_USER_ID: ""
      TELEGRAM_BOT_TOKEN: ""
      TELEGRAM_ENABLED: "false"
      TEST_DATABASE_URL: postgresql+asyncpg://ai_trading_os:ai_trading_os@localhost:5432/ai_trading_os_test
      TWELVE_DATA_API_KEY: ""
      TWELVE_DATA_BASE_URL: https://api.twelvedata.com
    networks:
      default: null
networks:
  default:
    name: ai-trading-os_default
volumes:
  postgres_data:
    name: ai-trading-os_postgres_data
```

## Final Verification Status

- Phase 3A changes are currently uncommitted.
- `uv run ruff format --check .` passed with `88 files already formatted`.
- `uv run ruff check .` passed with `All checks passed!`.
- `uv run mypy app` passed with `Success: no issues found in 63 source files`.
- `uv run pytest` passed with `145 passed, 5 skipped, 1 warning`.
- `uv run python scripts/security_check.py` exited with code `0`.
- `docker compose build` succeeded.
- `docker compose run --rm migrate alembic current` returned
  `0002_phase2_data_constraints (head)`.
- `docker compose run --rm migrate alembic check` returned
  `No new upgrade operations detected.`
- The `ai_trading_os_test` database migration to head succeeded.
- Docker integration tests were run twice against the same `ai_trading_os_test` database without
  cleanup between runs; both runs passed with `5 passed, 1 warning`.

## Remaining Risks

- Phase 3A adds no migration; it uses existing Phase 2 candle and economic event tables.

## Phase Boundary Confirmation

- Phase 3B was not started.

- No strategy, signals, AI agents, OpenAI calls, broker APIs, paper trading, order execution, or real trading exist in this Phase 3A implementation.

- Existing foundation-era signal, direction, agent, or paper-position schemas/tables remain inactive and were not used for decision-making.

## Traceability Table

| Requirement | Implementation file | Test file | Verification result |

|---|---|---|---|

| Update project phase | `app/core/constants.py` | `tests/integration/test_database_and_api.py` | .venv mypy/pytest passed |

| Persist normalized closed candles | `app/persistence/repositories/foundation.py` | `tests/integration/test_database_and_api.py` | Repository test present; default integration skipped without DB |

| Persist normalized economic events | `app/persistence/repositories/foundation.py` | `tests/integration/test_database_and_api.py` | Repository test present; default integration skipped without DB |

| Duplicate-safe upsert behavior | `app/persistence/repositories/foundation.py` | `tests/integration/test_database_and_api.py` | Upsert insert/update assertions added |

| Deterministic data-quality checks | `app/domain/entities/data_quality.py` | `tests/unit/test_data_quality_foundation.py` | .venv pytest passed |

| Read/query repositories | `app/domain/interfaces/repositories.py; app/persistence/repositories/foundation.py` | `tests/integration/test_database_and_api.py` | Query test present; default integration skipped without DB |

| Feature-snapshot structures | `app/domain/entities/data_quality.py` | `tests/unit/test_data_quality_foundation.py` | .venv pytest passed |

| Historical replay utilities | `app/domain/replay.py` | `tests/unit/test_data_quality_foundation.py` | .venv pytest passed |

| Keep integrations disabled by default | `README.md; AGENTS.md; existing settings` | `tests/contract/test_provider_contracts.py` | .venv pytest passed |

| No strategy/signals/trading activation | `No activation code added` | `tests/contract/test_safety_boundaries.py` | .venv security_check passed |


## Full Contents Of Changed Source Files

### `app/core/constants.py`

```python
PROJECT_PHASE = "phase_3a_data_quality_foundation"
STRATEGY_IMPLEMENTED = False
REAL_TRADING_ENABLED = False

SYSTEM_STATE_SCAN_ENABLED = "scan_enabled"
SYSTEM_STATE_WORKER_HEARTBEAT = "worker_heartbeat"
SYSTEM_STATE_LAST_SUCCESSFUL_MARKET_FETCH = "last_successful_market_fetch"
SYSTEM_STATE_LAST_SUCCESSFUL_CALENDAR_FETCH = "last_successful_calendar_fetch"
SYSTEM_STATE_LAST_ERROR = "last_error"

DEFAULT_STRATEGY_VERSION = "foundation-v1"

```

### `app/domain/entities/__init__.py`

```python
from app.domain.entities.data_quality import (
    CandleAvailability,
    DataQualityIssue,
    DataQualityIssueCode,
    EconomicEventAvailability,
    FeatureSnapshot,
    UpsertResult,
    build_feature_snapshot,
)
from app.domain.entities.market_data import Candle, EconomicEvent, EconomicImpact, Timeframe

__all__ = [
    "Candle",
    "CandleAvailability",
    "DataQualityIssue",
    "DataQualityIssueCode",
    "EconomicEvent",
    "EconomicEventAvailability",
    "EconomicImpact",
    "FeatureSnapshot",
    "Timeframe",
    "UpsertResult",
    "build_feature_snapshot",
]

```

### `app/domain/entities/data_quality.py`

```python
from collections import Counter
from collections.abc import Sequence
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.market_data import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.value_objects import CurrencyPair

TIMEFRAME_TO_DELTA = {Timeframe.M15: timedelta(minutes=15), Timeframe.H1: timedelta(hours=1)}


class DataQualityIssueCode(StrEnum):
    NO_CANDLES = "NO_CANDLES"
    WINDOW_NOT_ALIGNED = "WINDOW_NOT_ALIGNED"
    CANDLE_OUT_OF_RANGE = "CANDLE_OUT_OF_RANGE"
    CANDLE_PAIR_MISMATCH = "CANDLE_PAIR_MISMATCH"
    CANDLE_TIMEFRAME_MISMATCH = "CANDLE_TIMEFRAME_MISMATCH"
    DUPLICATE_CANDLE = "DUPLICATE_CANDLE"
    MISSING_CANDLE = "MISSING_CANDLE"
    EVENT_OUT_OF_RANGE = "EVENT_OUT_OF_RANGE"


class DataQualityIssue(BaseModel):
    code: DataQualityIssueCode
    description: str = Field(min_length=1)
    timestamp: datetime | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_utc(cls, value: datetime | None) -> datetime | None:
        return normalize_to_utc(value) if value is not None else None


class UpsertResult(BaseModel):
    inserted: int = Field(ge=0)
    updated: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)

    @property
    def total(self) -> int:
        return self.inserted + self.updated


class CandleAvailability(BaseModel):
    expected_count: int = Field(ge=0)
    observed_count: int = Field(ge=0)
    missing_count: int = Field(ge=0)
    first_open_time: datetime | None = None
    last_close_time: datetime | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("first_open_time", "last_close_time")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime | None) -> datetime | None:
        return normalize_to_utc(value) if value is not None else None

    @property
    def is_complete(self) -> bool:
        return self.expected_count > 0 and self.observed_count == self.expected_count


class EconomicEventAvailability(BaseModel):
    event_count: int = Field(ge=0)
    currencies: tuple[str, ...] = ()
    high_impact_count: int = Field(default=0, ge=0)

    model_config = ConfigDict(frozen=True)


class FeatureSnapshot(BaseModel):
    pair: CurrencyPair
    timeframe: Timeframe
    window_start: datetime
    window_end: datetime
    candle_availability: CandleAvailability
    economic_event_availability: EconomicEventAvailability
    quality_issues: tuple[DataQualityIssue, ...] = ()

    model_config = ConfigDict(frozen=True)

    @field_validator("window_start", "window_end")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @model_validator(mode="after")
    def validate_window(self) -> Self:
        if self.window_end <= self.window_start:
            raise ValueError("snapshot window_end must be later than window_start")
        return self

    @property
    def market_data_complete(self) -> bool:
        blocking_codes = {
            DataQualityIssueCode.NO_CANDLES,
            DataQualityIssueCode.WINDOW_NOT_ALIGNED,
            DataQualityIssueCode.CANDLE_OUT_OF_RANGE,
            DataQualityIssueCode.CANDLE_PAIR_MISMATCH,
            DataQualityIssueCode.CANDLE_TIMEFRAME_MISMATCH,
            DataQualityIssueCode.DUPLICATE_CANDLE,
            DataQualityIssueCode.MISSING_CANDLE,
        }
        return self.candle_availability.is_complete and not any(
            issue.code in blocking_codes for issue in self.quality_issues
        )


def _expected_open_times(
    *,
    timeframe: Timeframe,
    window_start: datetime,
    window_end: datetime,
) -> tuple[datetime, ...]:
    delta = TIMEFRAME_TO_DELTA[timeframe]
    expected: list[datetime] = []
    cursor = window_start
    while cursor + delta <= window_end:
        expected.append(cursor)
        cursor += delta
    return tuple(expected)


def build_feature_snapshot(
    *,
    pair: CurrencyPair,
    timeframe: Timeframe,
    window_start: datetime,
    window_end: datetime,
    candles: Sequence[Candle],
    economic_events: Sequence[EconomicEvent] = (),
) -> FeatureSnapshot:
    start_utc = normalize_to_utc(window_start)
    end_utc = normalize_to_utc(window_end)
    if end_utc <= start_utc:
        raise ValueError("snapshot window_end must be later than window_start")

    expected_times = _expected_open_times(
        timeframe=timeframe,
        window_start=start_utc,
        window_end=end_utc,
    )
    issues: list[DataQualityIssue] = []
    delta = TIMEFRAME_TO_DELTA[timeframe]
    if start_utc + (len(expected_times) * delta) != end_utc:
        issues.append(
            DataQualityIssue(
                code=DataQualityIssueCode.WINDOW_NOT_ALIGNED,
                description="Requested window is not an exact multiple of the timeframe.",
            )
        )

    observed_times: list[datetime] = []
    matching_candles: list[Candle] = []
    for candle in candles:
        if candle.pair != pair:
            issues.append(
                DataQualityIssue(
                    code=DataQualityIssueCode.CANDLE_PAIR_MISMATCH,
                    description="Candle pair does not match the requested pair.",
                    timestamp=candle.open_time,
                )
            )
            continue
        if candle.timeframe != timeframe:
            issues.append(
                DataQualityIssue(
                    code=DataQualityIssueCode.CANDLE_TIMEFRAME_MISMATCH,
                    description="Candle timeframe does not match the requested timeframe.",
                    timestamp=candle.open_time,
                )
            )
            continue
        if candle.open_time < start_utc or candle.close_time > end_utc:
            issues.append(
                DataQualityIssue(
                    code=DataQualityIssueCode.CANDLE_OUT_OF_RANGE,
                    description="Candle is not fully contained in the requested window.",
                    timestamp=candle.open_time,
                )
            )
            continue
        matching_candles.append(candle)
        observed_times.append(candle.open_time)

    duplicates = [open_time for open_time, count in Counter(observed_times).items() if count > 1]
    for open_time in sorted(duplicates):
        issues.append(
            DataQualityIssue(
                code=DataQualityIssueCode.DUPLICATE_CANDLE,
                description="Duplicate candle open time in snapshot window.",
                timestamp=open_time,
            )
        )

    observed_unique = set(observed_times)
    for open_time in expected_times:
        if open_time not in observed_unique:
            issues.append(
                DataQualityIssue(
                    code=DataQualityIssueCode.MISSING_CANDLE,
                    description="Expected candle is missing from snapshot window.",
                    timestamp=open_time,
                )
            )

    if not matching_candles:
        issues.append(
            DataQualityIssue(
                code=DataQualityIssueCode.NO_CANDLES,
                description="No matching closed candles are available in the requested window.",
            )
        )

    event_currencies: set[str] = set()
    high_impact_count = 0
    event_count = 0
    for event in economic_events:
        if event.scheduled_at < start_utc or event.scheduled_at >= end_utc:
            issues.append(
                DataQualityIssue(
                    code=DataQualityIssueCode.EVENT_OUT_OF_RANGE,
                    description="Economic event is outside the requested window.",
                    timestamp=event.scheduled_at,
                )
            )
            continue
        event_count += 1
        event_currencies.add(event.currency)
        if event.impact == EconomicImpact.HIGH:
            high_impact_count += 1

    return FeatureSnapshot(
        pair=pair,
        timeframe=timeframe,
        window_start=start_utc,
        window_end=end_utc,
        candle_availability=CandleAvailability(
            expected_count=len(expected_times),
            observed_count=len(observed_unique),
            missing_count=max(len(expected_times) - len(observed_unique), 0),
            first_open_time=min(observed_times) if observed_times else None,
            last_close_time=max((candle.close_time for candle in matching_candles), default=None),
        ),
        economic_event_availability=EconomicEventAvailability(
            event_count=event_count,
            currencies=tuple(sorted(event_currencies)),
            high_impact_count=high_impact_count,
        ),
        quality_issues=tuple(issues),
    )

```

### `app/domain/interfaces/repositories.py`

```python
from collections.abc import Mapping
from datetime import datetime
from typing import Any, Protocol

from app.domain.entities import Candle, EconomicEvent, Timeframe
from app.domain.entities.data_quality import UpsertResult
from app.domain.value_objects import CurrencyPair


class SystemStateRepository(Protocol):
    async def get(self, key: str) -> Any | None:
        """Return one state value by key."""

    async def set(self, key: str, value: Any) -> None:
        """Persist one state value by key."""

    async def get_all(self) -> dict[str, Any]:
        """Return all persisted system state values."""


class AuditLogRepository(Protocol):
    async def add(
        self,
        *,
        event_type: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        actor: str | None = None,
        before_json: Mapping[str, Any] | None = None,
        after_json: Mapping[str, Any] | None = None,
    ) -> None:
        """Append an audit log event."""


class ErrorEventRepository(Protocol):
    async def add(
        self,
        *,
        error_code: str,
        severity: str,
        component: str,
        message_ru: str,
        technical_details: str | None = None,
        context_json: Mapping[str, Any] | None = None,
        resolved: bool = False,
    ) -> None:
        """Append a structured error event."""


class CandleRepository(Protocol):
    async def upsert_many(self, candles: list[Candle]) -> UpsertResult:
        """Insert or update normalized closed candles without creating duplicates."""

    async def list_range(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        start_at: datetime,
        end_at: datetime,
        provider: str | None = None,
    ) -> list[Candle]:
        """Return closed candles fully contained in the requested UTC window."""


class EconomicEventRepository(Protocol):
    async def upsert_many(self, events: list[EconomicEvent]) -> UpsertResult:
        """Insert or update normalized economic events without creating duplicates."""

    async def list_window(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
        currencies: list[str] | None = None,
        provider: str | None = None,
    ) -> list[EconomicEvent]:
        """Return economic events satisfying start_at <= scheduled_at < end_at."""

```

### `app/domain/interfaces/unit_of_work.py`

```python
from types import TracebackType
from typing import Protocol, Self

from app.domain.interfaces.repositories import (
    AuditLogRepository,
    CandleRepository,
    EconomicEventRepository,
    ErrorEventRepository,
    SystemStateRepository,
)


class UnitOfWork(Protocol):
    @property
    def system_state(self) -> SystemStateRepository:
        """Repository for persisted system state."""
        ...

    @property
    def audit_logs(self) -> AuditLogRepository:
        """Repository for audit events."""
        ...

    @property
    def error_events(self) -> ErrorEventRepository:
        """Repository for structured error events."""
        ...

    @property
    def candles(self) -> CandleRepository:
        """Repository for normalized closed candles."""
        ...

    @property
    def economic_events(self) -> EconomicEventRepository:
        """Repository for normalized economic events."""
        ...

    async def __aenter__(self) -> Self:
        """Open one asynchronous persistence boundary."""

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Rollback uncommitted work and close resources."""

    async def commit(self) -> None:
        """Commit the current unit of work explicitly."""

    async def rollback(self) -> None:
        """Rollback the current unit of work."""

```

### `app/domain/replay.py`

```python
from collections.abc import Sequence
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.core.time import normalize_to_utc
from app.domain.entities.data_quality import FeatureSnapshot, build_feature_snapshot
from app.domain.entities.market_data import Candle, EconomicEvent, Timeframe
from app.domain.value_objects import CurrencyPair


class HistoricalReplayFrame(BaseModel):
    as_of: datetime
    candles: tuple[Candle, ...]
    economic_events: tuple[EconomicEvent, ...]
    feature_snapshot: FeatureSnapshot

    model_config = ConfigDict(frozen=True)

    @field_validator("as_of")
    @classmethod
    def as_of_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)


class HistoricalReplay:
    def __init__(
        self,
        *,
        candles: Sequence[Candle],
        economic_events: Sequence[EconomicEvent] = (),
    ) -> None:
        self._candles = tuple(
            sorted(candles, key=lambda candle: (candle.open_time, candle.provider))
        )
        self._economic_events = tuple(
            sorted(
                economic_events,
                key=lambda event: (event.scheduled_at, event.currency, event.provider_event_id),
            )
        )

    def frame(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        window_start: datetime,
        window_end: datetime,
        as_of: datetime,
        currencies: Sequence[str] | None = None,
    ) -> HistoricalReplayFrame:
        start_utc = normalize_to_utc(window_start)
        end_utc = normalize_to_utc(window_end)
        as_of_utc = normalize_to_utc(as_of)
        currency_filter = set(currencies) if currencies is not None else None
        candles = tuple(
            candle
            for candle in self._candles
            if candle.pair == pair
            and candle.timeframe == timeframe
            and candle.open_time >= start_utc
            and candle.close_time <= end_utc
            and candle.close_time <= as_of_utc
        )
        economic_events = tuple(
            event
            for event in self._economic_events
            if event.scheduled_at >= start_utc
            and event.scheduled_at < end_utc
            and event.scheduled_at <= as_of_utc
            and (currency_filter is None or event.currency in currency_filter)
        )
        snapshot = build_feature_snapshot(
            pair=pair,
            timeframe=timeframe,
            window_start=start_utc,
            window_end=end_utc,
            candles=candles,
            economic_events=economic_events,
        )
        return HistoricalReplayFrame(
            as_of=as_of_utc,
            candles=candles,
            economic_events=economic_events,
            feature_snapshot=snapshot,
        )

```

### `app/persistence/repositories/__init__.py`

```python
from app.persistence.repositories.foundation import (
    SqlAlchemyAuditLogRepository,
    SqlAlchemyCandleRepository,
    SqlAlchemyEconomicEventRepository,
    SqlAlchemyErrorEventRepository,
    SqlAlchemySystemStateRepository,
)

__all__ = [
    "SqlAlchemyAuditLogRepository",
    "SqlAlchemyCandleRepository",
    "SqlAlchemyEconomicEventRepository",
    "SqlAlchemyErrorEventRepository",
    "SqlAlchemySystemStateRepository",
]

```

### `app/persistence/repositories/foundation.py`

```python
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import redact_text
from app.core.time import normalize_to_utc, utc_now
from app.domain.entities import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.entities.data_quality import UpsertResult
from app.domain.value_objects import CurrencyPair
from app.persistence.models import (
    AuditLogModel,
    CandleModel,
    EconomicEventModel,
    ErrorEventModel,
    SystemStateModel,
)


def _candle_from_model(row: CandleModel) -> Candle:
    return Candle(
        provider=row.provider,
        pair=CurrencyPair(value=row.pair),
        timeframe=Timeframe(row.timeframe),
        open_time=row.open_time,
        close_time=row.close_time,
        open=row.open,
        high=row.high,
        low=row.low,
        close=row.close,
        volume=row.volume,
        is_closed=row.is_closed,
    )


def _event_from_model(row: EconomicEventModel) -> EconomicEvent:
    return EconomicEvent(
        provider=row.provider,
        provider_event_id=row.provider_event_id,
        title=row.title,
        currency=row.currency,
        country=row.country,
        impact=EconomicImpact(row.impact),
        scheduled_at=row.scheduled_at,
        actual=row.actual,
        forecast=row.forecast,
        previous=row.previous,
        actual_raw=row.actual_raw,
        forecast_raw=row.forecast_raw,
        previous_raw=row.previous_raw,
        fetched_at=row.fetched_at,
    )


class SqlAlchemySystemStateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, key: str) -> Any | None:
        row = await self._session.get(SystemStateModel, key)
        return None if row is None else row.value_json

    async def set(self, key: str, value: Any) -> None:
        row = await self._session.get(SystemStateModel, key)
        if row is None:
            self._session.add(SystemStateModel(key=key, value_json=value))
            return
        row.value_json = value
        row.updated_at = utc_now()

    async def get_all(self) -> dict[str, Any]:
        result = await self._session.execute(select(SystemStateModel))
        rows = result.scalars().all()
        return {row.key: row.value_json for row in rows}


class SqlAlchemyAuditLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(
        self,
        *,
        event_type: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        actor: str | None = None,
        before_json: Mapping[str, Any] | None = None,
        after_json: Mapping[str, Any] | None = None,
    ) -> None:
        self._session.add(
            AuditLogModel(
                event_type=event_type,
                entity_type=entity_type,
                entity_id=entity_id,
                actor=actor,
                before_json=dict(before_json) if before_json is not None else None,
                after_json=dict(after_json) if after_json is not None else None,
            )
        )


class SqlAlchemyErrorEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(
        self,
        *,
        error_code: str,
        severity: str,
        component: str,
        message_ru: str,
        technical_details: str | None = None,
        context_json: Mapping[str, Any] | None = None,
        resolved: bool = False,
    ) -> None:
        self._session.add(
            ErrorEventModel(
                error_code=error_code,
                severity=severity,
                component=component,
                message_ru=message_ru,
                technical_details=redact_text(technical_details) if technical_details else None,
                context_json=dict(context_json) if context_json is not None else None,
                resolved=resolved,
            )
        )


class SqlAlchemyCandleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_many(self, candles: list[Candle]) -> UpsertResult:
        inserted = 0
        updated = 0
        for candle in candles:
            result = await self._session.execute(
                select(CandleModel).where(
                    CandleModel.provider == candle.provider,
                    CandleModel.pair == candle.pair.value,
                    CandleModel.timeframe == candle.timeframe.value,
                    CandleModel.open_time == candle.open_time,
                )
            )
            row = result.scalar_one_or_none()
            if row is None:
                self._session.add(
                    CandleModel(
                        provider=candle.provider,
                        pair=candle.pair.value,
                        timeframe=candle.timeframe.value,
                        open_time=candle.open_time,
                        close_time=candle.close_time,
                        open=candle.open,
                        high=candle.high,
                        low=candle.low,
                        close=candle.close,
                        volume=candle.volume,
                        is_closed=True,
                    )
                )
                inserted += 1
                continue
            row.close_time = candle.close_time
            row.open = candle.open
            row.high = candle.high
            row.low = candle.low
            row.close = candle.close
            row.volume = candle.volume
            row.is_closed = True
            updated += 1
        return UpsertResult(inserted=inserted, updated=updated)

    async def list_range(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        start_at: datetime,
        end_at: datetime,
        provider: str | None = None,
    ) -> list[Candle]:
        start_utc = normalize_to_utc(start_at)
        end_utc = normalize_to_utc(end_at)
        query = select(CandleModel).where(
            CandleModel.pair == pair.value,
            CandleModel.timeframe == timeframe.value,
            CandleModel.open_time >= start_utc,
            CandleModel.close_time <= end_utc,
            CandleModel.is_closed.is_(True),
        )
        if provider is not None:
            query = query.where(CandleModel.provider == provider)
        result = await self._session.execute(
            query.order_by(CandleModel.open_time.asc(), CandleModel.provider.asc())
        )
        return [_candle_from_model(row) for row in result.scalars().all()]


class SqlAlchemyEconomicEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_many(self, events: list[EconomicEvent]) -> UpsertResult:
        inserted = 0
        updated = 0
        for event in events:
            result = await self._session.execute(
                select(EconomicEventModel).where(
                    EconomicEventModel.provider == event.provider,
                    EconomicEventModel.provider_event_id == event.provider_event_id,
                )
            )
            row = result.scalar_one_or_none()
            if row is None:
                self._session.add(
                    EconomicEventModel(
                        provider=event.provider,
                        provider_event_id=event.provider_event_id,
                        title=event.title,
                        currency=event.currency,
                        country=event.country,
                        impact=event.impact.value,
                        scheduled_at=event.scheduled_at,
                        actual=event.actual,
                        forecast=event.forecast,
                        previous=event.previous,
                        actual_raw=event.actual_raw,
                        forecast_raw=event.forecast_raw,
                        previous_raw=event.previous_raw,
                        fetched_at=event.fetched_at,
                    )
                )
                inserted += 1
                continue
            row.title = event.title
            row.currency = event.currency
            row.country = event.country
            row.impact = event.impact.value
            row.scheduled_at = event.scheduled_at
            row.actual = event.actual
            row.forecast = event.forecast
            row.previous = event.previous
            row.actual_raw = event.actual_raw
            row.forecast_raw = event.forecast_raw
            row.previous_raw = event.previous_raw
            row.fetched_at = event.fetched_at
            updated += 1
        return UpsertResult(inserted=inserted, updated=updated)

    async def list_window(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
        currencies: list[str] | None = None,
        provider: str | None = None,
    ) -> list[EconomicEvent]:
        start_utc = normalize_to_utc(start_at)
        end_utc = normalize_to_utc(end_at)
        query = select(EconomicEventModel).where(
            EconomicEventModel.scheduled_at >= start_utc,
            EconomicEventModel.scheduled_at < end_utc,
        )
        if currencies is not None:
            query = query.where(EconomicEventModel.currency.in_(currencies))
        if provider is not None:
            query = query.where(EconomicEventModel.provider == provider)
        result = await self._session.execute(
            query.order_by(
                EconomicEventModel.scheduled_at.asc(),
                EconomicEventModel.currency.asc(),
                EconomicEventModel.provider_event_id.asc(),
            )
        )
        return [_event_from_model(row) for row in result.scalars().all()]

```

### `app/persistence/unit_of_work.py`

```python
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.interfaces.repositories import (
    AuditLogRepository,
    CandleRepository,
    EconomicEventRepository,
    ErrorEventRepository,
    SystemStateRepository,
)
from app.persistence.repositories import (
    SqlAlchemyAuditLogRepository,
    SqlAlchemyCandleRepository,
    SqlAlchemyEconomicEventRepository,
    SqlAlchemyErrorEventRepository,
    SqlAlchemySystemStateRepository,
)


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._committed = False
        self._system_state: SystemStateRepository | None = None
        self._audit_logs: AuditLogRepository | None = None
        self._error_events: ErrorEventRepository | None = None
        self._candles: CandleRepository | None = None
        self._economic_events: EconomicEventRepository | None = None

    async def __aenter__(self) -> Self:
        if self._session is not None:
            raise RuntimeError("unit of work is already active")
        self._session = self._session_factory()
        self._committed = False
        self._system_state = SqlAlchemySystemStateRepository(self._session)
        self._audit_logs = SqlAlchemyAuditLogRepository(self._session)
        self._error_events = SqlAlchemyErrorEventRepository(self._session)
        self._candles = SqlAlchemyCandleRepository(self._session)
        self._economic_events = SqlAlchemyEconomicEventRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session is None:
            return
        try:
            in_transaction = getattr(self._session, "in_transaction", lambda: False)
            if exc_type is not None or not self._committed or in_transaction():
                await self._session.rollback()
        finally:
            await self._session.close()
            self._session = None
            self._system_state = None
            self._audit_logs = None
            self._error_events = None
            self._candles = None
            self._economic_events = None
            self._committed = False

    @property
    def system_state(self) -> SystemStateRepository:
        if self._session is None or self._system_state is None:
            raise RuntimeError("unit of work has not been entered")
        return self._system_state

    @property
    def audit_logs(self) -> AuditLogRepository:
        if self._session is None or self._audit_logs is None:
            raise RuntimeError("unit of work has not been entered")
        return self._audit_logs

    @property
    def error_events(self) -> ErrorEventRepository:
        if self._session is None or self._error_events is None:
            raise RuntimeError("unit of work has not been entered")
        return self._error_events

    @property
    def candles(self) -> CandleRepository:
        if self._session is None or self._candles is None:
            raise RuntimeError("unit of work has not been entered")
        return self._candles

    @property
    def economic_events(self) -> EconomicEventRepository:
        if self._session is None or self._economic_events is None:
            raise RuntimeError("unit of work has not been entered")
        return self._economic_events

    async def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("unit of work has not been entered")
        await self._session.commit()
        self._committed = True

    async def rollback(self) -> None:
        if self._session is None:
            raise RuntimeError("unit of work has not been entered")
        await self._session.rollback()
        self._committed = False

```

## Migration Contents

### `migrations/versions/0001_foundation_schema.py`

```python
"""foundation schema

Revision ID: 0001_foundation_schema
Revises:
Create Date: 2026-07-02 00:00:00.000000
"""

from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_foundation_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "system_state",
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("value_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )
    system_state = sa.table(
        "system_state",
        sa.column("key", sa.String),
        sa.column("value_json", postgresql.JSONB),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    op.bulk_insert(
        system_state,
        [{"key": "scan_enabled", "value_json": False, "updated_at": datetime.now(UTC)}],
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("entity_type", sa.String(length=120), nullable=True),
        sa.Column("entity_id", sa.String(length=120), nullable=True),
        sa.Column("actor", sa.String(length=120), nullable=True),
        sa.Column("before_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("after_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])
    op.create_index("ix_audit_logs_event_type", "audit_logs", ["event_type"])

    op.create_table(
        "error_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("error_code", sa.String(length=80), nullable=False),
        sa.Column("severity", sa.String(length=30), nullable=False),
        sa.Column("component", sa.String(length=120), nullable=False),
        sa.Column("message_ru", sa.String(length=500), nullable=False),
        sa.Column("technical_details", sa.String(length=2000), nullable=True),
        sa.Column("context_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("resolved", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_error_events_component", "error_events", ["component"])
    op.create_index("ix_error_events_created_at", "error_events", ["created_at"])
    op.create_index("ix_error_events_error_code", "error_events", ["error_code"])
    op.create_index("ix_error_events_resolved", "error_events", ["resolved"])
    op.create_index("ix_error_events_severity", "error_events", ["severity"])

    op.create_table(
        "candles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("pair", sa.String(length=6), nullable=False),
        sa.Column("timeframe", sa.String(length=20), nullable=False),
        sa.Column("open_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("close_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Numeric(20, 10), nullable=False),
        sa.Column("high", sa.Numeric(20, 10), nullable=False),
        sa.Column("low", sa.Numeric(20, 10), nullable=False),
        sa.Column("close", sa.Numeric(20, 10), nullable=False),
        sa.Column("volume", sa.Numeric(24, 8), nullable=True),
        sa.Column("is_closed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "provider", "pair", "timeframe", "open_time", name="uq_candle_identity"
        ),
    )
    op.create_index("ix_candles_close_time", "candles", ["close_time"])
    op.create_index("ix_candles_pair", "candles", ["pair"])
    op.create_index(
        "ix_candles_pair_timeframe_close_time",
        "candles",
        ["pair", "timeframe", "close_time"],
    )
    op.create_index("ix_candles_timeframe", "candles", ["timeframe"])

    op.create_table(
        "economic_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider_event_id", sa.String(length=120), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("impact", sa.String(length=40), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actual", sa.Numeric(20, 6), nullable=True),
        sa.Column("forecast", sa.Numeric(20, 6), nullable=True),
        sa.Column("previous", sa.Numeric(20, 6), nullable=True),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_economic_events_currency", "economic_events", ["currency"])
    op.create_index(
        "ix_economic_events_currency_scheduled",
        "economic_events",
        ["currency", "scheduled_at"],
    )
    op.create_index("ix_economic_events_impact", "economic_events", ["impact"])
    op.create_index(
        "ix_economic_events_provider_event_id", "economic_events", ["provider_event_id"]
    )
    op.create_index("ix_economic_events_scheduled_at", "economic_events", ["scheduled_at"])

    op.create_table(
        "scans",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pair", sa.String(length=6), nullable=False),
        sa.Column("m15_close_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("strategy_version", sa.String(length=80), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pair", "m15_close_time", "strategy_version", name="uq_scan_identity"),
    )
    op.create_index("ix_scans_pair", "scans", ["pair"])
    op.create_index("ix_scans_status", "scans", ["status"])
    op.create_index("ix_scans_status_started", "scans", ["status", "started_at"])

    op.create_table(
        "agent_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_name", sa.String(length=120), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False),
        sa.Column("verdict", sa.String(length=40), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.String(length=20), nullable=False),
        sa.Column("summary_ru", sa.String(length=2000), nullable=False),
        sa.Column("reasons_for_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("reasons_against_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("invalid_if_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("evidence_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("rule_version", sa.String(length=80), nullable=False),
        sa.Column("model_version", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("score >= 0 AND score <= 100", name="ck_agent_reports_score_range"),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_reports_scan_agent", "agent_reports", ["scan_id", "agent_name"])
    op.create_index("ix_agent_reports_scan_id", "agent_reports", ["scan_id"])

    op.create_table(
        "signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fingerprint", sa.String(length=160), nullable=False),
        sa.Column("pair", sa.String(length=6), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False),
        sa.Column("setup_score", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.String(length=20), nullable=False),
        sa.Column("entry_min", sa.Numeric(20, 10), nullable=False),
        sa.Column("entry_max", sa.Numeric(20, 10), nullable=False),
        sa.Column("invalidation_price", sa.Numeric(20, 10), nullable=False),
        sa.Column("stop_loss", sa.Numeric(20, 10), nullable=False),
        sa.Column("take_profit_1", sa.Numeric(20, 10), nullable=False),
        sa.Column("take_profit_2", sa.Numeric(20, 10), nullable=False),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancel_reason_ru", sa.String(length=1000), nullable=True),
        sa.Column("strategy_version", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_signals_pair", "signals", ["pair"])
    op.create_index(
        "ix_signals_pair_status_valid_until", "signals", ["pair", "status", "valid_until"]
    )
    op.create_index("ix_signals_scan_id", "signals", ["scan_id"])
    op.create_index("ix_signals_status", "signals", ["status"])
    op.create_index("ix_signals_valid_until", "signals", ["valid_until"])
    op.create_index("uq_signals_fingerprint", "signals", ["fingerprint"], unique=True)

    op.create_table(
        "paper_positions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("signal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_balance_before", sa.Numeric(20, 2), nullable=False),
        sa.Column("risk_percent", sa.Numeric(8, 4), nullable=False),
        sa.Column("risk_amount_eur", sa.Numeric(20, 2), nullable=False),
        sa.Column("position_size", sa.Numeric(24, 8), nullable=False),
        sa.Column("entry_price", sa.Numeric(20, 10), nullable=False),
        sa.Column("entered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("stop_loss", sa.Numeric(20, 10), nullable=False),
        sa.Column("take_profit_1", sa.Numeric(20, 10), nullable=False),
        sa.Column("take_profit_2", sa.Numeric(20, 10), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("result_eur", sa.Numeric(20, 2), nullable=True),
        sa.Column("result_percent", sa.Numeric(10, 4), nullable=True),
        sa.Column("result_r", sa.Numeric(10, 4), nullable=True),
        sa.Column("spread_cost", sa.Numeric(20, 2), nullable=True),
        sa.Column("slippage_cost", sa.Numeric(20, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["signal_id"], ["signals.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_paper_positions_signal_id", "paper_positions", ["signal_id"])
    op.create_index("ix_paper_positions_status", "paper_positions", ["status"])
    op.create_index(
        "ix_paper_positions_status_created",
        "paper_positions",
        ["status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_paper_positions_status_created", table_name="paper_positions")
    op.drop_index("ix_paper_positions_status", table_name="paper_positions")
    op.drop_index("ix_paper_positions_signal_id", table_name="paper_positions")
    op.drop_table("paper_positions")
    op.drop_index("uq_signals_fingerprint", table_name="signals")
    op.drop_index("ix_signals_valid_until", table_name="signals")
    op.drop_index("ix_signals_status", table_name="signals")
    op.drop_index("ix_signals_scan_id", table_name="signals")
    op.drop_index("ix_signals_pair_status_valid_until", table_name="signals")
    op.drop_index("ix_signals_pair", table_name="signals")
    op.drop_table("signals")
    op.drop_index("ix_agent_reports_scan_id", table_name="agent_reports")
    op.drop_index("ix_agent_reports_scan_agent", table_name="agent_reports")
    op.drop_table("agent_reports")
    op.drop_index("ix_scans_status_started", table_name="scans")
    op.drop_index("ix_scans_status", table_name="scans")
    op.drop_index("ix_scans_pair", table_name="scans")
    op.drop_table("scans")
    op.drop_index("ix_economic_events_scheduled_at", table_name="economic_events")
    op.drop_index("ix_economic_events_provider_event_id", table_name="economic_events")
    op.drop_index("ix_economic_events_impact", table_name="economic_events")
    op.drop_index("ix_economic_events_currency_scheduled", table_name="economic_events")
    op.drop_index("ix_economic_events_currency", table_name="economic_events")
    op.drop_table("economic_events")
    op.drop_index("ix_candles_timeframe", table_name="candles")
    op.drop_index("ix_candles_pair_timeframe_close_time", table_name="candles")
    op.drop_index("ix_candles_pair", table_name="candles")
    op.drop_index("ix_candles_close_time", table_name="candles")
    op.drop_table("candles")
    op.drop_index("ix_error_events_severity", table_name="error_events")
    op.drop_index("ix_error_events_resolved", table_name="error_events")
    op.drop_index("ix_error_events_error_code", table_name="error_events")
    op.drop_index("ix_error_events_created_at", table_name="error_events")
    op.drop_index("ix_error_events_component", table_name="error_events")
    op.drop_table("error_events")
    op.drop_index("ix_audit_logs_event_type", table_name="audit_logs")
    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_table("system_state")

```

### `migrations/versions/0002_phase2_data_constraints.py`

```python
"""phase2 data constraints

Revision ID: 0002_phase2_data_constraints
Revises: 0001_foundation_schema
Create Date: 2026-07-03 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_phase2_data_constraints"
down_revision: str | None = "0001_foundation_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("economic_events", sa.Column("country", sa.String(length=120), nullable=True))
    op.add_column("economic_events", sa.Column("actual_raw", sa.String(length=200), nullable=True))
    op.add_column(
        "economic_events", sa.Column("forecast_raw", sa.String(length=200), nullable=True)
    )
    op.add_column(
        "economic_events", sa.Column("previous_raw", sa.String(length=200), nullable=True)
    )
    op.create_unique_constraint(
        "uq_economic_events_provider_event",
        "economic_events",
        ["provider", "provider_event_id"],
    )
    op.create_check_constraint("ck_candles_open_positive", "candles", "open > 0")
    op.create_check_constraint("ck_candles_high_positive", "candles", "high > 0")
    op.create_check_constraint("ck_candles_low_positive", "candles", "low > 0")
    op.create_check_constraint("ck_candles_close_positive", "candles", "close > 0")
    op.create_check_constraint("ck_candles_close_after_open", "candles", "close_time > open_time")
    op.create_check_constraint(
        "ck_candles_volume_non_negative",
        "candles",
        "volume IS NULL OR volume >= 0",
    )
    op.create_check_constraint("ck_candles_is_closed", "candles", "is_closed = true")


def downgrade() -> None:
    op.drop_constraint("ck_candles_is_closed", "candles", type_="check")
    op.drop_constraint("ck_candles_volume_non_negative", "candles", type_="check")
    op.drop_constraint("ck_candles_close_after_open", "candles", type_="check")
    op.drop_constraint("ck_candles_close_positive", "candles", type_="check")
    op.drop_constraint("ck_candles_low_positive", "candles", type_="check")
    op.drop_constraint("ck_candles_high_positive", "candles", type_="check")
    op.drop_constraint("ck_candles_open_positive", "candles", type_="check")
    op.drop_constraint("uq_economic_events_provider_event", "economic_events", type_="unique")
    op.drop_column("economic_events", "previous_raw")
    op.drop_column("economic_events", "forecast_raw")
    op.drop_column("economic_events", "actual_raw")
    op.drop_column("economic_events", "country")

```

## New And Changed Tests

### `tests/unit/test_data_quality_foundation.py`

```python
from datetime import UTC, datetime
from decimal import Decimal

from app.domain.entities import (
    Candle,
    DataQualityIssueCode,
    EconomicEvent,
    EconomicImpact,
    Timeframe,
    build_feature_snapshot,
)
from app.domain.replay import HistoricalReplay
from app.domain.value_objects import CurrencyPair


def _candle(open_hour: int, open_minute: int = 0) -> Candle:
    open_time = datetime(2026, 7, 8, open_hour, open_minute, tzinfo=UTC)
    close_time = open_time.replace(minute=open_time.minute + 15)
    return Candle(
        provider="fixture",
        pair=CurrencyPair(value="EURUSD"),
        timeframe=Timeframe.M15,
        open_time=open_time,
        close_time=close_time,
        open=Decimal("1.1000"),
        high=Decimal("1.1050"),
        low=Decimal("1.0950"),
        close=Decimal("1.1020"),
        volume=Decimal("100"),
        is_closed=True,
    )


def _event(scheduled_at: datetime, currency: str = "EUR") -> EconomicEvent:
    return EconomicEvent(
        provider="fixture",
        provider_event_id=f"{currency}-{scheduled_at.isoformat()}",
        title="Consumer Price Index",
        currency=currency,
        country="Eurozone",
        impact=EconomicImpact.HIGH,
        scheduled_at=scheduled_at,
        actual=Decimal("2.2"),
        forecast=Decimal("2.1"),
        previous=Decimal("2.0"),
        fetched_at=datetime(2026, 7, 8, 7, 0, tzinfo=UTC),
    )


def test_feature_snapshot_reports_complete_market_data_window() -> None:
    snapshot = build_feature_snapshot(
        pair=CurrencyPair(value="EURUSD"),
        timeframe=Timeframe.M15,
        window_start=datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
        window_end=datetime(2026, 7, 8, 8, 30, tzinfo=UTC),
        candles=[_candle(8, 0), _candle(8, 15)],
        economic_events=[_event(datetime(2026, 7, 8, 8, 10, tzinfo=UTC))],
    )

    assert snapshot.market_data_complete is True
    assert snapshot.candle_availability.expected_count == 2
    assert snapshot.candle_availability.observed_count == 2
    assert snapshot.economic_event_availability.event_count == 1
    assert snapshot.economic_event_availability.currencies == ("EUR",)
    assert snapshot.quality_issues == ()


def test_feature_snapshot_reports_missing_duplicate_and_out_of_range_data() -> None:
    outside = _candle(9, 0)
    duplicate = _candle(8, 0)

    snapshot = build_feature_snapshot(
        pair=CurrencyPair(value="EURUSD"),
        timeframe=Timeframe.M15,
        window_start=datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
        window_end=datetime(2026, 7, 8, 8, 45, tzinfo=UTC),
        candles=[_candle(8, 0), duplicate, outside],
        economic_events=[_event(datetime(2026, 7, 8, 9, 0, tzinfo=UTC))],
    )

    issue_codes = [issue.code for issue in snapshot.quality_issues]
    assert snapshot.market_data_complete is False
    assert DataQualityIssueCode.DUPLICATE_CANDLE in issue_codes
    assert DataQualityIssueCode.MISSING_CANDLE in issue_codes
    assert DataQualityIssueCode.CANDLE_OUT_OF_RANGE in issue_codes
    assert DataQualityIssueCode.EVENT_OUT_OF_RANGE in issue_codes


def test_historical_replay_frame_is_deterministic_and_cutoff_based() -> None:
    replay = HistoricalReplay(
        candles=[_candle(8, 0), _candle(8, 15)],
        economic_events=[
            _event(datetime(2026, 7, 8, 8, 5, tzinfo=UTC)),
            _event(datetime(2026, 7, 8, 8, 25, tzinfo=UTC), currency="USD"),
        ],
    )

    frame = replay.frame(
        pair=CurrencyPair(value="EURUSD"),
        timeframe=Timeframe.M15,
        window_start=datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
        window_end=datetime(2026, 7, 8, 8, 30, tzinfo=UTC),
        as_of=datetime(2026, 7, 8, 8, 15, tzinfo=UTC),
        currencies=["EUR"],
    )

    assert len(frame.candles) == 1
    assert frame.candles[0].open_time == datetime(2026, 7, 8, 8, 0, tzinfo=UTC)
    assert len(frame.economic_events) == 1
    assert frame.economic_events[0].currency == "EUR"
    assert frame.feature_snapshot.market_data_complete is False

```

### `tests/unit/test_unit_of_work_lifecycle.py`

```python
import pytest

from app.persistence.unit_of_work import SqlAlchemyUnitOfWork


class FakeSession:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0
        self.closes = 0

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        self.rollbacks += 1

    async def close(self) -> None:
        self.closes += 1


@pytest.mark.asyncio
async def test_uncommitted_exit_rolls_back_and_closes() -> None:
    session = FakeSession()
    uow = SqlAlchemyUnitOfWork(lambda: session)  # type: ignore[arg-type]

    async with uow:
        _ = uow.system_state

    assert session.rollbacks == 1
    assert session.closes == 1


@pytest.mark.asyncio
async def test_explicit_commit_commits_and_closes() -> None:
    session = FakeSession()
    uow = SqlAlchemyUnitOfWork(lambda: session)  # type: ignore[arg-type]

    async with uow:
        await uow.commit()

    assert session.commits == 1
    assert session.closes == 1


@pytest.mark.asyncio
async def test_exception_exit_rolls_back() -> None:
    session = FakeSession()
    uow = SqlAlchemyUnitOfWork(lambda: session)  # type: ignore[arg-type]

    with pytest.raises(RuntimeError):
        async with uow:
            raise RuntimeError("boom")

    assert session.rollbacks == 1
    assert session.closes == 1


@pytest.mark.asyncio
async def test_repository_access_after_exit_fails() -> None:
    session = FakeSession()
    uow = SqlAlchemyUnitOfWork(lambda: session)  # type: ignore[arg-type]

    async with uow:
        _ = uow.audit_logs
        _ = uow.candles
        _ = uow.economic_events

    with pytest.raises(RuntimeError):
        _ = uow.audit_logs
    with pytest.raises(RuntimeError):
        _ = uow.candles
    with pytest.raises(RuntimeError):
        _ = uow.economic_events


@pytest.mark.asyncio
async def test_repeated_active_entry_is_rejected() -> None:
    session = FakeSession()
    uow = SqlAlchemyUnitOfWork(lambda: session)  # type: ignore[arg-type]

    async with uow:
        with pytest.raises(RuntimeError):
            await uow.__aenter__()


@pytest.mark.asyncio
async def test_work_after_commit_before_exception_rolls_back_open_transaction() -> None:
    session = FakeSession()
    uow = SqlAlchemyUnitOfWork(lambda: session)  # type: ignore[arg-type]

    async def commit_then_fail() -> None:
        async with uow:
            await uow.commit()
            _ = uow.system_state
            raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        await commit_then_fail()

    assert session.commits == 1
    assert session.rollbacks == 1
    assert session.closes == 1

```

### `tests/integration/test_database_and_api.py`

```python
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.domain.entities import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.value_objects import CurrencyPair
from app.main import create_app
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory
from app.services.system_state_service import SystemStateService


@pytest.mark.integration
@pytest.mark.asyncio
async def test_system_state_persists_in_postgresql(postgres_database_url: str) -> None:
    engine = create_engine(postgres_database_url)
    try:
        service = SystemStateService(build_uow_factory(create_session_factory(engine)))

        await service.enable_scanning(actor="integration-test")
        status = await service.get_full_status()

        assert status["scan_enabled"] is True
    finally:
        await engine.dispose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_unit_of_work_rolls_back_uncommitted_failure(postgres_database_url: str) -> None:
    engine = create_engine(postgres_database_url)
    key = f"rollback_{uuid4().hex}"
    try:
        uow_factory = build_uow_factory(create_session_factory(engine))

        async def fail_inside_unit_of_work() -> None:
            async with uow_factory() as uow:
                await uow.system_state.set(key, {"value": "should_not_persist"})
                raise RuntimeError("force rollback")

        with pytest.raises(RuntimeError):
            await fail_inside_unit_of_work()

        async with uow_factory() as uow:
            value = await uow.system_state.get(key)

        assert value is None
    finally:
        await engine.dispose()


@pytest.mark.integration
def test_api_health_readiness_status_and_scan_state(postgres_database_url: str) -> None:
    settings = Settings(_env_file=None, database_url=postgres_database_url)
    app = create_app(settings)

    with TestClient(app) as client:
        health = client.get("/health")
        ready = client.get("/ready")
        status = client.get("/api/v1/system/status")
        start = client.post(
            "/api/v1/system/scanning/start",
            headers={"X-Internal-API-Key": settings.internal_api_key.get_secret_value()},
        )
        stop = client.post(
            "/api/v1/system/scanning/stop",
            headers={"X-Internal-API-Key": settings.internal_api_key.get_secret_value()},
        )

    assert health.status_code == 200
    assert health.json() == {"status": "alive", "service": "api"}
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
    assert status.status_code == 200
    assert status.json()["project_phase"] == "phase_3a_data_quality_foundation"
    assert status.json()["trading_strategy_implemented"] is False
    assert status.json()["real_trading_enabled"] is False
    assert start.status_code == 200
    assert start.json()["scan_enabled"] is True
    assert stop.status_code == 200
    assert stop.json()["scan_enabled"] is False


@pytest.mark.integration
def test_state_changing_endpoint_requires_internal_api_key(postgres_database_url: str) -> None:
    settings = Settings(_env_file=None, database_url=postgres_database_url)
    app = create_app(settings)

    with TestClient(app) as client:
        response = client.post("/api/v1/system/scanning/start")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_market_and_calendar_repositories_upsert_and_query(
    postgres_database_url: str,
) -> None:
    engine = create_engine(postgres_database_url)
    try:
        uow_factory = build_uow_factory(create_session_factory(engine))
        pair = CurrencyPair(value="EURUSD")
        candle = Candle(
            provider="integration",
            pair=pair,
            timeframe=Timeframe.M15,
            open_time=datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
            close_time=datetime(2026, 7, 8, 8, 15, tzinfo=UTC),
            open=Decimal("1.1000"),
            high=Decimal("1.1050"),
            low=Decimal("1.0950"),
            close=Decimal("1.1020"),
            volume=Decimal("100"),
            is_closed=True,
        )
        updated_candle = candle.model_copy(update={"close": Decimal("1.1030")})
        event = EconomicEvent(
            provider="integration",
            provider_event_id=f"event-{uuid4().hex}",
            title="Consumer Price Index",
            currency="EUR",
            country="Eurozone",
            impact=EconomicImpact.HIGH,
            scheduled_at=datetime(2026, 7, 8, 8, 5, tzinfo=UTC),
            actual=Decimal("2.2"),
            forecast=Decimal("2.1"),
            previous=Decimal("2.0"),
            fetched_at=datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
        )
        updated_event = event.model_copy(update={"actual": Decimal("2.3")})

        async with uow_factory() as uow:
            candle_insert = await uow.candles.upsert_many([candle])
            candle_update = await uow.candles.upsert_many([updated_candle])
            event_insert = await uow.economic_events.upsert_many([event])
            event_update = await uow.economic_events.upsert_many([updated_event])
            await uow.commit()

        async with uow_factory() as uow:
            candles = await uow.candles.list_range(
                pair=pair,
                timeframe=Timeframe.M15,
                start_at=datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
                end_at=datetime(2026, 7, 8, 8, 15, tzinfo=UTC),
                provider="integration",
            )
            events = await uow.economic_events.list_window(
                start_at=datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
                end_at=datetime(2026, 7, 8, 8, 15, tzinfo=UTC),
                currencies=["EUR"],
                provider="integration",
            )

        assert candle_insert.inserted == 1
        assert candle_update.updated == 1
        assert event_insert.inserted == 1
        assert event_update.updated == 1
        assert [stored.close for stored in candles] == [Decimal("1.1030000000")]
        assert [stored.actual for stored in events] == [Decimal("2.300000")]
    finally:
        await engine.dispose()

```

## Documentation Files Changed

### `AGENTS.md`

```markdown
# AI Trading OS Agent Guide

AI Trading OS is a foundation for a future Forex analysis and paper-trading platform.

Current project phase: phase_3a_data_quality_foundation.
Phase 3A is limited to deterministic data storage, data-quality, feature-snapshot, and historical
replay foundations. External integrations are disabled by default. The project contains no strategy,
no signals, no broker order APIs, and no real trading.

## Start and Checks

- Install: `uv sync`
- Start Docker stack: `docker compose up --build`
- Migrate: `uv run alembic upgrade head`
- Test: `uv run pytest`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Type-check: `uv run mypy app`
- Full check: `make check`

## Repository Layout

- `app/api`: API adapters.
- `app/services`: application services.
- `app/domain`: domain value objects and contracts.
- `app/persistence`: database models, repositories, unit of work.
- `app/telegram`: Telegram adapter.
- `app/scheduler`: worker process.
- `docs`: detailed project documentation.

## Rules

- Dependency direction is adapters -> application services -> domain.
- Domain code must not import FastAPI, Telegram, SQLAlchemy, PostgreSQL, APScheduler, OpenAI, market-data providers, or calendar providers.
- Use async SQLAlchemy sessions only; one `AsyncSession` per unit of work or task.
- Use `Decimal` for financial values. Do not use binary floating point for money, prices, percentages, or risk.
- Store timestamps in UTC; present user-facing time in Europe/Stockholm when needed.
- Telegram user-facing text must be Russian.
- Every Telegram message must contain exactly one semantic emoji at the beginning.
- Never add real trading execution, broker order APIs, real account credentials, or live position management.
- Never fabricate market data, calendar data, agent evidence, or scan results.
- LLM output may explain deterministic results only; it must not change prices, scores, risk, or rejected decisions.
- Update documentation when architecture or safety boundaries change.

## Definition of Done

Code is complete only when tests, formatting, linting, type checking, migrations, and relevant Docker checks have been run or a truthful limitation is documented in `docs/foundation-report.md`.

```

### `PLANS.md`

```markdown
# AI Trading OS Plans

## Completed Foundation Scope

- Project metadata and uv-compatible dependency management.
- FastAPI health, readiness, system status, and scanning-state endpoints.
- Async PostgreSQL models, Alembic migration, repositories, and unit of work.
- Worker process with heartbeat and health-check jobs.
- Telegram disabled mode, authorization, Russian text validation, and one-emoji formatting.
- Future provider and agent contracts without live calls or analysis.
- Safety scan for forbidden real-order execution concepts.
- Documentation and tests for foundation behavior.
- Phase 2 foundation hardening: Docker runtime defaults, internal API key security, redaction,
  UTC normalization, UoW lifecycle hardening, architecture boundary tests, typed provider
  contracts, disabled adapters, production Twelve Data/FMP adapters, and MockTransport-backed
  provider contract tests.
- Phase 3A data-quality foundation: duplicate-safe candle/event storage repositories,
  deterministic data-quality snapshots, and historical replay utilities for tests.

## Current Implementation Status

The repository has completed the foundation phase, Phase 2 hardening/data adapters, and Phase 3A
data-quality foundation. Production Twelve Data and FMP adapters exist, but live integrations remain
disabled by default. Scanning state can be enabled or disabled, but no analytical engine is
connected.

## Future Phases

- Phase 2: market-data and calendar adapters — completed as disabled-by-default factories plus
  production adapters covered by MockTransport-backed contract tests
- Phase 3A: data-quality foundation — completed without trading analysis or decisions
- Phase 3B: feature engine and deterministic analysis
- Phase 4: analytical agents and Decision Engine
- Phase 5: Russian Chief AI explanations
- Phase 6: Telegram signal delivery
- Phase 7: backtesting and paper trading

## Explicit Non-Goals

- No broker execution.
- No real trading.
- No strategy logic.
- No indicators or signal generation.
- No OpenAI calls.
- No fabricated market data or scan results.

## Known Risks

- Local Docker or PostgreSQL availability can affect verification.
- Future provider adapters must preserve disabled-by-default behavior.
- Telegram message validation is intentionally simple and should be tightened as message complexity grows.

## Next Planned Task

Phase 3B should add a feature-engine foundation for deterministic closed-candle feature extraction
without signal generation, scoring, or trading recommendations.

```

### `README.md`

```markdown
# AI Trading OS

AI Trading OS is a safety-first foundation for a future modular Forex analysis and paper-trading platform. The current repository implements only infrastructure: API health/status endpoints, async PostgreSQL persistence, a scheduler heartbeat, Telegram command foundations, strict configuration, and safety contracts.

## Current Status

- Current project phase: phase_3a_data_quality_foundation.
- Trading strategy: not implemented.
- Real trading: disabled and unsupported.
- External integrations: disabled by default.
- Telegram: can run in disabled mode without a token.
- Phase 3A: deterministic data-quality foundation only.

## Safety Warning

This project must not open, modify, or close real financial positions. It contains no broker order API, no real account credentials, and no automatic trading execution.

## Phase 2 Status

Phase 2 adds hardened runtime defaults, stronger secret redaction, strict UTC normalization, typed
`Candle` and `EconomicEvent` domain models, typed provider contracts, disabled-by-default provider
adapters, production Twelve Data and FMP adapters tested through `httpx.MockTransport`, and
architecture/safety verification. It still does not add strategy, indicators, analysis, signals,
OpenAI calls, or trading execution.

## Phase 3A Status

Phase 3A adds duplicate-safe storage/query repositories for normalized closed candles and economic
events, deterministic data-quality snapshots, and historical replay utilities for tests. It does not
add strategy, indicators, technical analysis, scoring, signals, AI agents, OpenAI calls, paper
trading, broker APIs, order execution, or real trading.

## Prerequisites

- Python 3.12
- uv
- Docker and Docker Compose
- PostgreSQL for local non-Docker development

## Mac and Linux Setup

```bash
uv sync
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:create_app --factory --reload
```

## Windows Setup

Use PowerShell with Python 3.12 and uv installed:

```powershell
uv sync
Copy-Item .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:create_app --factory --reload
```

## Docker Startup

The default configuration starts without paid API keys. Compose uses `.env` as an optional
local override file and does not use `.env.example` at runtime:

```bash
docker compose up --build
```

The Compose stack runs PostgreSQL, applies Alembic migrations, starts the API, starts the worker, and starts the Telegram process in disabled mode when `TELEGRAM_ENABLED=false`.

## Environment Configuration

Copy `.env.example` to `.env` for local overrides. The example keeps:

```text
TELEGRAM_ENABLED=false
OPENAI_ENABLED=false
MARKET_DATA_ENABLED=false
CALENDAR_ENABLED=false
SCAN_ENABLED=false
```

Secrets are required only when the matching integration is enabled.

## Migrations

```bash
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "message"
```

## Tests and Checks

```bash
make check
make test
make lint
make typecheck
```

Integration tests require a reachable `TEST_DATABASE_URL`; otherwise they skip with a clear message.

## API Endpoints

- `GET /health`
- `GET /ready`
- `GET /api/v1/system/status`
- `POST /api/v1/system/scanning/start`
- `POST /api/v1/system/scanning/stop`

State-changing endpoints require the `X-Internal-API-Key` header.
The default development key is rejected when `APP_ENV` is not `development`.

## Telegram Disabled Mode

When `TELEGRAM_ENABLED=false`, the bot process starts and remains healthy without creating a Telegram client or making network calls. When enabled, a bot token, allowed user ID, and allowed chat ID are required.

## Current Limitations

- No strategy, indicators, signals, OpenAI calls, backtesting, position sizing, broker execution, or real trading.
- `/scan_now` explicitly reports that the analytical engine is not implemented.
- Worker jobs only update heartbeat and run foundation health checks.

## Directory Overview

- `app/api`: FastAPI adapters.
- `app/core`: configuration, errors, logging, time, security, enums.
- `app/domain`: provider and repository contracts plus financial value objects.
- `app/persistence`: SQLAlchemy models, repositories, unit of work.
- `app/services`: application services.
- `app/telegram`: Telegram authorization, formatting, commands, delivery.
- `app/scheduler`: worker process and jobs.
- `docs`: product, architecture, database, operations, and implementation notes.
- `tests`: unit, integration, and contract tests.

```
