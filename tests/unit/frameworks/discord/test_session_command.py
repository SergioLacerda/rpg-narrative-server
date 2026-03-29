import pytest

from rpg_narrative_server.frameworks.discord.adapters.session_commands import (
    register_session_commands,
)
from tests.config.factories.bot import make_bot, make_executor
from tests.config.factories.context import make_context
from tests.config.factories.deps import make_deps
from tests.config.fakes.usecases import DummyEndSession

# ---------------------------------------------------------
# SUCCESS
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_endsession_success():
    ctx = make_context(interaction=False)
    bot = make_bot()
    executor = make_executor()

    deps = make_deps(end_session=DummyEndSession("summary"))

    # 🔥 FIX
    deps.campaign_state.set(ctx.channel.id, "test_campaign")

    registry = bot._registry

    register_session_commands(bot, deps, executor, registry)

    cmd = bot.get_command("endsession")
    assert cmd is not None

    await cmd.callback(ctx)

    assert ctx.sent_messages
    assert any(keyword in ctx.sent_messages[0] for keyword in ("🛑", "encerrada"))


# ---------------------------------------------------------
# NO SUMMARY
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_endsession_no_summary():
    ctx = make_context()
    bot = make_bot()
    executor = make_executor()

    deps = make_deps(end_session=DummyEndSession(None))
    registry = bot._registry

    register_session_commands(bot, deps, executor, registry)

    cmd = bot.get_command("endsession")
    assert cmd is not None

    await cmd.callback(ctx)

    assert ctx.sent_messages
    assert "⚠️" in ctx.sent_messages[0]
