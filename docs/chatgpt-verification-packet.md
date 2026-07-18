# ChatGPT Verification Packet: Phase 4C Strategy Ruleset Validation Foundation

Generated: 2026-07-18T13:17:54Z

## Repository Metadata

- Repository path: `/Users/artem.otsel/Documents/ai-trading-os`
- Git branch: `main`
- Current commit hash: `437e1113a0ed63cff98d9276727f0d0b4d692e0a`
- Latest commit at start of Phase 4C work: `437e111  Phase 4B`
- Commit status: Phase 4C remains uncommitted at packet generation time.

## Preflight

Preflight passed before edits:

```text
git status --short
<clean>

git log --oneline -5
437e111  Phase 4B
a4c8f27  Phase 4A
bad58a4 Add Phase 3I persistent digest audit foundation
901d864 Phase 3H Done
ab4aafb phase 3G done

grep -n "PROJECT_PHASE" app/core/constants.py
1:PROJECT_PHASE = "phase_4b_strategy_rule_specification_foundation"

test -f app/domain/entities/strategy_rules.py && echo "Phase 4B strategy_rules exists"
Phase 4B strategy_rules exists

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
 M tests/unit/test_strategy_rule_specification_foundation.py
?? app/domain/entities/strategy_validation.py
?? app/domain/strategy_ruleset_validator.py
?? docs/phase4c-verification-report.md
?? tests/unit/test_strategy_ruleset_validation_foundation.py
```

## Git Diff Stat

```text
 AGENTS.md                                          |   22 +-
 PLANS.md                                           |   23 +-
 README.md                                          |   17 +-
 app/core/constants.py                              |    2 +-
 app/domain/entities/__init__.py                    |   10 +
 docs/chatgpt-verification-packet.md                | 1880 +++++++++++++-------
 docs/operations.md                                 |    7 +
 tests/contract/test_safety_boundaries.py           |  109 +-
 tests/unit/test_signal_contract_foundation.py      |    4 +-
 .../test_strategy_rule_specification_foundation.py |    4 +-
 10 files changed, 1366 insertions(+), 712 deletions(-)
```

## Git Log

```text
437e111  Phase 4B
a4c8f27  Phase 4A
bad58a4 Add Phase 3I persistent digest audit foundation
901d864 Phase 3H Done
ab4aafb phase 3G done
40473bd Add Phase 3F readiness scheduler foundation
588ab6a Phase 3E DONE
8166820 phase 3C DONE
60e6e53 Add Phase 3C indicator context foundation
a6f44f0 Add Phase 3B feature engine foundation
```

## Created Files

- `app/domain/entities/strategy_validation.py`
- `app/domain/strategy_ruleset_validator.py`
- `docs/phase4c-verification-report.md`
- `tests/unit/test_strategy_ruleset_validation_foundation.py`

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
- `tests/unit/test_strategy_rule_specification_foundation.py`

## Migration Files Created Or Modified

- None

Phase 4C did not require a migration. Alembic head remains `0003_phase3i_digest_audit (head)`.

## Phase Scope Confirmation

Phase 4C is validation-only. It validates only the structure and safety of `StrategyRuleSet` objects introduced in Phase 4B.

Phase 4C does not evaluate rules against market data, candles, indicators, economic events, context snapshots, analysis snapshots, or signal contracts. It does not implement a strategy engine, rule evaluation against market data, signal generation, setup scoring, confidence scoring, automated LONG/SHORT decisions, buy/sell recommendations, entry calculation logic, stop loss calculation logic, take profit calculation logic, position sizing logic, portfolio/risk decisions, AI agents, OpenAI calls, LLM usage, Telegram signal sending, API signal routes, scheduler signal jobs, broker APIs, order execution, paper trading, real trading, backtesting, or a trading simulator.

Rule specs and rule sets remain disabled and non-actionable.

Phase 3J digest audit API route is absent: `True`.

## Implementation Summary

- Updated `PROJECT_PHASE` to `phase_4c_strategy_ruleset_validation_foundation`.
- Added immutable validation report models in `app/domain/entities/strategy_validation.py`.
- Added `StrategyRuleSetValidator` in `app/domain/strategy_ruleset_validator.py`.
- Added a deterministic static allowed field registry and category-to-prefix compatibility map.
- Added forbidden action/scoring/confidence language checks for rule field refs, descriptions, and warnings.
- Added validation outcomes for enabled rule sets, enabled rules, unknown field refs, category mismatches, forbidden language, and invalid operands from unsafely constructed rule specs.
- Added deterministic issue ordering by code, rule ID, field ref, and message.
- Added deterministic validation report JSON serialization and SHA-256 fingerprinting excluding optional stored fingerprint.
- Added tests proving validator does not mutate input and accepts only `StrategyRuleSet` plus `checked_at`.
- Updated README, AGENTS, PLANS, operations docs, Phase 4C report, and this packet.

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

## Exact Verification Command Outputs

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

## Skipped Checks

