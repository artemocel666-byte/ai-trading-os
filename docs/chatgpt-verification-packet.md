# AI Trading OS - Phase 3C Verification Packet

Generated at: `2026-07-12T11:30:38Z`

## Scope

This packet documents Phase 3C: deterministic indicator/context foundation. Phase 3C builds typed,
immutable, descriptive context snapshots from already-normalized Phase 3A closed candles, Phase 3B
feature snapshots, and normalized economic events.

Phase 3C is uncommitted at packet generation time. Phase 3D was not started.

No strategy, signals, setup scoring, confidence scoring, AI agents, OpenAI calls, broker APIs,
paper trading, order execution, or real trading were added or activated. Existing foundation-era
signal/trading/paper schemas remain inactive.

## Git Metadata

- Branch: `main`
- Current commit hash: `a6f44f0e3276c99e7685e59be5dd8b01bb2aa263`

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
?? app/domain/context_engine.py
?? app/domain/entities/context.py
?? app/services/context_service.py
?? docs/phase3c-verification-report.md
?? tests/unit/test_context_engine_foundation.py
```

### `git diff --stat`

```text
 AGENTS.md                                  |   12 +-
 PLANS.md                                   |   16 +-
 README.md                                  |   15 +-
 app/core/constants.py                      |    2 +-
 app/domain/entities/__init__.py            |   28 +
 docs/chatgpt-verification-packet.md        | 3343 +++++++++++++---------------
 tests/contract/test_safety_boundaries.py   |   42 +
 tests/integration/test_database_and_api.py |    2 +-
 8 files changed, 1704 insertions(+), 1756 deletions(-)
```

### `git log --oneline -4`

```text
a6f44f0 Add Phase 3B feature engine foundation
03c3acd Add Phase 3A data quality foundation
9d68709 Document Phase 2 runtime verification
0848243 Complete Phase 2 data adapters
```

## Created Files

- `app/domain/context_engine.py`
- `app/domain/entities/context.py`
- `app/services/context_service.py`
- `docs/phase3c-verification-report.md`
- `tests/unit/test_context_engine_foundation.py`

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

- Updated `PROJECT_PHASE` to `phase_3c_indicator_context_foundation`.
- Added immutable Phase 3C context models in `app/domain/entities/context.py`.
- Added deterministic closed-candle context calculation in `app/domain/context_engine.py`.
- Added `ContextService` in `app/services/context_service.py`, depending on UnitOfWork protocols.
- Reused the Phase 3B feature engine as a descriptive input layer.
- Added unit/service tests for exact Decimal calculations, UTC normalization, closed-candle-only
  behavior, no future leakage, duplicate/gap/mismatch issues, empty/insufficient data behavior,
  moving averages, range and candle-shape summaries, event context, immutability, and fake-repo
  service behavior.
- Added safety coverage confirming Phase 3C context files do not introduce decision/execution terms.
- No migration was added; Phase 3C reads existing Phase 2/3A tables only.
- No API route, trading endpoint, signal endpoint, network call, provider call, secret, or API key was added.

## Verification Command Outputs

### `uv lock --check`

Exit code: `0`

```text
Resolved 46 packages in 15ms
```

### `uv sync`

Exit code: `0`

```text
Resolved 46 packages in 3ms
Checked 43 packages in 14ms
```

### `uv run ruff format --check .`

Exit code: `0`

```text
96 files already formatted
```

### `uv run ruff check .`

Exit code: `0`

```text
All checks passed!
```

### `uv run mypy app`

Exit code: `0`

```text
Success: no issues found in 69 source files
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
collected 176 items

