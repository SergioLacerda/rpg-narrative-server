import argparse
import asyncio

from rpg_narrative_server.bootstrap.container import Container
from rpg_narrative_server.usecases.run_benchmark import (
    RunBenchmarkInput,
)


class BenchmarkCLI:
    def __init__(self):
        container = Container()
        self.usecase = container.run_benchmark

    def run(self):
        parser = argparse.ArgumentParser(description="RPG Benchmark CLI")

        parser.add_argument("--n", type=int, default=50)
        parser.add_argument("--mode", choices=["io", "cpu", "jitter"], default="io")

        parser.add_argument("--no-dedup", action="store_true")
        parser.add_argument("--batch", action="store_true")

        parser.add_argument("--workers", type=int, default=None)
        parser.add_argument("--cpu-work", type=int, default=2_000_000)

        args = parser.parse_args()

        asyncio.run(self._execute(args))

    async def _execute(self, args):
        input_data = RunBenchmarkInput(
            mode=args.mode,
            n=args.n,
            batch=args.batch,
            cpu_work=args.cpu_work,
            workers=args.workers,
            dedup=not args.no_dedup,
        )

        result = await self.usecase.execute(input_data)

        self._print_report(result)

    def _print_report(self, report: dict):
        print("\n--- BENCHMARK REPORT ---")

        for k, v in report.items():
            if isinstance(v, float):
                print(f"{k}: {v:.4f}")
            else:
                print(f"{k}: {v}")
