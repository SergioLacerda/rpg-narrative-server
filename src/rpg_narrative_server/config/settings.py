import logging
from dataclasses import dataclass
from typing import Literal

StorageType = Literal["json", "chroma", "memory"]
EmbeddingProfile = Literal["local", "hybrid", "cloud"]


# ==========================================================
# LLM
# ==========================================================


@dataclass(frozen=True)
class LLMSettings:
    provider: Literal["openai", "lmstudio", "ollama", "groq", "anthropic"]
    model: str
    api_key: str | None = None
    base_url: str | None = None


# ==========================================================
# EMBEDDINGS
# ==========================================================


@dataclass(frozen=True)
class EmbeddingSettings:
    profile: EmbeddingProfile

    provider: str
    model: str

    api_key: str | None = None
    base_url: str | None = None

    batch_size: int = 32
    dimension: int | None = None


# ==========================================================
# RUNTIME
# ==========================================================


@dataclass(frozen=True)
class RuntimeSettings:
    environment: str
    device: str | None = None
    log_level: int = logging.INFO
    execution_timeout: int = 180


# ==========================================================
# APP
# ==========================================================


@dataclass(frozen=True)
class AppSettings:
    discord_token: str | None
    max_cache_size: int
    campaign_file: str

    storage: StorageType = "json"

    max_file_size_kb: int = 1024
    max_entries_per_file: int = 5000


# ==========================================================
# ROOT
# ==========================================================


@dataclass(frozen=True)
class Settings:
    runtime: RuntimeSettings
    llm: LLMSettings
    embeddings: EmbeddingSettings
    app: AppSettings
