# tests/architecture/test_layers.py

from pathlib import Path

from .utils import extract_imports
from .rules import RULES


SRC = Path("src/rpg_narrative_server")


def get_layer(file: Path) -> str:
    path = str(file)

    if "/domain/" in path:
        return "domain"
    if "/application/" in path:
        return "application"
    if "/interfaces/" in path:
        return "interfaces"
    if "/infrastructure/" in path:
        return "infrastructure"
    if "/shared/" in path:
        return "shared"

    return "unknown"


SRC = Path("src/rpg_narrative_server")


def test_layer_dependencies():
    errors = []

    for file in SRC.rglob("*.py"):
        layer = get_layer(file)

        if layer == "unknown":
            continue

        imports = extract_imports(file)

        for imp in imports:
            for forbidden in RULES[layer]["forbidden"]:
                if f"rpg_narrative_server.{forbidden}" in imp:
                    allowed = RULES[layer].get("allowed", [])

                    if any(imp.startswith(a) for a in allowed):
                        continue

                    errors.append(
                        f"{file} → {layer} cannot depend on {forbidden} ({imp})"
                    )

    assert not errors, "\n".join(errors)


def test_no_cross_layer_leak():
    errors = []

    for file in SRC.rglob("*.py"):
        content = file.read_text(encoding="utf-8")

        if "infrastructure" in content and "domain" in str(file):
            errors.append(f"{file} leaking infra")

    assert not errors, "\n".join(errors)
