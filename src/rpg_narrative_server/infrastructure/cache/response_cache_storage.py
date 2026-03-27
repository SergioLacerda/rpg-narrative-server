import json
from pathlib import Path


def build_file_storage(path: Path):

    def load():

        if not path.exists():
            return {}

        try:
            return json.loads(path.read_text())
        except Exception:
            return {}

    def save(data: dict):
        path.parent.mkdir(parents=True, exist_ok=True)

        tmp_path = path.with_suffix(".tmp")

        tmp_path.write_text(json.dumps(data, indent=2))
        tmp_path.replace(path)

    return load, save