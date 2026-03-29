from typing import Any


class CampaignCommand:
    name = "campaign"

    def __init__(self, campaign_state):
        self.campaign_state = campaign_state

    async def execute(
        self,
        ctx: Any,
        action: str | None = None,
        name: str | None = None,
    ):
        if action == "start":
            if not name:
                return "⚠️ Informe o nome da campanha."

            self.campaign_state.set(ctx.channel.id, name)
            return f"🎲 Campanha '{name}' iniciada."

        if action == "stop":
            current = self.campaign_state.get(ctx.channel.id)

            if not current:
                return "⚠️ Nenhuma campanha ativa."

            self.campaign_state.clear(ctx.channel.id)
            return "🛑 Campanha encerrada."

        current = self.campaign_state.get(ctx.channel.id)

        if not current:
            return "⚠️ Nenhuma campanha ativa."

        return f"🎲 Campanha atual: {current}"


def build_campaign_command(deps):
    return CampaignCommand(deps.campaign_state)
