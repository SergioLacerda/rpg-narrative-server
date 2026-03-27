class DummyLLM:
    def __init__(self, result="ACTION", error=None):
        self.result = result
        self.error = error

    async def classify(self, text):
        if self.error:
            raise self.error
        return self.result