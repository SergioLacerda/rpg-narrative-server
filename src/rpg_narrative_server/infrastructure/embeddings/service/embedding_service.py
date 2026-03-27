import asyncio
import logging
from typing import Sequence, Iterable, List

from rpg_narrative_server.application.ports.embedding_gateway import EmbeddingGateway
from rpg_narrative_server.infrastructure.embeddings.core.fallback import deterministic_vector


logger = logging.getLogger("rpg_narrative_server.embedding")


class EmbeddingService:

    def __init__(
        self,
        providers: Sequence[EmbeddingGateway],
        target_dim: int = 1536,
        cache=None,
        strict: bool = False,
        max_concurrency: int = 8,
    ):
        self.providers = list(providers)
        self.target_dim = target_dim
        self.cache = cache
        self.strict = strict

        self._semaphore = asyncio.Semaphore(max_concurrency)

    # -----------------------------------------
    # internal
    # -----------------------------------------

    def _fallback(self, text: str) -> List[float]:
        logger.debug("Embedding fallback → deterministic")
        return deterministic_vector(text, self.target_dim)

    async def _call_provider(self, provider, text: str) -> List[float]:
        async with self._semaphore:
            return await provider.embed(text)

    def _validate_vector(self, vec: List[float], provider_name: str) -> List[float]:

        if not isinstance(vec, list):
            raise RuntimeError(f"{provider_name} returned invalid vector type")

        if not vec:
            raise RuntimeError(f"{provider_name} returned empty vector")

        if len(vec) != self.target_dim:
            logger.warning(
                "Embedding dimension mismatch → provider=%s got=%d expected=%d",
                provider_name,
                len(vec),
                self.target_dim,
            )

        return vec

    # -----------------------------------------
    # single
    # -----------------------------------------

    async def embed(self, text: str) -> List[float]:

        text = (text or "").strip()

        if not text:
            return self._fallback(text)

        # cache
        if self.cache:
            cached = await self.cache.get(text)
            if cached:
                logger.debug("Embedding cache hit")
                return cached

        # providers
        for provider in self.providers:
            name = provider.__class__.__name__

            try:
                logger.debug("Embedding attempt → %s", name)

                vec = await self._call_provider(provider, text)
                vec = self._validate_vector(vec, name)

                if self.cache:
                    await self.cache.set(text, vec)

                logger.info("Embedding success → %s", name)

                return vec

            except Exception:
                logger.warning("Embedding failed → %s", name, exc_info=True)

        if self.strict:
            raise RuntimeError("All embedding providers failed")

        logger.error("Embedding fallback triggered")

        vec = self._fallback(text)

        if self.cache:
            await self.cache.set(text, vec)

        return vec

    # -----------------------------------------
    # batch 
    # -----------------------------------------

    async def embed_batch(self, texts: Iterable[str]) -> List[List[float]]:

        texts = [(t or "").strip() for t in texts]

        if not texts:
            return []

        for provider in self.providers:
            if getattr(provider, "supports_batch", False):
                name = provider.__class__.__name__

                try:
                    logger.debug("Batch embedding → %s", name)

                    vectors = await provider.embed_batch(texts)

                    validated = [
                        self._validate_vector(v, name) for v in vectors
                    ]

                    logger.info("Batch embedding success → %s", name)

                    return validated

                except Exception:
                    logger.warning("Batch provider failed → %s", name, exc_info=True)

        logger.debug("Batch fallback → parallel single calls")

        return await asyncio.gather(*[
            self.embed(t) for t in texts
        ])