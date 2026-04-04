import pytest

from rpg_narrative_server.application.commands.campaign_command import CampaignCommand
from tests.config.factories.context import make_context
from tests.config.fakes.state.campaign_state import DummyCampaignState


class DummyCreateCampaign:
    async def execute(self, name: str):
        return True


class DummyListCampaigns:
    async def execute(self):
        return ["aventura"]


class DummyDeleteCampaign:
    async def execute(self, name: str):
        return True


class DummyState:
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

    def clear(self, key):
        self.data.pop(key, None)


class DummyCtx:
    def __init__(self, channel_id="c1"):
        self.channel = type("C", (), {"id": channel_id})()


class DummyUC:
    def __init__(self, result):
        self.result = result

    async def execute(self, *args):
        return self.result


def build_cmd(create=True, list_result=None, delete=True):
    return CampaignCommand(
        campaign_state=DummyState(),
        create_campaign=DummyUC(create),
        list_campaigns=DummyUC(list_result or []),
        delete_campaign=DummyUC(delete),
    )


def make_command(state=None):
    state = state or DummyCampaignState()

    return CampaignCommand(
        campaign_state=state,
        create_campaign=DummyCreateCampaign(),
        list_campaigns=DummyListCampaigns(),
        delete_campaign=DummyDeleteCampaign(),
    )


@pytest.mark.asyncio
async def test_campaign_start_success():
    ctx = make_context()
    command = make_command()

    result = await command.execute(ctx, action="start", name="aventura")

    assert "🎲" in result
    assert "aventura" in result


@pytest.mark.asyncio
async def test_campaign_start_without_name():
    ctx = make_context()
    command = make_command()

    result = await command.execute(ctx, action="start", name=None)

    assert "⚠️" in result


@pytest.mark.asyncio
async def test_campaign_stop_success():
    ctx = make_context()
    command = make_command()

    await command.execute(ctx, action="start", name="aventura")

    result = await command.execute(ctx, action="stop")

    assert "🛑" in result


@pytest.mark.asyncio
async def test_campaign_stop_without_active():
    ctx = make_context()
    command = make_command()

    result = await command.execute(ctx, action="stop")

    assert "⚠️" in result


@pytest.mark.asyncio
async def test_campaign_status_with_active():
    ctx = make_context()
    command = make_command()

    await command.execute(ctx, action="start", name="aventura")

    result = await command.execute(ctx)

    assert "🎲" in result
    assert "aventura" in result


@pytest.mark.asyncio
async def test_campaign_status_without_active():
    ctx = make_context()
    command = make_command()

    result = await command.execute(ctx)

    assert "⚠️" in result


@pytest.mark.asyncio
async def test_campaign_unknown_action():
    ctx = make_context()
    command = make_command()

    result = await command.execute(ctx, action="invalid")

    assert "⚠️" in result


@pytest.mark.asyncio
async def test_start_created():
    cmd = build_cmd(create=True)

    result = await cmd.execute(DummyCtx(), action="start", name="A")

    assert "criada e iniciada" in result


@pytest.mark.asyncio
async def test_start_existing():
    cmd = build_cmd(create=False)

    result = await cmd.execute(DummyCtx(), action="start", name="A")

    assert "carregada" in result


@pytest.mark.asyncio
async def test_start_without_name():
    cmd = build_cmd()

    result = await cmd.execute(DummyCtx(), action="start")

    assert "Informe o nome" in result


@pytest.mark.asyncio
async def test_switch():
    cmd = build_cmd()

    result = await cmd.execute(DummyCtx(), action="switch", name="B")

    assert "alterada" in result


@pytest.mark.asyncio
async def test_list_empty():
    cmd = build_cmd(list_result=[])

    result = await cmd.execute(DummyCtx(), action="list")

    assert "Nenhuma campanha" in result


@pytest.mark.asyncio
async def test_list_with_campaigns():
    cmd = build_cmd(list_result=["A", "B"])

    result = await cmd.execute(DummyCtx(), action="list")

    assert "A" in result
    assert "B" in result


@pytest.mark.asyncio
async def test_delete_success():
    cmd = build_cmd(delete=True)

    result = await cmd.execute(DummyCtx(), action="delete", name="A")

    assert "removida" in result


@pytest.mark.asyncio
async def test_delete_not_found():
    cmd = build_cmd(delete=False)

    result = await cmd.execute(DummyCtx(), action="delete", name="A")

    assert "não encontrada" in result


@pytest.mark.asyncio
async def test_stop_no_campaign():
    cmd = build_cmd()

    result = await cmd.execute(DummyCtx(), action="stop")

    assert "Nenhuma campanha ativa" in result


@pytest.mark.asyncio
async def test_stop_with_campaign():
    cmd = build_cmd()

    ctx = DummyCtx()
    cmd.campaign_state.set(ctx.channel.id, "A")

    result = await cmd.execute(ctx, action="stop")

    assert "encerrada" in result


@pytest.mark.asyncio
async def test_status_no_campaign():
    cmd = build_cmd()

    result = await cmd.execute(DummyCtx())

    assert "Nenhuma campanha ativa" in result


@pytest.mark.asyncio
async def test_status_with_campaign():
    cmd = build_cmd()

    ctx = DummyCtx()
    cmd.campaign_state.set(ctx.channel.id, "A")

    result = await cmd.execute(ctx)

    assert "Campanha atual" in result
