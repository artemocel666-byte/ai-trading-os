# Phase 4B Verification Report

Generated: 2026-07-18T12:46:45Z

## Scope

Phase 4B is strategy rule specification foundation only. It defines immutable typed rule specification data models, validation rules, deterministic serialization, and deterministic fingerprinting for future strategy rule objects.

Phase 4B does not evaluate rules, does not implement a strategy engine, does not generate signals, does not provide trading recommendations, does not calculate entries/stops/targets, does not calculate position size, does not calculate setup score or confidence, does not call AI/OpenAI/LLM services, does not send Telegram signals, does not use broker APIs, does not execute orders, and does not enable paper or real trading. Rule specs and rule sets default to disabled/non-actionable.

Phase 3J was not created or restored.

## Current Phase

`PROJECT_PHASE = "phase_4b_strategy_rule_specification_foundation"`

## Implementation Summary

- Added `StrategyRuleOperator`, `StrategyRuleCategory`, and `StrategyRuleSeverity` enums.
- Added immutable `StrategyRuleValue`, `StrategyRuleCondition`, `StrategyRuleSpec`, and `StrategyRuleSet` models.
- Added UTC normalization, deterministic identifier validation, operator-specific value validation, duplicate rule-id protection, disabled defaults, deterministic warning/rule normalization, deterministic JSON serialization, and SHA-256 fingerprinting.
- Added typed value JSON encoding so Decimal rule values round-trip exactly without binary floating point.
- Added unit tests for validation, immutability, serialization, fingerprint determinism, disabled/non-actionable defaults, no scoring/confidence/action fields, and project phase.
- Updated safety tests to allow strategy/rule vocabulary only inside explicit Phase 4B specification objects while continuing to forbid evaluation, signal generation, scoring, and execution behavior.
- Added no API routes, Telegram handlers, scheduler jobs, services that evaluate rules, migrations, provider calls, OpenAI/LLM calls, broker code, order execution, paper trading, or real trading.

## Verification Summary

| Check | Result |
| --- | --- |
| Host lock check | Passed |
| Host sync | Passed |
| Ruff format | Passed |
| Ruff check | Passed |
| Mypy | Passed |
| Host pytest | Passed, 259 passed, 7 skipped, 1 warning |
| Security check | Passed |
| Docker build | Passed |
| PostgreSQL container | Passed |
| Alembic current | `0003_phase3i_digest_audit (head)` |
| Alembic check | Passed, no new upgrade operations detected |
| Test DB migration | Passed |
| Docker integration run 1 | Passed, 7 passed, 1 warning |
| Docker integration run 2 | Passed, 7 passed, 1 warning |
| Docker compose config | Passed |

## Exact Verification Outputs

### `uv lock --check`

Command: `uv lock --check`

Exit code: `0`

```text
STDERR:
Resolved 46 packages in 18ms
```

### `uv sync`

Command: `uv sync`

Exit code: `0`

```text
STDERR:
Resolved 46 packages in 2ms
Checked 43 packages in 9ms
```

### `uv run ruff format --check .`

Command: `uv run ruff format --check .`

Exit code: `0`

```text
STDOUT:
113 files already formatted
```

### `uv run ruff check .`

Command: `uv run ruff check .`

Exit code: `0`

```text
STDOUT:
All checks passed!
```

### `uv run mypy app`

Command: `uv run mypy app`

Exit code: `0`

```text
STDOUT:
Success: no issues found in 79 source files
```

### `uv run pytest`

Command: `uv run pytest`

Exit code: `0`

```text
STDOUT:
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/artem.otsel/Documents/ai-trading-os
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.14.1, asyncio-0.26.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 266 items

tests/contract/test_agent_contracts.py ......                            [  2%]
tests/contract/test_api_error_schema.py .                                [  2%]
tests/contract/test_architecture_boundaries.py ..                        [  3%]
tests/contract/test_provider_contracts.py .............................. [ 14%]
...............................                                          [ 26%]
tests/contract/test_safety_boundaries.py ..........................      [ 36%]
tests/integration/test_database_and_api.py sssssss                       [ 38%]
tests/unit/test_analysis_snapshot_foundation.py ..........               [ 42%]
tests/unit/test_context_engine_foundation.py .............               [ 47%]
tests/unit/test_data_quality_foundation.py ...                           [ 48%]
tests/unit/test_domain_market_models.py ..................               [ 55%]
tests/unit/test_errors_and_redaction.py .......                          [ 57%]
tests/unit/test_feature_engine_foundation.py ...........                 [ 62%]
tests/unit/test_internal_api_key.py ....                                 [ 63%]
tests/unit/test_readiness_scheduler_foundation.py .........              [ 66%]
tests/unit/test_scheduled_digest_delivery_foundation.py ...........      [ 71%]
tests/unit/test_settings.py .........                                    [ 74%]
tests/unit/test_signal_contract_foundation.py ............               [ 78%]
tests/unit/test_strategy_rule_specification_foundation.py .............. [ 84%]
...........                                                              [ 88%]
tests/unit/test_system_state_service.py .....                            [ 90%]
tests/unit/test_telegram_commands.py ........                            [ 93%]
tests/unit/test_telegram_policy.py .....                                 [ 95%]
tests/unit/test_time.py ...                                              [ 96%]
tests/unit/test_unit_of_work_lifecycle.py ......                         [ 98%]
tests/unit/test_value_objects_and_enums.py ....                          [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /Users/artem.otsel/Documents/ai-trading-os/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================== 259 passed, 7 skipped, 1 warning in 0.85s ===================
```

