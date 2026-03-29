# src/rpg_narrative_server/infrastructure/llm/factory.py

from rpg_narrative_server.config.loader import Settings


def create_llm_provider(settings: Settings):
    s = settings.llm

    if s.provider == "openai":
        from rpg_narrative_server.infrastructure.llm.openai_provider import OpenAIProvider

        return OpenAIProvider(
            api_key=s.api_key,
            model=s.model,
            base_url=s.base_url,
        )

    if s.provider == "lmstudio":
        from rpg_narrative_server.infrastructure.llm.lmstudio_provider import LMStudioProvider

        return LMStudioProvider(
            model=s.model,
            base_url=s.base_url,
        )

    if s.provider == "ollama":
        from rpg_narrative_server.infrastructure.llm.ollama_provider import OllamaProvider

        return OllamaProvider(
            model=s.model,
            base_url=s.base_url,
        )

    raise ValueError(f"Unknown LLM provider: {s.provider}")
