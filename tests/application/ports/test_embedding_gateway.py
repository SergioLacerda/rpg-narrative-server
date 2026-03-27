import pytest

from rpg_narrative_server.application.ports.embedding_gateway import EmbeddingGateway


# ---------------------------------------------------------
# FAKES
# ---------------------------------------------------------


class DummyEmbeddingGateway(EmbeddingGateway):
    async def embed(self, text: str):
        return [1.0]


class SpyEmbeddingGateway(EmbeddingGateway):
    def __init__(self):
        self.calls = []

    async def embed(self, text: str):
        self.calls.append(text)
        return [float(len(text))]


class CustomBatchGateway(EmbeddingGateway):
    async def embed(self, text: str):
        raise AssertionError("embed should not be called")

    async def embed_batch(self, texts):
        return [[42.0] for _ in texts]


# ---------------------------------------------------------
# PROPERTIES
# ---------------------------------------------------------


def test_default_properties():
    gateway = DummyEmbeddingGateway()

    assert gateway.dimension is None
    assert gateway.supports_batch is False


# ---------------------------------------------------------
# ABC CONTRACT
# ---------------------------------------------------------


def test_cannot_instantiate_abstract_class():
    with pytest.raises(TypeError):
        EmbeddingGateway()


# ---------------------------------------------------------
# FALLBACK BATCH
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_embed_batch_fallback_calls_embed():
    gateway = SpyEmbeddingGateway()

    texts = ["a", "bb", "ccc"]
    result = await gateway.embed_batch(texts)

    assert gateway.calls == texts
    assert result == [[1.0], [2.0], [3.0]]


@pytest.mark.asyncio
async def test_embed_batch_empty_input():
    gateway = SpyEmbeddingGateway()

    result = await gateway.embed_batch([])

    assert result == []
    assert gateway.calls == []


@pytest.mark.asyncio
async def test_embed_batch_accepts_iterable():
    gateway = SpyEmbeddingGateway()

    texts = (str(i) for i in range(3))  # generator

    result = await gateway.embed_batch(texts)

    assert result == [[1.0], [1.0], [1.0]]


# ---------------------------------------------------------
# CUSTOM BATCH
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_custom_batch_override():
    gateway = CustomBatchGateway()

    result = await gateway.embed_batch(["a", "b"])

    assert result == [[42.0], [42.0]]
