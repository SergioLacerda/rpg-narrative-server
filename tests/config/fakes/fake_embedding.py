class FakeEmbeddingProvider:

    async def embed(self, text):
        return [0.1] * 32

    async def embed_batch(self, texts):
        return [[0.1] * 32 for _ in texts]