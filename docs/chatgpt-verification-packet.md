# ChatGPT Verification Packet: Phase 4B Strategy Rule Specification Foundation

Generated: 2026-07-18T12:46:45Z

## Repository Metadata

- Repository path: `/Users/artem.otsel/Documents/ai-trading-os`
- Git branch: `main`
- Current commit hash: `a4c8f273f407a14765c401fe7dfe4162947770ea`
- Latest commit at start of Phase 4B work: `a4c8f27  Phase 4A`
- Commit status: Phase 4B remains uncommitted at packet generation time.

## Preflight

Preflight passed before edits:

```text
git status --short
<clean>

git log --oneline -5
a4c8f27  Phase 4A
bad58a4 Add Phase 3I persistent digest audit foundation
901d864 Phase 3H Done
ab4aafb phase 3G done
40473bd Add Phase 3F readiness scheduler foundation

grep -n "PROJECT_PHASE" app/core/constants.py
1:PROJECT_PHASE = "phase_4a_signal_contract_foundation"

test -f app/domain/entities/signal_contract.py && echo "Phase 4A signal_contract exists"
Phase 4A signal_contract exists

test ! -f app/api/routes/digest_deliveries.py && echo "Phase 3J API route absent"
Phase 3J API route absent
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
 M tests/unit/test_signal_contract_foundation.py
?? app/domain/entities/strategy_rules.py
?? docs/phase4b-verification-report.md
?? tests/unit/test_strategy_rule_specification_foundation.py
```

## Git Diff Stat

```text
 AGENTS.md                                     |   26 +-
 PLANS.md                                      |   24 +-
 README.md                                     |   15 +-
 app/core/constants.py                         |    2 +-
 app/domain/entities/__init__.py               |   16 +
 docs/chatgpt-verification-packet.md           | 2384 +++++++++++--------------
 docs/operations.md                            |    5 +
 tests/contract/test_safety_boundaries.py      |  107 +-
 tests/unit/test_signal_contract_foundation.py |    4 +-
 9 files changed, 1253 insertions(+), 1330 deletions(-)
```

## Git Log

```text
a4c8f27  Phase 4A
bad58a4 Add Phase 3I persistent digest audit foundation
901d864 Phase 3H Done
ab4aafb phase 3G done
40473bd Add Phase 3F readiness scheduler foundation
588ab6a Phase 3E DONE
8166820 phase 3C DONE
60e6e53 Add Phase 3C indicator context foundation
a6f44f0 Add Phase 3B feature engine foundation
03c3acd Add Phase 3A data quality foundation
```

## Created Files

- `app/domain/entities/strategy_rules.py`
- `docs/phase4b-verification-report.md`
- `tests/unit/test_strategy_rule_specification_foundation.py`

## Modified Files

- `AGENTS.md`
- `PLANS.md`
- `README.md`
- `app/core/constants.py`
- `app/domain/entities/__init__.py`
- `docs/chatgpt-verification-packet.md`
- `docs/operations.md`
- `tests/contract/test_safety_boundaries.py`
- `tests/unit/test_signal_contract_foundation.py`

## Migration Files Created Or Modified

- None

Phase 4B did not require a migration. Alembic head remains `0003_phase3i_digest_audit (head)`.

## Phase Scope Confirmation

Phase 4B is strategy rule specification foundation only. It defines typed contracts, enums, value objects, validation rules, deterministic serialization, deterministic fingerprinting, tests, and documentation for future strategy rule specifications.

Phase 4B does not implement rule evaluation, strategy execution logic, market-data rule evaluation, signal generation, setup scoring, confidence scoring, automated LONG/SHORT decisions, buy/sell recommendations, entry calculation logic, stop loss calculation logic, take profit calculation logic, position sizing logic, portfolio/risk decisions, AI agents, OpenAI calls, LLM usage, Telegram signal sending, API signal routes, scheduler signal jobs, broker APIs, order execution, paper trading, real trading, backtesting, or a trading simulator.

Rule specs and rule sets default to disabled and non-actionable.

Phase 3J digest audit API route is absent: `True`.

## Implementation Summary

