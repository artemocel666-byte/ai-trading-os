# AI Trading OS - Phase 3B Verification Packet

Generated at: `2026-07-11T15:48:23Z`

## Scope

This packet documents Phase 3B: deterministic feature engine foundation. Phase 3B computes typed,
immutable, descriptive market/data feature snapshots from already-normalized Phase 3A closed candles
and economic events.

Phase 3B is uncommitted at packet generation time. Phase 3C was not started.

No strategy, signals, setup scoring, AI agents, OpenAI calls, broker APIs, paper trading, order
execution, or real trading were added or activated. Existing foundation-era signal/trading/paper
tables remain inactive.

## Git Metadata

- Branch: `main`
- Current commit hash: `03c3acdb403867825db38936196000f53b9fd899`

### `git status --short`

```text
 M AGENTS.md
 M PLANS.md
 M README.md
 M app/core/constants.py
 M app/domain/entities/__init__.py
 M docs/chatgpt-verification-packet.md
 M tests/contract/test_safety_boundaries.py
 M tests/integration/test_database_and_api.py
?? app/domain/entities/features.py
?? app/domain/feature_engine.py
?? app/services/feature_service.py
?? docs/phase3b-verification-report.md
?? tests/unit/test_feature_engine_foundation.py
```

### `git diff --stat`

```text
 AGENTS.md                                  |   11 +-
 PLANS.md                                   |   18 +-
 README.md                                  |   15 +-
 app/core/constants.py                      |    2 +-
 app/domain/entities/__init__.py            |   18 +
 docs/chatgpt-verification-packet.md        | 3502 +++++++++++++---------------
 tests/contract/test_safety_boundaries.py   |   31 +
 tests/integration/test_database_and_api.py |    2 +-
 8 files changed, 1679 insertions(+), 1920 deletions(-)
```

### `git log --oneline -3`

```text
03c3acd Add Phase 3A data quality foundation
9d68709 Document Phase 2 runtime verification
0848243 Complete Phase 2 data adapters
```

## Created Files

- `app/domain/entities/features.py`
- `app/domain/feature_engine.py`
- `app/services/feature_service.py`
- `docs/phase3b-verification-report.md`
- `tests/unit/test_feature_engine_foundation.py`

## Modified Files

- `AGENTS.md`
- `PLANS.md`
- `README.md`
- `app/core/constants.py`
- `app/domain/entities/__init__.py`
- `docs/chatgpt-verification-packet.md`
- `tests/contract/test_safety_boundaries.py`
- `tests/integration/test_database_and_api.py`

## Implementation Summary

- Updated `PROJECT_PHASE` to `phase_3b_feature_engine_foundation`.
- Added immutable Phase 3B feature models in `app/domain/entities/features.py`.
- Added deterministic closed-candle feature calculation in `app/domain/feature_engine.py`.
- Added `FeatureService` in `app/services/feature_service.py`, depending on UnitOfWork protocols.
- Added unit/service tests for exact calculations, UTC normalization, closed-candle-only enforcement,
  no future leakage, duplicate/gap/mismatch issues, event counts, empty/insufficient data behavior,
  immutability, and repository-backed service behavior.
- Added safety coverage confirming Phase 3B feature files do not introduce decision/execution terms.
- No migration was added; Phase 3B reads existing Phase 2/3A tables only.
- No API route, trading endpoint, signal endpoint, network call, provider call, secret, or API key was added.

## Verification Command Outputs

### `uv lock --check`

Exit code: `0`

```text
Resolved 46 packages in 16ms
```

### `uv sync`

Exit code: `0`

```text
Resolved 46 packages in 3ms
Checked 43 packages in 13ms
```

### `uv run ruff format --check .`

Exit code: `0`

```text
92 files already formatted
```

### `uv run ruff check .`

Exit code: `0`

```text
All checks passed!
```

### `uv run mypy app`

Exit code: `0`

```text
Success: no issues found in 66 source files
```

### `uv run pytest`

Exit code: `0`

```text
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/artem.otsel/Documents/ai-trading-os
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.14.1, asyncio-0.26.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 162 items

tests/contract/test_agent_contracts.py ......                            [  3%]
tests/contract/test_api_error_schema.py .                                [  4%]
tests/contract/test_architecture_boundaries.py ..                        [  5%]
tests/contract/test_provider_contracts.py .............................. [ 24%]
...............................                                          [ 43%]
tests/contract/test_safety_boundaries.py ..........                      [ 49%]
tests/integration/test_database_and_api.py sssss                         [ 52%]
tests/unit/test_data_quality_foundation.py ...                           [ 54%]
tests/unit/test_domain_market_models.py ..................               [ 65%]
tests/unit/test_errors_and_redaction.py .......                          [ 69%]
tests/unit/test_feature_engine_foundation.py ...........                 [ 76%]
tests/unit/test_internal_api_key.py ....                                 [ 79%]
tests/unit/test_settings.py .........                                    [ 84%]
tests/unit/test_system_state_service.py .....                            [ 87%]
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
================== 157 passed, 5 skipped, 1 warning in 0.73s ===================
```

### `uv run python scripts/security_check.py`

Exit code: `0`

```text
```

## Superseded Fallback Audit History

The following `.venv` command outputs are retained only as audit history from the earlier fallback
verification pass. They are superseded by the successful host `uv` outputs above.

### `.venv/bin/ruff format --check .`

Exit code: `0`

```text
92 files already formatted
```

### `.venv/bin/ruff check .`

Exit code: `0`

```text
All checks passed!
```

### `.venv/bin/mypy app`

Exit code: `0`

```text
Success: no issues found in 66 source files
```

### `.venv/bin/pytest`

Exit code: `0`

```text
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/artem.otsel/Documents/ai-trading-os
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.14.1, asyncio-0.26.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 162 items

tests/contract/test_agent_contracts.py ......                            [  3%]
tests/contract/test_api_error_schema.py .                                [  4%]
tests/contract/test_architecture_boundaries.py ..                        [  5%]
tests/contract/test_provider_contracts.py .............................. [ 24%]
...............................                                          [ 43%]
tests/contract/test_safety_boundaries.py ..........                      [ 49%]
tests/integration/test_database_and_api.py sssss                         [ 52%]
tests/unit/test_data_quality_foundation.py ...                           [ 54%]
tests/unit/test_domain_market_models.py ..................               [ 65%]
tests/unit/test_errors_and_redaction.py .......                          [ 69%]
tests/unit/test_feature_engine_foundation.py ...........                 [ 76%]
tests/unit/test_internal_api_key.py ....                                 [ 79%]
tests/unit/test_settings.py .........                                    [ 84%]
tests/unit/test_system_state_service.py .....                            [ 87%]
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
================== 157 passed, 5 skipped, 1 warning in 0.70s ===================
```

