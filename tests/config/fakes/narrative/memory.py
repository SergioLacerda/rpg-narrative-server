class DummyMemory:

    def __init__(self, history=None):
        self.recent_events = list(history or [])
        self.summary = None

        self.events = self.recent_events

    def add_event(self, event):
        if event:
            self.recent_events.append(event)

    def update_summary(self, summary):
        self.summary = summary
