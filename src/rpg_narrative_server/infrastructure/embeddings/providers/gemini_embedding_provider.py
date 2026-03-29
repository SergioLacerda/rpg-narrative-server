import asyncio
import logging

from rpg_narrative_server.application.ports.embedding_gateway import EmbeddingGateway
from rpg_narrative_server.shared.resilience import resilient_call

try:
    import google.generativeai as genai
except ImportError:
    genai = None


logger = logging.getLogger("rpg_narrative_server.embedding.gemini")


class GeminiEmbeddingProvider(EmbeddingGateway):
    supports_batch = False

    def __init__(
        self,
        api_key: str,
        model: str = "models/embedding-001",
        timeout: float = 10.0,
        dimension: int | None = None,
    ):
        if not genai:
            raise RuntimeError("google-generativeai not installed")

        genai.configure(api_key=api_key)

        self.model = model
        self.timeout = timeout

        # 🔥 padrão correto
        self._dimension: int | None = dimension

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
        return [0.0] * 768  # fallback conhecido

    # ---------------------------------------------------------
    # single
    # ---------------------------------------------------------

    async def embed(self, text: str) -> list[float]:
        if not text or not text.strip():
            return self._zero_vector()

        def _call():
            return genai.embed_content(
                model=self.model,
                content=text,
            )

        async def call():
            resp = await asyncio.wait_for(asyncio.to_thread(_call), timeout=self.timeout)

            vec = resp["embedding"]

            # 🔥 lazy dimension
            if self._dimension is None:
                self._dimension = len(vec)

            return vec

        try:
            return await resilient_call([call])

        except Exception:
            logger.exception("Gemini embedding failed (len=%s)", len(text))
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

        semaphore = asyncio.Semaphore(5)

        async def safe_embed(t):
            async with semaphore:
                return await self.embed(t)

        return await asyncio.gather(*[safe_embed(t) for t in texts])


def create_gemini_embedding(**kwargs):
    return GeminiEmbeddingProvider(
        api_key=kwargs.get("api_key"),
        model=kwargs.get("model"),
    )