### `.venv/bin/python scripts/security_check.py`

Exit code: `0`

```text
```

### `docker compose build`

Exit code: `0`

```text
 Image ai-trading-os-bot Building 
 Image ai-trading-os-migrate Building 
 Image ai-trading-os-api Building 
 Image ai-trading-os-worker Building 
#1 [internal] load local bake definitions
#1 reading from stdin 1.91kB done
#1 DONE 0.0s

#2 [api internal] load build definition from Dockerfile
#2 transferring dockerfile: 411B done
#2 DONE 0.0s

#3 [api internal] load metadata for ghcr.io/astral-sh/uv:python3.12-bookworm-slim
#3 DONE 0.9s

#4 [worker internal] load .dockerignore
#4 transferring context: 143B done
#4 DONE 0.0s

#5 [migrate 1/5] FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58
#5 resolve ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58 0.0s done
#5 DONE 0.0s

#6 [api internal] load build context
#6 transferring context: 14.99kB 0.0s done
#6 DONE 0.0s

#7 [bot 4/5] RUN uv sync --frozen --no-dev
#7 CACHED

#8 [bot 2/5] WORKDIR /app
#8 CACHED

#9 [bot 3/5] COPY pyproject.toml uv.lock* ./
#9 CACHED

#10 [bot 5/5] COPY . .
#10 CACHED

#11 [worker] exporting to image
#11 exporting layers done
#11 exporting manifest sha256:75d5970a128d594a79cf241ecc6822be4a6ecb087d47835a6d16434da5331e5d done
#11 exporting config sha256:e58f38bc3916ca22e827b2c88659d1b6c0429642c1cf58a9764e6485c3251cec done
#11 exporting attestation manifest sha256:326070a17427897e1297a4a853107bd683853ce7324c9c2c373f90b0b5f3109c 0.0s done
#11 exporting manifest list sha256:3359dcb75c47a80668d76a99b995b9156480e9b8411e6595de0d7bb48cbe088f done
#11 naming to docker.io/library/ai-trading-os-worker:latest done
#11 unpacking to docker.io/library/ai-trading-os-worker:latest done
#11 DONE 0.1s

#12 [api] exporting to image
#12 exporting layers done
#12 exporting manifest sha256:a0a3fad2cf870fe09f41e11d2e36c861d749ba1be07d9c396d4699d38c2f63f8 done
#12 exporting config sha256:efd47a8301d0b468032ebe17b2cd6ae91dc7f25fec08b114007c8cd11bb5c103 done
#12 exporting attestation manifest sha256:7125df21bb25e8eb26ae3e60fe90d6301553525740616e358a82006a9ba04dfc 0.0s done
#12 exporting manifest list sha256:504fda9abbaab94f7adf9905d4490e3da5617b7232d15950aaf4563ec413c034 done
#12 naming to docker.io/library/ai-trading-os-api:latest done
#12 unpacking to docker.io/library/ai-trading-os-api:latest done
#12 DONE 0.1s

#13 [migrate] exporting to image
#13 exporting layers done
#13 exporting manifest sha256:1ec15e6b576705f0805ffe20dc4d050f40d0e4a66672a086c6eb0b990ed0aea8 done
#13 exporting config sha256:0e97928144bf4db74de54f8908468fd887e9f7f15739be5b598dd2bc3df1752e done
#13 exporting attestation manifest sha256:2ab67968ea3358e14300769819cd73c6c56596309054af4f2f5d8a655f57a54b 0.0s done
#13 exporting manifest list sha256:acec5f773f5ebcdffc371ff596bfb38b146153ebdc72266380e465e964938fcd done
#13 naming to docker.io/library/ai-trading-os-migrate:latest done
#13 unpacking to docker.io/library/ai-trading-os-migrate:latest done
#13 DONE 0.1s

#14 [bot] exporting to image
#14 exporting layers done
#14 exporting manifest sha256:1a35cd6952c69a536e2a7063a3998e4fb39b11b03047e1096bd514898a96606d done
#14 exporting config sha256:af538b39d44357aca9ea0ec49145559f0f80e9861a3eb5a6ccdf2dac9abb9d4f done
#14 exporting attestation manifest sha256:2bb2799894f4be0a898acd05b2ef44c19a13355184042231ba488a308cf91118 0.0s done
#14 exporting manifest list sha256:6580bf3b6b854c89cb2f6ad034cd6ce1ad3853abde86c1cbe496761910cc202a done
#14 naming to docker.io/library/ai-trading-os-bot:latest done
#14 unpacking to docker.io/library/ai-trading-os-bot:latest done
#14 DONE 0.1s

#15 [api] resolving provenance for metadata file
#15 DONE 0.0s

#16 [bot] resolving provenance for metadata file
#16 DONE 0.0s

#17 [migrate] resolving provenance for metadata file
#17 DONE 0.0s

#18 [worker] resolving provenance for metadata file
#18 DONE 0.0s
 Image ai-trading-os-migrate Built 
 Image ai-trading-os-worker Built 
 Image ai-trading-os-api Built 
 Image ai-trading-os-bot Built 
```

### `docker compose up -d postgres`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
```

### `docker compose run --rm migrate alembic current`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-79aec6754cb0 Creating 
 Container ai-trading-os-migrate-run-79aec6754cb0 Created 
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
0002_phase2_data_constraints (head)
```

### `docker compose run --rm migrate alembic check`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-f83ab10c141c Creating 
 Container ai-trading-os-migrate-run-f83ab10c141c Created 
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

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-309708b1496e Creating 
 Container ai-trading-os-migrate-run-309708b1496e Created 
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

### `docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-15672a776746 Creating 
 Container ai-trading-os-migrate-run-15672a776746 Created 