tests/contract/test_agent_contracts.py ......                            [  3%]
tests/contract/test_api_error_schema.py .                                [  3%]
tests/contract/test_architecture_boundaries.py ..                        [  5%]
tests/contract/test_provider_contracts.py .............................. [ 22%]
...............................                                          [ 39%]
tests/contract/test_safety_boundaries.py ...........                     [ 46%]
tests/integration/test_database_and_api.py sssss                         [ 48%]
tests/unit/test_context_engine_foundation.py .............               [ 56%]
tests/unit/test_data_quality_foundation.py ...                           [ 57%]
tests/unit/test_domain_market_models.py ..................               [ 68%]
tests/unit/test_errors_and_redaction.py .......                          [ 72%]
tests/unit/test_feature_engine_foundation.py ...........                 [ 78%]
tests/unit/test_internal_api_key.py ....                                 [ 80%]
tests/unit/test_settings.py .........                                    [ 85%]
tests/unit/test_system_state_service.py .....                            [ 88%]
tests/unit/test_telegram_commands.py ..                                  [ 89%]
tests/unit/test_telegram_policy.py .....                                 [ 92%]
tests/unit/test_time.py ...                                              [ 94%]
tests/unit/test_unit_of_work_lifecycle.py ......                         [ 97%]
tests/unit/test_value_objects_and_enums.py ....                          [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /Users/artem.otsel/Documents/ai-trading-os/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================== 171 passed, 5 skipped, 1 warning in 0.75s ===================
```

### `uv run python scripts/security_check.py`

Exit code: `0`

```text
```

## Docker and PostgreSQL Verification Outputs

### `docker compose build`

Exit code: `0`

```text
 Image ai-trading-os-api Building 
 Image ai-trading-os-worker Building 
 Image ai-trading-os-bot Building 
 Image ai-trading-os-migrate Building 
#1 [internal] load local bake definitions
#1 reading from stdin 1.91kB done
#1 DONE 0.0s

#2 [migrate internal] load build definition from Dockerfile
#2 transferring dockerfile: 411B done
#2 DONE 0.0s

#3 [migrate internal] load metadata for ghcr.io/astral-sh/uv:python3.12-bookworm-slim
#3 DONE 1.0s

#4 [worker internal] load .dockerignore
#4 transferring context: 143B done
#4 DONE 0.0s

#5 [api 1/5] FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58
#5 resolve ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58 0.0s done
#5 DONE 0.0s

#6 [api internal] load build context
#6 transferring context: 330.44kB 0.0s done
#6 DONE 0.0s

#7 [worker 2/5] WORKDIR /app
#7 CACHED

#8 [worker 3/5] COPY pyproject.toml uv.lock* ./
#8 CACHED

#9 [worker 4/5] RUN uv sync --frozen --no-dev
#9 CACHED

#10 [worker 5/5] COPY . .
#10 DONE 0.0s

#11 [migrate] exporting to image
#11 exporting layers 0.0s done
#11 ...

#12 [worker] exporting to image
#12 exporting layers 0.0s done
#12 exporting manifest sha256:1ade8280b565b0d720d55ffb6dc756c9a8c9eeffef7040f2f8dd4eec6e61fc94 done
#12 exporting config sha256:8908017fe840805f64a75fc7dc4a0b7c6504da52e6d7af7b20bc606e3b820ea2 done
#12 exporting attestation manifest sha256:4e90926576a66f536708b51223e9daae6449709ea6798be8abf033fdb7be8cf9 0.0s done
#12 exporting manifest list sha256:bbe283817bdf6b830415d8debb45357472f01ad02b5e9ce44d5c4badee6fe827 done
#12 naming to docker.io/library/ai-trading-os-worker:latest done
#12 unpacking to docker.io/library/ai-trading-os-worker:latest 0.0s done
#12 DONE 0.1s

#11 [migrate] exporting to image
#11 exporting manifest sha256:d2a4408f75060409c5ebdba017a991d58b2121a9499c0aaf82688581b45f84ca done
#11 exporting config sha256:1bdee32edd39031a6bbf8316b198e6b24c4533f0194541b56d74628a193da29a done
#11 exporting attestation manifest sha256:3fab60fc3572b7df9fdb6df1b7ce7b59b4183b613f18f0db0df2f45054442b3a 0.0s done
#11 exporting manifest list sha256:2e57cbce9806bf85fe422ba246c9a793ce829fb8bd2472f0cb7f82397798d062 done
#11 naming to docker.io/library/ai-trading-os-migrate:latest done
#11 unpacking to docker.io/library/ai-trading-os-migrate:latest 0.0s done
#11 DONE 0.1s

#13 [api] exporting to image
#13 exporting layers 0.0s done
#13 exporting manifest sha256:07c8ac92f4eff42ba722080ae4d5812120c9f471f75c8d6570e9200db0cfc89a done
#13 exporting config sha256:685e968a6e2b42b5a7207126bfcc3eb4d53d7aa62b9fe18f9813a705b0d81c06 done
#13 exporting attestation manifest sha256:57c3aec052d8b07adc19d4f25ec8544f5409a3179c65903cdaa0eb71fa0f4216 0.0s done
#13 exporting manifest list sha256:6bc8803107b31d7cbf0f10c9e0ce671a50ef7037a80ebaa00d4d73281aa2e7ef done
#13 naming to docker.io/library/ai-trading-os-api:latest done
#13 unpacking to docker.io/library/ai-trading-os-api:latest 0.0s done
#13 DONE 0.1s

#14 [bot] exporting to image
#14 exporting layers 0.0s done
#14 exporting manifest sha256:89d0c68d66bb11599e81912d8e62214b455569abaded59f66b4abc4c239c476f done
#14 exporting config sha256:6726986c2faab2cd6c5f7b27f30e7ead46c6526c55540ae8759a1154f7738146 done
#14 exporting attestation manifest sha256:fce4cb405b07bdb668018e868067655c291b3be31a34f2cc4a78e478fb1b0547 0.0s done
#14 exporting manifest list sha256:a8f9ff68d10b16d61c6cfa6e90c0eacfcf141aab20cc0904392adf835b6906a1 done
#14 naming to docker.io/library/ai-trading-os-bot:latest done
#14 unpacking to docker.io/library/ai-trading-os-bot:latest 0.0s done
#14 DONE 0.1s

#15 [worker] resolving provenance for metadata file
#15 DONE 0.0s

#16 [bot] resolving provenance for metadata file
#16 DONE 0.0s

#17 [migrate] resolving provenance for metadata file
#17 DONE 0.0s

#18 [api] resolving provenance for metadata file
#18 DONE 0.0s
 Image ai-trading-os-migrate Built 
 Image ai-trading-os-worker Built 
 Image ai-trading-os-api Built 
 Image ai-trading-os-bot Built 
```

### `docker compose up -d postgres`

Exit code: `0`

```text
 Network ai-trading-os_default Creating 
 Network ai-trading-os_default Created 
 Container ai-trading-os-postgres-1 Creating 
 Container ai-trading-os-postgres-1 Created 
 Container ai-trading-os-postgres-1 Starting 
 Container ai-trading-os-postgres-1 Started 
```

### `docker compose run --rm migrate alembic current`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-abb9409cd4b2 Creating 
 Container ai-trading-os-migrate-run-abb9409cd4b2 Created 
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
 Container ai-trading-os-migrate-run-a2bcebb328ff Creating 
 Container ai-trading-os-migrate-run-a2bcebb328ff Created 
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
 Container ai-trading-os-migrate-run-c46aceeaa50c Creating 
 Container ai-trading-os-migrate-run-c46aceeaa50c Created 
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

### Docker integration run #1

Command:

```text
docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py
```

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-459bd2223678 Creating 
 Container ai-trading-os-migrate-run-459bd2223678 Created 
Downloading pygments (1.2MiB)
Downloading ruff (10.5MiB)
Downloading mypy (13.1MiB)
 Downloaded ruff
 Downloaded pygments
 Downloaded mypy
Installed 11 packages in 79ms
Bytecode compiled 1963 files in 501ms
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

### Docker integration run #2

Command:

```text
docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py
```

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-17eecdde01cd Creating 
 Container ai-trading-os-migrate-run-17eecdde01cd Created 
Downloading pygments (1.2MiB)
Downloading ruff (10.5MiB)
Downloading mypy (13.1MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 45ms
Bytecode compiled 1963 files in 415ms
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

- Host integration tests in `uv run pytest` were skipped because `REQUIRE_INTEGRATION_TESTS` was not
  enabled for the host run. The PostgreSQL integration suite was run inside Docker twice against the
  same `ai_trading_os_test` database without cleanup, and both runs passed.
- Full API stack `/ready` probing was not rerun for Phase 3C because the requested Docker verification
  set was PostgreSQL, Alembic, integration tests, and compose configuration.

## Unavailable Checks

- None for the requested Phase 3C verification commands. Host `uv` and Docker were available.

## Remaining Risks

- Phase 3C changes are uncommitted at packet generation time.
- Context snapshots are deterministic in-memory structures and are not persisted by design.
- Existing foundation-era database names and environment variables may still mention future trading
  concepts, but Phase 3C did not activate them or use them for decisions.

## Phase Boundary Confirmation

- Phase 3D was not started.
- No strategy was added.
- No signals were added.
- No setup scoring or confidence scoring was added.
- No AI agents, OpenAI calls, or LLM calls were added.
- No broker APIs, paper trading, order execution, or real trading were added.
- Feature and context engines produce descriptive deterministic structures only.

## Traceability

| Requirement | Implementation file | Test file | Verification result |
| --- | --- | --- | --- |
| Update project phase to Phase 3C | `app/core/constants.py` | `tests/integration/test_database_and_api.py` | Host pytest and Docker integration tests passed |
| Typed immutable context snapshots | `app/domain/entities/context.py` | `tests/unit/test_context_engine_foundation.py` | Host pytest passed |
| Closed-candle-only context engine | `app/domain/context_engine.py` | `tests/unit/test_context_engine_foundation.py` | Host pytest passed |
| Exact deterministic Decimal calculations | `app/domain/context_engine.py` | `tests/unit/test_context_engine_foundation.py` | Host pytest passed |
| UTC normalization and no future leakage | `app/domain/entities/context.py`, `app/domain/context_engine.py` | `tests/unit/test_context_engine_foundation.py` | Host pytest passed |
| Duplicate/gap/mismatch and insufficient-data issues | `app/domain/context_engine.py` | `tests/unit/test_context_engine_foundation.py` | Host pytest passed |
| Moving averages, ranges, candle shape, event context, time context | `app/domain/context_engine.py` | `tests/unit/test_context_engine_foundation.py` | Host pytest passed |
| Service uses UnitOfWork/repository protocols | `app/services/context_service.py` | `tests/unit/test_context_engine_foundation.py` | Host pytest and mypy passed |
| Preserve PostgreSQL repeatability | existing repositories and integration tests | `tests/integration/test_database_and_api.py` | Docker integration tests passed twice without DB cleanup |
| Preserve safety boundary | `app/domain/entities/context.py`, `app/domain/context_engine.py`, `app/services/context_service.py` | `tests/contract/test_safety_boundaries.py`, `scripts/security_check.py` | Ruff, pytest, and security check passed |
| Avoid new migrations | no new migration file | `docker compose run --rm migrate alembic check` | No new upgrade operations detected |

## Full Contents of Changed Source Files

### `app/core/constants.py`

```python
PROJECT_PHASE = "phase_3c_indicator_context_foundation"
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
from app.domain.entities.context import (
    CandleShapeSummary,
    ContextCurrencyCount,
    ContextImpactCount,
    ContextIssue,
    ContextIssueCode,
    EventContextSummary,
    IndicatorWindow,
    MarketContextSnapshot,
    MovingAverageSeries,
    MovingAverageSummary,
    RangeContextSummary,
    ReturnDistributionSummary,
    TimeContextSummary,
)
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
    "CandleShapeSummary",
    "ContextCurrencyCount",
    "ContextImpactCount",
    "ContextIssue",
    "ContextIssueCode",
    "CurrencyEventCount",
    "DataQualityIssue",
    "DataQualityIssueCode",
    "EconomicEvent",
    "EconomicEventAvailability",
    "EconomicEventFeatureSummary",
    "EconomicImpact",
    "EconomicImpactCount",
    "EventContextSummary",
    "FeatureIssue",
    "FeatureIssueCode",
    "FeatureSnapshot",
    "FeatureWindow",
    "IndicatorWindow",
    "MarketContextSnapshot",
    "MarketFeatureSnapshot",
    "MovingAverageSeries",
    "MovingAverageSummary",
    "RangeContextSummary",
    "ReturnDistributionSummary",
    "TimeContextSummary",
    "Timeframe",
    "UpsertResult",
    "build_feature_snapshot",
]
```

### `app/domain/entities/context.py`

```python
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.features import MarketFeatureSnapshot
from app.domain.entities.market_data import EconomicImpact, Timeframe
from app.domain.value_objects import CurrencyPair


