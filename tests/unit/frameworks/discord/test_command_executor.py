import pytest

from rpg_narrative_server.frameworks.discord.executor import CommandExecutor
from tests.config.factories.context import make_context
from tests.config.helpers.discord_factory import DummySettings


@pytest.mark.asyncio
async def test_executor_success():
    ctx = make_context(guild_id=None, user_id="999")

    executor = CommandExecutor(settings=DummySettings())

    async def handler():
        return "ok"

    result = await executor.run(ctx, handler)

    assert result == "ok"


@pytest.mark.asyncio
async def test_executor_exception():
    ctx = make_context(guild_id=None, user_id="999")
    executor = CommandExecutor(settings=DummySettings(), debug=False)

    async def handler():
        raise ValueError("boom")

    await executor.run(ctx, handler)

    assert ctx.sent_messages
    assert ctx.sent_messages[0] == "⚠️ Algo deu errado."
