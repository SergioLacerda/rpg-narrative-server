import asyncio
import time

from scripts.benchmark.metrics import build_report


async def run_concurrent(engine, n=50, same_query=True):
    latencies = []

    async def call(i):
        query = "same" if same_query else f"q{i}"

        start = time.perf_counter()
        await engine.search(query)
        latencies.append(time.perf_counter() - start)

    start_total = time.perf_counter()

    await asyncio.gather(*[call(i) for i in range(n)])

    total = time.perf_counter() - start_total

    return build_report(latencies, total, engine._benchmark_index.calls)
