# AI Trading OS - Phase 3F Verification Packet

Generated at: `2026-07-15T17:24:22Z`

## Scope

This packet documents Phase 3F: neutral readiness scheduler / snapshot digest foundation. Phase 3F
builds typed, immutable, JSON-serializable schedule plans, digest items, digest summaries, and
notification payloads from existing Phase 3D analysis snapshots.

Phase 3F is uncommitted at packet generation time. Phase 4 was not started.

No strategy, signals, setup scoring, confidence scoring, AI agents, OpenAI calls, broker APIs,
paper trading, order execution, or real trading were added or activated. Existing foundation-era
signal/trading/paper schemas remain inactive.

## Git Metadata

- Branch: `main`
- Current commit hash: `588ab6a51eb52b4455688fd8e4cc3fdfc533a6dd`

### `git status --short`

```text
 M AGENTS.md
 M PLANS.md
 M README.md
 M app/core/constants.py
 M app/domain/entities/__init__.py
 M app/telegram/formatter.py
 M docs/chatgpt-verification-packet.md
 M docs/operations.md
 M tests/contract/test_safety_boundaries.py
 M tests/integration/test_database_and_api.py
 M tests/unit/test_analysis_snapshot_foundation.py
?? app/domain/entities/readiness.py
?? app/domain/readiness_engine.py
?? app/services/readiness_digest_service.py
?? docs/phase3f-verification-report.md
?? tests/unit/test_readiness_scheduler_foundation.py
```

### `git diff --stat`

```text
 AGENTS.md                                       |   12 +-
 PLANS.md                                        |   13 +-
 README.md                                       |   13 +-
 app/core/constants.py                           |    2 +-
 app/domain/entities/__init__.py                 |   22 +
 app/telegram/formatter.py                       |    5 +
 docs/chatgpt-verification-packet.md             | 1499 ++++++++++++-----------
 docs/operations.md                              |    5 +
 tests/contract/test_safety_boundaries.py        |   48 +
 tests/integration/test_database_and_api.py      |    2 +-
 tests/unit/test_analysis_snapshot_foundation.py |    4 +-
 11 files changed, 909 insertions(+), 716 deletions(-)
```

### `git log --oneline -6`

```text
588ab6a Phase 3E DONE
8166820 phase 3C DONE
60e6e53 Add Phase 3C indicator context foundation
a6f44f0 Add Phase 3B feature engine foundation
03c3acd Add Phase 3A data quality foundation
9d68709 Document Phase 2 runtime verification
```

## Created Files

- `app/domain/entities/readiness.py`
- `app/domain/readiness_engine.py`
- `app/services/readiness_digest_service.py`
- `docs/phase3f-verification-report.md`
- `tests/unit/test_readiness_scheduler_foundation.py`

## Modified Files

- `AGENTS.md`
- `PLANS.md`
- `README.md`
- `app/core/constants.py`
- `app/domain/entities/__init__.py`
- `app/telegram/formatter.py`
- `docs/chatgpt-verification-packet.md`
- `docs/operations.md`
- `tests/contract/test_safety_boundaries.py`
- `tests/integration/test_database_and_api.py`
- `tests/unit/test_analysis_snapshot_foundation.py`

## Implementation Summary

- Updated `PROJECT_PHASE` to `phase_3f_readiness_scheduler_foundation`.
- Added immutable Phase 3F readiness models in `app/domain/entities/readiness.py`.
- Added deterministic planning and digest building in `app/domain/readiness_engine.py`.
- Added `ReadinessDigestService` in `app/services/readiness_digest_service.py` over existing
  `AnalysisService` and UnitOfWork-backed repositories.
- Added Telegram-safe digest body formatting without registering a new automatic delivery command.
- Added tests for latest closed-window resolution, M15/H1 planning, invalid lookback handling, UTC
  normalization, no-future window leakage, dedup key stability, digest aggregation, formatting, JSON
  serialization, immutability, fake-repository service behavior, and existing `/snapshot` coverage.
- Added safety coverage confirming Phase 3F files do not introduce decision/execution terms.
- No migration was added; Phase 3F reads existing Phase 2/3A tables through Phase 3D services only.
- No API route, signal endpoint, network call, provider call, secret, or API key was added.

## Verification Command Outputs