- Updated `PROJECT_PHASE` to `phase_4b_strategy_rule_specification_foundation`.
- Added immutable `StrategyRuleValue`, `StrategyRuleCondition`, `StrategyRuleSpec`, and `StrategyRuleSet` domain models.
- Added `StrategyRuleOperator`, `StrategyRuleCategory`, and `StrategyRuleSeverity` enums.
- Added validation for UTC timestamps, deterministic identifiers, duplicate `rule_id` values, disabled defaults, `BETWEEN`, `IN`, `EXISTS`/`NOT_EXISTS`, comparison operators, Decimal-compatible values, and finite Decimal values.
- Added typed JSON serialization for rule values so Decimal values round-trip without binary floating point or string ambiguity.
- Added deterministic JSON serialization and SHA-256 fingerprinting for rule specs and rule sets.
- Normalized warnings into sorted unique tuples and normalized rule ordering by `rule_id`.
- Added safety tests proving no API routes, Telegram handlers, scheduler jobs, strategy evaluation service, rule evaluation behavior, signal generation, scoring, or execution behavior was added.
- Updated README, AGENTS, PLANS, operations docs, Phase 4B report, and this packet.

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

## Exact Verification Command Outputs

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

## Skipped Checks

- Host `uv run pytest` skipped 7 integration tests because host integration tests require `REQUIRE_INTEGRATION_TESTS=true` and a PostgreSQL integration database. The same integration file was run in Docker twice with `REQUIRE_INTEGRATION_TESTS=true`, and both Docker runs passed.

## Unavailable Checks

- None for the requested Phase 4B verification set. Docker Desktop, PostgreSQL container, Alembic, Docker integration tests, and `docker compose config` were available and run.

## Remaining Risks

- Phase 4B intentionally defines rule specifications only; future phases must add separate tests before any rule evaluation, decision engine, signal generation, delivery, broker, paper-trading, or live-trading behavior can exist.
- Rule specifications are not persisted in this phase; no database migration was added.
- Existing Starlette/httpx deprecation warning remains in test output and is unrelated to Phase 4B behavior.

## Traceability

| Requirement | Implementation File | Test File | Verification Result |
| --- | --- | --- | --- |
| Update project phase to Phase 4B | `app/core/constants.py` | `tests/unit/test_strategy_rule_specification_foundation.py` | Host and Docker tests passed |
| Define strategy rule operators/categories/severity | `app/domain/entities/strategy_rules.py` | `tests/unit/test_strategy_rule_specification_foundation.py` | Unit tests passed |
| Validate rule values and reject floats | `app/domain/entities/strategy_rules.py` | `tests/unit/test_strategy_rule_specification_foundation.py` | Float and invalid value tests passed |
| Preserve Decimal values through deterministic JSON | `app/domain/entities/strategy_rules.py` | `tests/unit/test_strategy_rule_specification_foundation.py` | Decimal JSON round-trip test passed |
| Validate `BETWEEN`, `IN`, `EXISTS`/`NOT_EXISTS`, and comparison operators | `app/domain/entities/strategy_rules.py` | `tests/unit/test_strategy_rule_specification_foundation.py` | Operator validation tests passed |
| Normalize warnings and rules deterministically | `app/domain/entities/strategy_rules.py` | `tests/unit/test_strategy_rule_specification_foundation.py` | Determinism tests passed |
| Deterministic fingerprinting | `app/domain/entities/strategy_rules.py` | `tests/unit/test_strategy_rule_specification_foundation.py` | Fingerprint tests passed |
| Default rule specs and rule sets to disabled/non-actionable | `app/domain/entities/strategy_rules.py` | `tests/unit/test_strategy_rule_specification_foundation.py` | Default enabled and `is_actionable` tests passed |
| Do not add scoring/confidence/action fields | `app/domain/entities/strategy_rules.py` | `tests/unit/test_strategy_rule_specification_foundation.py` | Field-name safety test passed |
| Do not add API routes, Telegram handlers, scheduler jobs, or strategy evaluation service | No runtime files added | `tests/contract/test_safety_boundaries.py` | Safety boundary tests passed |
| Do not add broker/order/paper/live trading behavior | No execution code added | `tests/contract/test_safety_boundaries.py`, `scripts/security_check.py` | Safety tests and security check passed |
| Keep Phase 3J absent | No `app/api/routes/digest_deliveries.py` | `tests/contract/test_safety_boundaries.py` | Phase 3J absence test passed |
| No migration required | No migration file created or modified | `docker compose run --rm migrate alembic current`, `docker compose run --rm migrate alembic check` | Alembic head remained `0003_phase3i_digest_audit (head)` and check passed |

## Full Contents Of Changed Source Files

### `app/core/constants.py`

```python
PROJECT_PHASE = "phase_4b_strategy_rule_specification_foundation"
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
from app.domain.entities.strategy_rules import (
    StrategyRuleCategory,
    StrategyRuleCondition,
    StrategyRuleOperator,
    StrategyRuleSet,
    StrategyRuleSeverity,
    StrategyRuleSpec,
    StrategyRuleValue,
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
    "StrategyRuleCategory",
    "StrategyRuleCondition",
    "StrategyRuleOperator",
    "StrategyRuleSet",
    "StrategyRuleSeverity",
    "StrategyRuleSpec",
    "StrategyRuleValue",
    "TimeContextSummary",
    "Timeframe",
    "UpsertResult",
    "build_feature_snapshot",
    "digest_status_from_analysis",
]
```

