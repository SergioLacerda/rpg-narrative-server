async def send(ctx, content: str):

    interaction = getattr(ctx, "interaction", None)

    # slash command
    if interaction:
        if not interaction.response.is_done():
            await interaction.response.send_message(content)
        else:
            await interaction.followup.send(content)

    # prefix command
    else:
        await ctx.send(content)
