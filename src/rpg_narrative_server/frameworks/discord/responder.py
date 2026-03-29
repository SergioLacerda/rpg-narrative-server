import logging

from rpg_narrative_server.application.contracts.response import Response

logger = logging.getLogger("rpg_narrative_server.discord")


class DiscordResponder:
    def __init__(self, ctx):
        self.ctx = ctx

    async def send(self, content):

        if isinstance(content, Response):
            content = content.text

        interaction = getattr(self.ctx, "interaction", None)

        if interaction:
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(content)
                else:
                    await interaction.followup.send(content)
                return
            except Exception:
                try:
                    await interaction.followup.send(content)
                    return
                except Exception:
                    logger.exception("Responder failed")

        try:
            await self.ctx.send(content)
        except Exception:
            logger.exception("Responder failed")
