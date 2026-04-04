import asyncio
from types import SimpleNamespace

import pytest

from rpg_narrative_server.usecases.end_session import EndSessionUseCase

# ==========================================================
# MOCKS
# ==========================================================


class MockMemory:
    def __init__(self, events):
        self.events = events
        self.cleared = False

    async def load_memory(self, campaign_id):
        return SimpleNamespace(recent_events=self.events)

    async def clear(self, campaign_id):
        self.cleared = True


class MockLLM:
    def __init__(self, content=None, fail=False):
        self.content = content
        self.fail = fail

    async def generate(self, request):
        if self.fail:
            raise Exception("boom")
        return SimpleNamespace(content=self.content)


class MockVectorMemory:
    async def store_event(self, **kwargs):
        pass


class FailingLLM:
    async def generate(self, prompt):
        raise Exception("fail")


class EmptyLLM:
    async def generate(self, prompt):
        return ""


# ==========================================================
# HELPERS
# ==========================================================


def build_usecase(events, llm_content="summary", fail=False):
    memory = MockMemory(events)
    llm = MockLLM(content=llm_content, fail=fail)
    vector_memory = MockVectorMemory()

    return EndSessionUseCase(memory, llm, vector_memory), memory


def fake_create_task(coro):
    return asyncio.get_event_loop().create_task(coro)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_end_session_basic(container):
    result = await container.end_session.execute("test")
    assert result is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_end_session_persists_summary(container):
    await container.narrative.execute(campaign_id="test", action="something", user_id="user1")

    result = await container.end_session.execute("test")

    assert result is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("llm", [FailingLLM(), EmptyLLM()])
async def test_end_session_llm_edge_cases(container_factory, llm):
    container = container_factory(llm=llm)

    result = await container.end_session.execute("test")

    assert result is not None


@pytest.mark.asyncio
async def test_end_session_event_bus_failure(container, monkeypatch):
    monkeypatch.setattr(
        container.event_bus,
        "publish",
        lambda *a, **k: (_ for _ in ()).throw(Exception()),
    )

    result = await container.end_session.execute("test")

    assert result is not None


@pytest.mark.asyncio
async def test_end_session_index_failure(container, monkeypatch):
    async def fail(*args, **kwargs):
        raise Exception()

    monkeypatch.setattr(container.vector_index, "index_campaign", fail)

    result = await container.end_session.execute("test")

    assert result is not None


@pytest.mark.asyncio
async def test_end_session_no_memory(container):
    await container.memory_service.clear("empty")

    result = await container.end_session.execute("empty")

    assert result is not None


@pytest.mark.asyncio
async def test_end_session_clears_memory(container):
    await container.narrative.execute(campaign_id="test", action="action", user_id="user")

    await container.end_session.execute("test")

    memory = await container.memory_service.load_memory("test")

    assert memory.recent_events == []


@pytest.mark.asyncio
async def test_end_session_empty_extracted_text(container, monkeypatch):
    monkeypatch.setattr(container.end_session.summarizer, "extract", lambda x: "")

    result = await container.end_session.execute("test")

    assert result is not None


@pytest.mark.asyncio
async def test_no_events():
    usecase, _ = build_usecase(events=[])

    result = await usecase.execute("c1")

    assert "Nenhum evento" in result


@pytest.mark.asyncio
async def test_empty_text(monkeypatch):
    usecase, _ = build_usecase(events=["event"])

    monkeypatch.setattr(
        usecase.summarizer,
        "extract",
        lambda x: "   ",
    )

    result = await usecase.execute("c1")

    assert "sem eventos relevantes" in result


@pytest.mark.asyncio
async def test_llm_success():
    usecase, memory = build_usecase(events=["event"], llm_content="final summary")

    result = await usecase.execute("c1")

    assert result == "final summary"
    assert memory.cleared is True


@pytest.mark.asyncio
async def test_llm_failure_fallback():
    usecase, _ = build_usecase(events=["event"], fail=True)

    result = await usecase.execute("c1")

    assert len(result) > 0


@pytest.mark.asyncio
async def test_llm_empty_response_fallback():
    usecase, _ = build_usecase(events=["event"], llm_content="   ")

    result = await usecase.execute("c1")

    assert len(result) > 0


@pytest.mark.asyncio
async def test_vector_memory_called(monkeypatch):
    usecase, _ = build_usecase(events=["event"])

    called = {"ok": False}

    async def fake_store_event(**kwargs):
        called["ok"] = True

    monkeypatch.setattr(
        usecase.vector_memory,
        "store_event",
        fake_store_event,
    )

    monkeypatch.setattr("asyncio.create_task", fake_create_task)

    await usecase.execute("c1")

    await asyncio.sleep(0)

    assert called["ok"] is True