Downloading pygments (1.2MiB)
Downloading mypy (13.1MiB)
Downloading ruff (10.5MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 89ms
Bytecode compiled 1963 files in 445ms
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

### `docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-b3fee6416b36 Creating 
 Container ai-trading-os-migrate-run-b3fee6416b36 Created 
Downloading pygments (1.2MiB)
Downloading ruff (10.5MiB)
Downloading mypy (13.1MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 46ms
Bytecode compiled 1963 files in 402ms
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
========================= 5 passed, 1 warning in 0.31s =========================
```

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


## Skipped Checks

- Default host `.venv/bin/pytest` skipped 5 integration tests because PostgreSQL integration tests are gated unless a test database is configured/required for that process.

## Unavailable Checks

- None for the current authoritative Phase 3B verification pass. Host `uv` checks, Docker build,
  Alembic checks, test database migration, and repeated Docker integration tests are documented
  above with successful outputs.

## Remaining Risks

- Phase 3B changes are currently uncommitted.
- Phase 3B adds no migration and persists no feature snapshots; it computes deterministic in-memory snapshots from existing repository data.

## Phase Boundary Confirmation

- Phase 3C was not started.
- No strategy, signals, setup scoring, AI agents, OpenAI calls, broker APIs, paper trading, order execution, or real trading were added.
- The feature engine produces descriptive values only and does not produce directions, recommendations, entries, stops, targets, or position decisions.
- Existing signal, scan, agent-report, and paper-position schemas remain inactive.

## Traceability Table

| Requirement | Implementation file | Test file | Verification result |
|---|---|---|---|
| Project phase updated | `app/core/constants.py` | `tests/integration/test_database_and_api.py` | Docker integration tests passed twice |
| Immutable feature models | `app/domain/entities/features.py` | `tests/unit/test_feature_engine_foundation.py` | `.venv/bin/pytest` passed |
| UTC normalization | `app/domain/entities/features.py` | `tests/unit/test_feature_engine_foundation.py` | `.venv/bin/pytest` passed |
| Deterministic closed-candle feature calculations | `app/domain/feature_engine.py` | `tests/unit/test_feature_engine_foundation.py` | `.venv/bin/pytest` passed |
| Closed-candle-only enforcement | `app/domain/feature_engine.py` | `tests/unit/test_feature_engine_foundation.py` | `.venv/bin/pytest` passed |
| No future leakage with `as_of` | `app/domain/feature_engine.py` | `tests/unit/test_feature_engine_foundation.py` | `.venv/bin/pytest` passed |
| Duplicate candle detection | `app/domain/feature_engine.py` | `tests/unit/test_feature_engine_foundation.py` | `.venv/bin/pytest` passed |
| Missing candle/gap detection | `app/domain/feature_engine.py` | `tests/unit/test_feature_engine_foundation.py` | `.venv/bin/pytest` passed |
| Pair/timeframe mismatch detection | `app/domain/feature_engine.py` | `tests/unit/test_feature_engine_foundation.py` | `.venv/bin/pytest` passed |
| Economic event impact/currency counts | `app/domain/feature_engine.py` | `tests/unit/test_feature_engine_foundation.py` | `.venv/bin/pytest` passed |
| Empty/insufficient data behavior | `app/domain/feature_engine.py` | `tests/unit/test_feature_engine_foundation.py` | `.venv/bin/pytest` passed |
| Service reads repository protocols | `app/services/feature_service.py` | `tests/unit/test_feature_engine_foundation.py` | `.venv/bin/pytest` passed |
| Architecture boundaries | `app/domain/feature_engine.py`, `app/services/feature_service.py` | `tests/contract/test_architecture_boundaries.py` | `.venv/bin/pytest` passed |
| No decision/execution behavior | New Phase 3B files | `tests/contract/test_safety_boundaries.py`, `scripts/security_check.py` | `.venv` safety checks passed |
| Docker integration repeatability | `tests/integration/test_database_and_api.py` | `tests/integration/test_database_and_api.py` | Docker integration tests passed twice |

## Full Contents Of Changed Source Files

### `app/core/constants.py`

```python
PROJECT_PHASE = "phase_3b_feature_engine_foundation"
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
from app.domain.entities.features import (
    CandleFeatureSummary,
    CurrencyEventCount,
    EconomicEventFeatureSummary,
    EconomicImpactCount,
    FeatureIssue,
    FeatureIssueCode,
    FeatureWindow,
    MarketFeatureSnapshot,
)
from app.domain.entities.market_data import Candle, EconomicEvent, EconomicImpact, Timeframe

__all__ = [
    "Candle",
    "CandleAvailability",
    "CandleFeatureSummary",
    "CurrencyEventCount",
    "DataQualityIssue",
    "DataQualityIssueCode",
    "EconomicEvent",
    "EconomicEventAvailability",
    "EconomicEventFeatureSummary",
    "EconomicImpact",
    "EconomicImpactCount",
    "FeatureIssue",
    "FeatureIssueCode",
    "FeatureSnapshot",
    "FeatureWindow",
    "MarketFeatureSnapshot",
    "Timeframe",
    "UpsertResult",
    "build_feature_snapshot",
]
```

### `app/domain/entities/features.py`

```python
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.data_quality import DataQualityIssue
from app.domain.entities.market_data import EconomicImpact, Timeframe
from app.domain.value_objects import CurrencyPair


class FeatureIssueCode(StrEnum):
    NO_CANDLES = "NO_CANDLES"
    INSUFFICIENT_CANDLES = "INSUFFICIENT_CANDLES"
    WINDOW_NOT_ALIGNED = "WINDOW_NOT_ALIGNED"
    CANDLE_NOT_CLOSED = "CANDLE_NOT_CLOSED"
    CANDLE_AFTER_AS_OF = "CANDLE_AFTER_AS_OF"
    CANDLE_OUT_OF_RANGE = "CANDLE_OUT_OF_RANGE"
    CANDLE_PAIR_MISMATCH = "CANDLE_PAIR_MISMATCH"
    CANDLE_TIMEFRAME_MISMATCH = "CANDLE_TIMEFRAME_MISMATCH"
    DUPLICATE_CANDLE = "DUPLICATE_CANDLE"
    MISSING_CANDLE = "MISSING_CANDLE"
    EVENT_AFTER_AS_OF = "EVENT_AFTER_AS_OF"
    EVENT_OUT_OF_RANGE = "EVENT_OUT_OF_RANGE"


class FeatureIssue(BaseModel):
    code: FeatureIssueCode
    description: str = Field(min_length=1)
    timestamp: datetime | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_utc(cls, value: datetime | None) -> datetime | None:
        return normalize_to_utc(value) if value is not None else None


class FeatureWindow(BaseModel):
    pair: CurrencyPair
    timeframe: Timeframe
    window_start: datetime
    window_end: datetime
    as_of: datetime

    model_config = ConfigDict(frozen=True)

    @field_validator("window_start", "window_end", "as_of")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @model_validator(mode="after")
    def validate_window(self) -> Self:
        if self.window_end <= self.window_start:
            raise ValueError("feature window_end must be later than window_start")
        return self


class CandleFeatureSummary(BaseModel):
    expected_candle_count: int = Field(ge=0)
    input_candle_count: int = Field(ge=0)
    used_candle_count: int = Field(ge=0)
    latest_close: Decimal | None = None
    first_candle_open_time: datetime | None = None
    latest_candle_close_time: datetime | None = None
    simple_return: Decimal | None = None
    per_candle_returns: tuple[Decimal, ...] = ()
    rolling_close_mean_window: int = Field(ge=1)
    rolling_close_means: tuple[Decimal, ...] = ()
    rolling_high_low_ranges: tuple[Decimal, ...] = ()
    average_candle_range: Decimal | None = None
    average_body_size: Decimal | None = None
    volume_observed_count: int = Field(default=0, ge=0)
    volume_sum: Decimal | None = None
    volume_average: Decimal | None = None
    true_ranges: tuple[Decimal, ...] = ()
    average_true_range: Decimal | None = None
    market_data_complete: bool

    model_config = ConfigDict(frozen=True)

    @field_validator("first_candle_open_time", "latest_candle_close_time")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime | None) -> datetime | None:
        return normalize_to_utc(value) if value is not None else None


class EconomicImpactCount(BaseModel):
    impact: EconomicImpact
    count: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)


