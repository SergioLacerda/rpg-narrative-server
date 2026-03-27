import argparse
import asyncio
import random
import statistics
import os
import time

from rpg_narrative_server.infrastructure.rag.retrieval_engine import RetrievalEngine
from rpg_narrative_server.infrastructure.runtime.executor import Executor, ExecutorType


# ==================================================
# CPU WORK
# ==================================================


def cpu_heavy_compute(work: int):
    total = 0
    for i in range(work):
        total += i * i
    return total


# ==================================================
# INDEXES
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

    def search(self, query, q_vec, k):
        self.calls += 1
        cpu_heavy_compute(self.work)
        return [query]


# ==================================================
# EMBEDDINGS
# ==================================================


class FakeEmbedding:
    async def get(self, query):
        return [1.0]


class BatchEmbedding:
    def __init__(self):
        self.calls = 0

    async def embed_batch(self, texts):
        self.calls += 1
        await asyncio.sleep(0.01)
        return [[1.0] for _ in texts]

    async def get(self, text):
        return [1.0]


# ==================================================
# CACHE
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


def create_engine(mode="io", batch=False, cpu_work=2_000_000):

    if mode == "cpu":
        index = CpuBoundIndex(work=cpu_work)

        workers = max(2, os.cpu_count() // 2)

        executor = Executor(mode=ExecutorType.PROCESS, max_workers=workers)

    elif mode == "jitter":
        index = JitterIndex()
        executor = Executor(mode=ExecutorType.THREAD)

    else:
        index = SlowIndex()
        executor = Executor(mode=ExecutorType.THREAD)

    embedding = BatchEmbedding() if batch else FakeEmbedding()

    engine = RetrievalEngine(
        vector_index=index,
        embedding_cache=embedding,
        semantic_cache=FakeSemanticCache(),
        executor=executor,
        enable_hedging=True,
    )

    engine._benchmark_index = index

    return engine


# ==================================================
# METRICS
# ==================================================


def percentile(data, p):
    data = sorted(data)
    k = (len(data) - 1) * (p / 100)
    f = int(k)
    c = min(f + 1, len(data) - 1)

    if f == c:
        return data[int(k)]

    return data[f] + (data[c] - data[f]) * (k - f)


# ==================================================
# BENCHMARKS
# ==================================================


async def perf_cold(engine):

    start = time.perf_counter()

    for i in range(10):
        await engine.search(f"q{i}")

    elapsed = time.perf_counter() - start

    print(f"\nCOLD: {elapsed:.4f}s")


async def perf_warm(engine):

    await engine.search("same")

    start = time.perf_counter()

    for _ in range(10):
        await engine.search("same")

    elapsed = time.perf_counter() - start

    print(f"WARM: {elapsed:.6f}s")


async def perf_concurrent(engine, n=50, same_query=True):

    latencies = []

    workers = engine.executor._executor._max_workers
    limit = workers * 2
    semaphore = asyncio.Semaphore(limit)

    async def call(i):
        query = "same" if same_query else f"q{i}"

        async with semaphore:
            start = time.perf_counter()
            await engine.search(query)
            latencies.append(time.perf_counter() - start)

    start_total = time.perf_counter()

    await asyncio.gather(*[call(i) for i in range(n)])

    total = time.perf_counter() - start_total

    avg = statistics.mean(latencies)
    p95 = percentile(latencies, 95)
    p99 = percentile(latencies, 99)

    throughput = n / total if total > 0 else 0

    print("\n--- CONCURRENT REPORT ---")
    print(f"Requests: {n}")
    print(f"Mode: {'DEDUP' if same_query else 'NO DEDUP'}")
    print(f"Total: {total:.4f}s")
    print(f"Avg: {avg:.4f}s")
    print(f"P95: {p95:.4f}s")
    print(f"P99: {p99:.4f}s")
    print(f"Throughput: {throughput:.2f} req/s")
    print(f"Index calls: {engine._benchmark_index.calls}")


async def perf_scaling(engine):

    async def run(n):
        start = time.perf_counter()

        await asyncio.gather(*[engine.search(f"q{i}") for i in range(n)])

        return time.perf_counter() - start

    small_n = 5
    large_n = 20

    small = await run(small_n)
    large = await run(large_n)

    small_avg = small / small_n
    large_avg = large / large_n

    speedup = (small_avg / large_avg) if large_avg > 0 else 0

    print("\n--- SCALING REPORT ---")
    print(f"SMALL ({small_n}): {small:.4f}s | avg {small_avg:.4f}s")
    print(f"LARGE ({large_n}): {large:.4f}s | avg {large_avg:.4f}s")
    print(f"SPEEDUP: {speedup:.2f}x")


async def perf_memory(engine, n=1000):

    for i in range(n):
        await engine.search(f"q{i}")

    size = len(engine.semantic_cache.store)

    print("\n--- MEMORY REPORT ---")
    print(f"Queries: {n}")
    print(f"Cache size: {size}")


async def perf_batch(engine, n=50):

    if not hasattr(engine.embedding_cache, "embed_batch"):
        print("\nBatch not supported in this mode")
        return

    queries = [f"q{i}" for i in range(n)]

    start = time.perf_counter()

    await engine.embedding_cache.embed_batch(queries)

    await asyncio.gather(*[engine.search(q) for q in queries])

    elapsed = time.perf_counter() - start

    print("\n--- BATCH REPORT ---")
    print(f"Queries: {n}")
    print(f"Time: {elapsed:.4f}s")
    print(f"Embedding calls: {engine.embedding_cache.calls}")


# ==================================================
# MAIN
# ==================================================


async def main(args):

    print("\n🚀 Retrieval Engine Benchmark\n")

    engine = create_engine(args.mode, args.batch, args.cpu_work)
    await perf_cold(engine)

    engine = create_engine(args.mode, args.batch, args.cpu_work)
    await perf_warm(engine)

    engine = create_engine(args.mode, args.batch, args.cpu_work)
    await perf_concurrent(engine, n=args.n, same_query=not args.no_dedup)

    engine = create_engine(args.mode, args.batch, args.cpu_work)
    await perf_scaling(engine)

    if args.memory:
        engine = create_engine(args.mode, args.batch, args.cpu_work)
        await perf_memory(engine, n=args.n)

    if args.batch:
        engine = create_engine(args.mode, batch=True, cpu_work=args.cpu_work)
        await perf_batch(engine, n=args.n)


# ==================================================
# CLI
# ==================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--n", type=int, default=50)
    parser.add_argument("--no-dedup", action="store_true")
    parser.add_argument("--mode", choices=["io", "cpu", "jitter"], default="io")
    parser.add_argument("--memory", action="store_true")
    parser.add_argument("--batch", action="store_true")
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--cpu-work", type=int, default=2_000_000)

    args = parser.parse_args()

    asyncio.run(main(args))
