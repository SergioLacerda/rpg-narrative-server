# application/services/embedding_strategy.py

import logging
from typing import Sequence

from rpg_narrative_server.application.ports.embedding_gateway import EmbeddingGateway

logger = logging.getLogger("rpg_narrative_server.embedding.strategy")


class EmbeddingStrategy:

    def __init__(
        self,
        primary: EmbeddingGateway,
        fallback: Sequence[EmbeddingGateway] = (),
    ):
        self.primary = primary
        self.fallback = list(fallback)

    async def embed(self, text: str):

        try:
            logger.debug("Embedding primary → %s", self.primary.__class__.__name__)
            return await self.primary.embed(text)

        except Exception:
            logger.warning("Primary embedding failed")

        for provider in self.fallback:
            try:
                logger.debug("Embedding fallback → %s", provider.__class__.__name__)
                return await provider.embed(text)

            except Exception:
                logger.warning("Fallback provider failed")

        raise RuntimeError("All embedding providers failed")
