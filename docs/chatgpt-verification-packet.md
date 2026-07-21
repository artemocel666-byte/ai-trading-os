# ChatGPT Verification Packet - Phase 5

Generated: 2026-07-20T21:54:48Z

## Scope And Safety

Current phase:

```text
PROJECT_PHASE = phase_5_manual_review_layer_foundation
STRATEGY_IMPLEMENTED = False
REAL_TRADING_ENABLED = False
```

Phase 5 is the read-only Manual Review Layer foundation. It consumes already-created immutable,
disabled/non-actionable Phase 4G/4F/4E report artifacts and adds deterministic manual review models,
a report builder, stdout text/JSON rendering, an authorized Telegram `/review` command, and
in-memory comparison/completeness summaries.

The Phase 5 builder never invokes the Phase 4 evaluator or composer. It does not read market data,
call providers, open a database/session/UoW, persist reports, write runtime files, call Telegram,
register scheduler jobs, or call AI/OpenAI/LLM services. Local CLI and Telegram review build from
the Phase 4E disabled registry report because no Phase 4G persistence/retrieval boundary exists. A
caller may inject an already-built Phase 4G `PipelineDecisionReport` for read-only presentation.

Phase 3J is absent. Later phases were not started. No strategy engine, decision engine, new rule
evaluation, signal generation, setup scoring, confidence scoring, AI agent, OpenAI call, broker API,
paper trading, order execution, live trading, or real trading was added. No migration was added.

Phase 5 is uncommitted at packet generation time.

## Git Metadata

- Branch: `main`
- Current commit: `f898c0a674c09909185e92d063ca03652111ba70`
- Commit summary: `f898c0a PHASES 4F. 4G(Additional) DONE`
- Phase 5 changes: uncommitted

Backup created before edits:

- Branch: `backup/codex-before-phase5-20260720T212316Z`
- Tag: `codex-backup-before-phase5-20260720T212316Z`
- Bundle: `/Users/artem.otsel/Documents/ai-trading-os-backups/ai-trading-os-codex-before-phase5-20260720T212316Z.bundle`
- Backup commit: `f898c0a674c09909185e92d063ca03652111ba70`

`git status --short`, captured immediately before the final packet rewrite:

```text
 M AGENTS.md
 M PLANS.md
 M README.md
 M app/core/constants.py
 M app/domain/entities/__init__.py
 M app/telegram/commands.py
 M docs/operations.md
 M tests/contract/test_safety_boundaries.py
 M tests/unit/test_disabled_pipeline_report_shell_foundation.py
 M tests/unit/test_signal_contract_foundation.py
 M tests/unit/test_strategy_rule_specification_foundation.py
 M tests/unit/test_strategy_ruleset_registry_foundation.py
 M tests/unit/test_strategy_ruleset_validation_foundation.py
 M tests/unit/test_telegram_commands.py
?? app/domain/entities/manual_review.py
?? app/domain/manual_review_comparison.py
?? app/domain/manual_review_report_builder.py
?? app/telegram/manual_review_formatter.py
?? docs/phase5-verification-report.md
?? scripts/manual_review_report.py
?? tests/unit/test_manual_review_cli.py
?? tests/unit/test_manual_review_foundation.py
```

`docs/chatgpt-verification-packet.md` becomes modified by this final rewrite.

`git diff --stat`, captured immediately before the final packet rewrite (Git does not include
untracked files in this statistic):

```text
 AGENTS.md                                          |  22 ++-
 PLANS.md                                           |  16 +-
 README.md                                          |  34 +++-
 app/core/constants.py                              |   2 +-
 app/domain/entities/__init__.py                    |  18 +++
 app/telegram/commands.py                           |  23 ++-
 docs/operations.md                                 |  26 +++-
 tests/contract/test_safety_boundaries.py           | 173 +++++++++++++++++++++
 ...st_disabled_pipeline_report_shell_foundation.py |   2 +-
 tests/unit/test_signal_contract_foundation.py      |   2 +-
 .../test_strategy_rule_specification_foundation.py |   2 +-
 .../test_strategy_ruleset_registry_foundation.py   |   2 +-
 .../test_strategy_ruleset_validation_foundation.py |   2 +-
 tests/unit/test_telegram_commands.py               |  61 +++++++-
 14 files changed, 361 insertions(+), 24 deletions(-)
```

## Created Files

- `app/domain/entities/manual_review.py`
- `app/domain/manual_review_comparison.py`
- `app/domain/manual_review_report_builder.py`
- `app/telegram/manual_review_formatter.py`
- `docs/phase5-verification-report.md`
- `scripts/manual_review_report.py`
- `tests/unit/test_manual_review_cli.py`
- `tests/unit/test_manual_review_foundation.py`

## Modified Files

- `AGENTS.md`
- `PLANS.md`
- `README.md`
- `app/core/constants.py`
- `app/domain/entities/__init__.py`
- `app/telegram/commands.py`
- `docs/chatgpt-verification-packet.md`
- `docs/operations.md`
- `tests/contract/test_safety_boundaries.py`
- `tests/unit/test_disabled_pipeline_report_shell_foundation.py`
- `tests/unit/test_signal_contract_foundation.py`
- `tests/unit/test_strategy_rule_specification_foundation.py`
- `tests/unit/test_strategy_ruleset_registry_foundation.py`
- `tests/unit/test_strategy_ruleset_validation_foundation.py`
- `tests/unit/test_telegram_commands.py`

## Migration Contents

No migration file was created or modified. Existing migrations remain:

```text
migrations/versions/0001_foundation_schema.py
migrations/versions/0002_phase2_data_constraints.py
migrations/versions/0003_phase3i_scheduled_digest_deliveries.py
```

Docker Alembic current confirms the existing head:

```text
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
0003_phase3i_digest_audit (head)
```

## Exact Host Verification Outputs

The installed executable was invoked as `/Users/artem.otsel/.local/bin/uv` because `uv` is not on
the non-interactive shell PATH. This is the same installed uv runtime.

### `uv lock --check`

Exit code: `0`

```text
Resolved 46 packages in 15ms
```

### `uv sync`

Exit code: `0`

```text
Resolved 46 packages in 3ms
Checked 43 packages in 7ms
```

### `uv run ruff format --check .`

Exit code: `0`

```text
137 files already formatted
```

### `uv run ruff check .`

Exit code: `0`

```text
All checks passed!
```

### `uv run mypy app`

Exit code: `0`

```text
Success: no issues found in 94 source files
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
collected 447 items

tests/contract/test_agent_contracts.py ......                            [  1%]
tests/contract/test_api_error_schema.py .                                [  1%]
tests/contract/test_architecture_boundaries.py ..                        [  2%]
tests/contract/test_provider_contracts.py .............................. [  8%]
...............................                                          [ 15%]
tests/contract/test_safety_boundaries.py ............................... [ 22%]
.................................................                        [ 33%]
tests/integration/test_database_and_api.py sssssss                       [ 35%]
tests/unit/test_analysis_snapshot_foundation.py ..........               [ 37%]
tests/unit/test_context_engine_foundation.py .............               [ 40%]
tests/unit/test_data_quality_foundation.py ...                           [ 40%]
tests/unit/test_disabled_pipeline_report_shell_foundation.py ........... [ 43%]
......                                                                   [ 44%]
tests/unit/test_domain_market_models.py ..................               [ 48%]
tests/unit/test_errors_and_redaction.py .......                          [ 50%]
tests/unit/test_feature_engine_foundation.py ...........                 [ 52%]
tests/unit/test_internal_api_key.py ....                                 [ 53%]
tests/unit/test_manual_review_cli.py .....                               [ 54%]
tests/unit/test_manual_review_foundation.py ............................ [ 61%]
............                                                             [ 63%]
tests/unit/test_readiness_scheduler_foundation.py .........              [ 65%]
tests/unit/test_scheduled_digest_delivery_foundation.py ...........      [ 68%]
tests/unit/test_settings.py .........                                    [ 70%]
tests/unit/test_signal_contract_foundation.py ............               [ 72%]
tests/unit/test_snapshot_versioning_foundation.py .....                  [ 74%]
tests/unit/test_strategy_decision_composition_foundation.py .....        [ 75%]
tests/unit/test_strategy_rule_evaluation_foundation.py ..............    [ 78%]
tests/unit/test_strategy_rule_specification_foundation.py .............. [ 81%]
...........                                                              [ 83%]
tests/unit/test_strategy_ruleset_registry_foundation.py ................ [ 87%]
.                                                                        [ 87%]
tests/unit/test_strategy_ruleset_validation_foundation.py .............. [ 90%]
.......                                                                  [ 92%]
tests/unit/test_system_state_service.py .....                            [ 93%]
tests/unit/test_telegram_commands.py ...........                         [ 95%]
tests/unit/test_telegram_policy.py .....                                 [ 97%]
tests/unit/test_time.py ...                                              [ 97%]
tests/unit/test_unit_of_work_lifecycle.py ......                         [ 99%]
tests/unit/test_value_objects_and_enums.py ....                          [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /Users/artem.otsel/Documents/ai-trading-os/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================== 440 passed, 7 skipped, 1 warning in 1.28s ===================
```

### `uv run python scripts/security_check.py`

Exit code: `0`

```text
<no stdout or stderr>
```

## Exact CLI Outputs

### `uv run python scripts/manual_review_report.py`

Exit code: `0`

```text
READ-ONLY MANUAL REVIEW
NO TRADING SIGNAL
NO BUY/SELL RECOMMENDATION
NON-ACTIONABLE
Status: READ_ONLY
Project phase: phase_5_manual_review_layer_foundation
Created at: 2026-07-20T21:54:43.486267Z
Source fingerprint: 198ba96ffe40d63e3dc5f7364123c3e5f32117d3fa90ea19117d9df9358c7128
[AUDIT_EXPORT] Audit export: Source audit metadata is available.
- Source fingerprint: 198ba96ffe40d63e3dc5f7364123c3e5f32117d3fa90ea19117d9df9358c7128.
- Source content was summarized without persistence or external calls.
[BLOCKERS] Blockers: Existing disabled report contains 1 blocker(s).
- PIPELINE_DISABLED: The Phase 4E pipeline report shell is disabled.
[PIPELINE_STATE] Pipeline state: Existing source status: DISABLED.
- Registered items: 3.
- Valid items: 3.
- Invalid items: 0.
[PROJECT_STATE] Project state: Phase 5 manual review is read-only and disabled for runtime action.
- Current project phase: phase_5_manual_review_layer_foundation.
- Source project phase: phase_5_manual_review_layer_foundation.
- Source report type: DisabledPipelineReport.
[QUALITY_SUMMARY] Quality summary: All required review sections are present.
- Required sections present: 7/7.
- Review issues recorded: 0.
- Runtime enabled: false.
- Actionable output: false.
[REGISTRY_SUMMARY] Registry summary: Phase 4E registry counts are available for manual inspection.
- Total registry items: 3.
- Valid registry items: 3.
- Invalid registry items: 0.
- Registry snapshot fingerprint: ad67867d0b855415c84b83b20e281f54229adc6e30f646ff590f34968e1be623.
[SAFETY_CONFIRMATIONS] Safety confirmations: The manual review layer is disabled and non-actionable.
- Runtime enabled: false.
- Actionable output: false.
- NO TRADING SIGNAL.
- No external provider, database, scheduler, or messaging call was made by the builder.
[TELEGRAM_READINESS] Telegram readiness: Manual authorized review delivery is available without automatic alerts.
- The review command returns a short read-only summary.
- No scheduled delivery is registered.
Issues: none
```

