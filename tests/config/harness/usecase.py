class UsecaseHarness:

    def __init__(self, name, *, container_factory, **overrides):
        self.name = name
        self.container = container_factory(**overrides)
        self.usecase = getattr(self.container, name)

    async def run(self, **kwargs):
        return await self.usecase.execute(**kwargs)