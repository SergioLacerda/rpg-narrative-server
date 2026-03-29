from pathlib import Path

from rpg_narrative_server.config.settings import Settings
from rpg_narrative_server.infrastructure.storage.json_utils import read_json, write_json


class JSONKeyValueStore:
    def __init__(self, path: Path):
        self.path = path

    def get(self, key: str):
        data = read_json(self.path, {})
        return data.get(key)

    def set(self, key: str, value):
        data = read_json(self.path, {})
        data[key] = value
        write_json(self.path, data)

    def clear(self):
        write_json(self.path, {})

    def _should_rotate(self, data):
        app = Settings.app
        return len(data) > app.max_entries_per_file
