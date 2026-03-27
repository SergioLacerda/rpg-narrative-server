import ast
from pathlib import Path
from collections import defaultdict


SRC = Path("src/rpg_narrative_server")


def normalize(module: str) -> str:
    return module.split(":")[0].strip()


def is_internal(module: str) -> bool:
    return module.startswith("rpg_narrative_server")


def get_module_name(file: Path) -> str:
    return "rpg_narrative_server." + str(file.relative_to("src")).replace(
        "/", "."
    ).replace(".py", "")


def get_layer(module: str):
    if ".domain." in module:
        return "domain"
    if ".application." in module:
        return "application"
    if ".interfaces." in module:
        return "interfaces"
    if ".infrastructure." in module:
        return "infrastructure"

    return "unknown"


def get_import_graph():
    graph = defaultdict(set)

    for file in SRC.rglob("*.py"):
        module = get_module_name(file)

        tree = ast.parse(file.read_text(encoding="utf-8"))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    name = normalize(n.name)
                    if is_internal(name):
                        graph[module].add(name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    name = normalize(node.module)
                    if is_internal(name):
                        graph[module].add(name)

    return graph


def find_cycles(graph):
    visited = set()
    stack = []

    cycles = []

    def visit(node):
        if node in stack:
            idx = stack.index(node)
            cycles.append(stack[idx:] + [node])
            return

        if node in visited:
            return

        visited.add(node)
        stack.append(node)

        for neighbor in graph.get(node, []):
            visit(neighbor)

        stack.pop()

    for node in list(graph.keys()):
        visit(node)

    return cycles


def test_no_cycles():
    graph = get_import_graph()

    cycles = find_cycles(graph)

    assert not cycles, "\n\n".join(" -> ".join(cycle) for cycle in cycles)


def test_no_cross_layer_cycles():
    graph = get_import_graph()
    cycles = find_cycles(graph)

    errors = []

    for cycle in cycles:
        layers = {get_layer(m) for m in cycle}

        if len(layers) > 1:
            errors.append(f"Cross-layer cycle: {cycle}")

    assert not errors, "\n".join(errors)
