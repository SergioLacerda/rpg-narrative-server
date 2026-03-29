class DummySelector:
    def select(self, docs):
        return docs[:2]


class DummyContextWindow:
    def get_policy(self, query):
        return {"limit": 1}

    def apply(self, docs, policy):
        return docs[:1]


class RetrievalHarness:
    def __init__(self, docs=None):
        from tests.config.fakes.fake_vector_index import FakeVectorIndex

        self.vector_index = FakeVectorIndex()
        self.vector_index.docs = docs or ["doc1", "doc2", "doc3"]

        self.selector = DummySelector()
        self.context_window = DummyContextWindow()

    def build(self):
        from rpg_narrative_server.application.services.retrieval_pipeline import (
            RetrievalService,
        )

        return RetrievalService(
            vector_index=self.vector_index,
            planner=None,
            context_window=self.context_window,
            selector=self.selector,
        )

    async def run(self, query="test"):
        service = self.build()
        result = await service.search(query)

        return result
