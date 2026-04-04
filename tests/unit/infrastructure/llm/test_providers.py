import pytest

import rpg_narrative_server.infrastructure.adapters.llm as providers_mod
from rpg_narrative_server.application.dto.llm_request import LLMRequest
from rpg_narrative_server.application.services.llm.llm_errors import (
    LLMClientError,
    LLMRetryableError,
)
from rpg_narrative_server.infrastructure.adapters.llm.lmstudio_provider import LMStudioProvider
from rpg_narrative_server.infrastructure.adapters.llm.ollama_provider import OllamaProvider
from rpg_narrative_server.infrastructure.adapters.llm.openai_provider import OpenAIProvider
from tests.config.fakes.llm.fake_responses import (
    FakeOllamaResponse,
    FakeResponseEmpty,
    FakeResponseOpenAI,
)


@pytest.mark.asyncio
async def test_provider_success(monkeypatch):
    provider = OpenAIProvider(api_key="x", model="test")

    async def fake_call(*args, **kwargs):
        return FakeResponseOpenAI("hello")

    monkeypatch.setattr(provider, "_call_api", fake_call)

    req = LLMRequest(prompt="hi")

    result = await provider.generate(req)

    assert result.content == "hello"


@pytest.mark.asyncio
async def test_provider_empty_response(monkeypatch):
    provider = OpenAIProvider(api_key="x", model="test")

    async def fake_call(*args, **kwargs):
        return FakeResponseEmpty()

    monkeypatch.setattr(provider, "_call_api", fake_call)

    req = LLMRequest(prompt="hi")

    with pytest.raises(LLMRetryableError):
        await provider.generate(req)


@pytest.mark.asyncio
async def test_provider_generic_error(monkeypatch):
    provider = OpenAIProvider(api_key="x", model="test")

    async def fake_call(*args, **kwargs):
        raise Exception("boom")

    monkeypatch.setattr(provider, "_call_api", fake_call)

    req = LLMRequest(prompt="hi")

    with pytest.raises(LLMRetryableError):
        await provider.generate(req)


@pytest.mark.asyncio
async def test_provider_client_error(monkeypatch):
    provider = OpenAIProvider(api_key="x", model="test")

    async def fake_call(*args, **kwargs):
        raise ValueError("bad request")

    monkeypatch.setattr(provider, "_call_api", fake_call)

    req = LLMRequest(prompt="hi")

    with pytest.raises(LLMClientError):
        await provider.generate(req)


@pytest.mark.asyncio
async def test_ollama_response(monkeypatch):
    provider = OllamaProvider(model="x", base_url="http://localhost")

    async def fake_call(*args, **kwargs):
        return FakeOllamaResponse("dragon")

    monkeypatch.setattr(provider, "_call_api", fake_call)

    req = LLMRequest(prompt="hi")

    result = await provider.generate(req)

    assert result.content == "dragon"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "provider_cls,kwargs",
    [
        ("OpenAIProvider", {"api_key": "x", "model": "m"}),
        ("LMStudioProvider", {"base_url": "http://x", "model": "m"}),
        ("DeepSeekProvider", {"api_key": "x", "model": "m"}),
    ],
)
async def test_all_providers_success(monkeypatch, provider_cls, kwargs):
    cls = getattr(providers_mod, provider_cls)
    provider = cls(**kwargs)

    async def fake_call(*args, **kwargs):
        return FakeResponseOpenAI("ok")

    monkeypatch.setattr(provider, "_call_api", fake_call)

    result = await provider.generate(LLMRequest(prompt="test"))

    assert result.content == "ok"


@pytest.mark.asyncio
async def test_lmstudio_success(monkeypatch):
    provider = LMStudioProvider(base_url="http://x", model="m")

    class FakeResp:
        choices = [type("obj", (), {"message": type("msg", (), {"content": "ok"})})]

    async def fake_create(*args, **kwargs):
        return FakeResp()

    monkeypatch.setattr(provider.client.chat.completions, "create", fake_create)

    result = await provider.generate(LLMRequest(prompt="test"))

    assert result.content == "ok"
