import asyncio
import logging

from rpg_narrative_server.application.ports.embedding_gateway import EmbeddingGateway
from rpg_narrative_server.shared.resilience import resilient_call

logger = logging.getLogger("rpg_narrative_server.embedding.sentence")


# ---------------------------------------------------------
# lazy backend loader
# ---------------------------------------------------------


def _load_backend():
    try:
        import torch
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer, torch
    except ImportError as err:
        raise ImportError("msg") from err


# ---------------------------------------------------------
# helpers
# ---------------------------------------------------------


def _detect_device(device: str | None, torch):
    if device:
        device = device.lower()
        valid = {"cpu", "cuda", "mps"}

        if device not in valid:
            raise ValueError(f"Invalid device '{device}'. Expected {valid}")

        return device

    if torch and torch.cuda.is_available():
        return "cuda"

    if torch and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"

    return "cpu"


def _auto_batch_size(device: str):
    if device == "cuda":
        return 128
    if device == "mps":
        return 64
    return 16


# ---------------------------------------------------------
# provider
# ---------------------------------------------------------


class SentenceEmbeddingProvider(EmbeddingGateway):
    supports_batch = True

    def __init__(
        self,
        model: str,
        device: str | None = None,
        batch_size: int | None = None,
        timeout: float = 20.0,
    ):
        SentenceTransformer, torch = _load_backend()

        self._torch = torch
        self.model_name = model

        self.device = _detect_device(device, torch)
        self.batch_size = batch_size or _auto_batch_size(self.device)
        self.timeout = timeout

        logger.info(
            "Embedding config → model=%s device=%s batch_size=%s timeout=%s",
            self.model_name,
            self.device,
            self.batch_size,
            self.timeout,
        )

        self.model = SentenceTransformer(model, device=self.device)

        self.is_e5 = "e5" in model.lower()
        self._dimension = self.model.get_sentence_embedding_dimension()

        # limita concorrência (CPU/GPU proteção)
        self._semaphore = asyncio.Semaphore(2)

    # ---------------------------------------------------------
    # helpers
    # ---------------------------------------------------------

    def _prepare_doc(self, text: str):
        if self.is_e5:
            return "passage: " + text

        return text

    # ---------------------------------------------------------
    # encode (sync)
    # ---------------------------------------------------------

    def _encode_single(self, text: str):
        if self._torch:
            with self._torch.no_grad():
                return self.model.encode(text, normalize_embeddings=True)

        return self.model.encode(text)

    def _encode_batch(self, texts: list[str]):
        if self._torch:
            with self._torch.no_grad():
                return self.model.encode(
                    texts,
                    batch_size=self.batch_size,
                    show_progress_bar=False,
                    normalize_embeddings=True,
                )

        return self.model.encode(texts)

    # ---------------------------------------------------------
    # async wrappers (🔥 correto)
    # ---------------------------------------------------------

    async def _run_in_thread(self, fn, *args):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, fn, *args)

    # ---------------------------------------------------------
    # public API
    # ---------------------------------------------------------

    async def embed(self, text: str) -> list[float]:
        if not text or not text.strip():
            return [0.0] * self._dimension

        text = self._prepare_doc(text)

        async def call():
            async with self._semaphore:
                vec = await self._run_in_thread(self._encode_single, text)
                return vec.tolist()

        try:
            return await resilient_call(call)

        except Exception:
            logger.exception("Sentence embedding failed")
            raise

    async def embed_batch(self, texts: list[str]):
        texts = [t for t in texts if t and t.strip()]
        if not texts:
            return []

        if self.is_e5:
            texts = ["passage: " + t for t in texts]

        async def call():
            async with self._semaphore:
                vectors = await self._run_in_thread(self._encode_batch, texts)
                return [v.tolist() for v in vectors]

        try:
            return await resilient_call(call)

        except Exception:
            logger.exception("Sentence batch embedding failed")
            raise

    # ---------------------------------------------------------
    # metadata
    # ---------------------------------------------------------

    @property
    def dimension(self):
        return self._dimension


# ---------------------------------------------------------
# factory
# ---------------------------------------------------------


def create_sentence_embedding(**kwargs):
    return SentenceEmbeddingProvider(
        model=kwargs.get("model"),
        device=kwargs.get("device"),
        batch_size=kwargs.get("batch_size"),
    )