class CurrencyEventCount(BaseModel):
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    count: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)


class EconomicEventFeatureSummary(BaseModel):
    input_event_count: int = Field(ge=0)
    used_event_count: int = Field(ge=0)
    counts_by_impact: tuple[EconomicImpactCount, ...] = ()
    counts_by_currency: tuple[CurrencyEventCount, ...] = ()

    model_config = ConfigDict(frozen=True)


class MarketFeatureSnapshot(BaseModel):
    window: FeatureWindow
    candle_summary: CandleFeatureSummary
    economic_event_summary: EconomicEventFeatureSummary
    quality_issues: tuple[FeatureIssue, ...] = ()
    data_quality_issues: tuple[DataQualityIssue, ...] = ()

    model_config = ConfigDict(frozen=True)

    @property
    def quality_ok(self) -> bool:
        return not self.quality_issues and not self.data_quality_issues
```

### `app/domain/feature_engine.py`

```python
from collections import Counter
from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal

from app.core.time import normalize_to_utc
from app.domain.entities.data_quality import TIMEFRAME_TO_DELTA, build_feature_snapshot
from app.domain.entities.features import (
    CandleFeatureSummary,
    CurrencyEventCount,
    EconomicEventFeatureSummary,
    EconomicImpactCount,
    FeatureIssue,
    FeatureIssueCode,
    FeatureWindow,
    MarketFeatureSnapshot,
)
from app.domain.entities.market_data import Candle, EconomicEvent, Timeframe
from app.domain.value_objects import CurrencyPair


class MarketFeatureEngine:
    def build_snapshot(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        window_start: datetime,
        window_end: datetime,
        as_of: datetime,
        candles: Sequence[Candle],
        economic_events: Sequence[EconomicEvent] = (),
        rolling_window_size: int = 3,
    ) -> MarketFeatureSnapshot:
        window = FeatureWindow(
            pair=pair,
            timeframe=timeframe,
            window_start=window_start,
            window_end=window_end,
            as_of=as_of,
        )
        if rolling_window_size < 1:
            raise ValueError("rolling_window_size must be at least 1")

        start_utc = window.window_start
        end_utc = window.window_end
        as_of_utc = window.as_of
        expected_open_times = _expected_open_times(
            timeframe=timeframe,
            window_start=start_utc,
            window_end=end_utc,
        )
        issues: list[FeatureIssue] = []
        if _is_unaligned_window(timeframe=timeframe, start_at=start_utc, end_at=end_utc):
            issues.append(
                FeatureIssue(
                    code=FeatureIssueCode.WINDOW_NOT_ALIGNED,
                    description="Feature window is not an exact multiple of the timeframe.",
                )
            )

        sorted_candles = sorted(candles, key=lambda candle: (candle.open_time, candle.provider))
        usable_candidates: list[Candle] = []
        for candle in sorted_candles:
            if not candle.is_closed:
                issues.append(
                    FeatureIssue(
                        code=FeatureIssueCode.CANDLE_NOT_CLOSED,
                        description="Open candle excluded from feature calculation.",
                        timestamp=candle.open_time,
                    )
                )
                continue
            if candle.pair != pair:
                issues.append(
                    FeatureIssue(
                        code=FeatureIssueCode.CANDLE_PAIR_MISMATCH,
                        description="Candle pair does not match the requested pair.",
                        timestamp=candle.open_time,
                    )
                )
                continue
            if candle.timeframe != timeframe:
                issues.append(
                    FeatureIssue(
                        code=FeatureIssueCode.CANDLE_TIMEFRAME_MISMATCH,
                        description="Candle timeframe does not match the requested timeframe.",
                        timestamp=candle.open_time,
                    )
                )
                continue
            if candle.open_time < start_utc or candle.close_time > end_utc:
                issues.append(
                    FeatureIssue(
                        code=FeatureIssueCode.CANDLE_OUT_OF_RANGE,
                        description="Candle is outside the requested feature window.",
                        timestamp=candle.open_time,
                    )
                )
                continue
            if candle.close_time > as_of_utc:
                issues.append(
                    FeatureIssue(
                        code=FeatureIssueCode.CANDLE_AFTER_AS_OF,
                        description="Candle closes after the feature as_of timestamp.",
                        timestamp=candle.close_time,
                    )
                )
                continue
            usable_candidates.append(candle)

        duplicate_open_times = _duplicate_open_times(usable_candidates)
        for open_time in duplicate_open_times:
            issues.append(
                FeatureIssue(
                    code=FeatureIssueCode.DUPLICATE_CANDLE,
                    description="Duplicate candle open time in feature window.",
                    timestamp=open_time,
                )
            )

        usable_candles = _dedupe_candles_by_open_time(usable_candidates)
        observed_open_times = {candle.open_time for candle in usable_candles}
        for expected_open_time in expected_open_times:
            if expected_open_time not in observed_open_times:
                issues.append(
                    FeatureIssue(
                        code=FeatureIssueCode.MISSING_CANDLE,
                        description="Expected candle is missing from feature window.",
                        timestamp=expected_open_time,
                    )
                )

        if not usable_candles:
            issues.append(
                FeatureIssue(
                    code=FeatureIssueCode.NO_CANDLES,
                    description="No usable closed candles are available for feature calculation.",
                )
            )
        elif len(usable_candles) < rolling_window_size:
            issues.append(
                FeatureIssue(
                    code=FeatureIssueCode.INSUFFICIENT_CANDLES,
                    description="Not enough candles are available for the rolling window.",
                    timestamp=usable_candles[-1].close_time,
                )
            )

        sorted_events = sorted(
            economic_events,
            key=lambda event: (event.scheduled_at, event.currency, event.provider_event_id),
        )
        usable_events: list[EconomicEvent] = []
        for event in sorted_events:
            if event.scheduled_at < start_utc or event.scheduled_at >= end_utc:
                issues.append(
                    FeatureIssue(
                        code=FeatureIssueCode.EVENT_OUT_OF_RANGE,
                        description="Economic event is outside the requested feature window.",
                        timestamp=event.scheduled_at,
                    )
                )
                continue
            if event.scheduled_at > as_of_utc:
                issues.append(
                    FeatureIssue(
                        code=FeatureIssueCode.EVENT_AFTER_AS_OF,
                        description=(
                            "Economic event is scheduled after the feature as_of timestamp."
                        ),
                        timestamp=event.scheduled_at,
                    )
                )
                continue
            usable_events.append(event)

        data_quality_snapshot = build_feature_snapshot(
            pair=pair,
            timeframe=timeframe,
            window_start=start_utc,
            window_end=end_utc,
            candles=candles,
            economic_events=economic_events,
        )
        return MarketFeatureSnapshot(
            window=window,
            candle_summary=_build_candle_summary(
                expected_candle_count=len(expected_open_times),
                input_candle_count=len(candles),
                candles=usable_candles,
                rolling_window_size=rolling_window_size,
                market_data_complete=_market_data_complete(issues),
            ),
            economic_event_summary=_build_event_summary(
                input_event_count=len(economic_events),
                events=usable_events,
            ),
            quality_issues=tuple(issues),
            data_quality_issues=data_quality_snapshot.quality_issues,
        )


