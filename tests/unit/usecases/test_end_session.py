import pytest


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

class FailingLLM:
    async def generate(self, prompt):
        raise Exception("fail")


class EmptyLLM:
    async def generate(self, prompt):
        return ""


# ---------------------------------------------------------
# TESTES BASE
# ---------------------------------------------------------

@pytest.mark.integration
@pytest.mark.asyncio
async def test_end_session_basic(container):
    result = await container.end_session.execute("test")
    assert result is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_end_session_persists_summary(container):
    await container.narrative.execute(
        campaign_id="test",
        action="something",
        user_id="user1"
    )

    result = await container.end_session.execute("test")

    assert result is not None


# ---------------------------------------------------------
# FALHAS (AGRUPADAS)
# ---------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize("llm", [FailingLLM(), EmptyLLM()])
async def test_end_session_llm_edge_cases(container_factory, llm):
    container = container_factory(llm=llm)

    result = await container.end_session.execute("test")

    assert result is not None


@pytest.mark.asyncio
async def test_end_session_event_bus_failure(container, monkeypatch):
    monkeypatch.setattr(container.event_bus, "publish", lambda *a, **k: (_ for _ in ()).throw(Exception()))

    result = await container.end_session.execute("test")

    assert result is not None


@pytest.mark.asyncio
async def test_end_session_index_failure(container, monkeypatch):
    async def fail(*args, **kwargs):
        raise Exception()

    monkeypatch.setattr(container.vector_index, "index_campaign", fail)

    result = await container.end_session.execute("test")

    assert result is not None


# ---------------------------------------------------------
# MEMORY CASES
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_end_session_no_memory(container):
    await container.memory_service.clear("empty")

    result = await container.end_session.execute("empty")

    assert result is not None


@pytest.mark.asyncio
async def test_end_session_clears_memory(container):
    await container.narrative.execute(
        campaign_id="test",
        action="action",
        user_id="user"
    )

    await container.end_session.execute("test")

    memory = await container.memory_service.load_memory("test")

    assert memory.recent_events == []


@pytest.mark.asyncio
async def test_end_session_empty_extracted_text(container, monkeypatch):
    monkeypatch.setattr(container.end_session.summarizer, "extract", lambda x: "")

    result = await container.end_session.execute("test")

    assert result is not None