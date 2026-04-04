import pytest

from rpg_narrative_server.application.commands.session_command import (
    SessionCommand,
    build_session_command,
)


class DummyCtx:
    def __init__(self, channel_id="ch1"):
        self.channel = type("Channel", (), {"id": channel_id})()


class DummyState:
    def __init__(self, value=None):
        self.value = value
        self.cleared_keys = []

    def get(self, key):
        return self.value

    def clear(self, key):
        self.cleared_keys.append(key)


class DummyUsecase:
    def __init__(self, result):
        self.result = result
        self.called_with = None

    async def execute(self, **kwargs):
        self.called_with = kwargs
        return self.result


@pytest.mark.asyncio
async def test_no_campaign_active():
    state = DummyState(None)
    usecase = DummyUsecase("irrelevant")

    cmd = SessionCommand(usecase, state)

    result = await cmd.execute(DummyCtx())

    assert "Nenhuma campanha ativa" in result
    assert state.cleared_keys == []


@pytest.mark.asyncio
async def test_successful_session_end():
    state = DummyState("camp1")
    usecase = DummyUsecase("Resumo final")

    cmd = SessionCommand(usecase, state)

    ctx = DummyCtx()

    result = await cmd.execute(ctx)

    assert "Sessão encerrada" in result
    assert "Resumo final" in result

    assert state.cleared_keys == ["ch1"]

    assert usecase.called_with == {"campaign_id": "camp1"}


@pytest.mark.asyncio
async def test_result_none_returns_warning():
    state = DummyState("camp1")
    usecase = DummyUsecase(None)

    cmd = SessionCommand(usecase, state)

    ctx = DummyCtx()

    result = await cmd.execute(ctx)

    assert "Nenhum resumo gerado" in result

    assert state.cleared_keys == ["ch1"]


@pytest.mark.asyncio
async def test_usecase_called_with_correct_campaign():
    state = DummyState("campXYZ")
    usecase = DummyUsecase("ok")

    cmd = SessionCommand(usecase, state)

    result = await cmd.execute(DummyCtx())

    assert result is not None
    assert "Sessão encerrada" in result

    assert usecase.called_with is not None
    assert usecase.called_with["campaign_id"] == "campXYZ"


def test_build_session_command():
    class Deps:
        def __init__(self):
            self.end_session = DummyUsecase("ok")
            self.campaign_state = DummyState("camp1")

    deps = Deps()

    cmd = build_session_command(deps)

    assert isinstance(cmd, SessionCommand)
    assert cmd.end_session is deps.end_session
    assert cmd.campaign_state is deps.campaign_state
