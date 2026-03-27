class DummyKV:
    def __init__(self):
        self.data = {}

    def set(self, k, v):
        self.data[k] = v

    def get(self, k):
        return self.data.get(k)

    def clear(self):
        self.data.clear()