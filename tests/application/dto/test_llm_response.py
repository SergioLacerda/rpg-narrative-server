from typing import cast

from rpg_narrative_server.application.dto.llm_response import LLMResponse


def test_to_dict_full():
    resp = LLMResponse(
        content="hello",
        provider="openai",
        model="gpt",
        latency_ms=123.4,
        tokens_input=10,
        tokens_output=20,
        raw={"a": 1},
    )

    data = resp.to_dict()

    assert data["content"] == "hello"
    assert data["provider"] == "openai"
    assert data["model"] == "gpt"
    assert data["latency_ms"] == 123.4
    assert data["tokens_input"] == 10
    assert data["tokens_output"] == 20
    assert data["raw"] == {"a": 1}
    assert data["v"] == 1


def test_from_dict_none():
    assert LLMResponse.from_dict(cast(dict, None)) is None
    assert LLMResponse.from_dict({}) is None


def test_from_dict_string():
    resp = LLMResponse.from_dict(cast(dict, "hello"))

    assert resp is not None
    assert resp.content == "hello"
    assert resp.provider == "unknown"


def test_from_dict_full():
    data = {
        "content": "hi",
        "provider": "openai",
        "model": "gpt",
        "latency_ms": 1.2,
        "tokens_input": 5,
        "tokens_output": 6,
        "raw": {"x": 1},
    }

    resp = LLMResponse.from_dict(data)

    assert resp is not None

    assert resp.content == "hi"

    assert resp.content == "hi"
    assert resp.provider == "openai"
    assert resp.model == "gpt"
    assert resp.latency_ms == 1.2
    assert resp.tokens_input == 5
    assert resp.tokens_output == 6
    assert resp.raw == {"x": 1}


def test_from_dict_partial():
    resp = LLMResponse.from_dict({"content": "x"})

    assert resp is not None

    assert resp.content == "x"

    assert resp.content == "x"
    assert resp.provider == "unknown"
    assert resp.model is None


def test_safe_raw_none():
    resp = LLMResponse(content="x", provider="p", raw=None)

    assert resp.to_dict()["raw"] is None


def test_safe_raw_serializable():
    resp = LLMResponse(content="x", provider="p", raw={"a": 1})

    assert resp.to_dict()["raw"] == {"a": 1}


def test_safe_raw_not_serializable():
    class Bad:
        pass

    resp = LLMResponse(
        content="x",
        provider="p",
        raw=cast(dict, Bad()),
    )

    result = resp.to_dict()["raw"]

    assert isinstance(result, str)
