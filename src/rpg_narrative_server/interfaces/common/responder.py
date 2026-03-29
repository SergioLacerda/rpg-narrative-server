from typing import Protocol


class Responder(Protocol):
    async def send(self, content: str) -> None: ...
