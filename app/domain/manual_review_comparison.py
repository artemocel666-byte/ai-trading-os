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