class ContextIssueCode(StrEnum):
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


class ContextIssue(BaseModel):
    code: ContextIssueCode
    description: str = Field(min_length=1)
    timestamp: datetime | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_utc(cls, value: datetime | None) -> datetime | None:
        return normalize_to_utc(value) if value is not None else None


class IndicatorWindow(BaseModel):
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
            raise ValueError("context window_end must be later than window_start")
        return self


class ReturnDistributionSummary(BaseModel):
    close_values: tuple[Decimal, ...] = ()
    close_change_values: tuple[Decimal, ...] = ()
    per_candle_returns: tuple[Decimal, ...] = ()
    cumulative_return: Decimal | None = None
    mean_return: Decimal | None = None
    median_return: Decimal | None = None
    min_return: Decimal | None = None
    max_return: Decimal | None = None
    return_standard_deviation: Decimal | None = None
    realized_volatility: Decimal | None = None
    max_close_to_close_drawdown: Decimal | None = None

    model_config = ConfigDict(frozen=True)


class MovingAverageSeries(BaseModel):
    window_size: int = Field(ge=1)
    values: tuple[Decimal, ...] = ()

    model_config = ConfigDict(frozen=True)


class MovingAverageSummary(BaseModel):
    close_mean_series: tuple[MovingAverageSeries, ...] = ()
    return_mean_series: tuple[MovingAverageSeries, ...] = ()

    model_config = ConfigDict(frozen=True)


