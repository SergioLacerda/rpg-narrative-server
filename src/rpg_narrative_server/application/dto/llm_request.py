from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class LLMRequest:
    prompt: str

    # contexto
    system_prompt: Optional[str] = None

    # geração
    temperature: float = 0.7
    max_tokens: int = 1000

    # execução
    timeout: Optional[float] = None

    # metadata (🔥 importante)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ---------------------------------------------------------
    # validation
    # ---------------------------------------------------------

    def __post_init__(self):

        # prompt
        if not self.prompt or not self.prompt.strip():
            raise ValueError("LLMRequest.prompt cannot be empty")

        self.prompt = self.prompt.strip()

        # temperature
        if not (0 <= self.temperature <= 2):
            raise ValueError("temperature must be between 0 and 2")

        # tokens
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be > 0")