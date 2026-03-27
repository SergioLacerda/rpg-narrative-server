import pytest

from rpg_narrative_server.application.services.retrieval_pipeline import RetrievalService
from tests.config.fakes.retrieval import (
    DummyVectorIndex,
    DummySelector,
    DummyContextWindow,
)


@pytest.mark.asyncio
async def test_retrieval_pipeline_flow():
    service = RetrievalService(
        vector_index=DummyVectorIndex(["doc1", "doc2", "doc3"]),
        planner=None,
        context_window=DummyContextWindow(),
        selector=DummySelector(),
    )

    result = await service.search("dragon")

    assert result == ["doc1"]


@pytest.mark.asyncio
async def test_search_passes_k_correctly():
    vi = DummyVectorIndex([])

    service = RetrievalService(
        vector_index=vi,
        planner=None,
        context_window=DummyContextWindow(),
        selector=DummySelector(),
    )

    await service.search("test", k=10)

    assert vi.called_with == ("test", 10)