### `app/domain/entities/strategy_rules.py`

```python
import hashlib
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

from app.core.time import normalize_to_utc


class StrategyRuleOperator(StrEnum):
    EXISTS = "EXISTS"
    NOT_EXISTS = "NOT_EXISTS"
    EQ = "EQ"
    NE = "NE"
    GT = "GT"
    GTE = "GTE"
    LT = "LT"
    LTE = "LTE"
    BETWEEN = "BETWEEN"
    IN = "IN"


class StrategyRuleCategory(StrEnum):
    DATA_QUALITY = "DATA_QUALITY"
    MARKET_CONTEXT = "MARKET_CONTEXT"
    EVENT_CONTEXT = "EVENT_CONTEXT"
    RISK_GUARD = "RISK_GUARD"
    TIME_FILTER = "TIME_FILTER"
    SIGNAL_CONTRACT_GUARD = "SIGNAL_CONTRACT_GUARD"


class StrategyRuleSeverity(StrEnum):
    REQUIRED = "REQUIRED"
    WARNING = "WARNING"
    BLOCKING = "BLOCKING"


_EXISTS_OPERATORS = {StrategyRuleOperator.EXISTS, StrategyRuleOperator.NOT_EXISTS}
_COMPARISON_OPERATORS = {
    StrategyRuleOperator.EQ,
    StrategyRuleOperator.NE,
    StrategyRuleOperator.GT,
    StrategyRuleOperator.GTE,
    StrategyRuleOperator.LT,
    StrategyRuleOperator.LTE,
}
_ORDERED_COMPARISON_OPERATORS = {
    StrategyRuleOperator.GT,
    StrategyRuleOperator.GTE,
    StrategyRuleOperator.LT,
    StrategyRuleOperator.LTE,
}


def _normalize_identifier(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be non-empty")
    return normalized


def _normalize_string_collection(value: object, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        raw_items: tuple[object, ...] = (value,)
    elif isinstance(value, list | tuple):
        raw_items = tuple(value)
    else:
        raise ValueError(f"{field_name} must be a string, list, or tuple")
    return tuple(sorted({str(item).strip() for item in raw_items if str(item).strip()}))


def _normalize_decimal_value(value: object) -> Decimal:
    if isinstance(value, float):
        raise ValueError("strategy rule values must use Decimal-compatible inputs, not float")
    if isinstance(value, bool):
        raise ValueError("strategy rule Decimal values must not be boolean")
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("strategy rule Decimal value must be finite")
        return value
    if isinstance(value, int | str):
        try:
            normalized = Decimal(value)
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("strategy rule Decimal value is invalid") from exc
        if not normalized.is_finite():
            raise ValueError("strategy rule Decimal value must be finite")
        return normalized
    raise ValueError("unsupported strategy rule Decimal value type")


def _normalize_serialized_rule_value(
    value: dict[str, object],
) -> str | bool | Decimal | tuple[str, ...] | tuple[Decimal, ...]:
    value_type = value.get("type")
    raw_value = value.get("value")
    if value_type == "string":
        if not isinstance(raw_value, str):
            raise ValueError("serialized string rule value must contain a string")
        return _normalize_scalar_value(raw_value)
    if value_type == "bool":
        if not isinstance(raw_value, bool):
            raise ValueError("serialized bool rule value must contain a boolean")
        return raw_value
    if value_type == "decimal":
        return _normalize_decimal_value(raw_value)
    if value_type == "string_list":
        if not isinstance(raw_value, list):
            raise ValueError("serialized string_list rule value must contain a list")
        normalized = _normalize_collection_value(tuple(raw_value))
        if not all(isinstance(item, str) for item in normalized):
            raise ValueError("serialized string_list rule value must contain strings")
        return normalized
    if value_type == "decimal_list":
        if not isinstance(raw_value, list):
            raise ValueError("serialized decimal_list rule value must contain a list")
        normalized = tuple(sorted({_normalize_decimal_value(item) for item in raw_value}))
        if not normalized:
            raise ValueError("serialized decimal_list rule value must be non-empty")
        return normalized
    raise ValueError("serialized rule value type is unsupported")


def _normalize_scalar_value(value: object) -> str | bool | Decimal:
    if isinstance(value, float):
        raise ValueError("strategy rule values must use Decimal-compatible inputs, not float")
    if isinstance(value, bool):
        return value
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("strategy rule Decimal value must be finite")
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            raise ValueError("strategy rule string values must be non-empty")
        return normalized
    raise ValueError("unsupported strategy rule value type")


def _normalize_collection_value(
    value: list[object] | tuple[object, ...],
) -> tuple[str, ...] | tuple[Decimal, ...]:
    if not value:
        raise ValueError("strategy rule collection values must be non-empty")
    normalized_items = tuple(_normalize_scalar_value(item) for item in value)
    string_values = [item for item in normalized_items if isinstance(item, str)]
    if len(string_values) == len(normalized_items):
        return tuple(sorted(set(string_values)))
    decimal_values = [item for item in normalized_items if isinstance(item, Decimal)]
    if len(decimal_values) == len(normalized_items):
        return tuple(sorted(set(decimal_values)))
    raise ValueError("strategy rule collection values must be all strings or all Decimals")


def _normalize_rule_value(
    value: object,
) -> str | bool | Decimal | tuple[str, ...] | tuple[Decimal, ...]:
    if isinstance(value, dict):
        return _normalize_serialized_rule_value(value)
    if isinstance(value, list | tuple):
        return _normalize_collection_value(value)
    return _normalize_scalar_value(value)


class StrategyRuleValue(BaseModel):
    value: Any

    model_config = ConfigDict(frozen=True)

    @field_validator("value", mode="before")
    @classmethod
    def normalize_value(cls, value: object) -> object:
        return _normalize_rule_value(value)

    @property
    def is_collection(self) -> bool:
        return isinstance(self.value, tuple)

    @property
    def is_scalar(self) -> bool:
        return not self.is_collection

    def deterministic_json(self) -> str:
        return json.dumps(
            self.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    @field_serializer("value")
    def serialize_value(self, value: object) -> dict[str, object]:
        if isinstance(value, bool):
            return {"type": "bool", "value": value}
        if isinstance(value, Decimal):
            return {"type": "decimal", "value": str(value)}
        if isinstance(value, str):
            return {"type": "string", "value": value}
        if isinstance(value, tuple) and all(isinstance(item, Decimal) for item in value):
            return {"type": "decimal_list", "value": [str(item) for item in value]}
        if isinstance(value, tuple) and all(isinstance(item, str) for item in value):
            return {"type": "string_list", "value": list(value)}
        raise TypeError("unsupported normalized strategy rule value type")


class StrategyRuleCondition(BaseModel):
    field_ref: str = Field(pattern=r"^[A-Za-z0-9_.:-]+$")
    operator: StrategyRuleOperator
    expected_value: StrategyRuleValue | None = None
    lower_bound: StrategyRuleValue | None = None
    upper_bound: StrategyRuleValue | None = None
    allowed_values: StrategyRuleValue | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("field_ref", mode="before")
    @classmethod
    def normalize_field_ref(cls, value: object) -> str:
        return _normalize_identifier(value, "field_ref")

    @model_validator(mode="after")
    def validate_operator_values(self) -> Self:
        if self.operator in _EXISTS_OPERATORS:
            self._reject_operands_for_exists()
        elif self.operator in _COMPARISON_OPERATORS:
            self._validate_comparison_operator()
        elif self.operator == StrategyRuleOperator.BETWEEN:
            self._validate_between_operator()
        elif self.operator == StrategyRuleOperator.IN:
            self._validate_in_operator()
        return self

    def _reject_operands_for_exists(self) -> None:
        if any(
            value is not None
            for value in (
                self.expected_value,
                self.lower_bound,
                self.upper_bound,
                self.allowed_values,
            )
        ):
            raise ValueError("EXISTS and NOT_EXISTS rules must not define comparison values")

    def _validate_comparison_operator(self) -> None:
        if self.expected_value is None:
            raise ValueError(f"{self.operator} requires expected_value")
        if not self.expected_value.is_scalar:
            raise ValueError(f"{self.operator} expected_value must be scalar")
        if self.operator in _ORDERED_COMPARISON_OPERATORS and isinstance(
            self.expected_value.value, bool
        ):
            raise ValueError(f"{self.operator} expected_value must be ordered")
        if any(
            value is not None for value in (self.lower_bound, self.upper_bound, self.allowed_values)
        ):
            raise ValueError(f"{self.operator} must not define range or allowed values")

    def _validate_between_operator(self) -> None:
        if self.lower_bound is None or self.upper_bound is None:
            raise ValueError("BETWEEN requires lower_bound and upper_bound")
        if self.expected_value is not None or self.allowed_values is not None:
            raise ValueError("BETWEEN must not define expected_value or allowed_values")
        lower = self._ordered_scalar(self.lower_bound, "lower_bound")
        upper = self._ordered_scalar(self.upper_bound, "upper_bound")
        if self._lower_exceeds_upper(lower, upper):
            raise ValueError("BETWEEN lower_bound must be less than or equal to upper_bound")

    def _validate_in_operator(self) -> None:
        if self.allowed_values is None:
            raise ValueError("IN requires allowed_values")
        if not self.allowed_values.is_collection:
            raise ValueError("IN allowed_values must be a collection")
        if any(
            value is not None for value in (self.expected_value, self.lower_bound, self.upper_bound)
        ):
            raise ValueError("IN must not define expected_value or range values")

    @staticmethod
    def _ordered_scalar(value: StrategyRuleValue, field_name: str) -> str | Decimal:
        if not value.is_scalar or isinstance(value.value, bool):
            raise ValueError(f"{field_name} must be an ordered scalar")
        if not isinstance(value.value, str | Decimal):
            raise ValueError(f"{field_name} must be a string or Decimal")
        return value.value

    @staticmethod
    def _lower_exceeds_upper(lower: str | Decimal, upper: str | Decimal) -> bool:
        if isinstance(lower, Decimal):
            if not isinstance(upper, Decimal):
                raise ValueError("BETWEEN lower_bound and upper_bound must use the same value type")
            return lower > upper
        if not isinstance(upper, str):
            raise ValueError("BETWEEN lower_bound and upper_bound must use the same value type")
        return lower > upper


class StrategyRuleSpec(BaseModel):
    rule_id: str = Field(pattern=r"^[A-Za-z0-9_.:-]+$")
    category: StrategyRuleCategory
    severity: StrategyRuleSeverity
    condition: StrategyRuleCondition
    description: str = Field(min_length=1, max_length=1000)
    enabled: bool = False
    warnings: tuple[str, ...] = ()

    model_config = ConfigDict(frozen=True)

    @field_validator("rule_id", mode="before")
    @classmethod
    def normalize_rule_id(cls, value: object) -> str:
        return _normalize_identifier(value, "rule_id")

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: object) -> str:
        return _normalize_identifier(value, "description")

    @field_validator("warnings", mode="before")
    @classmethod
    def normalize_warnings(cls, value: object) -> tuple[str, ...]:
        return _normalize_string_collection(value, "warnings")

    @property
    def is_actionable(self) -> bool:
        return False

    def canonical_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    def deterministic_json(self) -> str:
        return json.dumps(
            self.canonical_payload(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def fingerprint_sha256(self) -> str:
        return hashlib.sha256(self.deterministic_json().encode("utf-8")).hexdigest()


class StrategyRuleSet(BaseModel):
    ruleset_version: str = Field(min_length=1)
    strategy_version: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    created_at: datetime
    rules: tuple[StrategyRuleSpec, ...] = Field(min_length=1)
    enabled: bool = False
    fingerprint: str | None = Field(default=None, min_length=64, max_length=64)

    model_config = ConfigDict(frozen=True)

    @field_validator("ruleset_version", "strategy_version", "name", mode="before")
    @classmethod
    def normalize_required_strings(cls, value: object) -> str:
        return _normalize_identifier(value, "strategy rule set string")

    @field_validator("description", mode="before")
    @classmethod
    def normalize_optional_description(cls, value: object) -> str | None:
        if value is None:
            return None
        return _normalize_identifier(value, "description")

    @field_validator("created_at")
    @classmethod
    def created_at_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("rules")
    @classmethod
    def normalize_rules(cls, value: tuple[StrategyRuleSpec, ...]) -> tuple[StrategyRuleSpec, ...]:
        return tuple(sorted(value, key=lambda rule: rule.rule_id))

    @model_validator(mode="after")
    def rule_ids_must_be_unique(self) -> Self:
        rule_ids = [rule.rule_id for rule in self.rules]
        if len(rule_ids) != len(set(rule_ids)):
            raise ValueError("StrategyRuleSet rule_id values must be unique")
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

### `tests/unit/test_strategy_rule_specification_foundation.py`

```python
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.entities.strategy_rules import (
    StrategyRuleCategory,
    StrategyRuleCondition,
    StrategyRuleOperator,
    StrategyRuleSet,
    StrategyRuleSeverity,
    StrategyRuleSpec,
    StrategyRuleValue,
)

