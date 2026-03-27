from pathlib import Path

from rpg_narrative_server.infrastructure.storage.kv.json_kv_store import JSONKeyValueStore


def test_set_and_get(tmp_path):

    path = tmp_path / "kv.json"

    store = JSONKeyValueStore(path)

    store.set("a", 1)

    assert store.get("a") == 1


def test_get_missing(tmp_path):

    path = tmp_path / "kv.json"

    store = JSONKeyValueStore(path)

    assert store.get("missing") is None


def test_clear(tmp_path):

    path = tmp_path / "kv.json"

    store = JSONKeyValueStore(path)

    store.set("a", 1)
    store.clear()

    assert store.get("a") is None