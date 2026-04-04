from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from rpg_narrative_server.application.services.llm.circuit_breaker import CircuitBreaker
from rpg_narrative_server.application.services.llm.llm_service import LLMService
from tests.config.fakes.llm.fake_request import DummyRequest


class DummyProvider:
    async def generate(self, request):
        return "ok"

    async def stream(self, request):
        yield "chunk"


class DummyCache:
    def __init__(self):
        self.store = {}

    def get(self, k):
        return self.store.get(k)

    def set(self, k, v):
        self.store[k] = v


class DummyAsyncCache:
    def __init__(self):
        self.store = {}

    async def get(self, k):
        return self.store.get(k)

    async def set(self, k, v):
        self.store[k] = v


class DummyCB:
    def __init__(self, allow=True):
        self._allow = allow
        self.failed = False
        self.succeeded = False

    def allow(self):
        return self._allow

    def success(self):
        self.succeeded = True

    def failure(self):
        self.failed = True


class Req:
    def __init__(self, **kwargs):
        self.prompt = kwargs.get("prompt", "hi")
        self.system_prompt = kwargs.get("system_prompt", "")
        self.temperature = kwargs.get("temperature", 0.5)
        self.max_tokens = kwargs.get("max_tokens", 10)
        self.campaign_id = kwargs.get("campaign_id", None)
        self.metadata = kwargs.get("metadata", None)
        self.tools = kwargs.get("tools", None)


@pytest.mark.asyncio
async def test_generate_empty_prompt():
    service = LLMService(provider=MagicMock())

    result = await service.generate(DummyRequest(prompt=""))

    assert result == ""


@pytest.mark.asyncio
async def test_generate_l1_cache_hit():
    ttl_cache = MagicMock()
    ttl_cache.get.return_value = "cached"

    service = LLMService(provider=MagicMock(), ttl_cache=ttl_cache)

    result = await service.generate(DummyRequest())

    assert result == "cached"


@pytest.mark.asyncio
async def test_generate_l2_cache_hit():
    ttl_cache = MagicMock()
    ttl_cache.get.return_value = None

    response_cache = MagicMock()
    response_cache.get = AsyncMock(return_value="cached_l2")

    service = LLMService(
        provider=MagicMock(),
        ttl_cache=ttl_cache,
        response_cache=response_cache,
    )

    result = await service.generate(DummyRequest())

    assert result == "cached_l2"
    ttl_cache.set.assert_called_once()


@pytest.mark.asyncio
async def test_generate_calls_provider():
    provider = MagicMock()
    provider.generate = AsyncMock(return_value="response")

    with patch(
        "rpg_narrative_server.application.services.llm.llm_service.resilient_call",
        new=AsyncMock(return_value="ok"),
    ):
        service = LLMService(provider=provider)

        result = await service.generate(DummyRequest())

    assert result == "ok"


@pytest.mark.asyncio
async def test_generate_sets_caches():
    ttl_cache = MagicMock()
    ttl_cache.get.return_value = None

    response_cache = MagicMock()
    response_cache.get = AsyncMock(return_value=None)
    response_cache.set = AsyncMock()

    with patch(
        "rpg_narrative_server.application.services.llm.llm_service.resilient_call",
        new=AsyncMock(return_value="ok"),
    ):
        service = LLMService(
            provider=MagicMock(),
            ttl_cache=ttl_cache,
            response_cache=response_cache,
        )

        result = await service.generate(DummyRequest())

    assert result == "ok"
    ttl_cache.set.assert_called_once()
    response_cache.set.assert_called_once()


@pytest.mark.asyncio
async def test_generate_empty_response():
    with patch(
        "rpg_narrative_server.application.services.llm.llm_service.resilient_call",
        new=AsyncMock(return_value=""),
    ):
        service = LLMService(provider=MagicMock())

        result = await service.generate(DummyRequest())

    assert result == ""


@pytest.mark.asyncio
async def test_generate_exception():
    with patch(
        "rpg_narrative_server.application.services.llm.llm_service.resilient_call",
        new=AsyncMock(side_effect=ValueError("fail")),
    ):
        service = LLMService(provider=MagicMock())

        with pytest.raises(ValueError):
            await service.generate(DummyRequest())


def test_cache_key_deterministic():
    service = LLMService(provider=MagicMock())

    req1 = DummyRequest(prompt="hello")
    req2 = DummyRequest(prompt="hello")

    assert service._cache_key(req1) == service._cache_key(req2)


def test_cache_key_changes():
    service = LLMService(provider=MagicMock())

    req1 = DummyRequest(prompt="hello", temperature=0.0)
    req2 = DummyRequest(prompt="hello", temperature=1.0)

    assert service._cache_key(req1) != service._cache_key(req2)


def test_compute_timeout_dynamic():
    service = LLMService(provider=MagicMock(), timeout=60)

    req = DummyRequest(max_tokens=100)

    result = service._compute_timeout(req)

    assert result <= 60
    assert result >= 30


def test_compute_timeout_default():
    service = LLMService(provider=MagicMock(), timeout=60)

    req = DummyRequest(max_tokens=None)

    assert service._compute_timeout(req) == 60


@pytest.mark.asyncio
async def test_circuit_open_blocks_call():
    cb = CircuitBreaker(failure_threshold=1)
    cb.failure()

    service = LLMService(
        provider=MagicMock(),
        circuit_breaker=cb,
    )

    with pytest.raises(RuntimeError):
        await service.generate(DummyRequest())


@pytest.mark.asyncio
async def test_success_resets_circuit():
    cb = CircuitBreaker(failure_threshold=1)

    with patch(
        "rpg_narrative_server.application.services.llm.llm_service.resilient_call",
        new=AsyncMock(return_value="ok"),
    ):
        service = LLMService(
            provider=MagicMock(),
            circuit_breaker=cb,
        )

        result = await service.generate(DummyRequest())

    assert result == "ok"
    assert cb.state == "CLOSED"


@pytest.mark.asyncio
async def test_failure_triggers_circuit():
    cb = CircuitBreaker(failure_threshold=1)

    with patch(
        "rpg_narrative_server.application.services.llm.llm_service.resilient_call",
        new=AsyncMock(side_effect=ValueError()),
    ):
        service = LLMService(
            provider=MagicMock(),
            circuit_breaker=cb,
        )

        with pytest.raises(ValueError):
            await service.generate(DummyRequest())

    assert cb.state == "OPEN"


def test_cache_key_with_metadata_and_tools():
    from rpg_narrative_server.application.services.llm.llm_service import LLMService

    svc = LLMService(DummyProvider())

    req = Req(
        metadata={"a": 1},
        tools=[{"name": "tool"}],
    )

    key = svc._cache_key(req)

    assert isinstance(key, str)


@pytest.mark.asyncio
async def test_circuit_breaker_blocks():
    from rpg_narrative_server.application.services.llm.llm_service import LLMService

    svc = LLMService(
        DummyProvider(),
        circuit_breaker=DummyCB(allow=False),
    )

    req = Req()

    with pytest.raises(RuntimeError):
        await svc.generate(req)


@pytest.mark.asyncio
async def test_generate_returns_none():
    from rpg_narrative_server.application.services.llm.llm_service import LLMService

    class Provider:
        async def generate(self, req):
            return None

    svc = LLMService(Provider())

    result = await svc.generate(Req())

    assert result is None


@pytest.mark.asyncio
async def test_stream():
    from rpg_narrative_server.application.services.llm.llm_service import LLMService

    svc = LLMService(DummyProvider())

    chunks = []
    async for c in svc.stream(Req()):
        chunks.append(c)

    assert chunks == ["chunk"]
