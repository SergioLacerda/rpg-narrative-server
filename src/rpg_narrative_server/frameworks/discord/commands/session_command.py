import logging
from discord.ext import commands

from rpg_narrative_server.frameworks.discord.processing import start_processing
from rpg_narrative_server.frameworks.discord.responder import send

from rpg_narrative_server.frameworks.discord.utils import (
    get_campaign_id,
    send_long_response,
)


logger = logging.getLogger("rpg_narrative_server.discord")


def register_session_commands(bot, usecases, executor):

    @bot.hybrid_command(name="endsession", description="Finaliza sessão")
    async def endsession(ctx: commands.Context):

        campaign_id = get_campaign_id(ctx)

        if not hasattr(usecases, "end_session") or usecases.end_session is None:
            await send(ctx, "⚠️ Encerramento indisponível.")
            return

        logger.info("EndSession command campaign=%s", campaign_id)

        # 🔥 feedback imediato
        await start_processing(ctx)

        async def handler():

            try:
                summary = await usecases.end_session.execute(campaign_id)
            except Exception:
                logger.exception("EndSession usecase failed")
                raise

            if not summary:
                await send(ctx, "⚠️ Nada para resumir.")
                return

            await send_long_response(ctx, summary)

        await executor.run(ctx, handler)