### `uv run python scripts/manual_review_report.py --format text`

Exit code: `0`

```text
READ-ONLY MANUAL REVIEW
NO TRADING SIGNAL
NO BUY/SELL RECOMMENDATION
NON-ACTIONABLE
Status: READ_ONLY
Project phase: phase_5_manual_review_layer_foundation
Created at: 2026-07-20T21:54:45.950285Z
Source fingerprint: fd6fce0cdc390ef3f639e6b806a390e4e91da18f2e96f48d7d4ae339045cab74
[AUDIT_EXPORT] Audit export: Source audit metadata is available.
- Source fingerprint: fd6fce0cdc390ef3f639e6b806a390e4e91da18f2e96f48d7d4ae339045cab74.
- Source content was summarized without persistence or external calls.
[BLOCKERS] Blockers: Existing disabled report contains 1 blocker(s).
- PIPELINE_DISABLED: The Phase 4E pipeline report shell is disabled.
[PIPELINE_STATE] Pipeline state: Existing source status: DISABLED.
- Registered items: 3.
- Valid items: 3.
- Invalid items: 0.
[PROJECT_STATE] Project state: Phase 5 manual review is read-only and disabled for runtime action.
- Current project phase: phase_5_manual_review_layer_foundation.
- Source project phase: phase_5_manual_review_layer_foundation.
- Source report type: DisabledPipelineReport.
[QUALITY_SUMMARY] Quality summary: All required review sections are present.
- Required sections present: 7/7.
- Review issues recorded: 0.
- Runtime enabled: false.
- Actionable output: false.
[REGISTRY_SUMMARY] Registry summary: Phase 4E registry counts are available for manual inspection.
- Total registry items: 3.
- Valid registry items: 3.
- Invalid registry items: 0.
- Registry snapshot fingerprint: 779b8cff274434facb987ea6e80ad5a4b63e0534b140d946ca09f4b7a51a6e2e.
[SAFETY_CONFIRMATIONS] Safety confirmations: The manual review layer is disabled and non-actionable.
- Runtime enabled: false.
- Actionable output: false.
- NO TRADING SIGNAL.
- No external provider, database, scheduler, or messaging call was made by the builder.
[TELEGRAM_READINESS] Telegram readiness: Manual authorized review delivery is available without automatic alerts.
- The review command returns a short read-only summary.
- No scheduled delivery is registered.
Issues: none
```

### `uv run python scripts/manual_review_report.py --format json`

Exit code: `0`

```json
{"created_at":"2026-07-20T21:54:48.082178Z","enabled_for_runtime":false,"fingerprint":null,"is_actionable":false,"issues":[],"project_phase":"phase_5_manual_review_layer_foundation","report_version":"phase5-manual-review-v1","sections":[{"code":"AUDIT_EXPORT","details":["Source fingerprint: 4fc74ff94dd3bc3ebc1fa3d2ca6674b431e4230e1596bb9e49014fd6a74584ce.","Source content was summarized without persistence or external calls."],"is_actionable":false,"issue_count":0,"summary":"Source audit metadata is available.","title":"Audit export"},{"code":"BLOCKERS","details":["PIPELINE_DISABLED: The Phase 4E pipeline report shell is disabled."],"is_actionable":false,"issue_count":0,"summary":"Existing disabled report contains 1 blocker(s).","title":"Blockers"},{"code":"PIPELINE_STATE","details":["Registered items: 3.","Valid items: 3.","Invalid items: 0."],"is_actionable":false,"issue_count":0,"summary":"Existing source status: DISABLED.","title":"Pipeline state"},{"code":"PROJECT_STATE","details":["Current project phase: phase_5_manual_review_layer_foundation.","Source project phase: phase_5_manual_review_layer_foundation.","Source report type: DisabledPipelineReport."],"is_actionable":false,"issue_count":0,"summary":"Phase 5 manual review is read-only and disabled for runtime action.","title":"Project state"},{"code":"QUALITY_SUMMARY","details":["Required sections present: 7/7.","Review issues recorded: 0.","Runtime enabled: false.","Actionable output: false."],"is_actionable":false,"issue_count":0,"summary":"All required review sections are present.","title":"Quality summary"},{"code":"REGISTRY_SUMMARY","details":["Total registry items: 3.","Valid registry items: 3.","Invalid registry items: 0.","Registry snapshot fingerprint: 20984774ce130549552ae96fec7e29f07a7195bbefb913258ea2c432bf70cdac."],"is_actionable":false,"issue_count":0,"summary":"Phase 4E registry counts are available for manual inspection.","title":"Registry summary"},{"code":"SAFETY_CONFIRMATIONS","details":["Runtime enabled: false.","Actionable output: false.","NO TRADING SIGNAL.","No external provider, database, scheduler, or messaging call was made by the builder."],"is_actionable":false,"issue_count":0,"summary":"The manual review layer is disabled and non-actionable.","title":"Safety confirmations"},{"code":"TELEGRAM_READINESS","details":["The review command returns a short read-only summary.","No scheduled delivery is registered."],"is_actionable":false,"issue_count":0,"summary":"Manual authorized review delivery is available without automatic alerts.","title":"Telegram readiness"}],"source_fingerprint":"4fc74ff94dd3bc3ebc1fa3d2ca6674b431e4230e1596bb9e49014fd6a74584ce","status":"READ_ONLY"}
```

## Docker And PostgreSQL Outputs

### `docker compose build`

Exit code: `0`. BuildKit completed all steps and reported:

```text
Image ai-trading-os-bot Built
Image ai-trading-os-migrate Built
Image ai-trading-os-worker Built
Image ai-trading-os-api Built
```

### `docker compose up -d postgres`

Exit code: `0`

```text
Network ai-trading-os_default Created
Container ai-trading-os-postgres-1 Created
Container ai-trading-os-postgres-1 Started
```

The following migration command confirmed the container was healthy.

### `docker compose run --rm migrate alembic current`

Exit code: `0`

```text
Container ai-trading-os-postgres-1 Running
Container ai-trading-os-postgres-1 Waiting
Container ai-trading-os-postgres-1 Healthy
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
0003_phase3i_digest_audit (head)
```

### `docker compose run --rm migrate alembic check`

Exit code: `0`

```text
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

### Test database migration

Command:

```text
docker compose run --rm -e DATABASE_URL=postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os_test migrate alembic upgrade head
```

Exit code: `0`

```text
Container ai-trading-os-postgres-1 Running
Container ai-trading-os-postgres-1 Waiting
Container ai-trading-os-postgres-1 Healthy
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

### Docker integration run 1

Exit code: `0`

```text
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
========================= 7 passed, 1 warning in 0.42s =========================
```

### Docker integration run 2, same database without cleanup

Exit code: `0`

```text
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
========================= 7 passed, 1 warning in 0.44s =========================
```

The two runs used the same `ai_trading_os_test` database and no cleanup/drop command ran between
them.

### `docker compose config`

Exit code: `0`. The command rendered all four application services plus PostgreSQL successfully.
Its raw output expanded the local `.env`, including a real Telegram token and IDs. Those values are
intentionally redacted and are not copied into this packet. Verified safety/default fields were:

```text
CALENDAR_ENABLED: "false"
MARKET_DATA_ENABLED: "false"
OPENAI_ENABLED: "false"
SCAN_ENABLED: "false"
REQUIRE_INTEGRATION_TESTS: "false"
TELEGRAM_BOT_TOKEN: <redacted>
TELEGRAM_ALLOWED_USER_ID: <redacted>
TELEGRAM_ALLOWED_CHAT_ID: <redacted>
```

The local `.env` overrides `TELEGRAM_ENABLED=true`; repository defaults remain disabled in
`.env.example`. Redaction is the only intentional deviation from verbatim command output.

## Skipped And Unavailable Checks

- The normal host `uv run pytest` skipped seven PostgreSQL integration tests because
  `REQUIRE_INTEGRATION_TESTS` was not enabled. The same seven tests passed in Docker twice against
  the same test database.
- The API service was not started during this task, so `/ready` and `/api/v1/system/status` were not
  rerun.
- No Alembic revision generation ran because Phase 5 has no persistence or schema changes.
- No later-phase runtime check was attempted.

## Remaining Risks

- CLI and Telegram local review intentionally use the Phase 4E disabled report until a safe Phase
  4G read-only retrieval boundary exists. Injected pre-built Phase 4G reports are supported.
- The existing Starlette `TestClient` deprecation warning remains.
- `docker compose config` expanded a real local Telegram token in terminal output. The packet
  redacts it; the token should be rotated as a precaution and raw Compose output must not be shared.
- The PostgreSQL container remains running after verification.

## Traceability

