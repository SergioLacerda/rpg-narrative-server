import asyncio

from rpg_narrative_server.application.dto.llm_response import LLMResponse


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

    async def get(self, key: str):
        cache = await self._load()
        data = cache.get(key)

        if not data:
            return None

        return LLMResponse.from_dict(data)

    async def set(self, key: str, response):
        cache = await self._load()

        if hasattr(response, "to_dict"):
            cache[key] = response.to_dict()
        else:
            cache[key] = {"content": str(response)}

        await asyncio.to_thread(self._saver, cache)
