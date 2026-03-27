import pytest

from tests.config.fakes.llm.llm import DummyLLM

from rpg_narrative_server.application.services.intent.llm_intent_classifier import LLMIntentClassifier


@pytest.mark.asyncio
async def test_llm_classify_basic():
    llm = DummyLLM("ACTION")

    clf = LLMIntentClassifier(lambda: llm)

    result = await clf.classify("attack now")

    assert result == "ACTION"


@pytest.mark.asyncio
async def test_llm_response_normalization():
    llm = DummyLLM(" action ")

    clf = LLMIntentClassifier(lambda: llm)

    result = await clf.classify("attack")

    assert result == "ACTION"


@pytest.mark.asyncio
async def test_prompt_sent_correctly():
    llm = DummyLLM("ACTION")

    clf = LLMIntentClassifier(lambda: llm)

    await clf.classify("hello")

    call = llm.calls[0]

    assert "hello" in call["prompt"]
    assert call["temperature"] == 0.0
    assert call["max_tokens"] == 5


@pytest.mark.asyncio
async def test_llm_instance_cached():
    llm = DummyLLM()

    factory_calls = {"count": 0}

    def factory():
        factory_calls["count"] += 1
        return llm

    clf = LLMIntentClassifier(factory)

    await clf.classify("a")
    await clf.classify("b")

    assert factory_calls["count"] == 1


@pytest.mark.asyncio
async def test_rule_based_skips_llm():
    class FakeLLM:
        async def generate(self, _):
            raise Exception("should not be called")

    clf = LLMIntentClassifier(lambda: FakeLLM())

    result = await clf.classify("eu ataco o goblin")

    assert result == "ACTION"


def test_rule_based_none():
    clf = LLMIntentClassifier(lambda: None)

    assert clf._rule_based("texto neutro") is None

@pytest.mark.asyncio
async def test_llm_empty_response():
    class FakeLLM:
        async def generate(self, _):
            return ""

    clf = LLMIntentClassifier(lambda: FakeLLM())

    result = await clf.classify("teste")

    assert result == "CHAT"


@pytest.mark.asyncio
async def test_llm_invalid_response():
    class FakeLLM:
        async def generate(self, _):
            return "banana"

    clf = LLMIntentClassifier(lambda: FakeLLM())

    result = await clf.classify("teste")

    assert result == "CHAT"


@pytest.mark.asyncio
async def test_llm_partial_match():
    class FakeLLM:
        async def generate(self, _):
            return "ACTION detected"

    clf = LLMIntentClassifier(lambda: FakeLLM())

    result = await clf.classify("teste")

    assert result == "ACTION"


@pytest.mark.asyncio
async def test_llm_exception():
    class FakeLLM:
        async def generate(self, _):
            raise Exception()

    clf = LLMIntentClassifier(lambda: FakeLLM())

    result = await clf.classify("teste")

    assert result == "CHAT"


