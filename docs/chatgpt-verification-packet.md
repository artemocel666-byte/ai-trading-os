# ChatGPT Verification Packet - Phase 3H
## Generation Metadata
- Generation timestamp: 2026-07-15T18:10:00Z
- Repository: `/Users/artem.otsel/Documents/ai-trading-os`
- Git branch: `main`
- Current git commit hash: `ab4aafbb2bf598cce9b3da14764e78b1ab0d3b28`
- Latest committed baseline observed locally: `ab4aafb phase 3G done`
- User prompt expected Phase 3G commit: `463d77 Add Phase 3G Telegram digest command foundation`; local clean baseline differs by hash/message but is Phase 3G.
- Phase 3H state: uncommitted at packet generation time
- Phase 4: not started
- Migration created: none
- Runtime note: host `uv` was available at `/Users/artem.otsel/.local/bin/uv`; commands were run with that directory on PATH.

## Scope Confirmation
- Implemented Phase 3H only: neutral scheduled readiness digest delivery foundation.
- Scheduled delivery remains disabled by default through `scheduled_digest_enabled=False` / `SCHEDULED_DIGEST_ENABLED=false`.
- A worker callable exists, but `register_jobs` does not register an automatic scheduled digest loop.
- Existing `/snapshot` and `/digest` commands remain active and tested.
- No strategy, signals, setup scoring, confidence scoring, AI agents, OpenAI calls, broker APIs, paper trading, order execution, or real trading were added.
- Feature/analysis/readiness/delivery flows remain descriptive and deterministic only.

## Changed Files
Created files:
- `app/domain/entities/scheduled_digest.py`
- `app/domain/interfaces/notifications.py`
- `app/services/scheduled_digest_delivery_service.py`
- `docs/phase3h-verification-report.md`
- `tests/unit/test_scheduled_digest_delivery_foundation.py`

Modified files:
- `.env.example`
- `AGENTS.md`
- `PLANS.md`
- `README.md`
- `app/core/config.py`
- `app/core/constants.py`
- `app/domain/entities/__init__.py`
- `app/scheduler/jobs.py`
- `docs/chatgpt-verification-packet.md`
- `docs/operations.md`
- `tests/contract/test_safety_boundaries.py`
- `tests/integration/test_database_and_api.py`
- `tests/unit/test_analysis_snapshot_foundation.py`
- `tests/unit/test_readiness_scheduler_foundation.py`
- `tests/unit/test_settings.py`

## Implementation Summary
- Updated `PROJECT_PHASE` to `phase_3h_scheduled_digest_delivery_foundation`.
- Added disabled-by-default scheduled digest settings.
- Added immutable Pydantic scheduled digest config, tick, decision, record, and result models.
- Added mockable `NotificationSender` and `ScheduledDigestDeliveryStore` protocols.
- Added scheduled digest delivery service with deterministic due checks, build-only-when-due behavior, duplicate skip, build-failed skip, and in-memory foundation store.
- Added a worker callable without automatic worker registration.
- Updated safety, settings, phase, and integration tests.
- Updated README, AGENTS, PLANS, operations, and Phase 3H verification docs.

## New Tests
- `tests/unit/test_scheduled_digest_delivery_foundation.py::test_scheduled_digest_disabled_skip`
- `tests/unit/test_scheduled_digest_delivery_foundation.py::test_scheduled_digest_not_due_skip`
- `tests/unit/test_scheduled_digest_delivery_foundation.py::test_scheduled_digest_due_builds_payload_and_sends_once`
- `tests/unit/test_scheduled_digest_delivery_foundation.py::test_scheduled_digest_duplicate_dedup_key_skip`
- `tests/unit/test_scheduled_digest_delivery_foundation.py::test_scheduled_digest_no_items_skip`
- `tests/unit/test_scheduled_digest_delivery_foundation.py::test_scheduled_digest_build_failed_skip`
- `tests/unit/test_scheduled_digest_delivery_foundation.py::test_scheduled_digest_tick_is_json_serializable_and_immutable`
- `tests/unit/test_scheduled_digest_delivery_foundation.py::test_scheduled_digest_tick_normalizes_utc`
- `tests/unit/test_scheduled_digest_delivery_foundation.py::test_scheduled_digest_due_policy_is_deterministic`
- `tests/unit/test_scheduled_digest_delivery_foundation.py::test_worker_callable_can_run_without_auto_registration`
- `tests/unit/test_scheduled_digest_delivery_foundation.py::test_register_jobs_does_not_start_scheduled_digest_delivery_loop`
- `tests/contract/test_safety_boundaries.py::test_phase3h_scheduled_digest_files_do_not_add_decision_or_execution_terms`

