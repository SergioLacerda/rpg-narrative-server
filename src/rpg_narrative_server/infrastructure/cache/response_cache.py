import asyncio
from typing import Optional

class ResponseCache:
    """
    Cache simples de respostas baseado em prompt.
    Infra puro (não pertence ao domain).
    """

    def __init__(self, loader, saver):

        self._cache = None
        self._loader = loader
        self._saver = saver


    async def _load(self):

        if self._cache is None:
            self._cache = await asyncio.to_thread(self._loader)

        return self._cache


    async def get(self, key: str) -> Optional[str]:
        cache = await self._load()
        return cache.get(key)


    async def set(self, key: str, response: str):
        cache = await self._load()
        cache[key] = response
        await asyncio.to_thread(self._saver, cache)