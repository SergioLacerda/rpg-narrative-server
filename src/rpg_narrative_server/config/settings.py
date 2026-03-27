from dataclasses import dataclass
from typing import Optional, Literal
import logging


# ==========================================================
# LLM
# ==========================================================


@dataclass(frozen=True)
class LLMSettings:
    provider: Literal["openai", "lmstudio", "ollama", "groq", "anthropic"]
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None


# ==========================================================
# EMBEDDINGS
# ==========================================================


@dataclass(frozen=True)
class EmbeddingSettings:

    profile: Literal["local", "hybrid", "cloud"]

    provider: str
    model: str

    api_key: Optional[str] = None
    base_url: Optional[str] = None

    batch_size: int = 32

    # melhor deixar opcional (evita mismatch)
    dimension: Optional[int] = None


# ==========================================================
# RUNTIME
# ==========================================================


@dataclass(frozen=True)
class RuntimeSettings:

    environment: str
    device: Optional[str] = None

    log_level: int = logging.INFO

    execution_timeout: int = 180


# ==========================================================
# APP
# ==========================================================


@dataclass(frozen=True)
class AppSettings:

    discord_token: str
    max_cache_size: int
    campaign_file: str

    storage: Literal["json", "chroma", "memory"] = "json"

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


__all__ = [
    "Settings",
    "RuntimeSettings",
    "LLMSettings",
    "EmbeddingSettings",
    "AppSettings",
]
