import pytest

from rpg_narrative_server.application.services.context_service import ContextService
from tests.config.fakes.retrieval import DummyRetrieval

@pytest.mark.asyncio
async def test_search_returns_texts():
    retrieval = DummyRetrieval([
        {"text": "doc1"},
        {"text": "doc2"},
    ])

    service = ContextService(retrieval)

    result = await service.search("dragon")

    assert result == ["doc1", "doc2"]


@pytest.mark.asyncio
async def test_search_passes_query_and_k():
    retrieval = DummyRetrieval([])

    service = ContextService(retrieval)

    await service.search("dragon", k=10)

    assert retrieval.called_with == ("dragon", 10)


@pytest.mark.asyncio
async def test_search_filters_none_docs():
    retrieval = DummyRetrieval([
        {"text": "doc1"},
        None,
        {"text": "doc2"},
    ])

    service = ContextService(retrieval)

    result = await service.search("q")

    assert result == ["doc1", "doc2"]


@pytest.mark.asyncio
async def test_search_preserves_order():
    retrieval = DummyRetrieval([
        {"text": "a"},
        {"text": "b"},
        {"text": "c"},
    ])

    service = ContextService(retrieval)

    result = await service.search("q")

    assert result == ["a", "b", "c"]


@pytest.mark.asyncio
async def test_search_missing_text_key_raises():
    retrieval = DummyRetrieval([
        {"text": "ok"},
        {"no_text": "fail"},
    ])

    service = ContextService(retrieval)

    with pytest.raises(KeyError):
        await service.search("q")