import asyncio
from types import SimpleNamespace

import pytest

from rpg_narrative_server.infrastructure.rag.async_vector_memory_adapter import (
    AsyncVectorMemoryAdapter,
)


class MockVectorStore:
    def __init__(self):
        self.calls = []

    def add(self, doc_id, emb):
        self.calls.append((doc_id, emb))


class MockStore:
    def __init__(self):
        self.data = {}

    def set(self, k, v):
        self.data[k] = v


def build_adapter(embedding):
    vector_index = SimpleNamespace(
        vector_store=MockVectorStore(),
        embedding_service=embedding,
        components=SimpleNamespace(
            document_store=MockStore(),
            metadata_store=MockStore(),
        ),
    )

    return AsyncVectorMemoryAdapter(vector_index)


def build_adapter_full(batch_size=2, flush_interval=0.01):
    vs = MockVectorStore()
    ds = MockStore()
    ms = MockStore()

    vector_index = SimpleNamespace(
        vector_store=vs,
        embedding_service=SimpleNamespace(
            embed=lambda t: [1],
            embed_batch=lambda t: [[1]] * len(t),
        ),
        components=SimpleNamespace(
            document_store=ds,
            metadata_store=ms,
        ),
    )

    return (
        AsyncVectorMemoryAdapter(
            vector_index,
            batch_size=batch_size,
            flush_interval=flush_interval,
        ),
        vs,
        ds,
        ms,
    )


@pytest.mark.asyncio
async def test_embed_batch_with_batch_method():
    class Emb:
        def embed_batch(self, texts):
            return [[1]] * len(texts)

    adapter = build_adapter(Emb())

    result = await adapter._embed_batch(["a", "b"])

    assert result == [[1], [1]]


@pytest.mark.asyncio
async def test_embed_batch_async():
    class Emb:
        async def embed_batch(self, texts):
            return [[2]] * len(texts)

    adapter = build_adapter(Emb())

    result = await adapter._embed_batch(["a"])

    assert result == [[2]]


@pytest.mark.asyncio
async def test_embed_batch_fallback():
    class Emb:
        def embed(self, text):
            return [3]

    adapter = build_adapter(Emb())

    result = await adapter._embed_batch(["a", "b"])

    assert result == [[3], [3]]


@pytest.mark.asyncio
async def test_embed_batch_fallback_async():
    class Emb:
        async def embed(self, text):
            return [4]

    adapter = build_adapter(Emb())

    result = await adapter._embed_batch(["a"])

    assert result == [[4]]


@pytest.mark.asyncio
async def test_flush_writes_all_stores():
    adapter, vs, ds, ms = build_adapter_full()

    batch = [
        ("c1", "hello", {"a": 1}),
        ("c1", "world", {"b": 2}),
    ]

    await adapter._flush(batch)

    assert len(vs.calls) == 2
    assert len(ds.data) == 2
    assert len(ms.data) == 2


@pytest.mark.asyncio
async def test_flush_empty():
    adapter, *_ = build_adapter_full()

    await adapter._flush([])


def test_generate_id():
    adapter, *_ = build_adapter_full()

    doc_id = adapter._generate_id("c1")

    assert doc_id.startswith("c1:")


@pytest.mark.asyncio
async def test_store_event_enqueue():
    adapter, *_ = build_adapter_full()

    await adapter.store_event("c1", ["a", "b"], {"x": 1})

    assert adapter._queue.qsize() == 2


@pytest.mark.asyncio
async def test_worker_flush_by_batch():
    adapter, vs, *_ = build_adapter_full(batch_size=2, flush_interval=10)

    await adapter.start()

    await adapter.store_event("c1", ["a", "b"], {})

    await asyncio.sleep(0.05)

    await adapter.stop()

    assert len(vs.calls) >= 2


@pytest.mark.asyncio
async def test_worker_flush_by_timeout():
    adapter, vs, *_ = build_adapter_full(batch_size=10, flush_interval=0.01)

    await adapter.start()

    await adapter.store_event("c1", ["a"], {})

    await asyncio.sleep(0.05)

    await adapter.stop()

    assert len(vs.calls) >= 1


@pytest.mark.asyncio
async def test_start_idempotent():
    adapter, *_ = build_adapter_full()

    await adapter.start()
    await adapter.start()

    await adapter.stop()


@pytest.mark.asyncio
async def test_stop_without_start():
    adapter, *_ = build_adapter_full()

    await adapter.stop()
