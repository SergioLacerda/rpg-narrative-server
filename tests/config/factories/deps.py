from tests.config.fakes.state.campaign_state import DummyCampaignState
from tests.config.fakes.usecases import (
    DummyEndSession,
    DummyNarrative,
    DummyRoll,
)


def make_deps(**overrides):
    base = {
        "narrative": DummyNarrative(),
        "roll_dice": DummyRoll(),
        "end_session": DummyEndSession(),
        "campaign_state": DummyCampaignState("test_campaign"),
        "intent_classifier": None,
    }

    base.update(overrides)

    return type("Deps", (), base)()