class RangeContextSummary(BaseModel):
    true_range_values: tuple[Decimal, ...] = ()
    average_true_range: Decimal | None = None
    candle_range_values: tuple[Decimal, ...] = ()
    average_candle_range: Decimal | None = None
    range_change_ratios: tuple[Decimal | None, ...] = ()

    model_config = ConfigDict(frozen=True)


class CandleShapeSummary(BaseModel):
    body_sizes: tuple[Decimal, ...] = ()
    average_body_size: Decimal | None = None
    upper_wick_sizes: tuple[Decimal, ...] = ()
    lower_wick_sizes: tuple[Decimal, ...] = ()
    average_upper_wick_size: Decimal | None = None
    average_lower_wick_size: Decimal | None = None
    body_to_range_ratios: tuple[Decimal | None, ...] = ()
    close_location_in_range_values: tuple[Decimal | None, ...] = ()

    model_config = ConfigDict(frozen=True)


class ContextImpactCount(BaseModel):
    impact: EconomicImpact
    count: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)


class ContextCurrencyCount(BaseModel):
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    count: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)


class EventContextSummary(BaseModel):
    input_event_count: int = Field(ge=0)
    used_event_count: int = Field(ge=0)
    counts_by_impact: tuple[ContextImpactCount, ...] = ()
    counts_by_currency: tuple[ContextCurrencyCount, ...] = ()
    latest_event_time: datetime | None = None
    minutes_since_latest_event: Decimal | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("latest_event_time")
    @classmethod
    def latest_event_time_must_be_utc(cls, value: datetime | None) -> datetime | None:
        return normalize_to_utc(value) if value is not None else None


class TimeContextSummary(BaseModel):
    as_of_utc_hour: int = Field(ge=0, le=23)
    as_of_utc_weekday: int = Field(ge=0, le=6)
    window_minutes: Decimal = Field(ge=Decimal("0"))
    candle_count: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)


class MarketContextSnapshot(BaseModel):
    window: IndicatorWindow
    feature_snapshot: MarketFeatureSnapshot
    return_distribution: ReturnDistributionSummary
    moving_average_summary: MovingAverageSummary
    range_context: RangeContextSummary
    candle_shape: CandleShapeSummary
    event_context: EventContextSummary
    time_context: TimeContextSummary
    context_issues: tuple[ContextIssue, ...] = ()

    model_config = ConfigDict(frozen=True)

    @property
    def quality_ok(self) -> bool:
        return (
            not self.context_issues
            and not self.feature_snapshot.quality_issues
            and not self.feature_snapshot.data_quality_issues
        )
```

### `app/domain/context_engine.py`

```python
from collections import Counter
from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal

from app.core.time import normalize_to_utc
from app.domain.entities.context import (
    CandleShapeSummary,
    ContextCurrencyCount,
    ContextImpactCount,
    ContextIssue,
    ContextIssueCode,
    EventContextSummary,
    IndicatorWindow,
    MarketContextSnapshot,
    MovingAverageSeries,
    MovingAverageSummary,
    RangeContextSummary,
    ReturnDistributionSummary,
    TimeContextSummary,
)
from app.domain.entities.features import FeatureIssue
from app.domain.entities.market_data import Candle, EconomicEvent, Timeframe
from app.domain.feature_engine import MarketFeatureEngine
from app.domain.value_objects import CurrencyPair


