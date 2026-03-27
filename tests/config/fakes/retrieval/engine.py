
class DummyIndex:
    def __init__(self):
        self.calls = []
    
    async def search(self, query, q_vec, k):
        self.calls.append((query, q_vec, k))
        return [f"result:{query}:{k}"]


class DummyEmbeddingCache:
    def __init__(self, vector=None):
        self.vector = vector or [1.0, 2.0, 3.0]

    async def get(self, query):
        return self.vector


class DummySemanticCache:
    def __init__(self):
        self.store = {}

    def get(self, query, vec):
        return self.store.get(query)

    def set(self, query, vec, value):
        self.store[query] = value