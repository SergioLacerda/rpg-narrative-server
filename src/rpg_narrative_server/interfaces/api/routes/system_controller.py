from fastapi import APIRouter

from rpg_narrative_server.config.loader import load_settings

router = APIRouter()


@router.get("/system/config")
def get_config():

    settings = load_settings()

    return {
        "environment": settings.runtime.environment,
        "storage": settings.app.storage,
        "embedding_provider": settings.embeddings.provider,
        "embedding_model": settings.embeddings.model,
        "llm_provider": settings.llm.provider,
        "llm_model": settings.llm.model,
    }
