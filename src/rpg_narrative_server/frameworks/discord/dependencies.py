from dataclasses import dataclass
from typing import Protocol

# =========================================================
# USE CASE PROTOCOLS
# =========================================================


class NarrativeUseCase(Protocol):
    async def execute(self, campaign_id: str, action: str, user_id: str): ...


class RollUseCase(Protocol):
    async def execute(self, expression: str): ...


class EndSessionUseCase(Protocol):
    async def execute(self, campaign_id: str): ...


# =========================================================
# SERVICES PROTOCOLS
# =========================================================


class CampaignStateProtocol(Protocol):
    def get(self, channel_id: str) -> str | None: ...
    def set(self, channel_id: str, campaign_id: str): ...
    def clear(self, channel_id: str): ...


class IntentClassifierProtocol(Protocol):
    async def classify(self, text: str): ...


# =========================================================
# DEPENDENCIES OBJECT
# =========================================================


class CreateCampaignUseCase(Protocol):
    async def execute(self, campaign_id: str) -> bool: ...


class ListCampaignsUseCase(Protocol):
    async def execute(self) -> list[str]: ...


class DeleteCampaignUseCase(Protocol):
    async def execute(self, campaign_id: str) -> bool: ...


@dataclass
class CommandDependencies:
    narrative: NarrativeUseCase
    roll_dice: RollUseCase
    end_session: EndSessionUseCase
    intent_classifier: IntentClassifierProtocol
    campaign_state: CampaignStateProtocol
    create_campaign: CreateCampaignUseCase
    list_campaigns: ListCampaignsUseCase
    delete_campaign: DeleteCampaignUseCase
