from fastapi import APIRouter, Depends

from rpg_narrative_server.interfaces.api.dependencies import get_health_service

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/ready")
async def ready(health_service=Depends(get_health_service)):
    is_ready = True

    if hasattr(health_service, "is_ready"):
        is_ready = await health_service.is_ready()

    return {"status": "ready" if is_ready else "loading"}
