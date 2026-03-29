from discord.ext.commands import Context

from rpg_narrative_server.application.commands.roll_command import (
    build_roll_command,
)
from rpg_narrative_server.frameworks.discord.command_adapter import (
    BaseDiscordCommandAdapter,
)


def register_roll_command(bot, deps, executor, registry):
    command = build_roll_command(deps)
    adapter = BaseDiscordCommandAdapter(command, executor)

    @bot.hybrid_command(name="roll", description="Rola dados")
    async def roll(ctx: Context, *, expression: str):
        await adapter.run(ctx, expression=expression)

    registry.register(command.name, command)

    return roll
