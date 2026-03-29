class UsecaseHarness:
    def __init__(self, name, *, container_factory, **overrides):
        self.name = name
        self.container = container_factory(**overrides)

        self.usecase = getattr(self.container, name)

        assert hasattr(self.usecase, "execute")

    async def run(self, **kwargs):
        result = await self.usecase.execute(**kwargs)

        return result
