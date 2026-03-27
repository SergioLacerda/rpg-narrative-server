import time
import uuid

from rpg_narrative_server.domain.narrative.narrative_memory import NarrativeMemory


class NarrativeMemoryService:
    """
    Orquestra memória narrativa + helpers para indexação.
    """

    def __init__(self, repo):
        self.repo = repo

    # ---------------------------------------------------------
    # leitura
    # ---------------------------------------------------------

    def load(self) -> NarrativeMemory:
        return self.repo.load()

    # ---------------------------------------------------------
    # helpers
    # ---------------------------------------------------------

    def now(self) -> float:
        return time.time()

    def generate_event_id(self) -> str:
        return str(uuid.uuid4())

    def get_last_event_id(self):

        memory = self.repo.load()

        if not memory.events:
            return None

        return memory.events[-1].get("id")

    # ---------------------------------------------------------
    # update
    # ---------------------------------------------------------

    def add_event(self, text: str):

        memory = self.repo.load()

        event = {
            "id": self.generate_event_id(),
            "text": text,
            "timestamp": self.now(),
        }

        memory.add_event(event)

        self.repo.save(memory)

        return event

    def update_summary(self, summary: str):

        memory = self.repo.load()

        memory.update_summary(summary)

        self.repo.save(memory)

    # ---------------------------------------------------------
    # NLP simples (MVP)
    # ---------------------------------------------------------

    def extract_tokens(self, text: str):

        return [
            token.lower()
            for token in text.split()
            if len(token) > 2
        ]