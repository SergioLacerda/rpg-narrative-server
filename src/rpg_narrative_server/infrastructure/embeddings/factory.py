from rpg_narrative_server.application.ports.embedding_gateway import EmbeddingGateway
from rpg_narrative_server.config.profile import ProfileConfig


def create_embedding(settings: ProfileConfig) -> EmbeddingGateway:
    provider = settings.embedding_provider.lower()

    # ---------------------------------------------------------
    # LOCAL (sentence-transformers)
    # ---------------------------------------------------------
    if provider == "sentence":
        from rpg_narrative_server.infrastructure.embeddings.providers.sentence_embedding_provider import (
            SentenceEmbeddingProvider,
        )

        return SentenceEmbeddingProvider(
            model=settings.embedding_model or "all-MiniLM-L6-v2",
            device=settings.device,
        )

    # ---------------------------------------------------------
    # OPENAI
    # ---------------------------------------------------------
    if provider == "openai":
        from rpg_narrative_server.infrastructure.embeddings.providers.openai_embedding_provider import (
            OpenAIEmbeddingProvider,
        )

        return OpenAIEmbeddingProvider(
            api_key=settings.embedding_api_key,
            model=settings.embedding_model,
            base_url=settings.embedding_base_url,
        )

    # ---------------------------------------------------------
    # OLLAMA
    # ---------------------------------------------------------
    if provider == "ollama":
        from rpg_narrative_server.infrastructure.embeddings.providers.ollama_embedding_provider import (
            OllamaEmbeddingProvider,
        )

        return OllamaEmbeddingProvider(
            model=settings.embedding_model,
            base_url=settings.embedding_base_url,
        )

    # ---------------------------------------------------------
    # LM STUDIO
    # ---------------------------------------------------------
    if provider == "lmstudio":
        from rpg_narrative_server.infrastructure.embeddings.providers.lmstudio_embedding_provider import (
            LMStudioEmbeddingProvider,
        )

        return LMStudioEmbeddingProvider(
            model=settings.embedding_model,
            base_url=settings.embedding_base_url,
        )

    # ---------------------------------------------------------
    # GEMINI
    # ---------------------------------------------------------
    if provider == "gemini":
        from rpg_narrative_server.infrastructure.embeddings.providers.gemini_embedding_provider import (
            GeminiEmbeddingProvider,
        )

        return GeminiEmbeddingProvider(
            api_key=settings.embedding_api_key,
            model=settings.embedding_model,
        )

    raise ValueError(f"Unknown embedding provider: {provider}")
