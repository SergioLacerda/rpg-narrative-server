import pytest

from rpg_narrative_server.usecases.narrative_event import NarrativeUseCase
from rpg_narrative_server.domain.rag.context_builder import ContextBuilder

from tests.config.fakes.narrative import (
    DummyLLM,
    DummyMemoryService,
    DummyVectorIndex,
    DummyEventBus,
    DummyVectorMemory,
    DummyDocumentResolver,
)


@pytest.mark.asyncio
async def test_narrative_calls_llm():
    llm = DummyLLM()

    memory_service = DummyMemoryService(history=["look around"])

    context_builder = ContextBuilder(memory_service=memory_service)

    usecase = NarrativeUseCase(
        repo=None,
        llm=llm,
        vector_index=DummyVectorIndex(),
        event_bus=DummyEventBus(),
        memory_service=memory_service,
        vector_memory=DummyVectorMemory(),
        document_resolver=DummyDocumentResolver(),
        context_builder=context_builder,
    )

    # 🔥 MOCK CORRETO
    async def fake_build(**kwargs):
        return {
            "summary": "",
            "recent_events": ["look around"],
            "history": ["look around"],
            "retrieved": "",
            "entities": [],
            "related_entities": [],
            "scene_type": "ACTION",
        }

    usecase.context_builder.build = fake_build

    result = await usecase.execute(campaign_id="c", action="open door", user_id="u")

    assert result
    assert "open door" in result or "door" in result
    assert "permanece incerto" not in result