### `uv lock --check`

Exit code: `0`

```text
Resolved 46 packages in 29ms
```

### `uv sync`

Exit code: `0`

```text
Resolved 46 packages in 2ms
Checked 43 packages in 11ms
```

### `uv run ruff format --check .`

Exit code: `0`

```text
104 files already formatted
```

### `uv run ruff check .`

Exit code: `0`

```text
All checks passed!
```

### `uv run mypy app`

Exit code: `0`

```text
Success: no issues found in 74 source files
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
collected 199 items

tests/contract/test_agent_contracts.py ......                            [  3%]
tests/contract/test_api_error_schema.py .                                [  3%]
tests/contract/test_architecture_boundaries.py ..                        [  4%]
tests/contract/test_provider_contracts.py .............................. [ 19%]
...............................                                          [ 35%]
tests/contract/test_safety_boundaries.py .............                   [ 41%]
tests/integration/test_database_and_api.py sssss                         [ 44%]
tests/unit/test_analysis_snapshot_foundation.py ..........               [ 49%]
tests/unit/test_context_engine_foundation.py .............               [ 55%]
tests/unit/test_data_quality_foundation.py ...                           [ 57%]
tests/unit/test_domain_market_models.py ..................               [ 66%]
tests/unit/test_errors_and_redaction.py .......                          [ 69%]
tests/unit/test_feature_engine_foundation.py ...........                 [ 75%]
tests/unit/test_internal_api_key.py ....                                 [ 77%]
tests/unit/test_readiness_scheduler_foundation.py .........              [ 81%]
tests/unit/test_settings.py .........                                    [ 86%]
tests/unit/test_system_state_service.py .....                            [ 88%]
tests/unit/test_telegram_commands.py ....                                [ 90%]
tests/unit/test_telegram_policy.py .....                                 [ 93%]
tests/unit/test_time.py ...                                              [ 94%]
tests/unit/test_unit_of_work_lifecycle.py ......                         [ 97%]
tests/unit/test_value_objects_and_enums.py ....                          [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /Users/artem.otsel/Documents/ai-trading-os/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================== 194 passed, 5 skipped, 1 warning in 0.79s ===================
```

### `uv run python scripts/security_check.py`

Exit code: `0`

```text
```

## Docker and PostgreSQL Verification Outputs

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

#3 [migrate internal] load metadata for ghcr.io/astral-sh/uv:python3.12-bookworm-slim
#3 DONE 0.7s

#4 [bot internal] load .dockerignore
#4 transferring context: 143B done
#4 DONE 0.0s

#5 [migrate 1/5] FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58
#5 resolve ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58 0.0s done
#5 DONE 0.0s

#6 [worker internal] load build context
#6 transferring context: 16.81kB 0.0s done
#6 DONE 0.0s

#7 [api 2/5] WORKDIR /app
#7 CACHED

#8 [api 3/5] COPY pyproject.toml uv.lock* ./
#8 CACHED

#9 [api 4/5] RUN uv sync --frozen --no-dev
#9 CACHED

#10 [api 5/5] COPY . .
#10 CACHED

#11 [worker] exporting to image
#11 exporting layers done
#11 exporting manifest sha256:72605e3f7c5910dc75bd2b546cba58c6fbc3dfc686824f14b6f4648414fceed7 done
#11 exporting config sha256:1967fbb840604bfa94c79843cc127f1c7c693997d561626bee678f36f25d0a55 done
#11 exporting attestation manifest sha256:47ef42af5de4ff2768798b6709f3ed0aba180c0fc726dca99f36a99783986655 0.0s done
#11 exporting manifest list sha256:36a7ed4ca927e30580906ba7e34b16e3dbe0deb22100930fb1a29ee57fd9c56f done
#11 naming to docker.io/library/ai-trading-os-worker:latest done
#11 unpacking to docker.io/library/ai-trading-os-worker:latest done
#11 DONE 0.1s

