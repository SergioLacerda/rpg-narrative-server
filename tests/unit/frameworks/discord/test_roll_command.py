import pytest

from rpg_narrative_server.frameworks.discord.adapters.roll_commands import (
    register_roll_command,
)
from tests.config.factories.bot import make_bot, make_executor
from tests.config.factories.context import make_context
from tests.config.factories.deps import make_deps
from tests.config.fakes.usecases import DummyRoll

# ---------------------------------------------------------
# SUCCESS
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_roll_success():
    ctx = make_context(guild_id=None, user_id="999")
    bot = make_bot()
    executor = make_executor()

    deps = make_deps(roll_dice=DummyRoll(result="resultado"))
    registry = bot._registry

    register_roll_command(bot, deps, executor, registry)

    await bot._command(ctx, expression="1d20")

    assert ctx.sent_messages


# ---------------------------------------------------------
# EMPTY EXPRESSION
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_roll_empty_expression():
    ctx = make_context(guild_id=None, user_id="999")
    bot = make_bot()
    executor = make_executor()

    deps = make_deps(roll_dice=DummyRoll())
    registry = bot._registry

    register_roll_command(bot, deps, executor, registry)

    await bot._command(ctx, expression="")

    assert ctx.sent_messages
    assert ctx.sent_messages[0] != ""


# ---------------------------------------------------------
# NO RESULT
# ---------------------------------------------------------


async def test_roll_no_result():
    ctx = make_context(guild_id=None, user_id="999")
    bot = make_bot()
    executor = make_executor()

    deps = make_deps(roll_dice=DummyRoll(result=None))

    registry = bot._registry

    register_roll_command(bot, deps, executor, registry)

    await bot._command(ctx, expression="1d20")

    assert ctx.sent_messages
    assert "⚠️" in ctx.sent_messages[0]