### `uv run python scripts/security_check.py`

Command: `uv run python scripts/security_check.py`

Exit code: `0`

```text
<no output>
```

### `docker compose build`

Command: `docker compose build`

Exit code: `0`

```text
STDOUT:
#1 [internal] load local bake definitions
#1 reading from stdin 1.91kB done
#1 DONE 0.0s

#2 [worker internal] load build definition from Dockerfile
#2 transferring dockerfile: 411B done
#2 DONE 0.0s

#3 [worker internal] load metadata for ghcr.io/astral-sh/uv:python3.12-bookworm-slim
#3 DONE 0.9s

#4 [api internal] load .dockerignore
#4 transferring context: 143B done
#4 DONE 0.0s

#5 [api 1/5] FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58
#5 resolve ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58 0.0s done
#5 DONE 0.0s

#6 [worker internal] load build context
#6 transferring context: 346.40kB 0.0s done
#6 DONE 0.0s

#7 [worker 3/5] COPY pyproject.toml uv.lock* ./
#7 CACHED

#8 [worker 2/5] WORKDIR /app
#8 CACHED

#9 [worker 4/5] RUN uv sync --frozen --no-dev
#9 CACHED

#10 [api 5/5] COPY . .
#10 DONE 0.1s

#11 [migrate] exporting to image
#11 exporting layers 0.1s done
#11 exporting manifest sha256:31bed7c8311e792c61623d204acf65ea1d9907a84f2968cc70e2de3abcd872ea done
#11 exporting config sha256:70bf5f89256b4fd8326570672a05d0d33a8500cecd592c8048b6bb63ab68cfc1 done
#11 exporting attestation manifest sha256:46d5cc1e6baf964f7c8599b5106ab0ab9b721f32a1b1d0df999fdbe490fc8f90 0.0s done
#11 exporting manifest list sha256:9c65b69ad1d66d1bca7b87a09140efde3c7d506888d6e5002e5a0af3d86987b7 done
#11 naming to docker.io/library/ai-trading-os-migrate:latest done
#11 unpacking to docker.io/library/ai-trading-os-migrate:latest
#11 unpacking to docker.io/library/ai-trading-os-migrate:latest 0.0s done
#11 DONE 0.2s

#12 [bot] exporting to image
#12 exporting layers 0.1s done
#12 exporting manifest sha256:81cb2951ae358ddce2fc0fdae7ffc4a74cf6e006378676fd50a7ee201a2812be done
#12 exporting config sha256:c09372ee86e6ee79ae18cbac00eb4d2f65ca27540177c394b529f82601782610 done
#12 exporting attestation manifest sha256:4325ec69affd4a7096bdd5ef9757b118f1f0c9d9ac3307742292fa871e444a53 0.0s done
#12 exporting manifest list sha256:7979d6153317a79e875a04bcf3a3dcace5da1897487091218d179b6555b7f8ca done
#12 naming to docker.io/library/ai-trading-os-bot:latest done
#12 unpacking to docker.io/library/ai-trading-os-bot:latest 0.0s done
#12 DONE 0.2s

#13 [api] exporting to image
#13 exporting layers 0.1s done
#13 exporting manifest sha256:c8c82cb87adbc66240d54512f6d124e672cd2930b0b6bb70ec997e40aac02a04 done
#13 exporting config sha256:0cfaba8e181163a485edb9372dcc5435a2b0a9101410fa0cdbd010a2c67dc904 done
#13 exporting attestation manifest sha256:f3532a32c3a54deffcbb3a792cbd43ee2d79e525b217e0e37e2822138a11c802 0.0s done
#13 exporting manifest list sha256:0e7b629409d5a4a62476c39dfac04be75d29940d5bf25ac7f6fbc20162598fe0 done
#13 naming to docker.io/library/ai-trading-os-api:latest done
#13 unpacking to docker.io/library/ai-trading-os-api:latest 0.0s done
#13 DONE 0.2s

#14 [worker] exporting to image
#14 exporting layers 0.1s done
#14 exporting manifest sha256:eadd4596f1ab17020b7c1f637671811c21fc95c6ff64bb256f1ec9116d8df37b done
#14 exporting config sha256:1ed9d6daca56021a6e30a67ca924d41b85080f6d0779c6891fb6556a7cf3b2cd done
#14 exporting attestation manifest sha256:fb01c7157362e3d708735e9d57b3f35c5cddafa63510daa53fb97af39daf7610 0.0s done
#14 exporting manifest list sha256:f5a3b5b2ef19015c2a367b9dce595552bdda79086ca200d518c2545179f5f1f6 done
#14 naming to docker.io/library/ai-trading-os-worker:latest done
#14 unpacking to docker.io/library/ai-trading-os-worker:latest 0.0s done
#14 DONE 0.2s

#15 [migrate] resolving provenance for metadata file
#15 DONE 0.0s

#16 [api] resolving provenance for metadata file
#16 DONE 0.0s

#17 [bot] resolving provenance for metadata file
#17 DONE 0.0s

#18 [worker] resolving provenance for metadata file
#18 DONE 0.0s

STDERR:
 Image ai-trading-os-bot Building
 Image ai-trading-os-migrate Building
 Image ai-trading-os-api Building
 Image ai-trading-os-worker Building
 Image ai-trading-os-migrate Built
 Image ai-trading-os-worker Built
 Image ai-trading-os-api Built
 Image ai-trading-os-bot Built
```

