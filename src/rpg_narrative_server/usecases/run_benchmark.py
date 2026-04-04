import asyncio
from dataclasses import dataclass, field

from rpg_narrative_server.application.dto.benchmark_strategy import BenchmarkStrategy
from rpg_narrative_server.application.ports.benchmark_port import BenchmarkPort
from rpg_narrative_server.application.services.benchmark_analysis import (
    extract_winner,
    rank_strategies,
)


@dataclass
class RunBenchmarkInput:
    mode: str = "io"
    n: int = 50
    batch: bool = False
    cpu_work: int = 2_000_000
    workers: int | None = None
    dedup: bool = True
    strategy: str = "concurrent"


@dataclass
class CompareBenchmarkInput:
    modes: list[str] = field(default_factory=lambda: ["io", "jitter", "cpu"])
    n: int = 50
    batch: bool = False
    strategy: str = "concurrent"


class RunBenchmarkUseCase:
    def __init__(self, service: BenchmarkPort):
        self.service = service

    async def execute(self, input_data: RunBenchmarkInput):
        return await self.service.run(
            mode=input_data.mode,
            n=input_data.n,
            batch=input_data.batch,
            cpu_work=input_data.cpu_work,
            workers=input_data.workers,
            dedup=input_data.dedup,
            strategy=input_data.strategy,
        )

    async def compare(self, input_data: CompareBenchmarkInput):
        async def run_mode(mode: str):
            try:
                result = await self.service.run(
                    mode=mode,
                    n=input_data.n,
                    batch=input_data.batch,
                    strategy=input_data.strategy,
                )
                return mode, result

            except Exception as e:
                return mode, {
                    "error": str(e),
                    "status": "failed",
                }

        tasks = [run_mode(mode) for mode in input_data.modes]

        results = await asyncio.gather(*tasks)

        return {mode: result for mode, result in results}

    async def compare_strategies(self, strategies: list[BenchmarkStrategy], n: int = 50):
        async def run(strategy: BenchmarkStrategy):
            try:
                result = await self.service.run(
                    mode=strategy.mode,
                    n=n,
                    batch=strategy.batch,
                    workers=strategy.workers,
                    dedup=strategy.dedup,
                    strategy=strategy.strategy,
                )
                return strategy.name, result

            except Exception as e:
                return strategy.name, {
                    "error": str(e),
                    "status": "failed",
                }

        tasks = [run(s) for s in strategies]

        results_list = await asyncio.gather(*tasks)

        results = {name: result for name, result in results_list}

        ranking = rank_strategies(results)
        winner = extract_winner(ranking)

        return {
            "results": results,
            "ranking": ranking,
            "winner": winner,
        }

    @staticmethod
    def generate_strategies():
        return [
            BenchmarkStrategy(name="baseline", batch=False, dedup=True),
            BenchmarkStrategy(name="no_dedup", batch=False, dedup=False),
            BenchmarkStrategy(name="batch_on", batch=True, dedup=True),
            BenchmarkStrategy(name="cpu_mode", mode="cpu"),
            BenchmarkStrategy(name="high_workers", workers=8),
        ]
