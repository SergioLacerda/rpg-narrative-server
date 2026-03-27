import pytest
from unittest.mock import AsyncMock, MagicMock

from rpg_narrative_server.application.services.memory_service import MemoryService
from rpg_narrative_server.domain.narrative.narrative_memory import NarrativeMemory


@pytest.mark.asyncio
async def test_load_memory_empty():
    repo = MagicMock()
    repo.get_events = AsyncMock(return_value=[])

    service = MemoryService(repo)

    memory = await service.load_memory("camp")

    assert isinstance(memory, NarrativeMemory)
    assert memory.recent_events == []


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

    repo.save_events.assert_called_once_with(
        "camp", [{"text": "event1"}, {"text": "event2"}]
    )


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
