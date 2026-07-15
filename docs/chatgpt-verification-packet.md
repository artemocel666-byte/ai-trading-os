# ChatGPT Verification Packet - Phase 3G
## Generation Metadata
- Generation timestamp: 2026-07-15T17:43:10Z
- Repository: `/Users/artem.otsel/Documents/ai-trading-os`
- Git branch: `main`
- Current git commit hash: `40473bdfa967831da953be26971e429bb757c7e2`
- Latest committed baseline: `40473bd Add Phase 3F readiness scheduler foundation`
- Phase 3G state: uncommitted at packet generation time
- Phase 4: not started
- Migration created: none
- Runtime note: host `uv` was available at `/Users/artem.otsel/.local/bin/uv`; commands were run with that directory on PATH.

## Scope Confirmation
- Implemented Phase 3G only: manual Telegram `/digest` readiness digest command foundation.
- `/digest` uses the existing Phase 3F `ReadinessDigestService` and `readiness_digest_text`.
- `/snapshot` remains active and tested.
- Integrations remain disabled by default.
- No strategy, signals, setup scoring, AI agents, OpenAI calls, broker APIs, paper trading, order execution, or real trading were added.
- Feature/analysis/readiness flows remain descriptive and deterministic only.

## Changed Files
Created files:
- `docs/phase3g-verification-report.md`

Modified files:
- `AGENTS.md`
- `PLANS.md`
- `README.md`
- `app/core/constants.py`
- `app/telegram/bot.py`
- `app/telegram/commands.py`
- `docs/operations.md`
- `docs/chatgpt-verification-packet.md`
- `tests/contract/test_safety_boundaries.py`
- `tests/integration/test_database_and_api.py`
- `tests/unit/test_analysis_snapshot_foundation.py`
- `tests/unit/test_readiness_scheduler_foundation.py`
- `tests/unit/test_telegram_commands.py`

## Implementation Summary
- Updated `PROJECT_PHASE` to `phase_3g_telegram_digest_command_foundation`.
- Added `DEFAULT_DIGEST_ITEMS` for EURUSD M15 and EURUSD H1.
- Added `/digest` parsing: no arguments uses defaults; `PAIR TIMEFRAME` builds one schedule item.
- Added Telegram error handling for invalid `/digest` arguments and unavailable local data.
- Wired `ReadinessDigestService` into Telegram bot application state without creating provider clients or network calls.
- Registered `/digest` while keeping `/snapshot`.
- Updated docs for Phase 3G status and operational usage.

## New Or Updated Tests
- `tests/unit/test_telegram_commands.py::test_add_handlers_keeps_snapshot_and_registers_digest`
- `tests/unit/test_telegram_commands.py::test_digest_command_returns_default_readiness_digest`
- `tests/unit/test_telegram_commands.py::test_digest_command_accepts_single_snapshot_identity`
- `tests/unit/test_telegram_commands.py::test_digest_command_rejects_invalid_arguments`
- `tests/contract/test_safety_boundaries.py::test_phase3g_digest_command_does_not_add_decision_or_execution_terms`
- Updated project phase assertions in analysis, readiness, and integration tests.

## Traceability Table
| Requirement | Implementation file | Test file | Verification result |
|---|---|---|---|
| Set Phase 3G project phase | app/core/constants.py | tests/integration/test_database_and_api.py; tests/unit/test_analysis_snapshot_foundation.py; tests/unit/test_readiness_scheduler_foundation.py | Host pytest passed; Docker integration tests passed twice |
| Add manual `/digest` command | app/telegram/commands.py | tests/unit/test_telegram_commands.py | Host pytest passed |
| Use existing readiness digest service | app/telegram/commands.py; app/telegram/bot.py | tests/unit/test_telegram_commands.py | Host pytest passed |
| Keep `/snapshot` working | app/telegram/commands.py | tests/unit/test_telegram_commands.py | Host pytest passed |
| Reject invalid digest args | app/telegram/commands.py | tests/unit/test_telegram_commands.py | Host pytest passed |
| Keep Telegram output neutral and Russian | app/services/readiness_digest_service.py; app/telegram/formatter.py; app/telegram/commands.py | tests/unit/test_telegram_commands.py; tests/contract/test_safety_boundaries.py | Host pytest and security check passed |
| No automatic delivery/provider/OpenAI/broker calls | app/telegram/bot.py; app/telegram/commands.py | tests/contract/test_safety_boundaries.py; scripts/security_check.py | Security check exit code 0 |
| Integration repeatability | tests/integration/test_database_and_api.py | tests/integration/test_database_and_api.py | Docker integration run 1 and run 2 both passed |
| No migration required | none | docker compose run --rm migrate alembic check | No new upgrade operations detected |

## Git Metadata
### git status --short

```
 M AGENTS.md
 M PLANS.md
 M README.md
 M app/core/constants.py
 M app/telegram/bot.py
 M app/telegram/commands.py
 M docs/operations.md
 M tests/contract/test_safety_boundaries.py
 M tests/integration/test_database_and_api.py
 M tests/unit/test_analysis_snapshot_foundation.py
 M tests/unit/test_readiness_scheduler_foundation.py
 M tests/unit/test_telegram_commands.py
?? docs/phase3g-verification-report.md
```
### git diff --stat

```
AGENTS.md                                         | 15 ++--
PLANS.md                                          | 12 ++-
README.md                                         | 12 ++-
app/core/constants.py                             |  2 +-
app/telegram/bot.py                               |  5 +-
app/telegram/commands.py                          | 73 +++++++++++++++++-
docs/operations.md                                | 11 ++-
tests/contract/test_safety_boundaries.py          | 33 +++++++++
tests/integration/test_database_and_api.py        |  2 +-
tests/unit/test_analysis_snapshot_foundation.py   |  4 +-
tests/unit/test_readiness_scheduler_foundation.py |  2 +-
tests/unit/test_telegram_commands.py              | 90 ++++++++++++++++++++++-
12 files changed, 236 insertions(+), 25 deletions(-)
```
### git log --oneline -7

```
40473bd Add Phase 3F readiness scheduler foundation
588ab6a Phase 3E DONE
8166820 phase 3C DONE
60e6e53 Add Phase 3C indicator context foundation
a6f44f0 Add Phase 3B feature engine foundation
03c3acd Add Phase 3A data quality foundation
9d68709 Document Phase 2 runtime verification
```

## Exact Verification Command Outputs
### uv lock --check

