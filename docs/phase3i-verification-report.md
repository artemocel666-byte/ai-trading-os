# Phase 3I Verification Report

Generated: 2026-07-15T18:57:41Z

## Scope

Phase 3I implements persistent neutral scheduled digest delivery audit storage only. It records delivery deduplication keys and non-sensitive delivery metadata so neutral readiness digest deliveries can be audited across process restarts.

Phase 4 was not started. No strategy, trade signal generation, setup scoring, confidence scoring, AI agent, OpenAI call, broker API, paper trading, order execution, or real trading work was added.

## Current Phase

`PROJECT_PHASE = "phase_3i_persistent_digest_audit_foundation"`

## Implementation Summary

- Added `scheduled_digest_deliveries` migration and SQLAlchemy model.
- Added `SqlAlchemyScheduledDigestDeliveryStore` implementing the existing scheduled digest delivery store protocol.
- Changed persistent delivery audit recording to use PostgreSQL conflict-safe insert semantics for duplicate dedup keys.
- Extended `ScheduledDigestDeliveryRecord` with neutral readiness metadata and payload preview fields.
- Updated scheduled digest delivery service to populate neutral audit metadata while continuing to work with the in-memory store.
- Added unit, contract, and PostgreSQL integration coverage for persistence, duplicate-safe delivery skipping, UTC normalization, and safety boundaries.
- Kept scheduled delivery and integrations disabled by default.

## Verification Summary

| Check | Result |
| --- | --- |
| Host lock check | Passed |
| Host sync | Passed |
| Ruff format | Passed |
| Ruff check | Passed |
| Mypy | Passed |
| Host pytest | Passed |
| Security check | Passed |
| Docker build | Passed |
| PostgreSQL container | Healthy |
| Alembic current | `0003_phase3i_digest_audit (head)` |
| Alembic check | Passed, no new upgrade operations detected |
| Test DB migration | Passed |
| Docker integration run 1 | Passed |
| Docker integration run 2 | Passed |
| Docker compose config | Generated successfully |

## Exact Host Outputs

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

## Exact Docker Outputs

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

## Notes

- The local repository baseline commit is `901d864 Phase 3H Done`; the prompt listed expected commit `141ef71 Add Phase 3H scheduled digest delivery foundation`. Work continued from the actual local clean baseline.
- The successful host checks used `/Users/artem.otsel/.local/bin` in PATH because this Codex shell does not include that directory by default.
- Host integration tests are skipped unless `REQUIRE_INTEGRATION_TESTS=true`; the PostgreSQL integration suite was run twice in Docker against the same test database without cleanup and passed both times.
