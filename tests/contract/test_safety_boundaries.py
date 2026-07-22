import inspect
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

import app.domain.disabled_pipeline_report_shell as disabled_pipeline_report_shell_module
import app.domain.manual_review_comparison as manual_review_comparison_module
import app.domain.manual_review_report_builder as manual_review_report_builder_module
import app.domain.snapshot_review as snapshot_review_module
import app.domain.strategy_decision_composer as strategy_decision_composer_module
import app.domain.strategy_field_resolver as strategy_field_resolver_module
import app.domain.strategy_rule_evaluator as strategy_rule_evaluator_module
import app.domain.strategy_ruleset_registry as strategy_ruleset_registry_module
import app.domain.strategy_ruleset_validator as strategy_ruleset_validator_module
from app.adapters.disabled import (
    DisabledEconomicCalendarProvider,
    DisabledLLMProvider,
    DisabledMarketDataProvider,
)
from app.core.enums import Decision
from app.core.exceptions import IntegrationDisabledError
from app.domain.analysis_engine import AnalysisEngine
from app.domain.disabled_pipeline_report_shell import DisabledPipelineReportShell
from app.domain.entities import (
    Timeframe,
    manual_review,
    pipeline_decision,
    pipeline_report,
    rule_evaluation,
    signal_contract,
    strategy_registry,
    strategy_rules,
    strategy_validation,
)
from app.domain.manual_review_report_builder import ManualReviewReportBuilder
from app.domain.strategy_decision_composer import StrategyDecisionComposer
from app.domain.strategy_field_resolver import resolve_field
from app.domain.strategy_rule_evaluator import StrategyRuleEvaluator
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
PHASE_4E_REPORT_OBJECTS = (
    pipeline_report.DisabledPipelineBlocker,
    pipeline_report.DisabledPipelineBlockerCode,
    pipeline_report.DisabledPipelineReport,
    pipeline_report.DisabledPipelineStatus,
    DisabledPipelineReportShell,
)
PHASE_4E_FORBIDDEN_RUNTIME_IMPORTS = (
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
PHASE_4E_FORBIDDEN_BEHAVIOR_TERMS = (
    "strategy_engine",
    "trading_decision_engine",
    "decision_engine",
    "strategy_evaluator",
    "rule_engine",
    "rule_evaluator",
    "evaluate_rules",
    "market_data_rule",
    "generate_signal",
    "signal_generator",
    "signal_engine",
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
PHASE_4F_EVALUATOR_OBJECTS = (
    rule_evaluation.RuleEvaluationResult,
    rule_evaluation.RuleEvaluationStatus,
    rule_evaluation.RuleSetEvaluationReport,
    rule_evaluation.RuleSetEvaluationStatus,
    StrategyRuleEvaluator,
)
PHASE_4F_FORBIDDEN_RUNTIME_IMPORTS = (
    "app.domain.entities.signal_contract",
    "app.adapters",
    "app.persistence",
    "app.telegram",
    "app.scheduler",
    "app.api",
    "sqlalchemy",
    "fastapi",
    "httpx",
    "openai",
)
PHASE_4F_FORBIDDEN_BEHAVIOR_TERMS = (
    "strategy_engine",
    "trading_decision_engine",
    "decision_engine",
    "generate_signal",
    "signal_generator",
    "signal_engine",
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
PHASE_4G_COMPOSER_OBJECTS = (
    pipeline_decision.PipelineDecisionReport,
    pipeline_decision.PipelineDecisionStatus,
    pipeline_decision.SkippedRuleset,
    pipeline_decision.SkippedRulesetReason,
    StrategyDecisionComposer,
)
PHASE_4G_FORBIDDEN_RUNTIME_IMPORTS = (
    "app.domain.entities.signal_contract",
    "app.adapters",
    "app.persistence",
    "app.telegram",
    "app.scheduler",
    "app.api",
    "sqlalchemy",
    "fastapi",
    "httpx",
    "openai",
)
PHASE_4G_FORBIDDEN_BEHAVIOR_TERMS = (
    "strategy_engine",
    "trading_decision_engine",
    "generate_signal",
    "signal_generator",
    "signal_engine",
    "signalcontract",
    "signal_contract",
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
PHASE_5_DOMAIN_OBJECTS = (
    manual_review.ManualReviewIssue,
    manual_review.ManualReviewSection,
    manual_review.ManualReviewReport,
    ManualReviewReportBuilder,
    manual_review_comparison_module.ManualReviewComparison,
    manual_review_comparison_module.compare_manual_review_reports,
    manual_review_comparison_module.build_manual_review_quality_summary,
)
PHASE_5_FILES = (
    Path("app/domain/entities/manual_review.py"),
    Path("app/domain/manual_review_report_builder.py"),
    Path("app/domain/manual_review_comparison.py"),
    Path("scripts/manual_review_report.py"),
    Path("app/telegram/manual_review_formatter.py"),
)
PHASE_5_FORBIDDEN_RUNTIME_IMPORTS = (
    "app.adapters",
    "app.persistence",
    "app.scheduler",
    "app.api",
    "sqlalchemy",
    "fastapi",
    "httpx",
    "openai",
)
PHASE_5_FORBIDDEN_BEHAVIOR_TERMS = (
    "strategy_engine",
    "decision_engine",
    "evaluate_rules",
    "evaluate_ruleset",
    "generate_signal",
    "signal_generator",
    "signal_engine",
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
PHASE_6_FILES = (
    Path("app/domain/snapshot_review.py"),
    Path("app/telegram/snapshot_review_formatter.py"),
)
PHASE_6_FORBIDDEN_RUNTIME_IMPORTS = (
    "app.domain.entities.signal_contract",
    "app.adapters",
    "app.persistence",
    "app.scheduler",
    "app.api",
    "sqlalchemy",
    "fastapi",
    "httpx",
    "openai",
)
PHASE_6_FORBIDDEN_BEHAVIOR_TERMS = (
    "strategy_engine",
    "generate_signal",
    "signal_generator",
    "signal_engine",
    "signalcontract",
    "signal_contract",
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


def test_phase4e_report_shell_objects_are_domain_only() -> None:
    offenders: list[str] = []
    texts = [inspect.getsource(source_object) for source_object in PHASE_4E_REPORT_OBJECTS]
    for index, text in enumerate(texts):
        lowered = text.lower()
        for term in PHASE_4E_FORBIDDEN_RUNTIME_IMPORTS:
            if term.lower() in lowered:
                offenders.append(f"phase4e-report-{index}: {term}")

    assert offenders == []


def test_phase4e_report_shell_objects_do_not_add_evaluation_or_execution_terms() -> None:
    offenders: list[str] = []
    texts = [inspect.getsource(source_object) for source_object in PHASE_4E_REPORT_OBJECTS]
    for index, text in enumerate(texts):
        lowered = text.lower()
        for term in PHASE_4E_FORBIDDEN_BEHAVIOR_TERMS:
            if term.lower() in lowered:
                offenders.append(f"phase4e-report-{index}: {term}")

    assert offenders == []


def test_phase4e_report_shell_signatures_have_no_market_or_runtime_inputs() -> None:
    assert tuple(inspect.signature(DisabledPipelineReportShell.__init__).parameters) == (
        "self",
        "registry",
        "enabled",
    )
    assert tuple(inspect.signature(DisabledPipelineReportShell.build_report).parameters) == (
        "self",
        "created_at",
    )


def test_phase4e_report_shell_module_does_not_import_runtime_dependencies() -> None:
    source = inspect.getsource(disabled_pipeline_report_shell_module).lower()
    import_lines = tuple(
        line
        for line in source.splitlines()
        if line.startswith("import ") or line.startswith("from ")
    )

    offenders = [
        term
        for term in PHASE_4E_FORBIDDEN_RUNTIME_IMPORTS
        if any(term.lower() in line for line in import_lines)
    ]

    assert offenders == []


def test_phase4e_report_model_has_no_decision_signal_price_or_scoring_fields() -> None:
    fields = set(pipeline_report.DisabledPipelineReport.model_fields)

    assert fields.isdisjoint(
        {
            "decision",
            "recommendation",
            "signal_direction",
            "direction",
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
    )


def test_phase4e_does_not_add_pipeline_api_routes() -> None:
    route_files = tuple(Path("app/api/routes").glob("*.py"))
    offenders = [
        str(file_path)
        for file_path in route_files
        if "pipeline" in file_path.name.lower()
        or "strategy" in file_path.name.lower()
        or "signal" in file_path.name.lower()
        or "DisabledPipelineReport" in file_path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_phase4e_does_not_add_telegram_pipeline_or_signal_handlers() -> None:
    source = Path("app/telegram/commands.py").read_text(encoding="utf-8")

    assert "pipeline_command" not in source
    assert "strategy_command" not in source
    assert "signal_command" not in source
    assert 'CommandHandler("pipeline"' not in source
    assert 'CommandHandler("signal"' not in source
    assert "DisabledPipelineReport" not in source


def test_phase4e_does_not_add_scheduler_pipeline_or_signal_jobs() -> None:
    scheduler_text = "\n".join(
        file_path.read_text(encoding="utf-8") for file_path in Path("app/scheduler").glob("*.py")
    )

    assert "DisabledPipelineReportShell" not in scheduler_text
    assert "pipeline_job" not in scheduler_text
    assert "generate_signal" not in scheduler_text


def test_phase4e_does_not_add_disabled_pipeline_service() -> None:
    service_files = tuple(Path("app/services").glob("*.py"))
    offenders = [
        str(file_path)
        for file_path in service_files
        if "pipeline" in file_path.name.lower()
        or "strategy" in file_path.name.lower()
        or "DisabledPipelineReport" in file_path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_phase4f_evaluator_objects_do_not_import_forbidden_runtime_dependencies() -> None:
    offenders: list[str] = []
    texts = [inspect.getsource(source_object) for source_object in PHASE_4F_EVALUATOR_OBJECTS]
    for index, text in enumerate(texts):
        lowered = text.lower()
        for term in PHASE_4F_FORBIDDEN_RUNTIME_IMPORTS:
            if term.lower() in lowered:
                offenders.append(f"phase4f-evaluator-{index}: {term}")

    assert offenders == []


def test_phase4f_evaluator_objects_do_not_add_generation_or_execution_terms() -> None:
    offenders: list[str] = []
    texts = [inspect.getsource(source_object) for source_object in PHASE_4F_EVALUATOR_OBJECTS]
    for index, text in enumerate(texts):
        lowered = text.lower()
        for term in PHASE_4F_FORBIDDEN_BEHAVIOR_TERMS:
            if term.lower() in lowered:
                offenders.append(f"phase4f-evaluator-{index}: {term}")

    assert offenders == []


def test_phase4f_evaluator_signatures_are_locked() -> None:
    assert tuple(inspect.signature(StrategyRuleEvaluator.evaluate_rule).parameters) == (
        "self",
        "rule",
        "snapshot",
    )
    assert tuple(inspect.signature(StrategyRuleEvaluator.evaluate_ruleset).parameters) == (
        "self",
        "ruleset",
        "snapshot",
        "evaluated_at",
    )


def test_phase4f_modules_do_not_import_forbidden_runtime_dependencies() -> None:
    for module in (strategy_rule_evaluator_module, strategy_field_resolver_module):
        source = inspect.getsource(module).lower()
        import_lines = tuple(
            line
            for line in source.splitlines()
            if line.startswith("import ") or line.startswith("from ")
        )
        offenders = [
            term
            for term in PHASE_4F_FORBIDDEN_RUNTIME_IMPORTS
            if any(term.lower() in line for line in import_lines)
        ]

        assert offenders == []


def test_phase4f_report_models_have_no_price_or_direction_fields() -> None:
    forbidden_fields = {
        "decision",
        "recommendation",
        "signal_direction",
        "direction",
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

    assert set(rule_evaluation.RuleSetEvaluationReport.model_fields).isdisjoint(forbidden_fields)
    assert set(rule_evaluation.RuleEvaluationResult.model_fields).isdisjoint(forbidden_fields)


def test_phase4f_evaluation_report_must_remain_non_actionable() -> None:
    with pytest.raises(ValidationError):
        rule_evaluation.RuleSetEvaluationReport(
            ruleset_version="v1",
            strategy_version="v1",
            ruleset_name="test",
            status=rule_evaluation.RuleSetEvaluationStatus.READY_FOR_REVIEW,
            evaluated_at=datetime.now(UTC),
            source_snapshot_id="a" * 64,
            results=(),
            blocking_failure_count=0,
            required_failure_count=0,
            warning_failure_count=0,
            is_actionable=True,
        )


def test_phase4f_unknown_field_ref_resolves_to_none_without_raising() -> None:
    snapshot = AnalysisEngine().build_snapshot(
        pair=CurrencyPair(value="EURUSD"),
        timeframe=Timeframe.M15,
        window_start=datetime(2026, 7, 20, 8, 0, tzinfo=UTC),
        window_end=datetime(2026, 7, 20, 8, 15, tzinfo=UTC),
        as_of=datetime(2026, 7, 20, 8, 15, tzinfo=UTC),
        candles=[],
        economic_events=[],
        moving_average_windows=(3,),
    )

    assert resolve_field("unknown_context.does_not_exist", snapshot) is None


def test_phase4f_does_not_add_strategy_evaluation_api_routes() -> None:
    route_files = tuple(Path("app/api/routes").glob("*.py"))
    offenders = [
        str(file_path)
        for file_path in route_files
        if "evaluat" in file_path.name.lower()
        or "strategy" in file_path.name.lower()
        or "signal" in file_path.name.lower()
        or "StrategyRuleEvaluator" in file_path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_phase4f_does_not_add_telegram_evaluation_or_signal_handlers() -> None:
    source = Path("app/telegram/commands.py").read_text(encoding="utf-8")

    assert "evaluate_command" not in source
    assert "strategy_command" not in source
    assert "signal_command" not in source
    assert 'CommandHandler("evaluate"' not in source
    assert 'CommandHandler("signal"' not in source
    assert "StrategyRuleEvaluator" not in source


def test_phase4f_does_not_add_scheduler_evaluation_or_signal_jobs() -> None:
    scheduler_text = "\n".join(
        file_path.read_text(encoding="utf-8") for file_path in Path("app/scheduler").glob("*.py")
    )

    assert "StrategyRuleEvaluator" not in scheduler_text
    assert "evaluation_job" not in scheduler_text
    assert "generate_signal" not in scheduler_text


def test_phase4f_does_not_add_strategy_evaluation_service() -> None:
    service_files = tuple(Path("app/services").glob("*.py"))
    offenders = [
        str(file_path)
        for file_path in service_files
        if "evaluat" in file_path.name.lower()
        or "strategy" in file_path.name.lower()
        or "StrategyRuleEvaluator" in file_path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_phase4g_composer_objects_do_not_import_forbidden_runtime_dependencies() -> None:
    offenders: list[str] = []
    texts = [inspect.getsource(source_object) for source_object in PHASE_4G_COMPOSER_OBJECTS]
    for index, text in enumerate(texts):
        lowered = text.lower()
        for term in PHASE_4G_FORBIDDEN_RUNTIME_IMPORTS:
            if term.lower() in lowered:
                offenders.append(f"phase4g-composer-{index}: {term}")

    assert offenders == []


def test_phase4g_composer_objects_do_not_add_generation_or_execution_terms() -> None:
    offenders: list[str] = []
    texts = [inspect.getsource(source_object) for source_object in PHASE_4G_COMPOSER_OBJECTS]
    for index, text in enumerate(texts):
        lowered = text.lower()
        for term in PHASE_4G_FORBIDDEN_BEHAVIOR_TERMS:
            if term.lower() in lowered:
                offenders.append(f"phase4g-composer-{index}: {term}")

    assert offenders == []


def test_phase4g_composer_signature_is_locked() -> None:
    assert tuple(inspect.signature(StrategyDecisionComposer.compose).parameters) == (
        "self",
        "snapshot",
        "evaluated_at",
    )


def test_phase4g_module_does_not_import_forbidden_runtime_dependencies() -> None:
    source = inspect.getsource(strategy_decision_composer_module).lower()
    import_lines = tuple(
        line
        for line in source.splitlines()
        if line.startswith("import ") or line.startswith("from ")
    )
    offenders = [
        term
        for term in PHASE_4G_FORBIDDEN_RUNTIME_IMPORTS
        if any(term.lower() in line for line in import_lines)
    ]

    assert offenders == []


def test_phase4g_report_has_no_price_or_direction_fields() -> None:
    forbidden_fields = {
        "decision",
        "recommendation",
        "signal_direction",
        "direction",
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

    assert set(pipeline_decision.PipelineDecisionReport.model_fields).isdisjoint(forbidden_fields)


def test_phase4g_pipeline_decision_report_must_remain_non_actionable() -> None:
    with pytest.raises(ValidationError):
        pipeline_decision.PipelineDecisionReport(
            pipeline_version="v1",
            project_phase="test",
            status=pipeline_decision.PipelineDecisionStatus.READY_FOR_REVIEW,
            evaluated_at=datetime.now(UTC),
            source_snapshot_id="a" * 64,
            ruleset_reports=(),
            skipped_rulesets=(),
            evaluated_ruleset_count=0,
            blocked_ruleset_count=0,
            not_ready_ruleset_count=0,
            is_actionable=True,
        )


def test_phase4g_does_not_add_decision_api_routes() -> None:
    route_files = tuple(Path("app/api/routes").glob("*.py"))
    offenders = [
        str(file_path)
        for file_path in route_files
        if "decision" in file_path.name.lower()
        or "compose" in file_path.name.lower()
        or "strategy" in file_path.name.lower()
        or "signal" in file_path.name.lower()
        or "StrategyDecisionComposer" in file_path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_phase4g_does_not_add_telegram_decision_or_signal_handlers() -> None:
    source = Path("app/telegram/commands.py").read_text(encoding="utf-8")

    assert "decision_command" not in source
    assert "strategy_command" not in source
    assert "signal_command" not in source
    assert 'CommandHandler("decision"' not in source
    assert 'CommandHandler("signal"' not in source
    assert "StrategyDecisionComposer" not in source


def test_phase4g_does_not_add_scheduler_decision_or_signal_jobs() -> None:
    scheduler_text = "\n".join(
        file_path.read_text(encoding="utf-8") for file_path in Path("app/scheduler").glob("*.py")
    )

    assert "StrategyDecisionComposer" not in scheduler_text
    assert "decision_job" not in scheduler_text
    assert "generate_signal" not in scheduler_text


def test_phase4g_does_not_add_strategy_decision_service() -> None:
    service_files = tuple(Path("app/services").glob("*.py"))
    offenders = [
        str(file_path)
        for file_path in service_files
        if "decision" in file_path.name.lower()
        or "strategy" in file_path.name.lower()
        or "StrategyDecisionComposer" in file_path.read_text(encoding="utf-8")
    ]

    assert offenders == []


def test_phase5_domain_objects_do_not_import_forbidden_runtime_dependencies() -> None:
    offenders: list[str] = []
    for index, source_object in enumerate(PHASE_5_DOMAIN_OBJECTS):
        source = inspect.getsource(source_object).lower()
        import_lines = tuple(
            line
            for line in source.splitlines()
            if line.startswith("import ") or line.startswith("from ")
        )
        for term in PHASE_5_FORBIDDEN_RUNTIME_IMPORTS:
            if any(term.lower() in line for line in import_lines):
                offenders.append(f"phase5-object-{index}: {term}")

    assert offenders == []


def test_phase5_modules_do_not_add_trading_behavior_terms() -> None:
    offenders: list[str] = []
    for file_path in PHASE_5_FILES:
        source = file_path.read_text(encoding="utf-8")
        lowered = source.lower()
        for term in PHASE_5_FORBIDDEN_BEHAVIOR_TERMS:
            if term.lower() in lowered:
                offenders.append(f"{file_path}: {term}")

    assert offenders == []


def test_phase5_builder_has_no_market_database_or_messaging_dependency() -> None:
    source = inspect.getsource(manual_review_report_builder_module).lower()
    forbidden_terms = (
        "app.domain.entities.market_data",
        "app.domain.entities.analysis",
        "app.persistence",
        "app.telegram",
        "app.scheduler",
        "app.adapters",
        "sqlalchemy",
        "httpx",
        "openai",
    )

    assert not any(term in source for term in forbidden_terms)


def test_phase5_comparison_is_in_memory_only() -> None:
    source = inspect.getsource(manual_review_comparison_module).lower()
    forbidden_terms = (
        "app.persistence",
        "sqlalchemy",
        "write_text",
        "write_bytes",
        "open(",
        "httpx",
    )

    assert not any(term in source for term in forbidden_terms)


def test_phase5_models_have_no_trading_output_fields() -> None:
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

    assert set(manual_review.ManualReviewReport.model_fields).isdisjoint(forbidden_fields)
    assert set(manual_review.ManualReviewSection.model_fields).isdisjoint(forbidden_fields)
    assert set(manual_review.ManualReviewIssue.model_fields).isdisjoint(forbidden_fields)
    assert set(manual_review_comparison_module.ManualReviewComparison.model_fields).isdisjoint(
        forbidden_fields
    )


def test_phase5_adds_no_api_route_or_scheduler_job() -> None:
    route_source = "\n".join(
        file_path.read_text(encoding="utf-8") for file_path in Path("app/api/routes").glob("*.py")
    )
    scheduler_source = "\n".join(
        file_path.read_text(encoding="utf-8") for file_path in Path("app/scheduler").glob("*.py")
    )

    assert "ManualReview" not in route_source
    assert "manual_review" not in route_source
    assert "ManualReview" not in scheduler_source
    assert "manual_review" not in scheduler_source
    assert 'CommandHandler("signal"' not in Path("app/telegram/commands.py").read_text(
        encoding="utf-8"
    )


def test_phase5_cli_has_no_runtime_file_writing() -> None:
    source = Path("scripts/manual_review_report.py").read_text(encoding="utf-8")

    assert "--output" not in source
    assert "write_text" not in source
    assert "write_bytes" not in source
    assert "open(" not in source


def test_phase5_adds_no_migration_and_phase3j_route_remains_absent() -> None:
    assert list(Path("migrations/versions").glob("*phase5*")) == []
    assert not Path("app/api/routes/digest_deliveries.py").exists()


def test_phase6_modules_do_not_import_forbidden_runtime_dependencies() -> None:
    source = inspect.getsource(snapshot_review_module).lower()
    import_lines = tuple(
        line
        for line in source.splitlines()
        if line.startswith("import ") or line.startswith("from ")
    )
    offenders = [
        term
        for term in PHASE_6_FORBIDDEN_RUNTIME_IMPORTS
        if any(term.lower() in line for line in import_lines)
    ]

    assert offenders == []


def test_phase6_files_do_not_add_trading_behavior_terms() -> None:
    offenders: list[str] = []
    for file_path in PHASE_6_FILES:
        lowered = file_path.read_text(encoding="utf-8").lower()
        for term in PHASE_6_FORBIDDEN_BEHAVIOR_TERMS:
            if term.lower() in lowered:
                offenders.append(f"{file_path}: {term}")

    assert offenders == []


def test_phase6_snapshot_review_produces_non_actionable_report() -> None:
    from datetime import timedelta
    from decimal import Decimal

    from app.domain.entities import Candle
    from app.domain.snapshot_review import build_snapshot_backed_manual_review_report
    from app.domain.value_objects import CurrencyPair as _CurrencyPair

    pair = _CurrencyPair(value="EURUSD")
    base_time = datetime(2026, 7, 20, 9, 0, tzinfo=UTC)
    candles = [
        Candle(
            provider="phase6-safety-test",
            pair=pair,
            timeframe=Timeframe.M15,
            open_time=base_time + (index * timedelta(minutes=15)),
            close_time=base_time + ((index + 1) * timedelta(minutes=15)),
            open=Decimal("1.1000"),
            high=Decimal("1.1005"),
            low=Decimal("1.0995"),
            close=Decimal("1.1001"),
            volume=Decimal("100"),
            is_closed=True,
        )
        for index in range(3)
    ]
    snapshot = AnalysisEngine().build_snapshot(
        pair=pair,
        timeframe=Timeframe.M15,
        window_start=base_time,
        window_end=base_time + timedelta(minutes=45),
        as_of=base_time + timedelta(minutes=45),
        candles=candles,
        economic_events=[],
        moving_average_windows=(3,),
    )

    report = build_snapshot_backed_manual_review_report(snapshot, base_time)

    assert report.is_actionable is False
    assert report.enabled_for_runtime is False


def test_phase6_review_command_does_not_construct_signal_contract() -> None:
    review_source = Path("app/telegram/commands.py").read_text(encoding="utf-8")
    domain_source = Path("app/domain/snapshot_review.py").read_text(encoding="utf-8")

    assert "SignalContract(" not in domain_source
    assert "SignalContract(" not in review_source
    assert "signal_contract" not in domain_source.lower()


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
