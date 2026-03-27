import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from tests.config.fakes.llm.fake_request import DummyRequest

from rpg_narrative_server.application.services.llm.llm_service import LLMService
from rpg_narrative_server.application.services.llm.circuit_breaker import CircuitBreaker

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

    with patch("rpg_narrative_server.application.services.llm.llm_service.resilient_call",new=AsyncMock(return_value="ok"),):
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

    with patch("rpg_narrative_server.application.services.llm.llm_service.resilient_call",new=AsyncMock(return_value="ok"),):
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
    with patch("rpg_narrative_server.application.services.llm.llm_service.resilient_call",new=AsyncMock(return_value=""),):
        service = LLMService(provider=MagicMock())

        result = await service.generate(DummyRequest())

    assert result == ""


@pytest.mark.asyncio
async def test_generate_exception():
    with patch("rpg_narrative_server.application.services.llm.llm_service.resilient_call",new=AsyncMock(side_effect=Exception("fail")),):
        service = LLMService(provider=MagicMock())

        with pytest.raises(Exception):
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
async def test_stream():
    async def fake_stream(_):
        yield "a"
        yield "b"

    provider = MagicMock()
    provider.stream = fake_stream

    service = LLMService(provider=provider)

    chunks = []
    async for c in service.stream(DummyRequest()):
        chunks.append(c)

    assert chunks == ["a", "b"]


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

    with patch("rpg_narrative_server.application.services.llm.llm_service.resilient_call", new=AsyncMock(return_value="ok")):
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

    with patch("rpg_narrative_server.application.services.llm.llm_service.resilient_call", new=AsyncMock(side_effect=Exception())):
        service = LLMService(
            provider=MagicMock(),
            circuit_breaker=cb,
        )

        with pytest.raises(Exception):
            await service.generate(DummyRequest())

    assert cb.state == "OPEN"


