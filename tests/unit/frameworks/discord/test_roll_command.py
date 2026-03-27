import pytest

from tests.config.helpers.discord_factory import (
    make_ctx,
    DummyBot,
    DummyExecutor,
    DummySettings,
)
from tests.config.fakes.discord.usecases import DummyUsecases, DummyRollDice

from rpg_narrative_server.frameworks.discord.commands.roll_commands import (
    register_roll_command,
)


@pytest.fixture
def bot():
    return DummyBot()


@pytest.fixture
def executor():
    return DummyExecutor(settings=DummySettings(), debug=True)


@pytest.mark.asyncio
async def test_roll_success(bot, executor):

    register_roll_command(
        bot, DummyUsecases(roll_dice=DummyRollDice("resultado")), executor
    )

    ctx = make_ctx()

    await bot._command(ctx, expression="1d20")

    assert ctx.sent_messages


@pytest.mark.asyncio
async def test_roll_empty_expression(bot, executor):

    register_roll_command(bot, DummyUsecases(roll_dice=DummyRollDice()), executor)

    ctx = make_ctx()

    await bot._command(ctx, expression="")

    assert "⚠️" in ctx.sent_messages[0]


@pytest.mark.asyncio
async def test_roll_no_result(bot, executor):

    register_roll_command(bot, DummyUsecases(roll_dice=DummyRollDice(None)), executor)

    ctx = make_ctx()

    await bot._command(ctx, expression="1d20")

    assert "⚠️" in ctx.sent_messages[0]