## Traceability Table
| Requirement | Implementation file | Test file | Verification result |
|---|---|---|---|
| Set Phase 3H project phase | app/core/constants.py | tests/integration/test_database_and_api.py; tests/unit/test_analysis_snapshot_foundation.py; tests/unit/test_readiness_scheduler_foundation.py | Host pytest passed; Docker integration tests passed twice |
| Disabled-by-default scheduled delivery setting | app/core/config.py; .env.example | tests/unit/test_settings.py | Host pytest passed |
| Immutable scheduled digest models with UTC normalization | app/domain/entities/scheduled_digest.py | tests/unit/test_scheduled_digest_delivery_foundation.py | Host pytest passed |
| Mockable notification sender and dedup store protocols | app/domain/interfaces/notifications.py; app/services/scheduled_digest_delivery_service.py | tests/unit/test_scheduled_digest_delivery_foundation.py | Host pytest passed |
| Due/not-due deterministic interval policy | app/services/scheduled_digest_delivery_service.py | tests/unit/test_scheduled_digest_delivery_foundation.py | Host pytest passed |
| Build payload only when enabled and due | app/services/scheduled_digest_delivery_service.py | tests/unit/test_scheduled_digest_delivery_foundation.py | Host pytest passed |
| Duplicate dedup key skip | app/services/scheduled_digest_delivery_service.py | tests/unit/test_scheduled_digest_delivery_foundation.py | Host pytest passed |
| No automatic worker loop | app/scheduler/jobs.py | tests/unit/test_scheduled_digest_delivery_foundation.py | Host pytest passed |
| Keep `/snapshot` and `/digest` working | app/telegram/commands.py | tests/unit/test_telegram_commands.py | Host pytest passed |
| No strategy/signals/AI/broker/execution additions | app/domain/entities/scheduled_digest.py; app/services/scheduled_digest_delivery_service.py; app/scheduler/jobs.py | tests/contract/test_safety_boundaries.py; scripts/security_check.py | Safety tests and security check passed |
| No migration required | none | docker compose run --rm migrate alembic check | No new upgrade operations detected |

## Git Metadata
### git status --short

```
 M .env.example
 M AGENTS.md
 M PLANS.md
 M README.md
 M app/core/config.py
 M app/core/constants.py
 M app/domain/entities/__init__.py
 M app/scheduler/jobs.py
 M docs/chatgpt-verification-packet.md
 M docs/operations.md
 M tests/contract/test_safety_boundaries.py
 M tests/integration/test_database_and_api.py
 M tests/unit/test_analysis_snapshot_foundation.py
 M tests/unit/test_readiness_scheduler_foundation.py
 M tests/unit/test_settings.py
?? app/domain/entities/scheduled_digest.py
?? app/domain/interfaces/notifications.py
?? app/services/scheduled_digest_delivery_service.py
?? docs/phase3h-verification-report.md
?? tests/unit/test_scheduled_digest_delivery_foundation.py
```
### git diff --stat

```
.env.example                                      |  2 ++
AGENTS.md                                         | 16 +++++----
PLANS.md                                          | 12 +++++--
README.md                                         | 17 ++++++++--
app/core/config.py                                |  2 ++
app/core/constants.py                             |  2 +-
app/domain/entities/__init__.py                   | 14 ++++++++
app/scheduler/jobs.py                             | 20 +++++++++++
docs/chatgpt-verification-packet.md               | regenerated for Phase 3H
docs/operations.md                                |  8 +++++
tests/contract/test_safety_boundaries.py          | 41 +++++++++++++++++++++++
tests/integration/test_database_and_api.py        |  2 +-
tests/unit/test_analysis_snapshot_foundation.py   |  4 +--
tests/unit/test_readiness_scheduler_foundation.py |  2 +-
tests/unit/test_settings.py                       |  2 ++
14 tracked files changed before packet regeneration; new untracked files are listed in git status.
```
### git log --oneline -8

```
ab4aafb phase 3G done
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
Resolved 46 packages in 2ms
Checked 43 packages in 0.89ms
```
### uv run ruff format --check .

```
108 files already formatted
```
### uv run ruff check .

```
All checks passed!
```
### uv run mypy app

