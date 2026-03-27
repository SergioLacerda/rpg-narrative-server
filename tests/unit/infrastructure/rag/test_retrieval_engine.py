import pytest
import asyncio

from rpg_narrative_server.infrastructure.rag.retrieval_engine import RetrievalEngine
from tests.config.fakes.retrieval import (
    DummyIndex,
    DummyEmbeddingCache,
    DummySemanticCache,
)


# --------------------------------------------------
# FIXTURE
# --------------------------------------------------


@pytest.fixture
def engine():
    return RetrievalEngine(
        vector_index=DummyIndex(),
        embedding_cache=DummyEmbeddingCache(),
        semantic_cache=DummySemanticCache(),
    )


# --------------------------------------------------
# BASIC SEARCH
# --------------------------------------------------


@pytest.mark.asyncio
async def test_search_basic(engine):
    result = await engine.search("hello", k=2)

    assert result == ["result:hello:2"]


# --------------------------------------------------
# SEMANTIC CACHE
# --------------------------------------------------


@pytest.mark.asyncio
async def test_search_uses_semantic_cache(engine):
    r1 = await engine.search("hello")
    r2 = await engine.search("hello")

    assert r1 == r2
    assert len(engine.default_index.calls) == 1


# --------------------------------------------------
# INFLIGHT DEDUPLICATION
# --------------------------------------------------


@pytest.mark.asyncio
async def test_inflight_deduplication(engine):
    async def call():
        return await engine.search("same")

    results = await asyncio.gather(call(), call(), call())

    assert all(r == results[0] for r in results)
    assert len(engine.default_index.calls) == 1


# --------------------------------------------------
# INDEX FACTORY
# --------------------------------------------------


@pytest.mark.asyncio
async def test_index_factory_usage():
    indexes = {}

    def factory(campaign_id):
        idx = DummyIndex()
        indexes[campaign_id] = idx
        return idx

    engine = RetrievalEngine(
        vector_index=DummyIndex(),
        embedding_cache=DummyEmbeddingCache(),
        semantic_cache=DummySemanticCache(),
        vector_index_factory=factory,
    )

    await engine.search("q1", campaign_id="A")
    await engine.search("q2", campaign_id="A")

    assert "A" in indexes
    assert len(indexes["A"].calls) == 2


# --------------------------------------------------
# DEFAULT INDEX
# --------------------------------------------------


@pytest.mark.asyncio
async def test_default_index_when_no_factory(engine):
    await engine.search("hello")

    assert len(engine.default_index.calls) == 1


# --------------------------------------------------
# MULTIPLE CAMPAIGNS
# --------------------------------------------------


@pytest.mark.asyncio
async def test_multiple_campaign_indexes():
    calls = {}

    def factory(cid):
        idx = DummyIndex()
        calls[cid] = idx
        return idx

    engine = RetrievalEngine(
        vector_index=DummyIndex(),
        embedding_cache=DummyEmbeddingCache(),
        semantic_cache=DummySemanticCache(),
        vector_index_factory=factory,
    )

    await engine.search("q1", campaign_id="A")
    await engine.search("q1", campaign_id="B")

    assert calls["A"] is not calls["B"]


# --------------------------------------------------
# CACHE HIT
# --------------------------------------------------


@pytest.mark.asyncio
async def test_semantic_cache_skips_search(engine):
    engine.semantic_cache.set("q", [1, 2], ["cached"])

    result = await engine.search("q")

    assert result == ["cached"]
    assert len(engine.default_index.calls) == 0