#12 [api] exporting to image
#12 exporting layers done
#12 exporting manifest sha256:da2eaf726ea1faeec8ffa1ee286e4a527a72282e61ae68872da274be6c654669 done
#12 exporting config sha256:6ef7d13e6e742971ca2501f1f76d828446e812222c29e520e8b0caec30c368ec done
#12 exporting attestation manifest sha256:ec256dab2589dc9b1fc31511f3df90577e6b71d80f58764b321de14a7c6bb183 0.0s done
#12 exporting manifest list sha256:9b06e82474c9bdece30ba5e963d1520fbd7833825461fd712ce4e6c93fa10864 done
#12 naming to docker.io/library/ai-trading-os-api:latest done
#12 unpacking to docker.io/library/ai-trading-os-api:latest done
#12 DONE 0.1s

#13 [bot] exporting to image
#13 exporting layers done
#13 exporting manifest sha256:ff0bde168fed8ad301a6699b2a5724d6fe2313d1686c1c55df3f8f0ef91fc51b done
#13 exporting config sha256:286beec80aedda2dd009b125607d8ae1d1f50e252a85beea121a33e3321770ff done
#13 exporting attestation manifest sha256:e4f59ddf150a1c9898fa16b62a0d61af9f5f9cec08c38f1928f78358cc140120 0.0s done
#13 exporting manifest list sha256:13ad7bdab4926bd42039b6bfb607b72d14740076bd1d54bcb825bac5be4b4a2c done
#13 naming to docker.io/library/ai-trading-os-bot:latest done
#13 unpacking to docker.io/library/ai-trading-os-bot:latest done
#13 DONE 0.1s

#14 [migrate] exporting to image
#14 exporting layers done
#14 exporting manifest sha256:a50e0e43d012b82e575cab53db09093e1d4fde45bec6de891d64d2d1dc178672 done
#14 exporting config sha256:0319e71fff323f8a5cacf1c40572f3b0f71e885064440228e4e459849f3eba52 done
#14 exporting attestation manifest sha256:8b3166a3883328a4500e0d49a0cfde4b0b3dbaab4f6e183b702de36eef08c219 0.0s done
#14 exporting manifest list sha256:8edfb1b01a2d189f87f17593d94b1c6ee554125cc09cafea3c7ec426281549e2 done
#14 naming to docker.io/library/ai-trading-os-migrate:latest done
#14 unpacking to docker.io/library/ai-trading-os-migrate:latest done
#14 DONE 0.1s

#15 [migrate] resolving provenance for metadata file
#15 DONE 0.0s

#16 [api] resolving provenance for metadata file
#16 DONE 0.0s

#17 [worker] resolving provenance for metadata file
#17 DONE 0.0s

#18 [bot] resolving provenance for metadata file
#18 DONE 0.0s
 Image ai-trading-os-worker Built 
 Image ai-trading-os-api Built 
 Image ai-trading-os-bot Built 
 Image ai-trading-os-migrate Built 
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
 Container ai-trading-os-migrate-run-232df7e87233 Creating 
 Container ai-trading-os-migrate-run-232df7e87233 Created 
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
 Container ai-trading-os-migrate-run-caf5a65cce98 Creating 
 Container ai-trading-os-migrate-run-caf5a65cce98 Created 
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
 Container ai-trading-os-migrate-run-a9ce2f0a029b Creating 
 Container ai-trading-os-migrate-run-a9ce2f0a029b Created 
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

### `docker integration run #1`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-f68e18c13ca8 Creating 
 Container ai-trading-os-migrate-run-f68e18c13ca8 Created 
