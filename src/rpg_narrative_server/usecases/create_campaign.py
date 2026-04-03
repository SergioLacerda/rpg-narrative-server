class CreateCampaignUseCase:
    def __init__(self, repo):
        self.repo = repo

    async def execute(self, campaign_id: str):
        if await self.repo.exists(campaign_id):
            return False

        await self.repo.create(campaign_id)
        return True
