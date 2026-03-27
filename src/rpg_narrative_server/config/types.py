from typing import TypedDict, Literal


LLMProvider = Literal["openai", "lmstudio", "ollama", "groq", "anthropic"]


class EmbeddingDefaults(TypedDict):
    provider: str
    model: str
    dimension: int
