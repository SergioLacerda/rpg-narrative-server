from dataclasses import dataclass
from typing import Any, Protocol

from rpg_narrative_server.frameworks.discord.dependencies import IntentClassifierProtocol


class CampaignStateProtocol(Protocol):
    def get(self, key): ...
    def set(self, key, value): ...
    def clear(self, key): ...


@dataclass
class DiscordServicesDTO:
    campaign_state: CampaignStateProtocol
    intent_classifier: IntentClassifierProtocol
    responder_factory: Any = None
