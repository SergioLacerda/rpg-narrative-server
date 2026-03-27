from .memory import DummyMemory


class DummyMemoryRepo:
    def __init__(self, memory=None):
        self.memory = memory or DummyMemory()
        self.saved_memory = None

    def load(self):
        return self.memory

    def save(self, memory):
        self.saved_memory = memory