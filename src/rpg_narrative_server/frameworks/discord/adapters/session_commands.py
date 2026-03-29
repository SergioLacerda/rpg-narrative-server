from discord.ext import commands

from rpg_narrative_server.application.commands.session_command import (
    build_session_command,
)
from rpg_narrative_server.frameworks.discord.command_adapter import (
    BaseDiscordCommandAdapter,
)


def register_session_commands(bot, deps, executor, registry):
    command = build_session_command(deps)
    adapter = BaseDiscordCommandAdapter(command, executor)

    @bot.hybrid_command(name="endsession", description="Finaliza sessão")
    async def endsession(ctx: commands.Context):
        await adapter.run(ctx)

    registry.register(command.name, command)

    return endsession