| Requirement | Implementation | Tests | Verification |
| --- | --- | --- | --- |
| Phase 5 project state and safety flags | `app/core/constants.py` | `test_manual_review_foundation.py`, safety contracts | Passed |
| Immutable read-only report model | `app/domain/entities/manual_review.py` | model immutability/validation tests | Passed |
| UTC normalization and deterministic ordering | `app/domain/entities/manual_review.py` | UTC, section, issue ordering tests | Passed |
| Deterministic JSON and SHA-256 | `app/domain/entities/manual_review.py` | serialization/fingerprint tests | Passed |
| Reject runtime/actionability and unsafe text | manual review entity/builder | flag, redaction, safety tests | Passed |
| Consume existing Phase 4G/4E report only | `app/domain/manual_review_report_builder.py` | Phase 4G/4E builder tests | Passed |
| No DB/provider/market/Telegram/AI call in builder | builder imports and safety contracts | architecture/safety tests | Passed |
| stdout-only text/JSON CLI | `scripts/manual_review_report.py` | `test_manual_review_cli.py` | Passed, all CLI commands exit 0 |
| Authorized read-only Telegram command | `app/telegram/commands.py`, formatter | Telegram authorization/output/help/registry tests | Passed |
| Existing `/snapshot` and `/digest` unchanged | existing command handlers | existing Telegram tests | Passed |
| In-memory deterministic comparison | `app/domain/manual_review_comparison.py` | same/changed/incomplete tests | Passed |
| Quality/completeness summary | comparison module | quality summary tests | Passed |
| No file writes, persistence, migration, API route, or scheduler job | CLI/domain/safety tests | safety contracts | Passed |
| Repeatable PostgreSQL integration suite | existing integration isolation | integration file | Passed twice, 7 tests each |
| Phase 3J remains absent | no route file | safety contract | Passed |
| No later phase or trading behavior | all Phase 5 modules | security and safety contracts | Passed |

## Full Contents Of Changed Source Files

The following appendices are exact snapshots from the uncommitted working tree at packet generation
time.

### `app/core/constants.py`

```python
PROJECT_PHASE = "phase_5_manual_review_layer_foundation"
STRATEGY_IMPLEMENTED = False
REAL_TRADING_ENABLED = False

FEATURE_SNAPSHOT_SCHEMA_VERSION = 1
CONTEXT_SNAPSHOT_SCHEMA_VERSION = 1
ANALYSIS_SNAPSHOT_SCHEMA_VERSION = 1

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
from app.domain.entities.manual_review import (
    ManualReviewIssue,
    ManualReviewIssueCode,
    ManualReviewIssueSeverity,
    ManualReviewReport,
    ManualReviewSection,
    ManualReviewSectionCode,
    ManualReviewStatus,
    contains_actionable_trading_text,
)
from app.domain.entities.market_data import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.entities.pipeline_decision import (
    PipelineDecisionReport,
    PipelineDecisionStatus,
    SkippedRuleset,
    SkippedRulesetReason,
)
from app.domain.entities.pipeline_report import (
    DisabledPipelineBlocker,
    DisabledPipelineBlockerCode,
    DisabledPipelineReport,
    DisabledPipelineStatus,
)
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
from app.domain.entities.rule_evaluation import (
    RuleEvaluationResult,
    RuleEvaluationStatus,
    RuleSetEvaluationReport,
    RuleSetEvaluationStatus,
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
from app.domain.entities.strategy_registry import (
    StrategyRuleSetRegistryItem,
    StrategyRuleSetRegistrySnapshot,
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
    "DisabledPipelineBlocker",
    "DisabledPipelineBlockerCode",
    "DisabledPipelineReport",
    "DisabledPipelineStatus",
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
    "ManualReviewIssue",
    "ManualReviewIssueCode",
    "ManualReviewIssueSeverity",
    "ManualReviewReport",
    "ManualReviewSection",
    "ManualReviewSectionCode",
    "ManualReviewStatus",
    "MarketContextSnapshot",
    "MarketFeatureSnapshot",
    "MovingAverageSeries",
    "MovingAverageSummary",
    "PipelineDecisionReport",
    "PipelineDecisionStatus",
    "RangeContextSummary",
    "ReturnDistributionSummary",
    "RuleEvaluationResult",
    "RuleEvaluationStatus",
    "RuleSetEvaluationReport",
    "RuleSetEvaluationStatus",
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
    "SkippedRuleset",
    "SkippedRulesetReason",
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
    "StrategyRuleSetRegistryItem",
    "StrategyRuleSetRegistrySnapshot",
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
    "contains_actionable_trading_text",
    "digest_status_from_analysis",
]
```

### `app/domain/entities/manual_review.py`

```python
import hashlib
import json
import re
from datetime import datetime
from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc


class ManualReviewStatus(StrEnum):
    READ_ONLY = "READ_ONLY"
    BLOCKED = "BLOCKED"
    INCOMPLETE = "INCOMPLETE"


class ManualReviewSectionCode(StrEnum):
    PROJECT_STATE = "PROJECT_STATE"
    PIPELINE_STATE = "PIPELINE_STATE"
    REGISTRY_SUMMARY = "REGISTRY_SUMMARY"
    AUDIT_EXPORT = "AUDIT_EXPORT"
    SAFETY_CONFIRMATIONS = "SAFETY_CONFIRMATIONS"
    BLOCKERS = "BLOCKERS"
    QUALITY_SUMMARY = "QUALITY_SUMMARY"
    TELEGRAM_READINESS = "TELEGRAM_READINESS"


class ManualReviewIssueCode(StrEnum):
    MISSING_AUDIT_EXPORT = "MISSING_AUDIT_EXPORT"
    MISSING_SAFETY_CONFIRMATIONS = "MISSING_SAFETY_CONFIRMATIONS"
    ACTIONABLE_CONTENT_FOUND = "ACTIONABLE_CONTENT_FOUND"
    RUNTIME_ENABLED_FOUND = "RUNTIME_ENABLED_FOUND"
    FINGERPRINT_MISMATCH = "FINGERPRINT_MISMATCH"
    INCOMPLETE_SECTION = "INCOMPLETE_SECTION"
    UNSAFE_TEXT_FOUND = "UNSAFE_TEXT_FOUND"


class ManualReviewIssueSeverity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKING = "BLOCKING"


_UNSAFE_TEXT_PATTERNS = (
    re.compile(r"\bgo\s+(?:long|short)\b", re.IGNORECASE),
    re.compile(r"\b(?:long|short)\s+recommendation\b", re.IGNORECASE),
    re.compile(r"\b(?:signal|recommendation)\b", re.IGNORECASE),
    re.compile(r"\b(?:LONG|SHORT)\b"),
    re.compile(r"\b(?:buy|sell)\b", re.IGNORECASE),
    re.compile(
        r"\b(?:entry|price|target|score|scoring|confidence|broker|order|execute)\b", re.IGNORECASE
    ),
    re.compile(r"\bstop[\s_-]+loss\b", re.IGNORECASE),
    re.compile(r"\btake[\s_-]+profit\b", re.IGNORECASE),
    re.compile(r"\bposition[\s_-]+size\b", re.IGNORECASE),
    re.compile(r"\bsetup[\s_-]+score\b", re.IGNORECASE),
    re.compile(r"\bconfidence[\s_-]+score\b", re.IGNORECASE),
    re.compile(r"\b(?:paper|live|real)[\s_-]+trad(?:e|ing)\b", re.IGNORECASE),
    re.compile(
        r"\b(?:entry_price|stop_loss|take_profit|position_size|setup_score|"
        r"confidence_score|paper_trade|live_trade|real_trade)\b",
        re.IGNORECASE,
    ),
)
_ALLOWED_SAFETY_DISCLAIMERS = (
    "NO BUY/SELL RECOMMENDATION",
    "NO TRADING SIGNAL",
)


def contains_actionable_trading_text(value: str) -> bool:
    filtered = value
    for disclaimer in _ALLOWED_SAFETY_DISCLAIMERS:
        filtered = filtered.replace(disclaimer, "")
    return any(pattern.search(filtered) for pattern in _UNSAFE_TEXT_PATTERNS)


def _normalize_required_text(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be non-empty")
    if contains_actionable_trading_text(normalized):
        raise ValueError(f"{field_name} contains actionable trading text")
    return normalized


class ManualReviewIssue(BaseModel):
    code: ManualReviewIssueCode
    message: str = Field(min_length=1, max_length=1000)
    section_code: ManualReviewSectionCode | None = None
    severity: ManualReviewIssueSeverity

    model_config = ConfigDict(frozen=True)

    @field_validator("message", mode="before")
    @classmethod
    def normalize_message(cls, value: object) -> str:
        return _normalize_required_text(value, "manual review issue message")

    @property
    def sort_key(self) -> tuple[str, str, str, str]:
        return (
            self.code.value,
            self.section_code.value if self.section_code is not None else "",
            self.message,
            self.severity.value,
        )


class ManualReviewSection(BaseModel):
    code: ManualReviewSectionCode
    title: str = Field(min_length=1, max_length=120)
    summary: str = Field(min_length=1, max_length=1000)
    details: tuple[str, ...] = ()
    issue_count: int = Field(default=0, ge=0)
    is_actionable: bool = False

    model_config = ConfigDict(frozen=True)

    @field_validator("title", "summary", mode="before")
    @classmethod
    def normalize_text_fields(cls, value: object) -> str:
        return _normalize_required_text(value, "manual review section text")

    @field_validator("details", mode="before")
    @classmethod
    def normalize_details(cls, value: object) -> tuple[str, ...]:
        if value is None:
            return ()
        if not isinstance(value, list | tuple):
            raise ValueError("manual review section details must be a list or tuple")
        normalized = tuple(
            _normalize_required_text(item, "manual review section detail") for item in value
        )
        return tuple(dict.fromkeys(normalized))

    @model_validator(mode="after")
    def must_remain_non_actionable(self) -> Self:
        if self.is_actionable:
            raise ValueError("manual review sections must remain non-actionable")
        return self


class ManualReviewReport(BaseModel):
    report_version: str = Field(min_length=1, max_length=120)
    project_phase: str = Field(min_length=1, max_length=120)
    created_at: datetime
    status: ManualReviewStatus
    source_fingerprint: str = Field(min_length=64, max_length=64)
    sections: tuple[ManualReviewSection, ...]
    issues: tuple[ManualReviewIssue, ...] = ()
    enabled_for_runtime: bool = False
    is_actionable: bool = False
    fingerprint: str | None = Field(default=None, min_length=64, max_length=64)

    model_config = ConfigDict(frozen=True)

    @field_validator("report_version", "project_phase", mode="before")
    @classmethod
    def normalize_identifiers(cls, value: object) -> str:
        return _normalize_required_text(value, "manual review report identifier")

    @field_validator("created_at")
    @classmethod
    def normalize_created_at(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("sections")
    @classmethod
    def normalize_sections(
        cls,
        value: tuple[ManualReviewSection, ...],
    ) -> tuple[ManualReviewSection, ...]:
        section_codes = [section.code for section in value]
        if len(section_codes) != len(set(section_codes)):
            raise ValueError("manual review section codes must be unique")
        return tuple(sorted(value, key=lambda section: section.code.value))

    @field_validator("issues")
    @classmethod
    def normalize_issues(
        cls,
        value: tuple[ManualReviewIssue, ...],
    ) -> tuple[ManualReviewIssue, ...]:
        unique = {issue.sort_key: issue for issue in value}
        return tuple(unique[key] for key in sorted(unique))

    @model_validator(mode="after")
    def validate_safety_and_status(self) -> Self:
        if self.enabled_for_runtime:
            raise ValueError("manual review reports must remain disabled for runtime use")
        if self.is_actionable:
            raise ValueError("manual review reports must remain non-actionable")

        has_blocking_issue = any(
            issue.severity == ManualReviewIssueSeverity.BLOCKING for issue in self.issues
        )
        if has_blocking_issue and self.status != ManualReviewStatus.BLOCKED:
            raise ValueError("blocking manual review issues require BLOCKED status")
        if self.issues and not has_blocking_issue and self.status != ManualReviewStatus.INCOMPLETE:
            raise ValueError("non-blocking manual review issues require INCOMPLETE status")
        if not self.issues and self.status != ManualReviewStatus.READ_ONLY:
            raise ValueError("an issue-free manual review report must be READ_ONLY")
        if self.fingerprint is not None and self.fingerprint != self.fingerprint_sha256():
            raise ValueError("manual review report fingerprint does not match its content")
        return self

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

    def render_text_summary(self) -> str:
        lines = [
            "READ-ONLY MANUAL REVIEW",
            "NO TRADING SIGNAL",
            "NO BUY/SELL RECOMMENDATION",
            "NON-ACTIONABLE",
            f"Status: {self.status.value}",
            f"Project phase: {self.project_phase}",
            f"Created at: {self.created_at.isoformat().replace('+00:00', 'Z')}",
            f"Source fingerprint: {self.source_fingerprint}",
        ]
        for section in self.sections:
            lines.append(f"[{section.code.value}] {section.title}: {section.summary}")
            lines.extend(f"- {detail}" for detail in section.details)
        if self.issues:
            lines.append("Issues:")
            lines.extend(
                f"- {issue.severity.value}/{issue.code.value}: {issue.message}"
                for issue in self.issues
            )
        else:
            lines.append("Issues: none")
        return "\n".join(lines)
```

