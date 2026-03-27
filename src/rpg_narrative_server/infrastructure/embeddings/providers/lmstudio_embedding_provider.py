import httpx
import logging
from typing import List

from rpg_narrative_server.infrastructure.resilience.resilience import resilient_call

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None


logger = logging.getLogger("rpg_narrative_server.embedding.lmstudio")


class LMStudioEmbeddingProvider:

    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:1234/v1",
        timeout: float = 30.0,
    ):

        self.model = model
        self.timeout = timeout

        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key="lmstudio",
            timeout=httpx.Timeout(timeout)
        )

        self._dimension = None

    # ---------------------------------------------------------
    # property
    # ---------------------------------------------------------

    @property
    def dimension(self):
        return self._dimension

    # ---------------------------------------------------------
    # single
    # ---------------------------------------------------------

    async def embed(self, text: str) -> List[float]:

        if not text or not text.strip():
            return self._zero_vector()

        async def call():
            resp = await self.client.embeddings.create(
                model=self.model,
                input=text,
            )

            vec = resp.data[0].embedding

            # 🔥 lazy dimension
            if self._dimension is None:
                self._dimension = len(vec)

            return vec

        try:
            return await resilient_call(
                [call],
                timeout=self.timeout
            )

        except Exception:
            logger.exception(
                "LMStudio embedding failed (len=%s)",
                len(text)
            )
            raise

    # ---------------------------------------------------------
    # batch
    # ---------------------------------------------------------

    async def embed_batch(self, texts: List[str]):

        if not texts:
            return []

        texts = [t for t in texts if t and t.strip()]
        if not texts:
            return []

        async def call():
            resp = await self.client.embeddings.create(
                model=self.model,
                input=texts,
            )

            vectors = [x.embedding for x in resp.data]

            # 🔥 lazy dimension
            if self._dimension is None and vectors:
                self._dimension = len(vectors[0])

            return vectors

        try:
            return await resilient_call(
                [call],
                timeout=self.timeout
            )

        except Exception:
            logger.exception(
                "LMStudio batch embedding failed (n=%s)",
                len(texts)
            )
            raise

    # ---------------------------------------------------------
    # helpers
    # ---------------------------------------------------------

    def _zero_vector(self):

        if self._dimension:
            return [0.0] * self._dimension

        return [0.0] * 384

def create_lmstudio_embedding(**kwargs):
    return LMStudioEmbeddingProvider(
        model=kwargs.get("model"),
        base_url=kwargs.get("base_url"),
    )