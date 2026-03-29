import asyncio
from abc import ABC, abstractmethod
from collections.abc import Iterable


class EmbeddingGateway(ABC):
    """
    Port (Clean Architecture) for embedding providers.
    """

    # ---------------------------------------------
    # metadata / capabilities
    # ---------------------------------------------

    @property
    def dimension(self) -> int | None:
        """
        Embedding vector size (e.g. 1536).
        Can be None if unknown.
        """
        return None

    @property
    def supports_batch(self) -> bool:
        """
        Whether the provider supports batch embedding natively.
        """
        return False

    # ---------------------------------------------
    # core methods
    # ---------------------------------------------

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.
        """
        raise NotImplementedError

    async def embed_batch(
        self,
        texts: Iterable[str],
        *,
        concurrency: int = 5,
    ) -> list[list[float]]:
        """
        Default batch implementation.

        - Uses sequential fallback if concurrency=1
        - Uses limited concurrency otherwise
        - Providers should override for native batch support
        """

        texts_list = list(texts)

        if not texts_list:
            return []

        # -----------------------------------------
        # Sequential (safe fallback)
        # -----------------------------------------
        if concurrency <= 1:
            return [await self.embed(t) for t in texts_list]

        # -----------------------------------------
        # Concurrent execution (bounded)
        # -----------------------------------------
        semaphore = asyncio.Semaphore(concurrency)

        async def _embed_one(text: str) -> list[float]:
            async with semaphore:
                return await self.embed(text)

        tasks = [_embed_one(t) for t in texts_list]

        return await asyncio.gather(*tasks)
