from rpg_narrative_server.application.ports.embedding_gateway import EmbeddingGateway


class DummyEmbedding(EmbeddingGateway):
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.called = False

    async def embed(self, text: str) -> list[float]:
        self.called = True
        if self.error:
            raise self.error
        return self.result
