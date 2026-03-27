import pytest
import asyncio
from rpg_narrative_server.infrastructure.resilience.resilience import resilient_call


@pytest.mark.asyncio
async def test_resilient_success():

    async def provider(x):
        return x + 1

    result = await resilient_call(provider, 1)

    assert result == 2


@pytest.mark.asyncio
async def test_resilient_retry():

    calls = {"n": 0}

    async def flaky(x):
        calls["n"] += 1
        if calls["n"] < 2:
            raise ValueError("fail")
        return x + 1

    result = await resilient_call(flaky, 1, retries=3)

    assert result == 2
    assert calls["n"] == 2


@pytest.mark.asyncio
async def test_resilient_fail_all():

    async def bad(x):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        await resilient_call(bad, 1, retries=2)


@pytest.mark.asyncio
async def test_resilient_timeout():

    async def slow(x):
        await asyncio.sleep(0.2)
        return x

    with pytest.raises(asyncio.TimeoutError):
        await resilient_call(slow, 1, timeout=0.05)


@pytest.mark.asyncio
async def test_resilient_sync_function():

    def sync_fn(x):
        return x + 5

    result = await resilient_call(sync_fn, 5)

    assert result == 10


@pytest.mark.asyncio
async def test_resilient_retry_exhausted():

    calls = {"n": 0}

    async def always_fail(x):
        calls["n"] += 1
        raise ValueError("fail")

    with pytest.raises(ValueError):
        await resilient_call(always_fail, 1, retries=3)

    assert calls["n"] == 3
