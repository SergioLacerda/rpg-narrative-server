from tests.config.fakes.state.campaign_state import DummyCampaignState
from tests.config.fakes.usecases import (
    DummyEndSession,
    DummyNarrative,
    DummyRoll,
)

# ---------------------------------------------------------
# NOVOS FAKES (campaign usecases)
# ---------------------------------------------------------


class DummyCreateCampaign:
    async def execute(self, name: str):
        return True


class DummyListCampaigns:
    async def execute(self):
        return ["test_campaign"]


class DummyDeleteCampaign:
    async def execute(self, name: str):
        return True


# ---------------------------------------------------------
# FACTORY
# ---------------------------------------------------------


def make_deps(**overrides):
    base = {
        "narrative": DummyNarrative(),
        "roll_dice": DummyRoll(),
        "end_session": DummyEndSession(),
        "campaign_state": DummyCampaignState("test_campaign"),
        "intent_classifier": None,
        "create_campaign": DummyCreateCampaign(),
        "list_campaigns": DummyListCampaigns(),
        "delete_campaign": DummyDeleteCampaign(),
    }

    base.update(overrides)

    return type("Deps", (), base)()
