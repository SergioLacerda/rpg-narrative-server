import pytest

from tests.config.helpers.discord_factory import make_ctx, DummyResponse, DummyInteraction, DummyCtx

from rpg_narrative_server.frameworks.discord.responder import send


@pytest.mark.asyncio
async def test_send_with_interaction():
    ctx = make_ctx(interaction=True)

    await send(ctx, "hello")

    assert ctx.sent_messages[0] == "hello"


@pytest.mark.asyncio
async def test_send_fallback():
    ctx = make_ctx()

    await send(ctx, "hello")

    assert ctx.sent_messages[0] == "hello"