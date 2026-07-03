import ast
import re
from pathlib import Path

FORBIDDEN_EXECUTION_TERMS = (
    "place_order",
    "submit_order",
    "send_order",
    "execute_order",
    "create_market_order",
    "market_order",
    "limit_order",
    "open_real_position",
    "open_position",
    "close_position",
)

FORBIDDEN_TRADING_METHODS = ("buy", "sell", "create_order")
FORBIDDEN_BROKER_IMPORT_ROOTS = (
    "MetaTrader5",
    "ccxt",
    "oandapyV20",
    "ib_insync",
    "alpaca_trade_api",
    "binance",
)
EXECUTION_ENDPOINT_RE = re.compile(r"/(?:orders?|positions?|trades?)(?:[/?:#]|$)", re.IGNORECASE)
PRODUCTION_ROOTS = (Path("app"),)


def _module_root(module_name: str) -> str:
    return module_name.split(".", maxsplit=1)[0]


def _scan_ast(file_path: Path, tree: ast.AST) -> list[tuple[Path, str]]:
    findings: list[tuple[Path, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _module_root(alias.name) in FORBIDDEN_BROKER_IMPORT_ROOTS:
                    findings.append((file_path, f"forbidden broker import: {alias.name}"))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if _module_root(module) in FORBIDDEN_BROKER_IMPORT_ROOTS:
                findings.append((file_path, f"forbidden broker import: {module}"))
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            lowered = node.name.lower()
            if lowered in FORBIDDEN_EXECUTION_TERMS:
                findings.append((file_path, f"forbidden execution definition: {node.name}"))
        elif isinstance(node, ast.Call):
            function = node.func
            if isinstance(function, ast.Name):
                lowered = function.id.lower()
                if lowered in FORBIDDEN_EXECUTION_TERMS:
                    findings.append((file_path, f"forbidden execution call: {function.id}"))
            elif isinstance(function, ast.Attribute):
                lowered = function.attr.lower()
                if lowered in FORBIDDEN_EXECUTION_TERMS or lowered in FORBIDDEN_TRADING_METHODS:
                    findings.append((file_path, f"forbidden trading method call: {function.attr}"))
        elif (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and EXECUTION_ENDPOINT_RE.search(node.value)
        ):
            findings.append((file_path, "forbidden execution HTTP endpoint"))
    return findings


def scan_files(files: list[Path]) -> list[tuple[Path, str]]:
    findings: list[tuple[Path, str]] = []
    for file_path in files:
        text = file_path.read_text(encoding="utf-8")
        lowered = text.lower()
        for term in FORBIDDEN_EXECUTION_TERMS:
            if term in lowered:
                findings.append((file_path, f"forbidden execution concept: {term}"))
        try:
            tree = ast.parse(text, filename=str(file_path))
        except SyntaxError as exc:
            findings.append((file_path, f"syntax error during scan: {exc.msg}"))
            continue
        findings.extend(_scan_ast(file_path, tree))
    return findings


def scan_production_code(root: Path) -> list[tuple[Path, str]]:
    files: list[Path] = []
    for production_root in PRODUCTION_ROOTS:
        path = root / production_root
        if not path.exists():
            continue
        for file_path in path.rglob("*.py"):
            files.append(file_path)
    return scan_files(files)


def main() -> None:
    findings = scan_production_code(Path.cwd())
    if findings:
        for file_path, term in findings:
            print(f"{file_path}: forbidden execution concept '{term}'")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