```
Success: no issues found in 77 source files
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
collected 216 items

tests/contract/test_agent_contracts.py ......                            [  2%]
tests/contract/test_api_error_schema.py .                                [  3%]
tests/contract/test_architecture_boundaries.py ..                        [  4%]
tests/contract/test_provider_contracts.py .............................. [ 18%]
...............................                                          [ 32%]
tests/contract/test_safety_boundaries.py ...............                 [ 39%]
tests/integration/test_database_and_api.py sssss                         [ 41%]
tests/unit/test_analysis_snapshot_foundation.py ..........               [ 46%]
tests/unit/test_context_engine_foundation.py .............               [ 52%]
tests/unit/test_data_quality_foundation.py ...                           [ 53%]
tests/unit/test_domain_market_models.py ..................               [ 62%]
tests/unit/test_errors_and_redaction.py .......                          [ 65%]
tests/unit/test_feature_engine_foundation.py ...........                 [ 70%]
tests/unit/test_internal_api_key.py ....                                 [ 72%]
tests/unit/test_readiness_scheduler_foundation.py .........              [ 76%]
tests/unit/test_scheduled_digest_delivery_foundation.py ...........      [ 81%]
tests/unit/test_settings.py .........                                    [ 85%]
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
================== 211 passed, 5 skipped, 1 warning in 0.83s ===================
```
### uv run python scripts/security_check.py

```
Exit code: 0
Output: <no output>
```
### docker compose build

```
Image ai-trading-os-api Building 
 Image ai-trading-os-worker Building 
 Image ai-trading-os-bot Building 
 Image ai-trading-os-migrate Building 
#1 [internal] load local bake definitions
#1 reading from stdin 1.91kB done
#1 DONE 0.0s

#2 [api internal] load build definition from Dockerfile
#2 transferring dockerfile: 411B done
#2 DONE 0.0s

#3 [worker internal] load metadata for ghcr.io/astral-sh/uv:python3.12-bookworm-slim
#3 DONE 1.1s

#4 [api internal] load .dockerignore
#4 transferring context: 143B done
#4 DONE 0.0s

#5 [bot 1/5] FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58
#5 resolve ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:e5b65587bce7de595f299855d7385fe7fca39b8a74baa261ba1b7147afa78e58 0.0s done
#5 DONE 0.0s

#6 [worker internal] load build context
#6 transferring context: 446.40kB 0.0s done
#6 DONE 0.0s

#7 [migrate 2/5] WORKDIR /app
#7 CACHED

#8 [migrate 3/5] COPY pyproject.toml uv.lock* ./
#8 CACHED

#9 [migrate 4/5] RUN uv sync --frozen --no-dev
#9 CACHED

#10 [worker 5/5] COPY . .
#10 DONE 0.1s

#11 [bot] exporting to image
#11 exporting layers
#11 exporting layers 0.0s done
#11 exporting manifest sha256:873b59e21a784cd9cac3fa064dac626786711c5b954828a565ef96f605eae3c1 done
#11 exporting config sha256:dcc8aba89b33ab6d6d3c3de7197afa6b0792c83680a360482fb4dccc2021a1bd 0.0s done
#11 exporting attestation manifest sha256:e900b639e5b4919e5d22a15810a15b754610d3ed7c6dc157bbd8e22d749da5c7 0.0s done
#11 exporting manifest list sha256:fd3d32bb7d3f2ecf4a913c8f94123cb3a66776197d85b39cf6824dc63da71942
#11 exporting manifest list sha256:fd3d32bb7d3f2ecf4a913c8f94123cb3a66776197d85b39cf6824dc63da71942 done
#11 naming to docker.io/library/ai-trading-os-bot:latest done
#11 unpacking to docker.io/library/ai-trading-os-bot:latest 0.0s done
#11 DONE 0.2s

#12 [worker] exporting to image
#12 exporting layers 0.0s done
#12 exporting manifest sha256:a67574b20bdf73940d5a2cfcab2de3a59f500f305dea983d5123c1ac00734ed4 done
#12 exporting config sha256:48e284755a59dc6c2dffe8c26bc0992d9990cc93df9be805181c5a61c74b6e6f 0.0s done
#12 exporting attestation manifest sha256:2f6159457022213953c44f2fdc35b79f01595ec1a225031dc3b250924557a218 0.0s done
#12 exporting manifest list sha256:3b067319363d9ee7d71198f5fc61d3cbe241ca4dd4d57972acd532c779654845 done
#12 naming to docker.io/library/ai-trading-os-worker:latest done
#12 unpacking to docker.io/library/ai-trading-os-worker:latest 0.0s done
#12 DONE 0.2s

#13 [api] exporting to image
#13 exporting layers 0.0s done
#13 exporting manifest sha256:19dd8ce1838f252def88e4eb7d77ba1a9ee8bcad32c3ca7c3402ed6b4d2a1254 0.0s done
#13 exporting config sha256:95bc4aab192e2ead3ae9d7edc7a29f32c115558641e58ed9073934f9b0764f9c done
#13 exporting attestation manifest sha256:640d9d6d386b94d329ef7e5d6896f51eb2d15fffdc30d87236e023ba92304c6d 0.0s done
#13 exporting manifest list sha256:cb4726db4d1aa1b5fa82d7a80ae0e42529142c5a479911e963de94f48e9934e0 done
#13 naming to docker.io/library/ai-trading-os-api:latest done
#13 unpacking to docker.io/library/ai-trading-os-api:latest 0.0s done
#13 DONE 0.2s

#14 [migrate] exporting to image
#14 exporting layers 0.0s done
#14 exporting manifest sha256:b6394bb7164077b903b4dfcae1c02f422483832b0a42c53c681c5c6aade3fd98 done
#14 exporting config sha256:2892f262a9c1a49c2c03b73ade90d87a81c09c851a5bd0ad9ac274dea787085a done
#14 exporting attestation manifest sha256:52cbfdf48b88c53991bb1e112c718b373f705e3a58ac34c29ce9cbb1ed58f5e5 0.0s done
#14 exporting manifest list sha256:86a31a7c5142c3d04081aa9c06a757df7fa978f3116e9d7d00ae89b8b63f7952 done
#14 naming to docker.io/library/ai-trading-os-migrate:latest done
#14 unpacking to docker.io/library/ai-trading-os-migrate:latest 0.0s done
#14 DONE 0.2s

#15 [bot] resolving provenance for metadata file
#15 DONE 0.0s

#16 [api] resolving provenance for metadata file
#16 DONE 0.0s

#17 [worker] resolving provenance for metadata file
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
Network ai-trading-os_default Creating 
Network ai-trading-os_default Created 
Container ai-trading-os-postgres-1 Creating 
Container ai-trading-os-postgres-1 Created 
Container ai-trading-os-postgres-1 Starting 
Container ai-trading-os-postgres-1 Started
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
Container ai-trading-os-migrate-run-c3c71a3af6d0 Creating 
Container ai-trading-os-migrate-run-c3c71a3af6d0 Created 
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
0002_phase2_data_constraints (head)
```
### docker compose run --rm migrate alembic check

