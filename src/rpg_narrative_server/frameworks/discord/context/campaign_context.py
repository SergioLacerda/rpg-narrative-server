from rpg_narrative_server.bootstrap.container import get_container
from rpg_narrative_server.frameworks.discord.utils import get_campaign_id


def resolve_campaign_id(ctx) -> str:
    """
    Resolve campanha ativa com fallback seguro.
    """

    container = get_container()
    channel_id = str(ctx.channel.id)

    # campanha selecionada via !campaign switch
    campaign = container.campaign_state.get(channel_id)

    if campaign:
        return campaign

    # fallback (comportamento antigo)
    return get_campaign_id(ctx)