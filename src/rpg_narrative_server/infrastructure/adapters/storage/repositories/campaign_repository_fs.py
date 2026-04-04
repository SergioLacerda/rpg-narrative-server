import shutil

from rpg_narrative_server.application.ports.campaign_repository import (
    CampaignRepositoryPort,
)
from rpg_narrative_server.config.paths import (
    BASE_CAMPAIGNS_DIR,
    get_campaign_path,
)


class FileSystemCampaignRepository(CampaignRepositoryPort):
    # ----------------------------------------
    # EVENTS (já existente - stub simples)
    # ----------------------------------------

    async def get_events(self, campaign_id: str) -> list:
        path = get_campaign_path(campaign_id) / "events.json"

        if not path.exists():
            return []

        import json

        return json.loads(path.read_text())

    async def save_events(self, campaign_id: str, events: list):
        path = get_campaign_path(campaign_id)
        path.mkdir(parents=True, exist_ok=True)

        import json

        (path / "events.json").write_text(json.dumps(events, indent=2))

    # ----------------------------------------
    # CAMPAIGN MANAGEMENT
    # ----------------------------------------

    async def create(self, campaign_id: str) -> None:
        path = get_campaign_path(campaign_id)

        if path.exists():
            return

        path.mkdir(parents=True, exist_ok=True)

    async def list(self) -> list[str]:
        if not BASE_CAMPAIGNS_DIR.exists():
            return []

        return [p.name for p in BASE_CAMPAIGNS_DIR.iterdir() if p.is_dir()]

    async def delete(self, campaign_id: str) -> None:
        path = get_campaign_path(campaign_id)

        if not path.exists():
            return

        shutil.rmtree(path)

    async def exists(self, campaign_id: str) -> bool:
        return get_campaign_path(campaign_id).exists()