class MarketContextEngine:
    def __init__(self, *, feature_engine: MarketFeatureEngine | None = None) -> None:
        self._feature_engine = feature_engine or MarketFeatureEngine()

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
        moving_average_windows: Sequence[int] = (3, 5),
    ) -> MarketContextSnapshot:
        window = IndicatorWindow(
            pair=pair,
            timeframe=timeframe,
            window_start=window_start,
            window_end=window_end,
            as_of=as_of,
        )
        normalized_windows = _normalize_windows(moving_average_windows)
        feature_snapshot = self._feature_engine.build_snapshot(
            pair=pair,
            timeframe=timeframe,
            window_start=window.window_start,
            window_end=window.window_end,
            as_of=window.as_of,
            candles=candles,
            economic_events=economic_events,
            rolling_window_size=min(normalized_windows),
        )
        usable_candles = _select_candles(
            pair=pair,
            timeframe=timeframe,
            start_at=window.window_start,
            end_at=window.window_end,
            as_of=window.as_of,
            candles=candles,
        )
        usable_events = _select_events(
            start_at=window.window_start,
            end_at=window.window_end,
            as_of=window.as_of,
            events=economic_events,
        )
        context_issues = tuple(_context_issue(issue) for issue in feature_snapshot.quality_issues)
        return MarketContextSnapshot(
            window=window,
            feature_snapshot=feature_snapshot,
            return_distribution=_return_distribution(usable_candles),
            moving_average_summary=_moving_average_summary(
                candles=usable_candles,
                windows=normalized_windows,
            ),
            range_context=_range_context(usable_candles),
            candle_shape=_candle_shape(usable_candles),
            event_context=_event_context(
                input_event_count=len(economic_events),
                events=usable_events,
                as_of=window.as_of,
            ),
            time_context=_time_context(window=window, candle_count=len(usable_candles)),
            context_issues=context_issues,
        )


def _normalize_windows(windows: Sequence[int]) -> tuple[int, ...]:
    if not windows:
        raise ValueError("at least one moving average window is required")
    unique = tuple(sorted(set(windows)))
    if any(window < 1 for window in unique):
        raise ValueError("moving average windows must be positive")
    return unique


def _context_issue(issue: FeatureIssue) -> ContextIssue:
    return ContextIssue(
        code=ContextIssueCode[issue.code.name],
        description=issue.description,
        timestamp=issue.timestamp,
    )


def _select_candles(
    *,
    pair: CurrencyPair,
    timeframe: Timeframe,
    start_at: datetime,
    end_at: datetime,
    as_of: datetime,
    candles: Sequence[Candle],
) -> tuple[Candle, ...]:
    start_utc = normalize_to_utc(start_at)
    end_utc = normalize_to_utc(end_at)
    as_of_utc = normalize_to_utc(as_of)
    selected: dict[datetime, Candle] = {}
    for candle in sorted(candles, key=lambda item: (item.open_time, item.provider)):
        if (
            candle.is_closed
            and candle.pair == pair
            and candle.timeframe == timeframe
            and candle.open_time >= start_utc
            and candle.close_time <= end_utc
            and candle.close_time <= as_of_utc
        ):
            selected.setdefault(candle.open_time, candle)
    return tuple(selected[open_time] for open_time in sorted(selected))


def _select_events(
    *,
    start_at: datetime,
    end_at: datetime,
    as_of: datetime,
    events: Sequence[EconomicEvent],
) -> tuple[EconomicEvent, ...]:
    start_utc = normalize_to_utc(start_at)
    end_utc = normalize_to_utc(end_at)
    as_of_utc = normalize_to_utc(as_of)
    return tuple(
        event
        for event in sorted(
            events,
            key=lambda item: (item.scheduled_at, item.currency, item.provider_event_id),
        )
        if start_utc <= event.scheduled_at < end_utc and event.scheduled_at <= as_of_utc
    )


def _return_distribution(candles: Sequence[Candle]) -> ReturnDistributionSummary:
    close_values = tuple(candle.close for candle in candles)
    close_changes = tuple(
        close_values[index] - close_values[index - 1] for index in range(1, len(close_values))
    )
    per_candle_returns = tuple((candle.close - candle.open) / candle.open for candle in candles)
    deviation = _population_standard_deviation(per_candle_returns)
    return ReturnDistributionSummary(
        close_values=close_values,
        close_change_values=close_changes,
        per_candle_returns=per_candle_returns,
        cumulative_return=_cumulative_return(close_values),
        mean_return=_mean(per_candle_returns),
        median_return=_median(per_candle_returns),
        min_return=min(per_candle_returns) if per_candle_returns else None,
        max_return=max(per_candle_returns) if per_candle_returns else None,
        return_standard_deviation=deviation,
        realized_volatility=deviation,
        max_close_to_close_drawdown=_max_close_to_close_drawdown(close_values),
    )


def _moving_average_summary(
    *,
    candles: Sequence[Candle],
    windows: Sequence[int],
) -> MovingAverageSummary:
    close_values = tuple(candle.close for candle in candles)
    per_candle_returns = tuple((candle.close - candle.open) / candle.open for candle in candles)
    return MovingAverageSummary(
        close_mean_series=tuple(
            MovingAverageSeries(window_size=window, values=_moving_means(close_values, window))
            for window in windows
        ),
        return_mean_series=tuple(
            MovingAverageSeries(
                window_size=window,
                values=_moving_means(per_candle_returns, window),
            )
            for window in windows
        ),
    )


def _range_context(candles: Sequence[Candle]) -> RangeContextSummary:
    range_values = tuple(candle.high - candle.low for candle in candles)
    true_range_values = _true_ranges(candles)
    return RangeContextSummary(
        true_range_values=true_range_values,
        average_true_range=_mean(true_range_values),
        candle_range_values=range_values,
        average_candle_range=_mean(range_values),
        range_change_ratios=_range_change_ratios(range_values),
    )