- Host `uv run pytest` skipped 7 integration tests because host integration tests require `REQUIRE_INTEGRATION_TESTS=true` and a PostgreSQL integration database. The same integration file was run in Docker twice with `REQUIRE_INTEGRATION_TESTS=true`, and both Docker runs passed.

## Unavailable Checks

- None for the requested Phase 4C verification set. Docker Desktop, PostgreSQL container, Alembic, Docker integration tests, and `docker compose config` were available and run.

## Remaining Risks

- Phase 4C intentionally validates specification structure only; future phases must add separate tests before any rule evaluation against market data, decision engine, signal generation, delivery, broker, paper-trading, or live-trading behavior can exist.
- Validation reports are not persisted in this phase; no database migration was added.
- Existing Starlette/httpx deprecation warning remains in test output and is unrelated to Phase 4C behavior.

## Traceability

| Requirement | Implementation File | Test File | Verification Result |
| --- | --- | --- | --- |
| Update project phase to Phase 4C | `app/core/constants.py` | `tests/unit/test_strategy_ruleset_validation_foundation.py` | Host and Docker tests passed |
| Define validation status, issue codes, issue/report models | `app/domain/entities/strategy_validation.py` | `tests/unit/test_strategy_ruleset_validation_foundation.py` | Unit tests passed |
| Normalize checked_at to UTC | `app/domain/entities/strategy_validation.py` | `tests/unit/test_strategy_ruleset_validation_foundation.py` | UTC normalization test passed |
| Validate clean disabled ruleset as VALID | `app/domain/strategy_ruleset_validator.py` | `tests/unit/test_strategy_ruleset_validation_foundation.py` | Clean validation test passed |
| Validate enabled ruleset/rules as INVALID | `app/domain/strategy_ruleset_validator.py` | `tests/unit/test_strategy_ruleset_validation_foundation.py` | Enabled invalid tests passed |
| Validate unknown field refs and category mismatches | `app/domain/strategy_ruleset_validator.py` | `tests/unit/test_strategy_ruleset_validation_foundation.py` | Registry/mismatch tests passed |
| Validate forbidden execution/scoring/confidence language | `app/domain/strategy_ruleset_validator.py` | `tests/unit/test_strategy_ruleset_validation_foundation.py` | Forbidden language tests passed |
| Validate invalid operator operands from unsafe construction | `app/domain/strategy_ruleset_validator.py` | `tests/unit/test_strategy_ruleset_validation_foundation.py` | Invalid operands test passed |
| Deterministic report JSON, fingerprint, and issue ordering | `app/domain/entities/strategy_validation.py` | `tests/unit/test_strategy_ruleset_validation_foundation.py` | Determinism tests passed |
| Validator does not mutate input and only accepts StrategyRuleSet | `app/domain/strategy_ruleset_validator.py` | `tests/unit/test_strategy_ruleset_validation_foundation.py` | Mutation/input tests passed |
| Do not add API routes, Telegram handlers, scheduler jobs, or validation/evaluation services | No runtime files added | `tests/contract/test_safety_boundaries.py` | Safety boundary tests passed |
| Do not add broker/order/paper/live trading behavior | No execution code added | `tests/contract/test_safety_boundaries.py`, `scripts/security_check.py` | Safety tests and security check passed |
| Keep Phase 3J absent | No `app/api/routes/digest_deliveries.py` | `tests/contract/test_safety_boundaries.py` | Phase 3J absence test passed |
| No migration required | No migration file created or modified | `docker compose run --rm migrate alembic current`, `docker compose run --rm migrate alembic check` | Alembic head remained `0003_phase3i_digest_audit (head)` and check passed |

## Full Contents Of Changed Source Files

### `app/core/constants.py`

```python
PROJECT_PHASE = "phase_4c_strategy_ruleset_validation_foundation"
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
from app.domain.entities.strategy_validation import (
    StrategyRuleSetValidationIssue,
    StrategyRuleSetValidationIssueCode,
    StrategyRuleSetValidationReport,
    StrategyRuleSetValidationStatus,
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
    "StrategyRuleSetValidationIssue",
    "StrategyRuleSetValidationIssueCode",
    "StrategyRuleSetValidationReport",
    "StrategyRuleSetValidationStatus",
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

### `app/domain/entities/strategy_validation.py`

```python
import hashlib
import json
from datetime import datetime
from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.strategy_rules import StrategyRuleSeverity


class StrategyRuleSetValidationStatus(StrEnum):
    VALID = "VALID"
    INVALID = "INVALID"
    WARNING = "WARNING"


class StrategyRuleSetValidationIssueCode(StrEnum):
    EMPTY_RULESET = "EMPTY_RULESET"
    DUPLICATE_RULE_ID = "DUPLICATE_RULE_ID"
    RULESET_ENABLED = "RULESET_ENABLED"
    RULE_ENABLED = "RULE_ENABLED"
    UNKNOWN_FIELD_REF = "UNKNOWN_FIELD_REF"
    CATEGORY_FIELD_MISMATCH = "CATEGORY_FIELD_MISMATCH"
    FORBIDDEN_FIELD_REF = "FORBIDDEN_FIELD_REF"
    FORBIDDEN_EXECUTION_LANGUAGE = "FORBIDDEN_EXECUTION_LANGUAGE"
    FORBIDDEN_SCORING_LANGUAGE = "FORBIDDEN_SCORING_LANGUAGE"
    FORBIDDEN_CONFIDENCE_LANGUAGE = "FORBIDDEN_CONFIDENCE_LANGUAGE"
    INVALID_OPERATOR_OPERANDS = "INVALID_OPERATOR_OPERANDS"


