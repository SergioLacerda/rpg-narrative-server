from cachetools import TTLCache


class EmbeddingCache:
    def __init__(self, client):
        self.client = client
        self.cache = TTLCache(ttl=3600, max_items=512)

    async def embed(self, text: str):
        key = self._key(text)

        cached = self.cache.get(key)
        if cached:
            return cached

        vec = await self.client.embed(text)

        self.cache.set(key, vec)

        return vec

    def _key(self, text: str):
        import hashlib

        return hashlib.sha1(text.strip().lower().encode()).hexdigest()