```
Resolved 46 packages in 3ms
```
### uv sync

```
Resolved 46 packages in 3ms
Checked 43 packages in 6ms
```
### uv run ruff format --check .

```
104 files already formatted
```
### uv run ruff check .

```
All checks passed!
```
### uv run mypy app

```
Success: no issues found in 74 source files
```
### uv run pytest

```
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/artem.otsel/Documents/ai-trading-os
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.14.1, asyncio-0.26.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 204 items

tests/contract/test_agent_contracts.py ......                            [  2%]
tests/contract/test_api_error_schema.py .                                [  3%]
tests/contract/test_architecture_boundaries.py ..                        [  4%]
tests/contract/test_provider_contracts.py .............................. [ 19%]
...............................                                          [ 34%]
tests/contract/test_safety_boundaries.py ..............                  [ 41%]
tests/integration/test_database_and_api.py sssss                         [ 43%]
tests/unit/test_analysis_snapshot_foundation.py ..........               [ 48%]
tests/unit/test_context_engine_foundation.py .............               [ 54%]
tests/unit/test_data_quality_foundation.py ...                           [ 56%]
tests/unit/test_domain_market_models.py ..................               [ 65%]
tests/unit/test_errors_and_redaction.py .......                          [ 68%]
tests/unit/test_feature_engine_foundation.py ...........                 [ 74%]
tests/unit/test_internal_api_key.py ....                                 [ 75%]
tests/unit/test_readiness_scheduler_foundation.py .........              [ 80%]
tests/unit/test_settings.py .........                                    [ 84%]
tests/unit/test_system_state_service.py .....                            [ 87%]
tests/unit/test_telegram_commands.py ........                            [ 91%]
tests/unit/test_telegram_policy.py .....                                 [ 93%]
tests/unit/test_time.py ...                                              [ 95%]
tests/unit/test_unit_of_work_lifecycle.py ......                         [ 98%]
tests/unit/test_value_objects_and_enums.py ....                          [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /Users/artem.otsel/Documents/ai-trading-os/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================== 199 passed, 5 skipped, 1 warning in 0.81s ===================
```
### uv run python scripts/security_check.py

```
Exit code: 0
Output: <no output>
```
### docker compose build

```
Image ai-trading-os-migrate Building 
 Image ai-trading-os-api Building 
 Image ai-trading-os-worker Building 
 Image ai-trading-os-bot Building 
#1 [internal] load local bake definitions
#1 reading from stdin 1.91kB done
#1 DONE 0.0s

#2 [worker internal] load build definition from Dockerfile
#2 transferring dockerfile: 411B done
#2 DONE 0.0s

#3 [bot internal] load metadata for ghcr.io/astral-sh/uv:python3.12-bookworm-slim
#3 DONE 1.0s

#4 [api internal] load .dockerignore
#4 transferring context: 143B done
#4 DONE 0.0s

#5 [api 1/5] FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58
#5 resolve ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58 0.0s done
#5 DONE 0.0s

#6 [worker internal] load build context
#6 transferring context: 377.31kB 0.0s done
#6 DONE 0.0s

#7 [worker 2/5] WORKDIR /app
#7 CACHED

#8 [worker 3/5] COPY pyproject.toml uv.lock* ./
#8 CACHED

#9 [bot 4/5] RUN uv sync --frozen --no-dev
#9 CACHED

#10 [migrate 5/5] COPY . .
#10 DONE 0.0s

#11 [bot] exporting to image
#11 exporting layers 0.0s done
#11 exporting manifest sha256:562b41f768d9fd141a1ea89a8ca1da3d7f8e5a9153cc43a508d8dd2f1012c4a5 done
#11 exporting config sha256:959ed25815ae45ffd3ecf83cfb6c72ab7aa61f26b84fbf346bbd067ae45834dd done
#11 exporting attestation manifest sha256:80c6423fac3c545f82c9a868dff2f3d53880cae6294539652e038fef0b00c20e 0.0s done
#11 exporting manifest list sha256:d3218f66011fa39cef51f7ac4f8a97fd96e147db2a81da6c7436d49b6e09ad4a done
#11 naming to docker.io/library/ai-trading-os-bot:latest done
#11 unpacking to docker.io/library/ai-trading-os-bot:latest 0.0s done
#11 DONE 0.1s

#12 [worker] exporting to image
#12 exporting layers 0.0s done
#12 exporting manifest sha256:7fccf25ec4e32e8197ab2042a1a2ec8f2ab4fea02c82111dda960dbb97c9efb1 done
#12 exporting config sha256:88fcd90c9c550359514a5974f419da289ec29b2be8d6ac42e64e9d9f94270061 done
#12 exporting attestation manifest sha256:66ae8ddaa8f72cab5b753e5d97e4e72e37738ab0a17283edb68b08889145c216 0.0s done
#12 exporting manifest list sha256:2c34bea6ca838fb069e2d84d2c2ae24bd0e6bbf0231a4c19ab1576362e157772 done
#12 naming to docker.io/library/ai-trading-os-worker:latest done
#12 unpacking to docker.io/library/ai-trading-os-worker:latest 0.0s done
#12 DONE 0.2s

#13 [migrate] exporting to image
#13 exporting layers 0.0s done
#13 exporting manifest sha256:c74ca706a0dbbc62782a893b60b2afcdcc251aeb4fc04a13f1b105f1fd9acc7b done
#13 exporting config sha256:5a5934f00c5abe340c07101b3b6a396921a394cbb0874e8c65b06813d5fe0995 done
#13 exporting attestation manifest sha256:db84c7007763606685badd4f084f33b809ca362c773bf648055b6533f8f6edbf 0.0s done
#13 exporting manifest list sha256:31d402eec27a60dcec57f4b3dc2e8368829c403c9c5d697be643ee02dd5522cc done
#13 naming to docker.io/library/ai-trading-os-migrate:latest done
#13 unpacking to docker.io/library/ai-trading-os-migrate:latest 0.0s done
#13 DONE 0.2s

#14 [api] exporting to image
#14 exporting layers 0.0s done
#14 exporting manifest sha256:6cc66e038c527114dc701a8925c4086d9abed137bd44dcff9041ece0aa7ca415 done
#14 exporting config sha256:1e0e84c7a5adf3c6c7f4b660cd85fc0cf985f69306890ec87feaf99a8e79acad done
#14 exporting attestation manifest sha256:da04695e06e65c891ad1e527785ecbb9a6e6c3e29194a0a47e19d10d81607c80 0.0s done
#14 exporting manifest list sha256:9bc696d9a8f023c04596a31759b55c126cfd7846eeead0d65727bd74702751d0 done
#14 naming to docker.io/library/ai-trading-os-api:latest done
#14 unpacking to docker.io/library/ai-trading-os-api:latest 0.0s done
#14 DONE 0.2s

#15 [api] resolving provenance for metadata file
#15 DONE 0.0s

#16 [worker] resolving provenance for metadata file
#16 DONE 0.0s

#17 [bot] resolving provenance for metadata file
#17 DONE 0.0s

#18 [migrate] resolving provenance for metadata file
#18 DONE 0.0s
 Image ai-trading-os-api Built 
 Image ai-trading-os-bot Built 
 Image ai-trading-os-migrate Built 
 Image ai-trading-os-worker Built
```
### docker compose up -d postgres