### `app/domain/manual_review_comparison.py`

```python
import hashlib
import json
from datetime import datetime
from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.manual_review import (
    ManualReviewReport,
    ManualReviewSection,
    ManualReviewSectionCode,
    ManualReviewStatus,
)


class ManualReviewComparisonStatus(StrEnum):
    SAME = "SAME"
    CHANGED = "CHANGED"
    INCOMPLETE = "INCOMPLETE"


class ManualReviewComparison(BaseModel):
    created_at: datetime
    left_fingerprint: str = Field(min_length=64, max_length=64)
    right_fingerprint: str = Field(min_length=64, max_length=64)
    status: ManualReviewComparisonStatus
    changed_sections: tuple[ManualReviewSectionCode, ...] = ()
    issue_delta: int
    is_actionable: bool = False
    fingerprint: str | None = Field(default=None, min_length=64, max_length=64)

    model_config = ConfigDict(frozen=True)

    @field_validator("created_at")
    @classmethod
    def normalize_created_at(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("changed_sections")
    @classmethod
    def normalize_changed_sections(
        cls,
        value: tuple[ManualReviewSectionCode, ...],
    ) -> tuple[ManualReviewSectionCode, ...]:
        return tuple(sorted(set(value), key=lambda section_code: section_code.value))

    @model_validator(mode="after")
    def validate_non_actionable_and_fingerprint(self) -> Self:
        if self.is_actionable:
            raise ValueError("manual review comparisons must remain non-actionable")
        if self.fingerprint is not None and self.fingerprint != self.fingerprint_sha256():
            raise ValueError("manual review comparison fingerprint does not match its content")
        return self

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


def compare_manual_review_reports(
    left: ManualReviewReport,
    right: ManualReviewReport,
    created_at: datetime,
) -> ManualReviewComparison:
    left_fingerprint = left.fingerprint_sha256()
    right_fingerprint = right.fingerprint_sha256()
    left_sections = {section.code: section.model_dump(mode="json") for section in left.sections}
    right_sections = {section.code: section.model_dump(mode="json") for section in right.sections}
    changed_sections = tuple(
        section_code
        for section_code in set(left_sections) | set(right_sections)
        if left_sections.get(section_code) != right_sections.get(section_code)
    )

    if left.status != ManualReviewStatus.READ_ONLY or right.status != ManualReviewStatus.READ_ONLY:
        status = ManualReviewComparisonStatus.INCOMPLETE
    elif left_fingerprint == right_fingerprint:
        status = ManualReviewComparisonStatus.SAME
    else:
        status = ManualReviewComparisonStatus.CHANGED

    return ManualReviewComparison(
        created_at=created_at,
        left_fingerprint=left_fingerprint,
        right_fingerprint=right_fingerprint,
        status=status,
        changed_sections=changed_sections,
        issue_delta=len(right.issues) - len(left.issues),
        is_actionable=False,
    )


def build_manual_review_quality_summary(report: ManualReviewReport) -> ManualReviewSection:
    required_codes = set(ManualReviewSectionCode) - {ManualReviewSectionCode.QUALITY_SUMMARY}
    present_codes = {section.code for section in report.sections}
    missing_codes = sorted(required_codes - present_codes, key=lambda code: code.value)
    present_count = len(required_codes) - len(missing_codes)
    details = [
        f"Required sections present: {present_count}/{len(required_codes)}.",
        f"Review issues recorded: {len(report.issues)}.",
        f"Runtime enabled: {str(report.enabled_for_runtime).lower()}.",
        f"Actionable output: {str(report.is_actionable).lower()}.",
    ]
    details.extend(f"Missing section: {code.value}." for code in missing_codes)
    summary = (
        "All required review sections are present."
        if not missing_codes
        else "The manual review report has missing sections."
    )
    return ManualReviewSection(
        code=ManualReviewSectionCode.QUALITY_SUMMARY,
        title="Quality summary",
        summary=summary,
        details=tuple(details),
        issue_count=len(missing_codes),
        is_actionable=False,
    )
```

### `app/domain/manual_review_report_builder.py`

