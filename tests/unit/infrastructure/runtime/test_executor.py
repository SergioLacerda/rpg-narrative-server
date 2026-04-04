import pytest

from rpg_narrative_server.infrastructure.runtime.executor import (
    Executor,
    ExecutorType,
)


def add_one(x):
    return x + 1


def add_two(x):
    return x + 2


def mul_two(x):
    return x * 2


def mul_three(x):
    return x * 3


def test_executor_run():
    executor = Executor(max_workers=1)

    future = executor.run(lambda x: x + 1, 1)

    assert future.result() == 2

    executor.shutdown()


def test_executor_multiple_tasks():
    executor = Executor(max_workers=2)

    futures = [executor.run(mul_two, i) for i in range(3)]

    results = [f.result() for f in futures]

    assert results == [0, 2, 4]

    executor.shutdown()


def test_executor_shutdown_twice():
    executor = Executor()

    executor.shutdown()
    executor.shutdown()


def test_executor_run_thread():
    executor = Executor(mode=ExecutorType.THREAD)

    future = executor.run(lambda x: x + 1, 1)

    assert future.result() == 2

    executor.shutdown()


def test_executor_run_process():
    executor = Executor(mode=ExecutorType.PROCESS)

    future = executor.run(add_two, 2)

    assert future.result() == 4

    executor.shutdown()


@pytest.mark.asyncio
async def test_executor_run_async_thread():
    executor = Executor(mode=ExecutorType.THREAD)

    result = await executor.run_async(lambda x: x * 2, 3)

    assert result == 6

    executor.shutdown()


@pytest.mark.asyncio
async def test_executor_run_async_process():
    executor = Executor(mode=ExecutorType.PROCESS)

    result = await executor.run_async(mul_three, 3)

    assert result == 9

    executor.shutdown()


def test_executor_shutdown():
    executor = Executor()

    executor.shutdown()
