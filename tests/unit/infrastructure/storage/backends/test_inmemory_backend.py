from rpg_narrative_server.infrastructure.adapters.storage.backends.inmemory_backend import (
    InMemoryStorageBackend,
    InMemoryVectorStore,
)


def test_inmemory_backend_builds():
    backend = InMemoryStorageBackend()

    vector = backend.build_vector_store()
    doc = backend.build_document_store()

    vector.add("a", [1, 0])

    assert vector.get("a") == [1, 0]

    doc.set("a", {"x": 1})

    assert doc.get("a")["x"] == 1


def test_vector_store_basic():
    store = InMemoryVectorStore()

    store.add("a", [1, 0])
    store.add("b", [0, 1])

    assert store.get("a") == [1, 0]
    assert set(store.keys()) == {"a", "b"}


def test_vector_store_get_missing():
    store = InMemoryVectorStore()

    assert store.get("missing") is None


def test_vector_store_search():
    store = InMemoryVectorStore()

    store.add("a", [1, 0])
    store.add("b", [0, 1])

    result = store.search([1, 0], k=1)

    assert result == ["a"]


def test_vector_store_clear():
    store = InMemoryVectorStore()

    store.add("a", [1, 0])
    store.clear()

    assert store.keys() == []