```python
import hashlib
from datetime import datetime

from app.core import constants
from app.core.time import normalize_to_utc
from app.domain.disabled_pipeline_report_shell import DisabledPipelineReportShell
from app.domain.entities.manual_review import (
    ManualReviewIssue,
    ManualReviewIssueCode,
    ManualReviewIssueSeverity,
    ManualReviewReport,
    ManualReviewSection,
    ManualReviewSectionCode,
    ManualReviewStatus,
    contains_actionable_trading_text,
)
from app.domain.entities.pipeline_decision import PipelineDecisionReport, PipelineDecisionStatus
from app.domain.entities.pipeline_report import DisabledPipelineReport, DisabledPipelineStatus
from app.domain.manual_review_comparison import build_manual_review_quality_summary

MANUAL_REVIEW_REPORT_VERSION = "phase5-manual-review-v1"
_MISSING_SOURCE_FINGERPRINT = hashlib.sha256(b"manual-review:no-source").hexdigest()

ReviewSource = PipelineDecisionReport | DisabledPipelineReport


class ManualReviewReportBuilder:
    def __init__(self, source_report: ReviewSource | None = None) -> None:
        self._source_report = source_report

    def build_report(self, created_at: datetime) -> ManualReviewReport:
        normalized_created_at = normalize_to_utc(created_at)
        source_fingerprint = self._source_fingerprint()
        issues = self._build_issues()
        sections = self._build_sections(source_fingerprint, issues)
        status = _review_status(issues)
        base_report = ManualReviewReport(
            report_version=MANUAL_REVIEW_REPORT_VERSION,
            project_phase=constants.PROJECT_PHASE,
            created_at=normalized_created_at,
            status=status,
            source_fingerprint=source_fingerprint,
            sections=sections,
            issues=issues,
            enabled_for_runtime=False,
            is_actionable=False,
        )
        quality_section = build_manual_review_quality_summary(base_report)
        return ManualReviewReport(
            **base_report.model_dump(exclude={"sections"}),
            sections=(*base_report.sections, quality_section),
        )

    def _source_fingerprint(self) -> str:
        if self._source_report is None:
            return _MISSING_SOURCE_FINGERPRINT
        return self._source_report.fingerprint_sha256()

    def _build_issues(self) -> tuple[ManualReviewIssue, ...]:
        if self._source_report is None:
            return (
                ManualReviewIssue(
                    code=ManualReviewIssueCode.MISSING_AUDIT_EXPORT,
                    message="No existing pipeline report was supplied for manual review.",
                    section_code=ManualReviewSectionCode.AUDIT_EXPORT,
                    severity=ManualReviewIssueSeverity.WARNING,
                ),
                ManualReviewIssue(
                    code=ManualReviewIssueCode.MISSING_SAFETY_CONFIRMATIONS,
                    message="Source safety flags cannot be confirmed without a pipeline report.",
                    section_code=ManualReviewSectionCode.SAFETY_CONFIRMATIONS,
                    severity=ManualReviewIssueSeverity.WARNING,
                ),
            )

        issues: list[ManualReviewIssue] = []
        source = self._source_report
        if source.fingerprint is not None and source.fingerprint != source.fingerprint_sha256():
            issues.append(
                ManualReviewIssue(
                    code=ManualReviewIssueCode.FINGERPRINT_MISMATCH,
                    message="The supplied source fingerprint does not match the source content.",
                    section_code=ManualReviewSectionCode.AUDIT_EXPORT,
                    severity=ManualReviewIssueSeverity.BLOCKING,
                )
            )
        if source.is_actionable:
            issues.append(
                ManualReviewIssue(
                    code=ManualReviewIssueCode.ACTIONABLE_CONTENT_FOUND,
                    message=(
                        "The supplied source is marked actionable and cannot be reviewed safely."
                    ),
                    section_code=ManualReviewSectionCode.SAFETY_CONFIRMATIONS,
                    severity=ManualReviewIssueSeverity.BLOCKING,
                )
            )
        if isinstance(source, DisabledPipelineReport) and source.enabled_for_runtime:
            issues.append(
                ManualReviewIssue(
                    code=ManualReviewIssueCode.RUNTIME_ENABLED_FOUND,
                    message="The supplied source is marked enabled for runtime use.",
                    section_code=ManualReviewSectionCode.SAFETY_CONFIRMATIONS,
                    severity=ManualReviewIssueSeverity.BLOCKING,
                )
            )
        if self._unsafe_source_text_found():
            issues.append(
                ManualReviewIssue(
                    code=ManualReviewIssueCode.UNSAFE_TEXT_FOUND,
                    message="Unsafe source text was withheld from the manual review output.",
                    section_code=ManualReviewSectionCode.BLOCKERS,
                    severity=ManualReviewIssueSeverity.BLOCKING,
                )
            )
        if isinstance(source, PipelineDecisionReport) and source.status != (
            PipelineDecisionStatus.READY_FOR_REVIEW
        ):
            issues.append(
                ManualReviewIssue(
                    code=ManualReviewIssueCode.INCOMPLETE_SECTION,
                    message="The Phase 4G source is not ready for complete manual review.",
                    section_code=ManualReviewSectionCode.PIPELINE_STATE,
                    severity=ManualReviewIssueSeverity.WARNING,
                )
            )
        if (
            isinstance(source, DisabledPipelineReport)
            and source.status == DisabledPipelineStatus.BLOCKED
        ):
            issues.append(
                ManualReviewIssue(
                    code=ManualReviewIssueCode.INCOMPLETE_SECTION,
                    message="The disabled pipeline source reports a blocked state.",
                    section_code=ManualReviewSectionCode.PIPELINE_STATE,
                    severity=ManualReviewIssueSeverity.WARNING,
                )
            )
        return tuple(issues)

    def _build_sections(
        self,
        source_fingerprint: str,
        issues: tuple[ManualReviewIssue, ...],
    ) -> tuple[ManualReviewSection, ...]:
        source = self._source_report
        issue_counts = {
            code: sum(1 for issue in issues if issue.section_code == code)
            for code in ManualReviewSectionCode
        }
        source_name = type(source).__name__ if source is not None else "none"
        source_status = source.status.value if source is not None else "MISSING"
        source_phase = self._safe_source_phase()

        sections = [
            ManualReviewSection(
                code=ManualReviewSectionCode.PROJECT_STATE,
                title="Project state",
                summary="Phase 5 manual review is read-only and disabled for runtime action.",
                details=(
                    f"Current project phase: {constants.PROJECT_PHASE}.",
                    f"Source project phase: {source_phase}.",
                    f"Source report type: {source_name}.",
                ),
                issue_count=issue_counts[ManualReviewSectionCode.PROJECT_STATE],
            ),
            ManualReviewSection(
                code=ManualReviewSectionCode.PIPELINE_STATE,
                title="Pipeline state",
                summary=f"Existing source status: {source_status}.",
                details=self._pipeline_details(),
                issue_count=issue_counts[ManualReviewSectionCode.PIPELINE_STATE],
            ),
            ManualReviewSection(
                code=ManualReviewSectionCode.REGISTRY_SUMMARY,
                title="Registry summary",
                summary=self._registry_summary(),
                details=self._registry_details(),
                issue_count=issue_counts[ManualReviewSectionCode.REGISTRY_SUMMARY],
            ),
            ManualReviewSection(
                code=ManualReviewSectionCode.AUDIT_EXPORT,
                title="Audit export",
                summary=(
                    "Source audit metadata is available."
                    if source is not None
                    else "Source audit metadata is unavailable."
                ),
                details=(
                    f"Source fingerprint: {source_fingerprint}.",
                    "Source content was summarized without persistence or external calls.",
                ),
                issue_count=issue_counts[ManualReviewSectionCode.AUDIT_EXPORT],
            ),
            ManualReviewSection(
                code=ManualReviewSectionCode.SAFETY_CONFIRMATIONS,
                title="Safety confirmations",
                summary="The manual review layer is disabled and non-actionable.",
                details=(
                    "Runtime enabled: false.",
                    "Actionable output: false.",
                    "NO TRADING SIGNAL.",
                    (
                        "No external provider, database, scheduler, or messaging call was made by "
                        "the builder."
                    ),
                ),
                issue_count=issue_counts[ManualReviewSectionCode.SAFETY_CONFIRMATIONS],
            ),
            ManualReviewSection(
                code=ManualReviewSectionCode.BLOCKERS,
                title="Blockers",
                summary=self._blocker_summary(),
                details=self._blocker_details(),
                issue_count=issue_counts[ManualReviewSectionCode.BLOCKERS],
            ),
            ManualReviewSection(
                code=ManualReviewSectionCode.TELEGRAM_READINESS,
                title="Telegram readiness",
                summary="Manual authorized review delivery is available without automatic alerts.",
                details=(
                    "The review command returns a short read-only summary.",
                    "No scheduled delivery is registered.",
                ),
                issue_count=issue_counts[ManualReviewSectionCode.TELEGRAM_READINESS],
            ),
        ]
        return tuple(sections)

    def _pipeline_details(self) -> tuple[str, ...]:
        source = self._source_report
        if isinstance(source, PipelineDecisionReport):
            return (
                f"Reviewed rule-set reports: {source.evaluated_ruleset_count}.",
                f"Blocked rule-set reports: {source.blocked_ruleset_count}.",
                f"Not-ready rule-set reports: {source.not_ready_ruleset_count}.",
                f"Skipped registry items: {len(source.skipped_rulesets)}.",
            )
        if isinstance(source, DisabledPipelineReport):
            return (
                f"Registered items: {source.registry_item_count}.",
                f"Valid items: {source.valid_registry_item_count}.",
                f"Invalid items: {source.invalid_registry_item_count}.",
            )
        return ("No existing pipeline report was supplied.",)

    def _registry_summary(self) -> str:
        source = self._source_report
        if isinstance(source, PipelineDecisionReport):
            return "Phase 4G report counts are available for manual inspection."
        if isinstance(source, DisabledPipelineReport):
            return "Phase 4E registry counts are available for manual inspection."
        return "Registry summary is incomplete because no source report was supplied."

    def _registry_details(self) -> tuple[str, ...]:
        source = self._source_report
        if isinstance(source, PipelineDecisionReport):
            return (
                f"Reviewed reports: {source.evaluated_ruleset_count}.",
                f"Skipped items: {len(source.skipped_rulesets)}.",
            )
        if isinstance(source, DisabledPipelineReport):
            return (
                f"Total registry items: {source.registry_item_count}.",
                f"Valid registry items: {source.valid_registry_item_count}.",
                f"Invalid registry items: {source.invalid_registry_item_count}.",
                f"Registry snapshot fingerprint: {source.registry_snapshot_fingerprint}.",
            )
        return ("No registry-derived counts are available.",)

    def _blocker_summary(self) -> str:
        source = self._source_report
        if isinstance(source, PipelineDecisionReport):
            blocker_count = source.blocked_ruleset_count + source.not_ready_ruleset_count
            return (
                f"Existing Phase 4G report contains {blocker_count} blocked or incomplete item(s)."
            )
        if isinstance(source, DisabledPipelineReport):
            return f"Existing disabled report contains {len(source.blockers)} blocker(s)."
        return "Source availability blocks a complete review."

    def _blocker_details(self) -> tuple[str, ...]:
        source = self._source_report
        if isinstance(source, PipelineDecisionReport):
            return (
                f"Blocked report count: {source.blocked_ruleset_count}.",
                f"Not-ready report count: {source.not_ready_ruleset_count}.",
            )
        if isinstance(source, DisabledPipelineReport):
            if not source.blockers:
                return ("No source blockers were recorded.",)
            return tuple(
                (
                    f"{blocker.code.value}: Source message withheld by safety validation."
                    if contains_actionable_trading_text(blocker.message)
                    else f"{blocker.code.value}: {blocker.message}"
                )
                for blocker in source.blockers
            )
        return ("MISSING_AUDIT_EXPORT: no source report was supplied.",)

    def _unsafe_source_text_found(self) -> bool:
        source = self._source_report
        if source is None:
            return False
        if contains_actionable_trading_text(source.project_phase):
            return True
        if isinstance(source, DisabledPipelineReport):
            return any(
                contains_actionable_trading_text(blocker.message) for blocker in source.blockers
            )
        return False

    def _safe_source_phase(self) -> str:
        source = self._source_report
        if source is None:
            return "unavailable"
        if contains_actionable_trading_text(source.project_phase):
            return "withheld by safety validation"
        return source.project_phase


def build_local_manual_review_report(created_at: datetime) -> ManualReviewReport:
    normalized_created_at = normalize_to_utc(created_at)
    source_report = DisabledPipelineReportShell().build_report(normalized_created_at)
    return ManualReviewReportBuilder(source_report).build_report(normalized_created_at)


def _review_status(issues: tuple[ManualReviewIssue, ...]) -> ManualReviewStatus:
    if any(issue.severity == ManualReviewIssueSeverity.BLOCKING for issue in issues):
        return ManualReviewStatus.BLOCKED
    if issues:
        return ManualReviewStatus.INCOMPLETE
    return ManualReviewStatus.READ_ONLY
```

### `app/telegram/commands.py`

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
from app.domain.manual_review_report_builder import build_local_manual_review_report
from app.domain.value_objects import CurrencyPair
from app.services.analysis_service import AnalysisService
from app.services.readiness_digest_service import ReadinessDigestService
from app.services.system_state_service import SystemStateService
from app.telegram.authorization import TelegramIdentity, is_authorized
from app.telegram.formatter import TelegramFormatter
from app.telegram.manual_review_formatter import format_manual_review_body

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
            "/stop_scan, /scan_now, /snapshot, /digest, /review."
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


async def review_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    try:
        report = build_local_manual_review_report(normalize_to_utc(utc_now()))
    except Exception:
        await _reply(
            update,
            context,
            MessageType.DATA_UNAVAILABLE,
            "Отчёт ручной проверки сейчас недоступен.",
        )
        return

    body = format_manual_review_body(report)
    await _reply(update, context, MessageType.REPORT, body)


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
    application.add_handler(CommandHandler("review", review_command))
```

### `app/telegram/manual_review_formatter.py`

```python
from app.domain.entities.manual_review import ManualReviewReport


def format_manual_review_body(report: ManualReviewReport) -> str:
    return (
        "READ-ONLY ручная проверка.\n"
        f"Статус: {report.status.value}.\n"
        f"Разделов: {len(report.sections)}.\n"
        f"Замечаний: {len(report.issues)}.\n"
        f"Источник: {report.source_fingerprint[:12]}.\n"
        "NO TRADING SIGNAL.\n"
        "NON-ACTIONABLE.\n"
        "Торговых указаний нет."
    )
