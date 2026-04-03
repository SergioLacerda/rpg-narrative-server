from rpg_narrative_server.infrastructure.cache.semantic_cache import SemanticCache


class SemanticCacheManager:
    def __init__(self):
        self._caches = {}

    def get(self, campaign_id: str) -> SemanticCache:
        if campaign_id not in self._caches:
            self._caches[campaign_id] = SemanticCache()

        return self._caches[campaign_id]

    def clear(self, campaign_id: str):
        self._caches.pop(campaign_id, None)

    def clear_all(self):
        self._caches.clear()
