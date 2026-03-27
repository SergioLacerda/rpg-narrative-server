
class DummySelector:
    def __init__(self):
        self.received = None

    def select(self, docs):
        self.received = docs
        return docs[:2]