import asyncio
import inspect
import random
import logging

logger = logging.getLogger("rpg_narrative_server.resilience")


async def resilient_call(
    fn,
    *args,
    retries: int = 3,
    backoff: float = 1.5,
    base_delay: float = 0.1,
    timeout: float | None = None,
    **kwargs
):

    delay = base_delay

    for attempt in range(1, retries + 1):

        try:
            result = fn(*args, **kwargs)

            if inspect.isawaitable(result):
                if timeout:
                    result = await asyncio.wait_for(result, timeout=timeout)
                else:
                    result = await result

            return result

        except Exception as e:

            logger.warning(
                "Attempt %s/%s failed: %s",
                attempt,
                retries,
                e,
            )

            if attempt >= retries:
                raise

            jitter = random.uniform(0, delay * 0.1)
            await asyncio.sleep(delay + jitter)

            delay *= backoff