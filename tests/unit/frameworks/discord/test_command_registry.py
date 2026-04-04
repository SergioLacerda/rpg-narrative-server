import pytest

from rpg_narrative_server.application.commands.base_command import BaseCommand
from rpg_narrative_server.application.commands.command_registry import (
    CommandRegistry,
)
from rpg_narrative_server.application.commands.gm_command import GMCommand


class DummyCommand(BaseCommand):
    name = "dummy"

    async def execute(self, ctx, **kwargs):
        return "ok"


class DummyCtx:
    def __init__(self):
        self.channel = type("C", (), {"id": "ch1"})()
        self.author = type("A", (), {"id": "u1"})()


class DummyState:
    def __init__(self, value=None):
        self.value = value

    def get(self, key):
        return self.value


class DummyUsecase:
    def __init__(self, result):
        self.result = result
        self.called = False

    async def execute(self, **kwargs):
        self.called = True
        return self.result


def test_register_and_get():
    registry = CommandRegistry()

    cmd = DummyCommand()

    registry.register("test", cmd)

    assert registry.get("test") is cmd


def test_get_not_found():
    registry = CommandRegistry()

    with pytest.raises(KeyError):
        registry.get("missing")


def test_all_returns_commands():
    registry = CommandRegistry()

    cmd1 = DummyCommand()
    cmd2 = DummyCommand()

    registry.register("a", cmd1)
    registry.register("b", cmd2)

    result = registry.all()

    assert result == {"a": cmd1, "b": cmd2}


def test_register_overwrites():
    registry = CommandRegistry()

    cmd1 = DummyCommand()
    cmd2 = DummyCommand()

    registry.register("x", cmd1)
    registry.register("x", cmd2)

    assert registry.get("x") is cmd2


@pytest.mark.asyncio
async def test_invalid_action():
    cmd = GMCommand(DummyUsecase("ok"), DummyState("c1"))

    result = await cmd.execute(DummyCtx(), action="")

    assert "Ação inválida" in result


@pytest.mark.asyncio
async def test_no_campaign():
    cmd = GMCommand(DummyUsecase("ok"), DummyState(None))

    result = await cmd.execute(DummyCtx(), action="attack")

    assert "Nenhuma campanha ativa" in result


@pytest.mark.asyncio
async def test_result_none():
    cmd = GMCommand(DummyUsecase(None), DummyState("c1"))

    result = await cmd.execute(DummyCtx(), action="attack")

    assert "Nenhuma resposta gerada" in result


@pytest.mark.asyncio
async def test_result_with_text_attr():
    class Resp:
        def __init__(self):
            self.text = "narrative text"

    cmd = GMCommand(DummyUsecase(Resp()), DummyState("c1"))

    result = await cmd.execute(DummyCtx(), action="look")

    assert result == "narrative text"


@pytest.mark.asyncio
async def test_result_plain_string():
    cmd = GMCommand(DummyUsecase("ok"), DummyState("c1"))

    result = await cmd.execute(DummyCtx(), action="look")

    assert result == "ok"


@pytest.mark.asyncio
async def test_usecase_called_with_correct_args():
    usecase = DummyUsecase("ok")
    cmd = GMCommand(usecase, DummyState("camp1"))

    await cmd.execute(DummyCtx(), action="attack")

    assert usecase.called is True
