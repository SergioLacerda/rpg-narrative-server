from fastapi import APIRouter

from rpg_narrative_server.config.loader import load_settings

router = APIRouter()


@router.get("/system/config")
def get_config():
    profile = load_settings()
    return {
        "environment": profile.environment,
        "storage": profile.storage,
        "llm_provider": profile.llm_provider,
        "llm_model": profile.llm_model,
        "embedding_provider": profile.embedding_provider,
        "embedding_model": profile.embedding_model,
    }