def _candle_shape(candles: Sequence[Candle]) -> CandleShapeSummary:
    body_sizes = tuple(abs(candle.close - candle.open) for candle in candles)
    upper_wicks = tuple(candle.high - max(candle.open, candle.close) for candle in candles)
    lower_wicks = tuple(min(candle.open, candle.close) - candle.low for candle in candles)
    range_values = tuple(candle.high - candle.low for candle in candles)
    return CandleShapeSummary(
        body_sizes=body_sizes,
        average_body_size=_mean(body_sizes),
        upper_wick_sizes=upper_wicks,
        lower_wick_sizes=lower_wicks,
        average_upper_wick_size=_mean(upper_wicks),
        average_lower_wick_size=_mean(lower_wicks),
        body_to_range_ratios=tuple(
            None if range_value == 0 else body_size / range_value
            for body_size, range_value in zip(body_sizes, range_values, strict=True)
        ),
        close_location_in_range_values=tuple(
            None if range_value == 0 else (candle.close - candle.low) / range_value
            for candle, range_value in zip(candles, range_values, strict=True)
        ),
    )


def _event_context(
    *,
    input_event_count: int,
    events: Sequence[EconomicEvent],
    as_of: datetime,
) -> EventContextSummary:
    impact_counts = Counter(event.impact for event in events)
    currency_counts = Counter(event.currency for event in events)
    latest_event_time = max((event.scheduled_at for event in events), default=None)
    return EventContextSummary(
        input_event_count=input_event_count,
        used_event_count=len(events),
        counts_by_impact=tuple(
            ContextImpactCount(impact=impact, count=impact_counts[impact])
            for impact in sorted(impact_counts, key=lambda value: value.value)
        ),
        counts_by_currency=tuple(
            ContextCurrencyCount(currency=currency, count=currency_counts[currency])
            for currency in sorted(currency_counts)
        ),
        latest_event_time=latest_event_time,
        minutes_since_latest_event=_minutes_between(latest_event_time, as_of)
        if latest_event_time is not None
        else None,
    )


def _time_context(*, window: IndicatorWindow, candle_count: int) -> TimeContextSummary:
    return TimeContextSummary(
        as_of_utc_hour=window.as_of.hour,
        as_of_utc_weekday=window.as_of.weekday(),
        window_minutes=_minutes_between(window.window_start, window.window_end) or Decimal("0"),
        candle_count=candle_count,
    )


def _cumulative_return(close_values: Sequence[Decimal]) -> Decimal | None:
    if len(close_values) < 2:
        return None
    return (close_values[-1] - close_values[0]) / close_values[0]


def _mean(values: Sequence[Decimal]) -> Decimal | None:
    if not values:
        return None
    return sum(values, Decimal("0")) / Decimal(len(values))


def _median(values: Sequence[Decimal]) -> Decimal | None:
    if not values:
        return None
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / Decimal("2")


def _population_standard_deviation(values: Sequence[Decimal]) -> Decimal | None:
    mean = _mean(values)
    if mean is None:
        return None
    variance = sum(((value - mean) ** 2 for value in values), Decimal("0")) / Decimal(len(values))
    return variance.sqrt()


def _max_close_to_close_drawdown(close_values: Sequence[Decimal]) -> Decimal | None:
    if len(close_values) < 2:
        return None
    peak = close_values[0]
    largest = Decimal("0")
    for close_value in close_values[1:]:
        if close_value > peak:
            peak = close_value
            continue
        current = (peak - close_value) / peak
        if current > largest:
            largest = current
    return largest


def _moving_means(values: Sequence[Decimal], window_size: int) -> tuple[Decimal, ...]:
    means: list[Decimal] = []
    for index in range(window_size, len(values) + 1):
        window = values[index - window_size : index]
        means.append(sum(window, Decimal("0")) / Decimal(window_size))
    return tuple(means)


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


def _range_change_ratios(values: Sequence[Decimal]) -> tuple[Decimal | None, ...]:
    if not values:
        return ()
    ratios: list[Decimal | None] = [None]
    for index in range(1, len(values)):
        previous = values[index - 1]
        ratios.append(None if previous == 0 else (values[index] - previous) / previous)
    return tuple(ratios)


def _minutes_between(start_at: datetime | None, end_at: datetime) -> Decimal | None:
    if start_at is None:
        return None
    delta = normalize_to_utc(end_at) - normalize_to_utc(start_at)
    microseconds = (delta.days * 86_400 + delta.seconds) * 1_000_000 + delta.microseconds
    return Decimal(microseconds) / Decimal("60000000")
```

### `app/services/context_service.py`

```python
from collections.abc import Callable, Sequence
from datetime import datetime

from app.domain.context_engine import MarketContextEngine
from app.domain.entities import Timeframe
from app.domain.entities.context import MarketContextSnapshot
from app.domain.interfaces.unit_of_work import UnitOfWork
from app.domain.value_objects import CurrencyPair

UnitOfWorkFactory = Callable[[], UnitOfWork]


class ContextService:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        *,
        engine: MarketContextEngine | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._engine = engine or MarketContextEngine()

    async def build_market_context(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        window_start: datetime,
        window_end: datetime,
        as_of: datetime,
        currencies: Sequence[str] | None = None,
        provider: str | None = None,
        moving_average_windows: Sequence[int] = (3, 5),
    ) -> MarketContextSnapshot:
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
            moving_average_windows=moving_average_windows,
        )
