from rpg_narrative_server.frameworks.discord.utils.ids import get_campaign_id


def resolve_campaign_id(ctx, campaign_state) -> str:
    channel_id = str(ctx.channel.id)

    campaign = campaign_state.get(channel_id)

    if campaign:
        return campaign

    return get_campaign_id(ctx)
