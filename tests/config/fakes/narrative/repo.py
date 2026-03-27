from .graph import DummyGraph


class DummyGraphRepo:
    def __init__(self, graph=None):
        self.graph = graph or DummyGraph()
        self.saved_graph = None

    def load(self):
        return self.graph

    def save(self, graph):
        self.saved_graph = graph
