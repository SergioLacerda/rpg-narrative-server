import asyncio
import os
import random
from collections.abc import Iterable
from typing import Any, Protocol

from rpg_narrative_server.infrastructure.adapters.benchmark.retrieval_adapter import (
    RetrievalAdapter,
)
from rpg_narrative_server.infrastructure.rag.retrieval_engine import RetrievalEngine
from rpg_narrative_server.infrastructure.runtime.executor import Executor, ExecutorType

# ==================================================
# PROTOCOL (contrato mínimo)
# ==================================================


class RetrievalLike(Protocol):
    async def search(self, query: str): ...


class IndexProtocol(Protocol):
    calls: int

    async def search(self, query: Any, q_vec: Any, k: int): ...


# ==================================================
# CPU WORK
# ==================================================


def cpu_heavy_compute(work: int):
    total = 0
    for i in range(work):
        total += i * i
    return total


# ==================================================
# INDEXES (simulações)
# ==================================================


class SlowIndex:
    def __init__(self, delay=0.05):
        self.delay = delay
        self.calls = 0

    async def search(self, query, q_vec, k):
        self.calls += 1
        await asyncio.sleep(self.delay)
        return [query]


class JitterIndex:
    def __init__(self, min_delay=0.03, max_delay=0.1):
        self.min = min_delay
        self.max = max_delay
        self.calls = 0

    async def search(self, query, q_vec, k):
        self.calls += 1
        await asyncio.sleep(random.uniform(self.min, self.max))
        return [query]


class CpuBoundIndex:
    def __init__(self, work=2_000_000):
        self.work = work
        self.calls = 0

    async def search(self, query, q_vec, k):
        self.calls += 1
        cpu_heavy_compute(self.work)
        return [query]


# ==================================================
# EMBEDDINGS (fake)
# ==================================================


class FakeEmbedding:
    async def get(self, query):
        return [1.0]


class BatchEmbedding:
    def __init__(self):
        self.calls = 0

    async def embed_batch(self, texts: Iterable[str]):
        self.calls += 1
        await asyncio.sleep(0.01)
        return [[1.0] for _ in texts]

    async def get(self, text):
        return [1.0]


# ==================================================
# CACHE (fake)
# ==================================================


class FakeSemanticCache:
    def __init__(self):
        self.store = {}

    def get(self, query, vec):
        return self.store.get(query)

    def set(self, query, vec, value):
        self.store[query] = value


# ==================================================
# FACTORY
# ==================================================


def create_engine(
    mode: str = "io",
    batch: bool = False,
    cpu_work: int = 2_000_000,
    workers: int | None = None,
) -> tuple[RetrievalLike, IndexProtocol]:
    if mode == "cpu":
        index = CpuBoundIndex(work=cpu_work)

        cpu_count = os.cpu_count() or 1
        workers = workers or max(2, cpu_count // 2)

        executor = Executor(mode=ExecutorType.PROCESS, max_workers=workers)

    elif mode == "jitter":
        index = JitterIndex()
        executor = Executor(mode=ExecutorType.THREAD, max_workers=workers)

    else:
        index = SlowIndex()
        executor = Executor(mode=ExecutorType.THREAD, max_workers=workers)

    embedding = BatchEmbedding() if batch else FakeEmbedding()

    engine = RetrievalEngine(
        vector_index=index,
        embedding_cache=embedding,
        semantic_cache=FakeSemanticCache(),
        executor=executor,
        enable_hedging=True,
    )

    adapter = RetrievalAdapter(engine)

    return adapter, index
