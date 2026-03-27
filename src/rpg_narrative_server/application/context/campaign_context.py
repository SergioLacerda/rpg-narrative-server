from pathlib import Path
from rpg_narrative_server.config.paths import get_campaign_path


class CampaignContext:

    def __init__(self, campaign_id: str):
        self.campaign_id = campaign_id
        self.base_path: Path = get_campaign_path(campaign_id)

    def __repr__(self):
        return f"<CampaignContext {self.campaign_id}>"