```

### `scripts/manual_review_report.py`

```python
import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.time import utc_now  # noqa: E402
from app.domain.manual_review_report_builder import (  # noqa: E402
    build_local_manual_review_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print a read-only manual review report to stdout."
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="stdout rendering format",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    report = build_local_manual_review_report(utc_now())
    output = (
        report.deterministic_json() if arguments.format == "json" else report.render_text_summary()
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## Full Contents Of New Tests

### `tests/unit/test_manual_review_foundation.py`

```python
import json
from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.entities.manual_review import (
    ManualReviewIssue,
    ManualReviewIssueCode,
    ManualReviewIssueSeverity,
    ManualReviewReport,
    ManualReviewSection,
    ManualReviewSectionCode,
    ManualReviewStatus,
)
from app.domain.entities.pipeline_decision import PipelineDecisionReport, PipelineDecisionStatus
from app.domain.entities.pipeline_report import (
    DisabledPipelineBlocker,
    DisabledPipelineBlockerCode,
    DisabledPipelineReport,
    DisabledPipelineStatus,
)
from app.domain.entities.strategy_rules import StrategyRuleSeverity
from app.domain.manual_review_comparison import (
    ManualReviewComparison,
    ManualReviewComparisonStatus,
    build_manual_review_quality_summary,
    compare_manual_review_reports,
)
from app.domain.manual_review_report_builder import ManualReviewReportBuilder

CREATED_AT = datetime(2026, 7, 20, 12, 0, tzinfo=UTC)


def _disabled_source(
    *,
    fingerprint: str | None = None,
    blocker_message: str = "The source pipeline remains disabled.",
) -> DisabledPipelineReport:
    return DisabledPipelineReport(
        pipeline_version="phase4e-test-v1",
        project_phase="phase_4g_strategy_decision_composition_foundation",
        status=DisabledPipelineStatus.DISABLED,
        created_at=CREATED_AT,
        registry_item_count=1,
        valid_registry_item_count=1,
        invalid_registry_item_count=0,
        blockers=(
            DisabledPipelineBlocker(
                code=DisabledPipelineBlockerCode.PIPELINE_DISABLED,
                message=blocker_message,
                severity=StrategyRuleSeverity.BLOCKING,
            ),
        ),
        registry_snapshot_fingerprint="a" * 64,
        enabled_for_runtime=False,
        is_actionable=False,
        fingerprint=fingerprint,
    )


def _phase4g_source() -> PipelineDecisionReport:
    return PipelineDecisionReport(
        pipeline_version="phase4g-test-v1",
        project_phase="phase_4g_strategy_decision_composition_foundation",
        status=PipelineDecisionStatus.READY_FOR_REVIEW,
        evaluated_at=CREATED_AT,
        source_snapshot_id="b" * 64,
        ruleset_reports=(),
        skipped_rulesets=(),
        evaluated_ruleset_count=0,
        blocked_ruleset_count=0,
        not_ready_ruleset_count=0,
        is_actionable=False,
    )


def _report() -> ManualReviewReport:
    return ManualReviewReportBuilder(_disabled_source()).build_report(CREATED_AT)


def test_phase5_project_state_remains_safe() -> None:
    assert constants.PROJECT_PHASE == "phase_5_manual_review_layer_foundation"
    assert constants.STRATEGY_IMPLEMENTED is False
    assert constants.REAL_TRADING_ENABLED is False


def test_manual_review_models_are_immutable_and_normalize_created_at_to_utc() -> None:
    local_created_at = datetime(2026, 7, 20, 14, 0, tzinfo=timezone(timedelta(hours=2)))
    report = ManualReviewReportBuilder(_disabled_source()).build_report(local_created_at)

    assert report.created_at == CREATED_AT
    assert report.created_at.tzinfo == UTC
    with pytest.raises(ValidationError):
        report.status = ManualReviewStatus.BLOCKED
    with pytest.raises(ValidationError):
        report.sections[0].summary = "Changed summary."


def test_duplicate_section_codes_are_rejected() -> None:
    section = ManualReviewSection(
        code=ManualReviewSectionCode.PROJECT_STATE,
        title="Project state",
        summary="Read-only project state.",
    )

    with pytest.raises(ValidationError, match="section codes must be unique"):
        ManualReviewReport(
            report_version="v1",
            project_phase=constants.PROJECT_PHASE,
            created_at=CREATED_AT,
            status=ManualReviewStatus.READ_ONLY,
            source_fingerprint="a" * 64,
            sections=(section, section),
        )


def test_duplicate_issues_are_deduplicated_and_sorted_deterministically() -> None:
    audit_issue = ManualReviewIssue(
        code=ManualReviewIssueCode.MISSING_AUDIT_EXPORT,
        message="Audit metadata is unavailable.",
        section_code=ManualReviewSectionCode.AUDIT_EXPORT,
        severity=ManualReviewIssueSeverity.WARNING,
    )
    safety_issue = ManualReviewIssue(
        code=ManualReviewIssueCode.MISSING_SAFETY_CONFIRMATIONS,
        message="Safety flags are unavailable.",
        section_code=ManualReviewSectionCode.SAFETY_CONFIRMATIONS,
        severity=ManualReviewIssueSeverity.WARNING,
    )
    report = ManualReviewReport(
        report_version="v1",
        project_phase=constants.PROJECT_PHASE,
        created_at=CREATED_AT,
        status=ManualReviewStatus.INCOMPLETE,
        source_fingerprint="a" * 64,
        sections=(
            ManualReviewSection(
                code=ManualReviewSectionCode.AUDIT_EXPORT,
                title="Audit export",
                summary="Audit metadata is unavailable.",
                issue_count=1,
            ),
        ),
        issues=(safety_issue, audit_issue, audit_issue),
    )

    assert report.issues == (audit_issue, safety_issue)


@pytest.mark.parametrize("field_name", ["enabled_for_runtime", "is_actionable"])
def test_manual_review_report_rejects_enabled_or_actionable_flags(field_name: str) -> None:
    payload = _report().model_dump()
    payload[field_name] = True

    with pytest.raises(ValidationError):
        ManualReviewReport.model_validate(payload)


@pytest.mark.parametrize(
    "unsafe_text",
    [
        "Buy EURUSD now.",
        "Sell EURUSD now.",
        "Go long now.",
        "Short recommendation.",
        "Trading signal available.",
        "Entry at the latest value.",
        "Set a stop loss.",
        "Set a take profit.",
        "Use this target.",
        "Calculate position size.",
        "Use setup score.",
        "Use confidence score.",
        "Contact a broker.",
        "Place an order.",
        "Execute immediately.",
        "Enable paper trading.",
        "Enable live trading.",
        "Enable real trading.",
    ],
)
def test_manual_review_section_rejects_actionable_text(unsafe_text: str) -> None:
    with pytest.raises(ValidationError, match="actionable trading text"):
        ManualReviewSection(
            code=ManualReviewSectionCode.PIPELINE_STATE,
            title="Pipeline state",
            summary=unsafe_text,
        )


def test_manual_review_section_rejects_actionable_flag() -> None:
    with pytest.raises(ValidationError, match="must remain non-actionable"):
        ManualReviewSection(
            code=ManualReviewSectionCode.PIPELINE_STATE,
            title="Pipeline state",
            summary="Read-only source summary.",
            is_actionable=True,
        )


def test_manual_review_serialization_and_fingerprint_are_stable() -> None:
    first = _report()
    second = _report()

    assert first.deterministic_json() == second.deterministic_json()
    assert first.fingerprint_sha256() == second.fingerprint_sha256()
    assert json.loads(first.deterministic_json())["is_actionable"] is False
    assert tuple(section.code.value for section in first.sections) == tuple(
        sorted(section.code.value for section in first.sections)
    )


def test_manual_review_fingerprint_changes_when_content_changes() -> None:
    first = _report()
    changed_sections = tuple(
        section.model_copy(update={"summary": "Updated read-only project state."})
        if section.code == ManualReviewSectionCode.PROJECT_STATE
        else section
        for section in first.sections
    )
    second = ManualReviewReport(
        **first.model_dump(exclude={"sections", "fingerprint"}),
        sections=changed_sections,
    )

    assert first.fingerprint_sha256() != second.fingerprint_sha256()


def test_text_summary_is_deterministic_and_contains_required_safety_messages() -> None:
    report = _report()

    assert report.render_text_summary() == _report().render_text_summary()
    assert "READ-ONLY MANUAL REVIEW" in report.render_text_summary()
    assert "NO TRADING SIGNAL" in report.render_text_summary()
    assert "NO BUY/SELL RECOMMENDATION" in report.render_text_summary()
    assert "NON-ACTIONABLE" in report.render_text_summary()
    assert "Buy EURUSD" not in report.render_text_summary()
    assert "Sell EURUSD" not in report.render_text_summary()
    assert "go long" not in report.render_text_summary().lower()
    assert "go short" not in report.render_text_summary().lower()


def test_manual_review_report_has_no_trading_output_fields() -> None:
    forbidden_fields = {
        "decision",
        "recommendation",
        "signal",
        "signal_direction",
        "direction",
        "price",
        "entry",
        "entry_price",
        "stop_loss",
        "take_profit",
        "target",
        "position_size",
        "setup_score",
        "confidence",
        "confidence_score",
    }

    assert set(ManualReviewReport.model_fields).isdisjoint(forbidden_fields)
    assert set(ManualReviewSection.model_fields).isdisjoint(forbidden_fields)
    assert set(ManualReviewIssue.model_fields).isdisjoint(forbidden_fields)


def test_builder_consumes_phase4g_report_without_recomputing_pipeline() -> None:
    source = _phase4g_source()
    report = ManualReviewReportBuilder(source).build_report(CREATED_AT)

    assert report.status == ManualReviewStatus.READ_ONLY
    assert report.source_fingerprint == source.fingerprint_sha256()
    assert report.enabled_for_runtime is False
    assert report.is_actionable is False
    assert len(report.sections) == len(ManualReviewSectionCode)
    assert {section.code for section in report.sections} == set(ManualReviewSectionCode)


def test_builder_reports_missing_source_as_incomplete_instead_of_crashing() -> None:
    report = ManualReviewReportBuilder().build_report(CREATED_AT)

    assert report.status == ManualReviewStatus.INCOMPLETE
    assert {issue.code for issue in report.issues} == {
        ManualReviewIssueCode.MISSING_AUDIT_EXPORT,
        ManualReviewIssueCode.MISSING_SAFETY_CONFIRMATIONS,
    }


def test_builder_blocks_a_mismatched_source_fingerprint() -> None:
    report = ManualReviewReportBuilder(_disabled_source(fingerprint="f" * 64)).build_report(
        CREATED_AT
    )

    assert report.status == ManualReviewStatus.BLOCKED
    assert report.issues[0].code == ManualReviewIssueCode.FINGERPRINT_MISMATCH


def test_builder_redacts_unsafe_source_text_and_records_blocking_issue() -> None:
    source = _disabled_source(blocker_message="Buy EURUSD now.")

    report = ManualReviewReportBuilder(source).build_report(CREATED_AT)

    assert report.status == ManualReviewStatus.BLOCKED
    assert ManualReviewIssueCode.UNSAFE_TEXT_FOUND in {issue.code for issue in report.issues}
    assert "Buy EURUSD" not in report.render_text_summary()
    assert "withheld by safety validation" in report.render_text_summary()


@pytest.mark.parametrize("flag_name", ["enabled_for_runtime", "is_actionable"])
def test_builder_blocks_unsafe_source_flags_defensively(flag_name: str) -> None:
    source = _disabled_source().model_copy(update={flag_name: True})

    report = ManualReviewReportBuilder(source).build_report(CREATED_AT)

    assert report.status == ManualReviewStatus.BLOCKED
    assert any(issue.severity == ManualReviewIssueSeverity.BLOCKING for issue in report.issues)


def test_quality_summary_is_deterministic_and_non_actionable() -> None:
    report = _report()
    first = build_manual_review_quality_summary(report)
    second = build_manual_review_quality_summary(report)

    assert first == second
    assert first.code == ManualReviewSectionCode.QUALITY_SUMMARY
    assert first.is_actionable is False


def test_compare_same_report_is_deterministic_and_non_actionable() -> None:
    report = _report()
    first = compare_manual_review_reports(report, report, CREATED_AT)
    second = compare_manual_review_reports(report, report, CREATED_AT)

    assert first.status == ManualReviewComparisonStatus.SAME
    assert first.changed_sections == ()
    assert first.is_actionable is False
    assert first.deterministic_json() == second.deterministic_json()
    assert first.fingerprint_sha256() == second.fingerprint_sha256()


def test_compare_changed_report_identifies_changed_section() -> None:
    left = _report()
    changed_sections = tuple(
        section.model_copy(update={"summary": "Updated read-only project state."})
        if section.code == ManualReviewSectionCode.PROJECT_STATE
        else section
        for section in left.sections
    )
    right = ManualReviewReport(
        **left.model_dump(exclude={"sections", "fingerprint"}),
        sections=changed_sections,
    )

    comparison = compare_manual_review_reports(left, right, CREATED_AT)

    assert comparison.status == ManualReviewComparisonStatus.CHANGED
    assert comparison.changed_sections == (ManualReviewSectionCode.PROJECT_STATE,)


def test_compare_incomplete_report_is_incomplete() -> None:
    incomplete = ManualReviewReportBuilder().build_report(CREATED_AT)

    comparison = compare_manual_review_reports(incomplete, _report(), CREATED_AT)

    assert comparison.status == ManualReviewComparisonStatus.INCOMPLETE


def test_comparison_has_no_trading_output_fields_and_rejects_actionable_flag() -> None:
    forbidden_fields = {
        "decision",
        "recommendation",
        "signal",
        "price",
        "entry",
        "stop_loss",
        "take_profit",
        "position_size",
        "setup_score",
        "confidence_score",
    }
    assert set(ManualReviewComparison.model_fields).isdisjoint(forbidden_fields)

    with pytest.raises(ValidationError, match="must remain non-actionable"):
        ManualReviewComparison(
            created_at=CREATED_AT,
            left_fingerprint="a" * 64,
            right_fingerprint="a" * 64,
            status=ManualReviewComparisonStatus.SAME,
            issue_delta=0,
            is_actionable=True,
        )
```

### `tests/unit/test_manual_review_cli.py`

```python
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from scripts import manual_review_report

CREATED_AT = datetime(2026, 7, 20, 12, 0, tzinfo=UTC)


def test_cli_defaults_to_read_only_text_on_stdout(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(manual_review_report, "utc_now", lambda: CREATED_AT)

    exit_code = manual_review_report.main([])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert output.startswith("READ-ONLY MANUAL REVIEW\n")
    assert "NO TRADING SIGNAL" in output
    assert "NO BUY/SELL RECOMMENDATION" in output
    assert "NON-ACTIONABLE" in output
    assert "go long" not in output.lower()
    assert "go short" not in output.lower()


def test_cli_text_format_is_deterministic(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(manual_review_report, "utc_now", lambda: CREATED_AT)

    assert manual_review_report.main(["--format", "text"]) == 0
    first = capsys.readouterr().out
    assert manual_review_report.main(["--format", "text"]) == 0
    second = capsys.readouterr().out

    assert first == second


def test_cli_json_format_is_deterministic(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(manual_review_report, "utc_now", lambda: CREATED_AT)

    assert manual_review_report.main(["--format", "json"]) == 0
    first = capsys.readouterr().out
    assert manual_review_report.main(["--format", "json"]) == 0
    second = capsys.readouterr().out

    assert first == second
    payload = json.loads(first)
    assert payload["enabled_for_runtime"] is False
    assert payload["is_actionable"] is False
    assert payload["project_phase"] == "phase_5_manual_review_layer_foundation"


def test_cli_has_no_file_writing_option_or_runtime_file_write() -> None:
    source = Path("scripts/manual_review_report.py").read_text(encoding="utf-8")

    assert "--output" not in source
    assert "write_text" not in source
    assert "write_bytes" not in source
    assert "open(" not in source


def test_cli_script_runs_directly_from_repository_root() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/manual_review_report.py", "--format", "json"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert json.loads(result.stdout)["status"] == "READ_ONLY"
```

+## Modified Existing Test Diffs

The following is the exact Git diff for existing test files that gained Phase 5 coverage or had the current project-phase assertion advanced:

```diff
diff --git a/tests/contract/test_safety_boundaries.py b/tests/contract/test_safety_boundaries.py
index 2edab0f..ea3017f 100644
--- a/tests/contract/test_safety_boundaries.py
+++ b/tests/contract/test_safety_boundaries.py
@@ -6,6 +6,8 @@ import pytest
 from pydantic import ValidationError

 import app.domain.disabled_pipeline_report_shell as disabled_pipeline_report_shell_module
+import app.domain.manual_review_comparison as manual_review_comparison_module
+import app.domain.manual_review_report_builder as manual_review_report_builder_module
 import app.domain.strategy_decision_composer as strategy_decision_composer_module
 import app.domain.strategy_field_resolver as strategy_field_resolver_module
 import app.domain.strategy_rule_evaluator as strategy_rule_evaluator_module
@@ -22,6 +24,7 @@ from app.domain.analysis_engine import AnalysisEngine
 from app.domain.disabled_pipeline_report_shell import DisabledPipelineReportShell
 from app.domain.entities import (
     Timeframe,
+    manual_review,
     pipeline_decision,
     pipeline_report,
     rule_evaluation,
@@ -30,6 +33,7 @@ from app.domain.entities import (
     strategy_rules,
     strategy_validation,
 )
+from app.domain.manual_review_report_builder import ManualReviewReportBuilder
 from app.domain.strategy_decision_composer import StrategyDecisionComposer
 from app.domain.strategy_field_resolver import resolve_field
 from app.domain.strategy_rule_evaluator import StrategyRuleEvaluator
@@ -544,6 +548,58 @@ PHASE_4G_FORBIDDEN_BEHAVIOR_TERMS = (
     "OpenAI",
     "LLM",
 )
+PHASE_5_DOMAIN_OBJECTS = (
+    manual_review.ManualReviewIssue,
+    manual_review.ManualReviewSection,
+    manual_review.ManualReviewReport,
+    ManualReviewReportBuilder,
+    manual_review_comparison_module.ManualReviewComparison,
+    manual_review_comparison_module.compare_manual_review_reports,
+    manual_review_comparison_module.build_manual_review_quality_summary,
+)
+PHASE_5_FILES = (
+    Path("app/domain/entities/manual_review.py"),
+    Path("app/domain/manual_review_report_builder.py"),
+    Path("app/domain/manual_review_comparison.py"),
+    Path("scripts/manual_review_report.py"),
+    Path("app/telegram/manual_review_formatter.py"),
+)
+PHASE_5_FORBIDDEN_RUNTIME_IMPORTS = (
+    "app.adapters",
+    "app.persistence",
+    "app.scheduler",
+    "app.api",
+    "sqlalchemy",
+    "fastapi",
+    "httpx",
+    "openai",
+)
+PHASE_5_FORBIDDEN_BEHAVIOR_TERMS = (
+    "strategy_engine",
+    "decision_engine",
+    "evaluate_rules",
+    "evaluate_ruleset",
+    "generate_signal",
+    "signal_generator",
+    "signal_engine",
+    "setup_scoring",
+    "confidence_scoring",
+    "calculate_entry",
+    "calculate_stop",
+    "calculate_target",
+    "calculate_position_size",
+    "send_signal",
+    "telegram_signal",
+    "place_order",
+    "submit_order",
+    "execute_order",
+    "paper_trading",
+    "real_trading",
+    "backtesting",
+    "trading_simulator",
+    "OpenAI",
+    "LLM",
+)


 def test_no_real_order_execution_code_exists() -> None:
@@ -1357,6 +1413,123 @@ def test_phase4g_does_not_add_strategy_decision_service() -> None:
     assert offenders == []


+def test_phase5_domain_objects_do_not_import_forbidden_runtime_dependencies() -> None:
+    offenders: list[str] = []
+    for index, source_object in enumerate(PHASE_5_DOMAIN_OBJECTS):
+        source = inspect.getsource(source_object).lower()
+        import_lines = tuple(
+            line
+            for line in source.splitlines()
+            if line.startswith("import ") or line.startswith("from ")
+        )
+        for term in PHASE_5_FORBIDDEN_RUNTIME_IMPORTS:
+            if any(term.lower() in line for line in import_lines):
+                offenders.append(f"phase5-object-{index}: {term}")
+
+    assert offenders == []
+
+
+def test_phase5_modules_do_not_add_trading_behavior_terms() -> None:
+    offenders: list[str] = []
+    for file_path in PHASE_5_FILES:
+        source = file_path.read_text(encoding="utf-8")
+        lowered = source.lower()
+        for term in PHASE_5_FORBIDDEN_BEHAVIOR_TERMS:
+            if term.lower() in lowered:
+                offenders.append(f"{file_path}: {term}")
+
+    assert offenders == []
+
+
+def test_phase5_builder_has_no_market_database_or_messaging_dependency() -> None:
+    source = inspect.getsource(manual_review_report_builder_module).lower()
+    forbidden_terms = (
+        "app.domain.entities.market_data",
+        "app.domain.entities.analysis",
+        "app.persistence",
+        "app.telegram",
+        "app.scheduler",
+        "app.adapters",
+        "sqlalchemy",
+        "httpx",
+        "openai",
+    )
+
+    assert not any(term in source for term in forbidden_terms)
+
+
+def test_phase5_comparison_is_in_memory_only() -> None:
+    source = inspect.getsource(manual_review_comparison_module).lower()
+    forbidden_terms = (
+        "app.persistence",
+        "sqlalchemy",
+        "write_text",
+        "write_bytes",
+        "open(",
+        "httpx",
+    )
+
+    assert not any(term in source for term in forbidden_terms)
+
+
+def test_phase5_models_have_no_trading_output_fields() -> None:
+    forbidden_fields = {
+        "decision",
+        "recommendation",
+        "signal",
+        "signal_direction",
+        "direction",
+        "price",
+        "entry",
+        "entry_price",
+        "stop_loss",
+        "take_profit",
+        "target",
+        "position_size",
+        "setup_score",
+        "confidence",
+        "confidence_score",
+    }
+
+    assert set(manual_review.ManualReviewReport.model_fields).isdisjoint(forbidden_fields)
+    assert set(manual_review.ManualReviewSection.model_fields).isdisjoint(forbidden_fields)
+    assert set(manual_review.ManualReviewIssue.model_fields).isdisjoint(forbidden_fields)
+    assert set(manual_review_comparison_module.ManualReviewComparison.model_fields).isdisjoint(
+        forbidden_fields
+    )
+
+
+def test_phase5_adds_no_api_route_or_scheduler_job() -> None:
+    route_source = "\n".join(
+        file_path.read_text(encoding="utf-8") for file_path in Path("app/api/routes").glob("*.py")
+    )
+    scheduler_source = "\n".join(
+        file_path.read_text(encoding="utf-8") for file_path in Path("app/scheduler").glob("*.py")
+    )
+
+    assert "ManualReview" not in route_source
+    assert "manual_review" not in route_source
+    assert "ManualReview" not in scheduler_source
+    assert "manual_review" not in scheduler_source
+    assert 'CommandHandler("signal"' not in Path("app/telegram/commands.py").read_text(
+        encoding="utf-8"
+    )
+
+
+def test_phase5_cli_has_no_runtime_file_writing() -> None:
+    source = Path("scripts/manual_review_report.py").read_text(encoding="utf-8")
+
+    assert "--output" not in source
+    assert "write_text" not in source
+    assert "write_bytes" not in source
+    assert "open(" not in source
+
+
+def test_phase5_adds_no_migration_and_phase3j_route_remains_absent() -> None:
+    assert list(Path("migrations/versions").glob("*phase5*")) == []
+    assert not Path("app/api/routes/digest_deliveries.py").exists()
+
+
 @pytest.mark.asyncio
 async def test_disabled_market_data_provider_fails_before_external_call() -> None:
     with pytest.raises(IntegrationDisabledError):
diff --git a/tests/unit/test_disabled_pipeline_report_shell_foundation.py b/tests/unit/test_disabled_pipeline_report_shell_foundation.py
index e335e19..aaab103 100644
--- a/tests/unit/test_disabled_pipeline_report_shell_foundation.py
+++ b/tests/unit/test_disabled_pipeline_report_shell_foundation.py
@@ -62,7 +62,7 @@ def _snapshot_from_registry(


 def test_project_phase_is_phase4e_disabled_pipeline_report_shell_foundation() -> None:
-    assert constants.PROJECT_PHASE == "phase_4g_strategy_decision_composition_foundation"
+    assert constants.PROJECT_PHASE == "phase_5_manual_review_layer_foundation"


 def test_blocker_and_report_models_are_immutable() -> None:
diff --git a/tests/unit/test_signal_contract_foundation.py b/tests/unit/test_signal_contract_foundation.py
index 339413e..fe0bfca 100644
--- a/tests/unit/test_signal_contract_foundation.py
+++ b/tests/unit/test_signal_contract_foundation.py
@@ -60,7 +60,7 @@ def _contract(**overrides: object) -> SignalContract:


 def test_project_phase_has_advanced_to_phase4e_disabled_pipeline_report_shell_foundation() -> None:
-    assert constants.PROJECT_PHASE == "phase_4g_strategy_decision_composition_foundation"
+    assert constants.PROJECT_PHASE == "phase_5_manual_review_layer_foundation"


 def test_signal_contract_models_are_immutable() -> None:
diff --git a/tests/unit/test_strategy_rule_specification_foundation.py b/tests/unit/test_strategy_rule_specification_foundation.py
index 21690de..ac50e28 100644
--- a/tests/unit/test_strategy_rule_specification_foundation.py
+++ b/tests/unit/test_strategy_rule_specification_foundation.py
@@ -58,7 +58,7 @@ def _ruleset(**overrides: object) -> StrategyRuleSet:


 def test_project_phase_has_advanced_to_phase4e_disabled_pipeline_report_shell_foundation() -> None:
-    assert constants.PROJECT_PHASE == "phase_4g_strategy_decision_composition_foundation"
+    assert constants.PROJECT_PHASE == "phase_5_manual_review_layer_foundation"


 def test_strategy_rule_models_are_immutable() -> None:
diff --git a/tests/unit/test_strategy_ruleset_registry_foundation.py b/tests/unit/test_strategy_ruleset_registry_foundation.py
index ddd1be4..481f4db 100644
--- a/tests/unit/test_strategy_ruleset_registry_foundation.py
+++ b/tests/unit/test_strategy_ruleset_registry_foundation.py
@@ -44,7 +44,7 @@ def _fixture_with_changed_description() -> dict[str, StrategyRuleSet]:


 def test_project_phase_is_phase4e_disabled_pipeline_report_shell_foundation() -> None:
-    assert constants.PROJECT_PHASE == "phase_4g_strategy_decision_composition_foundation"
+    assert constants.PROJECT_PHASE == "phase_5_manual_review_layer_foundation"


 def test_registry_item_and_snapshot_models_are_immutable() -> None:
diff --git a/tests/unit/test_strategy_ruleset_validation_foundation.py b/tests/unit/test_strategy_ruleset_validation_foundation.py
index 732c3c5..851be6b 100644
--- a/tests/unit/test_strategy_ruleset_validation_foundation.py
+++ b/tests/unit/test_strategy_ruleset_validation_foundation.py
@@ -82,7 +82,7 @@ def _codes(


 def test_project_phase_is_phase4e_disabled_pipeline_report_shell_foundation() -> None:
-    assert constants.PROJECT_PHASE == "phase_4g_strategy_decision_composition_foundation"
+    assert constants.PROJECT_PHASE == "phase_5_manual_review_layer_foundation"


 def test_validation_issue_and_report_models_are_immutable() -> None:
diff --git a/tests/unit/test_telegram_commands.py b/tests/unit/test_telegram_commands.py
index b54f41d..6db78a9 100644
--- a/tests/unit/test_telegram_commands.py
+++ b/tests/unit/test_telegram_commands.py
@@ -11,6 +11,8 @@ from app.services.readiness_digest_service import ReadinessDigestService
 from app.telegram import commands
 from app.telegram.commands import (
     digest_command,
+    help_command,
+    review_command,
     scan_now_command,
     snapshot_command,
     start_scan_command,
@@ -180,7 +182,7 @@ async def test_snapshot_command_rejects_invalid_arguments() -> None:
     ]


-def test_add_handlers_keeps_snapshot_and_registers_digest(
+def test_add_handlers_keeps_snapshot_digest_and_registers_review(
     monkeypatch: pytest.MonkeyPatch,
 ) -> None:
     application = FakeHandlerApplication()
@@ -191,6 +193,7 @@ def test_add_handlers_keeps_snapshot_and_registers_digest(
     registered = {handler.command: handler.callback for handler in application.handlers}
     assert registered["snapshot"] is snapshot_command
     assert registered["digest"] is digest_command
+    assert registered["review"] is review_command


 @pytest.mark.asyncio
@@ -242,3 +245,59 @@ async def test_digest_command_rejects_invalid_arguments() -> None:
     assert update.effective_message.replies == [
         "❌ Формат команды: /digest или /digest EURUSD M15. Поддерживаются M15 и H1."
     ]
+
+
+@pytest.mark.asyncio
+async def test_review_command_returns_authorized_read_only_summary(
+    monkeypatch: pytest.MonkeyPatch,
+) -> None:
+    factory = FakeUnitOfWorkFactory()
+    context = _context(factory)
+    update = FakeUpdate(user_id=1, chat_id=2, text="/review")
+    monkeypatch.setattr(commands, "utc_now", lambda: BASE_TIME)
+
+    await review_command(update, context)
+
+    assert len(update.effective_message.replies) == 1
+    reply = update.effective_message.replies[0]
+    assert reply.startswith("📊 ")
+    assert "READ-ONLY" in reply
+    assert "NO TRADING SIGNAL" in reply
+    assert "NON-ACTIONABLE" in reply
+    assert factory.state == {}
+    forbidden_terms = (
+        "LONG",
+        "SHORT",
+        "entry",
+        "stop loss",
+        "take profit",
+        "position size",
+        "setup score",
+        "confidence score",
+        "broker",
+        "order",
+    )
+    assert not any(term in reply for term in forbidden_terms)
+
+
+@pytest.mark.asyncio
+async def test_review_command_blocks_unauthorized_user() -> None:
+    factory = FakeUnitOfWorkFactory()
+    context = _context(factory)
+    update = FakeUpdate(user_id=99, chat_id=2, text="/review")
+
+    await review_command(update, context)
+
+    assert update.effective_message.replies == ["❌ Доступ запрещён."]
+
+
+@pytest.mark.asyncio
+async def test_help_command_includes_manual_review() -> None:
+    factory = FakeUnitOfWorkFactory()
+    context = _context(factory)
+    update = FakeUpdate(user_id=1, chat_id=2, text="/help")
+
+    await help_command(update, context)
+
+    assert len(update.effective_message.replies) == 1
+    assert "/review" in update.effective_message.replies[0]
```

## Final Confirmation

Phase 5A/5B/5C/5D/5E are complete and uncommitted for human review. Phase 5 remains read-only,
manual-review-only, disabled/non-actionable, and deterministic. No Phase 3J API route exists. No
rule evaluation against market data, strategy engine, decision engine, signal generation, setup
scoring, confidence scoring, AI agent, OpenAI call, broker API, paper trading, order execution, live
trading, or real trading was added.
