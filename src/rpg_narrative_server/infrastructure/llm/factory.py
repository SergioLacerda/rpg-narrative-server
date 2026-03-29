from rpg_narrative_server.config.profile import ProfileConfig


def create_llm_provider(settings: ProfileConfig):
    provider = settings.llm_provider.lower()

    # ---------------------------------------------------------
    # OPENAI
    # ---------------------------------------------------------
    if provider == "openai":
        from rpg_narrative_server.infrastructure.llm.openai_provider import OpenAIProvider

        return OpenAIProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            base_url=settings.llm_base_url,
        )

    # ---------------------------------------------------------
    # LM STUDIO
    # ---------------------------------------------------------
    if provider == "lmstudio":
        from rpg_narrative_server.infrastructure.llm.lmstudio_provider import LMStudioProvider

        return LMStudioProvider(
            model=settings.llm_model,
            base_url=settings.llm_base_url,
        )

    # ---------------------------------------------------------
    # OLLAMA
    # ---------------------------------------------------------
    if provider == "ollama":
        from rpg_narrative_server.infrastructure.llm.ollama_provider import OllamaProvider

        return OllamaProvider(
            model=settings.llm_model,
            base_url=settings.llm_base_url,
        )

    # ---------------------------------------------------------
    # GROQ
    # ---------------------------------------------------------
    if provider == "groq":
        from rpg_narrative_server.infrastructure.llm.groq_provider import GroqProvider

        return GroqProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
        )

    # ---------------------------------------------------------
    # ANTHROPIC
    # ---------------------------------------------------------
    if provider == "anthropic":
        from rpg_narrative_server.infrastructure.llm.anthropic_provider import AnthropicProvider

        return AnthropicProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
        )

    raise ValueError(
        f"Unknown LLM provider: {provider!r}. " f"Valid: openai, lmstudio, ollama, groq, anthropic"
    )
