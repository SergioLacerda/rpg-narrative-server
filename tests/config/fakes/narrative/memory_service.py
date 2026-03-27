from .memory import DummyMemory


class DummyMemoryService:
    def __init__(self, history=None):
        self.memory = DummyMemory(history)
        self.saved_memory = None

    async def load_memory(self, campaign_id):
        return self.memory

    async def save_memory(self, campaign_id, memory):
        self.saved_memory = memory
