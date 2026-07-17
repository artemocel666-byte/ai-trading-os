# ChatGPT Verification Packet: Phase 3I Persistent Digest Delivery Audit Foundation

Generated: 2026-07-15T18:57:41Z

## Repository Metadata

- Repository path: `/Users/artem.otsel/Documents/ai-trading-os`
- Git branch: `main`
- Current commit hash: `901d86411d01217b6b1ca0c7fd7e694621159577`
- Local latest commit: `901d864 Phase 3H Done`
- Prompt expected latest commit: `141ef71 Add Phase 3H scheduled digest delivery foundation`
- Baseline note: the prompt's expected Phase 3H commit did not match the local repository. The local repository was clean at `901d864 Phase 3H Done`, and Phase 3I work continued from that actual state.
- Commit status: Phase 3I remains uncommitted at packet generation time.

## Git Status Short

```text
 M AGENTS.md
 M PLANS.md
 M README.md
 M app/core/constants.py
 M app/domain/entities/scheduled_digest.py
 M app/domain/interfaces/notifications.py
 M app/domain/interfaces/unit_of_work.py
 M app/persistence/models/__init__.py
 M app/persistence/models/foundation.py
 M app/persistence/repositories/__init__.py
 M app/persistence/repositories/foundation.py
 M app/persistence/unit_of_work.py
 M app/services/scheduled_digest_delivery_service.py
 M docs/chatgpt-verification-packet.md
 M docs/database-schema.md
 M docs/operations.md
 M tests/contract/test_safety_boundaries.py
 M tests/fakes.py
 M tests/integration/test_database_and_api.py
 M tests/unit/test_analysis_snapshot_foundation.py
 M tests/unit/test_readiness_scheduler_foundation.py
 M tests/unit/test_scheduled_digest_delivery_foundation.py
?? docs/phase3i-verification-report.md
?? migrations/versions/0003_phase3i_scheduled_digest_deliveries.py
```

## Git Diff Stat

```text
 AGENTS.md                                          |   14 +-
 PLANS.md                                           |   18 +-
 README.md                                          |   13 +-
 app/core/constants.py                              |    2 +-
 app/domain/entities/scheduled_digest.py            |    8 +
 app/domain/interfaces/notifications.py             |    6 +
 app/domain/interfaces/unit_of_work.py              |    6 +
 app/persistence/models/__init__.py                 |    2 +
 app/persistence/models/foundation.py               |   36 +
 app/persistence/repositories/__init__.py           |    2 +
 app/persistence/repositories/foundation.py         |   69 +
 app/persistence/unit_of_work.py                    |   11 +
 app/services/scheduled_digest_delivery_service.py  |   22 +
 docs/chatgpt-verification-packet.md                | 3700 +++++++++++---------
 docs/database-schema.md                            |   11 +
 docs/operations.md                                 |    6 +
 tests/contract/test_safety_boundaries.py           |   43 +
 tests/fakes.py                                     |   33 +-
 tests/integration/test_database_and_api.py         |  220 +-
 tests/unit/test_analysis_snapshot_foundation.py    |    4 +-
 tests/unit/test_readiness_scheduler_foundation.py  |    2 +-
 .../test_scheduled_digest_delivery_foundation.py   |   13 +-
 22 files changed, 2631 insertions(+), 1610 deletions(-)
```

## Git Log

```text
901d864 Phase 3H Done
ab4aafb phase 3G done
40473bd Add Phase 3F readiness scheduler foundation
588ab6a Phase 3E DONE
8166820 phase 3C DONE
60e6e53 Add Phase 3C indicator context foundation
a6f44f0 Add Phase 3B feature engine foundation
03c3acd Add Phase 3A data quality foundation
9d68709 Document Phase 2 runtime verification
```

## Created Files

- `docs/phase3i-verification-report.md`
- `migrations/versions/0003_phase3i_scheduled_digest_deliveries.py`

## Modified Files

- `AGENTS.md`
- `PLANS.md`
- `README.md`
- `app/core/constants.py`
- `app/domain/entities/scheduled_digest.py`
- `app/domain/interfaces/notifications.py`
- `app/domain/interfaces/unit_of_work.py`
- `app/persistence/models/__init__.py`
- `app/persistence/models/foundation.py`
- `app/persistence/repositories/__init__.py`
- `app/persistence/repositories/foundation.py`
- `app/persistence/unit_of_work.py`
- `app/services/scheduled_digest_delivery_service.py`
- `docs/chatgpt-verification-packet.md`
- `docs/database-schema.md`
- `docs/operations.md`
- `tests/contract/test_safety_boundaries.py`
- `tests/fakes.py`
- `tests/integration/test_database_and_api.py`
- `tests/unit/test_analysis_snapshot_foundation.py`
- `tests/unit/test_readiness_scheduler_foundation.py`
- `tests/unit/test_scheduled_digest_delivery_foundation.py`

## Migration Files Created Or Modified

- `migrations/versions/0003_phase3i_scheduled_digest_deliveries.py`

## Phase Scope Confirmation

Phase 3I is persistent digest delivery audit foundation only. It stores neutral scheduled digest delivery deduplication keys and non-sensitive metadata.

Phase 4 was not started. No strategy implementation, trade signals, setup scoring, confidence scoring, AI agents, OpenAI calls, broker APIs, paper trading, order execution, or real trading were added.

Scheduled delivery remains disabled by default. Telegram output remains neutral readiness/reporting text only. Provider/network integrations remain disabled by default.

## Implementation Summary

- Updated `PROJECT_PHASE` to `phase_3i_persistent_digest_audit_foundation`.
- Added neutral `scheduled_digest_deliveries` database table with unique `dedup_key`, project phase, UTC delivery time, sender name, readiness status/counts, item summary, and payload preview.
- Added SQLAlchemy model and repository implementing the existing domain store protocol.
- Updated persistent audit recording to use PostgreSQL `ON CONFLICT DO NOTHING` on the unique dedup key.
- Added UoW access to the persistent delivery audit store without coupling domain code to SQLAlchemy.
- Extended scheduled digest delivery records with neutral audit fields.
- Updated delivery service to populate audit metadata and still support the in-memory store.
- Added repeatable PostgreSQL integration cleanup and tests for persistent duplicate skipping.
- Updated README, AGENTS, PLANS, operations, database schema, Phase 3I report, and this packet.

## Exact Verification Command Outputs

### Host Checks

The requested `uv ...` checks were executed with `/Users/artem.otsel/.local/bin` prepended to PATH because this Codex shell does not include that directory by default. This is an environment path detail, not a project failure.

### `uv lock --check`

Command: `uv lock --check`

Exit code: `0`

```text
Resolved 46 packages in 29ms
```

### `uv sync`

Command: `uv sync`

Exit code: `0`

```text
Resolved 46 packages in 2ms
Checked 43 packages in 7ms
```

### `uv run ruff format --check .`

Command: `uv run ruff format --check .`

Exit code: `0`

```text
109 files already formatted
```

### `uv run ruff check .`

Command: `uv run ruff check .`

Exit code: `0`

```text
All checks passed!
```

### `uv run mypy app`

Command: `uv run mypy app`

Exit code: `0`

```text
Success: no issues found in 77 source files
```

### `uv run pytest`

Command: `uv run pytest`

Exit code: `0`

```text
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/artem.otsel/Documents/ai-trading-os
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.14.1, asyncio-0.26.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 219 items

tests/contract/test_agent_contracts.py ......                            [  2%]
tests/contract/test_api_error_schema.py .                                [  3%]
tests/contract/test_architecture_boundaries.py ..                        [  4%]
tests/contract/test_provider_contracts.py .............................. [ 17%]
...............................                                          [ 31%]
tests/contract/test_safety_boundaries.py ................                [ 39%]
tests/integration/test_database_and_api.py sssssss                       [ 42%]
tests/unit/test_analysis_snapshot_foundation.py ..........               [ 47%]
tests/unit/test_context_engine_foundation.py .............               [ 52%]
tests/unit/test_data_quality_foundation.py ...                           [ 54%]
tests/unit/test_domain_market_models.py ..................               [ 62%]
tests/unit/test_errors_and_redaction.py .......                          [ 65%]
tests/unit/test_feature_engine_foundation.py ...........                 [ 70%]
tests/unit/test_internal_api_key.py ....                                 [ 72%]
tests/unit/test_readiness_scheduler_foundation.py .........              [ 76%]
tests/unit/test_scheduled_digest_delivery_foundation.py ...........      [ 81%]
tests/unit/test_settings.py .........                                    [ 85%]
tests/unit/test_system_state_service.py .....                            [ 88%]
tests/unit/test_telegram_commands.py ........                            [ 91%]
tests/unit/test_telegram_policy.py .....                                 [ 94%]
tests/unit/test_time.py ...                                              [ 95%]
tests/unit/test_unit_of_work_lifecycle.py ......                         [ 98%]
tests/unit/test_value_objects_and_enums.py ....                          [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /Users/artem.otsel/Documents/ai-trading-os/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================== 212 passed, 7 skipped, 1 warning in 0.77s ===================
```

### `uv run python scripts/security_check.py`

Command: `uv run python scripts/security_check.py`

Exit code: `0`

```text
<no output>
```

### Docker And PostgreSQL Checks

### `docker compose build`

Command: `docker compose build`

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

#3 [migrate internal] load metadata for ghcr.io/astral-sh/uv:python3.12-bookworm-slim
#3 DONE 1.1s

#4 [migrate internal] load .dockerignore
#4 transferring context: 143B done
#4 DONE 0.0s

#5 [bot 1/5] FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58
#5 resolve ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58 0.0s done
#5 DONE 0.0s

#6 [migrate internal] load build context
#6 transferring context: 282.09kB 0.0s done
#6 DONE 0.0s

#7 [bot 2/5] WORKDIR /app
#7 CACHED

#8 [bot 3/5] COPY pyproject.toml uv.lock* ./
#8 CACHED

#9 [bot 4/5] RUN uv sync --frozen --no-dev
#9 CACHED

#10 [api 5/5] COPY . .
#10 DONE 0.0s

#11 [migrate] exporting to image
#11 exporting layers 0.1s done
#11 exporting manifest sha256:7b38c8e56b4309f37915bd25d364bf139d9ee91e958ad09aee5ae825f0d51c43
#11 exporting manifest sha256:7b38c8e56b4309f37915bd25d364bf139d9ee91e958ad09aee5ae825f0d51c43 done
#11 exporting config sha256:8baa40577815966189bc7275e733ee3bb9cf0a66ae84635cd37986b791252b58 done
#11 exporting attestation manifest sha256:1bee49ba4b51956108c4dce9833046b4fa7698f31935c2e99fe34ae0df8b5e96 0.0s done
#11 exporting manifest list sha256:9015244eaf111398cd2fda7da43591646217e7fc19b5ebd9ddca78d9ff41ad95 done
#11 naming to docker.io/library/ai-trading-os-migrate:latest done
#11 unpacking to docker.io/library/ai-trading-os-migrate:latest 0.0s done
#11 DONE 0.2s

#12 [api] exporting to image
#12 exporting layers 0.1s done
#12 exporting manifest sha256:df22c64aaf398dd52f8a4de626ca06a5bd8dfbc6b6d851324571cc7db939d6f4 done
#12 exporting config sha256:3d711e92c7c74a657dea25edf1f1dff92a145d874844723f5539570bc09cde42 done
#12 exporting attestation manifest sha256:02c1138b53859051cfaddc40af9611b934ad1050530c13d231e218ab9f528b06 0.0s done
#12 exporting manifest list sha256:f4e6254ff395bd0903a5c92da9fc44303d6376462db411984ac20390bbfe7131 done
#12 naming to docker.io/library/ai-trading-os-api:latest done
#12 unpacking to docker.io/library/ai-trading-os-api:latest 0.0s done
#12 DONE 0.2s

#13 [worker] exporting to image
#13 exporting layers 0.1s done
#13 exporting manifest sha256:5ed933efc1c91e727cacfa31822a7e61eeb727182822b1c88fc2bec6b5d8602d done
#13 exporting config sha256:4389d788547b67c484a8480fb8f9b183c62b9177c15c69424bc646738dc1c722 done
#13 exporting attestation manifest sha256:c1062b6d5164094fb902ec9d986a56e9b2ef463e11894262fc893bb4f80cb6e3 0.0s done
#13 exporting manifest list sha256:262d1ad75deb3c479657c2a4fc9b48f780eb18a7a32628e3622d6ad44da2a917 done
#13 naming to docker.io/library/ai-trading-os-worker:latest done
#13 unpacking to docker.io/library/ai-trading-os-worker:latest 0.0s done
#13 DONE 0.2s

