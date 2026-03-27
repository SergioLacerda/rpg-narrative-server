import pytest
import uuid

from tests.config.fakes.narrative import DummyMemory, DummyMemoryRepo

from rpg_narrative_server.application.services.narrative_memory_service import (
    NarrativeMemoryService,
)


@pytest.fixture
def repo():
    return DummyMemoryRepo()


@pytest.fixture
def service(repo):
    return NarrativeMemoryService(repo)


def test_load_returns_memory(service, repo):
    assert service.load() is repo.memory


def test_now_returns_float(service):
    assert isinstance(service.now(), float)


def test_generate_event_id_is_valid_uuid(service):
    event_id = service.generate_event_id()

    assert str(uuid.UUID(event_id)) == event_id


def test_get_last_event_id_empty(service):
    assert service.get_last_event_id() is None


def test_get_last_event_id_returns_last():
    memory = DummyMemory(history=["open door"])
    memory.events = [{"id": "1"}, {"id": "2"}]

    service = NarrativeMemoryService(DummyMemoryRepo(memory))

    assert service.get_last_event_id() == "2"


def test_add_event_creates_and_saves(service, repo):
    event = service.add_event("dragon appears")

    assert repo.memory.events[0] == event
    assert repo.saved_memory is repo.memory


def test_update_summary_updates_and_saves(service, repo):
    service.update_summary("new summary")

    assert repo.memory.summary == "new summary"
    assert repo.saved_memory is repo.memory


def test_extract_tokens_basic(service):
    assert service.extract_tokens("The Dragon is BIG") == ["the", "dragon", "big"]


def test_extract_tokens_removes_short_words(service):
    assert service.extract_tokens("a an the big dragon") == ["the", "big", "dragon"]


def test_add_event_deterministic(repo):
    service = NarrativeMemoryService(repo)

    service.now = lambda: 123.0
    service.generate_event_id = lambda: "fixed-id"

    event = service.add_event("test")

    assert event == {
        "id": "fixed-id",
        "text": "test",
        "timestamp": 123.0,
    }