CREATED_AT = datetime(2026, 7, 18, 9, 0, tzinfo=UTC)


def _condition(**overrides: object) -> StrategyRuleCondition:
    values: dict[str, object] = {
        "field_ref": "data_quality.market_data_complete",
        "operator": StrategyRuleOperator.EQ,
        "expected_value": StrategyRuleValue(value=True),
    }
    values.update(overrides)
    return StrategyRuleCondition(**values)


def _rule(rule_id: str = "data_quality.complete", **overrides: object) -> StrategyRuleSpec:
    values: dict[str, object] = {
        "rule_id": rule_id,
        "category": StrategyRuleCategory.DATA_QUALITY,
        "severity": StrategyRuleSeverity.REQUIRED,
        "condition": _condition(),
        "description": "Require a complete deterministic data-quality snapshot.",
        "warnings": ("contract only",),
    }
    values.update(overrides)
    return StrategyRuleSpec(**values)


def _ruleset(**overrides: object) -> StrategyRuleSet:
    values: dict[str, object] = {
        "ruleset_version": "phase4b-ruleset-v1",
        "strategy_version": "future-strategy-spec-v1",
        "name": "Future strategy rule specification",
        "description": "Specification-only rule set for future deterministic checks.",
        "created_at": CREATED_AT,
        "rules": (
            _rule("time.session"),
            _rule("data_quality.complete"),
        ),
    }
    values.update(overrides)
    return StrategyRuleSet(**values)


