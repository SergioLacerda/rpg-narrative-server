class ListCampaignsUseCase:
    def __init__(self, repo):
        self.repo = repo

    async def execute(self) -> list[str]:
        return await self.repo.list()