def _is_unaligned_window(*, timeframe: Timeframe, start_at: datetime, end_at: datetime) -> bool:
    delta = TIMEFRAME_TO_DELTA[timeframe]
    expected_count = len(
        _expected_open_times(timeframe=timeframe, window_start=start_at, window_end=end_at)
    )
    return start_at + (expected_count * delta) != end_at


def _expected_open_times(
    *,
    timeframe: Timeframe,
    window_start: datetime,
    window_end: datetime,
) -> tuple[datetime, ...]:
    start_utc = normalize_to_utc(window_start)
    end_utc = normalize_to_utc(window_end)
    delta = TIMEFRAME_TO_DELTA[timeframe]
    expected: list[datetime] = []
    cursor = start_utc
    while cursor + delta <= end_utc:
        expected.append(cursor)
        cursor += delta
    return tuple(expected)


def _duplicate_open_times(candles: Sequence[Candle]) -> tuple[datetime, ...]:
    counts = Counter(candle.open_time for candle in candles)
    return tuple(sorted(open_time for open_time, count in counts.items() if count > 1))


def _dedupe_candles_by_open_time(candles: Sequence[Candle]) -> tuple[Candle, ...]:
    selected: dict[datetime, Candle] = {}
    for candle in sorted(candles, key=lambda item: (item.open_time, item.provider)):
        selected.setdefault(candle.open_time, candle)
    return tuple(selected[open_time] for open_time in sorted(selected))


def _build_candle_summary(
    *,
    expected_candle_count: int,
    input_candle_count: int,
    candles: Sequence[Candle],
    rolling_window_size: int,
    market_data_complete: bool,
) -> CandleFeatureSummary:
    candle_ranges = tuple(candle.high - candle.low for candle in candles)
    body_sizes = tuple(abs(candle.close - candle.open) for candle in candles)
    per_candle_returns = tuple((candle.close - candle.open) / candle.open for candle in candles)
    volumes = tuple(candle.volume for candle in candles if candle.volume is not None)
    true_ranges = _true_ranges(candles)
    return CandleFeatureSummary(
        expected_candle_count=expected_candle_count,
        input_candle_count=input_candle_count,
        used_candle_count=len(candles),
        latest_close=candles[-1].close if candles else None,
        first_candle_open_time=candles[0].open_time if candles else None,
        latest_candle_close_time=candles[-1].close_time if candles else None,
        simple_return=((candles[-1].close - candles[0].open) / candles[0].open)
        if candles
        else None,
        per_candle_returns=per_candle_returns,
        rolling_close_mean_window=rolling_window_size,
        rolling_close_means=_rolling_close_means(candles, rolling_window_size),
        rolling_high_low_ranges=_rolling_high_low_ranges(candles, rolling_window_size),
        average_candle_range=_mean(candle_ranges),
        average_body_size=_mean(body_sizes),
        volume_observed_count=len(volumes),
        volume_sum=sum(volumes) if volumes else None,
        volume_average=_mean(volumes),
        true_ranges=true_ranges,
        average_true_range=_mean(true_ranges),
        market_data_complete=market_data_complete,
    )


def _true_ranges(candles: Sequence[Candle]) -> tuple[Decimal, ...]:
    ranges: list[Decimal] = []
    previous_close: Decimal | None = None
    for candle in candles:
        high_low = candle.high - candle.low
        if previous_close is None:
            true_range = high_low
        else:
            true_range = max(
                high_low,
                abs(candle.high - previous_close),
                abs(candle.low - previous_close),
            )
        ranges.append(true_range)
        previous_close = candle.close
    return tuple(ranges)


def _rolling_close_means(candles: Sequence[Candle], window_size: int) -> tuple[Decimal, ...]:
    means: list[Decimal] = []
    for index in range(window_size, len(candles) + 1):
        window = candles[index - window_size : index]
        means.append(sum(candle.close for candle in window) / Decimal(window_size))
    return tuple(means)