#14 [bot] exporting to image
#14 exporting layers 0.1s done
#14 exporting manifest sha256:f137c746dad4dda50c473a34b2e81b888783794aadb2570bc93e2eb180da0d02 done
#14 exporting config sha256:7d1be4ac4752056dbd3a4967216de3b58551aa3b55446945a9c120eb12739b5c done
#14 exporting attestation manifest sha256:41c8f183518d0614dd6e1f8d77345ff9ec3c676652585b91494fd3adc3596bc6 0.0s done
#14 exporting manifest list sha256:502f3b5424b1360a5ab74cd10271cdc2eab970290c9fbac4354227af8ed949a4 done
#14 naming to docker.io/library/ai-trading-os-bot:latest done
#14 unpacking to docker.io/library/ai-trading-os-bot:latest 0.0s done
#14 DONE 0.2s

#15 [migrate] resolving provenance for metadata file
#15 DONE 0.0s

#16 [worker] resolving provenance for metadata file
#16 DONE 0.0s

#17 [bot] resolving provenance for metadata file
#17 DONE 0.0s

#18 [api] resolving provenance for metadata file
#18 DONE 0.0s
 Image ai-trading-os-bot Built 
 Image ai-trading-os-migrate Built 
 Image ai-trading-os-worker Built 
 Image ai-trading-os-api Built
```

### `docker compose up -d postgres`

Command: `docker compose up -d postgres`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running
```

### `docker compose ps postgres`

Command: `docker compose ps postgres`

Exit code: `0`

```text
NAME                       IMAGE                COMMAND                  SERVICE    CREATED          STATUS                    PORTS
ai-trading-os-postgres-1   postgres:16-alpine   "docker-entrypoint.s…"   postgres   19 minutes ago   Up 19 minutes (healthy)   5432/tcp
```

### `docker compose run --rm migrate alembic current`

Command: `docker compose run --rm migrate alembic current`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-737bbe8e5ebd Creating 
 Container ai-trading-os-migrate-run-737bbe8e5ebd Created 
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
0003_phase3i_digest_audit (head)
```

### `docker compose run --rm migrate alembic check`

Command: `docker compose run --rm migrate alembic check`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-501ef29f5f68 Creating 
 Container ai-trading-os-migrate-run-501ef29f5f68 Created 
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

### `docker compose run --rm -e DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate alembic upgrade head`

Command: `docker compose run --rm -e DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate alembic upgrade head`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-84ab7a3e018d Creating 
 Container ai-trading-os-migrate-run-84ab7a3e018d Created 
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

### `Docker integration run 1: docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py`

Command: `docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-a9aa9bf0d333 Creating 
 Container ai-trading-os-migrate-run-a9aa9bf0d333 Created 
