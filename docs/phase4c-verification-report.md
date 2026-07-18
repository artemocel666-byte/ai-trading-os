# Phase 4C Verification Report

Generated: 2026-07-18T13:17:54Z

## Scope

Phase 4C is strategy ruleset validation foundation only. It defines immutable validation issue/report models and a deterministic validator for the structure of Phase 4B `StrategyRuleSet` objects.

Phase 4C validates only the rule specification object itself. It does not evaluate rules against market data, indicators, economic events, context snapshots, analysis snapshots, or signal contracts. It does not implement a strategy engine, does not generate signals, does not provide trading recommendations, does not calculate entries/stops/targets, does not calculate position size, does not calculate setup score or confidence, does not call AI/OpenAI/LLM services, does not send Telegram signals, does not use broker APIs, does not execute orders, and does not enable paper or real trading. Rule specs and rule sets remain disabled/non-actionable.

Phase 3J was not created or restored.

## Current Phase

`PROJECT_PHASE = "phase_4c_strategy_ruleset_validation_foundation"`

## Implementation Summary

- Added `StrategyRuleSetValidationStatus` and `StrategyRuleSetValidationIssueCode` enums.
- Added immutable `StrategyRuleSetValidationIssue` and `StrategyRuleSetValidationReport` models.
- Added `StrategyRuleSetValidator` with a small static field registry and category-prefix compatibility checks.
- Added validation for disabled rule sets/rules, unknown field references, category/field mismatches, forbidden action/scoring/confidence language, and structurally invalid operator operands from unsafely constructed objects.
- Added deterministic issue ordering, deterministic JSON serialization, SHA-256 fingerprinting, UTC checked timestamp normalization, and `is_actionable=False`.
- Added unit tests for validation report immutability, UTC normalization, status outcomes, forbidden-language issues, deterministic serialization/fingerprints, issue ordering, no mutation, and validator input shape.
- Updated safety tests to allow strategy validation vocabulary only inside explicit Phase 4C validation files and tests while continuing to forbid runtime routes, handlers, jobs, services, market-data rule evaluation, signal generation, scoring, and execution behavior.
- Added no API routes, Telegram handlers, scheduler jobs, services that evaluate rules, migrations, provider calls, OpenAI/LLM calls, broker code, order execution, paper trading, or real trading.

## Verification Summary

| Check | Result |
| --- | --- |
| Host lock check | Passed |
| Host sync | Passed |
| Ruff format | Passed |
| Ruff check | Passed |
| Mypy | Passed |
| Host pytest | Passed, 287 passed, 7 skipped, 1 warning |
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
Resolved 46 packages in 27ms
```

### `uv sync`

Command: `uv sync`

Exit code: `0`

```text
STDERR:
Resolved 46 packages in 3ms
Checked 43 packages in 8ms
```

### `uv run ruff format --check .`

Command: `uv run ruff format --check .`

Exit code: `0`

```text
STDOUT:
116 files already formatted
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
Success: no issues found in 81 source files
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
collected 294 items

tests/contract/test_agent_contracts.py ......                            [  2%]
tests/contract/test_api_error_schema.py .                                [  2%]
tests/contract/test_architecture_boundaries.py ..                        [  3%]
tests/contract/test_provider_contracts.py .............................. [ 13%]
...............................                                          [ 23%]
tests/contract/test_safety_boundaries.py ............................... [ 34%]
..                                                                       [ 35%]
tests/integration/test_database_and_api.py sssssss                       [ 37%]
tests/unit/test_analysis_snapshot_foundation.py ..........               [ 40%]
tests/unit/test_context_engine_foundation.py .............               [ 45%]
tests/unit/test_data_quality_foundation.py ...                           [ 46%]
tests/unit/test_domain_market_models.py ..................               [ 52%]
tests/unit/test_errors_and_redaction.py .......                          [ 54%]
tests/unit/test_feature_engine_foundation.py ...........                 [ 58%]
tests/unit/test_internal_api_key.py ....                                 [ 59%]
tests/unit/test_readiness_scheduler_foundation.py .........              [ 62%]
tests/unit/test_scheduled_digest_delivery_foundation.py ...........      [ 66%]
tests/unit/test_settings.py .........                                    [ 69%]
tests/unit/test_signal_contract_foundation.py ............               [ 73%]
tests/unit/test_strategy_rule_specification_foundation.py .............. [ 78%]
...........                                                              [ 82%]
tests/unit/test_strategy_ruleset_validation_foundation.py .............. [ 87%]
.......                                                                  [ 89%]
tests/unit/test_system_state_service.py .....                            [ 91%]
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
================== 287 passed, 7 skipped, 1 warning in 0.99s ===================
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

#2 [bot internal] load build definition from Dockerfile
#2 transferring dockerfile: 411B done
#2 DONE 0.0s

#3 [migrate internal] load metadata for ghcr.io/astral-sh/uv:python3.12-bookworm-slim
#3 DONE 0.9s

#4 [worker internal] load .dockerignore
#4 transferring context: 143B done
#4 DONE 0.0s

#5 [api 1/5] FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58
#5 resolve ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58 done
#5 DONE 0.0s

#6 [bot internal] load build context
#6 transferring context: 412.65kB 0.0s done
#6 DONE 0.0s

#7 [migrate 2/5] WORKDIR /app
#7 CACHED

#8 [migrate 3/5] COPY pyproject.toml uv.lock* ./
#8 CACHED

#9 [migrate 4/5] RUN uv sync --frozen --no-dev
#9 CACHED

#10 [api 5/5] COPY . .
#10 DONE 0.1s

#11 [bot] exporting to image
#11 exporting layers 0.1s done
#11 ...