### `docker compose up -d postgres`

Command: `docker compose up -d postgres`

Exit code: `0`

```text
STDERR:
 Network ai-trading-os_default Creating
 Network ai-trading-os_default Created
 Container ai-trading-os-postgres-1 Creating
 Container ai-trading-os-postgres-1 Created
 Container ai-trading-os-postgres-1 Starting
 Container ai-trading-os-postgres-1 Started
```

### `docker compose run --rm migrate alembic current`

Command: `docker compose run --rm migrate alembic current`

Exit code: `0`

```text
STDOUT:
0003_phase3i_digest_audit (head)

STDERR:
 Container ai-trading-os-postgres-1 Running
 Container ai-trading-os-postgres-1 Waiting
 Container ai-trading-os-postgres-1 Healthy
 Container ai-trading-os-migrate-run-18119c95bfa4 Creating
 Container ai-trading-os-migrate-run-18119c95bfa4 Created
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

### `docker compose run --rm migrate alembic check`

Command: `docker compose run --rm migrate alembic check`

Exit code: `0`

```text
STDOUT:
No new upgrade operations detected.

STDERR:
 Container ai-trading-os-postgres-1 Running
 Container ai-trading-os-postgres-1 Waiting
 Container ai-trading-os-postgres-1 Healthy
 Container ai-trading-os-migrate-run-926e69c169f9 Creating
 Container ai-trading-os-migrate-run-926e69c169f9 Created
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.schemas
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.tables
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.types
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.constraints
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.defaults
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.comments
```

### `docker compose run --rm -e DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate alembic upgrade head`

Command: `docker compose run --rm -e DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate alembic upgrade head`

Exit code: `0`

```text
STDERR:
 Container ai-trading-os-postgres-1 Running
 Container ai-trading-os-postgres-1 Waiting
 Container ai-trading-os-postgres-1 Healthy
 Container ai-trading-os-migrate-run-2f5e17cbca14 Creating
 Container ai-trading-os-migrate-run-2f5e17cbca14 Created
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

### `Docker integration run 1: docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py`

Command: `docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py`

Exit code: `0`

```text
STDOUT:
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
========================= 7 passed, 1 warning in 0.38s =========================

STDERR:
 Container ai-trading-os-postgres-1 Running
 Container ai-trading-os-postgres-1 Waiting
 Container ai-trading-os-postgres-1 Healthy
 Container ai-trading-os-migrate-run-842522efe688 Creating
 Container ai-trading-os-migrate-run-842522efe688 Created
Downloading pygments (1.2MiB)
Downloading mypy (13.1MiB)
Downloading ruff (10.5MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 80ms
Bytecode compiled 1963 files in 476ms
```

### `Docker integration run 2: docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py`

Command: `docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py`

Exit code: `0`

```text
STDOUT:
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
========================= 7 passed, 1 warning in 0.35s =========================

STDERR:
 Container ai-trading-os-postgres-1 Running
 Container ai-trading-os-postgres-1 Waiting
 Container ai-trading-os-postgres-1 Healthy
 Container ai-trading-os-migrate-run-21885c81cf39 Creating
 Container ai-trading-os-migrate-run-21885c81cf39 Created
Downloading pygments (1.2MiB)
Downloading ruff (10.5MiB)
Downloading mypy (13.1MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 44ms
Bytecode compiled 1963 files in 410ms
```

### `docker compose config`

Command: `docker compose config`

Exit code: `0`

```text
STDOUT:
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
