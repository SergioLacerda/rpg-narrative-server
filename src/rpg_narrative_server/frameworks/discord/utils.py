import logging
from discord.ext import commands

from rpg_narrative_server.frameworks.discord.responder import send


MAX_MESSAGE_LEN = 1900
MAX_ACTION_LEN = 500


logger = logging.getLogger("rpg_narrative_server.discord")


def get_campaign_id(ctx: commands.Context) -> str:
    guild = getattr(ctx, "guild", None)
    if guild and getattr(guild, "id", None):
        return str(guild.id)

    author = getattr(ctx, "author", None)
    if author and getattr(author, "id", None):
        return f"dm_{author.id}"

    logger.warning("Fallback campaign_id used (ctx=%s)", ctx)

    return "unknown_campaign"


def get_user_id(ctx: commands.Context) -> str:
    """Retorna ID do usuário."""
    return str(ctx.author.id)


async def send_long_response(
    ctx: commands.Context,
    content: str,
    header: str = "",
) -> None:
    """
    Envia resposta longa com chunking seguro.
    - Short + header: envia tudo em uma única mensagem
    - Long: envia header primeiro + chunks do conteúdo
    """
    if not content:
        await send(ctx, "Sem conteúdo para enviar.")
        return

    if header:
        combined = header + content
        if len(combined) <= MAX_MESSAGE_LEN:
            await send(ctx, combined)

            return
        # long → header separado
        await send(ctx, header)

        content_to_send = content
    else:
        if len(content) <= MAX_MESSAGE_LEN:
            await send(ctx, content)

            return
        content_to_send = content

    for i in range(0, len(content_to_send), MAX_MESSAGE_LEN):
        await send(ctx, content_to_send[i : i + MAX_MESSAGE_LEN])