Downloading pygments (1.2MiB)
Downloading ruff (10.5MiB)
Downloading mypy (13.1MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 102ms
Bytecode compiled 1963 files in 468ms
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

### `docker integration run #2`

Exit code: `0`

```text
 Container ai-trading-os-postgres-1 Running 
 Container ai-trading-os-postgres-1 Waiting 
 Container ai-trading-os-postgres-1 Healthy 
 Container ai-trading-os-migrate-run-f3d4777e106d Creating 
 Container ai-trading-os-migrate-run-f3d4777e106d Created 
Downloading pygments (1.2MiB)
Downloading ruff (10.5MiB)
Downloading mypy (13.1MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 41ms
Bytecode compiled 1963 files in 433ms
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
========================= 5 passed, 1 warning in 0.30s =========================
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
- Full API stack `/ready` probing was not rerun for Phase 3F because the requested Docker verification
  set was PostgreSQL, Alembic, integration tests, and compose configuration.

## Unavailable Checks

- None for the requested Phase 3F verification commands. Host `uv` and Docker were available.

## Remaining Risks

- Phase 3F changes are uncommitted at packet generation time.
- Readiness plans and digests are deterministic in-memory structures and are not persisted by design.
- No automatic Telegram delivery path was added; payloads remain mockable and manually invokable from services.

## Phase Boundary Confirmation

- Phase 4 was not started.
- No strategy was added.
- No signals were added.
- No setup scoring or confidence scoring was added.
- No AI agents, OpenAI calls, or LLM calls were added.
- No broker APIs, paper trading, order execution, or real trading were added.
- Telegram output remains neutral readiness reporting only.

## Traceability

| Requirement | Implementation file | Test file | Verification result |
| --- | --- | --- | --- |
| Update project phase to Phase 3F | `app/core/constants.py` | `tests/integration/test_database_and_api.py` | Host pytest and Docker integration tests passed |
| Typed immutable readiness models | `app/domain/entities/readiness.py` | `tests/unit/test_readiness_scheduler_foundation.py` | Host pytest passed |
| Latest closed M15/H1 window planning | `app/domain/readiness_engine.py` | `tests/unit/test_readiness_scheduler_foundation.py` | Host pytest passed |
| Invalid lookback handling | `app/domain/entities/readiness.py`, `app/domain/readiness_engine.py` | `tests/unit/test_readiness_scheduler_foundation.py` | Host pytest passed |
| UTC normalization and no future window leakage | `app/domain/entities/readiness.py`, `app/domain/readiness_engine.py` | `tests/unit/test_readiness_scheduler_foundation.py` | Host pytest passed |
| Deterministic deduplication keys | `app/domain/readiness_engine.py` | `tests/unit/test_readiness_scheduler_foundation.py` | Host pytest passed |
| Digest aggregation READY/INCOMPLETE/BLOCKED | `app/domain/readiness_engine.py` | `tests/unit/test_readiness_scheduler_foundation.py` | Host pytest passed |
| Telegram-safe digest formatting | `app/services/readiness_digest_service.py`, `app/telegram/formatter.py` | `tests/unit/test_readiness_scheduler_foundation.py` | Host pytest passed |
| Service uses AnalysisService and repository protocols | `app/services/readiness_digest_service.py` | `tests/unit/test_readiness_scheduler_foundation.py` | Host pytest and mypy passed |
| Existing `/snapshot` still works | `app/telegram/commands.py`, `app/telegram/formatter.py` | `tests/unit/test_telegram_commands.py` | Host pytest passed |
| Preserve PostgreSQL repeatability | existing repositories and integration tests | `tests/integration/test_database_and_api.py` | Docker integration tests passed twice without DB cleanup |
| Preserve safety boundary | `app/domain/entities/readiness.py`, `app/domain/readiness_engine.py`, `app/services/readiness_digest_service.py` | `tests/contract/test_safety_boundaries.py`, `scripts/security_check.py` | Ruff, pytest, and security check passed |
| Avoid new migrations | no new migration file | `docker compose run --rm migrate alembic check` | No new upgrade operations detected |

## Full Contents of Changed Source Files

### `app/core/constants.py`

```python
PROJECT_PHASE = "phase_3f_readiness_scheduler_foundation"
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
from app.domain.entities.analysis import (
    AnalysisInputAudit,
    AnalysisIssue,
    AnalysisIssueCode,
    AnalysisIssueCount,
    AnalysisNumericSummary,
    AnalysisReadinessStatus,
    AnalysisReport,
    AnalysisSnapshot,
    AnalysisSnapshotMetadata,
    AnalysisWindow,
)
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
from app.domain.entities.readiness import (
    SnapshotDigest,
    SnapshotDigestIssueCount,
    SnapshotDigestItem,
    SnapshotDigestStatus,
    SnapshotNotificationDedupKey,
    SnapshotNotificationPayload,
    SnapshotScheduleItem,
    SnapshotSchedulePlan,
    SnapshotWindow,
    digest_status_from_analysis,
)

__all__ = [
    "AnalysisInputAudit",
    "AnalysisIssue",
    "AnalysisIssueCode",
    "AnalysisIssueCount",
    "AnalysisNumericSummary",
    "AnalysisReadinessStatus",
    "AnalysisReport",
    "AnalysisSnapshot",
    "AnalysisSnapshotMetadata",
    "AnalysisWindow",
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
    "SnapshotDigest",
    "SnapshotDigestIssueCount",
    "SnapshotDigestItem",
    "SnapshotDigestStatus",
    "SnapshotNotificationDedupKey",
    "SnapshotNotificationPayload",
    "SnapshotScheduleItem",
    "SnapshotSchedulePlan",
    "SnapshotWindow",
    "TimeContextSummary",
    "Timeframe",
    "UpsertResult",
    "build_feature_snapshot",
    "digest_status_from_analysis",
]
```

### `app/domain/entities/readiness.py`

```python
from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.analysis import AnalysisReadinessStatus
from app.domain.entities.market_data import Timeframe
from app.domain.value_objects import CurrencyPair


class SnapshotDigestStatus(StrEnum):
    READY = "READY"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"


class SnapshotNotificationDedupKey(BaseModel):
    value: str = Field(min_length=64, max_length=64)

    model_config = ConfigDict(frozen=True)


class SnapshotScheduleItem(BaseModel):
    pair: CurrencyPair
    timeframe: Timeframe
    lookback_candle_count: int = Field(ge=1)
    provider: str | None = None
    currencies: tuple[str, ...] = ()

    model_config = ConfigDict(frozen=True)

    @field_validator("currencies")
    @classmethod
    def currencies_must_be_unique(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(sorted(set(value)))


class SnapshotWindow(BaseModel):
    pair: CurrencyPair
    timeframe: Timeframe
    window_start: datetime
    window_end: datetime
    as_of: datetime
    lookback_candle_count: int = Field(ge=1)
    provider: str | None = None
    currencies: tuple[str, ...] = ()

    model_config = ConfigDict(frozen=True)

    @field_validator("window_start", "window_end", "as_of")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @model_validator(mode="after")
    def validate_window(self) -> Self:
        if self.window_end <= self.window_start:
            raise ValueError("snapshot window_end must be later than window_start")
        if self.window_end > self.as_of:
            raise ValueError("snapshot window_end must not be later than as_of")
        return self


class SnapshotSchedulePlan(BaseModel):
    project_phase: str = Field(min_length=1)
    as_of: datetime
    windows: tuple[SnapshotWindow, ...]

    model_config = ConfigDict(frozen=True)

    @field_validator("as_of")
    @classmethod
    def as_of_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)


class SnapshotDigestIssueCount(BaseModel):
    source: str = Field(min_length=1)
    code: str = Field(min_length=1)
    count: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)


