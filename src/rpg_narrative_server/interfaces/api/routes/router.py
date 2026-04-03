from fastapi import APIRouter

from rpg_narrative_server.interfaces.api.routes.campaign_controller import (
    router as campaign_router,
)
from rpg_narrative_server.interfaces.api.routes.dice_controller import (
    router as dice_router,
)
from rpg_narrative_server.interfaces.api.routes.health_controller import (
    router as health_router,
)
from rpg_narrative_server.interfaces.api.routes.narrative_controller import (
    router as narrative_router,
)
from rpg_narrative_server.interfaces.api.routes.system_controller import (
    router as system_router,
)

api_router = APIRouter()

# domínio narrativo
api_router.include_router(
    narrative_router,
    prefix="/campaign",
    tags=["Narrative"],
)

api_router.include_router(
    campaign_router,
    prefix="/campaigns",
    tags=["Campaign"],
)

# utilidades
api_router.include_router(
    dice_router,
    prefix="/utils",
    tags=["Dice"],
)

# sistema
api_router.include_router(
    health_router,
    tags=["Health"],
)

api_router.include_router(
    system_router,
    tags=["System"],
)
