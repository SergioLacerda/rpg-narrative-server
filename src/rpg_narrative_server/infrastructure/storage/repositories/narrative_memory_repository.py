import json
from pathlib import Path

from rpg_narrative_server.domain.narrative.narrative_memory import NarrativeMemory


class NarrativeMemoryRepository:

    def __init__(self, path: Path):
        self.path = path

    # ---------------------------------------------------------
    # load
    # ---------------------------------------------------------

    async def load(self) -> NarrativeMemory:

        if not self.path.exists():
            return NarrativeMemory()

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return NarrativeMemory.from_dict(data)

        except Exception:
            return NarrativeMemory()

    # ---------------------------------------------------------
    # save
    # ---------------------------------------------------------

    async def save(self, memory: NarrativeMemory):

        data = memory.to_dict()

        self.path.write_text(json.dumps(data, indent=2))