def test_project_phase_is_phase4b_strategy_rule_specification_foundation() -> None:
    assert constants.PROJECT_PHASE == "phase_4b_strategy_rule_specification_foundation"


def test_strategy_rule_models_are_immutable() -> None:
    rule_set = _ruleset()

    with pytest.raises(ValidationError):
        rule_set.enabled = True
    with pytest.raises(ValidationError):
        rule_set.rules[0].condition.field_ref = "changed"


def test_strategy_rule_set_normalizes_created_at_to_utc() -> None:
    offset = timezone(timedelta(hours=2))
    rule_set = _ruleset(created_at=datetime(2026, 7, 18, 11, 0, tzinfo=offset))

    assert rule_set.created_at == CREATED_AT


def test_strategy_rule_set_rejects_duplicate_rule_id() -> None:
    with pytest.raises(ValidationError):
        _ruleset(rules=(_rule("duplicate.rule"), _rule("duplicate.rule")))


def test_strategy_rule_identifiers_must_be_non_empty_and_deterministic() -> None:
    with pytest.raises(ValidationError):
        _rule(" ")
    with pytest.raises(ValidationError):
        _rule("bad rule id")
    with pytest.raises(ValidationError):
        _condition(field_ref=" ")
    with pytest.raises(ValidationError):
        _condition(field_ref="market context.value")


