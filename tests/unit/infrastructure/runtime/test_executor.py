from rpg_narrative_server.infrastructure.runtime.executor import Executor


def test_executor_run():
    executor = Executor(max_workers=1)

    future = executor.run(lambda x: x + 1, 1)

    assert future.result() == 2

    executor.shutdown()


def test_executor_multiple_tasks():
    executor = Executor(max_workers=2)

    futures = [executor.run(lambda x: x * 2, i) for i in range(3)]

    results = [f.result() for f in futures]

    assert results == [0, 2, 4]

    executor.shutdown()


def test_executor_shutdown_twice():
    executor = Executor()

    executor.shutdown()
    executor.shutdown()  # não deve quebrar
