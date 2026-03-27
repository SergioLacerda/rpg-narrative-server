import pytest

from rpg_narrative_server.infrastructure.storage.adapters.document_store import DocumentStoreAdapter
from tests.config.fakes.storage.kv import DummyKV


@pytest.fixture
def store():
    return DocumentStoreAdapter(DummyKV())


def test_set_and_get(store):
    store.set("doc1", {"a": 1})

    assert store.get("doc1")["a"] == 1


def test_set_invalid_doc_id(store):
    with pytest.raises(ValueError):
        store.set("", {"a": 1})


def test_set_invalid_document(store):
    with pytest.raises(TypeError):
        store.set("doc1", "invalid")


def test_get_empty_id(store):
    assert store.get("") is None


def test_clear():
    kv = DummyKV()
    store = DocumentStoreAdapter(kv)

    store.set("doc1", {"a": 1})
    store.clear()

    assert kv.data == {}