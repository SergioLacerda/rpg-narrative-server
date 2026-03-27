import logging
from discord.ext import commands

from rpg_narrative_server.frameworks.discord.responder import send
from rpg_narrative_server.bootstrap.container import get_container

logger = logging.getLogger("rpg_narrative_server.discord")


def register_campaign_commands(bot):

    @bot.hybrid_command(name="campaign", description="Gerenciar campanha")
    async def campaign(ctx: commands.Context, action: str = None, name: str = None):

        action = (action or "").lower().strip()
        name = (name or "").strip()

        container = get_container()
        channel_id = str(ctx.channel.id)

        # ---------------------------------------------------------
        # DEFAULT (UX melhor)
        # ---------------------------------------------------------
        if not action:
            current = container.campaign_state.get(channel_id)
            if current:
                await send(ctx, f"📖 Campanha atual: **{current}**")
            else:
                await send(ctx, "⚠️ Nenhuma campanha ativa.")
            return

        # ---------------------------------------------------------
        # SWITCH
        # ---------------------------------------------------------
        if action == "switch":

            if not name:
                await send(ctx, "⚠️ Use: !campaign switch <nome>")
                return

            container.campaign_state.set(channel_id, name)

            logger.info(
                "Campaign switched channel=%s campaign=%s",
                channel_id,
                name,
            )

            await send(ctx, f"🔄 Campanha ativa: **{name}**")
            return

        # ---------------------------------------------------------
        # SHOW
        # ---------------------------------------------------------
        if action == "show":

            current = container.campaign_state.get(channel_id)

            if not current:
                await send(ctx, "⚠️ Nenhuma campanha ativa.")
                return

            await send(ctx, f"📖 Campanha atual: **{current}**")
            return

        # ---------------------------------------------------------
        # INVALID
        # ---------------------------------------------------------
        await send(ctx, "⚠️ Use: !campaign switch <nome> | !campaign show")
