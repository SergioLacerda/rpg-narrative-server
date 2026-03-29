import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from enum import StrEnum

logger = logging.getLogger("rpg_narrative_server")


class ExecutorType(StrEnum):
    THREAD = "thread"
    PROCESS = "process"


class Executor:
    def __init__(self, max_workers=4, mode=ExecutorType.THREAD):
        if mode == ExecutorType.PROCESS:
            self._executor = ProcessPoolExecutor(max_workers=max_workers)
        else:
            self._executor = ThreadPoolExecutor(max_workers=max_workers)

    # 🔥 compatibilidade com testes (sync)
    def run(self, fn, *args, **kwargs):
        logger.debug("EXECUTOR: start")
        return self._executor.submit(fn, *args, **kwargs)

    # 🔥 async (novo padrão)
    async def run_async(self, fn, *args):
        logger.debug("EXECUTOR: start")
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, fn, *args)

    def shutdown(self):
        self._executor.shutdown(wait=True)
