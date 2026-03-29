from typing import Any


class GMCommand:
    name = "gm"

    def __init__(self, narrative_usecase, campaign_state):
        self.narrative = narrative_usecase
        self.campaign_state = campaign_state

    async def execute(self, ctx: Any, action: str):
        if not action:
            return "⚠️ Ação inválida."

        campaign_id = self.campaign_state.get(ctx.channel.id)

        if not campaign_id:
            return "⚠️ Nenhuma campanha ativa."

        result = await self.narrative.execute(
            campaign_id=campaign_id,
            action=action,
            user_id=str(ctx.author.id),
        )

        if not result:
            return "⚠️ Nenhuma resposta gerada."

        if hasattr(result, "text"):
            return result.text

        return result


def build_gm_command(deps):
    return GMCommand(deps.narrative, deps.campaign_state)