#12 [worker] exporting to image
#12 exporting layers 0.1s done
#12 exporting manifest sha256:300306424f4e396052573da7af4ac79ed1be00816c3614f4a51df8bd61b87f09 done
#12 exporting config sha256:9ee5dbe7f172ba6a8b990f974de51651580a6316acb7aeeef3c81925e1f216cd done
#12 exporting attestation manifest sha256:fefe4828728bcd9cfac1f648cd5a34215f7d13bcf9559991b8f98f443c28841b 0.0s done
#12 exporting manifest list sha256:a23cc0b6ddd535a2b5a768b9b840a87da5540792c22cdf659bb1384cc90c07a1 done
#12 naming to docker.io/library/ai-trading-os-worker:latest done
#12 unpacking to docker.io/library/ai-trading-os-worker:latest 0.0s done
#12 DONE 0.2s

#11 [bot] exporting to image
#11 exporting manifest sha256:3f6a258403526f2caff6d156c71a05e624d246af28ed5b979e925459c2c5de69 done
#11 exporting config sha256:691882a39c0c8570b44acf2636be3b061fb90b604c07d97c41548eba69c51989 done
#11 exporting attestation manifest sha256:f906bbadcbd24f55d2ee6138a74c0157de83ae3d9128c43a26b2ce224c091a60 0.0s done
#11 exporting manifest list sha256:426ae7a10ef2151374279cf2ce497043509fdee324655ee17c9909b676d0cb0f done
#11 naming to docker.io/library/ai-trading-os-bot:latest done
#11 unpacking to docker.io/library/ai-trading-os-bot:latest 0.0s done
#11 DONE 0.2s

#13 [migrate] exporting to image
#13 exporting layers 0.1s done
#13 exporting manifest sha256:1902a6a0120f067c137d559decc2bd29b318e85763cff3721ad3045e82e9e1f6 done
#13 exporting config sha256:b6957c7a9fe9e3c3ede44c1ac79abbdb8b046ff22547b01da1947186c82987d1 done
#13 exporting attestation manifest sha256:1b9d5ebaecfd1519c5156feb86e99bee680979c9a84998499a9b8bb869c38fff 0.0s done
#13 exporting manifest list sha256:f6aa30c215672ef7be94e0a6b1c724af85ba5166e4374beac70408fae76406aa done
#13 naming to docker.io/library/ai-trading-os-migrate:latest done
#13 unpacking to docker.io/library/ai-trading-os-migrate:latest 0.0s done
#13 DONE 0.2s

#14 [api] exporting to image
#14 exporting layers 0.1s done
#14 exporting manifest sha256:3f696663e70198dd242fe143c7c61fa4aeb7ba84dc5e483a389bd81b2a6628d1 done
#14 exporting config sha256:b327a86e2e647c9cd3c1cde89e3b5cf74541ea547ad31c1ba8fd6584cfe4fb2e done
#14 exporting attestation manifest sha256:527fdadb512cd34aaf67324bdd6cf17bcb667a751dbe1588310d26d995e03c20 0.0s done
#14 exporting manifest list sha256:c7130da79d67362f3eab8d9da8cbca3fab391bff5a2aa0fa58cdb40d751432e6 done
#14 naming to docker.io/library/ai-trading-os-api:latest done
#14 unpacking to docker.io/library/ai-trading-os-api:latest 0.0s done
#14 DONE 0.2s

#15 [bot] resolving provenance for metadata file
#15 DONE 0.0s

#16 [api] resolving provenance for metadata file
#16 DONE 0.1s

#17 [worker] resolving provenance for metadata file
#17 DONE 0.1s

#18 [migrate] resolving provenance for metadata file
#18 DONE 0.0s

STDERR:
 Image ai-trading-os-api Building
 Image ai-trading-os-worker Building
 Image ai-trading-os-bot Building
 Image ai-trading-os-migrate Building
 Image ai-trading-os-api Built
 Image ai-trading-os-bot Built
 Image ai-trading-os-migrate Built
 Image ai-trading-os-worker Built
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
 Container ai-trading-os-migrate-run-2ed043f4f30a Creating
 Container ai-trading-os-migrate-run-2ed043f4f30a Created
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
 Container ai-trading-os-migrate-run-21c61f2699d0 Creating
 Container ai-trading-os-migrate-run-21c61f2699d0 Created
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
 Container ai-trading-os-migrate-run-e220538d96fb Creating
 Container ai-trading-os-migrate-run-e220538d96fb Created
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
========================= 7 passed, 1 warning in 0.41s =========================

STDERR:
 Container ai-trading-os-postgres-1 Running
 Container ai-trading-os-postgres-1 Waiting
 Container ai-trading-os-postgres-1 Healthy
 Container ai-trading-os-migrate-run-37d9a17b7ab0 Creating
 Container ai-trading-os-migrate-run-37d9a17b7ab0 Created
Downloading pygments (1.2MiB)
Downloading ruff (10.5MiB)
Downloading mypy (13.1MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 93ms
Bytecode compiled 1963 files in 506ms
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
========================= 7 passed, 1 warning in 0.43s =========================

STDERR:
 Container ai-trading-os-postgres-1 Running
 Container ai-trading-os-postgres-1 Waiting
 Container ai-trading-os-postgres-1 Healthy
 Container ai-trading-os-migrate-run-4f1a70f2292c Creating
 Container ai-trading-os-migrate-run-4f1a70f2292c Created
Downloading pygments (1.2MiB)
Downloading ruff (10.5MiB)
Downloading mypy (13.1MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 51ms
Bytecode compiled 1963 files in 465ms
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
