import pytest

from tests.config.helpers.discord_factory import (
    make_ctx,
    DummyBot,
    DummyExecutor,
    DummySettings,
)
from tests.config.fakes.discord.usecases import DummyUsecases, DummyEndSession

from rpg_narrative_server.frameworks.discord.commands.session_command import (
    register_session_commands,
)


# ---------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------


@pytest.fixture
def bot():
    return DummyBot()


@pytest.fixture
def executor():
    return DummyExecutor(settings=DummySettings(), debug=True)


@pytest.mark.asyncio
async def test_endsession_success(executor):

    bot = DummyBot()

    register_session_commands(
        bot, DummyUsecases(end_session=DummyEndSession()), executor
    )

    ctx = make_ctx()

    await bot._command(ctx)

    assert ctx.sent_messages


@pytest.mark.asyncio
async def test_endsession_no_summary(executor):

    bot = DummyBot()

    register_session_commands(
        bot, DummyUsecases(end_session=DummyEndSession(None)), executor
    )

    ctx = make_ctx()

    await bot._command(ctx)

    assert "⚠️" in ctx.sent_messages[0]
