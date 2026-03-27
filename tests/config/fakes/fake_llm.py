from rpg_narrative_server.application.dto.llm_request import LLMRequest


class FakeLLMService:
    """
    Fake do LLMService (não do provider)

    ✔ compatível com arquitetura nova
    ✔ previsível
    ✔ fácil de controlar em testes
    """

    def __init__(
        self,
        result: str | None = None,
        fail: bool = False,
    ) -> None:
        self.result = result
        self.fail = fail
        self.calls: list[LLMRequest] = []

    async def generate(self, request: LLMRequest) -> str:
        if not isinstance(request, LLMRequest):
            raise TypeError("FakeLLMService espera LLMRequest")

        self.calls.append(request)

        if self.fail:
            raise RuntimeError("Fake LLM failure")

        if self.result is not None:
            return self.result

        prompt = request.prompt.lower()
        tail = prompt[-200:]

        if "look" in tail:
            return "you look around"

        if "enter room" in tail:
            return "you enter the room"

        if "open door" in tail:
            return "you open the door"

        return "action processed"
