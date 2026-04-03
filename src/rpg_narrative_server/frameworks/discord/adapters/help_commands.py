from discord.ext.commands import Context


def register_help_commands(bot):
    @bot.hybrid_command(name="commands", description="Lista comandos disponíveis")
    async def commands(ctx: Context):
        message = (
            "📚 **Comandos disponíveis:**\n\n"
            "🎲 **Campanha**\n"
            "!campaign start <nome>\n"
            "!campaign switch <nome>\n"
            "!campaign list\n"
            "!campaign delete <nome>\n"
            "!campaign stop\n\n"
            "🎭 **Narrativa**\n"
            "!gm <ação>\n\n"
            "🎲 **Dados**\n"
            "!roll <expressão>\n\n"
            "🛑 **Sessão**\n"
            "!endsession\n"
        )

        await ctx.send(message)

    return commands
