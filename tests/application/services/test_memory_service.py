from unittest.mock import AsyncMock, MagicMock

import pytest

from rpg_narrative_server.application.services.memory_service import MemoryService
from rpg_narrative_server.domain.narrative.narrative_memory import NarrativeMemory


class DummyRepo:
    def __init__(self, data=None):
        self.data = data or []
        self.saved = None

    async def get_events(self, campaign_id):
        return self.data

    async def save_events(self, campaign_id, events):
        self.saved = (campaign_id, events)


class DummySummarizer:
    def extract(self, events):
        return " ".join(e["text"] for e in events)

    def build_prompt(self, text):
        return f"SUMMARIZE: {text}"


class DummyLLM:
    async def generate(self, request):
        return "LLM SUMMARY"


@pytest.mark.asyncio
async def test_load_memory_with_events():
    repo = MagicMock()
    repo.get_events = AsyncMock(
        return_value=[
            {"text": "event1"},
            {"text": "event2"},
        ]
    )

    service = MemoryService(repo)

    memory = await service.load_memory("camp")

    assert memory.recent_events == ["event1", "event2"]


@pytest.mark.asyncio
async def test_load_memory_missing_text_field():
    repo = MagicMock()
    repo.get_events = AsyncMock(
        return_value=[
            {"foo": "bar"},
        ]
    )

    service = MemoryService(repo)

    memory = await service.load_memory("camp")

    assert memory.recent_events == [""]


@pytest.mark.asyncio
async def test_save_memory():
    repo = MagicMock()
    repo.save_events = AsyncMock()

    service = MemoryService(repo)

    memory = NarrativeMemory()
    memory.add_event("event1")
    memory.add_event("event2")

    await service.save_memory("camp", memory)

    repo.save_events.assert_called_once_with("camp", [{"text": "event1"}, {"text": "event2"}])


@pytest.mark.asyncio
async def test_append_new_memory():
    repo = MagicMock()
    repo.get_events = AsyncMock(return_value=[])
    repo.save_events = AsyncMock()

    service = MemoryService(repo)

    await service.append("camp", "new event")

    repo.save_events.assert_called_once()


@pytest.mark.asyncio
async def test_append_existing_memory():
    repo = MagicMock()
    repo.get_events = AsyncMock(return_value=[{"text": "old"}])
    repo.save_events = AsyncMock()

    service = MemoryService(repo)

    await service.append("camp", "new")

    args = repo.save_events.call_args[0]

    assert args[0] == "camp"
    assert {"text": "old"} in args[1]
    assert {"text": "new"} in args[1]


@pytest.mark.asyncio
async def test_clear_memory():
    repo = MagicMock()
    repo.save_events = AsyncMock()

    service = MemoryService(repo)

    await service.clear("camp")

    repo.save_events.assert_called_once_with("camp", [])


@pytest.mark.asyncio
async def test_append_flow_calls_load_and_save():
    repo = MagicMock()
    repo.get_events = AsyncMock(return_value=[])
    repo.save_events = AsyncMock()

    service = MemoryService(repo)

    await service.append("camp", "event")

    repo.get_events.assert_called_once_with("camp")
    repo.save_events.assert_called_once()


@pytest.mark.asyncio
async def test_append_empty_text():
    repo = MagicMock()
    repo.get_events = AsyncMock(return_value=[])
    repo.save_events = AsyncMock()

    service = MemoryService(repo)

    await service.append("camp", "")

    repo.save_events.assert_not_called()


def test_create_empty():
    service = MemoryService(DummyRepo())

    mem = service.create_empty()

    assert isinstance(mem, NarrativeMemory)
    assert mem.recent_events == []


@pytest.mark.asyncio
async def test_load_memory_empty():
    service = MemoryService(DummyRepo([]))

    mem = await service.load_memory("c1")

    assert mem.recent_events == []


@pytest.mark.asyncio
async def test_load_memory_with_data():
    repo = DummyRepo([{"text": "a"}, {"text": "b"}])
    service = MemoryService(repo)

    mem = await service.load_memory("c1")

    assert mem.recent_events == ["a", "b"]


@pytest.mark.asyncio
async def test_append_no_overflow():
    repo = DummyRepo([{"text": "a"}])
    service = MemoryService(repo, max_events=5)

    await service.append("c1", "b")

    assert repo.saved is not None
    _, events = repo.saved

    assert len(events) == 2


@pytest.mark.asyncio
async def test_append_overflow_no_summarizer():
    repo = DummyRepo([{"text": str(i)} for i in range(5)])

    service = MemoryService(repo, max_events=3)

    await service.append("c1", "new")

    assert repo.saved is not None
    _, events = repo.saved

    assert len(events) == 3


@pytest.mark.asyncio
async def test_append_with_summarizer_no_llm():
    repo = DummyRepo([{"text": str(i)} for i in range(5)])

    service = MemoryService(
        repo,
        max_events=3,
        summarizer=DummySummarizer(),
    )

    await service.append("c1", "new")

    assert repo.saved is not None
    _, events = repo.saved

    assert len(events) == 3


@pytest.mark.asyncio
async def test_append_with_llm_summary():
    repo = DummyRepo([{"text": str(i)} for i in range(5)])

    service = MemoryService(
        repo,
        max_events=3,
        summarizer=DummySummarizer(),
        llm_service=DummyLLM(),
    )

    await service.append("c1", "new")

    assert repo.saved is not None
    _, events = repo.saved

    assert len(events) == 3


@pytest.mark.asyncio
async def test_clear():
    repo = DummyRepo([{"text": "a"}])
    service = MemoryService(repo)

    await service.clear("c1")

    assert repo.saved == ("c1", [])


def test_compress_short():
    service = MemoryService(DummyRepo())

    text = "hello"

    assert service._default_compress(text) == "hello"


def test_compress_long():
    service = MemoryService(DummyRepo())

    text = "word " * 100

    result = service._default_compress(text)

    assert len(result) <= 200