def test_strategy_rules_default_to_disabled_and_not_actionable() -> None:
    rule = _rule()
    rule_set = _ruleset(rules=(rule,))

    assert rule.enabled is False
    assert rule_set.enabled is False
    assert rule.is_actionable is False
    assert rule_set.is_actionable is False


def test_between_operator_requires_ordered_bounds() -> None:
    condition = _condition(
        operator=StrategyRuleOperator.BETWEEN,
        expected_value=None,
        lower_bound=StrategyRuleValue(value=Decimal("0.10")),
        upper_bound=StrategyRuleValue(value=Decimal("0.25")),
    )

    assert condition.lower_bound == StrategyRuleValue(value=Decimal("0.10"))

    with pytest.raises(ValidationError):
        _condition(operator=StrategyRuleOperator.BETWEEN, expected_value=None)
    with pytest.raises(ValidationError):
        _condition(
            operator=StrategyRuleOperator.BETWEEN,
            expected_value=None,
            lower_bound=StrategyRuleValue(value=Decimal("0.25")),
            upper_bound=StrategyRuleValue(value=Decimal("0.10")),
        )
    with pytest.raises(ValidationError):
        _condition(
            operator=StrategyRuleOperator.BETWEEN,
            expected_value=StrategyRuleValue(value=Decimal("0.10")),
            lower_bound=StrategyRuleValue(value=Decimal("0.10")),
            upper_bound=StrategyRuleValue(value=Decimal("0.25")),
        )


def test_in_operator_requires_allowed_values_collection() -> None:
    condition = _condition(
        operator=StrategyRuleOperator.IN,
        expected_value=None,
        allowed_values=StrategyRuleValue(value=("LOW", "HIGH", "HIGH")),
    )

    assert condition.allowed_values == StrategyRuleValue(value=("HIGH", "LOW"))

    with pytest.raises(ValidationError):
        _condition(operator=StrategyRuleOperator.IN, expected_value=None)
    with pytest.raises(ValidationError):
        _condition(
            operator=StrategyRuleOperator.IN,
            expected_value=None,
            allowed_values=StrategyRuleValue(value="HIGH"),
        )
    with pytest.raises(ValidationError):
        _condition(
            operator=StrategyRuleOperator.IN,
            expected_value=StrategyRuleValue(value="HIGH"),
            allowed_values=StrategyRuleValue(value=("HIGH", "LOW")),
        )


