# Phase 4A Verification Report

Generated: 2026-07-18T12:16:14Z

## Scope

Phase 4A starts Phase 4 but is contract-only. It defines immutable typed signal contract data models, validation rules, deterministic serialization, and deterministic fingerprinting for future signal objects.

Phase 4A does not generate signals, does not provide trading recommendations, does not calculate entries/stops/targets, does not calculate position size, does not call AI/OpenAI/LLM services, does not send Telegram signals, does not use broker APIs, does not execute orders, and does not enable paper or real trading. Contracts default to `NOT_ACTIONABLE`.

Phase 3J was not created or restored.

## Current Phase

`PROJECT_PHASE = "phase_4a_signal_contract_foundation"`

## Implementation Summary

- Added `SignalDirection`, `SignalLifecycleStatus`, and `SignalActionability` enums.
- Added immutable `SignalPricePlan`, `SignalRiskPlan`, and `SignalContract` models.
- Added UTC normalization, Decimal input safety, directional price validation, risk bounds, deterministic collection normalization, deterministic JSON serialization, and SHA-256 fingerprinting.
- Added unit tests for validation, immutability, serialization, fingerprint determinism, default `NOT_ACTIONABLE`, and project phase.
- Updated safety tests to allow signal vocabulary only inside explicit Phase 4A contract objects while continuing to forbid generation and execution behavior.
- Added no API routes, Telegram handlers, scheduler jobs, services, migrations, broker code, provider calls, OpenAI/LLM calls, paper trading, or real trading.

## Verification Summary

| Check | Result |
| --- | --- |
| Host lock check | Passed |
| Host sync | Passed |
| Ruff format | Passed |
| Ruff check | Passed |
| Mypy | Passed, 78 source files |
| Host pytest | Passed, 228 passed, 7 skipped, 1 warning |
| Security check | Passed, exit code 0 |
| Docker build | Passed |
| PostgreSQL container | Healthy |
| Alembic current | `0003_phase3i_digest_audit (head)` |
| Alembic check | Passed, no new upgrade operations detected |
| Test DB migration | Passed |
| Docker integration run 1 | Passed, 7 passed, 1 warning |
| Docker integration run 2 | Passed, 7 passed, 1 warning |
| Docker compose config | Generated successfully |

## Exact Host Outputs

### `uv lock --check`

Command: `uv lock --check`

Exit code: `0`

```text
Resolved 46 packages in 18ms
```

### `uv sync`

Command: `uv sync`

Exit code: `0`

```text
Resolved 46 packages in 3ms
Checked 43 packages in 10ms
```

### `uv run ruff format --check .`

Command: `uv run ruff format --check .`

Exit code: `0`

