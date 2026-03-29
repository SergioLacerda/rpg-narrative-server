import logging

import discord
from discord.ext import commands

from rpg_narrative_server.application.commands.command_bus import CommandBus
from rpg_narrative_server.application.commands.command_registry import CommandRegistry
from rpg_narrative_server.application.services.message_service import MessageService
from rpg_narrative_server.frameworks.discord.adapters.campaign_commands import (
    register_campaign_commands,
)
from rpg_narrative_server.frameworks.discord.adapters.gm_commands import register_gm_command
from rpg_narrative_server.frameworks.discord.adapters.roll_commands import register_roll_command
from rpg_narrative_server.frameworks.discord.adapters.session_commands import (
    register_session_commands,
)
from rpg_narrative_server.frameworks.discord.context.message_context import MessageContext
from rpg_narrative_server.frameworks.discord.executor import CommandExecutor
from rpg_narrative_server.frameworks.discord.responder import DiscordResponder
from rpg_narrative_server.infrastructure.runtime.message_runtime import MessageRuntime

logger = logging.getLogger("rpg_narrative_server.discord")


def create_bot(settings, deps, register_commands: bool = True):
    # -------------------------------------------------
    # DISCORD SETUP
    # -------------------------------------------------
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)
    bot.debug = settings.runtime.environment != "prod"

    # -------------------------------------------------
    # CORE (Application wiring)
    # -------------------------------------------------
    registry = CommandRegistry()

    executor = CommandExecutor(
        settings=settings,
        debug=bot.debug,
    )

    # 🔥 CommandBus disponível para outros adapters (CLI/API/testes)
    command_bus = CommandBus(registry, executor)

    # -------------------------------------------------
    # SERVICES
    # -------------------------------------------------
    message_service = MessageService(
        usecases=deps,
        executor=executor,
        campaign_state=deps.campaign_state,
        runtime=MessageRuntime(),
        intent_classifier=deps.intent_classifier,
        settings=settings,
    )

    # -------------------------------------------------
    # EVENTS
    # -------------------------------------------------
    @bot.event
    async def on_ready():
        logger.info(
            "Bot ready user=%s env=%s",
            bot.user,
            settings.runtime.environment,
        )

        try:
            await bot.tree.sync()
            logger.info("Slash commands synced")
        except Exception:
            logger.exception("Failed to sync commands")

    @bot.event
    async def on_command_error(ctx, error):
        responder = DiscordResponder(ctx)

        if isinstance(error, commands.CommandOnCooldown):
            await responder.send("⏳ Aguarde antes de usar novamente.")
            return

        logger.exception("Command error: %s", error)
        await responder.send("⚠️ Erro ao executar comando.")

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        ctx = MessageContext(message)
        responder = DiscordResponder(ctx)

        # 🔥 pipeline narrativa (RAG + memória)
        await message_service.handle(message, ctx, responder)

        # permite comandos !gm, !roll etc
        await bot.process_commands(message)

    # -------------------------------------------------
    # COMMAND REGISTRATION (Discord Adapter)
    # -------------------------------------------------
    if register_commands:
        bot.gm_command = register_gm_command(bot, deps, executor, registry)
        bot.roll_command = register_roll_command(bot, deps, executor, registry)
        bot.session_command = register_session_commands(bot, deps, executor, registry)
        bot.campaign_command = register_campaign_commands(bot, deps, executor, registry)

    # -------------------------------------------------
    # OPTIONAL EXPOSURES (não obrigatórios)
    # -------------------------------------------------
    # 🔥 úteis para CLI / testes avançados / debug manual
    bot.command_bus = command_bus
    bot.command_registry = registry

    return bot
