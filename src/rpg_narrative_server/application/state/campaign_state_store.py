import json
from pathlib import Path


class CampaignStateStore:

    def __init__(self, path: Path):
        self.path = path
        self._data = self._load()

    def _load(self):
        if not self.path.exists():
            return {}

        try:
            return json.loads(self.path.file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save(self):
        self.path.write_text(json.dumps(self._data, indent=2))

    def get(self, channel_id: str):
        return self._data.get(channel_id)

    def set(self, channel_id: str, campaign_id: str):
        self._data[channel_id] = campaign_id
        self.save()
