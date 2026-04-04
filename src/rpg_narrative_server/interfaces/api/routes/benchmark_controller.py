from fastapi import APIRouter, Query, Request

from rpg_narrative_server.application.dto.benchmark_request import (
    BenchmarkRequest,
)
from rpg_narrative_server.usecases.run_benchmark import (
    CompareBenchmarkInput,
    RunBenchmarkInput,
)

router = APIRouter()


def get_usecase(request: Request):
    return request.app.state.container.run_benchmark


# ==========================================================
# RUN
# ==========================================================
@router.post("/benchmark/run")
async def run_benchmark(request: Request, req: BenchmarkRequest):
    usecase = get_usecase(request)

    input_data = RunBenchmarkInput(**req.dict())

    return await usecase.execute(input_data)


# ==========================================================
# COMPARE
# ==========================================================
@router.get("/benchmark/compare")
async def compare(
    request: Request,
    n: int = Query(50),
    batch: bool = Query(False),
    strategy: str = Query("concurrent"),
):
    usecase = get_usecase(request)

    input_data = CompareBenchmarkInput(
        n=n,
        batch=batch,
        strategy=strategy,
    )

    return await usecase.compare(input_data)


# ==========================================================
# STRATEGIES
# ==========================================================
@router.get("/benchmark/strategies")
async def compare_strategies(request: Request):
    usecase = request.app.state.container.run_benchmark

    strategies = usecase.generate_strategies()

    return await usecase.compare_strategies(strategies)
