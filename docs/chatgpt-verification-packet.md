# ChatGPT Verification Packet: Phase 4A Signal Contract Foundation

Generated: 2026-07-18T12:16:14Z

## Repository Metadata

- Repository path: `/Users/artem.otsel/Documents/ai-trading-os`
- Git branch: `main`
- Current commit hash: `bad58a4702b9e3d03fc566f5b2f21006019306c7`
- Latest expected commit from prompt: `bad58a4 Add Phase 3I persistent digest audit foundation`
- Commit status: Phase 4A remains uncommitted at packet generation time.

## Preflight

Preflight passed before edits:

```text
git status --short
<clean>

git log --oneline -1
bad58a4 Add Phase 3I persistent digest audit foundation
```

## Git Status Short

```text
 M AGENTS.md
 M PLANS.md
 M README.md
 M app/core/constants.py
 M app/domain/entities/__init__.py
 M docs/chatgpt-verification-packet.md
 M docs/operations.md
 M tests/contract/test_safety_boundaries.py
 M tests/integration/test_database_and_api.py
 M tests/unit/test_analysis_snapshot_foundation.py
 M tests/unit/test_readiness_scheduler_foundation.py
?? app/domain/entities/signal_contract.py
?? docs/phase4a-verification-report.md
?? tests/unit/test_signal_contract_foundation.py
```

## Git Diff Stat

```text
 AGENTS.md                                         |   23 +-
 PLANS.md                                          |   20 +-
 README.md                                         |   16 +-
 app/core/constants.py                             |    2 +-
 app/domain/entities/__init__.py                   |   14 +
 docs/chatgpt-verification-packet.md               | 2647 ++++++---------------
 docs/operations.md                                |    5 +
 tests/contract/test_safety_boundaries.py          |   76 +-
 tests/integration/test_database_and_api.py        |    2 +-
 tests/unit/test_analysis_snapshot_foundation.py   |    4 +-
 tests/unit/test_readiness_scheduler_foundation.py |    2 +-
 11 files changed, 816 insertions(+), 1995 deletions(-)
```

## Git Log

