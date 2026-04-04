from rpg_narrative_server.infrastructure.narrative.narrative_memory import (
    NarrativeMemory,
)


def test_initial_state():
    mem = NarrativeMemory()

    assert mem.world_facts == []
    assert mem.scene_state == []
    assert mem.recent_events == []
    assert mem.summary == ""


def test_add_event():
    mem = NarrativeMemory()

    mem.add_event("dragon appeared")

    assert mem.recent_events == ["dragon appeared"]


def test_add_multiple_events():
    mem = NarrativeMemory()

    mem.add_event("event1")
    mem.add_event("event2")

    assert mem.recent_events == ["event1", "event2"]


def test_update_summary():
    mem = NarrativeMemory()

    mem.update_summary("battle ended")

    assert mem.summary == "battle ended"


def test_update_summary_overwrites():
    mem = NarrativeMemory()

    mem.update_summary("old")
    mem.update_summary("new")

    assert mem.summary == "new"
