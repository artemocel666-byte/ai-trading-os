import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DOMAIN_FORBIDDEN_IMPORT_ROOTS = {
    "fastapi",
    "sqlalchemy",
    "telegram",
    "apscheduler",
    "asyncpg",
    "httpx",
    "openai",
}

SERVICE_FORBIDDEN_IMPORT_PREFIXES = (
    "sqlalchemy",
    "app.persistence",
)


def _imports_for(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def test_domain_layer_does_not_import_infrastructure_frameworks() -> None:
    offenders: list[str] = []
    for file_path in (PROJECT_ROOT / "app" / "domain").rglob("*.py"):
        for imported in _imports_for(file_path):
            if imported.split(".", maxsplit=1)[0] in DOMAIN_FORBIDDEN_IMPORT_ROOTS:
                offenders.append(f"{file_path.relative_to(PROJECT_ROOT)} imports {imported}")

    assert offenders == []


def test_application_services_do_not_import_persistence_or_sqlalchemy() -> None:
    offenders: list[str] = []
    for file_path in (PROJECT_ROOT / "app" / "services").rglob("*.py"):
        for imported in _imports_for(file_path):
            if imported.startswith(SERVICE_FORBIDDEN_IMPORT_PREFIXES):
                offenders.append(f"{file_path.relative_to(PROJECT_ROOT)} imports {imported}")

    assert offenders == []
