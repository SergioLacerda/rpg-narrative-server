from pathlib import Path


SRC_PATH = Path("src")

FORBIDDEN = [
    "pytest",
    "unittest",
    "mock",
    "faker",
]


def test_no_test_dependencies_in_src():

    errors = []

    for file in SRC_PATH.rglob("*.py"):

        content = file.read_text()

        for bad in FORBIDDEN:
            if f"import {bad}" in content or f"from {bad}" in content:
                errors.append(f"{file}: forbidden import '{bad}'")

    assert not errors, "\n".join(errors)


def test_no_monkeypatch_in_src():

    errors = []

    for file in SRC_PATH.rglob("*.py"):
        content = file.read_text()

        if "monkeypatch" in content:
            errors.append(f"{file}: monkeypatch found")

    assert not errors, "\n".join(errors)


def test_domain_is_pure():

    from pathlib import Path

    domain_path = Path("src/rpg_narrative_server/domain")

    errors = []

    for file in domain_path.rglob("*.py"):

        content = file.read_text()

        if "infrastructure" in content:
            errors.append(f"{file}: domain depends on infrastructure")

    assert not errors, "\n".join(errors)