import pytest

from rpg_narrative_server.frameworks.discord.adapters.gm_commands import (
    register_gm_command,
)
from tests.config.factories.bot import make_bot, make_executor
from tests.config.factories.context import make_context
from tests.config.factories.deps import make_deps
from tests.config.fakes.usecases import DummyNarrative

# ---------------------------------------------------------
# SUCCESS
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_gm_command_success():
    ctx = make_context(guild_id=None, user_id="999")
    bot = make_bot()
    executor = make_executor()

    deps = make_deps(narrative=DummyNarrative(result="Ataque realizado"))
    registry = bot._registry

    register_gm_command(bot, deps, executor, registry)

    await bot._command(ctx, action="attack")

    assert ctx.sent_messages
    assert ctx.sent_messages[0] != ""


# ---------------------------------------------------------
# EMPTY INPUT
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_gm_empty_action():
    ctx = make_context(guild_id=None, user_id="999")
    bot = make_bot()
    executor = make_executor()

    deps = make_deps(narrative=DummyNarrative())
    registry = bot._registry

    register_gm_command(bot, deps, executor, registry)

    await bot._command(ctx, action="")

    assert ctx.sent_messages
    assert "⚠️" in ctx.sent_messages[0]


# ---------------------------------------------------------
# NO RESPONSE (Response vazio)
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_gm_no_response():
    ctx = make_context(guild_id=None, user_id="999")
    bot = make_bot()
    executor = make_executor()

    deps = make_deps(narrative=DummyNarrative(result=""))
    registry = bot._registry

    register_gm_command(bot, deps, executor, registry)

    await bot._command(ctx, action="attack")

    assert ctx.sent_messages
    assert "⚠️" in ctx.sent_messages[0]


# ---------------------------------------------------------
# EXCEPTION
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_gm_exception():
    ctx = make_context(guild_id=None, user_id="999")
    bot = make_bot()
    executor = make_executor()

    deps = make_deps(narrative=DummyNarrative(error=RuntimeError("boom")))

    # 🔥 FIX
    deps.campaign_state.set(ctx.channel.id, "test_campaign")

    registry = bot._registry

    register_gm_command(bot, deps, executor, registry)

    with pytest.raises(RuntimeError):
        await bot._command(ctx, action="attack")