```
Network ai-trading-os_default Created
Container ai-trading-os-postgres-1 Created
Container ai-trading-os-postgres-1 Started
Exit code: 0
```
### docker compose ps postgres

```
NAME                       IMAGE                COMMAND                  SERVICE    CREATED         STATUS                   PORTS
ai-trading-os-postgres-1   postgres:16-alpine   "docker-entrypoint.s…"   postgres   7 seconds ago   Up 6 seconds (healthy)   5432/tcp
```
### docker compose run --rm migrate alembic current

```
Container ai-trading-os-postgres-1 Running
Container ai-trading-os-postgres-1 Waiting
Container ai-trading-os-postgres-1 Healthy
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
0002_phase2_data_constraints (head)
```
### docker compose run --rm migrate alembic check

```
Container ai-trading-os-postgres-1 Running
Container ai-trading-os-postgres-1 Waiting
Container ai-trading-os-postgres-1 Healthy
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
### docker compose run --rm -e DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate alembic upgrade head

```
Container ai-trading-os-postgres-1 Running
Container ai-trading-os-postgres-1 Waiting
Container ai-trading-os-postgres-1 Healthy
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
Exit code: 0
```
### docker integration run 1

```
docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py

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
========================= 5 passed, 1 warning in 0.34s =========================
```
### docker integration run 2

```
docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py

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
### docker compose config

```
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
- Host `uv run pytest` skipped 5 integration tests because those require explicit PostgreSQL integration settings.
- Those integration tests were run separately in Docker with `REQUIRE_INTEGRATION_TESTS=true`; both repeated Docker runs passed.

## Unavailable Checks
- None for the requested Phase 3G verification set. Docker, PostgreSQL, Alembic, host uv, and Docker integration checks were available and ran successfully.

## Remaining Risks
- Live Telegram API behavior was not tested with a real bot token; Phase 3G tests use local fakes and application wiring.
- Provider integrations remain disabled and were not called during Phase 3G verification.
- `docker compose config` output includes existing environment defaults such as future-phase configuration placeholders; Phase 3G did not activate them.

## Migration Contents
No migration was added for Phase 3G. Current Alembic head remains `0002_phase2_data_constraints (head)`, and `alembic check` reported `No new upgrade operations detected.`

## Full Contents Of Changed Source Files
### app/core/constants.py

```python
PROJECT_PHASE = "phase_3g_telegram_digest_command_foundation"
STRATEGY_IMPLEMENTED = False
REAL_TRADING_ENABLED = False

SYSTEM_STATE_SCAN_ENABLED = "scan_enabled"
SYSTEM_STATE_WORKER_HEARTBEAT = "worker_heartbeat"
SYSTEM_STATE_LAST_SUCCESSFUL_MARKET_FETCH = "last_successful_market_fetch"
SYSTEM_STATE_LAST_SUCCESSFUL_CALENDAR_FETCH = "last_successful_calendar_fetch"
SYSTEM_STATE_LAST_ERROR = "last_error"

DEFAULT_STRATEGY_VERSION = "foundation-v1"
```
### app/telegram/bot.py

```python
import asyncio
import logging
import signal

from telegram.ext import ApplicationBuilder

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory
from app.services.analysis_service import AnalysisService
from app.services.readiness_digest_service import ReadinessDigestService
from app.services.system_state_service import SystemStateService
from app.telegram.commands import add_handlers
from app.telegram.formatter import TelegramFormatter

logger = logging.getLogger(__name__)


async def run_disabled_mode() -> None:
    settings = get_settings()
    configure_logging("bot", settings.log_level)
    logger.info("telegram_disabled_mode_started")
    await asyncio.Event().wait()


async def run_enabled_bot() -> None:
    settings = get_settings()
    configure_logging("bot", settings.log_level)
    token = settings.telegram_bot_token
    if token is None:
        raise RuntimeError("telegram token is required when Telegram is enabled")

    engine = create_engine(settings.database_dsn())
    session_factory = create_session_factory(engine)
    uow_factory = build_uow_factory(session_factory)
    application = ApplicationBuilder().token(token.get_secret_value()).build()
    analysis_service = AnalysisService(uow_factory)
    application.bot_data["settings"] = settings
    application.bot_data["system_state_service"] = SystemStateService(uow_factory)
    application.bot_data["analysis_service"] = analysis_service
    application.bot_data["readiness_digest_service"] = ReadinessDigestService(analysis_service)
    application.bot_data["formatter"] = TelegramFormatter()
    add_handlers(application)

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    try:
        logger.info("telegram_bot_starting")
        await application.initialize()
        await application.start()
        if application.updater is None:
            raise RuntimeError("telegram updater is unavailable")
        await application.updater.start_polling()
        logger.info("telegram_bot_started")
        await stop_event.wait()
    finally:
        logger.info("telegram_bot_stopping")
        if application.updater is not None:
            await application.updater.stop()
        await application.stop()
        await application.shutdown()
        await engine.dispose()
        logger.info("telegram_bot_stopped")


def main() -> None:
    settings = get_settings()
    if settings.telegram_enabled:
        asyncio.run(run_enabled_bot())
    else:
        asyncio.run(run_disabled_mode())


if __name__ == "__main__":
    main()
```
### app/telegram/commands.py

```python
from datetime import datetime, timedelta
from typing import Any, cast

