import pytest

from rpg_narrative_server.application.commands.campaign_command import (
    CampaignCommand,
)
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


def make_command(state=None):
    state = state or DummyCampaignState()

    return CampaignCommand(
        campaign_state=state,
        create_campaign=DummyCreateCampaign(),
        list_campaigns=DummyListCampaigns(),
        delete_campaign=DummyDeleteCampaign(),
    )


# ---------------------------------------------------------
# START
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_campaign_start_success():
    # ARRANGE
    ctx = make_context()
    command = make_command()

    # ACT
    result = await command.execute(ctx, action="start", name="aventura")

    # ASSERT
    assert "🎲" in result
    assert "aventura" in result


@pytest.mark.asyncio
async def test_campaign_start_without_name():
    # ARRANGE
    ctx = make_context()
    command = make_command()

    # ACT
    result = await command.execute(ctx, action="start", name=None)

    # ASSERT
    assert "⚠️" in result


# ---------------------------------------------------------
# STOP
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_campaign_stop_success():
    # ARRANGE
    ctx = make_context()
    command = make_command()

    await command.execute(ctx, action="start", name="aventura")

    # ACT
    result = await command.execute(ctx, action="stop")

    # ASSERT
    assert "🛑" in result


@pytest.mark.asyncio
async def test_campaign_stop_without_active():
    # ARRANGE
    ctx = make_context()
    command = make_command()

    # ACT
    result = await command.execute(ctx, action="stop")

    # ASSERT
    assert "⚠️" in result


# ---------------------------------------------------------
# STATUS
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_campaign_status_with_active():
    # ARRANGE
    ctx = make_context()
    command = make_command()

    await command.execute(ctx, action="start", name="aventura")

    # ACT
    result = await command.execute(ctx)

    # ASSERT
    assert "🎲" in result
    assert "aventura" in result


@pytest.mark.asyncio
async def test_campaign_status_without_active():
    # ARRANGE
    ctx = make_context()
    command = make_command()

    # ACT
    result = await command.execute(ctx)

    # ASSERT
    assert "⚠️" in result


# ---------------------------------------------------------
# UNKNOWN ACTION
# ---------------------------------------------------------


@pytest.mark.asyncio
async def test_campaign_unknown_action():
    ctx = make_context()
    command = make_command()

    result = await command.execute(ctx, action="invalid")

    assert "⚠️" in result
