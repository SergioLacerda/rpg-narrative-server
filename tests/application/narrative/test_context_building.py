import pytest

from rpg_narrative_server.domain.rag.context_builder import ContextBuilder
from rpg_narrative_server.domain.rag.context_formatter import ContextFormatter

from tests.config.fakes.narrative.memory_service import DummyMemoryService

# ---------------------------------------------------------
# BASICO
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_context_includes_history_and_retrieved():

    memory = DummyMemoryService(history=["open door"])

    builder = ContextBuilder(memory_service=memory)

    ctx = await builder.build(
        campaign_id="c",
        action="test",
        history=["ação1", "ação2"],
        retrieved="doc1",
    )

    formatter = ContextFormatter()
    context = formatter.format(ctx)

    assert "Eventos recentes" in context
    assert "open door" in context

    assert "Memória relevante" in context
    assert "doc1" in context


@pytest.mark.asyncio
async def test_context_empty():

    memory = DummyMemoryService(history=[])

    builder = ContextBuilder(memory_service=memory)

    ctx = await builder.build(
        campaign_id="c",
        action="test",
        history=[],
        retrieved="",
    )

    formatter = ContextFormatter()
    context = formatter.format(ctx)

    assert context == ""


# ---------------------------------------------------------
# HISTORY
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_history_truncation():

    history = [f"h{i}" for i in range(30)]

    memory = DummyMemoryService(history=history)

    builder = ContextBuilder(memory_service=memory)

    ctx = await builder.build(
        campaign_id="c",
        action="test",
        history=history,
        retrieved="",
    )

    formatter = ContextFormatter()
    context = formatter.format(ctx)

    assert "h0" not in context
    assert "h29" in context


# ---------------------------------------------------------
# RETRIEVED
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_retrieved_deduplication():

    memory = DummyMemoryService()

    builder = ContextBuilder(memory_service=memory)

    ctx = await builder.build(
        campaign_id="c",
        action="test",
        history=[],
        retrieved="doc1\ndoc1\ndoc2",
    )

    formatter = ContextFormatter()
    context = formatter.format(ctx)

    assert "doc1" in context
    assert "doc2" in context


# ---------------------------------------------------------
# ORDEM
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_block_order():

    memory = DummyMemoryService(history=["h1"])

    builder = ContextBuilder(memory_service=memory)

    ctx = await builder.build(
        campaign_id="c",
        action="test",
        history=["h1"],
        retrieved="d1",
    )

    formatter = ContextFormatter()
    context = formatter.format(ctx)

    assert context.index("Eventos") < context.index("Memória relevante")
