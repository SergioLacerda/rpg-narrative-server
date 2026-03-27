from pathlib import Path
from rpg_narrative_server.config.loader import load_settings


BASE_DATA_DIR = Path("data")
BASE_CAMPAIGNS_DIR = BASE_DATA_DIR / "campaigns"
LOG_DIR = Path("logs")


# ---------------------------------------------------------
# Campaign
# ---------------------------------------------------------
def get_campaign_path(campaign_id: str) -> Path:
    if not campaign_id or "/" in campaign_id:
        raise ValueError(f"Invalid campaign_id: {campaign_id}")

    return BASE_CAMPAIGNS_DIR / campaign_id


# ---------------------------------------------------------
# Paths resolver
# ---------------------------------------------------------
def get_paths(campaign_id: str | None = None):
    settings = load_settings()

    if campaign_id:
        base = get_campaign_path(campaign_id)
    else:
        base = Path(settings.app.campaign_file)  # legacy

    memory_dir = base / "memory"

    return {
        "campaign_dir": base,
        "memory_dir": memory_dir,
        "log_dir": LOG_DIR,
        "embedding_cache": memory_dir / "embedding_cache.json",
        "vector_index": base / "vector.index",
    }


# ---------------------------------------------------------
# Infra global (SEM campanha)
# ---------------------------------------------------------
def ensure_global_directories():
    BASE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    BASE_CAMPAIGNS_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Compatibilidade (IMPORTANTE)
# ---------------------------------------------------------
def ensure_directories():
    """
    Mantém compatibilidade com código antigo.
    NÃO cria estrutura de campanha.
    """
    ensure_global_directories()