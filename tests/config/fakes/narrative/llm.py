from typing import Any

from rpg_narrative_server.application.dto.llm_response import LLMResponse


class DummyLLM:
    def __init__(
        self,
        *,
        mode: str = "valid",  # valid | invalid | error
        response: str | None = None,
        error: Exception | None = None,
    ):
        self.mode = mode
        self.response = response
        self.error = error or RuntimeError("LLM failure")

        self.calls: list[Any] = []

    # ---------------------------------------------------------

    async def generate(self, request):
        # ✔ consistente
        self.calls.append(request)

        # -----------------------------------------------------
        # ERROR MODE
        # -----------------------------------------------------
        if self.mode == "error":
            raise self.error

        # -----------------------------------------------------
        # INVALID MODE (força fallback)
        # -----------------------------------------------------
        if self.mode == "invalid":
            return LLMResponse(
                content=self.response or "",  # vazio = inválido
                provider="dummy",
                model="dummy-model",
            )

        # -----------------------------------------------------
        # VALID MODE
        # -----------------------------------------------------
        if self.mode == "valid":
            content = self.response or (
                "You push the door open slowly, revealing a dim corridor. "
                "A faint echo suggests something is moving deeper inside."
            )

            return LLMResponse(
                content=content,
                provider="dummy",
                model="dummy-model",
            )

        # -----------------------------------------------------
        # SAFETY FALLBACK
        # -----------------------------------------------------
        return LLMResponse(
            content=self.response or f"Narrativa sobre: {request.prompt}",
            provider="dummy",
            model="dummy-model",
        )