```text
111 files already formatted
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
Success: no issues found in 78 source files
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
collected 235 items

tests/contract/test_agent_contracts.py ......                            [  2%]
tests/contract/test_api_error_schema.py .                                [  2%]
tests/contract/test_architecture_boundaries.py ..                        [  3%]
tests/contract/test_provider_contracts.py .............................. [ 16%]
...............................                                          [ 29%]
tests/contract/test_safety_boundaries.py ....................            [ 38%]
tests/integration/test_database_and_api.py sssssss                       [ 41%]
tests/unit/test_analysis_snapshot_foundation.py ..........               [ 45%]
tests/unit/test_context_engine_foundation.py .............               [ 51%]
tests/unit/test_data_quality_foundation.py ...                           [ 52%]
tests/unit/test_domain_market_models.py ..................               [ 60%]
tests/unit/test_errors_and_redaction.py .......                          [ 62%]
tests/unit/test_feature_engine_foundation.py ...........                 [ 67%]
tests/unit/test_internal_api_key.py ....                                 [ 69%]
tests/unit/test_readiness_scheduler_foundation.py .........              [ 73%]
tests/unit/test_scheduled_digest_delivery_foundation.py ...........      [ 77%]
tests/unit/test_settings.py .........                                    [ 81%]
tests/unit/test_signal_contract_foundation.py ............               [ 86%]
tests/unit/test_system_state_service.py .....                            [ 88%]
tests/unit/test_telegram_commands.py ........                            [ 92%]
tests/unit/test_telegram_policy.py .....                                 [ 94%]
tests/unit/test_time.py ...                                              [ 95%]
tests/unit/test_unit_of_work_lifecycle.py ......                         [ 98%]
tests/unit/test_value_objects_and_enums.py ....                          [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /Users/artem.otsel/Documents/ai-trading-os/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================== 228 passed, 7 skipped, 1 warning in 0.83s ===================
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
 Image ai-trading-os-bot Building
 Image ai-trading-os-migrate Building
 Image ai-trading-os-api Building
 Image ai-trading-os-worker Building
#1 [internal] load local bake definitions
#1 reading from stdin 1.91kB done
#1 DONE 0.0s

#2 [migrate internal] load build definition from Dockerfile
#2 transferring dockerfile: 411B done
#2 DONE 0.0s

#3 [bot internal] load metadata for ghcr.io/astral-sh/uv:python3.12-bookworm-slim
#3 DONE 0.8s

#4 [worker internal] load .dockerignore
#4 transferring context: 143B done
#4 DONE 0.0s

#5 [migrate 1/5] FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58
#5 resolve ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58 0.0s done
#5 DONE 0.0s

#6 [api internal] load build context
#6 transferring context: 18.80kB 0.0s done
#6 DONE 0.0s

#7 [api 3/5] COPY pyproject.toml uv.lock* ./
#7 CACHED

#8 [api 2/5] WORKDIR /app
#8 CACHED

#9 [api 4/5] RUN uv sync --frozen --no-dev
#9 CACHED

#10 [api 5/5] COPY . .
#10 CACHED

#11 [bot] exporting to image
#11 exporting layers done
#11 exporting manifest sha256:b15fd1ccd5ea08f21ff8c28f50bf312d8b4c3788b3f6462d8b3539e3838fd787 done
#11 exporting config sha256:f367422c67d6a50b0862d7b86a170d4fe19b2baedcc3c584f4f2953b8fa79a83 done
#11 exporting attestation manifest sha256:c412f366743b859a309d61769871d541f57f6e6fdcfae304e0f69c479013998b 0.0s done
#11 exporting manifest list sha256:8e61ab29a1643ddb524dd8542404602535d6d78b1fdce4eaf9a8ad8590f0b80b done
#11 naming to docker.io/library/ai-trading-os-bot:latest done
#11 unpacking to docker.io/library/ai-trading-os-bot:latest done
#11 DONE 0.1s

#12 [api] exporting to image
#12 exporting layers done
#12 exporting manifest sha256:ac780751c37d77d73b762149b9fb8ca356e8250530b1e57d89b75aada0cde90b done
#12 exporting config sha256:9c45a93e67d313c4e32e9cd5b8f3a5a9f17195f3e95b84b3a228ce7a08ec6044 done
#12 exporting attestation manifest sha256:e1f1b8785680a204835bd3044c6abc28415692296ac86262222bf0b060e85d0d 0.0s done
#12 exporting manifest list sha256:8ae0518730f677851f18beaf0ad1f1a08c3e44a9d9d621eead5577be73f0cd9b done
#12 naming to docker.io/library/ai-trading-os-api:latest done
#12 unpacking to docker.io/library/ai-trading-os-api:latest done
#12 DONE 0.1s

#13 [migrate] exporting to image
#13 exporting layers done
#13 exporting manifest sha256:d369bb2d8be34128a814e59cef3a13d8ebf59b1e17e8d6bb4d27080d1a2ead0b done
#13 exporting config sha256:3b87c039d55def6eb0674816bf3008dba7af233271b9bfac5190b4f35bbbb419 done
#13 exporting attestation manifest sha256:489a1ffb4aa9ca268ad1d2e1b45bc1676e844af3511cdb71a0a6b68e4493fcfd 0.0s done
#13 exporting manifest list sha256:1d6458c24efb48266ab600cb929a71856ec3dd4ff59c24de4d7c62de0948408f done
#13 naming to docker.io/library/ai-trading-os-migrate:latest done
#13 unpacking to docker.io/library/ai-trading-os-migrate:latest done
#13 DONE 0.1s

#14 [worker] exporting to image
#14 exporting layers done
#14 exporting manifest sha256:820a1c148742512f94d41f94496e7f228dd36e5a753fac7c377eb82eb23ae095 done
#14 exporting config sha256:d46a495dc56eff6d37e22b05b47a4fa7bf335c9d272c8f29f28666bfe211a6d7 done
#14 exporting attestation manifest sha256:f79db324a3b72f973505aca9ca2f661d6c9bd6b5a64f2203843add086cf363d4 0.0s done
#14 exporting manifest list sha256:b901668935ed9fbfe44c6356908d23531f3eb04928e72ae5471d4a0d5159a7c4 done
#14 naming to docker.io/library/ai-trading-os-worker:latest done
#14 unpacking to docker.io/library/ai-trading-os-worker:latest done
#14 DONE 0.1s

#15 [worker] resolving provenance for metadata file
#15 DONE 0.0s

#16 [api] resolving provenance for metadata file
#16 DONE 0.0s

#17 [bot] resolving provenance for metadata file
#17 DONE 0.0s

#18 [migrate] resolving provenance for metadata file
#18 DONE 0.0s
 Image ai-trading-os-worker Built
 Image ai-trading-os-api Built
 Image ai-trading-os-bot Built
 Image ai-trading-os-migrate Built
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
NAME                       IMAGE                COMMAND                  SERVICE    CREATED         STATUS                   PORTS
ai-trading-os-postgres-1   postgres:16-alpine   "docker-entrypoint.s…"   postgres   4 minutes ago   Up 4 minutes (healthy)   5432/tcp
```

### `docker compose run --rm migrate alembic current`

Command: `docker compose run --rm migrate alembic current`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running
 Container ai-trading-os-postgres-1 Waiting
 Container ai-trading-os-postgres-1 Healthy
 Container ai-trading-os-migrate-run-489b06565fa5 Creating
 Container ai-trading-os-migrate-run-489b06565fa5 Created
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
 Container ai-trading-os-migrate-run-109055c459bb Creating
 Container ai-trading-os-migrate-run-109055c459bb Created
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
 Container ai-trading-os-migrate-run-6334ab9dc370 Creating
 Container ai-trading-os-migrate-run-6334ab9dc370 Created
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
 Container ai-trading-os-migrate-run-36e6960f25a2 Creating
 Container ai-trading-os-migrate-run-36e6960f25a2 Created
Downloading pygments (1.2MiB)
Downloading mypy (13.1MiB)
Downloading ruff (10.5MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 78ms
Bytecode compiled 1963 files in 407ms
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
========================= 7 passed, 1 warning in 0.36s =========================
```

### `Docker integration run 2: docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py`

Command: `docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running
 Container ai-trading-os-postgres-1 Waiting
 Container ai-trading-os-postgres-1 Healthy
 Container ai-trading-os-migrate-run-edc57ee9dd1e Creating
 Container ai-trading-os-migrate-run-edc57ee9dd1e Created
Downloading mypy (13.1MiB)
Downloading pygments (1.2MiB)
Downloading ruff (10.5MiB)
 Downloaded ruff
 Downloaded pygments
 Downloaded mypy
Installed 11 packages in 36ms
Bytecode compiled 1963 files in 398ms
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
========================= 7 passed, 1 warning in 0.36s =========================
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
