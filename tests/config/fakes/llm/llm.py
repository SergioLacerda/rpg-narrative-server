from typing import Any

from rpg_narrative_server.application.dto.llm_request import LLMRequest


class DummyLLM:
    def __init__(self, result: str = "ACTION") -> None:
        self.result = result
        self.calls: list[dict[str, Any]] = []

    async def generate(self, request: LLMRequest) -> str:
        self.calls.append(
            {
                "prompt": request.prompt,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
            }
        )
        return self.result
