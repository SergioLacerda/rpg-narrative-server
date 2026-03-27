class DummyIntent:
    def __init__(self, value="ACTION"):
        self.value = value

    async def classify(self, text: str):
        return self.value

    async def is_action(self, text: str):
        return self.value == "ACTION"
