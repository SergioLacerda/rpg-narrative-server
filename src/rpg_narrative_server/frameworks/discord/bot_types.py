from discord.ext import commands

from rpg_narrative_server.application.commands.command_bus import CommandBus
from rpg_narrative_server.application.commands.command_registry import CommandRegistry


class RPGDiscordBot(commands.Bot):
    debug: bool

    command_bus: CommandBus
    command_registry: CommandRegistry

    gm_command: object
    roll_command: object
    session_command: object
    campaign_command: object
