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