def test_exists_operators_do_not_accept_comparison_values() -> None:
    assert _condition(operator=StrategyRuleOperator.EXISTS, expected_value=None).operator == (
        StrategyRuleOperator.EXISTS
    )
    assert _condition(operator=StrategyRuleOperator.NOT_EXISTS, expected_value=None).operator == (
        StrategyRuleOperator.NOT_EXISTS
    )

    with pytest.raises(ValidationError):
        _condition(operator=StrategyRuleOperator.EXISTS)
    with pytest.raises(ValidationError):
        _condition(
            operator=StrategyRuleOperator.NOT_EXISTS,
            expected_value=None,
            allowed_values=StrategyRuleValue(value=("a", "b")),
        )


@pytest.mark.parametrize(
    "operator",
    [
        StrategyRuleOperator.EQ,
        StrategyRuleOperator.NE,
        StrategyRuleOperator.GT,
        StrategyRuleOperator.GTE,
        StrategyRuleOperator.LT,
        StrategyRuleOperator.LTE,
    ],
)
def test_comparison_operators_require_expected_value(operator: StrategyRuleOperator) -> None:
    expected_value = (
        StrategyRuleValue(value=Decimal("1.0"))
        if operator
        in {
            StrategyRuleOperator.GT,
            StrategyRuleOperator.GTE,
            StrategyRuleOperator.LT,
            StrategyRuleOperator.LTE,
        }
        else StrategyRuleValue(value=True)
    )

    assert _condition(operator=operator, expected_value=expected_value).operator == operator

    with pytest.raises(ValidationError):
        _condition(operator=operator, expected_value=None)
    with pytest.raises(ValidationError):
        _condition(
            operator=operator,
            expected_value=StrategyRuleValue(value=("a", "b")),
        )


def test_ordered_comparison_operators_reject_boolean_expected_values() -> None:
    with pytest.raises(ValidationError):
        _condition(operator=StrategyRuleOperator.GT, expected_value=StrategyRuleValue(value=True))


def test_strategy_rule_value_rejects_floats() -> None:
    with pytest.raises(ValidationError):
        StrategyRuleValue(value=1.2)
    with pytest.raises(ValidationError):
        StrategyRuleValue(value=(Decimal("1.0"), 2.0))


def test_strategy_rule_value_decimal_json_round_trips_exactly() -> None:
    value = StrategyRuleValue(value=Decimal("1.20"))
    values = StrategyRuleValue(value=(Decimal("1.20"), Decimal("1.10"), Decimal("1.10")))

    assert StrategyRuleValue.model_validate_json(value.model_dump_json()) == value
    assert StrategyRuleValue.model_validate_json(values.model_dump_json()) == StrategyRuleValue(
        value=(Decimal("1.10"), Decimal("1.20"))
    )


def test_strategy_rule_value_rejects_invalid_collection_values() -> None:
    with pytest.raises(ValidationError):
        StrategyRuleValue(value=())
    with pytest.raises(ValidationError):
        StrategyRuleValue(value=(Decimal("1.0"), "mixed"))
    with pytest.raises(ValidationError):
        StrategyRuleValue(value=(True, False))
    with pytest.raises(ValidationError):
        StrategyRuleValue(value=Decimal("NaN"))


def test_warnings_are_normalized_deterministically() -> None:
    rule = _rule(warnings=("beta", "alpha", "alpha", " "))

    assert rule.warnings == ("alpha", "beta")


def test_rules_are_normalized_deterministically_by_rule_id() -> None:
    rule_set = _ruleset(rules=(_rule("z.rule"), _rule("a.rule")))

    assert tuple(rule.rule_id for rule in rule_set.rules) == ("a.rule", "z.rule")


def test_strategy_rule_set_serializes_deterministically_and_round_trips() -> None:
    rule_set = _ruleset()
    same_rule_set = _ruleset(rules=tuple(reversed(rule_set.rules)))

    assert rule_set.deterministic_json() == same_rule_set.deterministic_json()
    assert StrategyRuleSet.model_validate_json(rule_set.deterministic_json()) == rule_set


def test_strategy_rule_fingerprints_are_deterministic() -> None:
    rule = _rule(warnings=("beta", "alpha"))
    same_rule = _rule(warnings=("alpha", "beta"))
    rule_set = _ruleset()
    same_rule_set = _ruleset(rules=tuple(reversed(rule_set.rules)))

    assert rule.fingerprint_sha256() == same_rule.fingerprint_sha256()
    assert rule_set.fingerprint_sha256() == same_rule_set.fingerprint_sha256()
    assert len(rule_set.fingerprint_sha256()) == 64


