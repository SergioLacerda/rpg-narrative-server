import pytest

from rpg_narrative_server.infrastructure.storage.adapters.metadata_store import MetadataStoreAdapter
from tests.config.fakes.storage.kv import DummyKV


@pytest.fixture
def store():
    return MetadataStoreAdapter(DummyKV())


def test_set_and_get_metadata(store):
    store.set("doc1", {"x": 1})

    assert store.get("doc1")["x"] == 1