from pydantic import ValidationError
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.core.config import Settings
from app.core.enums import MessageType
from app.core.exceptions import NotImplementedFeatureError
from app.core.time import normalize_to_utc, utc_now
from app.domain.entities import SnapshotScheduleItem, Timeframe
from app.domain.value_objects import CurrencyPair
from app.services.analysis_service import AnalysisService
from app.services.readiness_digest_service import ReadinessDigestService
from app.services.system_state_service import SystemStateService
from app.telegram.authorization import TelegramIdentity, is_authorized
from app.telegram.formatter import TelegramFormatter

DEFAULT_SNAPSHOT_CANDLE_COUNT = 12
DEFAULT_DIGEST_ITEMS = (
    SnapshotScheduleItem(
        pair=CurrencyPair(value="EURUSD"),
        timeframe=Timeframe.M15,
        lookback_candle_count=DEFAULT_SNAPSHOT_CANDLE_COUNT,
    ),
    SnapshotScheduleItem(
        pair=CurrencyPair(value="EURUSD"),
        timeframe=Timeframe.H1,
        lookback_candle_count=DEFAULT_SNAPSHOT_CANDLE_COUNT,
    ),
)


def _identity(update: Update) -> TelegramIdentity:
    user = update.effective_user
    chat = update.effective_chat
    return TelegramIdentity(
        user_id=user.id if user is not None else None,
        chat_id=chat.id if chat is not None else None,
    )


def _settings(context: ContextTypes.DEFAULT_TYPE) -> Settings:
    return cast(Settings, context.application.bot_data["settings"])


def _system_state_service(context: ContextTypes.DEFAULT_TYPE) -> SystemStateService:
    return cast(SystemStateService, context.application.bot_data["system_state_service"])


def _analysis_service(context: ContextTypes.DEFAULT_TYPE) -> AnalysisService:
    return cast(AnalysisService, context.application.bot_data["analysis_service"])


def _readiness_digest_service(context: ContextTypes.DEFAULT_TYPE) -> ReadinessDigestService:
    return cast(ReadinessDigestService, context.application.bot_data["readiness_digest_service"])


def _formatter(context: ContextTypes.DEFAULT_TYPE) -> TelegramFormatter:
    return cast(TelegramFormatter, context.application.bot_data["formatter"])


async def _reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    message_type: MessageType,
    body_ru: str,
) -> None:
    if update.effective_message is None:
        return
    await update.effective_message.reply_text(_formatter(context).format(message_type, body_ru))


