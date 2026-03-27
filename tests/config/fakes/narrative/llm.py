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

        self.calls = []

    # ---------------------------------------------------------

    async def generate(self, request):

        # 🔥 registra chamada
        self.calls.append(request.prompt)

        # -----------------------------------------------------
        # ERROR MODE
        # -----------------------------------------------------
        if self.mode == "error":
            raise self.error

        # -----------------------------------------------------
        # INVALID MODE (força fallback)
        # -----------------------------------------------------
        if self.mode == "invalid":
            return self.response or "ok"  # curto / inválido

        # -----------------------------------------------------
        # VALID MODE
        # -----------------------------------------------------
        if self.mode == "valid":
            return self.response or (
                "You push the door open slowly, revealing a dim corridor. "
                "A faint echo suggests something is moving deeper inside."
            )

        # -----------------------------------------------------
        # fallback safety
        # -----------------------------------------------------
        return "Unexpected state"
