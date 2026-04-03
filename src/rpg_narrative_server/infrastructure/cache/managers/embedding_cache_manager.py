from rpg_narrative_server.infrastructure.cache.embedding_cache import EmbeddingCache


class EmbeddingCacheManager:
    def __init__(self, client):
        self.client = client
        self._caches = {}

    def get(self, campaign_id: str) -> EmbeddingCache:
        if campaign_id not in self._caches:
            self._caches[campaign_id] = EmbeddingCache(self.client)

        return self._caches[campaign_id]

    def clear(self, campaign_id: str):
        self._caches.pop(campaign_id, None)

    def clear_all(self):
        self._caches.clear()