def _rolling_high_low_ranges(candles: Sequence[Candle], window_size: int) -> tuple[Decimal, ...]:
    ranges: list[Decimal] = []
    for index in range(window_size, len(candles) + 1):
        window = candles[index - window_size : index]
        ranges.append(max(candle.high for candle in window) - min(candle.low for candle in window))
    return tuple(ranges)


def _mean(values: Sequence[Decimal]) -> Decimal | None:
    if not values:
        return None
    return sum(values) / Decimal(len(values))


def _build_event_summary(
    *,
    input_event_count: int,
    events: Sequence[EconomicEvent],
) -> EconomicEventFeatureSummary:
    impact_counts = Counter(event.impact for event in events)
    currency_counts = Counter(event.currency for event in events)
    return EconomicEventFeatureSummary(
        input_event_count=input_event_count,
        used_event_count=len(events),
        counts_by_impact=tuple(
            EconomicImpactCount(impact=impact, count=impact_counts[impact])
            for impact in sorted(impact_counts, key=lambda value: value.value)
        ),
        counts_by_currency=tuple(
            CurrencyEventCount(currency=currency, count=currency_counts[currency])
            for currency in sorted(currency_counts)
        ),
    )


def _market_data_complete(issues: Sequence[FeatureIssue]) -> bool:
    blocking_codes = {
        FeatureIssueCode.NO_CANDLES,
        FeatureIssueCode.INSUFFICIENT_CANDLES,
        FeatureIssueCode.WINDOW_NOT_ALIGNED,
        FeatureIssueCode.CANDLE_NOT_CLOSED,
        FeatureIssueCode.CANDLE_AFTER_AS_OF,
        FeatureIssueCode.CANDLE_OUT_OF_RANGE,
        FeatureIssueCode.CANDLE_PAIR_MISMATCH,
        FeatureIssueCode.CANDLE_TIMEFRAME_MISMATCH,
        FeatureIssueCode.DUPLICATE_CANDLE,
        FeatureIssueCode.MISSING_CANDLE,
    }
    return not any(issue.code in blocking_codes for issue in issues)
```

### `app/services/feature_service.py`

```python
from collections.abc import Callable, Sequence
from datetime import datetime

from app.domain.entities import Timeframe
from app.domain.entities.features import MarketFeatureSnapshot
from app.domain.feature_engine import MarketFeatureEngine
from app.domain.interfaces.unit_of_work import UnitOfWork
from app.domain.value_objects import CurrencyPair

UnitOfWorkFactory = Callable[[], UnitOfWork]


class FeatureService:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        *,
        engine: MarketFeatureEngine | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._engine = engine or MarketFeatureEngine()

    async def build_market_snapshot(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        window_start: datetime,
        window_end: datetime,
        as_of: datetime,
        currencies: Sequence[str] | None = None,
        provider: str | None = None,
        rolling_window_size: int = 3,
    ) -> MarketFeatureSnapshot:
        event_currencies = (
            list(currencies)
            if currencies is not None
            else [
                pair.base_currency,
                pair.quote_currency,
            ]
        )
        async with self._uow_factory() as uow:
            candles = await uow.candles.list_range(
                pair=pair,
                timeframe=timeframe,
                start_at=window_start,
                end_at=window_end,
                provider=provider,
            )
            events = await uow.economic_events.list_window(
                start_at=window_start,
                end_at=window_end,
                currencies=event_currencies,
                provider=provider,
            )
        return self._engine.build_snapshot(
            pair=pair,
            timeframe=timeframe,
            window_start=window_start,
            window_end=window_end,
            as_of=as_of,
            candles=candles,
            economic_events=events,
            rolling_window_size=rolling_window_size,
        )
```


## Full Contents Of New And Changed Tests

### `tests/unit/test_feature_engine_foundation.py`

```python
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from types import TracebackType
from typing import Self

import pytest
from pydantic import ValidationError

from app.domain.entities import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.entities.features import FeatureIssueCode, MarketFeatureSnapshot
from app.domain.feature_engine import MarketFeatureEngine
from app.domain.value_objects import CurrencyPair
from app.services.feature_service import FeatureService

PAIR = CurrencyPair(value="EURUSD")
OTHER_PAIR = CurrencyPair(value="GBPUSD")
START = datetime(2026, 7, 8, 8, 0, tzinfo=UTC)


def _candle(
    index: int,
    *,
    provider: str = "unit",
    pair: CurrencyPair = PAIR,
    timeframe: Timeframe = Timeframe.M15,
    open_value: str = "100",
    high: str = "110",
    low: str = "95",
    close: str = "105",
    volume: str | None = "10",
) -> Candle:
    open_time = START + timedelta(minutes=15 * index)
    return Candle(
        provider=provider,
        pair=pair,
        timeframe=timeframe,
        open_time=open_time,
        close_time=open_time + timedelta(minutes=15),
        open=Decimal(open_value),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal(close),
        volume=Decimal(volume) if volume is not None else None,
        is_closed=True,
    )


def _event(
    minutes: int,
    *,
    currency: str = "EUR",
    impact: EconomicImpact = EconomicImpact.HIGH,
    provider_event_id: str = "event",
) -> EconomicEvent:
    return EconomicEvent(
        provider="unit",
        provider_event_id=provider_event_id,
        title="Consumer Price Index",
        currency=currency,
        country="Eurozone",
        impact=impact,
        scheduled_at=START + timedelta(minutes=minutes),
        actual=Decimal("2.2"),
        forecast=Decimal("2.1"),
        previous=Decimal("2.0"),
        fetched_at=START,
    )


def _engine() -> MarketFeatureEngine:
    return MarketFeatureEngine()


def _issue_codes(snapshot: MarketFeatureSnapshot) -> set[FeatureIssueCode]:
    return {issue.code for issue in snapshot.quality_issues}


