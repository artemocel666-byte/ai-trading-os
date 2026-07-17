# Phase 3I Verification Report

Generated at: 2026-07-17T00:00:00Z

## Scope

Phase 3I implemented a snapshot versioning and evidence foundation over the existing Phase 3A-3H
feature/context/analysis foundation, closing gaps identified by an external architecture review and
verified against the codebase before implementation.

- `PROJECT_PHASE = "phase_3i_snapshot_versioning_and_evidence_foundation"`.
- Added `FEATURE_SNAPSHOT_SCHEMA_VERSION`, `CONTEXT_SNAPSHOT_SCHEMA_VERSION`, and
  `ANALYSIS_SNAPSHOT_SCHEMA_VERSION` constants, each currently `1`.
- Added `schema_version` to `MarketFeatureSnapshot`, `MarketContextSnapshot`, and
  `AnalysisSnapshotMetadata`, set from the matching constant at each engine's construction site.
  Because `snapshot_id` hashes the full `model_dump()`, the version is automatically folded into
  the existing deduplication hash with no other code changes.
- Added a deterministic `data_completeness_ratio` (`used candles / expected candles`, bounded to
  `[0, 1]`) on `MarketFeatureSnapshot` and `MarketContextSnapshot`. Purely descriptive; does not
  change `quality_ok`, `AnalysisReadinessStatus`, or any existing branch logic.
- Added `used_candle_open_times`/`used_candle_close_times` to `CandleFeatureSummary`, populated
  from the same accepted-candle list already used for `latest_close`/`simple_return`/etc, giving a
  concrete provenance trail a future agent can use to honestly populate
  `EvidenceReference.candle_timestamp`.
- Added an unwired, read-only `AnalysisAgent` Protocol to `app/schemas/agents.py` (not
  `app/domain/interfaces`, to avoid a domain -> schemas layering violation, since `app.schemas` is
  consumed only by `app/api` and neither `app.domain` nor `app.services` import it elsewhere).
  Reuses the existing `AgentReport`/`EvidenceReference` DTOs rather than inventing new ones.
- Explicitly did not add a feature/agent registry, Decision Engine, Risk Engine, replay tooling, or
  observability metrics — deferred to Phase 4, where they can be designed against concrete agents
  instead of built speculatively.
- Confirmed all domain snapshot models were already `ConfigDict(frozen=True)` before this phase;
  no immutability change was needed.
- Phase 4 was not started.
- No strategy, signals, setup scoring, confidence scoring, AI agents, OpenAI calls, broker APIs,
  paper trading, order execution, or real trading were added.

## Verification Results

- `uv run ruff format .` -> `2 files reformatted, 107 files left unchanged` (new/updated test
  files), then stable.
- `uv run ruff check .` -> `All checks passed!`.
- `uv run mypy app` -> `Success: no issues found in 77 source files`.
- `uv run pytest` (excluding two pre-existing collection failures caused by placeholder values in
  a local, uncommitted `.env` file, unrelated to this phase and reproducible on `main` before this
  phase) -> `156 passed`.

## Tests Added Or Updated

- Added `tests/unit/test_snapshot_versioning_foundation.py`: schema version presence, deterministic
  and bounded `data_completeness_ratio`, evidence-timestamp coverage matching `used_candle_count`,
  and a structural check that the `AnalysisAgent` Protocol is satisfiable without being wired to
  anything.
- Added `PHASE_3I_FILES`/`PHASE_3I_FORBIDDEN_TERMS` and a matching safety-boundary test to
  `tests/contract/test_safety_boundaries.py`.
- Updated `tests/unit/test_analysis_snapshot_foundation.py` and
  `tests/unit/test_readiness_scheduler_foundation.py` project-phase string assertions to
  `phase_3i_snapshot_versioning_and_evidence_foundation`.
- Renamed the initial `quality_score` field to `data_completeness_ratio` during implementation
  after discovering the existing Phase 3C/3D safety-boundary tests ban the bare substring `score`
  in `app/domain/entities/context.py`, `app/domain/context_engine.py`,
  `app/domain/entities/analysis.py`, and `app/domain/analysis_engine.py`.

## Remaining Risks

- Two test files (`tests/contract/test_provider_contracts.py`,
  `tests/integration/test_database_and_api.py`) fail to collect because of placeholder,
  non-integer values in a local `.env` (`telegram_allowed_user_id`/`telegram_allowed_chat_id`).
  This is a local environment issue, not a code defect, and was already present before Phase 3I.
- Docker verification was not re-run for this phase; only host-level `pytest`/`ruff`/`mypy` were
  verified.
- The `AnalysisAgent` Protocol has no concrete implementation or runtime enforcement of its
  "no I/O, read-only" contract beyond the docstring; Phase 4 must decide how (or whether) to
  enforce it structurally.
