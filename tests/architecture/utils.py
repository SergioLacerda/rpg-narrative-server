# tests/architecture/utils.py

import ast


def extract_imports(file_path):

    tree = ast.parse(file_path.read_text())
    imports = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return imports
