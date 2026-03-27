from abc import ABC, abstractmethod
from typing import Iterable, List, Optional


class EmbeddingGateway(ABC):
    """
    Port (Clean Architecture) for embedding providers.
    """

    # ---------------------------------------------
    # metadata / capabilities
    # ---------------------------------------------

    @property
    def dimension(self) -> Optional[int]:
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
    async def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        """
        raise NotImplementedError

    async def embed_batch(self, texts: Iterable[str]) -> List[List[float]]:
        """
        Optional batch implementation.

        Default fallback: sequential calls.
        Providers can override for performance.
        """
        return [await self.embed(t) for t in texts]
