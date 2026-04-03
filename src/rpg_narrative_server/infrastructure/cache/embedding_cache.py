import hashlib

from cachetools import TTLCache


class EmbeddingCache:
    def __init__(self, client, ttl: int = 3600, max_items: int = 512):
        self.client = client
        self.cache = TTLCache(maxsize=max_items, ttl=ttl)

    # ---------------------------------------------------------
    # EMBED
    # ---------------------------------------------------------

    async def embed(self, campaign_id: str, text: str):
        if not text:
            return None

        key = self._key(campaign_id, text)

        cached = self.cache.get(key)
        if cached is not None:
            return cached

        vec = await self.client.embed(text)

        if vec is not None:
            self.cache.set(key, vec)

        return vec

    # ---------------------------------------------------------
    # KEY
    # ---------------------------------------------------------

    def _key(self, campaign_id: str, text: str):
        raw = f"{campaign_id}:{text.strip().lower()}"
        return hashlib.sha1(raw.encode()).hexdigest()

    # ---------------------------------------------------------
    # INVALIDATION
    # ---------------------------------------------------------

    def clear(self):
        self.cache.clear()
