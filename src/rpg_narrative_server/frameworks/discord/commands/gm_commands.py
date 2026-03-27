import logging
from discord.ext import commands
from discord import app_commands

from rpg_narrative_server.frameworks.discord.processing import start_processing
from rpg_narrative_server.frameworks.discord.responder import send
from rpg_narrative_server.frameworks.discord.utils import (
    get_user_id,
    send_long_response,
)

from rpg_narrative_server.frameworks.discord.context.campaign_context import (
    resolve_campaign_id,
)


logger = logging.getLogger("rpg_narrative_server.discord")


def register_gm_command(bot, usecases, executor):
    @bot.hybrid_command(name="gm", description="Ação narrativa")
    @app_commands.describe(action="Descreva sua ação")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def gm(ctx, *, action: str):
        action = (action or "").strip()

        if not action:
            await send(ctx, "⚠️ Você precisa descrever uma ação.")
            return

        campaign_id = resolve_campaign_id(ctx)
        user_id = get_user_id(ctx)

        logger.debug("GM command: begin")

        await start_processing(ctx)

        async def handler():
            response = await usecases.narrative.execute(
                campaign_id=campaign_id,
                action=action,
                user_id=user_id,
            )

            if not response:
                await send(ctx, "⚠️ O mestre ficou em silêncio...")
                return

            await send_long_response(ctx, response)

        await executor.run(ctx, handler)
