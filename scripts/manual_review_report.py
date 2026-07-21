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