def _normalize_optional_string(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be non-empty")
    return normalized


def _normalize_required_string(value: object, field_name: str) -> str:
    normalized = _normalize_optional_string(value, field_name)
    if normalized is None:
        raise ValueError(f"{field_name} must be non-empty")
    return normalized


class StrategyRuleSetValidationIssue(BaseModel):
    code: StrategyRuleSetValidationIssueCode
    message: str = Field(min_length=1, max_length=1000)
    rule_id: str | None = None
    field_ref: str | None = None
    severity: StrategyRuleSeverity

    model_config = ConfigDict(frozen=True)

    @field_validator("message", mode="before")
    @classmethod
    def normalize_message(cls, value: object) -> str:
        return _normalize_required_string(value, "message")

    @field_validator("rule_id", "field_ref", mode="before")
    @classmethod
    def normalize_optional_identifiers(cls, value: object) -> str | None:
        return _normalize_optional_string(value, "validation issue identifier")

    @property
    def sort_key(self) -> tuple[str, str, str, str]:
        return (
            self.code.value,
            self.rule_id or "",
            self.field_ref or "",
            self.message,
        )


class StrategyRuleSetValidationReport(BaseModel):
    ruleset_version: str = Field(min_length=1)
    strategy_version: str = Field(min_length=1)
    ruleset_name: str = Field(min_length=1, max_length=120)
    status: StrategyRuleSetValidationStatus
    checked_at: datetime
    issues: tuple[StrategyRuleSetValidationIssue, ...] = ()
    rule_count: int = Field(ge=0)
    enabled_rule_count: int = Field(ge=0)
    fingerprint: str | None = Field(default=None, min_length=64, max_length=64)

    model_config = ConfigDict(frozen=True)

    @field_validator("ruleset_version", "strategy_version", "ruleset_name", mode="before")
    @classmethod
    def normalize_required_strings(cls, value: object) -> str:
        return _normalize_required_string(value, "validation report string")

    @field_validator("checked_at")
    @classmethod
    def checked_at_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("issues")
    @classmethod
    def normalize_issues(
        cls,
        value: tuple[StrategyRuleSetValidationIssue, ...],
    ) -> tuple[StrategyRuleSetValidationIssue, ...]:
        return tuple(sorted(value, key=lambda issue: issue.sort_key))

    @model_validator(mode="after")
    def validate_counts_and_status(self) -> Self:
        if self.enabled_rule_count > self.rule_count:
            raise ValueError("enabled_rule_count must not exceed rule_count")
        if self.status == StrategyRuleSetValidationStatus.VALID and self.issues:
            raise ValueError("VALID validation reports must not contain issues")
        if self.status != StrategyRuleSetValidationStatus.VALID and not self.issues:
            raise ValueError("non-VALID validation reports must contain issues")
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

### `app/domain/strategy_ruleset_validator.py`

```python
from datetime import datetime
from decimal import Decimal

from app.domain.entities.strategy_rules import (
    StrategyRuleCategory,
    StrategyRuleCondition,
    StrategyRuleOperator,
    StrategyRuleSet,
    StrategyRuleSeverity,
    StrategyRuleSpec,
    StrategyRuleValue,
)
from app.domain.entities.strategy_validation import (
    StrategyRuleSetValidationIssue,
    StrategyRuleSetValidationIssueCode,
    StrategyRuleSetValidationReport,
    StrategyRuleSetValidationStatus,
)

ALLOWED_FIELD_PREFIXES: tuple[str, ...] = (
    "data_quality.",
    "market_context.",
    "event_context.",
    "risk_guard.",
    "time_filter.",
    "signal_contract_guard.",
)

CATEGORY_FIELD_PREFIXES: dict[StrategyRuleCategory, str] = {
    StrategyRuleCategory.DATA_QUALITY: "data_quality.",
    StrategyRuleCategory.MARKET_CONTEXT: "market_context.",
    StrategyRuleCategory.EVENT_CONTEXT: "event_context.",
    StrategyRuleCategory.RISK_GUARD: "risk_guard.",
    StrategyRuleCategory.TIME_FILTER: "time_filter.",
    StrategyRuleCategory.SIGNAL_CONTRACT_GUARD: "signal_contract_guard.",
}

FORBIDDEN_EXECUTION_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "execute",
    "order",
    "broker",
    "position_size",
    "open_trade",
    "close_trade",
    "take_trade",
    "entry_signal",
    "telegram_signal",
    "_".join(("place", "order")),
    "paper_trade",
    "live_trade",
    "backtest",
    "simulation",
)
FORBIDDEN_SCORING_TERMS: tuple[str, ...] = ("setup_score",)
FORBIDDEN_CONFIDENCE_TERMS: tuple[str, ...] = ("confidence", "openai", "llm")
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


class StrategyRuleSetValidator:
    def validate(
        self,
        ruleset: StrategyRuleSet,
        checked_at: datetime,
    ) -> StrategyRuleSetValidationReport:
        if not isinstance(ruleset, StrategyRuleSet):
            raise TypeError("StrategyRuleSetValidator validates StrategyRuleSet objects only")

        issues: list[StrategyRuleSetValidationIssue] = []
        if not ruleset.rules:
            issues.append(
                self._issue(
                    code=StrategyRuleSetValidationIssueCode.EMPTY_RULESET,
                    message="StrategyRuleSet must contain at least one rule.",
                )
            )
        if ruleset.enabled:
            issues.append(
                self._issue(
                    code=StrategyRuleSetValidationIssueCode.RULESET_ENABLED,
                    message="StrategyRuleSet must remain disabled in Phase 4C.",
                )
            )

        seen_rule_ids: set[str] = set()
        for rule in ruleset.rules:
            if rule.rule_id in seen_rule_ids:
                issues.append(
                    self._issue(
                        code=StrategyRuleSetValidationIssueCode.DUPLICATE_RULE_ID,
                        message="Duplicate rule_id detected.",
                        rule=rule,
                    )
                )
            seen_rule_ids.add(rule.rule_id)
            issues.extend(self._validate_rule(rule))

        return StrategyRuleSetValidationReport(
            ruleset_version=ruleset.ruleset_version,
            strategy_version=ruleset.strategy_version,
            ruleset_name=ruleset.name,
            status=self._status_for(issues),
            checked_at=checked_at,
            issues=tuple(issues),
            rule_count=len(ruleset.rules),
            enabled_rule_count=sum(1 for rule in ruleset.rules if rule.enabled),
        )

    def _validate_rule(self, rule: StrategyRuleSpec) -> tuple[StrategyRuleSetValidationIssue, ...]:
        issues: list[StrategyRuleSetValidationIssue] = []
        if rule.enabled:
            issues.append(
                self._issue(
                    code=StrategyRuleSetValidationIssueCode.RULE_ENABLED,
                    message="StrategyRuleSpec must remain disabled in Phase 4C.",
                    rule=rule,
                )
            )
        if not rule.condition.field_ref.startswith(ALLOWED_FIELD_PREFIXES):
            issues.append(
                self._issue(
                    code=StrategyRuleSetValidationIssueCode.UNKNOWN_FIELD_REF,
                    message="Rule field_ref is not in the static validation registry.",
                    rule=rule,
                    field_ref=rule.condition.field_ref,
                )
            )
        expected_prefix = CATEGORY_FIELD_PREFIXES[rule.category]
        if not rule.condition.field_ref.startswith(expected_prefix):
            issues.append(
                self._issue(
                    code=StrategyRuleSetValidationIssueCode.CATEGORY_FIELD_MISMATCH,
                    message="Rule category does not match the field_ref prefix.",
                    rule=rule,
                    field_ref=rule.condition.field_ref,
                )
            )
        issues.extend(self._scan_forbidden_language(rule))
        issues.extend(self._validate_condition_operands(rule))
        return tuple(issues)

    def _scan_forbidden_language(
        self,
        rule: StrategyRuleSpec,
    ) -> tuple[StrategyRuleSetValidationIssue, ...]:
        text = " ".join((rule.condition.field_ref, rule.description, *rule.warnings))
        lowered = text.lower()
        issues: list[StrategyRuleSetValidationIssue] = []
        if any(term in lowered for term in FORBIDDEN_EXECUTION_TERMS):
            issues.append(
                self._issue(
                    code=StrategyRuleSetValidationIssueCode.FORBIDDEN_EXECUTION_LANGUAGE,
                    message="Rule specification contains forbidden execution language.",
                    rule=rule,
                    field_ref=rule.condition.field_ref,
                )
            )
        if any(term in lowered for term in FORBIDDEN_SCORING_TERMS):
            issues.append(
                self._issue(
                    code=StrategyRuleSetValidationIssueCode.FORBIDDEN_SCORING_LANGUAGE,
                    message="Rule specification contains forbidden scoring language.",
                    rule=rule,
                    field_ref=rule.condition.field_ref,
                )
            )
        if any(term in lowered for term in FORBIDDEN_CONFIDENCE_TERMS):
            issues.append(
                self._issue(
                    code=StrategyRuleSetValidationIssueCode.FORBIDDEN_CONFIDENCE_LANGUAGE,
                    message="Rule specification contains forbidden confidence or AI language.",
                    rule=rule,
                    field_ref=rule.condition.field_ref,
                )
            )
        if self._field_ref_contains_forbidden_token(rule.condition.field_ref):
            issues.append(
                self._issue(
                    code=StrategyRuleSetValidationIssueCode.FORBIDDEN_FIELD_REF,
                    message="Rule field_ref contains forbidden action-oriented language.",
                    rule=rule,
                    field_ref=rule.condition.field_ref,
                )
            )
        return tuple(issues)

    def _validate_condition_operands(
        self,
        rule: StrategyRuleSpec,
    ) -> tuple[StrategyRuleSetValidationIssue, ...]:
        condition = rule.condition
        if condition.operator in _EXISTS_OPERATORS and self._has_any_operand(condition):
            return (self._invalid_operands_issue(rule),)
        if condition.operator in _COMPARISON_OPERATORS:
            if (
                condition.expected_value is None
                or not condition.expected_value.is_scalar
                or self._has_range_or_allowed_values(condition)
            ):
                return (self._invalid_operands_issue(rule),)
            if condition.operator in _ORDERED_COMPARISON_OPERATORS and isinstance(
                condition.expected_value.value, bool
            ):
                return (self._invalid_operands_issue(rule),)
        if (
            condition.operator == StrategyRuleOperator.BETWEEN
            and self._has_invalid_between_operands(condition)
        ):
            return (self._invalid_operands_issue(rule),)
        if condition.operator == StrategyRuleOperator.IN and self._has_invalid_in_operands(
            condition
        ):
            return (self._invalid_operands_issue(rule),)
        return ()

    @staticmethod
    def _has_any_operand(condition: StrategyRuleCondition) -> bool:
        return any(
            value is not None
            for value in (
                condition.expected_value,
                condition.lower_bound,
                condition.upper_bound,
                condition.allowed_values,
            )
        )

    @staticmethod
    def _has_range_or_allowed_values(condition: StrategyRuleCondition) -> bool:
        return any(
            value is not None
            for value in (condition.lower_bound, condition.upper_bound, condition.allowed_values)
        )

    def _has_invalid_between_operands(self, condition: StrategyRuleCondition) -> bool:
        lower_bound = condition.lower_bound
        upper_bound = condition.upper_bound
        if (
            lower_bound is None
            or upper_bound is None
            or condition.expected_value is not None
            or condition.allowed_values is not None
        ):
            return True
        return self._invalid_between_bounds(lower_bound, upper_bound)

    @staticmethod
    def _has_invalid_in_operands(condition: StrategyRuleCondition) -> bool:
        return (
            condition.allowed_values is None
            or not condition.allowed_values.is_collection
            or condition.expected_value is not None
            or condition.lower_bound is not None
            or condition.upper_bound is not None
        )

    @staticmethod
    def _invalid_between_bounds(
        lower_bound: StrategyRuleValue,
        upper_bound: StrategyRuleValue,
    ) -> bool:
        lower = lower_bound.value
        upper = upper_bound.value
        if not lower_bound.is_scalar or not upper_bound.is_scalar:
            return True
        if isinstance(lower, bool) or isinstance(upper, bool):
            return True
        if isinstance(lower, Decimal) and isinstance(upper, Decimal):
            return lower > upper
        if isinstance(lower, str) and isinstance(upper, str):
            return lower > upper
        return True

    @staticmethod
    def _field_ref_contains_forbidden_token(field_ref: str) -> bool:
        tokens = field_ref.lower().replace("-", "_").replace(".", "_").split("_")
        return any(token in {"buy", "sell", "order", "broker", "execute"} for token in tokens)

    @staticmethod
    def _status_for(
        issues: list[StrategyRuleSetValidationIssue],
    ) -> StrategyRuleSetValidationStatus:
        if not issues:
            return StrategyRuleSetValidationStatus.VALID
        if all(issue.severity == StrategyRuleSeverity.WARNING for issue in issues):
            return StrategyRuleSetValidationStatus.WARNING
        return StrategyRuleSetValidationStatus.INVALID

    def _invalid_operands_issue(self, rule: StrategyRuleSpec) -> StrategyRuleSetValidationIssue:
        return self._issue(
            code=StrategyRuleSetValidationIssueCode.INVALID_OPERATOR_OPERANDS,
            message="Rule operator operands are structurally invalid.",
            rule=rule,
            field_ref=rule.condition.field_ref,
        )

    @staticmethod
    def _issue(
        *,
        code: StrategyRuleSetValidationIssueCode,
        message: str,
        rule: StrategyRuleSpec | None = None,
        field_ref: str | None = None,
    ) -> StrategyRuleSetValidationIssue:
        return StrategyRuleSetValidationIssue(
            code=code,
            message=message,
            rule_id=rule.rule_id if rule is not None else None,
            field_ref=field_ref,
            severity=StrategyRuleSeverity.BLOCKING,
        )
```

## Full Contents Of Changed Test Files

### `tests/unit/test_strategy_ruleset_validation_foundation.py`

```python
from datetime import UTC, datetime, timedelta, timezone

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
from app.domain.entities.strategy_validation import (
    StrategyRuleSetValidationIssue,
    StrategyRuleSetValidationIssueCode,
    StrategyRuleSetValidationReport,
    StrategyRuleSetValidationStatus,
)
from app.domain.strategy_ruleset_validator import StrategyRuleSetValidator

CREATED_AT = datetime(2026, 7, 18, 9, 0, tzinfo=UTC)
CHECKED_AT = datetime(2026, 7, 18, 10, 0, tzinfo=UTC)


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
        "description": "Require deterministic data-quality structure.",
    }
    values.update(overrides)
    return StrategyRuleSpec(**values)


def _ruleset(**overrides: object) -> StrategyRuleSet:
    values: dict[str, object] = {
        "ruleset_version": "phase4c-ruleset-v1",
        "strategy_version": "future-strategy-validation-v1",
        "name": "Future strategy ruleset validation",
        "description": "Validation-only ruleset.",
        "created_at": CREATED_AT,
        "rules": (
            _rule("data_quality.complete"),
            _rule(
                "time_filter.session_exists",
                category=StrategyRuleCategory.TIME_FILTER,
                condition=_condition(
                    field_ref="time_filter.session",
                    operator=StrategyRuleOperator.EXISTS,
                    expected_value=None,
                ),
            ),
        ),
    }
    values.update(overrides)
    return StrategyRuleSet(**values)


def _validate(ruleset: StrategyRuleSet) -> StrategyRuleSetValidationReport:
    return StrategyRuleSetValidator().validate(ruleset, CHECKED_AT)


def _codes(
    report: StrategyRuleSetValidationReport,
) -> tuple[StrategyRuleSetValidationIssueCode, ...]:
    return tuple(issue.code for issue in report.issues)


def test_project_phase_is_phase4c_strategy_ruleset_validation_foundation() -> None:
    assert constants.PROJECT_PHASE == "phase_4c_strategy_ruleset_validation_foundation"


def test_validation_issue_and_report_models_are_immutable() -> None:
    report = _validate(_ruleset())

    with pytest.raises(ValidationError):
        report.status = StrategyRuleSetValidationStatus.INVALID
    with pytest.raises(ValidationError):
        StrategyRuleSetValidationIssue(
            code=StrategyRuleSetValidationIssueCode.RULE_ENABLED,
            message="message",
            severity=StrategyRuleSeverity.BLOCKING,
        ).message = "changed"


def test_validation_report_normalizes_checked_at_to_utc() -> None:
    checked_at = datetime(2026, 7, 18, 12, 0, tzinfo=timezone(timedelta(hours=2)))
    report = StrategyRuleSetValidator().validate(_ruleset(), checked_at)

    assert report.checked_at == CHECKED_AT


def test_clean_disabled_ruleset_validates_as_valid() -> None:
    report = _validate(_ruleset())

    assert report.status == StrategyRuleSetValidationStatus.VALID
    assert report.issues == ()
    assert report.rule_count == 2
    assert report.enabled_rule_count == 0


def test_enabled_ruleset_validates_as_invalid() -> None:
    report = _validate(_ruleset(enabled=True))

    assert report.status == StrategyRuleSetValidationStatus.INVALID
    assert StrategyRuleSetValidationIssueCode.RULESET_ENABLED in _codes(report)


def test_enabled_rule_validates_as_invalid() -> None:
    report = _validate(_ruleset(rules=(_rule(enabled=True),)))

    assert report.status == StrategyRuleSetValidationStatus.INVALID
    assert report.enabled_rule_count == 1
    assert StrategyRuleSetValidationIssueCode.RULE_ENABLED in _codes(report)


def test_unknown_field_ref_validates_as_invalid() -> None:
    report = _validate(
        _ruleset(
            rules=(
                _rule(
                    condition=_condition(field_ref="unknown_context.value"),
                ),
            )
        )
    )

    assert report.status == StrategyRuleSetValidationStatus.INVALID
    assert StrategyRuleSetValidationIssueCode.UNKNOWN_FIELD_REF in _codes(report)


def test_category_field_ref_mismatch_validates_as_invalid() -> None:
    report = _validate(
        _ruleset(
            rules=(
                _rule(
                    category=StrategyRuleCategory.DATA_QUALITY,
                    condition=_condition(field_ref="market_context.regime"),
                ),
            )
        )
    )

    assert report.status == StrategyRuleSetValidationStatus.INVALID
    assert StrategyRuleSetValidationIssueCode.CATEGORY_FIELD_MISMATCH in _codes(report)


def test_forbidden_execution_language_validates_as_invalid() -> None:
    report = _validate(
        _ruleset(rules=(_rule(description="Never buy or sell from a rule specification."),))
    )

    assert report.status == StrategyRuleSetValidationStatus.INVALID
    assert StrategyRuleSetValidationIssueCode.FORBIDDEN_EXECUTION_LANGUAGE in _codes(report)


def test_forbidden_scoring_language_validates_as_invalid() -> None:
    report = _validate(_ruleset(rules=(_rule(warnings=("setup_score is not allowed here",)),)))

    assert report.status == StrategyRuleSetValidationStatus.INVALID
    assert StrategyRuleSetValidationIssueCode.FORBIDDEN_SCORING_LANGUAGE in _codes(report)


def test_forbidden_confidence_language_validates_as_invalid() -> None:
    report = _validate(
        _ruleset(rules=(_rule(description="confidence and OpenAI language are forbidden."),))
    )

    assert report.status == StrategyRuleSetValidationStatus.INVALID
    assert StrategyRuleSetValidationIssueCode.FORBIDDEN_CONFIDENCE_LANGUAGE in _codes(report)


def test_forbidden_field_ref_validates_as_invalid() -> None:
    report = _validate(
        _ruleset(
            rules=(
                _rule(
                    category=StrategyRuleCategory.RISK_GUARD,
                    condition=_condition(field_ref="risk_guard.broker_state"),
                ),
            )
        )
    )

    assert report.status == StrategyRuleSetValidationStatus.INVALID
    assert StrategyRuleSetValidationIssueCode.FORBIDDEN_FIELD_REF in _codes(report)


def test_invalid_operator_operands_validate_as_invalid_when_constructed_unsafely() -> None:
    unsafe_condition = StrategyRuleCondition.model_construct(
        field_ref="data_quality.market_data_complete",
        operator=StrategyRuleOperator.EXISTS,
        expected_value=StrategyRuleValue(value=True),
        lower_bound=None,
        upper_bound=None,
        allowed_values=None,
    )
    unsafe_rule = StrategyRuleSpec.model_construct(
        rule_id="unsafe.operands",
        category=StrategyRuleCategory.DATA_QUALITY,
        severity=StrategyRuleSeverity.REQUIRED,
        condition=unsafe_condition,
        description="Unsafe constructed rule.",
        enabled=False,
        warnings=(),
    )
    unsafe_ruleset = StrategyRuleSet.model_construct(
        ruleset_version="phase4c-ruleset-v1",
        strategy_version="future-strategy-validation-v1",
        name="Unsafe constructed ruleset",
        description=None,
        created_at=CREATED_AT,
        rules=(unsafe_rule,),
        enabled=False,
        fingerprint=None,
    )

    report = _validate(unsafe_ruleset)

    assert report.status == StrategyRuleSetValidationStatus.INVALID
    assert StrategyRuleSetValidationIssueCode.INVALID_OPERATOR_OPERANDS in _codes(report)


def test_empty_ruleset_and_duplicate_rule_ids_remain_model_level_rejections() -> None:
    with pytest.raises(ValidationError):
        _ruleset(rules=())
    with pytest.raises(ValidationError):
        _ruleset(rules=(_rule("duplicate.rule"), _rule("duplicate.rule")))


def test_validation_report_is_not_actionable() -> None:
    assert _validate(_ruleset()).is_actionable is False


def test_validation_report_serializes_deterministically_and_round_trips() -> None:
    report = _validate(_ruleset())
    same_report = _validate(_ruleset(rules=tuple(reversed(_ruleset().rules))))

    assert report.deterministic_json() == same_report.deterministic_json()
    assert (
        StrategyRuleSetValidationReport.model_validate_json(report.deterministic_json()) == report
    )


def test_validation_report_fingerprint_is_deterministic() -> None:
    report = _validate(_ruleset())
    same_report = _validate(_ruleset(rules=tuple(reversed(_ruleset().rules))))

    assert report.fingerprint_sha256() == same_report.fingerprint_sha256()
    assert len(report.fingerprint_sha256()) == 64


def test_validation_report_fingerprint_changes_when_issue_content_changes() -> None:
    report = _validate(_ruleset(rules=(_rule(description="buy is forbidden"),)))
    changed = _validate(_ruleset(rules=(_rule(warnings=("setup_score is forbidden",)),)))

    assert report.fingerprint_sha256() != changed.fingerprint_sha256()


def test_validation_issue_ordering_is_deterministic() -> None:
    issues = (
        StrategyRuleSetValidationIssue(
            code=StrategyRuleSetValidationIssueCode.RULE_ENABLED,
            message="b",
            rule_id="b.rule",
            field_ref="data_quality.b",
            severity=StrategyRuleSeverity.BLOCKING,
        ),
        StrategyRuleSetValidationIssue(
            code=StrategyRuleSetValidationIssueCode.CATEGORY_FIELD_MISMATCH,
            message="a",
            rule_id="a.rule",
            field_ref="market_context.a",
            severity=StrategyRuleSeverity.BLOCKING,
        ),
    )
    report = StrategyRuleSetValidationReport(
        ruleset_version="phase4c-ruleset-v1",
        strategy_version="future-strategy-validation-v1",
        ruleset_name="Ordered report",
        status=StrategyRuleSetValidationStatus.INVALID,
        checked_at=CHECKED_AT,
        issues=issues,
        rule_count=2,
        enabled_rule_count=1,
    )

    assert _codes(report) == (
        StrategyRuleSetValidationIssueCode.CATEGORY_FIELD_MISMATCH,
        StrategyRuleSetValidationIssueCode.RULE_ENABLED,
    )


def test_validator_does_not_mutate_input_ruleset() -> None:
    ruleset = _ruleset()
    before = ruleset.deterministic_json()

    _validate(ruleset)

    assert ruleset.deterministic_json() == before


def test_validator_accepts_only_strategy_ruleset_objects() -> None:
    with pytest.raises(TypeError):
        StrategyRuleSetValidator().validate(object(), CHECKED_AT)  # type: ignore[arg-type]
```

### `tests/contract/test_safety_boundaries.py`

```python
import inspect
from datetime import UTC, datetime
from pathlib import Path

import pytest

import app.domain.strategy_ruleset_validator as strategy_ruleset_validator_module
from app.adapters.disabled import (
    DisabledEconomicCalendarProvider,
    DisabledLLMProvider,
    DisabledMarketDataProvider,
)
from app.core.enums import Decision
from app.core.exceptions import IntegrationDisabledError
from app.domain.entities import Timeframe, signal_contract, strategy_rules, strategy_validation
from app.domain.strategy_ruleset_validator import StrategyRuleSetValidator
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
PHASE_4C_VALIDATION_OBJECTS = (
    strategy_validation.StrategyRuleSetValidationIssue,
    strategy_validation.StrategyRuleSetValidationIssueCode,
    strategy_validation.StrategyRuleSetValidationReport,
    strategy_validation.StrategyRuleSetValidationStatus,
    StrategyRuleSetValidator,
)
PHASE_4C_FORBIDDEN_RUNTIME_IMPORTS = (
    "app.domain.entities.market_data",
    "app.domain.entities.context",
    "app.domain.entities.analysis",
    "app.domain.entities.features",
    "app.domain.entities.signal_contract",
    "app.adapters",
    "app.persistence",
    "app.telegram",
    "app.scheduler",
    "sqlalchemy",
    "fastapi",
    "httpx",
    "openai",
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


def test_phase4c_validation_objects_are_domain_only() -> None:
    offenders: list[str] = []
    texts = [inspect.getsource(source_object) for source_object in PHASE_4C_VALIDATION_OBJECTS]
    for index, text in enumerate(texts):
        lowered = text.lower()
        for term in PHASE_4C_FORBIDDEN_RUNTIME_IMPORTS:
            if term.lower() in lowered:
                offenders.append(f"phase4c-validation-{index}: {term}")

    assert offenders == []


def test_phase4c_validator_signature_has_no_market_or_runtime_inputs() -> None:
    signature = inspect.signature(StrategyRuleSetValidator.validate)

    assert tuple(signature.parameters) == ("self", "ruleset", "checked_at")


def test_phase4c_validator_module_does_not_import_runtime_dependencies() -> None:
    source = inspect.getsource(strategy_ruleset_validator_module).lower()
    import_lines = tuple(
        line
        for line in source.splitlines()
        if line.startswith("import ") or line.startswith("from ")
    )

    offenders = [
        term
        for term in PHASE_4C_FORBIDDEN_RUNTIME_IMPORTS
        if any(term.lower() in line for line in import_lines)
    ]

    assert offenders == []


def test_phase4c_does_not_add_validation_api_routes() -> None:
    route_files = tuple(Path("app/api/routes").glob("*.py"))
    offenders = [
        str(file_path)
        for file_path in route_files
        if "validation" in file_path.name.lower()
        or "ruleset" in file_path.name.lower()
        or "StrategyRuleSetValidationReport" in file_path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_phase4c_does_not_add_telegram_validation_or_signal_handlers() -> None:
    source = Path("app/telegram/commands.py").read_text(encoding="utf-8")

    assert "validation_command" not in source
    assert "ruleset_command" not in source
    assert 'CommandHandler("validate"' not in source
    assert 'CommandHandler("signal"' not in source
    assert "StrategyRuleSetValidationReport" not in source


def test_phase4c_does_not_add_scheduler_validation_or_signal_jobs() -> None:
    scheduler_text = "\n".join(
        file_path.read_text(encoding="utf-8") for file_path in Path("app/scheduler").glob("*.py")
    )

    assert "StrategyRuleSetValidator" not in scheduler_text
    assert "StrategyRuleSetValidationReport" not in scheduler_text
    assert "ruleset_validation_job" not in scheduler_text
    assert "generate_signal" not in scheduler_text


def test_phase4c_does_not_add_strategy_validation_service() -> None:
    service_files = tuple(Path("app/services").glob("*.py"))
    offenders = [
        str(file_path)
        for file_path in service_files
        if "validation" in file_path.name.lower()
        or "ruleset" in file_path.name.lower()
        or "StrategyRuleSetValidator" in file_path.read_text(encoding="utf-8")
        or "StrategyRuleSetValidationReport" in file_path.read_text(encoding="utf-8")
    ]

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


def test_project_phase_has_advanced_to_phase4c_strategy_ruleset_validation_foundation() -> None:
    assert constants.PROJECT_PHASE == "phase_4c_strategy_ruleset_validation_foundation"


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


def test_project_phase_has_advanced_to_phase4c_strategy_ruleset_validation_foundation() -> None:
    assert constants.PROJECT_PHASE == "phase_4c_strategy_ruleset_validation_foundation"


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
- `docs/phase4c-verification-report.md`
- `docs/chatgpt-verification-packet.md`
