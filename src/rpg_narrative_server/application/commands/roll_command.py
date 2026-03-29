from typing import Any


class RollCommand:
    name = "roll"

    def __init__(self, roll_usecase):
        self.roll = roll_usecase

    async def execute(self, ctx: Any, expression: str):
        if not expression:
            return "⚠️ Expressão inválida."

        result = await self.roll.execute(expression)

        if result is None:
            return "⚠️ Nenhum resultado."

        return result


def build_roll_command(deps):
    return RollCommand(deps.roll_dice)
