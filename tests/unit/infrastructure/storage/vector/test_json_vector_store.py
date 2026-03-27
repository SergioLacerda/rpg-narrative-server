from pathlib import Path
import pytest

from rpg_narrative_server.infrastructure.storage.vector.json_vector_store import JSONVectorStore


# ---------------------------------------------------------
# FIXTURE
# ---------------------------------------------------------

@pytest.fixture
def store(tmp_path):
    return JSONVectorStore(tmp_path / "vec.json")


# ---------------------------------------------------------
# TESTES
# ---------------------------------------------------------

def test_add_and_get(store):
    store.add("doc1", [1.0, 0.0])

    assert store.get("doc1") == [1.0, 0.0]


def test_keys(store):
    store.add("a", [1, 0])
    store.add("b", [0, 1])

    assert set(store.keys()) == {"a", "b"}


def test_clear(store):
    store.add("a", [1, 0])

    store.clear()

    assert store.keys() == []


def test_search_basic(store):
    store.add("a", [1, 0])
    store.add("b", [0, 1])

    assert store.search([1, 0], k=1) == ["a"]


def test_search_empty(store):
    assert store.search([1, 0], k=1) == []


def test_persistence(tmp_path):
    path = tmp_path / "vec.json"

    store = JSONVectorStore(path)
    store.add("doc1", [1, 0])

    # novo instance
    new_store = JSONVectorStore(path)

    assert new_store.get("doc1") == [1, 0]