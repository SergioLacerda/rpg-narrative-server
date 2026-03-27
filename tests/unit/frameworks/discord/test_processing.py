import pytest

from tests.config.helpers.discord_factory import make_ctx

from rpg_narrative_server.frameworks.discord.processing import start_processing


@pytest.mark.asyncio
async def test_processing_with_interaction():
    ctx = make_ctx(interaction=True)

    await start_processing(ctx)

    assert ctx.interaction.deferred is True


@pytest.mark.asyncio
async def test_processing_without_interaction():
    ctx = make_ctx()

    await start_processing(ctx)

    assert hasattr(ctx.channel, "typing_called")
