from typing import Protocol


class LLMGateway(Protocol):
    async def generate(self, prompt: str) -> str: ...
