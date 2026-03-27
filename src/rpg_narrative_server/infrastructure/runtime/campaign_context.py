from contextvars import ContextVar
from contextlib import contextmanager


_current_campaign: ContextVar[str | None] = ContextVar("current_campaign", default=None)


class CampaignContext:
    """
    Contexto de campanha isolado por coroutine.
    """

    # ---------------------------------------------------------
    # set
    # ---------------------------------------------------------

    def set_campaign(self, campaign_id: str):

        return _current_campaign.set(str(campaign_id))

    # ---------------------------------------------------------
    # get
    # ---------------------------------------------------------

    def get_campaign(self) -> str:

        campaign = _current_campaign.get()

        if campaign is None:
            raise RuntimeError("Campaign context not set")

        return campaign

    # ---------------------------------------------------------
    # reset
    # ---------------------------------------------------------

    def reset(self, token=None):

        if token:
            _current_campaign.reset(token)
        else:
            _current_campaign.set(None)

    # ---------------------------------------------------------
    # scope
    # ---------------------------------------------------------

    @contextmanager
    def scope(self, campaign_id: str):

        token = _current_campaign.set(str(campaign_id))

        try:
            yield campaign_id
        finally:
            _current_campaign.reset(token)
