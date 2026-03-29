import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import Any


class InflightDeduplicator:
    """
    Evita execução duplicada de operações async.

    - deduplica chamadas concorrentes
    - mantém micro-cache com TTL
    """

    def __init__(self, ttl: float = 2.0):
        self._inflight: dict[str, asyncio.Task] = {}
        self._recent: dict[str, tuple[float, Any]] = {}

        self._ttl = ttl

    # ---------------------------------------------------------
    # execução deduplicada
    # ---------------------------------------------------------

    async def run(self, key: str, coro_factory: Callable[[], Awaitable[Any]]) -> Any:
        now = time.monotonic()

        # ---------------------------------------------------------
        # micro-cache
        # ---------------------------------------------------------

        if key in self._recent:
            ts, value = self._recent[key]

            if now - ts < self._ttl:
                return value

            del self._recent[key]

        # ---------------------------------------------------------
        # inflight dedup
        # ---------------------------------------------------------

        if key in self._inflight:
            return await self._inflight[key]

        task = asyncio.create_task(coro_factory())

        self._inflight[key] = task

        try:
            result = await task

            self._recent[key] = (time.monotonic(), result)

            return result

        finally:
            self._inflight.pop(key, None)

    # ---------------------------------------------------------
    # limpeza manual (opcional)
    # ---------------------------------------------------------

    def clear(self):
        self._inflight.clear()
        self._recent.clear()
