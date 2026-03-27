from typing import Protocol


class CampaignRepositoryPort(Protocol):

    async def get_events(self, campaign_id: str) -> list: ...
    async def save_events(self, campaign_id: str, events: list): ...
