import pytest
from pathlib import Path

from rpg_narrative_server.infrastructure.storage.repositories.json_campaign_repository import JSONCampaignRepository


@pytest.mark.asyncio
async def test_get_events_empty(tmp_path):

    repo = JSONCampaignRepository(tmp_path)

    result = await repo.get_events("test")

    assert result == []


@pytest.mark.asyncio
async def test_save_and_get_events(tmp_path):

    repo = JSONCampaignRepository(tmp_path)

    await repo.save_events("test", [{"a": 1}])

    result = await repo.get_events("test")

    assert result[0]["a"] == 1


@pytest.mark.asyncio
async def test_invalid_json(tmp_path):

    repo = JSONCampaignRepository(tmp_path)

    path = tmp_path / "campaigns" / "test" / "events.json"
    path.parent.mkdir(parents=True)
    path.write_text("invalid")

    result = await repo.get_events("test")

    assert result == []