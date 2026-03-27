class DummyRetrieval:
    def __init__(self, result=None):
        self.result = result or []
        self.called_with = None

    async def search(self, query, k=4):
        self.called_with = (query, k)
        return self.result
