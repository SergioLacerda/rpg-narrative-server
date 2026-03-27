import os
import logging
from functools import lru_cache
from typing import cast

from rpg_narrative_server.config.types import EmbeddingDefaults, LLMProvider
from rpg_narrative_server.config.env_loader import load_environment
from rpg_narrative_server.config.profile import load_profile

from rpg_narrative_server.config.settings import (
    Settings,
    RuntimeSettings,
    LLMSettings,
    EmbeddingSettings,
    AppSettings,
)


# ---------------------------------------------------------
# bootstrap ENV
# ---------------------------------------------------------

ENVIRONMENT, ENV_FILES, CLI_OVERRIDES = load_environment()

device = os.getenv("DEVICE", "").lower()

if device == "cpu":
    os.environ["CUDA_VISIBLE_DEVICES"] = ""


# ---------------------------------------------------------
# helpers
# ---------------------------------------------------------


def _get(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except Exception:
        return default


def _require(name: str) -> str:
    value = _get(name)
    if not value:
        raise RuntimeError(f"Missing env variable: {name}")
    return value


def _get_log_level() -> int:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    return getattr(logging, level, logging.INFO)


def _get_embedding_defaults(profile_embedding: str) -> EmbeddingDefaults:
    if profile_embedding == "local":
        return {
            "provider": "sentence",
            "model": "intfloat/e5-base-v2",
            "dimension": 768,
        }

    return {
        "provider": "openai",
        "model": "text-embedding-3-small",
        "dimension": 1536,
    }


def _validate_llm_provider(value: str) -> LLMProvider:
    if value not in {"openai", "lmstudio", "ollama", "groq", "anthropic"}:
        raise ValueError(f"Invalid LLM provider: {value}")
    return cast(LLMProvider, value)


# ---------------------------------------------------------
# settings loader
# ---------------------------------------------------------


@lru_cache
def load_settings() -> Settings:
    profile = load_profile()

    embedding_defaults = _get_embedding_defaults(profile.embedding)

    provider = _get("EMBEDDING_PROVIDER", embedding_defaults["provider"])

    settings = Settings(
        runtime=RuntimeSettings(
            environment=ENVIRONMENT,
            device=_get("DEVICE"),
            log_level=_get_log_level(),
            execution_timeout=_get_int("LLM_TIMEOUT", 180),
        ),
        llm=LLMSettings(
            provider=_validate_llm_provider(_get("LLM_PROVIDER", "openai") or "openai"),
            model=_get("LLM_MODEL", "gpt-4o-mini") or "gpt-4o-mini",
            api_key=_get("LLM_API_KEY"),
            base_url=_get("LLM_BASE_URL"),
        ),
        embeddings=EmbeddingSettings(
            profile=profile.embedding,
            provider=provider or "openai",
            model=_get("EMBEDDING_MODEL", embedding_defaults["model"])
            or embedding_defaults["model"],
            api_key=_get("EMBEDDING_API_KEY"),
            base_url=_get("EMBEDDING_BASE_URL"),
            batch_size=_get_int("EMBEDDING_BATCH_SIZE", 32),
            dimension=_get_int("EMBEDDING_DIMENSION", embedding_defaults["dimension"]),
        ),
        app=AppSettings(
            discord_token=_require("DISCORD_TOKEN"),
            max_cache_size=_get_int("MAX_CACHE_SIZE", 10000),
            campaign_file=_get("CAMPAIGN_PATH", "./data") or "./data",
            storage=profile.storage,
        ),
    )

    # validação leve
    if settings.embeddings.provider not in {
        "openai",
        "sentence",
        "ollama",
        "lmstudio",
        "gemini",
    }:
        raise ValueError(f"Invalid embedding provider: {settings.embeddings.provider}")

    return settings
