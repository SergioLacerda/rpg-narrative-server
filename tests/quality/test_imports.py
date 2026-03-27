import ast
from pathlib import Path


SRC_PATH = Path("src")


def get_imports(file_path):

    tree = ast.parse(file_path.read_text(encoding="utf-8"))
    imports = set()

    for node in ast.walk(tree):

        # import x
        if isinstance(node, ast.Import):
            for n in node.names:
                alias = n.asname or n.name.split(".")[0]
                imports.add(alias)

        # from x import y
        elif isinstance(node, ast.ImportFrom):
            for n in node.names:
                alias = n.asname or n.name
                imports.add(alias)

    return imports


def get_used_names(file_path):

    tree = ast.parse(file_path.read_text(encoding="utf-8"))
    names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)

    return names


def test_no_unused_imports():

    errors = []

    for file in SRC_PATH.rglob("*.py"):

        if "__init__" in file.name:
            continue

        imports = get_imports(file)
        used = get_used_names(file)

        unused = imports - used

        if unused:
            errors.append(f"{file}: unused imports → {unused}")

    assert not errors, "\n".join(errors)
