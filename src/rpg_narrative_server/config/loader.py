import logging
import os
from functools import lru_cache

from rpg_narrative_server.config.env_loader import load_environment
from rpg_narrative_server.config.profile import ProfileConfig, build_profile, get_profile_defaults

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


def _get(name: str) -> str | None:
    """Campos opcionais — pode ser None."""
    return os.getenv(name)


def _get_str(name: str, default: str) -> str:
    """Campos obrigatórios — nunca None."""
    return os.getenv(name, default) or default


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default


def _get_log_level() -> int:
    return getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)


# ---------------------------------------------------------
# ponto único de entrada para todo o sistema
# ---------------------------------------------------------


@lru_cache
def load_settings() -> ProfileConfig:
    profile_name = _get_str("APP_PROFILE", "local")
    d = get_profile_defaults(profile_name)

    return build_profile(
        # perfil
        profile=profile_name,
        # storage
        storage=_get_str("STORAGE", str(d["storage"])),
        campaign_file=_get_str("CAMPAIGN_PATH", "./data"),
        max_file_size_kb=_get_int("MAX_FILE_SIZE_KB", 1024),
        max_entries_per_file=_get_int("MAX_ENTRIES_PER_FILE", 5000),
        # LLM
        llm_provider=_get_str("LLM_PROVIDER", str(d["llm_provider"])),
        llm_model=_get_str("LLM_MODEL", str(d["llm_model"])),
        llm_api_key=_get("LLM_API_KEY"),
        llm_base_url=_get("LLM_BASE_URL"),
        llm_timeout=_get_int("LLM_TIMEOUT", 180),
        # embeddings
        embedding_provider=_get_str("EMBEDDING_PROVIDER", str(d["embedding_provider"])),
        embedding_model=_get_str("EMBEDDING_MODEL", str(d["embedding_model"])),
        embedding_api_key=_get("EMBEDDING_API_KEY"),
        embedding_base_url=_get("EMBEDDING_BASE_URL"),
        embedding_dim=_get_int("EMBEDDING_DIMENSION", int(d["embedding_dim"])),
        embedding_batch=_get_int("EMBEDDING_BATCH_SIZE", 32),
        # runtime
        environment=ENVIRONMENT,
        device=_get("DEVICE"),
        log_level=_get_log_level(),
        max_cache_size=_get_int("MAX_CACHE_SIZE", 10000),
        # discord
        discord_enable=_get("DISCORD_ENABLE"),
        discord_token=_get("DISCORD_TOKEN"),
        discord_public_key=_get("DISCORD_PUBLIC_KEY"),
        discord_app_id=_get("DISCORD_APPLICATION_ID"),
    )
