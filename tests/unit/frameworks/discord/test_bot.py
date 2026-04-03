import pytest
from discord.ext import commands

from rpg_narrative_server.frameworks.discord.bot import create_bot
from tests.config.factories.context import make_context
from tests.config.factories.deps import make_deps
from tests.config.factories.help import make_help
from tests.config.helpers.discord_factory import DummySettings

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------


@pytest.fixture(autouse=True)
def mock_help_command(monkeypatch):
    monkeypatch.setattr(
        "rpg_narrative_server.frameworks.discord.bot.register_help_commands",
        lambda bot: make_help(),
    )


def make_test_bot():
    return create_bot(
        settings=DummySettings,
        deps=make_deps(),
    )


# ---------------------------------------------------------
# BOT CREATION
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_bot_creation():
    bot = make_test_bot()

    assert bot is not None


# ---------------------------------------------------------
# COOLDOWN ERROR
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_on_command_error_cooldown():
    bot = make_test_bot()
    ctx = make_context(guild_id=None, user_id="999")

    cooldown = commands.Cooldown(1, 3)
    error = commands.CommandOnCooldown(cooldown, 1.5, commands.BucketType.user)

    await bot.on_command_error(ctx, error)

    assert ctx.sent_messages
    assert "⏳" in ctx.sent_messages[0]


# ---------------------------------------------------------
# READY SUCCESS
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_on_ready_sync_called(monkeypatch):
    bot = make_test_bot()

    called = {}

    async def fake_sync():
        called["ok"] = True
        return []

    bot.tree.sync = fake_sync

    await bot.on_ready()

    assert called.get("ok") is True


# ---------------------------------------------------------
# READY FAILURE
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_on_ready_sync_failure(monkeypatch):
    bot = make_test_bot()

    async def fake_sync():
        raise RuntimeError("fail")

    bot.tree.sync = fake_sync

    await bot.on_ready()


# ---------------------------------------------------------
# GENERIC ERROR
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_on_command_error_generic():
    bot = make_test_bot()
    ctx = make_context(guild_id=None, user_id="999")

    await bot.on_command_error(ctx, RuntimeError("boom"))

    assert ctx.sent_messages
    assert "⚠️" in ctx.sent_messages[0]
