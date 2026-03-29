from rpg_narrative_server.application.dto.llm_request import LLMRequest
from rpg_narrative_server.application.dto.llm_response import LLMResponse


class FakeLLMService:
    def __init__(
        self,
        result: str | None = None,
        fail: bool = False,
    ) -> None:
        self.result = result
        self.fail = fail
        self.calls: list[LLMRequest] = []

    async def generate(self, request: LLMRequest) -> LLMResponse:
        if not isinstance(request, LLMRequest):
            raise TypeError("FakeLLMService espera LLMRequest")

        self.calls.append(request)

        if self.fail:
            raise RuntimeError("Fake LLM failure")

        # ---------------------------------
        # resposta explícita
        # ---------------------------------
        if self.result is not None:
            return LLMResponse(
                content=self.result,
                provider="fake",
                model="fake-model",
            )

        # ---------------------------------
        # comportamento baseado no prompt
        # ---------------------------------
        prompt = request.prompt.lower()
        tail = prompt[-200:]

        if "look" in tail:
            content = "you look around"

        elif "enter room" in tail:
            content = "you enter the room"

        elif "open door" in tail:
            content = "you open the door"

        else:
            content = "action processed"

        return LLMResponse(
            content=content,
            provider="fake",
            model="fake-model",
        )
