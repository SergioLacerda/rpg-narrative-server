class DummyGraph:
    def __init__(self):
        self.updated_with = None
        self.related_called_with = None

    def update(self, entities):
        self.updated_with = entities

    def related(self, entities):
        self.related_called_with = entities
        return {"result_1", "result_2"}
