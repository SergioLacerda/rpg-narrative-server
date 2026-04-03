class DeleteCampaignUseCase:
    def __init__(self, repo, runtime_manager):
        self.repo = repo
        self.runtime = runtime_manager

    async def execute(self, campaign_id: str):
        if not await self.repo.exists(campaign_id):
            return False

        await self.repo.delete(campaign_id)

        self.runtime.delete_campaign_runtime(campaign_id)

        return True