class SnapshotDigestItem(BaseModel):
    pair: CurrencyPair
    timeframe: Timeframe
    window_start: datetime
    window_end: datetime
    as_of: datetime
    readiness_status: SnapshotDigestStatus
    input_candle_count: int = Field(ge=0)
    used_candle_count: int = Field(ge=0)
    input_event_count: int = Field(ge=0)
    used_event_count: int = Field(ge=0)
    issue_count: int = Field(ge=0)
    issue_counts: tuple[SnapshotDigestIssueCount, ...] = ()
    issue_descriptions: tuple[str, ...] = ()
    no_candles_after_as_of_used: bool
    no_events_after_as_of_used: bool
    snapshot_id: str = Field(min_length=64, max_length=64)
    dedup_key: SnapshotNotificationDedupKey

    model_config = ConfigDict(frozen=True)

    @field_validator("window_start", "window_end", "as_of")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)


class SnapshotDigest(BaseModel):
    project_phase: str = Field(min_length=1)
    generated_at: datetime
    as_of: datetime
    readiness_status: SnapshotDigestStatus
    items: tuple[SnapshotDigestItem, ...]
    ready_count: int = Field(ge=0)
    incomplete_count: int = Field(ge=0)
    blocked_count: int = Field(ge=0)
    dedup_key: SnapshotNotificationDedupKey

    model_config = ConfigDict(frozen=True)

    @field_validator("generated_at", "as_of")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)


class SnapshotNotificationPayload(BaseModel):
    project_phase: str = Field(min_length=1)
    dedup_key: SnapshotNotificationDedupKey
    digest: SnapshotDigest
    text: str = Field(min_length=1)

    model_config = ConfigDict(frozen=True)


