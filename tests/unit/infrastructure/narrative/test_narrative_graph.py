from rpg_narrative_server.infrastructure.narrative.narrative_graph import (
    NarrativeGraph,
)

# ==========================================================
# HELPERS
# ==========================================================


class FakeExtractor:
    def __init__(self, entities):
        self.entities = entities

    def extract(self, text):
        return self.entities


def test_init_loads_graph(monkeypatch):
    monkeypatch.setattr(
        "rpg_narrative_server.infrastructure.narrative.narrative_graph.load_json",
        lambda path, default: {"A": {"links": ["B"]}},
    )

    g = NarrativeGraph()

    assert "A" in g.graph


def test_update_from_event_creates_links(monkeypatch):
    saved = {}

    monkeypatch.setattr(
        "rpg_narrative_server.infrastructure.narrative.narrative_graph.load_json",
        lambda *a: {},
    )

    monkeypatch.setattr(
        "rpg_narrative_server.infrastructure.narrative.narrative_graph.save_json",
        lambda path, data: saved.update(data),
    )

    monkeypatch.setattr(
        "rpg_narrative_server.infrastructure.narrative.narrative_graph.entity_extractor",
        FakeExtractor(["A", "B"]),
    )

    g = NarrativeGraph()

    g.update_from_event("anything")

    assert "A" in g.graph
    assert "B" in g.graph

    assert "B" in g.graph["A"]["links"]
    assert "A" in g.graph["B"]["links"]


def test_no_duplicate_links(monkeypatch):
    monkeypatch.setattr(
        "rpg_narrative_server.infrastructure.narrative.narrative_graph.load_json",
        lambda *a: {},
    )

    monkeypatch.setattr(
        "rpg_narrative_server.infrastructure.narrative.narrative_graph.save_json",
        lambda *a: None,
    )

    monkeypatch.setattr(
        "rpg_narrative_server.infrastructure.narrative.narrative_graph.entity_extractor",
        FakeExtractor(["A", "B"]),
    )

    g = NarrativeGraph()

    g.update_from_event("x")
    g.update_from_event("x")

    assert g.graph["A"]["links"].count("B") == 1


def test_related_entities(monkeypatch):
    monkeypatch.setattr(
        "rpg_narrative_server.infrastructure.narrative.narrative_graph.load_json",
        lambda *a: {"A": {"links": ["B", "C"]}},
    )

    monkeypatch.setattr(
        "rpg_narrative_server.infrastructure.narrative.narrative_graph.entity_extractor",
        FakeExtractor(["A"]),
    )

    g = NarrativeGraph()

    result = g.related("query")

    assert result == {"B", "C"}


def test_related_no_entities(monkeypatch):
    monkeypatch.setattr(
        "rpg_narrative_server.infrastructure.narrative.narrative_graph.load_json",
        lambda *a: {},
    )

    monkeypatch.setattr(
        "rpg_narrative_server.infrastructure.narrative.narrative_graph.entity_extractor",
        FakeExtractor(["X"]),
    )

    g = NarrativeGraph()

    result = g.related("query")

    assert result == set()
