class DummyCampaignState:
    def __init__(self, campaign_id):
        self.campaign_id = campaign_id

    def get(self, _):
        return self.campaign_id