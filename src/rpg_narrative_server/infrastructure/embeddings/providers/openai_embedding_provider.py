import logging
from typing import List

from rpg_narrative_server.application.ports.embedding_gateway import EmbeddingGateway
from rpg_narrative_server.shared.resilience import resilient_call

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None


logger = logging.getLogger("rpg_narrative_server.embedding.openai")


class OpenAIEmbeddingProvider(EmbeddingGateway):

    supports_batch = True

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        timeout: float = 10.0,
        base_url: str | None = None,
    ):
        if not AsyncOpenAI:
            raise RuntimeError("openai package not installed")

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        self.model = model
        self.timeout = timeout

        # 🔥 dimensão dinâmica
        self._dimension: int | None = None

    # ---------------------------------------------------------
    # property
    # ---------------------------------------------------------

    @property
    def dimension(self):
        return self._dimension

    # ---------------------------------------------------------
    # helpers
    # ---------------------------------------------------------

    def _zero_vector(self):
        if self._dimension:
            return [0.0] * self._dimension
        return [0.0] * 1536  # fallback seguro

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

            # 🔥 lazy dimension discovery
            if self._dimension is None:
                self._dimension = len(vec)

            return vec

        try:
            return await resilient_call([call], timeout=self.timeout)

        except Exception:
            logger.exception("OpenAI embedding failed (len=%s)", len(text))
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

            # 🔥 lazy dimension discovery
            if self._dimension is None and vectors:
                self._dimension = len(vectors[0])

            return vectors

        try:
            return await resilient_call([call], timeout=self.timeout)

        except Exception:
            logger.exception("OpenAI batch embedding failed (n=%s)", len(texts))
            raise


def create_openai_embedding(**kwargs):
    return OpenAIEmbeddingProvider(
        api_key=kwargs.get("api_key"),
        model=kwargs.get("model"),
        base_url=kwargs.get("base_url"),
    )
