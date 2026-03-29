import json
from pathlib import Path

DEFAULT_FILES = {
    "documents.json": {},
    "metadata.json": {},
    "vectors.json": {},
    "tokens.json": {},
}


def ensure_storage_structure(base: Path):
    base.mkdir(parents=True, exist_ok=True)

    for name, default in DEFAULT_FILES.items():
        path = base / name

        if not path.exists():
            path.write_text(json.dumps(default, indent=2))


def ensure_memory_structure(base: Path):
    memory = base / "memory"
    memory.mkdir(parents=True, exist_ok=True)

    memory_files = {
        "events.json": [],
        "narrative_graph.json": {},
        "response_cache.json": {},
    }

    for name, default in memory_files.items():
        path = memory / name

        if not path.exists():
            path.write_text(json.dumps(default, indent=2))
