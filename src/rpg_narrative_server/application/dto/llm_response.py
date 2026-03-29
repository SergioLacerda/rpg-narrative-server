from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str

    provider: str
    model: str | None = None

    # métricas
    latency_ms: float | None = None
    tokens_input: int | None = None
    tokens_output: int | None = None

    # debug
    raw: dict | None = None
