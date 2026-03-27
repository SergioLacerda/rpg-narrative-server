import pytest

from tests.config.helpers.ctx import make_ctx

from discord.ext import commands
from rpg_narrative_server.frameworks.discord.bot import create_bot


class DummySettings:
    class runtime:
        environment = "dev"


class DummyUsecases:
    pass


@pytest.mark.asyncio
async def test_bot_creation():
    bot = create_bot(
        settings=DummySettings(),
        usecases=DummyUsecases(),
    )

    assert bot is not None


@pytest.mark.asyncio
async def test_on_command_error_cooldown():

    bot = create_bot(
        settings=DummySettings(),
        usecases=DummyUsecases(),
    )

    class DummyCtx:
        def __init__(self):
            self.sent = []

        async def send(self, msg):
            self.sent.append(msg)

    ctx = make_ctx()

    from discord.ext import commands

    cooldown = commands.Cooldown(1, 3)
    error = commands.CommandOnCooldown(cooldown, 1.5, commands.BucketType.user)

    await bot.on_command_error(ctx, error)

    assert "⏳" in ctx.sent[0]


@pytest.mark.asyncio
async def test_on_ready_sync_called(monkeypatch):

    called = {}

    async def fake_sync():
        called["ok"] = True
        return []

    bot = create_bot(
        settings=DummySettings(),
        usecases=DummyUsecases(),
    )

    bot.tree.sync = fake_sync

    await bot.on_ready()

    assert called.get("ok") is True


@pytest.mark.asyncio
async def test_on_ready_sync_failure(monkeypatch):

    async def fake_sync():
        raise RuntimeError("fail")

    bot = create_bot(
        settings=DummySettings(),
        usecases=DummyUsecases(),
    )

    bot.tree.sync = fake_sync

    await bot.on_ready()


@pytest.mark.asyncio
async def test_on_command_error_generic(container):

    bot = create_bot(
        settings=DummySettings(),
        usecases=DummyUsecases(),
        container=container,
    )

    class DummyCtx:
        def __init__(self):
            self.sent = []

        async def send(self, msg):
            self.sent.append(msg)

    ctx = make_ctx()

    await bot.on_command_error(ctx, RuntimeError("boom"))

    assert "⚠️" in ctx.sent[0]