def digest_status_from_analysis(status: AnalysisReadinessStatus) -> SnapshotDigestStatus:
    return SnapshotDigestStatus(status.value)
```

### `app/domain/readiness_engine.py`

```python
import hashlib
import json
from collections.abc import Sequence
from datetime import datetime

from app.core import constants
from app.core.time import normalize_to_utc
from app.domain.entities.analysis import AnalysisSnapshot
from app.domain.entities.data_quality import TIMEFRAME_TO_DELTA
from app.domain.entities.market_data import Timeframe
from app.domain.entities.readiness import (
    SnapshotDigest,
    SnapshotDigestIssueCount,
    SnapshotDigestItem,
    SnapshotDigestStatus,
    SnapshotNotificationDedupKey,
    SnapshotScheduleItem,
    SnapshotSchedulePlan,
    SnapshotWindow,
    digest_status_from_analysis,
)


class SnapshotReadinessPlanner:
    def build_plan(
        self,
        *,
        items: Sequence[SnapshotScheduleItem],
        as_of: datetime,
    ) -> SnapshotSchedulePlan:
        if not items:
            raise ValueError("at least one schedule item is required")
        as_of_utc = normalize_to_utc(as_of)
        windows = tuple(
            _window_for_item(item=item, as_of=as_of_utc)
            for item in sorted(items, key=lambda value: (value.pair.value, value.timeframe.value))
        )
        return SnapshotSchedulePlan(
            project_phase=constants.PROJECT_PHASE,
            as_of=as_of_utc,
            windows=windows,
        )


class SnapshotDigestBuilder:
    def build_digest(
        self,
        *,
        snapshots: Sequence[AnalysisSnapshot],
        generated_at: datetime,
        as_of: datetime,
    ) -> SnapshotDigest:
        if not snapshots:
            raise ValueError("at least one snapshot is required")
        generated_at_utc = normalize_to_utc(generated_at)
        as_of_utc = normalize_to_utc(as_of)
        items = tuple(
            _digest_item(snapshot)
            for snapshot in sorted(
                snapshots,
                key=lambda value: (value.window.pair.value, value.window.timeframe.value),
            )
        )
        ready_count = sum(
            1 for item in items if item.readiness_status == SnapshotDigestStatus.READY
        )
        incomplete_count = sum(
            1 for item in items if item.readiness_status == SnapshotDigestStatus.INCOMPLETE
        )
        blocked_count = sum(
            1 for item in items if item.readiness_status == SnapshotDigestStatus.BLOCKED
        )
        readiness_status = _combined_status(items)
        dedup_key = SnapshotNotificationDedupKey(
            value=_hash_payload(
                {
                    "project_phase": constants.PROJECT_PHASE,
                    "as_of": as_of_utc.isoformat(),
                    "items": [item.dedup_key.value for item in items],
                    "status": readiness_status.value,
                }
            )
        )
        return SnapshotDigest(
            project_phase=constants.PROJECT_PHASE,
            generated_at=generated_at_utc,
            as_of=as_of_utc,
            readiness_status=readiness_status,
            items=items,
            ready_count=ready_count,
            incomplete_count=incomplete_count,
            blocked_count=blocked_count,
            dedup_key=dedup_key,
        )