```text
bad58a4 Add Phase 3I persistent digest audit foundation
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

- `app/domain/entities/signal_contract.py`
- `docs/phase4a-verification-report.md`
- `tests/unit/test_signal_contract_foundation.py`

## Modified Files

- `AGENTS.md`
- `PLANS.md`
- `README.md`
- `app/core/constants.py`
- `app/domain/entities/__init__.py`
- `docs/chatgpt-verification-packet.md`
- `docs/operations.md`
- `tests/contract/test_safety_boundaries.py`
- `tests/integration/test_database_and_api.py`
- `tests/unit/test_analysis_snapshot_foundation.py`
- `tests/unit/test_readiness_scheduler_foundation.py`

## Migration Files Created Or Modified

- None

Phase 4A did not require a migration. Alembic head remains `0003_phase3i_digest_audit (head)`.

## Phase Scope Confirmation

Phase 4A starts Phase 4 but is contract-only. It defines typed contracts, value objects, validation rules, deterministic serialization, deterministic fingerprinting, tests, and documentation for future signal contract objects.

Phase 4A does not implement signal generation, strategy rules, setup scoring, confidence scoring, automated LONG/SHORT decisions, buy/sell recommendations, entry calculation logic, stop loss calculation logic, take profit calculation logic, position sizing logic, portfolio/risk decisions, AI agents, OpenAI calls, LLM usage, Telegram signal sending, broker APIs, order execution, paper trading, real trading, backtesting, or a trading simulator.

Contracts default to `NOT_ACTIONABLE` and must not be treated as recommendations.

Phase 3J does not exist in the final result:

```text
<no Phase 3J references found outside this packet/report>
```

## Implementation Summary

- Updated `PROJECT_PHASE` to `phase_4a_signal_contract_foundation`.
- Added immutable domain contract models in `app/domain/entities/signal_contract.py`.
- Exported the contract types from `app/domain/entities/__init__.py`.
- Added validation for UTC timestamps, valid time windows, ordered entry range, LONG/SHORT price relationships, risk percent, max loss amount, and position size.
- Added deterministic JSON serialization and SHA-256 fingerprinting that excludes the optional stored fingerprint field.
- Normalized evidence IDs and warnings into sorted unique tuples before serialization/fingerprinting.
- Added contract-only safety tests proving no signal API route, Telegram handler, scheduler job, generation engine, or execution behavior was added.
- Updated README, AGENTS, PLANS, operations docs, Phase 4A report, and this packet.

## Exact Verification Command Outputs

### Host Checks

The requested `uv ...` checks were executed with `/Users/artem.otsel/.local/bin` prepended to PATH because this Codex shell does not include that directory by default. This is an environment path detail, not a project failure.

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

### Docker And PostgreSQL Checks

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

## Skipped Checks

- Host `uv run pytest` skipped 7 integration tests because host integration tests require `REQUIRE_INTEGRATION_TESTS=true` and a PostgreSQL integration database. The same integration file was run in Docker twice with `REQUIRE_INTEGRATION_TESTS=true`, and both runs passed.

## Unavailable Checks

- None for the requested Phase 4A verification set. Docker Desktop, PostgreSQL container, Alembic, and integration tests were available and run.

## Remaining Risks

- Phase 4A defines future signal contract shape only. No future signal generator consumes it yet.
- The contract contains future planning fields such as entry range, stop loss, take profit, and position size, but no code calculates those values or treats the contract as actionable.
- Existing inactive signal/trading/paper tables remain present from earlier foundation schema work but were not activated or used.

## Traceability

| Requirement | Implementation file | Test file | Verification result |
| --- | --- | --- | --- |
| Update project phase to Phase 4A | `app/core/constants.py` | `tests/unit/test_signal_contract_foundation.py`, `tests/integration/test_database_and_api.py` | Host and Docker tests passed |
| Add immutable signal contract models | `app/domain/entities/signal_contract.py`, `app/domain/entities/__init__.py` | `tests/unit/test_signal_contract_foundation.py` | Immutability test passed |
| Normalize timestamps to UTC | `app/domain/entities/signal_contract.py` | `tests/unit/test_signal_contract_foundation.py` | UTC normalization test passed |
| Validate valid_until after created_at | `app/domain/entities/signal_contract.py` | `tests/unit/test_signal_contract_foundation.py` | Validation test passed |
| Validate entry range and LONG/SHORT price relationships | `app/domain/entities/signal_contract.py` | `tests/unit/test_signal_contract_foundation.py` | LONG, SHORT, and entry range tests passed |
| Validate risk percent, max loss, and position size bounds | `app/domain/entities/signal_contract.py` | `tests/unit/test_signal_contract_foundation.py` | Risk validation tests passed |
| Default contracts to NOT_ACTIONABLE | `app/domain/entities/signal_contract.py` | `tests/unit/test_signal_contract_foundation.py` | Default actionability and is_actionable tests passed |
| Add deterministic JSON serialization and fingerprinting | `app/domain/entities/signal_contract.py` | `tests/unit/test_signal_contract_foundation.py` | Serialization and fingerprint tests passed |
| Add no API routes, Telegram handlers, scheduler jobs, generation, or execution | No API/service/scheduler/Telegram changes for signals | `tests/contract/test_safety_boundaries.py`, `scripts/security_check.py` | Safety tests and security check passed |
| Preserve existing snapshot/digest foundations | Existing Telegram/readiness files unchanged for signal behavior | `tests/unit/test_telegram_commands.py`, `tests/unit/test_readiness_scheduler_foundation.py` | Host pytest passed |
| No migration required | No migration file created or modified | `docker compose run --rm migrate alembic current`, `docker compose run --rm migrate alembic check` | Alembic head remained `0003_phase3i_digest_audit (head)` and check passed |

## Full Contents Of Changed Source Files

### `app/core/constants.py`

```python
PROJECT_PHASE = "phase_4a_signal_contract_foundation"
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
from app.domain.entities.scheduled_digest import (
    ScheduledDigestConfig,
    ScheduledDigestDecision,
    ScheduledDigestDecisionReason,
    ScheduledDigestDeliveryRecord,
    ScheduledDigestDeliveryResult,
    ScheduledDigestTick,
)
from app.domain.entities.signal_contract import (
    SignalActionability,
    SignalContract,
    SignalDirection,
    SignalLifecycleStatus,
    SignalPricePlan,
    SignalRiskPlan,
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
    "ScheduledDigestConfig",
    "ScheduledDigestDecision",
    "ScheduledDigestDecisionReason",
    "ScheduledDigestDeliveryRecord",
    "ScheduledDigestDeliveryResult",
    "ScheduledDigestTick",
    "SignalActionability",
    "SignalContract",
    "SignalDirection",
    "SignalLifecycleStatus",
    "SignalPricePlan",
    "SignalRiskPlan",
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

### `app/domain/entities/signal_contract.py`

```python
import hashlib
import json
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.market_data import Timeframe
from app.domain.value_objects import CurrencyPair


class SignalDirection(StrEnum):
    LONG = "LONG"
    SHORT = "SHORT"


class SignalLifecycleStatus(StrEnum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class SignalActionability(StrEnum):
    NOT_ACTIONABLE = "NOT_ACTIONABLE"
    PAPER_ONLY = "PAPER_ONLY"
    LIVE_DISABLED = "LIVE_DISABLED"


def _reject_float(value: object, field_name: str) -> object:
    if isinstance(value, float):
        raise ValueError(f"{field_name} must use Decimal-compatible inputs, not float")
    return value


class SignalPricePlan(BaseModel):
    entry_min: Decimal = Field(gt=Decimal("0"))
    entry_max: Decimal = Field(gt=Decimal("0"))
    stop_loss: Decimal = Field(gt=Decimal("0"))
    take_profit_1: Decimal = Field(gt=Decimal("0"))
    take_profit_2: Decimal | None = Field(default=None, gt=Decimal("0"))

    model_config = ConfigDict(frozen=True)

    @field_validator(
        "entry_min", "entry_max", "stop_loss", "take_profit_1", "take_profit_2", mode="before"
    )
    @classmethod
    def reject_float_prices(cls, value: object) -> object:
        return _reject_float(value, "signal price")

    @model_validator(mode="after")
    def entry_range_must_be_ordered(self) -> Self:
        if self.entry_min > self.entry_max:
            raise ValueError("entry_min must be less than or equal to entry_max")
        return self


class SignalRiskPlan(BaseModel):
    risk_percent: Decimal | None = Field(default=None, gt=Decimal("0"), le=Decimal("5"))
    max_loss_amount: Decimal | None = Field(default=None, gt=Decimal("0"))
    position_size: Decimal | None = Field(default=None, gt=Decimal("0"))
    actionability: SignalActionability = SignalActionability.NOT_ACTIONABLE

    model_config = ConfigDict(frozen=True)

    @field_validator("risk_percent", "max_loss_amount", "position_size", mode="before")
    @classmethod
    def reject_float_risk_values(cls, value: object) -> object:
        return _reject_float(value, "signal risk value")


class SignalContract(BaseModel):
    contract_version: str = Field(min_length=1)
    pair: CurrencyPair
    timeframe: Timeframe
    direction: SignalDirection
    status: SignalLifecycleStatus = SignalLifecycleStatus.DRAFT
    actionability: SignalActionability = SignalActionability.NOT_ACTIONABLE
    created_at: datetime
    valid_until: datetime
    strategy_version: str = Field(min_length=1)
    price_plan: SignalPricePlan
    risk_plan: SignalRiskPlan | None = None
    rationale_summary: str | None = Field(default=None, max_length=1000)
    evidence_ids: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    source_snapshot_id: str | None = Field(default=None, min_length=64, max_length=64)
    fingerprint: str | None = Field(default=None, min_length=64, max_length=64)

    model_config = ConfigDict(frozen=True)

    @field_validator("created_at", "valid_until")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("evidence_ids", "warnings", mode="before")
    @classmethod
    def normalize_string_collections(cls, value: object) -> tuple[str, ...]:
        if value is None:
            return ()
        if isinstance(value, str):
            raw_items: tuple[object, ...] = (value,)
        elif isinstance(value, list | set | tuple):
            raw_items = tuple(value)
        else:
            raise ValueError("signal string collections must be lists, sets, tuples, or strings")
        return tuple(sorted({str(item).strip() for item in raw_items if str(item).strip()}))

    @model_validator(mode="after")
    def validate_contract(self) -> Self:
        if self.valid_until <= self.created_at:
            raise ValueError("valid_until must be after created_at")
        if self.direction == SignalDirection.LONG:
            if self.price_plan.stop_loss >= self.price_plan.entry_min:
                raise ValueError("LONG stop_loss must be below entry_min")
            if self.price_plan.take_profit_1 <= self.price_plan.entry_max:
                raise ValueError("LONG take_profit_1 must be above entry_max")
            if (
                self.price_plan.take_profit_2 is not None
                and self.price_plan.take_profit_2 <= self.price_plan.take_profit_1
            ):
                raise ValueError("LONG take_profit_2 must be above take_profit_1")
        else:
            if self.price_plan.stop_loss <= self.price_plan.entry_max:
                raise ValueError("SHORT stop_loss must be above entry_max")
            if self.price_plan.take_profit_1 >= self.price_plan.entry_min:
                raise ValueError("SHORT take_profit_1 must be below entry_min")
            if (
                self.price_plan.take_profit_2 is not None
                and self.price_plan.take_profit_2 >= self.price_plan.take_profit_1
            ):
                raise ValueError("SHORT take_profit_2 must be below take_profit_1")
        return self

    @property
    def is_actionable(self) -> bool:
        return False

    def canonical_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"fingerprint"})

    def deterministic_json(self) -> str:
        return json.dumps(
            self.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def fingerprint_sha256(self) -> str:
        canonical = json.dumps(
            self.canonical_payload(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```


## Full Contents Of Changed Test Files

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
from app.domain.entities import Timeframe, signal_contract
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
PHASE_4A_CONTRACT_OBJECTS = (
    signal_contract.SignalActionability,
    signal_contract.SignalContract,
    signal_contract.SignalDirection,
    signal_contract.SignalLifecycleStatus,
    signal_contract.SignalPricePlan,
    signal_contract.SignalRiskPlan,
)
PHASE_4A_FORBIDDEN_BEHAVIOR_TERMS = (
    "generate_signal",
    "signal_generator",
    "signal_engine",
    "decision_engine",
    "setup_scoring",
    "confidence_scoring",
    "calculate_entry",
    "calculate_stop",
    "calculate_target",
    "calculate_position_size",
    "send_signal",
    "telegram_signal",
    "broker",
    "place_order",
    "submit_order",
    "execute_order",
    "paper_trading",
    "real_trading",
    "backtesting",
    "trading_simulator",
    "OpenAI",
    "LLM",
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


def test_phase4a_signal_contract_objects_do_not_add_generation_or_execution_terms() -> None:
    offenders: list[str] = []
    texts = [inspect.getsource(source_object) for source_object in PHASE_4A_CONTRACT_OBJECTS]
    for index, text in enumerate(texts):
        lowered = text.lower()
        for term in PHASE_4A_FORBIDDEN_BEHAVIOR_TERMS:
            if term.lower() in lowered:
                offenders.append(f"phase4a-contract-{index}: {term}")

    assert offenders == []


def test_phase4a_does_not_add_signal_api_routes() -> None:
    route_files = tuple(Path("app/api/routes").glob("*.py"))
    offenders = [
        str(file_path)
        for file_path in route_files
        if "signal" in file_path.name.lower()
        or "SignalContract" in file_path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_phase4a_does_not_add_telegram_signal_handlers() -> None:
    source = Path("app/telegram/commands.py").read_text(encoding="utf-8")

    assert "signal_command" not in source
    assert 'CommandHandler("signal"' not in source
    assert "SignalContract" not in source


def test_phase4a_does_not_add_scheduler_signal_jobs() -> None:
    scheduler_text = "\n".join(
        file_path.read_text(encoding="utf-8") for file_path in Path("app/scheduler").glob("*.py")
    )

    assert "SignalContract" not in scheduler_text
    assert "signal_job" not in scheduler_text
    assert "generate_signal" not in scheduler_text


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
    assert status.json()["project_phase"] == constants.PROJECT_PHASE
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

    assert data["metadata"]["project_phase"] == constants.PROJECT_PHASE
    assert constants.PROJECT_PHASE in text
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
    assert constants.PROJECT_PHASE in digest.model_dump_json()
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

### `tests/unit/test_signal_contract_foundation.py`

```python
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.entities import Timeframe
from app.domain.entities.signal_contract import (
    SignalActionability,
    SignalContract,
    SignalDirection,
    SignalLifecycleStatus,
    SignalPricePlan,
    SignalRiskPlan,
)
from app.domain.value_objects import CurrencyPair

PAIR = CurrencyPair(value="EURUSD")
CREATED_AT = datetime(2026, 7, 18, 9, 0, tzinfo=UTC)
VALID_UNTIL = CREATED_AT + timedelta(minutes=30)


def _long_price_plan() -> SignalPricePlan:
    return SignalPricePlan(
        entry_min=Decimal("1.1000"),
        entry_max=Decimal("1.1010"),
        stop_loss=Decimal("1.0950"),
        take_profit_1=Decimal("1.1060"),
        take_profit_2=Decimal("1.1100"),
    )


def _short_price_plan() -> SignalPricePlan:
    return SignalPricePlan(
        entry_min=Decimal("1.1000"),
        entry_max=Decimal("1.1010"),
        stop_loss=Decimal("1.1060"),
        take_profit_1=Decimal("1.0950"),
        take_profit_2=Decimal("1.0910"),
    )


def _contract(**overrides: object) -> SignalContract:
    values: dict[str, object] = {
        "contract_version": "phase4a-contract-v1",
        "pair": PAIR,
        "timeframe": Timeframe.M15,
        "direction": SignalDirection.LONG,
        "created_at": CREATED_AT,
        "valid_until": VALID_UNTIL,
        "strategy_version": "future-strategy-contract-v1",
        "price_plan": _long_price_plan(),
        "evidence_ids": ("snapshot-b", "snapshot-a", "snapshot-a"),
        "warnings": ("contract only",),
        "source_snapshot_id": "a" * 64,
    }
    values.update(overrides)
    return SignalContract(**values)


def test_project_phase_is_phase4a_signal_contract_foundation() -> None:
    assert constants.PROJECT_PHASE == "phase_4a_signal_contract_foundation"


def test_signal_contract_models_are_immutable() -> None:
    contract = _contract()

    with pytest.raises(ValidationError):
        contract.status = SignalLifecycleStatus.VALIDATED
    with pytest.raises(ValidationError):
        contract.price_plan.entry_min = Decimal("1.0990")


def test_signal_contract_normalizes_timestamps_to_utc() -> None:
    offset = timezone(timedelta(hours=2))
    contract = _contract(
        created_at=datetime(2026, 7, 18, 11, 0, tzinfo=offset),
        valid_until=datetime(2026, 7, 18, 11, 30, tzinfo=offset),
    )

    assert contract.created_at == CREATED_AT
    assert contract.valid_until == VALID_UNTIL


def test_signal_contract_requires_valid_until_after_created_at() -> None:
    with pytest.raises(ValidationError):
        _contract(valid_until=CREATED_AT)


def test_signal_price_plan_requires_ordered_entry_range() -> None:
    with pytest.raises(ValidationError):
        SignalPricePlan(
            entry_min=Decimal("1.1020"),
            entry_max=Decimal("1.1010"),
            stop_loss=Decimal("1.0950"),
            take_profit_1=Decimal("1.1060"),
        )


def test_signal_contract_validates_long_price_plan() -> None:
    assert _contract(direction=SignalDirection.LONG, price_plan=_long_price_plan()).direction == (
        SignalDirection.LONG
    )

    with pytest.raises(ValidationError):
        _contract(
            direction=SignalDirection.LONG,
            price_plan=_long_price_plan().model_copy(update={"stop_loss": Decimal("1.1000")}),
        )
    with pytest.raises(ValidationError):
        _contract(
            direction=SignalDirection.LONG,
            price_plan=_long_price_plan().model_copy(update={"take_profit_1": Decimal("1.1010")}),
        )
    with pytest.raises(ValidationError):
        _contract(
            direction=SignalDirection.LONG,
            price_plan=_long_price_plan().model_copy(update={"take_profit_2": Decimal("1.1060")}),
        )


def test_signal_contract_validates_short_price_plan() -> None:
    assert _contract(direction=SignalDirection.SHORT, price_plan=_short_price_plan()).direction == (
        SignalDirection.SHORT
    )

    with pytest.raises(ValidationError):
        _contract(
            direction=SignalDirection.SHORT,
            price_plan=_short_price_plan().model_copy(update={"stop_loss": Decimal("1.1010")}),
        )
    with pytest.raises(ValidationError):
        _contract(
            direction=SignalDirection.SHORT,
            price_plan=_short_price_plan().model_copy(update={"take_profit_1": Decimal("1.1000")}),
        )
    with pytest.raises(ValidationError):
        _contract(
            direction=SignalDirection.SHORT,
            price_plan=_short_price_plan().model_copy(update={"take_profit_2": Decimal("1.0950")}),
        )


def test_signal_risk_plan_rejects_invalid_values() -> None:
    with pytest.raises(ValidationError):
        SignalRiskPlan(risk_percent=Decimal("5.1"))
    with pytest.raises(ValidationError):
        SignalRiskPlan(max_loss_amount=Decimal("0"))
    with pytest.raises(ValidationError):
        SignalRiskPlan(position_size=Decimal("0"))


def test_signal_contract_defaults_to_not_actionable() -> None:
    contract = _contract()
    risk_plan = SignalRiskPlan()

    assert contract.actionability == SignalActionability.NOT_ACTIONABLE
    assert risk_plan.actionability == SignalActionability.NOT_ACTIONABLE
    assert contract.is_actionable is False


def test_signal_contract_serializes_deterministically_and_round_trips() -> None:
    contract = _contract()
    same_contract = _contract(evidence_ids=("snapshot-a", "snapshot-b"))

    assert contract.evidence_ids == ("snapshot-a", "snapshot-b")
    assert contract.deterministic_json() == same_contract.deterministic_json()
    assert SignalContract.model_validate_json(contract.deterministic_json()) == contract


def test_signal_contract_fingerprint_is_deterministic() -> None:
    contract = _contract()
    same_contract = _contract(evidence_ids=("snapshot-b", "snapshot-a"))

    assert contract.fingerprint_sha256() == same_contract.fingerprint_sha256()
    assert len(contract.fingerprint_sha256()) == 64


def test_signal_contract_fingerprint_changes_when_key_fields_change() -> None:
    contract = _contract()
    changed = _contract(direction=SignalDirection.SHORT, price_plan=_short_price_plan())

    assert contract.fingerprint_sha256() != changed.fingerprint_sha256()
```


## Documentation Files Updated

- `README.md`
- `AGENTS.md`
- `PLANS.md`
- `docs/operations.md`
- `docs/phase4a-verification-report.md`
- `docs/chatgpt-verification-packet.md`