```
Container ai-trading-os-postgres-1 Running 
Container ai-trading-os-postgres-1 Waiting 
Container ai-trading-os-postgres-1 Healthy 
Container ai-trading-os-migrate-run-9b86b06663c9 Creating 
Container ai-trading-os-migrate-run-9b86b06663c9 Created 
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
### test database migration

```
docker compose run --rm -e DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate alembic upgrade head

Container ai-trading-os-postgres-1 Running 
Container ai-trading-os-postgres-1 Waiting 
Container ai-trading-os-postgres-1 Healthy 
Container ai-trading-os-migrate-run-af8c55ea470b Creating 
Container ai-trading-os-migrate-run-af8c55ea470b Created 
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```
### docker integration run 1

```
docker compose run --rm -e REQUIRE_INTEGRATION_TESTS=true -e TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate uv run pytest tests/integration/test_database_and_api.py

Container ai-trading-os-postgres-1 Running 
Container ai-trading-os-postgres-1 Waiting 
Container ai-trading-os-postgres-1 Healthy 
Container ai-trading-os-migrate-run-795958161608 Creating 
Container ai-trading-os-migrate-run-795958161608 Created 
Downloading pygments (1.2MiB)
Downloading mypy (13.1MiB)
Downloading ruff (10.5MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 81ms
Bytecode compiled 1963 files in 538ms
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

Container ai-trading-os-postgres-1 Running 
Container ai-trading-os-postgres-1 Waiting 
Container ai-trading-os-postgres-1 Healthy 
Container ai-trading-os-migrate-run-e6ebffd9eeb4 Creating 
Container ai-trading-os-migrate-run-e6ebffd9eeb4 Created 
Downloading pygments (1.2MiB)
Downloading mypy (13.1MiB)
Downloading ruff (10.5MiB)
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
Installed 11 packages in 49ms
Bytecode compiled 1963 files in 406ms
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
- The PostgreSQL integration tests were run separately in Docker with `REQUIRE_INTEGRATION_TESTS=true`; both repeated Docker runs passed.

## Unavailable Checks
- None for the requested Phase 3H verification set. Docker, PostgreSQL, Alembic, host uv, and Docker integration checks were available and ran successfully.

## Remaining Risks
- Live Telegram API behavior was not tested with a real bot token; Phase 3H tests use fakes and protocols.
- Scheduled digest deduplication persistence is in-memory foundation behavior in Phase 3H; no durable delivery table was added.
- Provider integrations remain disabled and were not called during Phase 3H verification.
- `docker compose config` output includes existing future-phase environment placeholders; Phase 3H did not activate them.

## Migration Contents
No migration was added for Phase 3H. Current Alembic head remains `0002_phase2_data_constraints (head)`, and `alembic check` reported `No new upgrade operations detected.`

## Full Contents Of Changed Source Files
### .env.example

```dotenv
APP_NAME=AI Trading OS
APP_ENV=development
APP_TIMEZONE=Europe/Stockholm
STORAGE_TIMEZONE=UTC
LOG_LEVEL=INFO

DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os
TEST_DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@localhost:5432/ai_trading_os_test
INTERNAL_API_KEY=development-internal-key-change-me

TELEGRAM_ENABLED=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_ALLOWED_USER_ID=
TELEGRAM_ALLOWED_CHAT_ID=

OPENAI_ENABLED=false
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1

MARKET_DATA_ENABLED=false
TWELVE_DATA_API_KEY=
TWELVE_DATA_BASE_URL=https://api.twelvedata.com

CALENDAR_ENABLED=false
FMP_API_KEY=
FMP_BASE_URL=https://financialmodelingprep.com

PROVIDER_CONNECT_TIMEOUT_SECONDS=5
PROVIDER_READ_TIMEOUT_SECONDS=10
PROVIDER_WRITE_TIMEOUT_SECONDS=5
PROVIDER_POOL_TIMEOUT_SECONDS=5
PROVIDER_RETRY_COUNT=2
PROVIDER_RETRY_BACKOFF_SECONDS=0.1
PROVIDER_MAX_REQUEST_RANGE_DAYS=31
REQUIRE_INTEGRATION_TESTS=false

SCAN_ENABLED=false
SCHEDULED_DIGEST_ENABLED=false
SCHEDULED_DIGEST_INTERVAL_MINUTES=60
SETUP_SCORE_THRESHOLD=85

PAPER_ACCOUNT_CURRENCY=EUR
PAPER_ACCOUNT_BALANCE=10000
PAPER_RISK_PERCENT=0.5
MAX_OPEN_RISK_PERCENT=1.0
MAX_DAILY_LOSS_PERCENT=1.5
MAX_WEEKLY_LOSS_PERCENT=4.0
MAX_CONSECUTIVE_LOSSES=3

SIGNAL_VALID_MINUTES=30
```
### app/core/config.py

```python
from decimal import Decimal
from functools import lru_cache
from typing import Any

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DEVELOPMENT_INTERNAL_API_KEY = "development-internal-key-change-me"


class Settings(BaseSettings):
    app_name: str = "AI Trading OS"
    app_env: str = "development"
    app_timezone: str = "Europe/Stockholm"
    storage_timezone: str = "UTC"
    log_level: str = "INFO"

    database_url: SecretStr = SecretStr(
        "postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os"
    )
    test_database_url: SecretStr | None = SecretStr(
        "postgresql+asyncpg://ai_trading_os:ai_trading_os@localhost:5432/ai_trading_os_test"
    )
    internal_api_key: SecretStr = SecretStr(DEFAULT_DEVELOPMENT_INTERNAL_API_KEY)

    telegram_enabled: bool = False
    telegram_bot_token: SecretStr | None = None
    telegram_allowed_user_id: int | None = None
    telegram_allowed_chat_id: int | None = None

    openai_enabled: bool = False
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4.1"

    market_data_enabled: bool = False
    twelve_data_api_key: SecretStr | None = None
    twelve_data_base_url: str = "https://api.twelvedata.com"

    calendar_enabled: bool = False
    fmp_api_key: SecretStr | None = None
    fmp_base_url: str = "https://financialmodelingprep.com"

    provider_connect_timeout_seconds: float = Field(default=5.0, gt=0, le=30)
    provider_read_timeout_seconds: float = Field(default=10.0, gt=0, le=60)
    provider_write_timeout_seconds: float = Field(default=5.0, gt=0, le=30)
    provider_pool_timeout_seconds: float = Field(default=5.0, gt=0, le=30)
    provider_retry_count: int = Field(default=2, ge=0, le=5)
    provider_retry_backoff_seconds: float = Field(default=0.1, ge=0, le=5)
    provider_max_request_range_days: int = Field(default=31, ge=1, le=370)
    require_integration_tests: bool = False

    scan_enabled: bool = False
    scheduled_digest_enabled: bool = False
    scheduled_digest_interval_minutes: int = Field(default=60, ge=1, le=1440)
    setup_score_threshold: int = Field(default=85, ge=0, le=100)

    paper_account_currency: str = "EUR"
    paper_account_balance: Decimal = Field(default=Decimal("10000"), gt=Decimal("0"))
    paper_risk_percent: Decimal = Field(default=Decimal("0.5"), ge=Decimal("0"))
    max_open_risk_percent: Decimal = Field(default=Decimal("1.0"), ge=Decimal("0"))
    max_daily_loss_percent: Decimal = Field(default=Decimal("1.5"), ge=Decimal("0"))
    max_weekly_loss_percent: Decimal = Field(default=Decimal("4.0"), ge=Decimal("0"))
    max_consecutive_losses: int = Field(default=3, ge=0)

    signal_valid_minutes: int = Field(default=30, ge=1)

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator(
        "telegram_bot_token",
        "telegram_allowed_user_id",
        "telegram_allowed_chat_id",
        "openai_api_key",
        "twelve_data_api_key",
        "fmp_api_key",
        "test_database_url",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, value: Any) -> Any:
        if value == "":
            return None
        return value

    @field_validator("paper_account_currency")
    @classmethod
    def currency_code_must_be_uppercase(cls, value: str) -> str:
        if len(value) != 3 or not value.isalpha() or value.upper() != value:
            raise ValueError("paper account currency must be a three-letter uppercase code")
        return value

    @model_validator(mode="after")
    def validate_conditional_settings(self) -> "Settings":
        errors: list[str] = []
        if not self.internal_api_key.get_secret_value().strip():
            errors.append("INTERNAL_API_KEY is required")
        if self.storage_timezone != "UTC":
            errors.append("STORAGE_TIMEZONE must be UTC")
        if (
            self.app_env != "development"
            and self.internal_api_key.get_secret_value() == DEFAULT_DEVELOPMENT_INTERNAL_API_KEY
        ):
            errors.append("Default development INTERNAL_API_KEY is rejected outside development")
        if self.telegram_enabled:
            if not self.telegram_bot_token:
                errors.append("TELEGRAM_BOT_TOKEN is required when TELEGRAM_ENABLED=true")
            if self.telegram_allowed_user_id is None:
                errors.append("TELEGRAM_ALLOWED_USER_ID is required when TELEGRAM_ENABLED=true")
            if self.telegram_allowed_chat_id is None:
                errors.append("TELEGRAM_ALLOWED_CHAT_ID is required when TELEGRAM_ENABLED=true")
        if self.openai_enabled and not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required when OPENAI_ENABLED=true")
        if self.market_data_enabled and not self.twelve_data_api_key:
            errors.append("TWELVE_DATA_API_KEY is required when MARKET_DATA_ENABLED=true")
        if self.calendar_enabled and not self.fmp_api_key:
            errors.append("FMP_API_KEY is required when CALENDAR_ENABLED=true")
        if errors:
            raise ValueError("; ".join(errors))
        return self

    def database_dsn(self) -> str:
        return self.database_url.get_secret_value()

    def test_database_dsn(self) -> str | None:
        return self.test_database_url.get_secret_value() if self.test_database_url else None

    def enabled_integrations(self) -> dict[str, bool]:
        return {
            "telegram": self.telegram_enabled,
            "openai": self.openai_enabled,
            "market_data": self.market_data_enabled,
            "calendar": self.calendar_enabled,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
```
### app/core/constants.py

```python
PROJECT_PHASE = "phase_3h_scheduled_digest_delivery_foundation"
STRATEGY_IMPLEMENTED = False
REAL_TRADING_ENABLED = False

SYSTEM_STATE_SCAN_ENABLED = "scan_enabled"
SYSTEM_STATE_WORKER_HEARTBEAT = "worker_heartbeat"
SYSTEM_STATE_LAST_SUCCESSFUL_MARKET_FETCH = "last_successful_market_fetch"
SYSTEM_STATE_LAST_SUCCESSFUL_CALENDAR_FETCH = "last_successful_calendar_fetch"
SYSTEM_STATE_LAST_ERROR = "last_error"

DEFAULT_STRATEGY_VERSION = "foundation-v1"
```
### app/domain/entities/__init__.py

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
### app/domain/entities/scheduled_digest.py

```python
from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core import constants
from app.core.time import normalize_to_utc
from app.domain.entities.readiness import (
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
### app/domain/interfaces/notifications.py

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
```
### app/scheduler/jobs.py

```python
import logging
from datetime import datetime
from typing import Any

from app.core.time import utc_now
from app.domain.entities import ScheduledDigestDeliveryResult
from app.observability.health_checks import run_application_health_check
from app.services.health_service import HealthService
from app.services.scheduled_digest_delivery_service import ScheduledDigestDeliveryService
from app.services.system_state_service import SystemStateService

logger = logging.getLogger(__name__)


async def update_worker_heartbeat_job(service: SystemStateService) -> None:
    await service.update_worker_heartbeat()
    logger.info("worker_heartbeat_updated")


async def application_health_check_job(health_service: HealthService) -> None:
    result = await run_application_health_check(health_service)
    logger.info("worker_health_check_completed", extra={"database_status": result["database"]})


async def scheduled_digest_delivery_job(
    service: ScheduledDigestDeliveryService,
    *,
    as_of: datetime | None = None,
) -> ScheduledDigestDeliveryResult:
    result = await service.run_tick(as_of=as_of or utc_now())
    logger.info(
        "scheduled_digest_delivery_checked",
        extra={
            "delivered": result.delivered,
            "reason": result.decision.reason.value,
        },
    )
    return result


def register_jobs(
    scheduler: Any,
    *,
    system_state_service: SystemStateService,
    health_service: HealthService,
) -> None:
    scheduler.add_job(
        update_worker_heartbeat_job,
        "interval",
        seconds=30,
        args=[system_state_service],
        id="worker_heartbeat",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.add_job(
        application_health_check_job,
        "interval",
        seconds=60,
        args=[health_service],
        id="application_health_check",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
```
### app/services/scheduled_digest_delivery_service.py

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
```

## Full Contents Of New Tests
### tests/unit/test_scheduled_digest_delivery_foundation.py

```python
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, cast

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.entities import Candle, Timeframe
from app.domain.entities.readiness import SnapshotNotificationPayload, SnapshotScheduleItem
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
    assert status.json()["project_phase"] == "phase_3h_scheduled_digest_delivery_foundation"
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

    assert data["metadata"]["project_phase"] == "phase_3h_scheduled_digest_delivery_foundation"
    assert "phase_3h_scheduled_digest_delivery_foundation" in text
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
    assert "phase_3h_scheduled_digest_delivery_foundation" in digest.model_dump_json()
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
### tests/unit/test_settings.py

```python
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_default_settings_keep_external_integrations_disabled() -> None:
    settings = Settings(_env_file=None)

    assert settings.telegram_enabled is False
    assert settings.openai_enabled is False
    assert settings.market_data_enabled is False
    assert settings.calendar_enabled is False
    assert settings.scan_enabled is False
    assert settings.scheduled_digest_enabled is False
    assert settings.scheduled_digest_interval_minutes == 60
    assert settings.paper_account_balance == Decimal("10000")


@pytest.mark.parametrize(
    ("field", "enabled_kwargs"),
    [
        ("TELEGRAM_BOT_TOKEN", {"telegram_enabled": True}),
        ("OPENAI_API_KEY", {"openai_enabled": True}),
        ("TWELVE_DATA_API_KEY", {"market_data_enabled": True}),
        ("FMP_API_KEY", {"calendar_enabled": True}),
    ],
)
def test_conditional_secret_requirements(field: str, enabled_kwargs: dict[str, bool]) -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None, **enabled_kwargs)

    assert field in str(exc_info.value)


def test_telegram_enabled_requires_allowed_identity() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None, telegram_enabled=True, telegram_bot_token="token")

    assert "TELEGRAM_ALLOWED_USER_ID" in str(exc_info.value)
    assert "TELEGRAM_ALLOWED_CHAT_ID" in str(exc_info.value)


def test_enabled_integrations_are_safe_booleans() -> None:
    settings = Settings(_env_file=None, telegram_enabled=False, openai_enabled=False)

    assert settings.enabled_integrations() == {
        "telegram": False,
        "openai": False,
        "market_data": False,
        "calendar": False,
    }


def test_storage_timezone_must_be_utc() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, storage_timezone="Europe/Stockholm")


def test_require_integration_tests_defaults_to_false() -> None:
    assert Settings(_env_file=None).require_integration_tests is False
```

## Updated Documentation Files
### README.md

```markdown
# AI Trading OS

AI Trading OS is a safety-first foundation for a future modular Forex analysis and paper-trading platform. The current repository implements only infrastructure: API health/status endpoints, async PostgreSQL persistence, a scheduler heartbeat, Telegram command foundations, strict configuration, and safety contracts.

## Current Status

- Current project phase: phase_3h_scheduled_digest_delivery_foundation.
- Trading strategy: not implemented.
- Real trading: disabled and unsupported.
- External integrations: disabled by default.
- Telegram: can run in disabled mode without a token.
- Phase 3D: deterministic analysis snapshot/readiness report foundation only.
- Phase 3E: local Telegram readiness reports only.
- Phase 3F: neutral readiness scheduler/snapshot digest foundation only.
- Phase 3G: manual Telegram `/digest` readiness digest command only.
- Phase 3H: neutral scheduled digest delivery foundation only, disabled by default.

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
AI output, broker activity, paper trading, order execution, or real trading.

## Phase 3H Status

Phase 3H adds a neutral scheduled digest delivery foundation. It can decide whether a readiness
digest is due on a tick, build the existing readiness digest payload, pass it to a mockable
notification sender, and skip duplicate deduplication keys. Scheduled delivery is disabled by
default and no automatic delivery loop is registered in the worker. It does not add provider calls,
AI output, strategy decisions, setup scoring, confidence scoring, trade directions, recommendations,
signals, broker activity, paper trading, order execution, or real trading. Phase 4 has not started.

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
SCHEDULED_DIGEST_ENABLED=false
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
- Scheduled digest delivery is disabled by default and has no automatic worker loop.
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

Current project phase: phase_3h_scheduled_digest_delivery_foundation.
Phase 3H is limited to neutral scheduled readiness digest delivery orchestration over existing
Phase 3F/3G readiness digest payloads. External integrations are disabled by default. The project
contains no strategy, no signals, no broker order APIs, no paper trading, and no real trading.
Phase 4 has not started.

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
- While working in Phase 3H, output is limited to neutral readiness reports and readiness digests.
  Scheduled delivery must remain disabled by default. Do not add Telegram trading signals, entry
  guidance, LONG/SHORT advice, buy/sell recommendations, automatic runtime loops, or paper-trading
  actions.
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
- Phase 3H scheduled digest delivery foundation: disabled-by-default scheduled readiness digest
  due checks, mockable notification sending, deduplication records, and safety tests confirming no
  strategy/signals/trading activation.

## Current Implementation Status

The repository has completed the foundation phase, Phase 2 hardening/data adapters, Phase 3A
data-quality foundation, Phase 3B deterministic feature-engine foundation, Phase 3C deterministic
indicator/context foundation, Phase 3D deterministic analysis snapshot/readiness report foundation,
Phase 3E local Telegram readiness-report foundation, and Phase 3F deterministic readiness
scheduler/snapshot digest foundation, and Phase 3G manual Telegram digest command foundation.
scheduler/snapshot digest foundation, Phase 3G manual Telegram digest command foundation, and Phase
3H neutral scheduled digest delivery foundation. Production Twelve Data and FMP adapters exist, but
live integrations remain disabled by default. Scanning state can be enabled or disabled, Telegram can
request readiness reports and readiness digests, and scheduled digest orchestration remains disabled
by default. No strategy, signal generation, AI agent, paper-trading, or execution flow is connected.

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
- Phase 3H: neutral scheduled digest delivery foundation — completed without trading decisions
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

Phase 3H adds a neutral scheduled digest delivery foundation. It can decide whether a digest is due,
build the same readiness payload, pass it to a mockable notification sender, and skip duplicate
deduplication keys. It is disabled by default with `SCHEDULED_DIGEST_ENABLED=false`, and the worker
does not register an automatic scheduled digest job. It does not call providers, AI services, or
brokers, and it does not produce trading guidance.

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
SCHEDULED_DIGEST_ENABLED=false
SCHEDULED_DIGEST_INTERVAL_MINUTES=60
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
### docs/phase3h-verification-report.md

```markdown
# Phase 3H Verification Report

Generated at: 2026-07-15T18:10:00Z

## Scope

Phase 3H implemented the neutral scheduled digest delivery foundation.

- `PROJECT_PHASE = "phase_3h_scheduled_digest_delivery_foundation"`.
- Scheduled digest delivery is disabled by default.
- The service decides whether a readiness digest is due on a tick.
- The service builds existing Phase 3F/3G readiness digest payloads only when enabled and due.
- Delivery uses a mockable notification sender protocol.
- Duplicate deterministic deduplication keys are skipped.
- A worker callable exists, but no automatic scheduled digest worker loop is registered.
- Existing `/snapshot` and `/digest` commands remain unchanged and covered by tests.
- No migration was required.
- Phase 4 was not started.
- No strategy, signals, setup scoring, confidence scoring, AI agents, OpenAI calls, broker APIs, paper trading, order execution, or real trading were added.

## Verification Results

Host verification:

- `uv lock --check` -> passed.
- `uv sync` -> passed.
- `uv run ruff format --check .` -> `108 files already formatted`.
- `uv run ruff check .` -> `All checks passed!`.
- `uv run mypy app` -> `Success: no issues found in 77 source files`.
- `uv run pytest` -> `211 passed, 5 skipped, 1 warning`.
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

- Added scheduled digest disabled skip coverage.
- Added not-due skip coverage.
- Added due payload build and fake sender delivery coverage.
- Added duplicate deduplication key skip coverage.
- Added no-items and build-failed skip coverage.
- Added delivery result JSON serialization and immutability coverage.
- Added UTC normalization coverage.
- Added worker callable coverage without automatic registration.
- Added Phase 3H safety-boundary coverage.
- Updated project phase assertions to `phase_3h_scheduled_digest_delivery_foundation`.

## Remaining Risks

- Live Telegram API behavior was not tested and no real Telegram network calls were made.
- Provider integrations remain disabled by default and were not called during Phase 3H verification.
- Scheduled delivery persistence uses an in-memory foundation store in this phase; no database migration was added.
```
