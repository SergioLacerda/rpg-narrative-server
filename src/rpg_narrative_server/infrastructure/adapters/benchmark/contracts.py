from typing import Protocol


class RetrievalLike(Protocol):
    async def search(self, query: str): ...
