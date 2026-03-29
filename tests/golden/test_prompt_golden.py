from pathlib import Path

import pytest

from rpg_narrative_server.domain.narrative.narrative_builder import NarrativeBuilder
from rpg_narrative_server.domain.rag.context_builder import ContextBuilder
from tests.config.fakes.narrative.memory_service import DummyMemoryService
from tests.config.helpers.golden_assert import assert_golden, normalize

GOLDEN_DIR = Path(__file__).parent / "prompts"
UPDATE_GOLDEN = False


def assert_prompt_structure(prompt: str):
    assert "Você é um mestre de RPG" in prompt
    assert "Ação do jogador:" in prompt
    assert "Continue a narrativa" in prompt


def build_prompt(ctx: dict, action: str) -> str:
    builder = NarrativeBuilder()

    system = builder.build_system_prompt(str(ctx.get("scene_type") or "DEFAULT"))

    user = builder.build_user_prompt(
        ctx=ctx,
        action=action,
    )

    return normalize(f"{system}\n\n{user}")


# ---------------------------------------------------------
# HISTORY
# ---------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.golden
async def test_prompt_with_history_golden():
    memory_service = DummyMemoryService(history=["open door"])

    context_builder = ContextBuilder(memory_service=memory_service)

    ctx, _ = await context_builder.build(
        campaign_id="test",
        action="enter room",
        history=["open door", "look around"],
        retrieved=[],
    )

    prompt = build_prompt(ctx, "enter room")

    assert "Eventos recentes:" in prompt
    assert "open door" in prompt
    assert "Memória relevante:" not in prompt

    assert_prompt_structure(prompt)

    assert_golden(GOLDEN_DIR / "with_history.txt", prompt, update=UPDATE_GOLDEN)


# ---------------------------------------------------------
# MEMORY
# ---------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.golden
async def test_prompt_with_memory_golden():
    memory_service = DummyMemoryService(history=["abriu a porta"])

    context_builder = ContextBuilder(memory_service=memory_service)

    ctx, _ = await context_builder.build(
        campaign_id="test",
        action="entrar na sala",
        history=["abriu a porta"],
        retrieved="um cheiro estranho no ar",
    )

    prompt = build_prompt(ctx, "entrar na sala")

    assert "Memória relevante:" in prompt
    assert "um cheiro estranho no ar" in prompt

    assert_prompt_structure(prompt)

    assert_golden(GOLDEN_DIR / "with_memory.txt", prompt, update=UPDATE_GOLDEN)
