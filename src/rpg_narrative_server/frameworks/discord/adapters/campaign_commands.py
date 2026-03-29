from discord.ext import commands

from rpg_narrative_server.application.commands.campaign_command import (
    build_campaign_command,
)
from rpg_narrative_server.frameworks.discord.command_adapter import (
    BaseDiscordCommandAdapter,
)


def register_campaign_commands(bot, deps, executor, registry):
    command = build_campaign_command(deps)
    adapter = BaseDiscordCommandAdapter(command, executor)

    @bot.hybrid_command(name="campaign", description="Gerenciar campanha")
    async def campaign(
        ctx: commands.Context,
        action: str | None = None,
        name: str | None = None,
    ):
        await adapter.run(ctx, action=action, name=name)

    registry.register(command.name, command)

    return campaign
