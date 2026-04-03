from pathlib import Path

from rpg_narrative_server.config.paths import get_paths
from rpg_narrative_server.infrastructure.cache.response_cache import ResponseCache
from rpg_narrative_server.infrastructure.cache.response_cache_storage import build_file_storage


class ResponseCacheManager:
    def __init__(self):
        self._caches = {}

    def get(self, campaign_id: str) -> ResponseCache:
        if campaign_id not in self._caches:
            path = Path(get_paths(campaign_id)["response_cache"])

            loader, saver = build_file_storage(path)

            self._caches[campaign_id] = ResponseCache(loader, saver)

        return self._caches[campaign_id]

    def clear(self, campaign_id: str):
        self._caches.pop(campaign_id, None)

    def clear_all(self):
        self._caches.clear()