def test_feature_engine_calculates_exact_deterministic_decimal_features() -> None:
    candles = [
        _candle(2, open_value="110", high="115", low="108", close="112", volume=None),
        _candle(0, open_value="100", high="110", low="95", close="105", volume="10"),
        _candle(1, open_value="105", high="112", low="104", close="110", volume="20"),
    ]

    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=45),
        as_of=START + timedelta(minutes=45),
        candles=candles,
        rolling_window_size=2,
    )

    summary = snapshot.candle_summary
    assert snapshot.quality_ok is True
    assert summary.expected_candle_count == 3
    assert summary.input_candle_count == 3
    assert summary.used_candle_count == 3
    assert summary.latest_close == Decimal("112")
    assert summary.latest_candle_close_time == START + timedelta(minutes=45)
    assert summary.simple_return == Decimal("0.12")
    assert summary.per_candle_returns == (
        Decimal("0.05"),
        Decimal("5") / Decimal("105"),
        Decimal("2") / Decimal("110"),
    )
    assert summary.rolling_close_mean_window == 2
    assert summary.rolling_close_means == (Decimal("107.5"), Decimal("111"))
    assert summary.rolling_high_low_ranges == (Decimal("17"), Decimal("11"))
    assert summary.average_candle_range == Decimal("10")
    assert summary.average_body_size == Decimal("4")
    assert summary.volume_observed_count == 2
    assert summary.volume_sum == Decimal("30")
    assert summary.volume_average == Decimal("15")
    assert summary.true_ranges == (Decimal("15"), Decimal("8"), Decimal("7"))
    assert summary.average_true_range == Decimal("10")
    assert summary.market_data_complete is True


def test_feature_models_normalize_datetimes_to_utc() -> None:
    stockholm = timezone(timedelta(hours=2))
    candle = _candle(0).model_copy(
        update={
            "open_time": datetime(2026, 7, 8, 10, 0, tzinfo=stockholm),
            "close_time": datetime(2026, 7, 8, 10, 15, tzinfo=stockholm),
        }
    )

    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=datetime(2026, 7, 8, 10, 0, tzinfo=stockholm),
        window_end=datetime(2026, 7, 8, 10, 15, tzinfo=stockholm),
        as_of=datetime(2026, 7, 8, 10, 15, tzinfo=stockholm),
        candles=[candle],
        rolling_window_size=1,
    )

    assert snapshot.window.window_start == START
    assert snapshot.window.window_end == START + timedelta(minutes=15)
    assert snapshot.window.as_of == START + timedelta(minutes=15)


def test_feature_engine_excludes_future_candles_and_events_after_as_of() -> None:
    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=45),
        as_of=START + timedelta(minutes=30),
        candles=[_candle(0), _candle(1), _candle(2)],
        economic_events=[
            _event(20, provider_event_id="included"),
            _event(40, provider_event_id="future"),
        ],
        rolling_window_size=2,
    )

    assert snapshot.candle_summary.used_candle_count == 2
    assert snapshot.economic_event_summary.used_event_count == 1
    assert FeatureIssueCode.CANDLE_AFTER_AS_OF in _issue_codes(snapshot)
    assert FeatureIssueCode.EVENT_AFTER_AS_OF in _issue_codes(snapshot)


def test_feature_engine_reports_duplicate_candles_without_weakening_upsert_semantics() -> None:
    duplicate = _candle(0, provider="duplicate")

    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        candles=[_candle(0), duplicate, _candle(1)],
        rolling_window_size=2,
    )

    assert snapshot.candle_summary.used_candle_count == 2
    assert FeatureIssueCode.DUPLICATE_CANDLE in _issue_codes(snapshot)
    assert snapshot.candle_summary.market_data_complete is False


def test_feature_engine_reports_missing_candle_gaps() -> None:
    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=45),
        as_of=START + timedelta(minutes=45),
        candles=[_candle(0), _candle(2)],
        rolling_window_size=2,
    )

    assert snapshot.candle_summary.used_candle_count == 2
    assert FeatureIssueCode.MISSING_CANDLE in _issue_codes(snapshot)
    assert snapshot.candle_summary.market_data_complete is False


def test_feature_engine_reports_mismatched_pair_and_timeframe() -> None:
    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=15),
        as_of=START + timedelta(minutes=15),
        candles=[
            _candle(0, pair=OTHER_PAIR),
            _candle(0, timeframe=Timeframe.H1),
        ],
        rolling_window_size=1,
    )

    assert snapshot.candle_summary.used_candle_count == 0
    assert FeatureIssueCode.CANDLE_PAIR_MISMATCH in _issue_codes(snapshot)
    assert FeatureIssueCode.CANDLE_TIMEFRAME_MISMATCH in _issue_codes(snapshot)
    assert FeatureIssueCode.NO_CANDLES in _issue_codes(snapshot)


def test_feature_engine_requires_closed_candles_only() -> None:
    open_candle = _candle(0).model_copy(update={"is_closed": False})

    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=15),
        as_of=START + timedelta(minutes=15),
        candles=[open_candle],
        rolling_window_size=1,
    )

    assert snapshot.candle_summary.used_candle_count == 0
    assert FeatureIssueCode.CANDLE_NOT_CLOSED in _issue_codes(snapshot)
    assert FeatureIssueCode.NO_CANDLES in _issue_codes(snapshot)


def test_feature_engine_counts_economic_events_by_impact_and_currency() -> None:
    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        candles=[_candle(0), _candle(1)],
        economic_events=[
            _event(5, currency="EUR", impact=EconomicImpact.HIGH, provider_event_id="1"),
            _event(10, currency="USD", impact=EconomicImpact.LOW, provider_event_id="2"),
            _event(20, currency="EUR", impact=EconomicImpact.HIGH, provider_event_id="3"),
            _event(35, currency="EUR", impact=EconomicImpact.MEDIUM, provider_event_id="4"),
        ],
        rolling_window_size=2,
    )

    assert [
        (item.impact, item.count) for item in snapshot.economic_event_summary.counts_by_impact
    ] == [
        (EconomicImpact.HIGH, 2),
        (EconomicImpact.LOW, 1),
    ]
    assert [
        (item.currency, item.count) for item in snapshot.economic_event_summary.counts_by_currency
    ] == [("EUR", 2), ("USD", 1)]
    assert snapshot.economic_event_summary.input_event_count == 4
    assert snapshot.economic_event_summary.used_event_count == 3
    assert FeatureIssueCode.EVENT_OUT_OF_RANGE in _issue_codes(snapshot)


def test_feature_engine_handles_empty_and_insufficient_data_without_fake_values() -> None:
    empty = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        candles=[],
        rolling_window_size=3,
    )
    assert empty.candle_summary.latest_close is None
    assert empty.candle_summary.simple_return is None
    assert empty.candle_summary.per_candle_returns == ()
    assert empty.candle_summary.rolling_close_means == ()
    assert FeatureIssueCode.NO_CANDLES in _issue_codes(empty)

    insufficient = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        candles=[_candle(0), _candle(1)],
        rolling_window_size=3,
    )
    assert insufficient.candle_summary.rolling_close_means == ()
    assert FeatureIssueCode.INSUFFICIENT_CANDLES in _issue_codes(insufficient)


