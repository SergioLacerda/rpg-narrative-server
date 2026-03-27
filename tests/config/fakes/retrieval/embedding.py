class DummyEmbedding:
    def __init__(self, result=None, error=None):
        self.result = result or [1.0]
        self.error = error
        self.called = False

    async def embed(self, text):
        self.called = True

        if self.error:
            raise self.error

        return self.result