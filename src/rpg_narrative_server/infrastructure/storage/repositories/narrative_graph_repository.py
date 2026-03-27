import json
from pathlib import Path

from rpg_narrative_server.domain.narrative.narrative_graph import NarrativeGraph


class NarrativeGraphRepository:

    def __init__(self, path: Path):
        self.path = path

    def _safe_read(self):
        try:
            return json.loads(self.path.read_text())
        except Exception:
            return {}
            
    # ---------------------------------------------------------
    # load
    # ---------------------------------------------------------

    async def load(self) -> NarrativeGraph:

        if not self.path.exists():
            return NarrativeGraph()

        try:
            data = json.loads(self.path.read_text())
            return NarrativeGraph.from_dict(data)

        except Exception:
            return NarrativeGraph()

    # ---------------------------------------------------------
    # save
    # ---------------------------------------------------------

    async def save(self, graph: NarrativeGraph):

        data = graph.to_dict()

        self.path.write_text(
            json.dumps(data, indent=2)
        )