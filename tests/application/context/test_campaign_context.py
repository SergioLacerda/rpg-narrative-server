from pathlib import Path

from rpg_narrative_server.application.context.campaign_context import CampaignContext

# ---------------------------------------------------------
# TESTES
# ---------------------------------------------------------


def test_initialization_sets_campaign_id(monkeypatch):
    monkeypatch.setattr(
        "rpg_narrative_server.application.context.campaign_context.get_campaign_path",
        lambda cid: Path(f"/fake/{cid}"),
    )

    ctx = CampaignContext("camp1")

    assert ctx.campaign_id == "camp1"


def test_base_path_uses_get_campaign_path(monkeypatch):
    called = {}

    def fake_get_path(cid):
        called["cid"] = cid
        return Path("/fake/path")

    monkeypatch.setattr(
        "rpg_narrative_server.application.context.campaign_context.get_campaign_path",
        fake_get_path,
    )

    ctx = CampaignContext("camp1")

    assert called["cid"] == "camp1"
    assert ctx.base_path == Path("/fake/path")


def test_repr():
    ctx = CampaignContext("camp1")

    assert repr(ctx) == "<CampaignContext camp1>"
