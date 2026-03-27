from fastapi import APIRouter, Depends

from rpg_narrative_server.interfaces.api.schemas.narrative_schema import NarrativeEventRequest
from rpg_narrative_server.interfaces.api.dependencies import get_narrative_usecase

router = APIRouter()

@router.post("/{campaign_id}/event")
async def narrative_event(
    campaign_id: str,
    payload: NarrativeEventRequest,
    usecase = Depends(get_narrative_usecase)
):
    response = await usecase.execute(
        campaign_id=campaign_id,
        action=payload.action,
        user_id=payload.user_id
    )

    return {
        "status": "ok",
        "response": response,
    }