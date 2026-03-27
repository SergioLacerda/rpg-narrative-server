# vector_index/api/index.py

class VectorIndexAPI:

    def __init__(self, engine):
        self._engine = engine

    async def search(self, query: str, k: int = 4):
        return await self._engine.search(query, k)