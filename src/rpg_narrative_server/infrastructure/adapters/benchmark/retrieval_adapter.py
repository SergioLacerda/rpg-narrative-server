class RetrievalAdapter:
    def __init__(self, engine):
        self.engine = engine

    async def search(self, query: str):
        return await self.engine.search(query)
