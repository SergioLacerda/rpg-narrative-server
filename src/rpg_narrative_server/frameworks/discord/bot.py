import logging
import discord
from discord.ext import commands

from rpg_narrative_server.bootstrap.container import get_container

from rpg_narrative_server.frameworks.discord.command_base import CommandExecutor
from rpg_narrative_server.frameworks.discord.context.message_context import (
    MessageContext,
)

from rpg_narrative_server.frameworks.discord.commands.gm_commands import (
    register_gm_command,
)
from rpg_narrative_server.frameworks.discord.commands.roll_commands import (
    register_roll_command,
)
from rpg_narrative_server.frameworks.discord.commands.session_command import (
    register_session_commands,
)
from rpg_narrative_server.frameworks.discord.commands.campaign_commands import (
    register_campaign_commands,
)

from rpg_narrative_server.frameworks.discord.responder import send

# 🆕 application
from rpg_narrative_server.application.services.message_service import MessageService

# 🆕 runtime
from rpg_narrative_server.infrastructure.runtime.message_runtime import MessageRuntime


logger = logging.getLogger("rpg_narrative_server.discord")


def create_bot(*, settings, usecases, container=None):
    container = container or get_container()
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    bot.debug = settings.runtime.environment != "prod"

    executor = CommandExecutor(settings=settings, debug=bot.debug)

    # -------------------------------------------------
    # 🔥 BOOTSTRAP (fora de eventos)
    # -------------------------------------------------

    message_service = MessageService(
        usecases=usecases,
        executor=executor,
        campaign_state=container.campaign_state,
        runtime=MessageRuntime(),
        intent_classifier=container.intent_classifier,
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

        if settings.runtime.environment in ("local", "dev"):
            try:
                synced = await bot.tree.sync()
                logger.info("Synced %s commands", len(synced))
            except Exception:
                logger.exception("Sync failed")

    @bot.event
    async def on_disconnect():
        logger.warning("Bot disconnected")

    @bot.event
    async def on_resumed():
        logger.info("Bot resumed connection")

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await send(ctx, f"⏳ Aguarde {error.retry_after:.1f}s.")
            return

        logger.exception("Command error: %s", error)

        try:
            await send(ctx, "⚠️ Erro ao executar comando.")
        except Exception:
            pass

    # -------------------------------------------------
    # 🔥 RP AUTOMÁTICO (core)
    # -------------------------------------------------
    @bot.event
    async def on_message(message):
        # ignora bots
        if message.author.bot:
            return

        # comandos prefixados
        if message.content.startswith("!"):
            await bot.process_commands(message)
            return

        # adapter → executor compatível
        ctx = MessageContext(message)

        # fluxo principal
        await message_service.handle(message, ctx)

        # garante compatibilidade com outros handlers futuros
        await bot.process_commands(message)

    # -------------------------------------------------
    # COMMANDS
    # -------------------------------------------------
    register_gm_command(bot, usecases, executor)
    register_roll_command(bot, usecases, executor)
    register_session_commands(bot, usecases, executor)
    register_campaign_commands(bot)

    return bot
