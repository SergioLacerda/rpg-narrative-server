async def start_processing(ctx):
    interaction = getattr(ctx, "interaction", None)

    if interaction:
        # só defere se ainda não respondeu
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=True)
    else:
        if hasattr(ctx, "channel"):
            await ctx.channel.typing()
