import pytest
import asyncio

from tests.config.fakes.llm.fake_responses import (
    FakeResponseEmpty, 
    FakeResponseOpenAI, 
    FakeOllamaResponse
)

import rpg_narrative_server.infrastructure.llm as providers_mod

from rpg_narrative_server.infrastructure.llm.ollama_provider import OllamaProvider
from rpg_narrative_server.infrastructure.llm.openai_provider import OpenAIProvider
from rpg_narrative_server.infrastructure.llm.deepseek_provider import DeepSeekProvider
from rpg_narrative_server.infrastructure.llm.lmstudio_provider import LMStudioProvider
from rpg_narrative_server.infrastructure.llm.anthropic_provider import AnthropicProvider
from rpg_narrative_server.infrastructure.llm.groq_provider import GroqProvider
from rpg_narrative_server.infrastructure.llm.gemini_provider import GeminiProvider

from rpg_narrative_server.application.dto.llm_request import LLMRequest
from rpg_narrative_server.application.services.llm.llm_errors import (
    LLMRetryableError,
    LLMTimeoutError,
    LLMClientError
)


@pytest.mark.asyncio
async def test_provider_success(monkeypatch):

    provider = OpenAIProvider(api_key="x", model="test")

    async def fake_call(*args, **kwargs):
        return FakeResponseOpenAI("hello")

    monkeypatch.setattr(provider, "_call_api", fake_call)

    req = LLMRequest(prompt="hi")

    result = await provider.generate(req)

    assert result == "hello"


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
async def test_provider_timeout(monkeypatch):

    provider = LMStudioProvider(base_url="http://x", model="m", timeout=0.01)

    async def slow(*args, **kwargs):
        import asyncio
        await asyncio.sleep(1)

    monkeypatch.setattr(
        provider.client.chat.completions,
        "create",
        slow
    )

    req = LLMRequest(prompt="hi")

    with pytest.raises(Exception): 
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

    assert result == "dragon"


@pytest.mark.asyncio
@pytest.mark.parametrize("provider_cls,kwargs", [
    ("OpenAIProvider", {"api_key": "x", "model": "m"}),
    ("LMStudioProvider", {"base_url": "http://x", "model": "m"}),
    ("DeepSeekProvider", {"api_key": "x", "model": "m"}),
])
async def test_all_providers_success(monkeypatch, provider_cls, kwargs):

    cls = getattr(providers_mod, provider_cls)
    provider = cls(**kwargs)

    async def fake_call(*args, **kwargs):
        return FakeResponseOpenAI("ok")

    monkeypatch.setattr(provider, "_call_api", fake_call)

    result = await provider.generate(
        LLMRequest(prompt="test")
    )

    assert result == "ok"

@pytest.mark.asyncio
async def test_lmstudio_success(monkeypatch):

    provider = LMStudioProvider(base_url="http://x", model="m")

    class FakeResp:
        choices = [
            type("obj", (), {
                "message": type("msg", (), {"content": "ok"})
            })
        ]

    async def fake_create(*args, **kwargs):
        return FakeResp()

    monkeypatch.setattr(
        provider.client.chat.completions,
        "create",
        fake_create
    )

    result = await provider.generate(LLMRequest(prompt="test"))

    assert result == "ok"