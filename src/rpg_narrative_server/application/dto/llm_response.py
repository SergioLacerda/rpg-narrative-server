from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    content: str

    provider: str
    model: Optional[str] = None

    # métricas
    latency_ms: Optional[float] = None
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None

    # debug
    raw: Optional[dict] = None
