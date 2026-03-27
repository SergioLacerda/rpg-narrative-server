import pytest

from rpg_narrative_server.application.services.narrative_graph_service import NarrativeGraphService
from tests.config.fakes.narrative import (
    DummyGraph,
    DummyGraphRepo,
    DummyExtractor,
)


def test_update_from_text_with_entities():
    extractor = DummyExtractor({"dragon", "castle"})
    repo = DummyGraphRepo()

    service = NarrativeGraphService(repo, extractor)

    service.update_from_text("dragon in castle")

    assert extractor.called_with == "dragon in castle"
    assert repo.graph.updated_with == {"dragon", "castle"}
    assert repo.saved_graph is repo.graph


def test_update_from_text_without_entities():
    extractor = DummyExtractor(set())
    repo = DummyGraphRepo()

    service = NarrativeGraphService(repo, extractor)

    service.update_from_text("...")

    assert repo.graph.updated_with is None
    assert repo.saved_graph is None


def test_related_with_entities():
    extractor = DummyExtractor({"dragon"})
    repo = DummyGraphRepo()

    service = NarrativeGraphService(repo, extractor)

    result = service.related("dragon")

    assert repo.graph.related_called_with == {"dragon"}
    assert result == {"result_1", "result_2"}


def test_related_without_entities():
    extractor = DummyExtractor(set())
    repo = DummyGraphRepo()

    service = NarrativeGraphService(repo, extractor)

    assert service.related("...") == set()