```

## Migration Contents

No new migration was added for Phase 3C. Existing migration contents are included below.

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

## New and Modified Tests

### `tests/unit/test_context_engine_foundation.py`

```python
from collections.abc import Sequence
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.domain.context_engine import MarketContextEngine
from app.domain.entities import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.entities.context import ContextIssueCode, MarketContextSnapshot
from app.domain.value_objects import CurrencyPair
from app.services.context_service import ContextService

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


def _engine() -> MarketContextEngine:
    return MarketContextEngine()


def _issue_codes(snapshot: MarketContextSnapshot) -> set[ContextIssueCode]:
    return {issue.code for issue in snapshot.context_issues}


def test_context_engine_calculates_exact_decimal_context() -> None:
    candles = [
        _candle(2, open_value="90", high="100", low="89", close="99"),
        _candle(0, open_value="100", high="112", low="99", close="110"),
        _candle(1, open_value="80", high="90", low="79", close="88"),
    ]

    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=45),
        as_of=START + timedelta(minutes=45),
        candles=candles,
        moving_average_windows=(2, 3),
    )

    assert snapshot.quality_ok is True
    assert snapshot.return_distribution.close_values == (
        Decimal("110"),
        Decimal("88"),
        Decimal("99"),
    )
    assert snapshot.return_distribution.close_change_values == (
        Decimal("-22"),
        Decimal("11"),
    )
    assert snapshot.return_distribution.per_candle_returns == (
        Decimal("0.1"),
        Decimal("0.1"),
        Decimal("0.1"),
    )
    assert snapshot.return_distribution.cumulative_return == Decimal("-0.1")
    assert snapshot.return_distribution.mean_return == Decimal("0.1")
    assert snapshot.return_distribution.median_return == Decimal("0.1")
    assert snapshot.return_distribution.min_return == Decimal("0.1")
    assert snapshot.return_distribution.max_return == Decimal("0.1")
    assert snapshot.return_distribution.return_standard_deviation == Decimal("0")
    assert snapshot.return_distribution.realized_volatility == Decimal("0")
    assert snapshot.return_distribution.max_close_to_close_drawdown == Decimal("0.2")


def test_context_models_normalize_times_to_utc() -> None:
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
        moving_average_windows=(1,),
    )

    assert snapshot.window.window_start == START
    assert snapshot.window.window_end == START + timedelta(minutes=15)
    assert snapshot.window.as_of == START + timedelta(minutes=15)


def test_context_engine_excludes_items_after_as_of() -> None:
    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=45),
        as_of=START + timedelta(minutes=30),
        candles=[_candle(0), _candle(1), _candle(2)],
        economic_events=[
            _event(20, provider_event_id="included"),
            _event(40, provider_event_id="later"),
        ],
        moving_average_windows=(2,),
    )

    assert snapshot.time_context.candle_count == 2
    assert snapshot.event_context.used_event_count == 1
    assert ContextIssueCode.CANDLE_AFTER_AS_OF in _issue_codes(snapshot)
    assert ContextIssueCode.EVENT_AFTER_AS_OF in _issue_codes(snapshot)


def test_context_engine_reports_duplicate_candles() -> None:
    duplicate = _candle(0, provider="duplicate")

    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        candles=[_candle(0), duplicate, _candle(1)],
        moving_average_windows=(2,),
    )

    assert snapshot.time_context.candle_count == 2
    assert ContextIssueCode.DUPLICATE_CANDLE in _issue_codes(snapshot)
    assert snapshot.quality_ok is False


def test_context_engine_reports_missing_candle_gaps() -> None:
    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=45),
        as_of=START + timedelta(minutes=45),
        candles=[_candle(0), _candle(2)],
        moving_average_windows=(2,),
    )

    assert snapshot.time_context.candle_count == 2
    assert ContextIssueCode.MISSING_CANDLE in _issue_codes(snapshot)
    assert snapshot.quality_ok is False


def test_context_engine_reports_mismatched_pair_and_timeframe() -> None:
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
        moving_average_windows=(1,),
    )

    assert snapshot.time_context.candle_count == 0
    assert ContextIssueCode.CANDLE_PAIR_MISMATCH in _issue_codes(snapshot)
    assert ContextIssueCode.CANDLE_TIMEFRAME_MISMATCH in _issue_codes(snapshot)
    assert ContextIssueCode.NO_CANDLES in _issue_codes(snapshot)


def test_context_engine_requires_closed_candles_only() -> None:
    open_candle = _candle(0).model_copy(update={"is_closed": False})

    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=15),
        as_of=START + timedelta(minutes=15),
        candles=[open_candle],
        moving_average_windows=(1,),
    )

    assert snapshot.time_context.candle_count == 0
    assert ContextIssueCode.CANDLE_NOT_CLOSED in _issue_codes(snapshot)
    assert ContextIssueCode.NO_CANDLES in _issue_codes(snapshot)


def test_context_engine_handles_empty_and_small_input_without_fake_values() -> None:
    empty = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        candles=[],
        moving_average_windows=(3,),
    )

    assert empty.return_distribution.close_values == ()
    assert empty.return_distribution.cumulative_return is None
    assert empty.return_distribution.return_standard_deviation is None
    assert empty.range_context.average_true_range is None
    assert empty.candle_shape.average_body_size is None
    assert ContextIssueCode.NO_CANDLES in _issue_codes(empty)

    small = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        candles=[_candle(0), _candle(1)],
        moving_average_windows=(3,),
    )
    assert small.moving_average_summary.close_mean_series[0].values == ()
    assert ContextIssueCode.INSUFFICIENT_CANDLES in _issue_codes(small)


