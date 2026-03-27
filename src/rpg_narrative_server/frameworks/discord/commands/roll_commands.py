import logging
from discord.ext import commands

from rpg_narrative_server.frameworks.discord.processing import start_processing
from rpg_narrative_server.frameworks.discord.responder import send
from rpg_narrative_server.frameworks.discord.utils import send_long_response

logger = logging.getLogger("rpg_narrative_server.discord")


def register_roll_command(bot, usecases, executor):

    @bot.hybrid_command(name="roll", description="Rolagem de dados")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def roll(ctx: commands.Context, *, expression: str):

        expression = (expression or "").strip()

        if not expression:
            await send(ctx, "⚠️ Informe uma expressão.")
            return

        # 🔥 feedback imediato
        await start_processing(ctx)

        async def handler():

            try:
                result = await usecases.roll_dice.execute(
                    expression=expression
                )
            except Exception:
                logger.exception("Roll usecase failed")
                raise

            if not result:
                await send(ctx, "⚠️ Sem resultado.")
                return

            await send_long_response(ctx, str(result))

        await executor.run(ctx, handler)