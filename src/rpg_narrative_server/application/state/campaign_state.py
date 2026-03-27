class CampaignState:

    def __init__(self):
        self._active_campaign_by_channel = {}

    def get(self, channel_id: str) -> str | None:
        return self._active_campaign_by_channel.get(channel_id)

    def set(self, channel_id: str, campaign_id: str):
        self._active_campaign_by_channel[channel_id] = campaign_id