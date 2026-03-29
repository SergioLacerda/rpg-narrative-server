from discord.ext import commands

from rpg_narrative_server.application.commands.gm_command import (
    build_gm_command,
)
from rpg_narrative_server.frameworks.discord.command_adapter import (
    BaseDiscordCommandAdapter,
)


def register_gm_command(bot, deps, executor, registry):
    command = build_gm_command(deps)
    adapter = BaseDiscordCommandAdapter(command, executor)

    @bot.hybrid_command(name="gm", description="Executa ação narrativa")
    async def gm(ctx: commands.Context, *, action: str):
        await adapter.run(ctx, action=action)

    registry.register(command.name, command)

    return gm
