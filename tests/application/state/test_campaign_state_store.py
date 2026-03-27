from rpg_narrative_server.application.state.campaign_state_store import (
    CampaignStateStore,
)


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------


def make_store(tmp_path, content=None):
    path = tmp_path / "state.json"

    if content is not None:
        path.write_text(content)

    return CampaignStateStore(path), path


# ---------------------------------------------------------
# TESTES
# ---------------------------------------------------------


def test_load_valid_json(tmp_path):
    store, _ = make_store(tmp_path, '{"123": "campaign_a"}')

    assert store.get("123") == "campaign_a"


def test_load_invalid_json_returns_empty(tmp_path):
    store, _ = make_store(tmp_path, "INVALID JSON")

    assert store._data == {}


def test_save_writes_file(tmp_path):
    store, path = make_store(tmp_path)

    store._data = {"abc": "campaign_x"}
    store.save()

    assert '"abc": "campaign_x"' in path.read_text()


def test_get_returns_none_when_missing(tmp_path):
    store, _ = make_store(tmp_path)

    assert store.get("unknown") is None


def test_set_updates_and_persists(tmp_path):
    store, path = make_store(tmp_path)

    store.set("channel_1", "campaign_1")

    # memória
    assert store.get("channel_1") == "campaign_1"

    # persistência
    new_store = CampaignStateStore(path)
    assert new_store.get("channel_1") == "campaign_1"


def test_set_overwrites_existing_value(tmp_path):
    store, _ = make_store(tmp_path)

    store.set("channel_1", "campaign_1")
    store.set("channel_1", "campaign_2")

    assert store.get("channel_1") == "campaign_2"