Downloading ruff (10.5MiB)
Downloading mypy (13.1MiB)
Downloading pygments (1.2MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 112ms
Bytecode compiled 1963 files in 449ms
============================= test session starts ==============================
platform linux -- Python 3.12.12, pytest-8.4.2, pluggy-1.6.0
rootdir: /app
configfile: pyproject.toml
plugins: anyio-4.14.1, asyncio-0.26.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 7 items

tests/integration/test_database_and_api.py .......                       [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /app/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
========================= 7 passed, 1 warning in 0.37s =========================
```

### `Docker integration run 2: docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py`

Command: `docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-14e2ee8cf490 Creating 
 Container ai-trading-os-migrate-run-14e2ee8cf490 Created 
Downloading pygments (1.2MiB)
Downloading ruff (10.5MiB)
Downloading mypy (13.1MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 44ms
Bytecode compiled 1963 files in 410ms
============================= test session starts ==============================
platform linux -- Python 3.12.12, pytest-8.4.2, pluggy-1.6.0
rootdir: /app
configfile: pyproject.toml
plugins: anyio-4.14.1, asyncio-0.26.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 7 items

tests/integration/test_database_and_api.py .......                       [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /app/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
========================= 7 passed, 1 warning in 0.37s =========================
```

### `docker compose config`

Command: `docker compose config`

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

### Superseded Pre-Upgrade Docker Audit Note

Before applying the new Phase 3I migration to the main Docker database, an initial `alembic current` showed `0002_phase2_data_constraints`, and an initial `alembic check` failed with:

```text
FAILED: Target database is not up to date.
ERROR [alembic.util.messaging] Target database is not up to date.
```

That was a pre-upgrade state, not the final status. After running the migration, `alembic current` returned `0003_phase3i_digest_audit (head)` and `alembic check` returned `No new upgrade operations detected.`

## Skipped Checks

- Host `uv run pytest` skipped 7 integration tests because host integration tests require `REQUIRE_INTEGRATION_TESTS=true` and a PostgreSQL integration database. The same integration file was run in Docker twice with `REQUIRE_INTEGRATION_TESTS=true`, and both runs passed.

## Unavailable Checks

- None for the requested Phase 3I verification set. Docker Desktop, PostgreSQL container, Alembic, and integration tests were available and run.

## Remaining Risks

- Phase 3I stores audit metadata only; production scheduled delivery remains disabled by default and was not activated end-to-end against a live Telegram service.
- The Docker integration suite validates repository persistence and duplicate skipping against PostgreSQL, but it does not send real Telegram messages.
- Existing inactive signal/trading/paper tables remain present from prior foundation work but were not activated or used for decision-making.

## Traceability

| Requirement | Implementation file | Test file | Verification result |
| --- | --- | --- | --- |
| Update project phase to Phase 3I | `app/core/constants.py` | `tests/unit/test_analysis_snapshot_foundation.py`, `tests/unit/test_readiness_scheduler_foundation.py`, `tests/integration/test_database_and_api.py` | Host pytest passed; Docker integration status coverage passed |
| Persist neutral scheduled digest delivery audit records | `migrations/versions/0003_phase3i_scheduled_digest_deliveries.py`, `app/persistence/models/foundation.py` | `tests/integration/test_database_and_api.py` | Docker Alembic upgrade/current/check passed; Docker integration tests passed twice |
| Implement SQLAlchemy-backed `ScheduledDigestDeliveryStore` | `app/persistence/repositories/foundation.py`, `app/persistence/unit_of_work.py` | `tests/integration/test_database_and_api.py` | Repository insert/get/exists coverage passed in Docker |
| Make duplicate recording conflict-safe | `app/persistence/repositories/foundation.py` | `tests/integration/test_database_and_api.py` | Duplicate direct record with changed metadata did not overwrite first audit row; Docker integration passed twice |
| Preserve in-memory store behavior | `app/services/scheduled_digest_delivery_service.py` | `tests/unit/test_scheduled_digest_delivery_foundation.py` | Host pytest passed |
| Duplicate-safe delivery skip survives persistence | `app/services/scheduled_digest_delivery_service.py`, `app/persistence/repositories/foundation.py` | `tests/integration/test_database_and_api.py` | Docker integration tests passed twice against the same DB |
| UTC-normalized persisted timestamps | `app/domain/entities/scheduled_digest.py`, `app/persistence/repositories/foundation.py` | `tests/integration/test_database_and_api.py` | Host and Docker tests passed |
| Existing `/snapshot` and `/digest` commands still work | Existing Telegram command handlers | `tests/unit/test_telegram_commands.py` | Host pytest passed |
| Scheduled delivery remains disabled by default | Settings and compose defaults, documented in README/operations | `docker compose config` | Config output shows integrations and Telegram disabled defaults |
| Safety boundary: no strategy/signals/scoring/AI/broker/order execution | No Phase 4 code added | `tests/contract/test_safety_boundaries.py`, `scripts/security_check.py` | Contract safety tests and security check passed |

## Full Migration Contents

### `migrations/versions/0003_phase3i_scheduled_digest_deliveries.py`

```python
"""phase3i scheduled digest delivery audit

Revision ID: 0003_phase3i_digest_audit
Revises: 0002_phase2_data_constraints
Create Date: 2026-07-15 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_phase3i_digest_audit"
down_revision: str | None = "0002_phase2_data_constraints"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "scheduled_digest_deliveries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dedup_key", sa.String(length=64), nullable=False),
        sa.Column("project_phase", sa.String(length=120), nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sender_name", sa.String(length=120), nullable=False),
        sa.Column("readiness_status", sa.String(length=20), nullable=True),
        sa.Column("item_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("ready_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("incomplete_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("blocked_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("items_summary", sa.String(length=500), nullable=True),
        sa.Column("payload_preview", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dedup_key", name="uq_scheduled_digest_deliveries_dedup_key"),
        sa.CheckConstraint("item_count >= 0", name="ck_scheduled_digest_item_count_non_negative"),
        sa.CheckConstraint("ready_count >= 0", name="ck_scheduled_digest_ready_count_non_negative"),
        sa.CheckConstraint(
            "incomplete_count >= 0",
            name="ck_scheduled_digest_incomplete_count_non_negative",
        ),
        sa.CheckConstraint(
            "blocked_count >= 0",
            name="ck_scheduled_digest_blocked_count_non_negative",
        ),
    )
    op.create_index(
        "ix_scheduled_digest_deliveries_delivered_at",
        "scheduled_digest_deliveries",
        ["delivered_at"],
    )
    op.create_index(
        "ix_scheduled_digest_deliveries_project_phase",
        "scheduled_digest_deliveries",
        ["project_phase"],
    )
    op.create_index(
        "ix_scheduled_digest_deliveries_readiness_status",
        "scheduled_digest_deliveries",
        ["readiness_status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_scheduled_digest_deliveries_readiness_status",
        table_name="scheduled_digest_deliveries",
    )
    op.drop_index(
        "ix_scheduled_digest_deliveries_project_phase",
        table_name="scheduled_digest_deliveries",
    )
    op.drop_index(
        "ix_scheduled_digest_deliveries_delivered_at",
        table_name="scheduled_digest_deliveries",
    )
    op.drop_table("scheduled_digest_deliveries")
```


## Full Contents Of Changed Source Files

### `app/core/constants.py`

```python
PROJECT_PHASE = "phase_3i_persistent_digest_audit_foundation"
STRATEGY_IMPLEMENTED = False
REAL_TRADING_ENABLED = False

SYSTEM_STATE_SCAN_ENABLED = "scan_enabled"
SYSTEM_STATE_WORKER_HEARTBEAT = "worker_heartbeat"
SYSTEM_STATE_LAST_SUCCESSFUL_MARKET_FETCH = "last_successful_market_fetch"
SYSTEM_STATE_LAST_SUCCESSFUL_CALENDAR_FETCH = "last_successful_calendar_fetch"
SYSTEM_STATE_LAST_ERROR = "last_error"

DEFAULT_STRATEGY_VERSION = "foundation-v1"
```

### `app/domain/entities/scheduled_digest.py`

```python
from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core import constants
from app.core.time import normalize_to_utc
from app.domain.entities.readiness import (
    SnapshotDigestStatus,
    SnapshotNotificationDedupKey,
    SnapshotNotificationPayload,
    SnapshotScheduleItem,
)


class ScheduledDigestDecisionReason(StrEnum):
    DISABLED = "DISABLED"
    NOT_DUE = "NOT_DUE"
    DUE = "DUE"
    DUPLICATE = "DUPLICATE"
    NO_ITEMS = "NO_ITEMS"
    BUILD_FAILED = "BUILD_FAILED"
    DELIVERED = "DELIVERED"


class ScheduledDigestConfig(BaseModel):
    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    enabled: bool = False
    interval_minutes: int = Field(default=60, ge=1, le=1440)
    items: tuple[SnapshotScheduleItem, ...] = ()

    model_config = ConfigDict(frozen=True)


class ScheduledDigestTick(BaseModel):
    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    as_of: datetime

    model_config = ConfigDict(frozen=True)

    @field_validator("as_of")
    @classmethod
    def as_of_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)


class ScheduledDigestDecision(BaseModel):
    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    enabled: bool
    is_due: bool
    should_build: bool
    reason: ScheduledDigestDecisionReason
    item_count: int = Field(ge=0)
    tick_as_of: datetime
    dedup_key: SnapshotNotificationDedupKey | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("tick_as_of")
    @classmethod
    def tick_as_of_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        if self.should_build and not self.is_due:
            raise ValueError("scheduled digest cannot build when tick is not due")
        if self.should_build and not self.enabled:
            raise ValueError("scheduled digest cannot build while disabled")
        return self


class ScheduledDigestDeliveryRecord(BaseModel):
    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    dedup_key: SnapshotNotificationDedupKey
    delivered_at: datetime
    sender_name: str = Field(min_length=1)
    readiness_status: SnapshotDigestStatus | None = None
    item_count: int = Field(default=0, ge=0)
    ready_count: int = Field(default=0, ge=0)
    incomplete_count: int = Field(default=0, ge=0)
    blocked_count: int = Field(default=0, ge=0)
    items_summary: str | None = Field(default=None, max_length=500)
    payload_preview: str | None = Field(default=None, max_length=1000)

    model_config = ConfigDict(frozen=True)

    @field_validator("delivered_at")
    @classmethod
    def delivered_at_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)


class ScheduledDigestDeliveryResult(BaseModel):
    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    tick: ScheduledDigestTick
    decision: ScheduledDigestDecision
    delivered: bool
    skipped: bool
    dedup_key: SnapshotNotificationDedupKey | None = None
    payload: SnapshotNotificationPayload | None = None
    record: ScheduledDigestDeliveryRecord | None = None

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        if self.delivered == self.skipped:
            raise ValueError("scheduled digest result must be either delivered or skipped")
        if self.delivered and self.record is None:
            raise ValueError("delivered scheduled digest result requires a record")
        if self.skipped and self.record is not None:
            raise ValueError("skipped scheduled digest result must not include a record")
        return self
```

### `app/domain/interfaces/notifications.py`

```python
from typing import Protocol

from app.domain.entities.readiness import SnapshotNotificationDedupKey, SnapshotNotificationPayload
from app.domain.entities.scheduled_digest import ScheduledDigestDeliveryRecord


class NotificationSender(Protocol):
    async def send(self, payload: SnapshotNotificationPayload) -> None:
        """Deliver a neutral readiness notification payload."""


class ScheduledDigestDeliveryStore(Protocol):
    async def exists(self, dedup_key: SnapshotNotificationDedupKey) -> bool:
        """Return whether a scheduled digest deduplication key is already recorded."""

    async def record(self, record: ScheduledDigestDeliveryRecord) -> None:
        """Record a delivered scheduled digest deduplication key."""

    async def get(
        self,
        dedup_key: SnapshotNotificationDedupKey,
    ) -> ScheduledDigestDeliveryRecord | None:
        """Return one neutral scheduled digest delivery audit record when present."""
```

### `app/domain/interfaces/unit_of_work.py`

```python
from types import TracebackType
from typing import Protocol, Self

from app.domain.interfaces.notifications import ScheduledDigestDeliveryStore
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

    @property
    def scheduled_digest_deliveries(self) -> ScheduledDigestDeliveryStore:
        """Store for neutral scheduled digest delivery audit records."""
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

### `app/persistence/models/__init__.py`

```python
from app.persistence.models.foundation import (
    AgentReportModel,
    AuditLogModel,
    CandleModel,
    EconomicEventModel,
    ErrorEventModel,
    PaperPositionModel,
    ScanModel,
    ScheduledDigestDeliveryModel,
    SignalModel,
    SystemStateModel,
)

__all__ = [
    "AgentReportModel",
    "AuditLogModel",
    "CandleModel",
    "EconomicEventModel",
    "ErrorEventModel",
    "PaperPositionModel",
    "ScanModel",
    "ScheduledDigestDeliveryModel",
    "SignalModel",
    "SystemStateModel",
]
```

### `app/persistence/models/foundation.py`

```python
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.core.time import utc_now
from app.persistence.database import Base

JSONB_TYPE = postgresql.JSONB().with_variant(JSON(), "sqlite")
UUID_PK = Uuid(as_uuid=True)


class SystemStateModel(Base):
    __tablename__ = "system_state"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    value_json: Mapped[Any] = mapped_column(JSONB_TYPE, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID_PK, primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    entity_type: Mapped[str | None] = mapped_column(String(120))
    entity_id: Mapped[str | None] = mapped_column(String(120))
    actor: Mapped[str | None] = mapped_column(String(120))
    before_json: Mapped[Any | None] = mapped_column(JSONB_TYPE)
    after_json: Mapped[Any | None] = mapped_column(JSONB_TYPE)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )


class ErrorEventModel(Base):
    __tablename__ = "error_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID_PK, primary_key=True, default=uuid.uuid4)
    error_code: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    component: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    message_ru: Mapped[str] = mapped_column(String(500), nullable=False)
    technical_details: Mapped[str | None] = mapped_column(String(2000))
    context_json: Mapped[Any | None] = mapped_column(JSONB_TYPE)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )


class CandleModel(Base):
    __tablename__ = "candles"
    __table_args__ = (
        UniqueConstraint("provider", "pair", "timeframe", "open_time", name="uq_candle_identity"),
        CheckConstraint("open > 0", name="ck_candles_open_positive"),
        CheckConstraint("high > 0", name="ck_candles_high_positive"),
        CheckConstraint("low > 0", name="ck_candles_low_positive"),
        CheckConstraint("close > 0", name="ck_candles_close_positive"),
        CheckConstraint("close_time > open_time", name="ck_candles_close_after_open"),
        CheckConstraint("volume IS NULL OR volume >= 0", name="ck_candles_volume_non_negative"),
        CheckConstraint("is_closed = true", name="ck_candles_is_closed"),
        Index("ix_candles_pair_timeframe_close_time", "pair", "timeframe", "close_time"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID_PK, primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    pair: Mapped[str] = mapped_column(String(6), nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    open_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    close_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    open: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    volume: Mapped[Decimal | None] = mapped_column(Numeric(24, 8))
    is_closed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class EconomicEventModel(Base):
    __tablename__ = "economic_events"
    __table_args__ = (
        UniqueConstraint("provider", "provider_event_id", name="uq_economic_events_provider_event"),
        Index("ix_economic_events_currency_scheduled", "currency", "scheduled_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID_PK, primary_key=True, default=uuid.uuid4)
    provider_event_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    country: Mapped[str | None] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    impact: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    actual: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    forecast: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    previous: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    actual_raw: Mapped[str | None] = mapped_column(String(200))
    forecast_raw: Mapped[str | None] = mapped_column(String(200))
    previous_raw: Mapped[str | None] = mapped_column(String(200))
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ScheduledDigestDeliveryModel(Base):
    __tablename__ = "scheduled_digest_deliveries"
    __table_args__ = (
        UniqueConstraint("dedup_key", name="uq_scheduled_digest_deliveries_dedup_key"),
        CheckConstraint("item_count >= 0", name="ck_scheduled_digest_item_count_non_negative"),
        CheckConstraint("ready_count >= 0", name="ck_scheduled_digest_ready_count_non_negative"),
        CheckConstraint(
            "incomplete_count >= 0",
            name="ck_scheduled_digest_incomplete_count_non_negative",
        ),
        CheckConstraint(
            "blocked_count >= 0",
            name="ck_scheduled_digest_blocked_count_non_negative",
        ),
        Index("ix_scheduled_digest_deliveries_delivered_at", "delivered_at"),
        Index("ix_scheduled_digest_deliveries_project_phase", "project_phase"),
        Index("ix_scheduled_digest_deliveries_readiness_status", "readiness_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID_PK, primary_key=True, default=uuid.uuid4)
    dedup_key: Mapped[str] = mapped_column(String(64), nullable=False)
    project_phase: Mapped[str] = mapped_column(String(120), nullable=False)
    delivered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sender_name: Mapped[str] = mapped_column(String(120), nullable=False)
    readiness_status: Mapped[str | None] = mapped_column(String(20))
    item_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ready_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    incomplete_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    blocked_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_summary: Mapped[str | None] = mapped_column(String(500))
    payload_preview: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class ScanModel(Base):
    __tablename__ = "scans"
    __table_args__ = (
        UniqueConstraint("pair", "m15_close_time", "strategy_version", name="uq_scan_identity"),
        Index("ix_scans_status_started", "status", "started_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID_PK, primary_key=True, default=uuid.uuid4)
    pair: Mapped[str] = mapped_column(String(6), nullable=False, index=True)
    m15_close_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    snapshot_id: Mapped[uuid.UUID | None] = mapped_column(UUID_PK)
    strategy_version: Mapped[str] = mapped_column(String(80), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_code: Mapped[str | None] = mapped_column(String(80))


class AgentReportModel(Base):
    __tablename__ = "agent_reports"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="ck_agent_reports_score_range"),
        Index("ix_agent_reports_scan_agent", "scan_id", "agent_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID_PK, primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scans.id"), nullable=False, index=True)
    agent_name: Mapped[str] = mapped_column(String(120), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    verdict: Mapped[str] = mapped_column(String(40), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[str] = mapped_column(String(20), nullable=False)
    summary_ru: Mapped[str] = mapped_column(String(2000), nullable=False)
    reasons_for_json: Mapped[Any] = mapped_column(JSONB_TYPE, nullable=False)
    reasons_against_json: Mapped[Any] = mapped_column(JSONB_TYPE, nullable=False)
    invalid_if_json: Mapped[Any] = mapped_column(JSONB_TYPE, nullable=False)
    evidence_json: Mapped[Any] = mapped_column(JSONB_TYPE, nullable=False)
    rule_version: Mapped[str] = mapped_column(String(80), nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class SignalModel(Base):
    __tablename__ = "signals"
    __table_args__ = (
        Index("uq_signals_fingerprint", "fingerprint", unique=True),
        Index("ix_signals_pair_status_valid_until", "pair", "status", "valid_until"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID_PK, primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scans.id"), nullable=False, index=True)
    fingerprint: Mapped[str] = mapped_column(String(160), nullable=False)
    pair: Mapped[str] = mapped_column(String(6), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    setup_score: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[str] = mapped_column(String(20), nullable=False)
    entry_min: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    entry_max: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    invalidation_price: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    stop_loss: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    take_profit_1: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    take_profit_2: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    valid_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancel_reason_ru: Mapped[str | None] = mapped_column(String(1000))
    strategy_version: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class PaperPositionModel(Base):
    __tablename__ = "paper_positions"
    __table_args__ = (Index("ix_paper_positions_status_created", "status", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID_PK, primary_key=True, default=uuid.uuid4)
    signal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("signals.id"), nullable=False, index=True
    )
    account_balance_before: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    risk_percent: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    risk_amount_eur: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    position_size: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    entry_price: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    entered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    stop_loss: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    take_profit_1: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    take_profit_2: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False)
    status: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    result_eur: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    result_percent: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    result_r: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    spread_cost: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    slippage_cost: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
```

### `app/persistence/repositories/__init__.py`

```python
from app.persistence.repositories.foundation import (
    SqlAlchemyAuditLogRepository,
    SqlAlchemyCandleRepository,
    SqlAlchemyEconomicEventRepository,
    SqlAlchemyErrorEventRepository,
    SqlAlchemyScheduledDigestDeliveryStore,
    SqlAlchemySystemStateRepository,
)

__all__ = [
    "SqlAlchemyAuditLogRepository",
    "SqlAlchemyCandleRepository",
    "SqlAlchemyEconomicEventRepository",
    "SqlAlchemyErrorEventRepository",
    "SqlAlchemyScheduledDigestDeliveryStore",
    "SqlAlchemySystemStateRepository",
]
```

### `app/persistence/repositories/foundation.py`

```python
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import redact_text
from app.core.time import normalize_to_utc, utc_now
from app.domain.entities import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.entities.data_quality import UpsertResult
from app.domain.entities.readiness import SnapshotDigestStatus, SnapshotNotificationDedupKey
from app.domain.entities.scheduled_digest import ScheduledDigestDeliveryRecord
from app.domain.value_objects import CurrencyPair
from app.persistence.models import (
    AuditLogModel,
    CandleModel,
    EconomicEventModel,
    ErrorEventModel,
    ScheduledDigestDeliveryModel,
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


def _delivery_from_model(row: ScheduledDigestDeliveryModel) -> ScheduledDigestDeliveryRecord:
    return ScheduledDigestDeliveryRecord(
        project_phase=row.project_phase,
        dedup_key=SnapshotNotificationDedupKey(value=row.dedup_key),
        delivered_at=row.delivered_at,
        sender_name=row.sender_name,
        readiness_status=(
            SnapshotDigestStatus(row.readiness_status) if row.readiness_status is not None else None
        ),
        item_count=row.item_count,
        ready_count=row.ready_count,
        incomplete_count=row.incomplete_count,
        blocked_count=row.blocked_count,
        items_summary=row.items_summary,
        payload_preview=row.payload_preview,
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


class SqlAlchemyScheduledDigestDeliveryStore:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists(self, dedup_key: SnapshotNotificationDedupKey) -> bool:
        result = await self._session.execute(
            select(ScheduledDigestDeliveryModel.dedup_key).where(
                ScheduledDigestDeliveryModel.dedup_key == dedup_key.value
            )
        )
        return result.scalar_one_or_none() is not None

    async def record(self, record: ScheduledDigestDeliveryRecord) -> None:
        statement = (
            postgresql_insert(ScheduledDigestDeliveryModel)
            .values(
                dedup_key=record.dedup_key.value,
                project_phase=record.project_phase,
                delivered_at=record.delivered_at,
                sender_name=record.sender_name,
                readiness_status=(
                    record.readiness_status.value if record.readiness_status is not None else None
                ),
                item_count=record.item_count,
                ready_count=record.ready_count,
                incomplete_count=record.incomplete_count,
                blocked_count=record.blocked_count,
                items_summary=record.items_summary,
                payload_preview=record.payload_preview,
            )
            .on_conflict_do_nothing(index_elements=[ScheduledDigestDeliveryModel.dedup_key])
        )
        await self._session.execute(statement)

    async def get(
        self,
        dedup_key: SnapshotNotificationDedupKey,
    ) -> ScheduledDigestDeliveryRecord | None:
        result = await self._session.execute(
            select(ScheduledDigestDeliveryModel).where(
                ScheduledDigestDeliveryModel.dedup_key == dedup_key.value
            )
        )
        row = result.scalar_one_or_none()
        return None if row is None else _delivery_from_model(row)
```

### `app/persistence/unit_of_work.py`

```python
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.interfaces.notifications import ScheduledDigestDeliveryStore
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
    SqlAlchemyScheduledDigestDeliveryStore,
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
        self._scheduled_digest_deliveries: ScheduledDigestDeliveryStore | None = None

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
        self._scheduled_digest_deliveries = SqlAlchemyScheduledDigestDeliveryStore(self._session)
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
            self._scheduled_digest_deliveries = None
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

    @property
    def scheduled_digest_deliveries(self) -> ScheduledDigestDeliveryStore:
        if self._session is None or self._scheduled_digest_deliveries is None:
            raise RuntimeError("unit of work has not been entered")
        return self._scheduled_digest_deliveries

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

### `app/services/scheduled_digest_delivery_service.py`

```python
from datetime import datetime
from typing import Protocol

from app.core.time import normalize_to_utc
from app.domain.entities.readiness import (
    SnapshotNotificationDedupKey,
    SnapshotNotificationPayload,
    SnapshotScheduleItem,
)
from app.domain.entities.scheduled_digest import (
    ScheduledDigestConfig,
    ScheduledDigestDecision,
    ScheduledDigestDecisionReason,
    ScheduledDigestDeliveryRecord,
    ScheduledDigestDeliveryResult,
    ScheduledDigestTick,
)
from app.domain.interfaces.notifications import NotificationSender, ScheduledDigestDeliveryStore


class ReadinessDigestPayloadBuilder(Protocol):
    async def build_payload(
        self,
        *,
        items: tuple[SnapshotScheduleItem, ...],
        as_of: datetime,
    ) -> SnapshotNotificationPayload:
        """Build a neutral readiness digest payload for scheduled delivery."""


class InMemoryScheduledDigestDeliveryStore:
    def __init__(self) -> None:
        self._records: dict[str, ScheduledDigestDeliveryRecord] = {}

    async def exists(self, dedup_key: SnapshotNotificationDedupKey) -> bool:
        return dedup_key.value in self._records

    async def record(self, record: ScheduledDigestDeliveryRecord) -> None:
        self._records[record.dedup_key.value] = record

    async def get(
        self,
        dedup_key: SnapshotNotificationDedupKey,
    ) -> ScheduledDigestDeliveryRecord | None:
        return self._records.get(dedup_key.value)


class ScheduledDigestDeliveryService:
    def __init__(
        self,
        *,
        config: ScheduledDigestConfig,
        readiness_digest_service: ReadinessDigestPayloadBuilder,
        sender: NotificationSender,
        delivery_store: ScheduledDigestDeliveryStore,
        sender_name: str = "notification_sender",
    ) -> None:
        self._config = config
        self._readiness_digest_service = readiness_digest_service
        self._sender = sender
        self._delivery_store = delivery_store
        self._sender_name = sender_name

    async def run_tick(self, *, as_of: datetime) -> ScheduledDigestDeliveryResult:
        tick = ScheduledDigestTick(as_of=as_of)
        base_decision = self._decide(tick)
        if not base_decision.should_build:
            return _skipped_result(tick=tick, decision=base_decision)

        try:
            payload = await self._readiness_digest_service.build_payload(
                items=self._config.items,
                as_of=tick.as_of,
            )
        except Exception:
            return _skipped_result(
                tick=tick,
                decision=_decision(
                    config=self._config,
                    tick=tick,
                    reason=ScheduledDigestDecisionReason.BUILD_FAILED,
                    is_due=True,
                    should_build=False,
                ),
            )

        if await self._delivery_store.exists(payload.dedup_key):
            return _skipped_result(
                tick=tick,
                decision=_decision(
                    config=self._config,
                    tick=tick,
                    reason=ScheduledDigestDecisionReason.DUPLICATE,
                    is_due=True,
                    should_build=False,
                    dedup_key=payload.dedup_key,
                ),
                dedup_key=payload.dedup_key,
                payload=payload,
            )

        await self._sender.send(payload)
        record = ScheduledDigestDeliveryRecord(
            dedup_key=payload.dedup_key,
            delivered_at=tick.as_of,
            sender_name=self._sender_name,
            readiness_status=payload.digest.readiness_status,
            item_count=len(payload.digest.items),
            ready_count=payload.digest.ready_count,
            incomplete_count=payload.digest.incomplete_count,
            blocked_count=payload.digest.blocked_count,
            items_summary=_items_summary(payload),
            payload_preview=_payload_preview(payload.text),
        )
        await self._delivery_store.record(record)
        return ScheduledDigestDeliveryResult(
            tick=tick,
            decision=_decision(
                config=self._config,
                tick=tick,
                reason=ScheduledDigestDecisionReason.DELIVERED,
                is_due=True,
                should_build=True,
                dedup_key=payload.dedup_key,
            ),
            delivered=True,
            skipped=False,
            dedup_key=payload.dedup_key,
            payload=payload,
            record=record,
        )

    def _decide(self, tick: ScheduledDigestTick) -> ScheduledDigestDecision:
        if not self._config.enabled:
            return _decision(
                config=self._config,
                tick=tick,
                reason=ScheduledDigestDecisionReason.DISABLED,
                is_due=False,
                should_build=False,
            )
        if not self._config.items:
            return _decision(
                config=self._config,
                tick=tick,
                reason=ScheduledDigestDecisionReason.NO_ITEMS,
                is_due=False,
                should_build=False,
            )
        is_due = is_scheduled_digest_due(
            as_of=tick.as_of,
            interval_minutes=self._config.interval_minutes,
        )
        if not is_due:
            return _decision(
                config=self._config,
                tick=tick,
                reason=ScheduledDigestDecisionReason.NOT_DUE,
                is_due=False,
                should_build=False,
            )
        return _decision(
            config=self._config,
            tick=tick,
            reason=ScheduledDigestDecisionReason.DUE,
            is_due=True,
            should_build=True,
        )


def is_scheduled_digest_due(*, as_of: datetime, interval_minutes: int) -> bool:
    if interval_minutes < 1:
        raise ValueError("scheduled digest interval must be at least one minute")
    as_of_utc = normalize_to_utc(as_of)
    if as_of_utc.second != 0 or as_of_utc.microsecond != 0:
        return False
    minutes_since_midnight = (as_of_utc.hour * 60) + as_of_utc.minute
    return minutes_since_midnight % interval_minutes == 0


def _decision(
    *,
    config: ScheduledDigestConfig,
    tick: ScheduledDigestTick,
    reason: ScheduledDigestDecisionReason,
    is_due: bool,
    should_build: bool,
    dedup_key: SnapshotNotificationDedupKey | None = None,
) -> ScheduledDigestDecision:
    return ScheduledDigestDecision(
        enabled=config.enabled,
        is_due=is_due,
        should_build=should_build,
        reason=reason,
        item_count=len(config.items),
        tick_as_of=tick.as_of,
        dedup_key=dedup_key,
    )


def _skipped_result(
    *,
    tick: ScheduledDigestTick,
    decision: ScheduledDigestDecision,
    dedup_key: SnapshotNotificationDedupKey | None = None,
    payload: SnapshotNotificationPayload | None = None,
) -> ScheduledDigestDeliveryResult:
    return ScheduledDigestDeliveryResult(
        tick=tick,
        decision=decision,
        delivered=False,
        skipped=True,
        dedup_key=dedup_key,
        payload=payload,
        record=None,
    )


def _items_summary(payload: SnapshotNotificationPayload) -> str:
    return ",".join(f"{item.pair.value}:{item.timeframe.value}" for item in payload.digest.items)


def _payload_preview(text: str) -> str:
    normalized = " ".join(text.split())
    return normalized[:1000]
```


## Full Contents Of Changed Test Files

No brand-new test file was added in Phase 3I; existing unit, contract, integration, and fake-support tests were extended. Full contents of the changed test files are included below.

### `tests/contract/test_safety_boundaries.py`

```python
import inspect
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.adapters.disabled import (
    DisabledEconomicCalendarProvider,
    DisabledLLMProvider,
    DisabledMarketDataProvider,
)
from app.core.enums import Decision
from app.core.exceptions import IntegrationDisabledError
from app.domain.entities import Timeframe
from app.domain.value_objects import CurrencyPair
from app.persistence.models import ScheduledDigestDeliveryModel
from app.persistence.repositories.foundation import SqlAlchemyScheduledDigestDeliveryStore
from app.telegram.commands import digest_command
from scripts.security_check import scan_files, scan_production_code

PHASE_3B_FILES = (
    Path("app/domain/entities/features.py"),
    Path("app/domain/feature_engine.py"),
    Path("app/services/feature_service.py"),
)
PHASE_3B_FORBIDDEN_TERMS = (
    "LONG",
    "SHORT",
    "BUY",
    "SELL",
    "NO_TRADE",
    "signal",
    "setup_score",
    "recommendation",
    "OpenAI",
    "broker",
    "paper_trading",
    "order_execution",
)
PHASE_3C_FILES = (
    Path("app/domain/entities/context.py"),
    Path("app/domain/context_engine.py"),
    Path("app/services/context_service.py"),
)
PHASE_3C_FORBIDDEN_TERMS = (
    "bullish",
    "bearish",
    "strong",
    "weak",
    "overbought",
    "oversold",
    "breakout",
    "reversal",
    "trend",
    "entry",
    "exit",
    "buy",
    "sell",
    "long",
    "short",
    "recommendation",
    "setup",
    "score",
    "confidence",
    "signal",
    "OpenAI",
    "broker",
    "paper_trading",
    "order_execution",
)
PHASE_3D_FILES = (
    Path("app/domain/entities/analysis.py"),
    Path("app/domain/analysis_engine.py"),
    Path("app/services/analysis_service.py"),
    Path("tests/unit/test_analysis_snapshot_foundation.py"),
)
PHASE_3D_FORBIDDEN_TERMS = (
    "bullish",
    "bearish",
    "strong",
    "weak",
    "overbought",
    "oversold",
    "breakout",
    "reversal",
    "trend signal",
    "entry",
    "exit",
    "buy",
    "sell",
    "long",
    "short",
    "recommendation",
    "setup",
    "score",
    "confidence",
    "trade",
    "trading",
    "strategy",
    "signal",
    "OpenAI",
    "broker",
    "paper_trading",
    "order_execution",
)
PHASE_3F_FILES = (
    Path("app/domain/entities/readiness.py"),
    Path("app/domain/readiness_engine.py"),
    Path("app/services/readiness_digest_service.py"),
    Path("app/telegram/formatter.py"),
    Path("tests/unit/test_readiness_scheduler_foundation.py"),
)
PHASE_3F_FORBIDDEN_TERMS = (
    "bullish",
    "bearish",
    "strong",
    "weak",
    "overbought",
    "oversold",
    "breakout",
    "reversal",
    "trend signal",
    "entry",
    "exit",
    "buy",
    "sell",
    "long",
    "short",
    "recommendation",
    "setup",
    "score",
    "confidence",
    "trade",
    "trading",
    "strategy",
    "signal",
    "OpenAI",
    "broker",
    "paper_trading",
    "order_execution",
)
PHASE_3G_FORBIDDEN_TERMS = (
    "bullish",
    "bearish",
    "overbought",
    "oversold",
    "breakout",
    "reversal",
    "trend signal",
    "entry",
    "exit",
    "buy",
    "sell",
    "long",
    "short",
    "recommendation",
    "setup",
    "score",
    "confidence",
    "OpenAI",
    "broker",
    "paper_trading",
    "order_execution",
)
PHASE_3H_FILES = (
    Path("app/domain/entities/scheduled_digest.py"),
    Path("app/domain/interfaces/notifications.py"),
    Path("app/services/scheduled_digest_delivery_service.py"),
    Path("app/scheduler/jobs.py"),
)
PHASE_3H_FORBIDDEN_TERMS = (
    "bullish",
    "bearish",
    "overbought",
    "oversold",
    "breakout",
    "reversal",
    "trend signal",
    "entry",
    "exit",
    "buy",
    "sell",
    "long",
    "short",
    "recommendation",
    "setup",
    "score",
    "confidence",
    "OpenAI",
    "broker",
    "paper_trading",
    "order_execution",
)
PHASE_3I_FILES = (Path("migrations/versions/0003_phase3i_scheduled_digest_deliveries.py"),)
PHASE_3I_SOURCE_OBJECTS = (
    ScheduledDigestDeliveryModel,
    SqlAlchemyScheduledDigestDeliveryStore,
)
PHASE_3I_FORBIDDEN_TERMS = (
    "bullish",
    "bearish",
    "overbought",
    "oversold",
    "breakout",
    "reversal",
    "trend signal",
    "entry",
    "exit",
    "buy",
    "sell",
    "long",
    "short",
    "recommendation",
    "setup",
    "score",
    "confidence",
    "OpenAI",
    "broker",
    "paper_trading",
    "order_execution",
)


def test_no_real_order_execution_code_exists() -> None:
    findings = scan_production_code(Path.cwd())

    assert findings == []


def test_phase3b_feature_engine_files_do_not_add_decision_or_execution_terms() -> None:
    offenders: list[str] = []
    for file_path in PHASE_3B_FILES:
        text = file_path.read_text(encoding="utf-8")
        for term in PHASE_3B_FORBIDDEN_TERMS:
            if term in text:
                offenders.append(f"{file_path}: {term}")

    assert offenders == []


def test_phase3c_context_files_do_not_add_decision_or_execution_terms() -> None:
    offenders: list[str] = []
    for file_path in PHASE_3C_FILES:
        text = file_path.read_text(encoding="utf-8")
        for term in PHASE_3C_FORBIDDEN_TERMS:
            if term in text:
                offenders.append(f"{file_path}: {term}")

    assert offenders == []


def test_phase3d_analysis_files_do_not_add_decision_or_execution_terms() -> None:
    offenders: list[str] = []
    for file_path in PHASE_3D_FILES:
        text = file_path.read_text(encoding="utf-8")
        lowered = text.lower()
        for term in PHASE_3D_FORBIDDEN_TERMS:
            if term.lower() in lowered:
                offenders.append(f"{file_path}: {term}")

    assert offenders == []


def test_phase3f_readiness_files_do_not_add_decision_or_execution_terms() -> None:
    offenders: list[str] = []
    for file_path in PHASE_3F_FILES:
        text = file_path.read_text(encoding="utf-8")
        lowered = text.lower()
        for term in PHASE_3F_FORBIDDEN_TERMS:
            if term.lower() in lowered:
                offenders.append(f"{file_path}: {term}")

    assert offenders == []


def test_phase3g_digest_command_does_not_add_decision_or_execution_terms() -> None:
    source = inspect.getsource(digest_command).lower()

    offenders = [term for term in PHASE_3G_FORBIDDEN_TERMS if term.lower() in source]

    assert offenders == []


def test_phase3h_scheduled_digest_files_do_not_add_decision_or_execution_terms() -> None:
    offenders: list[str] = []
    for file_path in PHASE_3H_FILES:
        text = file_path.read_text(encoding="utf-8")
        lowered = text.lower()
        for term in PHASE_3H_FORBIDDEN_TERMS:
            if term.lower() in lowered:
                offenders.append(f"{file_path}: {term}")

    assert offenders == []


def test_phase3i_digest_audit_files_do_not_add_decision_or_execution_terms() -> None:
    offenders: list[str] = []
    texts = [path.read_text(encoding="utf-8") for path in PHASE_3I_FILES]
    texts.extend(inspect.getsource(source_object) for source_object in PHASE_3I_SOURCE_OBJECTS)
    for index, text in enumerate(texts):
        lowered = text.lower()
        for term in PHASE_3I_FORBIDDEN_TERMS:
            if term.lower() in lowered:
                offenders.append(f"phase3i-source-{index}: {term}")

    assert offenders == []


@pytest.mark.asyncio
async def test_disabled_market_data_provider_fails_before_external_call() -> None:
    with pytest.raises(IntegrationDisabledError):
        await DisabledMarketDataProvider().get_closed_candles(
            CurrencyPair(value="EURUSD"),
            Timeframe.M15,
            datetime.now(UTC),
            datetime.now(UTC),
        )


@pytest.mark.asyncio
async def test_disabled_calendar_provider_fails_explicitly() -> None:
    with pytest.raises(IntegrationDisabledError):
        await DisabledEconomicCalendarProvider().get_events(
            datetime.now(UTC),
            datetime.now(UTC),
        )


@pytest.mark.asyncio
async def test_disabled_llm_provider_fails_explicitly() -> None:
    with pytest.raises(IntegrationDisabledError):
        await DisabledLLMProvider().explain(Decision.NO_TRADE, [])


def test_safety_scanner_allows_analytical_code(tmp_path: Path) -> None:
    file_path = tmp_path / "analysis.py"
    file_path.write_text(
        "def calculate_structure():\n    return {'bias': 'neutral'}\n",
        encoding="utf-8",
    )

    assert scan_files([file_path]) == []


def test_safety_scanner_allows_read_only_provider_code(tmp_path: Path) -> None:
    file_path = tmp_path / "provider.py"
    file_path.write_text(
        "async def get_closed_candles(client):\n"
        "    return await client.get('/candles?pair=EURUSD')\n",
        encoding="utf-8",
    )

    assert scan_files([file_path]) == []


def test_safety_scanner_rejects_order_execution_code(tmp_path: Path) -> None:
    file_path = tmp_path / "bad.py"
    file_path.write_text("async def place_order():\n    return None\n", encoding="utf-8")

    assert scan_files([file_path])


def test_safety_scanner_rejects_broker_execution_imports(tmp_path: Path) -> None:
    file_path = tmp_path / "bad_import.py"
    file_path.write_text("import ccxt\n", encoding="utf-8")

    assert scan_files([file_path])


def test_safety_scanner_rejects_execution_http_endpoints(tmp_path: Path) -> None:
    file_path = tmp_path / "bad_endpoint.py"
    file_path.write_text("ORDERS_URL = 'https://broker.example/v1/orders'\n", encoding="utf-8")

    assert scan_files([file_path])
```

### `tests/fakes.py`

```python
from types import TracebackType
from typing import Any, Self

from app.domain.entities import Candle, EconomicEvent, Timeframe
from app.domain.entities.data_quality import UpsertResult
from app.domain.entities.readiness import SnapshotNotificationDedupKey
from app.domain.entities.scheduled_digest import ScheduledDigestDeliveryRecord
from app.domain.interfaces.notifications import ScheduledDigestDeliveryStore
from app.domain.interfaces.repositories import (
    AuditLogRepository,
    CandleRepository,
    EconomicEventRepository,
    ErrorEventRepository,
    SystemStateRepository,
)
from app.domain.value_objects import CurrencyPair


class FakeSystemStateRepository:
    def __init__(self, state: dict[str, Any]) -> None:
        self._state = state

    async def get(self, key: str) -> Any | None:
        return self._state.get(key)

    async def set(self, key: str, value: Any) -> None:
        self._state[key] = value

    async def get_all(self) -> dict[str, Any]:
        return dict(self._state)


class FakeAuditLogRepository:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    async def add(
        self,
        *,
        event_type: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        actor: str | None = None,
        before_json: dict[str, Any] | None = None,
        after_json: dict[str, Any] | None = None,
    ) -> None:
        self.events.append(
            {
                "event_type": event_type,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "actor": actor,
                "before_json": before_json,
                "after_json": after_json,
            }
        )


class FakeErrorEventRepository:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    async def add(
        self,
        *,
        error_code: str,
        severity: str,
        component: str,
        message_ru: str,
        technical_details: str | None = None,
        context_json: dict[str, Any] | None = None,
        resolved: bool = False,
    ) -> None:
        self.events.append(
            {
                "error_code": error_code,
                "severity": severity,
                "component": component,
                "message_ru": message_ru,
                "technical_details": technical_details,
                "context_json": context_json,
                "resolved": resolved,
            }
        )


class FakeCandleRepository:
    def __init__(self, candles: list[Candle]) -> None:
        self._candles = candles

    async def upsert_many(self, candles: list[Candle]) -> UpsertResult:
        self._candles.extend(candles)
        return UpsertResult(inserted=len(candles), updated=0)

    async def list_range(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        start_at: Any,
        end_at: Any,
        provider: str | None = None,
    ) -> list[Candle]:
        return [
            candle
            for candle in self._candles
            if candle.pair == pair
            and candle.timeframe == timeframe
            and candle.open_time >= start_at
            and candle.close_time <= end_at
            and (provider is None or candle.provider == provider)
        ]


class FakeEconomicEventRepository:
    def __init__(self, events: list[EconomicEvent]) -> None:
        self._events = events

    async def upsert_many(self, events: list[EconomicEvent]) -> UpsertResult:
        self._events.extend(events)
        return UpsertResult(inserted=len(events), updated=0)

    async def list_window(
        self,
        *,
        start_at: Any,
        end_at: Any,
        currencies: list[str] | None = None,
        provider: str | None = None,
    ) -> list[EconomicEvent]:
        return [
            event
            for event in self._events
            if start_at <= event.scheduled_at < end_at
            and (currencies is None or event.currency in currencies)
            and (provider is None or event.provider == provider)
        ]


class FakeScheduledDigestDeliveryStore:
    def __init__(self, records: dict[str, ScheduledDigestDeliveryRecord]) -> None:
        self._records = records

    async def exists(self, dedup_key: SnapshotNotificationDedupKey) -> bool:
        return dedup_key.value in self._records

    async def record(self, record: ScheduledDigestDeliveryRecord) -> None:
        self._records.setdefault(record.dedup_key.value, record)

    async def get(
        self,
        dedup_key: SnapshotNotificationDedupKey,
    ) -> ScheduledDigestDeliveryRecord | None:
        return self._records.get(dedup_key.value)


class FakeUnitOfWork:
    def __init__(
        self,
        state: dict[str, Any],
        candles: list[Candle],
        events: list[EconomicEvent],
        scheduled_digest_deliveries: dict[str, ScheduledDigestDeliveryRecord],
    ) -> None:
        self.system_state: SystemStateRepository = FakeSystemStateRepository(state)
        self.audit_logs: AuditLogRepository = FakeAuditLogRepository()
        self.error_events: ErrorEventRepository = FakeErrorEventRepository()
        self.candles: CandleRepository = FakeCandleRepository(candles)
        self.economic_events: EconomicEventRepository = FakeEconomicEventRepository(events)
        self.scheduled_digest_deliveries: ScheduledDigestDeliveryStore = (
            FakeScheduledDigestDeliveryStore(scheduled_digest_deliveries)
        )
        self.committed = False
        self.rolled_back = False

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None or not self.committed:
            self.rolled_back = True

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class FakeUnitOfWorkFactory:
    def __init__(
        self,
        state: dict[str, Any] | None = None,
        candles: list[Candle] | None = None,
        events: list[EconomicEvent] | None = None,
        scheduled_digest_deliveries: dict[str, ScheduledDigestDeliveryRecord] | None = None,
    ) -> None:
        self.state = state or {}
        self.candles = candles or []
        self.events = events or []
        self.scheduled_digest_deliveries = scheduled_digest_deliveries or {}
        self.instances: list[FakeUnitOfWork] = []

    def __call__(self) -> FakeUnitOfWork:
        uow = FakeUnitOfWork(
            self.state,
            self.candles,
            self.events,
            self.scheduled_digest_deliveries,
        )
        self.instances.append(uow)
        return uow
```

### `tests/integration/test_database_and_api.py`

```python
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core import constants
from app.core.config import Settings
from app.domain.entities import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.entities.readiness import (
    SnapshotDigest,
    SnapshotDigestItem,
    SnapshotDigestStatus,
    SnapshotNotificationDedupKey,
    SnapshotNotificationPayload,
    SnapshotScheduleItem,
)
from app.domain.entities.scheduled_digest import (
    ScheduledDigestConfig,
    ScheduledDigestDecisionReason,
    ScheduledDigestDeliveryRecord,
)
from app.domain.value_objects import CurrencyPair
from app.main import create_app
from app.persistence.database import create_engine, create_session_factory
from app.persistence.models import CandleModel, EconomicEventModel, ScheduledDigestDeliveryModel
from app.persistence.session import build_uow_factory
from app.services.scheduled_digest_delivery_service import ScheduledDigestDeliveryService
from app.services.system_state_service import SystemStateService

_MARKET_CALENDAR_TEST_PROVIDER = "integration-phase3a-repository-test"
_SCHEDULED_DIGEST_TEST_SENDER = "integration-phase3i-sender"


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


async def _delete_scheduled_digest_test_rows(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        await session.execute(
            delete(ScheduledDigestDeliveryModel).where(
                ScheduledDigestDeliveryModel.sender_name == _SCHEDULED_DIGEST_TEST_SENDER
            )
        )
        await session.commit()


class FakeNotificationSender:
    def __init__(self) -> None:
        self.payloads: list[SnapshotNotificationPayload] = []

    async def send(self, payload: SnapshotNotificationPayload) -> None:
        self.payloads.append(payload)


class StaticReadinessDigestPayloadBuilder:
    def __init__(self, payload: SnapshotNotificationPayload) -> None:
        self._payload = payload

    async def build_payload(
        self,
        *,
        items: tuple[SnapshotScheduleItem, ...],
        as_of: datetime,
    ) -> SnapshotNotificationPayload:
        return self._payload


def _dedup_key(seed: str) -> SnapshotNotificationDedupKey:
    return SnapshotNotificationDedupKey(value=(seed * 64)[:64])


def _scheduled_digest_payload(
    dedup_key: SnapshotNotificationDedupKey,
) -> SnapshotNotificationPayload:
    as_of = datetime(2026, 7, 15, 10, 45, tzinfo=UTC)
    item = SnapshotDigestItem(
        pair=CurrencyPair(value="EURUSD"),
        timeframe=Timeframe.M15,
        window_start=datetime(2026, 7, 15, 10, 0, tzinfo=UTC),
        window_end=as_of,
        as_of=as_of,
        readiness_status=SnapshotDigestStatus.READY,
        input_candle_count=3,
        used_candle_count=3,
        input_event_count=0,
        used_event_count=0,
        issue_count=0,
        no_candles_after_as_of_used=True,
        no_events_after_as_of_used=True,
        snapshot_id="b" * 64,
        dedup_key=dedup_key,
    )
    digest = SnapshotDigest(
        project_phase=constants.PROJECT_PHASE,
        generated_at=as_of,
        as_of=as_of,
        readiness_status=SnapshotDigestStatus.READY,
        items=(item,),
        ready_count=1,
        incomplete_count=0,
        blocked_count=0,
        dedup_key=dedup_key,
    )
    return SnapshotNotificationPayload(
        project_phase=constants.PROJECT_PHASE,
        dedup_key=dedup_key,
        digest=digest,
        text="Системный отчёт готовности. Решений и указаний нет.",
    )


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
    assert status.json()["project_phase"] == "phase_3i_persistent_digest_audit_foundation"
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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_scheduled_digest_delivery_store_persists_and_deduplicates(
    postgres_database_url: str,
) -> None:
    engine = create_engine(postgres_database_url)
    session_factory = create_session_factory(engine)
    dedup_key = _dedup_key("c")
    record = ScheduledDigestDeliveryRecord(
        dedup_key=dedup_key,
        delivered_at=datetime(2026, 7, 15, 12, 45, tzinfo=UTC),
        sender_name=_SCHEDULED_DIGEST_TEST_SENDER,
        readiness_status=SnapshotDigestStatus.READY,
        item_count=1,
        ready_count=1,
        incomplete_count=0,
        blocked_count=0,
        items_summary="EURUSD:M15",
        payload_preview="Системный отчёт готовности. Решений и указаний нет.",
    )
    try:
        await _delete_scheduled_digest_test_rows(session_factory)
        uow_factory = build_uow_factory(session_factory)

        async with uow_factory() as uow:
            assert await uow.scheduled_digest_deliveries.exists(dedup_key) is False
            await uow.scheduled_digest_deliveries.record(record)
            await uow.scheduled_digest_deliveries.record(record)
            await uow.commit()

        duplicate_record = record.model_copy(
            update={
                "readiness_status": SnapshotDigestStatus.INCOMPLETE,
                "item_count": 2,
                "ready_count": 0,
                "incomplete_count": 2,
                "items_summary": "EURUSD:M15,GBPUSD:M15",
                "payload_preview": "Повторная запись не должна менять первый аудит.",
            }
        )
        async with uow_factory() as uow:
            await uow.scheduled_digest_deliveries.record(duplicate_record)
            await uow.commit()

        async with uow_factory() as uow:
            assert await uow.scheduled_digest_deliveries.exists(dedup_key) is True
            stored = await uow.scheduled_digest_deliveries.get(dedup_key)

        assert stored is not None
        assert stored.project_phase == constants.PROJECT_PHASE
        assert stored.delivered_at == datetime(2026, 7, 15, 12, 45, tzinfo=UTC)
        assert stored.sender_name == _SCHEDULED_DIGEST_TEST_SENDER
        assert stored.readiness_status == SnapshotDigestStatus.READY
        assert stored.item_count == 1
        assert stored.ready_count == 1
        assert stored.incomplete_count == 0
        assert stored.items_summary == "EURUSD:M15"
        assert "Решений и указаний нет" in (stored.payload_preview or "")

    finally:
        await _delete_scheduled_digest_test_rows(session_factory)
        await engine.dispose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_scheduled_digest_delivery_service_skips_persisted_duplicate(
    postgres_database_url: str,
) -> None:
    engine = create_engine(postgres_database_url)
    session_factory = create_session_factory(engine)
    dedup_key = _dedup_key("d")
    payload = _scheduled_digest_payload(dedup_key)
    config = ScheduledDigestConfig(
        enabled=True,
        interval_minutes=15,
        items=(
            SnapshotScheduleItem(
                pair=CurrencyPair(value="EURUSD"),
                timeframe=Timeframe.M15,
                lookback_candle_count=3,
            ),
        ),
    )
    try:
        await _delete_scheduled_digest_test_rows(session_factory)
        uow_factory = build_uow_factory(session_factory)

        first_sender = FakeNotificationSender()
        async with uow_factory() as uow:
            service = ScheduledDigestDeliveryService(
                config=config,
                readiness_digest_service=StaticReadinessDigestPayloadBuilder(payload),
                sender=first_sender,
                delivery_store=uow.scheduled_digest_deliveries,
                sender_name=_SCHEDULED_DIGEST_TEST_SENDER,
            )
            first = await service.run_tick(as_of=datetime(2026, 7, 15, 10, 45, tzinfo=UTC))
            await uow.commit()

        second_sender = FakeNotificationSender()
        async with uow_factory() as uow:
            service = ScheduledDigestDeliveryService(
                config=config,
                readiness_digest_service=StaticReadinessDigestPayloadBuilder(payload),
                sender=second_sender,
                delivery_store=uow.scheduled_digest_deliveries,
                sender_name=_SCHEDULED_DIGEST_TEST_SENDER,
            )
            second = await service.run_tick(as_of=datetime(2026, 7, 15, 10, 45, tzinfo=UTC))

        assert first.delivered is True
        assert len(first_sender.payloads) == 1
        assert second.skipped is True
        assert second.decision.reason == ScheduledDigestDecisionReason.DUPLICATE
        assert second.dedup_key == first.dedup_key
        assert second_sender.payloads == []

    finally:
        await _delete_scheduled_digest_test_rows(session_factory)
        await engine.dispose()
```

### `tests/unit/test_analysis_snapshot_foundation.py`

```python
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.analysis_engine import AnalysisEngine
from app.domain.entities import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.entities.analysis import AnalysisIssueCode, AnalysisReadinessStatus
from app.domain.value_objects import CurrencyPair
from app.services.analysis_service import AnalysisService

PAIR = CurrencyPair(value="EURUSD")
BASE_TIME = datetime(2026, 7, 8, 8, 0, tzinfo=UTC)
OPEN_VALUES = (Decimal("100"), Decimal("110"), Decimal("121"))
CLOSE_VALUES = (Decimal("110"), Decimal("121"), Decimal("133.1"))
HIGH_VALUES = (Decimal("112"), Decimal("123"), Decimal("135"))
LOW_VALUES = (Decimal("98"), Decimal("109"), Decimal("120"))


def _candle(
    index: int,
    *,
    provider: str = "phase3d-provider",
    pair: CurrencyPair = PAIR,
    timeframe: Timeframe = Timeframe.M15,
) -> Candle:
    open_time = BASE_TIME + timedelta(minutes=15 * index)
    return Candle(
        provider=provider,
        pair=pair,
        timeframe=timeframe,
        open_time=open_time,
        close_time=open_time + timedelta(minutes=15),
        open=OPEN_VALUES[index],
        high=HIGH_VALUES[index],
        low=LOW_VALUES[index],
        close=CLOSE_VALUES[index],
        volume=Decimal("100"),
        is_closed=True,
    )


def _event(
    minutes_after_base: int,
    *,
    provider: str = "phase3d-provider",
    provider_event_id: str = "event-1",
    currency: str = "EUR",
) -> EconomicEvent:
    return EconomicEvent(
        provider=provider,
        provider_event_id=provider_event_id,
        title="Consumer Price Index",
        currency=currency,
        country="Eurozone",
        impact=EconomicImpact.HIGH,
        scheduled_at=BASE_TIME + timedelta(minutes=minutes_after_base),
        actual=Decimal("2.2"),
        forecast=Decimal("2.1"),
        previous=Decimal("2.0"),
        fetched_at=BASE_TIME,
    )


def _engine() -> AnalysisEngine:
    return AnalysisEngine()


def _snapshot(
    candles: Sequence[Candle] | None = None,
    events: Sequence[EconomicEvent] | None = None,
    *,
    window_start: datetime = BASE_TIME,
    window_end: datetime = BASE_TIME + timedelta(minutes=45),
    as_of: datetime = BASE_TIME + timedelta(minutes=45),
    moving_average_windows: Sequence[int] = (2,),
):
    return _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=window_start,
        window_end=window_end,
        as_of=as_of,
        candles=list(candles) if candles is not None else [_candle(0), _candle(1), _candle(2)],
        economic_events=list(events) if events is not None else [_event(10)],
        moving_average_windows=moving_average_windows,
    )


def _issue_codes(snapshot) -> set[AnalysisIssueCode]:
    return {issue.code for issue in snapshot.readiness_issues}


def test_analysis_snapshot_assembly_is_exact_and_neutral() -> None:
    snapshot = _snapshot()

    assert snapshot.readiness_status == AnalysisReadinessStatus.READY
    assert snapshot.metadata.project_phase == constants.PROJECT_PHASE
    assert snapshot.input_audit.input_candle_count == 3
    assert snapshot.input_audit.used_candle_count == 3
    assert snapshot.input_audit.input_event_count == 1
    assert snapshot.input_audit.used_event_count == 1
    assert snapshot.input_audit.no_candles_after_as_of_used is True
    assert snapshot.input_audit.no_events_after_as_of_used is True
    assert snapshot.feature_snapshot is not None
    assert snapshot.context_snapshot is not None
    assert snapshot.feature_snapshot.candle_summary.latest_close == Decimal("133.1")
    assert snapshot.context_snapshot.return_distribution.mean_return == Decimal("0.1")
    assert snapshot.context_snapshot.return_distribution.cumulative_return == Decimal("0.21")
    assert snapshot.context_snapshot.return_distribution.return_standard_deviation == Decimal("0.0")
    assert snapshot.context_snapshot.event_context.used_event_count == 1
    assert snapshot.metadata.snapshot_id


def test_analysis_window_normalizes_to_utc() -> None:
    offset = timezone(timedelta(hours=2))
    snapshot = _snapshot(
        window_start=datetime(2026, 7, 8, 10, 0, tzinfo=offset),
        window_end=datetime(2026, 7, 8, 10, 45, tzinfo=offset),
        as_of=datetime(2026, 7, 8, 10, 45, tzinfo=offset),
    )

    assert snapshot.window.window_start == BASE_TIME
    assert snapshot.window.window_end == BASE_TIME + timedelta(minutes=45)
    assert snapshot.window.as_of == BASE_TIME + timedelta(minutes=45)


def test_analysis_snapshot_is_json_serializable() -> None:
    snapshot = _snapshot()

    data = snapshot.model_dump(mode="json")
    text = snapshot.model_dump_json()

    assert data["metadata"]["project_phase"] == "phase_3i_persistent_digest_audit_foundation"
    assert "phase_3i_persistent_digest_audit_foundation" in text
    assert data["context_snapshot"]["return_distribution"]["mean_return"] == "0.1"


def test_readiness_statuses_are_ready_incomplete_and_blocked() -> None:
    ready = _snapshot()
    incomplete = _snapshot(candles=[_candle(0), _candle(2)])
    blocked = _snapshot(
        candles=[
            _candle(0),
            _candle(0, provider="phase3d-provider-b"),
            _candle(1),
            _candle(2),
        ]
    )

    assert ready.readiness_status == AnalysisReadinessStatus.READY
    assert incomplete.readiness_status == AnalysisReadinessStatus.INCOMPLETE
    assert AnalysisIssueCode.MISSING_CANDLE in _issue_codes(incomplete)
    assert blocked.readiness_status == AnalysisReadinessStatus.BLOCKED
    assert AnalysisIssueCode.DUPLICATE_CANDLE in _issue_codes(blocked)


def test_as_of_proof_excludes_later_inputs_from_used_data() -> None:
    snapshot = _snapshot(
        events=[_event(10), _event(35, provider_event_id="event-2")],
        as_of=BASE_TIME + timedelta(minutes=30),
    )

    assert snapshot.readiness_status == AnalysisReadinessStatus.BLOCKED
    assert AnalysisIssueCode.CANDLE_AFTER_AS_OF in _issue_codes(snapshot)
    assert AnalysisIssueCode.EVENT_AFTER_AS_OF in _issue_codes(snapshot)
    assert snapshot.input_audit.input_candles_after_as_of_count == 1
    assert snapshot.input_audit.input_events_after_as_of_count == 1
    assert snapshot.input_audit.no_candles_after_as_of_used is True
    assert snapshot.input_audit.no_events_after_as_of_used is True
    assert snapshot.input_audit.latest_used_candle_close_time == BASE_TIME + timedelta(minutes=30)
    assert snapshot.input_audit.latest_used_event_time == BASE_TIME + timedelta(minutes=10)


def test_issues_are_aggregated_from_source_snapshots() -> None:
    snapshot = _snapshot(candles=[_candle(0), _candle(2)])
    counts = {
        (item.source, item.code): item.count for item in snapshot.input_audit.excluded_issue_counts
    }

    assert counts[("feature", AnalysisIssueCode.MISSING_CANDLE)] == 1
    assert counts[("context", AnalysisIssueCode.MISSING_CANDLE)] == 1
    assert counts[("data_quality", AnalysisIssueCode.MISSING_CANDLE)] == 1


def test_empty_and_small_inputs_are_handled_safely() -> None:
    empty = _snapshot(candles=[], events=[])
    small = _snapshot(
        candles=[_candle(0)],
        events=[],
        window_end=BASE_TIME + timedelta(minutes=15),
        moving_average_windows=(3,),
    )

    assert empty.readiness_status == AnalysisReadinessStatus.BLOCKED
    assert AnalysisIssueCode.NO_CANDLES in _issue_codes(empty)
    assert empty.input_audit.used_candle_count == 0
    assert small.readiness_status == AnalysisReadinessStatus.INCOMPLETE
    assert AnalysisIssueCode.INSUFFICIENT_CANDLES in _issue_codes(small)


def test_analysis_models_are_immutable() -> None:
    snapshot = _snapshot()

    with pytest.raises(ValidationError):
        snapshot.input_audit.used_candle_count = 99


def test_analysis_output_is_deterministic_for_same_input() -> None:
    first = _snapshot()
    second = _snapshot()

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert first.metadata.snapshot_id == second.metadata.snapshot_id


@asynccontextmanager
async def _analysis_scope(
    candle_repository,
    event_repository,
) -> AsyncIterator[object]:
    class Repositories:
        candles = candle_repository
        economic_events = event_repository

    yield Repositories()


class _CandleRepository:
    def __init__(self, candles: Sequence[Candle]) -> None:
        self._candles = list(candles)
        self.provider: str | None = None

    async def list_range(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        start_at: datetime,
        end_at: datetime,
        provider: str | None = None,
    ) -> list[Candle]:
        self.provider = provider
        return [
            candle
            for candle in self._candles
            if candle.pair == pair
            and candle.timeframe == timeframe
            and candle.open_time >= start_at
            and candle.close_time <= end_at
        ]


class _EventRepository:
    def __init__(self, events: Sequence[EconomicEvent]) -> None:
        self._events = list(events)
        self.currencies: list[str] | None = None
        self.provider: str | None = None

    async def list_window(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
        currencies: list[str] | None = None,
        provider: str | None = None,
    ) -> list[EconomicEvent]:
        self.currencies = currencies
        self.provider = provider
        return [
            event
            for event in self._events
            if start_at <= event.scheduled_at < end_at
            and (currencies is None or event.currency in currencies)
        ]


class _UnitOfWorkFactory:
    def __init__(
        self,
        candle_repository: _CandleRepository,
        event_repository: _EventRepository,
    ) -> None:
        self._candle_repository = candle_repository
        self._event_repository = event_repository

    def __call__(self):
        return _analysis_scope(self._candle_repository, self._event_repository)


@pytest.mark.asyncio
async def test_analysis_service_uses_repository_protocols() -> None:
    candle_repository = _CandleRepository([_candle(0), _candle(1), _candle(2)])
    event_repository = _EventRepository([_event(10)])
    service = AnalysisService(_UnitOfWorkFactory(candle_repository, event_repository))

    report = await service.build_report(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=BASE_TIME,
        window_end=BASE_TIME + timedelta(minutes=45),
        as_of=BASE_TIME + timedelta(minutes=45),
        provider="phase3d-provider",
    )

    assert report.snapshot.readiness_status == AnalysisReadinessStatus.READY
    assert report.ready_for_review is True
    assert report.used_candle_count == 3
    assert report.used_event_count == 1
    assert candle_repository.provider == "phase3d-provider"
    assert event_repository.provider == "phase3d-provider"
    assert event_repository.currencies == ["EUR", "USD"]
```

### `tests/unit/test_readiness_scheduler_foundation.py`

```python
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core import constants
from app.core.enums import MessageType
from app.domain.analysis_engine import AnalysisEngine
from app.domain.entities import Candle, Timeframe
from app.domain.entities.readiness import (
    SnapshotDigestStatus,
    SnapshotScheduleItem,
)
from app.domain.readiness_engine import (
    SnapshotDigestBuilder,
    SnapshotReadinessPlanner,
    latest_closed_boundary,
)
from app.domain.value_objects import CurrencyPair
from app.services.analysis_service import AnalysisService
from app.services.readiness_digest_service import ReadinessDigestService
from app.telegram.formatter import TelegramFormatter
from tests.fakes import FakeUnitOfWorkFactory

PAIR = CurrencyPair(value="EURUSD")
BASE_TIME = datetime(2026, 7, 15, 8, 0, tzinfo=UTC)


def _schedule_item(
    *,
    timeframe: Timeframe = Timeframe.M15,
    lookback_candle_count: int = 3,
) -> SnapshotScheduleItem:
    return SnapshotScheduleItem(
        pair=PAIR,
        timeframe=timeframe,
        lookback_candle_count=lookback_candle_count,
    )


def _candle(index: int, *, timeframe: Timeframe = Timeframe.M15) -> Candle:
    step = timedelta(minutes=15) if timeframe == Timeframe.M15 else timedelta(hours=1)
    open_time = BASE_TIME + (index * step)
    open_price = Decimal("1.1000") + (Decimal("0.0001") * Decimal(index))
    close_price = open_price + Decimal("0.0001")
    return Candle(
        provider="readiness-test",
        pair=PAIR,
        timeframe=timeframe,
        open_time=open_time,
        close_time=open_time + step,
        open=open_price,
        high=close_price + Decimal("0.0002"),
        low=open_price - Decimal("0.0002"),
        close=close_price,
        volume=Decimal("100"),
        is_closed=True,
    )


def _snapshot(candles: list[Candle]):
    return AnalysisEngine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=BASE_TIME,
        window_end=BASE_TIME + timedelta(minutes=45),
        as_of=BASE_TIME + timedelta(minutes=45),
        candles=candles,
        economic_events=[],
        moving_average_windows=(3,),
    )


def test_latest_closed_boundary_uses_existing_timeframes() -> None:
    as_of = datetime(2026, 7, 15, 10, 37, 12, tzinfo=UTC)

    assert latest_closed_boundary(timeframe=Timeframe.M15, as_of=as_of) == datetime(
        2026, 7, 15, 10, 30, tzinfo=UTC
    )
    assert latest_closed_boundary(timeframe=Timeframe.H1, as_of=as_of) == datetime(
        2026, 7, 15, 10, 0, tzinfo=UTC
    )


def test_planner_builds_deterministic_m15_and_h1_windows() -> None:
    planner = SnapshotReadinessPlanner()
    as_of = datetime(2026, 7, 15, 10, 37, tzinfo=UTC)

    plan = planner.build_plan(
        items=[
            _schedule_item(timeframe=Timeframe.H1, lookback_candle_count=2),
            _schedule_item(timeframe=Timeframe.M15, lookback_candle_count=4),
        ],
        as_of=as_of,
    )

    assert plan.project_phase == constants.PROJECT_PHASE
    assert [window.timeframe for window in plan.windows] == [Timeframe.H1, Timeframe.M15]
    assert plan.windows[0].window_start == datetime(2026, 7, 15, 8, 0, tzinfo=UTC)
    assert plan.windows[0].window_end == datetime(2026, 7, 15, 10, 0, tzinfo=UTC)
    assert plan.windows[1].window_start == datetime(2026, 7, 15, 9, 30, tzinfo=UTC)
    assert plan.windows[1].window_end == datetime(2026, 7, 15, 10, 30, tzinfo=UTC)
    assert plan.model_dump(mode="json") == planner.build_plan(
        items=[
            _schedule_item(timeframe=Timeframe.H1, lookback_candle_count=2),
            _schedule_item(timeframe=Timeframe.M15, lookback_candle_count=4),
        ],
        as_of=as_of,
    ).model_dump(mode="json")


def test_invalid_lookback_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _schedule_item(lookback_candle_count=0)

    with pytest.raises(ValueError, match="at least one schedule item"):
        SnapshotReadinessPlanner().build_plan(items=[], as_of=BASE_TIME)


def test_planner_normalizes_utc_and_never_ends_after_as_of() -> None:
    offset = timezone(timedelta(hours=2))
    as_of = datetime(2026, 7, 15, 12, 14, tzinfo=offset)

    plan = SnapshotReadinessPlanner().build_plan(items=[_schedule_item()], as_of=as_of)

    assert plan.as_of == datetime(2026, 7, 15, 10, 14, tzinfo=UTC)
    assert plan.windows[0].window_end == datetime(2026, 7, 15, 10, 0, tzinfo=UTC)
    assert plan.windows[0].window_end <= plan.windows[0].as_of


def test_digest_dedup_key_is_stable() -> None:
    snapshots = [_snapshot([_candle(0), _candle(1), _candle(2)])]
    builder = SnapshotDigestBuilder()

    first = builder.build_digest(
        snapshots=snapshots,
        generated_at=BASE_TIME + timedelta(minutes=45),
        as_of=BASE_TIME + timedelta(minutes=45),
    )
    second = builder.build_digest(
        snapshots=snapshots,
        generated_at=BASE_TIME + timedelta(minutes=45),
        as_of=BASE_TIME + timedelta(minutes=45),
    )

    assert first.dedup_key == second.dedup_key
    assert first.items[0].dedup_key == second.items[0].dedup_key


def test_digest_aggregates_statuses() -> None:
    ready = _snapshot([_candle(0), _candle(1), _candle(2)])
    incomplete = _snapshot([_candle(0), _candle(2)])
    blocked = _snapshot([_candle(0), _candle(0), _candle(1), _candle(2)])

    digest = SnapshotDigestBuilder().build_digest(
        snapshots=[ready, incomplete, blocked],
        generated_at=BASE_TIME + timedelta(minutes=45),
        as_of=BASE_TIME + timedelta(minutes=45),
    )

    assert digest.readiness_status == SnapshotDigestStatus.BLOCKED
    assert digest.ready_count == 1
    assert digest.incomplete_count == 1
    assert digest.blocked_count == 1
    assert [item.readiness_status for item in digest.items] == [
        SnapshotDigestStatus.READY,
        SnapshotDigestStatus.INCOMPLETE,
        SnapshotDigestStatus.BLOCKED,
    ]


def test_digest_payload_is_json_serializable_and_immutable() -> None:
    digest = SnapshotDigestBuilder().build_digest(
        snapshots=[_snapshot([_candle(0), _candle(1), _candle(2)])],
        generated_at=BASE_TIME + timedelta(minutes=45),
        as_of=BASE_TIME + timedelta(minutes=45),
    )

    data = digest.model_dump(mode="json")
    assert data["items"][0]["readiness_status"] == "READY"
    assert "phase_3i_persistent_digest_audit_foundation" in digest.model_dump_json()
    with pytest.raises(ValidationError):
        digest.ready_count = 99


def test_telegram_digest_formatting_is_neutral() -> None:
    digest = SnapshotDigestBuilder().build_digest(
        snapshots=[_snapshot([_candle(0), _candle(1), _candle(2)])],
        generated_at=BASE_TIME + timedelta(minutes=45),
        as_of=BASE_TIME + timedelta(minutes=45),
    )

    body = TelegramFormatter().format_snapshot_digest_body(digest)
    message = TelegramFormatter().format(MessageType.REPORT, body)

    assert message.startswith("📊 ")
    assert "Системный отчёт готовности" in message
    assert "EURUSD M15: READY" in message
    assert "Решений и указаний нет." in message


@pytest.mark.asyncio
async def test_digest_service_uses_repository_protocols() -> None:
    factory = FakeUnitOfWorkFactory(candles=[_candle(0), _candle(1), _candle(2)])
    service = ReadinessDigestService(AnalysisService(factory))

    payload = await service.build_payload(
        items=[_schedule_item()],
        as_of=BASE_TIME + timedelta(minutes=45),
    )

    assert payload.digest.readiness_status == SnapshotDigestStatus.READY
    assert payload.digest.items[0].input_candle_count == 3
    assert payload.digest.items[0].used_candle_count == 3
    assert payload.digest.items[0].no_candles_after_as_of_used is True
    assert payload.dedup_key == payload.digest.dedup_key
    assert "EURUSD M15: READY" in payload.text
```

### `tests/unit/test_scheduled_digest_delivery_foundation.py`

```python
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, cast

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.entities import Candle, Timeframe
from app.domain.entities.readiness import (
    SnapshotDigestStatus,
    SnapshotNotificationPayload,
    SnapshotScheduleItem,
)
from app.domain.entities.scheduled_digest import (
    ScheduledDigestConfig,
    ScheduledDigestDecisionReason,
    ScheduledDigestTick,
)
from app.domain.value_objects import CurrencyPair
from app.scheduler.jobs import register_jobs, scheduled_digest_delivery_job
from app.services.analysis_service import AnalysisService
from app.services.health_service import HealthService
from app.services.readiness_digest_service import ReadinessDigestService
from app.services.scheduled_digest_delivery_service import (
    InMemoryScheduledDigestDeliveryStore,
    ScheduledDigestDeliveryService,
    is_scheduled_digest_due,
)
from app.services.system_state_service import SystemStateService
from tests.fakes import FakeUnitOfWorkFactory

PAIR = CurrencyPair(value="EURUSD")
BASE_TIME = datetime(2026, 7, 15, 8, 0, tzinfo=UTC)


class FakeNotificationSender:
    def __init__(self) -> None:
        self.payloads: list[SnapshotNotificationPayload] = []

    async def send(self, payload: SnapshotNotificationPayload) -> None:
        self.payloads.append(payload)


class FailingReadinessDigestService:
    async def build_payload(
        self,
        *,
        items: tuple[SnapshotScheduleItem, ...],
        as_of: datetime,
    ) -> SnapshotNotificationPayload:
        raise RuntimeError("forced digest build failure")


class FakeScheduler:
    def __init__(self) -> None:
        self.job_ids: list[str] = []

    def add_job(self, *args: Any, **kwargs: Any) -> None:
        self.job_ids.append(str(kwargs["id"]))


def _schedule_config(*, enabled: bool = True, interval_minutes: int = 15) -> ScheduledDigestConfig:
    return ScheduledDigestConfig(
        enabled=enabled,
        interval_minutes=interval_minutes,
        items=(
            SnapshotScheduleItem(
                pair=PAIR,
                timeframe=Timeframe.M15,
                lookback_candle_count=3,
            ),
        ),
    )


def _candle(index: int) -> Candle:
    open_time = BASE_TIME + timedelta(minutes=15 * index)
    open_price = Decimal("1.1000") + (Decimal("0.0001") * Decimal(index))
    close_price = open_price + Decimal("0.0001")
    return Candle(
        provider="scheduled-digest-test",
        pair=PAIR,
        timeframe=Timeframe.M15,
        open_time=open_time,
        close_time=open_time + timedelta(minutes=15),
        open=open_price,
        high=close_price + Decimal("0.0002"),
        low=open_price - Decimal("0.0002"),
        close=close_price,
        volume=Decimal("100"),
        is_closed=True,
    )


def _service(
    *,
    config: ScheduledDigestConfig | None = None,
    sender: FakeNotificationSender | None = None,
    store: InMemoryScheduledDigestDeliveryStore | None = None,
) -> tuple[ScheduledDigestDeliveryService, FakeNotificationSender]:
    notification_sender = sender or FakeNotificationSender()
    factory = FakeUnitOfWorkFactory(candles=[_candle(0), _candle(1), _candle(2)])
    readiness_service = ReadinessDigestService(AnalysisService(factory))
    return (
        ScheduledDigestDeliveryService(
            config=config or _schedule_config(),
            readiness_digest_service=readiness_service,
            sender=notification_sender,
            delivery_store=store or InMemoryScheduledDigestDeliveryStore(),
            sender_name="fake_sender",
        ),
        notification_sender,
    )


@pytest.mark.asyncio
async def test_scheduled_digest_disabled_skip() -> None:
    service, sender = _service(config=_schedule_config(enabled=False))

    result = await service.run_tick(as_of=BASE_TIME + timedelta(minutes=45))

    assert result.skipped is True
    assert result.delivered is False
    assert result.decision.reason == ScheduledDigestDecisionReason.DISABLED
    assert result.payload is None
    assert sender.payloads == []


@pytest.mark.asyncio
async def test_scheduled_digest_not_due_skip() -> None:
    service, sender = _service(config=_schedule_config(interval_minutes=60))

    result = await service.run_tick(as_of=BASE_TIME + timedelta(minutes=45))

    assert result.skipped is True
    assert result.decision.reason == ScheduledDigestDecisionReason.NOT_DUE
    assert result.decision.is_due is False
    assert sender.payloads == []


@pytest.mark.asyncio
async def test_scheduled_digest_due_builds_payload_and_sends_once() -> None:
    service, sender = _service()

    result = await service.run_tick(as_of=BASE_TIME + timedelta(minutes=45))

    assert result.delivered is True
    assert result.skipped is False
    assert result.decision.reason == ScheduledDigestDecisionReason.DELIVERED
    assert result.payload is not None
    assert result.record is not None
    assert result.dedup_key == result.payload.dedup_key
    assert len(sender.payloads) == 1
    assert sender.payloads[0] == result.payload
    assert result.record.readiness_status == SnapshotDigestStatus.READY
    assert result.record.item_count == 1
    assert result.record.ready_count == 1
    assert result.record.items_summary == "EURUSD:M15"
    assert "Решений и указаний нет" in (result.record.payload_preview or "")
    assert "Системный отчёт готовности" in result.payload.text
    assert "Решений и указаний нет." in result.payload.text
    data = result.model_dump(mode="json")
    assert data["project_phase"] == constants.PROJECT_PHASE
    assert data["payload"]["project_phase"] == constants.PROJECT_PHASE
    with pytest.raises(ValidationError):
        result.delivered = False


@pytest.mark.asyncio
async def test_scheduled_digest_duplicate_dedup_key_skip() -> None:
    store = InMemoryScheduledDigestDeliveryStore()
    sender = FakeNotificationSender()
    service, _ = _service(store=store, sender=sender)
    as_of = BASE_TIME + timedelta(minutes=45)

    first = await service.run_tick(as_of=as_of)
    second = await service.run_tick(as_of=as_of)

    assert first.delivered is True
    assert second.skipped is True
    assert second.decision.reason == ScheduledDigestDecisionReason.DUPLICATE
    assert second.dedup_key == first.dedup_key
    assert len(sender.payloads) == 1
    stored = await store.get(first.dedup_key)
    assert stored == first.record


@pytest.mark.asyncio
async def test_scheduled_digest_no_items_skip() -> None:
    service, sender = _service(config=ScheduledDigestConfig(enabled=True, items=()))

    result = await service.run_tick(as_of=BASE_TIME + timedelta(minutes=45))

    assert result.skipped is True
    assert result.decision.reason == ScheduledDigestDecisionReason.NO_ITEMS
    assert sender.payloads == []


@pytest.mark.asyncio
async def test_scheduled_digest_build_failed_skip() -> None:
    sender = FakeNotificationSender()
    service = ScheduledDigestDeliveryService(
        config=_schedule_config(),
        readiness_digest_service=FailingReadinessDigestService(),
        sender=sender,
        delivery_store=InMemoryScheduledDigestDeliveryStore(),
    )

    result = await service.run_tick(as_of=BASE_TIME + timedelta(minutes=45))

    assert result.skipped is True
    assert result.decision.reason == ScheduledDigestDecisionReason.BUILD_FAILED
    assert result.payload is None
    assert sender.payloads == []


def test_scheduled_digest_tick_is_json_serializable_and_immutable() -> None:
    tick = ScheduledDigestTick(as_of=datetime(2026, 7, 15, 10, 45, tzinfo=UTC))

    data = tick.model_dump(mode="json")

    assert data["project_phase"] == constants.PROJECT_PHASE
    assert data["as_of"] == "2026-07-15T10:45:00Z"
    with pytest.raises(ValidationError):
        tick.as_of = BASE_TIME


def test_scheduled_digest_tick_normalizes_utc() -> None:
    tick = ScheduledDigestTick(
        as_of=datetime(2026, 7, 15, 12, 45, tzinfo=timezone(timedelta(hours=2)))
    )

    assert tick.as_of == datetime(2026, 7, 15, 10, 45, tzinfo=UTC)


def test_scheduled_digest_due_policy_is_deterministic() -> None:
    assert is_scheduled_digest_due(
        as_of=datetime(2026, 7, 15, 10, 45, tzinfo=UTC),
        interval_minutes=15,
    )
    assert not is_scheduled_digest_due(
        as_of=datetime(2026, 7, 15, 10, 46, tzinfo=UTC),
        interval_minutes=15,
    )
    assert not is_scheduled_digest_due(
        as_of=datetime(2026, 7, 15, 10, 45, 1, tzinfo=UTC),
        interval_minutes=15,
    )


@pytest.mark.asyncio
async def test_worker_callable_can_run_without_auto_registration() -> None:
    service, sender = _service()

    result = await scheduled_digest_delivery_job(
        service,
        as_of=BASE_TIME + timedelta(minutes=45),
    )

    assert result.delivered is True
    assert len(sender.payloads) == 1


def test_register_jobs_does_not_start_scheduled_digest_delivery_loop() -> None:
    scheduler = FakeScheduler()

    register_jobs(
        scheduler,
        system_state_service=cast(SystemStateService, object()),
        health_service=cast(HealthService, object()),
    )

    assert scheduler.job_ids == ["worker_heartbeat", "application_health_check"]
```


## Documentation Files Updated

- `README.md`
- `AGENTS.md`
- `PLANS.md`
- `docs/operations.md`
- `docs/database-schema.md`
- `docs/phase3i-verification-report.md`
- `docs/chatgpt-verification-packet.md`
