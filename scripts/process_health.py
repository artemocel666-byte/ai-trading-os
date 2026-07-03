import os
import sys
from pathlib import Path


def process_exists(needle: str) -> bool:
    current_pid = str(os.getpid())
    for cmdline_path in Path("/proc").glob("[0-9]*/cmdline"):
        if cmdline_path.parts[-2] == current_pid:
            continue
        try:
            cmdline = cmdline_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if needle in cmdline.replace("\x00", " "):
            return True
    return False


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(2)
    raise SystemExit(0 if process_exists(sys.argv[1]) else 1)


if __name__ == "__main__":
    main()
