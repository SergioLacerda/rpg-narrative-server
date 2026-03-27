from typing import List


class NarrativeMemory:
    """
    Representa o estado narrativo de uma campanha.
    Não conhece IO.
    """

    def __init__(
        self,
        world_facts: List[str] | None = None,
        scene_state: List[str] | None = None,
        recent_events: List[str] | None = None,
        summary: str = "",
    ):
        self.world_facts = world_facts or []
        self.scene_state = scene_state or []
        self.recent_events = recent_events or []
        self.summary = summary

    # ---------------------------------------------------------
    # comportamento
    # ---------------------------------------------------------

    def add_event(self, text: str):
        self.recent_events.append(text)

    def add_fact(self, fact: str):
        self.world_facts.append(fact)

    def update_scene(self, state: str):
        self.scene_state.append(state)

    def update_summary(self, summary: str):
        self.summary = summary

    # ---------------------------------------------------------
    # serialização (boundary)
    # ---------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "world_facts": self.world_facts,
            "scene_state": self.scene_state,
            "recent_events": self.recent_events,
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: dict):

        return cls(
            world_facts=data.get("world_facts", []),
            scene_state=data.get("scene_state", []),
            recent_events=data.get("recent_events", []),
            summary=data.get("summary", ""),
        )