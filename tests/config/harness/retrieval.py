# tests/config/harness/retrieval.py


class RetrievalHarness:

    def __init__(self, docs=None):
        from tests.config.fakes.fake_vector_index import FakeVectorIndex

        self.vector_index = FakeVectorIndex()
        self.vector_index.docs = docs or ["doc1", "doc2", "doc3"]

    def build(self):

        from rpg_narrative_server.application.services.retrieval_pipeline import (
            RetrievalService,
        )

        self.selector = type("Selector", (), {"select": lambda _, docs: docs[:2]})()

        self.context_window = type(
            "CW",
            (),
            {
                "get_policy": lambda _, q: {"limit": 1},
                "apply": lambda _, docs, policy: docs[:1],
            },
        )()

        return RetrievalService(
            vector_index=self.vector_index,
            planner=None,
            context_window=self.context_window,
            selector=self.selector,
        )

    async def run(self, query="test"):
        service = self.build()
        return await service.search(query)
