from fastapi import APIRouter, Depends

from rpg_narrative_server.interfaces.api.dependencies import get_roll_dice_usecase

router = APIRouter()


@router.get("/roll")
async def roll(expression: str, usecase=Depends(get_roll_dice_usecase)):
    result = await usecase.execute(expression)

    return {
        "expression": expression,
        "result": result,
    }
