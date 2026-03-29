import pytest

from rpg_narrative_server.domain.narrative.narrative_memory import NarrativeMemory
from rpg_narrative_server.domain.rag.context_builder import ContextBuilder
from rpg_narrative_server.usecases.narrative_event import NarrativeUseCase
from tests.config.fakes.narrative import (
    DummyDocumentResolver,
    DummyEventBus,
    DummyLLM,
    DummyMemoryService,
    DummyVectorIndex,
    DummyVectorMemory,
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

    async def fake_build(**kwargs):
        return (
            {
                "summary": "",
                "recent_events": ["look around"],
                "history": ["look around"],
                "retrieved": "",
                "entities": [],
                "related_entities": [],
                "scene_type": "ACTION",
                "intent": "ACTION",
            },
            NarrativeMemory(),
        )

    usecase.context_builder.build = fake_build

    result = await usecase.execute(campaign_id="c", action="open door", user_id="u")

    assert result
    assert isinstance(result.text, str)

    assert "open door" in result.text or "door" in result.text
    assert "permanece incerto" not in result.text
