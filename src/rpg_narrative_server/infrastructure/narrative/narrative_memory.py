class NarrativeMemory:
    def __init__(self):
        self.world_facts = []
        self.scene_state = []
        self.recent_events = []
        self.summary = ""

    def add_event(self, text: str):
        self.recent_events.append(text)

    def update_summary(self, summary: str):
        self.summary = summary
