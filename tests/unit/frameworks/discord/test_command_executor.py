import pytest

from tests.config.helpers.discord_factory import make_ctx, DummySettings

from rpg_narrative_server.frameworks.discord.command_base import CommandExecutor


@pytest.mark.asyncio
async def test_executor_success():
    ctx = make_ctx()

    executor = CommandExecutor(settings=DummySettings())

    async def handler():
        return "ok"

    result = await executor.run(ctx, handler)

    assert result == "ok"


@pytest.mark.asyncio
async def test_executor_exception():
    ctx = make_ctx()
    executor = CommandExecutor(settings=DummySettings(), debug=False)

    async def handler():
        raise ValueError("boom")

    await executor.run(ctx, handler)

    assert ctx.sent_messages[0] == "⚠️ Algo deu errado"