def test_context_engine_calculates_moving_averages() -> None:
    candles = [
        _candle(0, open_value="100", high="101", low="99", close="100"),
        _candle(1, open_value="100", high="111", low="99", close="110"),
        _candle(2, open_value="100", high="121", low="99", close="120"),
        _candle(3, open_value="100", high="131", low="99", close="130"),
        _candle(4, open_value="100", high="141", low="99", close="140"),
    ]

    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=75),
        as_of=START + timedelta(minutes=75),
        candles=candles,
        moving_average_windows=(3, 5),
    )

    assert snapshot.moving_average_summary.close_mean_series[0].values == (
        Decimal("110"),
        Decimal("120"),
        Decimal("130"),
    )
    assert snapshot.moving_average_summary.close_mean_series[1].values == (Decimal("120"),)
    assert snapshot.moving_average_summary.return_mean_series[0].values == (
        Decimal("0.1"),
        Decimal("0.2"),
        Decimal("0.3"),
    )


def test_context_engine_calculates_range_and_shape_values() -> None:
    candles = [
        _candle(0, open_value="100", high="110", low="95", close="105"),
        _candle(1, open_value="105", high="112", low="104", close="110"),
    ]

    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        candles=candles,
        moving_average_windows=(2,),
    )

    assert snapshot.range_context.true_range_values == (Decimal("15"), Decimal("8"))
    assert snapshot.range_context.average_true_range == Decimal("11.5")
    assert snapshot.range_context.candle_range_values == (Decimal("15"), Decimal("8"))
    assert snapshot.range_context.range_change_ratios == (None, Decimal("-7") / Decimal("15"))
    assert snapshot.candle_shape.body_sizes == (Decimal("5"), Decimal("5"))
    assert snapshot.candle_shape.upper_wick_sizes == (Decimal("5"), Decimal("2"))
    assert snapshot.candle_shape.lower_wick_sizes == (Decimal("5"), Decimal("1"))
    assert snapshot.candle_shape.average_upper_wick_size == Decimal("3.5")
    assert snapshot.candle_shape.average_lower_wick_size == Decimal("3")
    assert snapshot.candle_shape.body_to_range_ratios == (
        Decimal("1") / Decimal("3"),
        Decimal("5") / Decimal("8"),
    )
    assert snapshot.candle_shape.close_location_in_range_values == (
        Decimal("2") / Decimal("3"),
        Decimal("3") / Decimal("4"),
    )


def test_context_engine_calculates_event_context() -> None:
    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=45),
        as_of=START + timedelta(minutes=30),
        candles=[_candle(0), _candle(1), _candle(2)],
        economic_events=[
            _event(5, currency="EUR", impact=EconomicImpact.HIGH, provider_event_id="1"),
            _event(20, currency="USD", impact=EconomicImpact.LOW, provider_event_id="2"),
            _event(40, currency="EUR", impact=EconomicImpact.MEDIUM, provider_event_id="3"),
        ],
        moving_average_windows=(2,),
    )

    assert snapshot.event_context.input_event_count == 3
    assert snapshot.event_context.used_event_count == 2
    assert [(item.impact, item.count) for item in snapshot.event_context.counts_by_impact] == [
        (EconomicImpact.HIGH, 1),
        (EconomicImpact.LOW, 1),
    ]
    assert [(item.currency, item.count) for item in snapshot.event_context.counts_by_currency] == [
        ("EUR", 1),
        ("USD", 1),
    ]
    assert snapshot.event_context.latest_event_time == START + timedelta(minutes=20)
    assert snapshot.event_context.minutes_since_latest_event == Decimal("10")
    assert ContextIssueCode.EVENT_AFTER_AS_OF in _issue_codes(snapshot)


def test_context_models_are_immutable() -> None:
    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=15),
        as_of=START + timedelta(minutes=15),
        candles=[_candle(0)],
        moving_average_windows=(1,),
    )

    with pytest.raises(ValidationError):
        snapshot.return_distribution.close_values = (Decimal("999"),)


class _ContextCandleRepository:
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


class _ContextEventRepository:
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


class _ContextRepositories:
    def __init__(
        self,
        candle_repository: _ContextCandleRepository,
        event_repository: _ContextEventRepository,
    ) -> None:
        self.candles = candle_repository
        self.economic_events = event_repository


@asynccontextmanager
async def _context_repositories(
    candle_repository: _ContextCandleRepository,
    event_repository: _ContextEventRepository,
):
    yield _ContextRepositories(candle_repository, event_repository)


class _ContextUnitOfWorkFactory:
    def __init__(
        self,
        candle_repository: _ContextCandleRepository,
        event_repository: _ContextEventRepository,
    ) -> None:
        self._candle_repository = candle_repository
        self._event_repository = event_repository

    def __call__(self):
        return _context_repositories(self._candle_repository, self._event_repository)


@pytest.mark.asyncio
async def test_context_service_reads_repositories_and_builds_snapshot() -> None:
    candle_repository = _ContextCandleRepository([_candle(0), _candle(1)])
    event_repository = _ContextEventRepository([_event(5, provider_event_id="service")])
    service = ContextService(_ContextUnitOfWorkFactory(candle_repository, event_repository))

    snapshot = await service.build_market_context(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        provider="unit",
        moving_average_windows=(2,),
    )

    assert snapshot.time_context.candle_count == 2
    assert snapshot.event_context.used_event_count == 1
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
    assert status.json()["project_phase"] == "phase_3c_indicator_context_foundation"
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

