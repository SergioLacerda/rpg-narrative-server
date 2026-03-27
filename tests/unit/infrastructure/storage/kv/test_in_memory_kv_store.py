from rpg_narrative_server.infrastructure.storage.kv.in_memory_kv_store import InMemoryKVStore


def test_set_and_get():

    store = InMemoryKVStore()

    store.set("a", 1)

    assert store.get("a") == 1


def test_get_missing():

    store = InMemoryKVStore()

    assert store.get("missing") is None


def test_clear():

    store = InMemoryKVStore()

    store.set("a", 1)
    store.clear()

    assert store.get("a") is None