def test_strategy_rule_fingerprint_changes_when_key_fields_change() -> None:
    rule_set = _ruleset()
    changed = _ruleset(strategy_version="future-strategy-spec-v2")

    assert rule_set.fingerprint_sha256() != changed.fingerprint_sha256()


def test_strategy_rule_specs_do_not_define_scoring_confidence_or_executable_fields() -> None:
    forbidden_fragments = (
        "score",
        "weight",
        "confidence",
        "action",
        "execution",
        "broker",
        "order",
        "position",
    )
    field_names = set(StrategyRuleSpec.model_fields) | set(StrategyRuleSet.model_fields)
    condition_field_names = set(StrategyRuleCondition.model_fields)
    all_field_names = field_names | condition_field_names

    offenders = [
        field_name
        for field_name in all_field_names
        for fragment in forbidden_fragments
        if fragment in field_name.lower()
    ]

    assert offenders == []
```

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
from app.domain.entities import Timeframe, signal_contract, strategy_rules
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
PHASE_4B_SPEC_OBJECTS = (
    strategy_rules.StrategyRuleCategory,
    strategy_rules.StrategyRuleCondition,
    strategy_rules.StrategyRuleOperator,
    strategy_rules.StrategyRuleSet,
    strategy_rules.StrategyRuleSeverity,
    strategy_rules.StrategyRuleSpec,
    strategy_rules.StrategyRuleValue,
)
PHASE_4B_FORBIDDEN_BEHAVIOR_TERMS = (
    "strategy_engine",
    "strategy_evaluator",
    "rule_engine",
    "rule_evaluator",
    "evaluate_rules",
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


def test_phase4b_strategy_rule_spec_objects_do_not_add_evaluation_or_execution_terms() -> None:
    offenders: list[str] = []
    texts = [inspect.getsource(source_object) for source_object in PHASE_4B_SPEC_OBJECTS]
    for index, text in enumerate(texts):
        lowered = text.lower()
        for term in PHASE_4B_FORBIDDEN_BEHAVIOR_TERMS:
            if term.lower() in lowered:
                offenders.append(f"phase4b-spec-{index}: {term}")

    assert offenders == []


def test_phase4b_does_not_add_strategy_or_signal_api_routes() -> None:
    route_files = tuple(Path("app/api/routes").glob("*.py"))
    offenders = [
        str(file_path)
        for file_path in route_files
        if "signal" in file_path.name.lower()
        or "strategy" in file_path.name.lower()
        or "rule" in file_path.name.lower()
        or "StrategyRuleSet" in file_path.read_text(encoding="utf-8")
        or "StrategyRuleSpec" in file_path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_phase4b_does_not_add_telegram_signal_or_rule_handlers() -> None:
    source = Path("app/telegram/commands.py").read_text(encoding="utf-8")

    assert "signal_command" not in source
    assert "strategy_command" not in source
    assert "rule_command" not in source
    assert 'CommandHandler("signal"' not in source
    assert 'CommandHandler("strategy"' not in source
    assert 'CommandHandler("rules"' not in source
    assert "StrategyRuleSet" not in source


def test_phase4b_does_not_add_scheduler_signal_or_rule_jobs() -> None:
    scheduler_text = "\n".join(
        file_path.read_text(encoding="utf-8") for file_path in Path("app/scheduler").glob("*.py")
    )

    assert "StrategyRuleSet" not in scheduler_text
    assert "strategy_rule_job" not in scheduler_text
    assert "rule_evaluation" not in scheduler_text
    assert "generate_signal" not in scheduler_text


def test_phase4b_does_not_add_strategy_evaluation_service() -> None:
    service_files = tuple(Path("app/services").glob("*.py"))
    offenders = [
        str(file_path)
        for file_path in service_files
        if "strategy" in file_path.name.lower()
        or "rule" in file_path.name.lower()
        or "StrategyRuleSet" in file_path.read_text(encoding="utf-8")
        or "StrategyRuleSpec" in file_path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_phase3j_digest_audit_api_route_is_absent() -> None:
    assert not Path("app/api/routes/digest_deliveries.py").exists()


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


def test_project_phase_has_advanced_to_phase4b_strategy_rule_specification_foundation() -> None:
    assert constants.PROJECT_PHASE == "phase_4b_strategy_rule_specification_foundation"


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
- `docs/phase4b-verification-report.md`
- `docs/chatgpt-verification-packet.md`
