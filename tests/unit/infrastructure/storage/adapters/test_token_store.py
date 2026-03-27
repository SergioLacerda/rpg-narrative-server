import pytest

from rpg_narrative_server.infrastructure.storage.adapters.token_store import (
    TokenStoreAdapter,
)
from tests.config.fakes.storage.kv import DummyKV


@pytest.fixture
def store():
    return TokenStoreAdapter(DummyKV())


def test_token_store_set_and_get(store):
    store.set("doc1", {"x": 1})

    assert store.get("doc1")["x"] == 1
