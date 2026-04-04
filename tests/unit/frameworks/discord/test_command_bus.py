import pytest

from rpg_narrative_server.application.commands.command_bus import CommandBus


class DummyCommand:
    def __init__(self, name="cmd", result="ok"):
        self.name = name
        self._result = result

    async def execute(self, ctx, **kwargs):
        return self._result


class DummyRegistry:
    def __init__(self, commands):
        self.commands = commands

    def get(self, name):
        return self.commands.get(name)

    def all(self):
        return self.commands


class DummyExecutor:
    async def run(self, ctx, handler):
        return await handler()


class DummyCtx:
    def __init__(self, with_send=True):
        self.sent: list[str] = []
        if with_send:

            async def send(msg):
                self.sent.append(msg)

            self.send = send


@pytest.mark.asyncio
async def test_dispatch_with_command_name():
    cmd = DummyCommand("test")

    bus = CommandBus(
        registry=DummyRegistry({"test": cmd}),
        executor=DummyExecutor(),
    )

    result = await bus.dispatch(DummyCtx(), command_name="test")

    assert result == "ok"


def test_command_not_found():
    bus = CommandBus(
        registry=DummyRegistry({}),
        executor=DummyExecutor(),
    )

    with pytest.raises(ValueError):
        bus._resolve_command("x")


def test_no_commands_registered():
    bus = CommandBus(
        registry=DummyRegistry({}),
        executor=DummyExecutor(),
    )

    with pytest.raises(ValueError):
        bus._resolve_command(None)


def test_multiple_commands_without_name():
    bus = CommandBus(
        registry=DummyRegistry(
            {
                "a": DummyCommand("a"),
                "b": DummyCommand("b"),
            }
        ),
        executor=DummyExecutor(),
    )

    with pytest.raises(ValueError):
        bus._resolve_command(None)


@pytest.mark.asyncio
async def test_single_command_without_name():
    cmd = DummyCommand("only")

    bus = CommandBus(
        registry=DummyRegistry({"only": cmd}),
        executor=DummyExecutor(),
    )

    result = await bus.dispatch(DummyCtx())

    assert result == "ok"


@pytest.mark.asyncio
async def test_result_empty_fallback():
    cmd = DummyCommand(result=None)

    ctx = DummyCtx()

    bus = CommandBus(
        registry=DummyRegistry({"cmd": cmd}),
        executor=DummyExecutor(),
    )

    result = await bus.dispatch(ctx, command_name="cmd")

    assert "Nenhuma resposta" in result
    assert ctx.sent


@pytest.mark.asyncio
async def test_ctx_without_send():
    cmd = DummyCommand()

    ctx = DummyCtx(with_send=False)

    bus = CommandBus(
        registry=DummyRegistry({"cmd": cmd}),
        executor=DummyExecutor(),
    )

    result = await bus.dispatch(ctx, command_name="cmd")

    assert result == "ok"


@pytest.mark.asyncio
async def test_ctx_send_called():
    cmd = DummyCommand("cmd", result="hello")

    ctx = DummyCtx()

    bus = CommandBus(
        registry=DummyRegistry({"cmd": cmd}),
        executor=DummyExecutor(),
    )

    await bus.dispatch(ctx, command_name="cmd")

    assert ctx.sent == ["hello"]
