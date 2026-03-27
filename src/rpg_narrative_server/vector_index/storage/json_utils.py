import json
from pathlib import Path
from typing import Any


# ---------------------------------------------------------
# load
# ---------------------------------------------------------


def _backup_corrupted_file(path: Path):
    try:
        backup_path = path.with_suffix(path.suffix + ".corrupted")
        path.rename(backup_path)
    except Exception:
        pass


def load_json(path: Path, default: Any):
    # ---------------------------------------------------------
    # 1. arquivo não existe → cria
    # ---------------------------------------------------------
    if not path.exists():
        save_json(path, default)
        return default

    # ---------------------------------------------------------
    # 2. tentar carregar
    # ---------------------------------------------------------
    try:
        return json.loads(path.read_text(encoding="utf-8"))

    # ---------------------------------------------------------
    # 3. arquivo corrompido → recuperar
    # ---------------------------------------------------------
    except Exception:
        _backup_corrupted_file(path)
        save_json(path, default)
        return default


# ---------------------------------------------------------
# save
# ---------------------------------------------------------


def save_json(path: Path, data: Any):
    def _default(obj):
        if isinstance(obj, set):
            return list(obj)
        raise TypeError(f"{type(obj)} not serializable")

    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=_default),
        encoding="utf-8",
    )


# ---------------------------------------------------------
# update (helper útil)
# ---------------------------------------------------------


def update_json(path: Path, updater):
    data = load_json(path, default={})

    new_data = updater(data)

    save_json(path, new_data)

    return new_data
