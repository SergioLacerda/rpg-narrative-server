from rpg_narrative_server.infrastructure.storage.vector.chroma_vector_store import (
    ChromaVectorStore,
)


# ---------------------------------------------------------
# DUMMY
# ---------------------------------------------------------


class DummyCollection:
    def __init__(self):
        self.data = {}
        self.last_query = None

    def add(self, ids, embeddings):
        self.data[ids[0]] = embeddings[0]

    def get(self):
        return {"ids": list(self.data.keys())}

    def query(self, query_embeddings, n_results):
        self.last_query = (query_embeddings, n_results)

        if not self.data:
            return {"ids": [[]]}

        return {"ids": [[list(self.data.keys())[0]]]}


# ---------------------------------------------------------
# TESTES
# ---------------------------------------------------------


def test_add_and_keys():
    store = ChromaVectorStore(DummyCollection())

    store.add("doc1", [1, 0])

    assert "doc1" in store.keys()


def test_search_returns_expected_key():
    collection = DummyCollection()
    store = ChromaVectorStore(collection)

    store.add("doc1", [1, 0])

    result = store.search([1, 0], k=1)

    assert result == ["doc1"]


def test_search_calls_query_correctly():
    collection = DummyCollection()
    store = ChromaVectorStore(collection)

    store.add("doc1", [1, 0])

    store.search([1, 0], k=2)

    assert collection.last_query == ([[1, 0]], 2)