async def _ensure_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    identity = _identity(update)
    command = (
        update.effective_message.text
        if update.effective_message and update.effective_message.text
        else "unknown"
    )
    if is_authorized(_settings(context), identity):
        return True
    await _system_state_service(context).record_unauthorized_telegram_access(
        user_id=identity.user_id,
        chat_id=identity.chat_id,
        command=command.split()[0],
    )
    await _reply(update, context, MessageType.REJECTED, "Доступ запрещён.")
    return False


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    await _reply(
        update,
        context,
        MessageType.EDUCATION,
        "AI Trading OS находится в foundation-фазе и режиме разработки бумажной аналитики.",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    await _reply(
        update,
        context,
        MessageType.EDUCATION,
        (
            "Доступные команды: /start, /help, /status, /start_scan, "
            "/stop_scan, /scan_now, /snapshot, /digest."
        ),
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    status = await _system_state_service(context).get_full_status()
    scan_text = "включено" if status["scan_enabled"] else "выключено"
    heartbeat = status["worker_heartbeat"] or "ещё не получен"
    await _reply(
        update,
        context,
        MessageType.SYSTEM_STATUS,
        (
            "Статус системы: foundation-фаза. "
            f"Сканирование: {scan_text}. "
            f"Пульс worker: {heartbeat}. "
            "Реальная торговля отключена."
        ),
    )


async def start_scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    await _system_state_service(context).enable_scanning(actor="telegram")
    await _reply(
        update,
        context,
        MessageType.APPROVED,
        "Состояние сканирования включено, но аналитическая стратегия ещё не подключена.",
    )


async def stop_scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    await _system_state_service(context).disable_scanning(actor="telegram")
    await _reply(update, context, MessageType.CANCELLED, "Состояние сканирования выключено.")


async def scan_now_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    try:
        await _analysis_service(context).scan_now()
    except NotImplementedFeatureError:
        await _reply(
            update,
            context,
            MessageType.DATA_UNAVAILABLE,
            "Аналитический движок не реализован в foundation-фазе. Результат не создан.",
        )


async def snapshot_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    try:
        pair, timeframe = _parse_snapshot_command(update)
    except (ValueError, ValidationError):
        await _reply(
            update,
            context,
            MessageType.REJECTED,
            "Формат команды: /snapshot EURUSD M15. Поддерживаются M15 и H1.",
        )
        return

    window_start, window_end, as_of = _default_snapshot_window(timeframe)
    try:
        snapshot = await _analysis_service(context).build_snapshot(
            pair=pair,
            timeframe=timeframe,
            window_start=window_start,
            window_end=window_end,
            as_of=as_of,
        )
    except Exception:
        await _reply(
            update,
            context,
            MessageType.DATA_UNAVAILABLE,
            "Отчёт готовности сейчас недоступен. Проверьте базу данных и настройки сервиса.",
        )
        return

    body = _formatter(context).format_analysis_readiness_body(snapshot)
    await _reply(update, context, MessageType.REPORT, body)


async def digest_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    try:
        items = _parse_digest_command(update)
    except (ValueError, ValidationError):
        await _reply(
            update,
            context,
            MessageType.REJECTED,
            "Формат команды: /digest или /digest EURUSD M15. Поддерживаются M15 и H1.",
        )
        return

    try:
        payload = await _readiness_digest_service(context).build_payload(
            items=items,
            as_of=normalize_to_utc(utc_now()),
        )
    except Exception:
        await _reply(
            update,
            context,
            MessageType.DATA_UNAVAILABLE,
            "Дайджест готовности сейчас недоступен. Проверьте базу данных и настройки сервиса.",
        )
        return

    await _reply(update, context, MessageType.REPORT, payload.text)


def _parse_snapshot_command(update: Update) -> tuple[CurrencyPair, Timeframe]:
    text = (
        update.effective_message.text
        if update.effective_message is not None and update.effective_message.text is not None
        else ""
    )
    parts = text.split()
    if len(parts) != 3:
        raise ValueError("snapshot command requires pair and timeframe")
    return CurrencyPair(value=parts[1].upper()), Timeframe(parts[2].upper())


def _parse_digest_command(update: Update) -> tuple[SnapshotScheduleItem, ...]:
    text = (
        update.effective_message.text
        if update.effective_message is not None and update.effective_message.text is not None
        else ""
    )
    parts = text.split()
    if len(parts) == 1:
        return DEFAULT_DIGEST_ITEMS
    if len(parts) != 3:
        raise ValueError("digest command expects no arguments or pair and timeframe")
    return (
        SnapshotScheduleItem(
            pair=CurrencyPair(value=parts[1].upper()),
            timeframe=Timeframe(parts[2].upper()),
            lookback_candle_count=DEFAULT_SNAPSHOT_CANDLE_COUNT,
        ),
    )


def _default_snapshot_window(timeframe: Timeframe) -> tuple[datetime, datetime, datetime]:
    as_of = normalize_to_utc(utc_now())
    if timeframe == Timeframe.M15:
        minute = (as_of.minute // 15) * 15
        window_end = as_of.replace(minute=minute, second=0, microsecond=0)
        step_minutes = 15
    else:
        window_end = as_of.replace(minute=0, second=0, microsecond=0)
        step_minutes = 60
    window_start = window_end - timedelta(minutes=DEFAULT_SNAPSHOT_CANDLE_COUNT * step_minutes)
    return window_start, window_end, window_end


def add_handlers(application: Application[Any, Any, Any, Any, Any, Any]) -> None:
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("start_scan", start_scan_command))
    application.add_handler(CommandHandler("stop_scan", stop_scan_command))
    application.add_handler(CommandHandler("scan_now", scan_now_command))
    application.add_handler(CommandHandler("snapshot", snapshot_command))
    application.add_handler(CommandHandler("digest", digest_command))
```

## Full Contents Of Changed Test Files
### tests/contract/test_safety_boundaries.py

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
### tests/integration/test_database_and_api.py

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
    assert status.json()["project_phase"] == "phase_3g_telegram_digest_command_foundation"
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
### tests/unit/test_analysis_snapshot_foundation.py

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

    assert data["metadata"]["project_phase"] == "phase_3g_telegram_digest_command_foundation"
    assert "phase_3g_telegram_digest_command_foundation" in text
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
### tests/unit/test_readiness_scheduler_foundation.py

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
    assert "phase_3g_telegram_digest_command_foundation" in digest.model_dump_json()
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
### tests/unit/test_telegram_commands.py

```python
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.core.config import Settings
from app.domain.entities import Candle, Timeframe
from app.domain.value_objects import CurrencyPair
from app.services.analysis_service import AnalysisService
from app.services.readiness_digest_service import ReadinessDigestService
from app.telegram import commands
from app.telegram.commands import (
    digest_command,
    scan_now_command,
    snapshot_command,
    start_scan_command,
)
from app.telegram.formatter import TelegramFormatter
from tests.fakes import FakeUnitOfWorkFactory

PAIR = CurrencyPair(value="EURUSD")
BASE_TIME = datetime(2026, 7, 13, 9, 0, tzinfo=UTC)


class FakeUser:
    def __init__(self, user_id: int) -> None:
        self.id = user_id


class FakeChat:
    def __init__(self, chat_id: int) -> None:
        self.id = chat_id


class FakeMessage:
    def __init__(self, text: str) -> None:
        self.text = text
        self.replies: list[str] = []

    async def reply_text(self, text: str) -> None:
        self.replies.append(text)


class FakeUpdate:
    def __init__(self, *, user_id: int, chat_id: int, text: str) -> None:
        self.effective_user = FakeUser(user_id)
        self.effective_chat = FakeChat(chat_id)
        self.effective_message = FakeMessage(text)


class FakeApplication:
    def __init__(self, bot_data: dict[str, object]) -> None:
        self.bot_data = bot_data


class FakeContext:
    def __init__(self, bot_data: dict[str, object]) -> None:
        self.application = FakeApplication(bot_data)


class FakeHandlerApplication:
    def __init__(self) -> None:
        self.handlers: list[FakeCommandHandler] = []

    def add_handler(self, handler: "FakeCommandHandler") -> None:
        self.handlers.append(handler)


class FakeCommandHandler:
    def __init__(self, command: str, callback: object) -> None:
        self.command = command
        self.callback = callback


def _context(factory: FakeUnitOfWorkFactory) -> FakeContext:
    settings = Settings(
        _env_file=None,
        telegram_enabled=True,
        telegram_bot_token="token",
        telegram_allowed_user_id=1,
        telegram_allowed_chat_id=2,
    )
    analysis_service = AnalysisService(factory)
    return FakeContext(
        {
            "settings": settings,
            "system_state_service": __import__(
                "app.services.system_state_service",
                fromlist=["SystemStateService"],
            ).SystemStateService(factory),
            "analysis_service": analysis_service,
            "readiness_digest_service": ReadinessDigestService(analysis_service),
            "formatter": TelegramFormatter(),
        }
    )


def _candle(index: int) -> Candle:
    open_time = BASE_TIME + timedelta(minutes=15 * index)
    open_price = Decimal("1.1000") + (Decimal("0.0005") * Decimal(index))
    close_price = open_price + Decimal("0.0002")
    return Candle(
        provider="telegram-test",
        pair=PAIR,
        timeframe=Timeframe.M15,
        open_time=open_time,
        close_time=open_time + timedelta(minutes=15),
        open=open_price,
        high=close_price + Decimal("0.0003"),
        low=open_price - Decimal("0.0003"),
        close=close_price,
        volume=Decimal("100"),
        is_closed=True,
    )


@pytest.mark.asyncio
async def test_unauthorized_user_cannot_change_scan_state() -> None:
    factory = FakeUnitOfWorkFactory()
    context = _context(factory)
    update = FakeUpdate(user_id=99, chat_id=2, text="/start_scan")

    await start_scan_command(update, context)

    assert "scan_enabled" not in factory.state
    assert update.effective_message.replies == ["❌ Доступ запрещён."]


@pytest.mark.asyncio
async def test_scan_now_command_reports_not_implemented_without_fabrication() -> None:
    factory = FakeUnitOfWorkFactory()
    context = _context(factory)
    update = FakeUpdate(user_id=1, chat_id=2, text="/scan_now")

    await scan_now_command(update, context)

    assert len(update.effective_message.replies) == 1
    assert "Аналитический движок не реализован" in update.effective_message.replies[0]
    assert "LONG" not in update.effective_message.replies[0]
    assert "SHORT" not in update.effective_message.replies[0]


@pytest.mark.asyncio
async def test_snapshot_command_returns_readiness_report(monkeypatch: pytest.MonkeyPatch) -> None:
    factory = FakeUnitOfWorkFactory(candles=[_candle(index) for index in range(12)])
    context = _context(factory)
    update = FakeUpdate(user_id=1, chat_id=2, text="/snapshot EURUSD M15")
    monkeypatch.setattr(commands, "utc_now", lambda: BASE_TIME + timedelta(hours=3))

    await snapshot_command(update, context)

    assert len(update.effective_message.replies) == 1
    reply = update.effective_message.replies[0]
    assert reply.startswith("📊 ")
    assert "Отчёт готовности EURUSD M15" in reply
    assert "Статус: готово" in reply
    assert "Свечей использовано: 12 из 12" in reply
    forbidden_terms = (
        "LONG",
        "SHORT",
        "buy",
        "sell",
        "рекомендую",
        "войти",
        "шортить",
    )
    assert not any(term in reply for term in forbidden_terms)


@pytest.mark.asyncio
async def test_snapshot_command_rejects_invalid_arguments() -> None:
    factory = FakeUnitOfWorkFactory()
    context = _context(factory)
    update = FakeUpdate(user_id=1, chat_id=2, text="/snapshot EURUSD M5")

    await snapshot_command(update, context)

    assert update.effective_message.replies == [
        "❌ Формат команды: /snapshot EURUSD M15. Поддерживаются M15 и H1."
    ]


def test_add_handlers_keeps_snapshot_and_registers_digest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    application = FakeHandlerApplication()
    monkeypatch.setattr(commands, "CommandHandler", FakeCommandHandler)

    commands.add_handlers(application)

    registered = {handler.command: handler.callback for handler in application.handlers}
    assert registered["snapshot"] is snapshot_command
    assert registered["digest"] is digest_command


@pytest.mark.asyncio
async def test_digest_command_returns_default_readiness_digest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    factory = FakeUnitOfWorkFactory(candles=[_candle(index) for index in range(12)])
    context = _context(factory)
    update = FakeUpdate(user_id=1, chat_id=2, text="/digest")
    monkeypatch.setattr(commands, "utc_now", lambda: BASE_TIME + timedelta(hours=3))

    await digest_command(update, context)

    assert len(update.effective_message.replies) == 1
    reply = update.effective_message.replies[0]
    assert reply.startswith("📊 ")
    assert "Системный отчёт готовности" in reply
    assert "EURUSD M15: READY" in reply
    assert "EURUSD H1: BLOCKED" in reply
    assert "Решений и указаний нет." in reply


@pytest.mark.asyncio
async def test_digest_command_accepts_single_snapshot_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    factory = FakeUnitOfWorkFactory(candles=[_candle(index) for index in range(12)])
    context = _context(factory)
    update = FakeUpdate(user_id=1, chat_id=2, text="/digest EURUSD M15")
    monkeypatch.setattr(commands, "utc_now", lambda: BASE_TIME + timedelta(hours=3))

    await digest_command(update, context)

    assert len(update.effective_message.replies) == 1
    reply = update.effective_message.replies[0]
    assert "EURUSD M15: READY" in reply
    assert "EURUSD H1" not in reply
    assert "Решений и указаний нет." in reply


@pytest.mark.asyncio
async def test_digest_command_rejects_invalid_arguments() -> None:
    factory = FakeUnitOfWorkFactory()
    context = _context(factory)
    update = FakeUpdate(user_id=1, chat_id=2, text="/digest EURUSD M5")

    await digest_command(update, context)

    assert update.effective_message.replies == [
        "❌ Формат команды: /digest или /digest EURUSD M15. Поддерживаются M15 и H1."
    ]
```

## Updated Documentation Files
### README.md

```markdown
# AI Trading OS

AI Trading OS is a safety-first foundation for a future modular Forex analysis and paper-trading platform. The current repository implements only infrastructure: API health/status endpoints, async PostgreSQL persistence, a scheduler heartbeat, Telegram command foundations, strict configuration, and safety contracts.

## Current Status

- Current project phase: phase_3g_telegram_digest_command_foundation.
- Trading strategy: not implemented.
- Real trading: disabled and unsupported.
- External integrations: disabled by default.
- Telegram: can run in disabled mode without a token.
- Phase 3D: deterministic analysis snapshot/readiness report foundation only.
- Phase 3E: local Telegram readiness reports only.
- Phase 3F: neutral readiness scheduler/snapshot digest foundation only.
- Phase 3G: manual Telegram `/digest` readiness digest command only.

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
paper trading, order execution, or real trading.

## Phase 3C Status

Phase 3C adds a deterministic, closed-candle-only indicator/context foundation over the Phase 3B
feature engine. It produces typed immutable context snapshots with descriptive close statistics,
return distribution summaries, moving averages, range and candle-shape summaries, event metadata,
time context, and deterministic data-quality issues. It does not produce strategy decisions, setup
scoring, confidence scoring, trade directions, recommendations, signals, AI output, broker activity,
paper trading, order execution, or real trading.

## Phase 3D Status

Phase 3D adds deterministic analysis snapshots and readiness reports over the Phase 3A storage,
Phase 3B feature, and Phase 3C context foundations. It answers neutral infrastructure questions
about window completeness, source inputs, excluded data, quality/context issues, attached summaries,
and no-future-data proof. It does not produce strategy decisions, setup scoring, confidence scoring,
trade directions, recommendations, signals, AI output, broker activity, paper trading, order
execution, or real trading.

## Phase 3E Status

Phase 3E adds a local Telegram readiness-report slice over the deterministic Phase 3D analysis
snapshot foundation. It wires the Telegram bot to the real UnitOfWork-backed analysis service,
adds `/snapshot EURUSD M15`, formats Russian readiness reports with exactly one leading semantic
emoji, and provides `scripts/seed_local_snapshot_data.py` for local demo candles/events. It still
does not produce strategy decisions, setup scoring, confidence scoring, trade directions,
recommendations, signals, AI output, broker activity, paper trading, order execution, or real
trading.

## Phase 3F Status

Phase 3F adds a deterministic readiness scheduler and snapshot digest foundation. It plans neutral
readiness windows for configured pairs/timeframes, resolves the latest fully closed M15/H1 boundary,
aggregates Phase 3D snapshot readiness states, creates deterministic deduplication keys, and builds
Telegram-safe readiness digest payload text. It does not send automatic Telegram messages, produce
strategy decisions, setup scoring, confidence scoring, trade directions, recommendations, signals,
AI output, broker activity, paper trading, order execution, or real trading.

## Phase 3G Status

Phase 3G adds a manual Telegram `/digest` command over the Phase 3F readiness digest service. The
command returns Russian, neutral readiness digest text for the default EURUSD M15/H1 schedule or a
single requested pair/timeframe. It does not add automatic Telegram delivery, provider calls,
strategy decisions, setup scoring, confidence scoring, trade directions, recommendations, signals,
AI output, broker activity, paper trading, order execution, or real trading. Phase 4 has not
started.

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
For a local live Telegram test, see `docs/operations.md` and configure `TELEGRAM_BOT_TOKEN`,
`TELEGRAM_ALLOWED_USER_ID`, and `TELEGRAM_ALLOWED_CHAT_ID` in an uncommitted `.env` file.

## Current Limitations

- No strategy, signals, OpenAI calls, backtesting, position sizing, broker execution, or real trading.
- `/scan_now` explicitly remains disconnected from analysis snapshots and does not fabricate a scan result.
- `/snapshot` returns readiness reports only and does not produce trading guidance.
- `/digest` returns manual readiness digests only and does not produce trading guidance.
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
### AGENTS.md

```markdown
# AI Trading OS Agent Guide

AI Trading OS is a foundation for a future Forex analysis and paper-trading platform.

Current project phase: phase_3g_telegram_digest_command_foundation.
Phase 3G is limited to the manual Telegram `/digest` command over the existing Phase 3F readiness
digest service. External integrations are disabled by default. The project contains no strategy, no
signals, no broker order APIs, no paper trading, and no real trading. Phase 4 has not started.

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
  broker APIs, order execution, or real trading while working in foundation phases.
- While working in Phase 3G, Telegram output is limited to manual readiness reports and readiness
  digests. Do not add Telegram trading signals, entry guidance, LONG/SHORT advice, buy/sell
  recommendations, automatic digest delivery, or paper-trading actions.
- Never fabricate market data, calendar data, agent evidence, or scan results.
- LLM output may explain deterministic results only; it must not change prices, scores, risk, or rejected decisions.
- Update documentation when architecture or safety boundaries change.

## Definition of Done

Code is complete only when tests, formatting, linting, type checking, migrations, and relevant Docker checks have been run or a truthful limitation is documented in `docs/foundation-report.md`.
```
### PLANS.md

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
- Phase 3C indicator/context foundation: deterministic closed-candle context models, context
  calculation engine over Phase 3B features, context service over repository protocols, and safety
  tests confirming no strategy/signals/trading activation.
- Phase 3D analysis snapshot foundation: deterministic readiness report models, analysis snapshot
  engine over Phase 3A/3B/3C outputs, analysis service over repository protocols, and safety tests
  confirming no strategy/signals/trading activation.
- Phase 3E Telegram readiness foundation: local `/snapshot` readiness reports in Telegram,
  UnitOfWork-backed analysis service wiring, local seed data utility, and safety tests confirming no
  strategy/signals/trading activation.
- Phase 3F readiness scheduler foundation: deterministic pair/timeframe readiness plans, latest
  closed-window resolution, snapshot digest payloads, deduplication keys, and safety tests
  confirming no strategy/signals/trading activation.
- Phase 3G Telegram digest command foundation: manual `/digest` command wiring over the existing
  readiness digest service, default EURUSD M15/H1 digest arguments, and safety tests confirming no
  strategy/signals/trading activation.

## Current Implementation Status

The repository has completed the foundation phase, Phase 2 hardening/data adapters, Phase 3A
data-quality foundation, Phase 3B deterministic feature-engine foundation, Phase 3C deterministic
indicator/context foundation, Phase 3D deterministic analysis snapshot/readiness report foundation,
Phase 3E local Telegram readiness-report foundation, and Phase 3F deterministic readiness
scheduler/snapshot digest foundation, and Phase 3G manual Telegram digest command foundation.
Production Twelve Data and FMP adapters exist, but live integrations remain disabled by default.
Scanning state can be enabled or disabled, and Telegram can request readiness reports and readiness
digests, but no strategy, signal generation, AI agent, paper-trading, or execution flow is connected.

## Future Phases

- Phase 2: market-data and calendar adapters — completed as disabled-by-default factories plus
  production adapters covered by MockTransport-backed contract tests
- Phase 3A: data-quality foundation — completed without trading analysis or decisions
- Phase 3B: deterministic feature engine foundation — completed without trading decisions
- Phase 3C: deterministic indicator/context foundation — completed without trading decisions
- Phase 3D: deterministic analysis snapshot/readiness report foundation — completed without trading decisions
- Phase 3E: local Telegram readiness reports — completed without trading decisions
- Phase 3F: neutral readiness scheduler/snapshot digest foundation — completed without trading decisions
- Phase 3G: manual Telegram digest command foundation — completed without trading decisions
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

Phase 4 is the next phase if applicable. It has not started, and no Phase 4 behavior is active.
```
### docs/operations.md

```markdown
# Operations

## Startup

Docker startup:

```bash
docker compose up --build
```

Compose reads `.env` as an optional local runtime override. `.env.example` is only a template.
The API is bound to `127.0.0.1:8000` by default, and PostgreSQL is not exposed to the host by
the default Compose stack.

Local startup:

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:create_app --factory --reload
```

## Shutdown

Use `Ctrl+C` for foreground Compose or:

```bash
docker compose down
```

The worker and Telegram process handle shutdown signals and dispose database resources.

## Migrations

Apply migrations:

```bash
uv run alembic upgrade head
```

Create a migration:

```bash
uv run alembic revision --autogenerate -m "message"
```

## Logs

Application processes emit structured JSON logs with service, component, event, level, timestamp, request IDs where available, and redacted secret-like fields.

## Health Checks

- `GET /health` checks API liveness only.
- `GET /ready` checks database connectivity and schema access.
- `GET /api/v1/system/status` reports phase, scan state, worker heartbeat, enabled integrations, database status, and safety flags.

## Disabled Integrations

The default `.env.example` disables Telegram, OpenAI, market data, calendar, and scanning. Disabled providers raise typed errors before external calls.

## Local Telegram Readiness Demo

Phase 3E can run a local readiness report without live market or calendar integrations. Start
PostgreSQL, migrate the schema, seed deterministic local demo data, and then use `/snapshot EURUSD
M15` in the authorized Telegram chat.

```bash
docker compose up -d postgres
docker compose run --rm migrate alembic upgrade head
docker compose run --rm api python -m scripts.seed_local_snapshot_data
```

To use a real Telegram chat, create a bot token with BotFather, set `TELEGRAM_ENABLED=true`,
`TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USER_ID`, and `TELEGRAM_ALLOWED_CHAT_ID` in `.env`, then
start the bot service. The `/snapshot` command returns readiness reports only; it does not produce
trading guidance or paper-trading actions.

Phase 3F adds an internal readiness digest planner that can prepare neutral digest payloads for
configured pair/timeframe windows. It does not schedule automatic Telegram delivery by itself and
does not call market-data, calendar, AI, or broker services. Any future delivery path must keep
Telegram output limited to readiness reporting text.

Phase 3G exposes that digest foundation through a manual Telegram `/digest` command. `/digest`
returns the default EURUSD M15/H1 readiness digest, and `/digest EURUSD M15` returns a single
pair/timeframe digest. The command remains read-only and neutral; it does not schedule automatic
delivery, call providers, call AI services, contact brokers, or produce trading guidance.

## Telegram Bot Local Setup

Create the bot in Telegram before enabling the `bot` service:

1. Open `@BotFather`.
2. Send `/newbot`.
3. Choose a display name, for example `AI Trading OS Local`.
4. Choose a username ending in `bot`, for example `ai_trading_os_local_bot`.
5. Copy the token. Telegram bot tokens look like `1234567890:AA...`; keep this value secret and
   never commit it.

Find the allowed Telegram identity:

- `TELEGRAM_ALLOWED_USER_ID`: send `/start` to `@userinfobot` or `@getmyid_bot` and copy the
  numeric `Id`.
- `TELEGRAM_ALLOWED_CHAT_ID`: for a direct private chat with the bot, this is usually the same as
  `TELEGRAM_ALLOWED_USER_ID`.
- To confirm the chat ID, send `/start` to your new bot and open
  `https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getUpdates` in a browser. Use the numeric
  `message.chat.id` value from the JSON response.

Create a local `.env` file in the repository root. Do not commit `.env`.

```env
APP_ENV=development
DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os
INTERNAL_API_KEY=development-internal-key-change-me

TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=1234567890:AA_REPLACE_WITH_REAL_SECRET
TELEGRAM_ALLOWED_USER_ID=123456789
TELEGRAM_ALLOWED_CHAT_ID=123456789

OPENAI_ENABLED=false
MARKET_DATA_ENABLED=false
CALENDAR_ENABLED=false
SCAN_ENABLED=false
```

Prepare the local database and demo data:

```bash
docker compose up -d postgres
docker compose run --rm migrate alembic upgrade head
docker compose run --rm api python -m scripts.seed_local_snapshot_data
```

Start only the Telegram bot service:

```bash
docker compose up --build bot
```

Then send these commands to the bot in Telegram:

```text
/start
/status
/snapshot EURUSD M15
/digest
/digest EURUSD M15
```

Expected behavior: `/snapshot EURUSD M15` returns a Russian readiness report with one leading emoji.
`/digest` returns a Russian readiness digest with one leading emoji. These commands must not contain
LONG/SHORT directions, entry guidance, buy/sell recommendations, or paper-trade actions.

## Common Failure Cases

- Missing Telegram token while Telegram is enabled: configuration validation fails.
- PostgreSQL unavailable: readiness fails and state changes cannot persist.
- Migrations not applied: readiness returns not ready.
- Wrong internal API key: state-changing API calls return `UNAUTHORIZED`.

## Safe Recovery

1. Check `docker compose ps`.
2. Inspect `docker compose logs --no-color`.
3. Confirm PostgreSQL is healthy.
4. Run `uv run alembic upgrade head`.
5. Recheck `/ready` and `/api/v1/system/status`.
```
### docs/phase3g-verification-report.md

```markdown
# Phase 3G Verification Report

Generated at: 2026-07-15T17:43:10Z

## Scope

Phase 3G implemented the manual Telegram `/digest` readiness digest command foundation.

- `PROJECT_PHASE = "phase_3g_telegram_digest_command_foundation"`.
- `/digest` uses the existing Phase 3F `ReadinessDigestService`.
- `/digest` defaults to EURUSD M15 and EURUSD H1 readiness windows.
- `/digest EURUSD M15` supports a single requested pair/timeframe.
- `/snapshot` remains available and covered by tests.
- Telegram output remains Russian, neutral, and readiness-only.
- No automatic Telegram digest delivery was added.
- No provider calls, OpenAI calls, broker APIs, paper trading, order execution, real trading, strategy, scoring, recommendations, or signals were added.
- No database migration was required.
- Phase 4 was not started.

## Verification Results

Host verification:

- `uv lock --check` -> passed.
- `uv sync` -> passed.
- `uv run ruff format --check .` -> `104 files already formatted`.
- `uv run ruff check .` -> `All checks passed!`.
- `uv run mypy app` -> `Success: no issues found in 74 source files`.
- `uv run pytest` -> `199 passed, 5 skipped, 1 warning`.
- `uv run python scripts/security_check.py` -> exit code 0.

Docker verification:

- `docker compose build` -> succeeded.
- `docker compose up -d postgres` -> succeeded.
- PostgreSQL container status -> healthy.
- `docker compose run --rm migrate alembic current` -> `0002_phase2_data_constraints (head)`.
- `docker compose run --rm migrate alembic check` -> `No new upgrade operations detected.`
- Test database migration to head -> succeeded.
- Docker integration tests run 1 -> `5 passed, 1 warning`.
- Docker integration tests run 2 against the same test database without cleanup -> `5 passed, 1 warning`.
- `docker compose config` -> succeeded.

## Tests Added Or Updated

- Added `/digest` default command coverage.
- Added `/digest EURUSD M15` single snapshot identity coverage.
- Added `/digest` invalid-argument rejection coverage.
- Added handler registration coverage confirming `/snapshot` remains registered and `/digest` is registered.
- Added Phase 3G safety-boundary coverage for the digest command source.
- Updated project phase assertions to `phase_3g_telegram_digest_command_foundation`.

## Remaining Risks

- Real Telegram delivery was not exercised with a live Telegram API token, by design.
- Provider integrations remain disabled by default and were not called during Phase 3G verification.
- Docker integration tests cover API/database behavior and repeatability, not a live Telegram chat.
```