def test_feature_snapshot_models_are_immutable() -> None:
    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=15),
        as_of=START + timedelta(minutes=15),
        candles=[_candle(0)],
        rolling_window_size=1,
    )

    with pytest.raises(ValidationError):
        snapshot.candle_summary.latest_close = Decimal("999")


class _FakeCandleRepository:
    def __init__(self, candles: Sequence[Candle]) -> None:
        self.candles = list(candles)
        self.calls: list[dict[str, object]] = []

    async def list_range(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        start_at: datetime,
        end_at: datetime,
        provider: str | None = None,
    ) -> list[Candle]:
        self.calls.append(
            {
                "pair": pair,
                "timeframe": timeframe,
                "start_at": start_at,
                "end_at": end_at,
                "provider": provider,
            }
        )
        return list(self.candles)


class _FakeEconomicEventRepository:
    def __init__(self, events: Sequence[EconomicEvent]) -> None:
        self.events = list(events)
        self.calls: list[dict[str, object]] = []

    async def list_window(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
        currencies: list[str] | None = None,
        provider: str | None = None,
    ) -> list[EconomicEvent]:
        self.calls.append(
            {
                "start_at": start_at,
                "end_at": end_at,
                "currencies": currencies,
                "provider": provider,
            }
        )
        return list(self.events)


class _FakeFeatureUnitOfWork:
    def __init__(
        self,
        candle_repository: _FakeCandleRepository,
        event_repository: _FakeEconomicEventRepository,
    ) -> None:
        self.candles = candle_repository
        self.economic_events = event_repository

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None


class _FakeFeatureUnitOfWorkFactory:
    def __init__(
        self,
        candle_repository: _FakeCandleRepository,
        event_repository: _FakeEconomicEventRepository,
    ) -> None:
        self._candle_repository = candle_repository
        self._event_repository = event_repository

    def __call__(self) -> _FakeFeatureUnitOfWork:
        return _FakeFeatureUnitOfWork(self._candle_repository, self._event_repository)


@pytest.mark.asyncio
async def test_feature_service_reads_repositories_and_builds_snapshot() -> None:
    candles = [_candle(0), _candle(1)]
    events = [_event(5, currency="EUR", provider_event_id="service")]
    candle_repository = _FakeCandleRepository(candles)
    event_repository = _FakeEconomicEventRepository(events)
    service = FeatureService(_FakeFeatureUnitOfWorkFactory(candle_repository, event_repository))

    snapshot = await service.build_market_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        provider="unit",
        rolling_window_size=2,
    )

    assert snapshot.candle_summary.used_candle_count == 2
    assert snapshot.economic_event_summary.used_event_count == 1
    assert candle_repository.calls[0]["pair"] == PAIR
    assert candle_repository.calls[0]["provider"] == "unit"
    assert event_repository.calls[0]["currencies"] == ["EUR", "USD"]
    assert event_repository.calls[0]["provider"] == "unit"
```

### `tests/contract/test_safety_boundaries.py`

```python
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

### `tests/integration/test_database_and_api.py`

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
    assert status.json()["project_phase"] == "phase_3b_feature_engine_foundation"
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


## Migration Contents

No new migration was added for Phase 3B. Existing migration contents are included for verification.

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


## Documentation Contents

### `README.md`

```markdown
# AI Trading OS

AI Trading OS is a safety-first foundation for a future modular Forex analysis and paper-trading platform. The current repository implements only infrastructure: API health/status endpoints, async PostgreSQL persistence, a scheduler heartbeat, Telegram command foundations, strict configuration, and safety contracts.

## Current Status

- Current project phase: phase_3b_feature_engine_foundation.
- Trading strategy: not implemented.
- Real trading: disabled and unsupported.
- External integrations: disabled by default.
- Telegram: can run in disabled mode without a token.
- Phase 3B: deterministic feature engine foundation only.

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

## Phase 3B Status

Phase 3B adds a deterministic, closed-candle-only feature engine that transforms existing normalized
Phase 3A candles and economic events into typed immutable feature snapshots. It computes descriptive
features only, such as latest close, candle counts, simple returns, rolling close means, ranges,
volume summaries, true ranges, economic-event counts, and quality issues. It does not produce
trading decisions, setup scoring, directions, recommendations, signals, AI output, broker activity,
paper trading, order execution, or real trading. Phase 3C has not started.

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

- No strategy, signals, OpenAI calls, backtesting, position sizing, broker execution, or real trading.
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

### `AGENTS.md`

```markdown
# AI Trading OS Agent Guide

AI Trading OS is a foundation for a future Forex analysis and paper-trading platform.

Current project phase: phase_3b_feature_engine_foundation.
Phase 3B is limited to deterministic, closed-candle-only feature snapshots built from existing
normalized Phase 3A market/calendar data. External integrations are disabled by default. The project
contains no strategy, no signals, no broker order APIs, no paper trading, and no real trading.
Phase 3C has not started.

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
- Never add strategy, setup scoring, LONG/SHORT direction, buy/sell recommendations, paper trading,
  broker APIs, order execution, or real trading while working in Phase 3B.
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
- Phase 3B feature engine foundation: deterministic closed-candle feature models, feature
  calculation engine, feature service over repository protocols, and safety tests confirming no
  strategy/signals/trading activation.

## Current Implementation Status

The repository has completed the foundation phase, Phase 2 hardening/data adapters, Phase 3A
data-quality foundation, and Phase 3B deterministic feature-engine foundation. Production Twelve
Data and FMP adapters exist, but live integrations remain disabled by default. Scanning state can be
enabled or disabled, but no strategy, signal generation, AI agent, paper-trading, or execution flow
is connected.

## Future Phases

- Phase 2: market-data and calendar adapters — completed as disabled-by-default factories plus
  production adapters covered by MockTransport-backed contract tests
- Phase 3A: data-quality foundation — completed without trading analysis or decisions
- Phase 3B: deterministic feature engine foundation — completed without trading decisions
- Phase 3C: next phase if applicable; not started
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

Phase 3C is the next phase if applicable. It has not started, and no Phase 3C behavior is active.
```
