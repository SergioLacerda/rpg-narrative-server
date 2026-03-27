import pytest
from pathlib import Path

from tests.config.fakes.narrative import (
    DummyLLM,
    DummyMemoryService,
    DummyVectorIndex,
    DummyEventBus,
    DummyVectorMemory,
    DummyDocumentResolver,
)

from tests.config.helpers.golden_assert import assert_golden
from rpg_narrative_server.usecases.narrative_event import NarrativeUseCase
from rpg_narrative_server.domain.rag.context_builder import ContextBuilder


@pytest.mark.asyncio
async def test_narrative_pipeline_prompt_golden():
    llm = DummyLLM()

    memory_service = DummyMemoryService(history=["open door"])

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

    # ---------------------------------------------------------
    # 🔥 MOCK CORRETO (async + ctx)
    # ---------------------------------------------------------

    async def fake_build(**kwargs):
        return {
            "summary": "",
            "recent_events": ["open door"],
            "history": ["open door"],
            "retrieved": "dark corridor",
            "entities": [],
            "related_entities": [],
            "scene_type": "DEFAULT",
        }

    usecase.context_builder.build = fake_build

    # ---------------------------------------------------------

    await usecase.execute(campaign_id="c", action="enter room", user_id="u")

    prompt = next(p for p in llm.calls if "Ação do jogador" in p)

    # ---------------------------------------------------------
    # ASSERTS FUNCIONAIS
    # ---------------------------------------------------------

    assert "open door" in prompt
    assert "dark corridor" in prompt
    assert "enter room" in prompt

    # ---------------------------------------------------------
    # GOLDEN SNAPSHOT
    # ---------------------------------------------------------

    path = Path(__file__).parent / "prompts" / "pipeline.txt"

    assert_golden(path, prompt, update=False)