def latest_closed_boundary(*, timeframe: Timeframe, as_of: datetime) -> datetime:
    as_of_utc = normalize_to_utc(as_of)
    if timeframe == Timeframe.M15:
        minute = (as_of_utc.minute // 15) * 15
        return as_of_utc.replace(minute=minute, second=0, microsecond=0)
    if timeframe == Timeframe.H1:
        return as_of_utc.replace(minute=0, second=0, microsecond=0)
    raise ValueError(f"unsupported timeframe: {timeframe.value}")


def _window_for_item(*, item: SnapshotScheduleItem, as_of: datetime) -> SnapshotWindow:
    if item.lookback_candle_count < 1:
        raise ValueError("lookback_candle_count must be at least 1")
    window_end = latest_closed_boundary(timeframe=item.timeframe, as_of=as_of)
    delta = TIMEFRAME_TO_DELTA[item.timeframe]
    window_start = window_end - (item.lookback_candle_count * delta)
    return SnapshotWindow(
        pair=item.pair,
        timeframe=item.timeframe,
        window_start=window_start,
        window_end=window_end,
        as_of=as_of,
        lookback_candle_count=item.lookback_candle_count,
        provider=item.provider,
        currencies=item.currencies,
    )


def _digest_item(snapshot: AnalysisSnapshot) -> SnapshotDigestItem:
    status = digest_status_from_analysis(snapshot.readiness_status)
    audit = snapshot.input_audit
    issue_counts = tuple(
        SnapshotDigestIssueCount(
            source=item.source,
            code=item.code.value,
            count=item.count,
        )
        for item in audit.excluded_issue_counts
    )
    issue_descriptions = tuple(issue.description for issue in snapshot.readiness_issues[:5])
    dedup_key = SnapshotNotificationDedupKey(
        value=_hash_payload(
            {
                "project_phase": constants.PROJECT_PHASE,
                "pair": snapshot.window.pair.value,
                "timeframe": snapshot.window.timeframe.value,
                "window_start": snapshot.window.window_start.isoformat(),
                "window_end": snapshot.window.window_end.isoformat(),
                "as_of": snapshot.window.as_of.isoformat(),
                "snapshot_id": snapshot.metadata.snapshot_id,
                "status": status.value,
            }
        )
    )
    return SnapshotDigestItem(
        pair=snapshot.window.pair,
        timeframe=snapshot.window.timeframe,
        window_start=snapshot.window.window_start,
        window_end=snapshot.window.window_end,
        as_of=snapshot.window.as_of,
        readiness_status=status,
        input_candle_count=audit.input_candle_count,
        used_candle_count=audit.used_candle_count,
        input_event_count=audit.input_event_count,
        used_event_count=audit.used_event_count,
        issue_count=len(snapshot.readiness_issues),
        issue_counts=issue_counts,
        issue_descriptions=issue_descriptions,
        no_candles_after_as_of_used=audit.no_candles_after_as_of_used,
        no_events_after_as_of_used=audit.no_events_after_as_of_used,
        snapshot_id=snapshot.metadata.snapshot_id,
        dedup_key=dedup_key,
    )


def _combined_status(items: Sequence[SnapshotDigestItem]) -> SnapshotDigestStatus:
    if any(item.readiness_status == SnapshotDigestStatus.BLOCKED for item in items):
        return SnapshotDigestStatus.BLOCKED
    if any(item.readiness_status == SnapshotDigestStatus.INCOMPLETE for item in items):
        return SnapshotDigestStatus.INCOMPLETE
    return SnapshotDigestStatus.READY


def _hash_payload(payload: object) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

### `app/services/readiness_digest_service.py`

```python
from collections.abc import Sequence
from datetime import datetime

from app.core import constants
from app.domain.entities.readiness import (
    SnapshotDigest,
    SnapshotNotificationPayload,
    SnapshotScheduleItem,
)
from app.domain.readiness_engine import SnapshotDigestBuilder, SnapshotReadinessPlanner
from app.services.analysis_service import AnalysisService


class ReadinessDigestService:
    def __init__(
        self,
        analysis_service: AnalysisService,
        *,
        planner: SnapshotReadinessPlanner | None = None,
        digest_builder: SnapshotDigestBuilder | None = None,
    ) -> None:
        self._analysis_service = analysis_service
        self._planner = planner or SnapshotReadinessPlanner()
        self._digest_builder = digest_builder or SnapshotDigestBuilder()

    async def build_digest(
        self,
        *,
        items: Sequence[SnapshotScheduleItem],
        as_of: datetime,
    ) -> SnapshotDigest:
        plan = self._planner.build_plan(items=items, as_of=as_of)
        snapshots = []
        for window in plan.windows:
            snapshots.append(
                await self._analysis_service.build_snapshot(
                    pair=window.pair,
                    timeframe=window.timeframe,
                    window_start=window.window_start,
                    window_end=window.window_end,
                    as_of=window.as_of,
                    currencies=window.currencies or None,
                    provider=window.provider,
                )
            )
        return self._digest_builder.build_digest(
            snapshots=snapshots,
            generated_at=plan.as_of,
            as_of=plan.as_of,
        )

    async def build_payload(
        self,
        *,
        items: Sequence[SnapshotScheduleItem],
        as_of: datetime,
    ) -> SnapshotNotificationPayload:
        digest = await self.build_digest(items=items, as_of=as_of)
        return SnapshotNotificationPayload(
            project_phase=constants.PROJECT_PHASE,
            dedup_key=digest.dedup_key,
            digest=digest,
            text=readiness_digest_text(digest),
        )


def readiness_digest_text(digest: SnapshotDigest) -> str:
    lines = [
        "Системный отчёт готовности.",
        f"Статус: {digest.readiness_status.value}.",
        "Элементы:",
    ]
    for item in digest.items:
        lines.append(
            f"- {item.pair.value} {item.timeframe.value}: {item.readiness_status.value}, "
            f"свечи {item.used_candle_count}/{item.input_candle_count}, "
            f"проблемы {item.issue_count}"
        )
    lines.append("Решений и указаний нет.")
    return "\n".join(lines)
```

### `app/telegram/formatter.py`

```python
import re

from app.core.enums import MessageType
from app.core.exceptions import MessageFormatInvalidError, RussianTextInvalidError
from app.domain.entities.analysis import AnalysisReadinessStatus, AnalysisSnapshot
from app.domain.entities.readiness import SnapshotDigest
from app.services.readiness_digest_service import readiness_digest_text
from app.telegram.emoji_policy import EMOJI_BY_MESSAGE_TYPE, validate_telegram_emoji

CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")  # noqa: RUF001


def validate_russian_foundation_text(text: str) -> None:
    body = text.strip()
    if not body:
        raise RussianTextInvalidError("Текст сообщения не должен быть пустым.")
    if not CYRILLIC_RE.search(body):
        raise RussianTextInvalidError("Сообщение выглядит как английский-only текст.")


class TelegramFormatter:
    def format(self, message_type: MessageType, body_ru: str) -> str:
        validate_russian_foundation_text(body_ru)
        if any(emoji in body_ru for emoji in EMOJI_BY_MESSAGE_TYPE.values()):
            raise MessageFormatInvalidError("Сервисы не должны вставлять эмодзи в тело сообщения.")
        text = f"{EMOJI_BY_MESSAGE_TYPE[message_type]} {body_ru.strip()}"
        validate_telegram_emoji(message_type, text)
        return text

    def format_analysis_readiness_body(self, snapshot: AnalysisSnapshot) -> str:
        status_ru = {
            AnalysisReadinessStatus.READY: "готово",
            AnalysisReadinessStatus.INCOMPLETE: "неполные данные",
            AnalysisReadinessStatus.BLOCKED: "заблокировано",
        }[snapshot.readiness_status]
        audit = snapshot.input_audit
        future_data_status = (
            "пройдена"
            if audit.no_candles_after_as_of_used and audit.no_events_after_as_of_used
            else "требует проверки"
        )
        issue_summary = _issue_summary(snapshot)
        return (
            f"Отчёт готовности {snapshot.window.pair.value} {snapshot.window.timeframe.value}.\n"
            f"Статус: {status_ru}.\n"
            f"Свечей использовано: {audit.used_candle_count} из {audit.input_candle_count}.\n"
            f"Событий календаря: {audit.used_event_count} из {audit.input_event_count}.\n"
            f"Проверка будущих данных: {future_data_status}.\n"
            f"Проблемы: {issue_summary}.\n"
            f"Снимок: {snapshot.metadata.snapshot_id[:12]}.\n"
            "Только отчёт готовности; торговых действий нет."
        )

    def format_snapshot_digest_body(self, digest: SnapshotDigest) -> str:
        return readiness_digest_text(digest)


def _issue_summary(snapshot: AnalysisSnapshot) -> str:
    if not snapshot.input_audit.excluded_issue_counts:
        return "не обнаружены"
    return "; ".join(
        f"{item.source}/{item.code.value}: {item.count}"
        for item in snapshot.input_audit.excluded_issue_counts[:5]
    )
```

## Migration Contents

No new migration was added for Phase 3F. Existing migration contents are included below.

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
    assert "phase_3f_readiness_scheduler_foundation" in digest.model_dump_json()
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

    assert data["metadata"]["project_phase"] == "phase_3f_readiness_scheduler_foundation"
    assert "phase_3f_readiness_scheduler_foundation" in text
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
    assert status.json()["project_phase"] == "phase_3f_readiness_scheduler_foundation"
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

