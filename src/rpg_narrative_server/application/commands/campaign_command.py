from typing import Any


class CampaignCommand:
    name = "campaign"

    def __init__(
        self,
        campaign_state,
        create_campaign,
        list_campaigns,
        delete_campaign,
    ):
        self.campaign_state = campaign_state
        self.create_campaign = create_campaign
        self.list_campaigns = list_campaigns
        self.delete_campaign = delete_campaign

    async def execute(
        self,
        ctx: Any,
        action: str | None = None,
        name: str | None = None,
    ):
        # -----------------------------
        # START
        # -----------------------------
        if action == "start":
            if not name:
                return "⚠️ Informe o nome da campanha."

            created = await self.create_campaign.execute(name)

            self.campaign_state.set(ctx.channel.id, name)

            if created:
                return f"🎲 Campanha '{name}' criada e iniciada."

            return f"🎲 Campanha '{name}' carregada."

        # -----------------------------
        # SWITCH
        # -----------------------------
        if action == "switch":
            if not name:
                return "⚠️ Informe o nome da campanha."

            self.campaign_state.set(ctx.channel.id, name)
            return f"🔁 Campanha alterada para '{name}'."

        # -----------------------------
        # LIST
        # -----------------------------
        if action == "list":
            campaigns = await self.list_campaigns.execute()

            if not campaigns:
                return "📭 Nenhuma campanha encontrada."

            return "📚 Campanhas:\n" + "\n".join(f"- {c}" for c in campaigns)

        # -----------------------------
        # DELETE
        # -----------------------------
        if action == "delete":
            if not name:
                return "⚠️ Informe o nome da campanha."

            ok = await self.delete_campaign.execute(name)

            if not ok:
                return "⚠️ Campanha não encontrada."

            return f"🗑️ Campanha '{name}' removida."

        # -----------------------------
        # STOP
        # -----------------------------
        if action == "stop":
            current = self.campaign_state.get(ctx.channel.id)

            if not current:
                return "⚠️ Nenhuma campanha ativa."

            self.campaign_state.clear(ctx.channel.id)
            return "🛑 Campanha encerrada."

        # -----------------------------
        # STATUS
        # -----------------------------
        current = self.campaign_state.get(ctx.channel.id)

        if not current:
            return "⚠️ Nenhuma campanha ativa."

        return f"🎲 Campanha atual: {current}"


def build_campaign_command(deps):
    return CampaignCommand(
        campaign_state=deps.campaign_state,
        create_campaign=deps.create_campaign,
        list_campaigns=deps.list_campaigns,
        delete_campaign=deps.delete_campaign,
    )
