import asyncio
import logging

import httpx

from rpg_narrative_server.application.ports.embedding_gateway import EmbeddingGateway
from rpg_narrative_server.shared.resilience import resilient_call

logger = logging.getLogger("rpg_narrative_server.embedding.ollama")


class OllamaEmbeddingProvider(EmbeddingGateway):
    supports_batch = False

    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434",
        timeout: float = 15.0,
        dimension: int | None = None,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # 🔥 padrão correto
        self._dimension: int | None = dimension

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        )

    # ---------------------------------------------------------
    # property
    # ---------------------------------------------------------

    @property
    def dimension(self):
        return self._dimension

    # ---------------------------------------------------------
    # single
    # ---------------------------------------------------------

    async def embed(self, text: str) -> list[float]:
        if not text or not text.strip():
            return self._zero_vector()

        async def call():
            resp = await self.client.post(
                "/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text,
                },
            )

            resp.raise_for_status()

            data = resp.json()

            if "embedding" not in data:
                raise RuntimeError("Invalid Ollama response")

            vec = data["embedding"]

            # 🔥 lazy dimension
            if self._dimension is None:
                self._dimension = len(vec)

            return vec

        try:
            return await resilient_call([call], timeout=self.timeout)

        except Exception:
            logger.exception("Ollama embedding failed (len=%s)", len(text))
            raise

    # ---------------------------------------------------------
    # batch (paralelo controlado)
    # ---------------------------------------------------------

    async def embed_batch(self, texts: list[str]):
        if not texts:
            return []

        texts = [t for t in texts if t and t.strip()]
        if not texts:
            return []

        semaphore = asyncio.Semaphore(4)

        async def safe_embed(t):
            async with semaphore:
                return await self.embed(t)

        return await asyncio.gather(*[safe_embed(t) for t in texts])

    # ---------------------------------------------------------
    # lifecycle
    # ---------------------------------------------------------

    async def close(self):
        await self.client.aclose()

    # ---------------------------------------------------------
    # helpers
    # ---------------------------------------------------------

    def _zero_vector(self):
        if self._dimension:
            return [0.0] * self._dimension

        return [0.0] * 384


def create_ollama_embedding(**kwargs):
    return OllamaEmbeddingProvider(
        model=kwargs.get("model"),
        base_url=kwargs.get("base_url"),
    )
