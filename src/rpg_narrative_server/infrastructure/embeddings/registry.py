class EmbeddingRegistry:

    def __init__(self):
        self._providers = {}

    def register(self, name: str, factory):

        if name in self._providers:
            return  # idempotente por nome

        self._providers[name] = factory

    def create(self, name: str, **kwargs):

        if name not in self._providers:
            raise ValueError(
                f"Embedding provider not found: {name}. "
                f"Available: {list(self._providers.keys())}"
            )

        return self._providers[name](**kwargs)
