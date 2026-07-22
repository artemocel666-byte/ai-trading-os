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
    assert payload["project_phase"] == "phase_6_snapshot_backed_review_foundation"


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
