class DummyVectorIndex:
    def __init__(self, docs=None):
        self.docs = docs or ["doc1", "doc2", "doc3"]
        self.called_with = None

    async def search(self, query, k=4):
        self.called_with = (query, k)
        return self.docs