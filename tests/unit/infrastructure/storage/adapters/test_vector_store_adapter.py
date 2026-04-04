import pytest

from rpg_narrative_server.infrastructure.adapters.storage.adapters.vector_store import (
    VectorStoreAdapter,
)

# ---------------------------------------------------------
# DUMMY
# ---------------------------------------------------------


class DummyBackend:
    def __init__(self):
        self.data = {}
        self.last_search = None

    def add(self, k, v):
        self.data[k] = v

    def get(self, k):
        return self.data.get(k)

    def search(self, q, k):
        self.last_search = (q, k)
        return list(self.data.keys())[:k]

    def keys(self):
        return list(self.data.keys())


@pytest.fixture
def backend():
    return DummyBackend()


@pytest.fixture
def store(backend):
    return VectorStoreAdapter(backend)


def test_vector_adapter_basic(store):
    store.add("doc1", [1, 0])

    assert store.get("doc1") == [1, 0]
    assert store.keys() == ["doc1"]
    assert store.search([1, 0], 1) == ["doc1"]


def test_search_calls_backend(backend, store):
    store.add("doc1", [1, 0])

    store.search([1, 0], 2)

    assert backend.last_search == ([1, 0], 2)
