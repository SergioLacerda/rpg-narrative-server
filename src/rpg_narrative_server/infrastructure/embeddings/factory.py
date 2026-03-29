# src/rpg_narrative_server/infrastructure/embeddings/factory.py

from rpg_narrative_server.application.ports.embedding_gateway import (
    EmbeddingGateway,
)
from rpg_narrative_server.config.loader import Settings


def create_embedding(settings: Settings) -> EmbeddingGateway:
    s = settings
    provider = s.llm.provider.lower()

    # ---------------------------------------------------------
    # LOCAL (sentence-transformers)
    # ---------------------------------------------------------
    if provider == "sentence":
        from rpg_narrative_server.infrastructure.embeddings.providers.sentence_embedding_provider import (
            SentenceEmbeddingProvider,
        )

        return SentenceEmbeddingProvider(
            model=s.embeddings.model or "all-MiniLM-L6-v2",
            device=s.runtime.device,
        )

    # ---------------------------------------------------------
    # OPENAI
    # ---------------------------------------------------------
    if provider == "openai":
        from rpg_narrative_server.infrastructure.embeddings.providers.openai_embedding_provider import (
            OpenAIEmbeddingProvider,
        )

        return OpenAIEmbeddingProvider(
            api_key=s.embeddings.api_key,
            model=s.embeddings.model,
            base_url=s.embeddings.base_url,
        )

    # ---------------------------------------------------------
    # OLLAMA
    # ---------------------------------------------------------
    if provider == "ollama":
        from rpg_narrative_server.infrastructure.embeddings.providers.ollama_embedding_provider import (
            OllamaEmbeddingProvider,
        )

        return OllamaEmbeddingProvider(
            model=s.embeddings.model,
            base_url=s.embeddings.base_url,
        )

    # ---------------------------------------------------------
    # LM STUDIO
    # ---------------------------------------------------------
    if provider == "lmstudio":
        from rpg_narrative_server.infrastructure.embeddings.providers.lmstudio_embedding_provider import (
            LMStudioEmbeddingProvider,
        )

        return LMStudioEmbeddingProvider(
            model=s.embeddings.model,
            base_url=s.embeddings.base_url,
        )

    # ---------------------------------------------------------
    # GEMINI
    # ---------------------------------------------------------
    if provider == "gemini":
        from rpg_narrative_server.infrastructure.embeddings.providers.gemini_embedding_provider import (
            GeminiEmbeddingProvider,
        )

        return GeminiEmbeddingProvider(
            api_key=s.embeddings.api_key,
            model=s.embeddings.model,
        )

    raise ValueError(f"Unknown embedding provider: {provider}")
