import inspect
from datetime import UTC, datetime
from pathlib import Path

import pytest

import app.domain.strategy_ruleset_registry as strategy_ruleset_registry_module
import app.domain.strategy_ruleset_validator as strategy_ruleset_validator_module
from app.adapters.disabled import (
    DisabledEconomicCalendarProvider,
    DisabledLLMProvider,
    DisabledMarketDataProvider,
)
from app.core.enums import Decision
from app.core.exceptions import IntegrationDisabledError
from app.domain.entities import (
    Timeframe,
    signal_contract,
    strategy_registry,
    strategy_rules,
    strategy_validation,
)
from app.domain.strategy_ruleset_registry import StrategyRuleSetRegistry
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
PHASE_3I_DIGEST_AUDIT_FILES = (
    Path("migrations/versions/0003_phase3i_scheduled_digest_deliveries.py"),
)
PHASE_3I_DIGEST_AUDIT_SOURCE_OBJECTS = (
    ScheduledDigestDeliveryModel,
    SqlAlchemyScheduledDigestDeliveryStore,
)
PHASE_3I_DIGEST_AUDIT_FORBIDDEN_TERMS = (
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
PHASE_3I_SNAPSHOT_VERSIONING_FILES = (
    Path("app/core/constants.py"),
    Path("app/domain/entities/features.py"),
    Path("app/domain/entities/context.py"),
    Path("app/domain/entities/analysis.py"),
    Path("app/domain/feature_engine.py"),
    Path("app/domain/context_engine.py"),
    Path("app/domain/analysis_engine.py"),
)
PHASE_3I_SNAPSHOT_VERSIONING_FORBIDDEN_TERMS = (
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
PHASE_4D_REGISTRY_OBJECTS = (
    strategy_registry.StrategyRuleSetRegistryItem,
    strategy_registry.StrategyRuleSetRegistrySnapshot,
    StrategyRuleSetRegistry,
)
PHASE_4D_FORBIDDEN_RUNTIME_IMPORTS = (
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
PHASE_4D_FORBIDDEN_BEHAVIOR_TERMS = (
    "strategy_engine",
    "strategy_evaluator",
    "rule_engine",
    "rule_evaluator",
    "evaluate_rules",
    "market_data_rule",
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
    texts = [path.read_text(encoding="utf-8") for path in PHASE_3I_DIGEST_AUDIT_FILES]
    texts.extend(
        inspect.getsource(source_object) for source_object in PHASE_3I_DIGEST_AUDIT_SOURCE_OBJECTS
    )
    for index, text in enumerate(texts):
        lowered = text.lower()
        for term in PHASE_3I_DIGEST_AUDIT_FORBIDDEN_TERMS:
            if term.lower() in lowered:
                offenders.append(f"phase3i-source-{index}: {term}")

    assert offenders == []


def test_phase3i_snapshot_versioning_files_do_not_add_decision_or_execution_terms() -> None:
    offenders: list[str] = []
    for file_path in PHASE_3I_SNAPSHOT_VERSIONING_FILES:
        text = file_path.read_text(encoding="utf-8")
        lowered = text.lower()
        for term in PHASE_3I_SNAPSHOT_VERSIONING_FORBIDDEN_TERMS:
            if term.lower() in lowered:
                offenders.append(f"{file_path}: {term}")

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


def test_phase4d_registry_objects_are_domain_only() -> None:
    offenders: list[str] = []
    texts = [inspect.getsource(source_object) for source_object in PHASE_4D_REGISTRY_OBJECTS]
    for index, text in enumerate(texts):
        lowered = text.lower()
        for term in PHASE_4D_FORBIDDEN_RUNTIME_IMPORTS:
            if term.lower() in lowered:
                offenders.append(f"phase4d-registry-{index}: {term}")

    assert offenders == []


def test_phase4d_registry_objects_do_not_add_evaluation_or_execution_terms() -> None:
    offenders: list[str] = []
    texts = [inspect.getsource(source_object) for source_object in PHASE_4D_REGISTRY_OBJECTS]
    for index, text in enumerate(texts):
        lowered = text.lower()
        for term in PHASE_4D_FORBIDDEN_BEHAVIOR_TERMS:
            if term.lower() in lowered:
                offenders.append(f"phase4d-registry-{index}: {term}")

    assert offenders == []


def test_phase4d_registry_signatures_have_no_market_or_runtime_inputs() -> None:
    assert tuple(inspect.signature(StrategyRuleSetRegistry.list_keys).parameters) == ("self",)
    assert tuple(inspect.signature(StrategyRuleSetRegistry.load_builtin_rulesets).parameters) == (
        "self",
        "checked_at",
    )
    assert tuple(inspect.signature(StrategyRuleSetRegistry.get_by_key).parameters) == (
        "self",
        "key",
        "checked_at",
    )


def test_phase4d_registry_module_does_not_import_runtime_dependencies() -> None:
    source = inspect.getsource(strategy_ruleset_registry_module).lower()
    import_lines = tuple(
        line
        for line in source.splitlines()
        if line.startswith("import ") or line.startswith("from ")
    )

    offenders = [
        term
        for term in PHASE_4D_FORBIDDEN_RUNTIME_IMPORTS
        if any(term.lower() in line for line in import_lines)
    ]

    assert offenders == []


def test_phase4d_does_not_add_registry_api_routes() -> None:
    route_files = tuple(Path("app/api/routes").glob("*.py"))
    offenders = [
        str(file_path)
        for file_path in route_files
        if "registry" in file_path.name.lower()
        or "ruleset" in file_path.name.lower()
        or "strategy" in file_path.name.lower()
        or "StrategyRuleSetRegistry" in file_path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_phase4d_does_not_add_telegram_registry_or_signal_handlers() -> None:
    source = Path("app/telegram/commands.py").read_text(encoding="utf-8")

    assert "registry_command" not in source
    assert "strategy_command" not in source
    assert "ruleset_command" not in source
    assert "signal_command" not in source
    assert 'CommandHandler("registry"' not in source
    assert 'CommandHandler("strategy"' not in source
    assert 'CommandHandler("signal"' not in source
    assert "StrategyRuleSetRegistry" not in source


def test_phase4d_does_not_add_scheduler_registry_or_signal_jobs() -> None:
    scheduler_text = "\n".join(
        file_path.read_text(encoding="utf-8") for file_path in Path("app/scheduler").glob("*.py")
    )

    assert "StrategyRuleSetRegistry" not in scheduler_text
    assert "registry_job" not in scheduler_text
    assert "ruleset_registry_job" not in scheduler_text
    assert "generate_signal" not in scheduler_text


def test_phase4d_does_not_add_strategy_registry_service() -> None:
    service_files = tuple(Path("app/services").glob("*.py"))
    offenders = [
        str(file_path)
        for file_path in service_files
        if "registry" in file_path.name.lower()
        or "strategy" in file_path.name.lower()
        or "ruleset" in file_path.name.lower()
        or "StrategyRuleSetRegistry" in file_path.read_text(encoding="utf-8")
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
