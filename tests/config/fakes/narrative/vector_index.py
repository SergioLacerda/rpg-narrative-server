class DummyVectorIndex:
    async def search_async(self, *args, **kwargs):
        return []
