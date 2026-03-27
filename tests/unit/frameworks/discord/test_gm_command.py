import pytest

from tests.config.helpers.discord_factory import make_ctx, DummyBot, DummyExecutor, DummySettings
from tests.config.fakes.discord.usecases import DummyUsecases, DummyNarrative

from rpg_narrative_server.frameworks.discord.commands.gm_commands import register_gm_command


@pytest.fixture
def bot():
    return DummyBot()


@pytest.fixture
def executor():
    return DummyExecutor(settings=DummySettings(), debug=True)


@pytest.mark.asyncio
async def test_gm_command_success(bot, executor):

    register_gm_command(bot, DummyUsecases(narrative=DummyNarrative()), executor)

    ctx = make_ctx()

    await bot._command(ctx, action="attack")

    assert ctx.sent_messages


@pytest.mark.asyncio
async def test_gm_empty_action(bot, executor):

    register_gm_command(bot, DummyUsecases(narrative=DummyNarrative()), executor)

    ctx = make_ctx()

    await bot._command(ctx, action="")

    assert "⚠️" in ctx.sent_messages[0]


@pytest.mark.asyncio
async def test_gm_no_response(bot, executor):

    register_gm_command(bot, DummyUsecases(narrative=DummyNarrative(result=None)), executor)

    ctx = make_ctx()

    await bot._command(ctx, action="attack")

    assert "⚠️" in ctx.sent_messages[0]


@pytest.mark.asyncio
async def test_gm_exception(bot, executor):

    register_gm_command(
        bot,
        DummyUsecases(narrative=DummyNarrative(error=RuntimeError("boom"))),
        executor,
    )

    ctx = make_ctx()

    with pytest.raises(RuntimeError):
        await bot._command(ctx, action="attack")