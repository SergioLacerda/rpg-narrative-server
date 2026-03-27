from contextlib import asynccontextmanager
import asyncio
import logging
import os

from fastapi import FastAPI

from rpg_narrative_server.bootstrap.container import get_container
from rpg_narrative_server.frameworks.discord.bot import create_bot
from rpg_narrative_server.frameworks.discord.dependencies import BotDependencies
from rpg_narrative_server.config.paths import ensure_directories

logger = logging.getLogger("rpg_narrative_server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting RPG Narrative Server")

    # ----------------------------------------
    # filesystem
    # ----------------------------------------
    ensure_directories()
    logger.info("📁 Directories ensured")

    # ----------------------------------------
    # vector index (warmup opcional)
    # ----------------------------------------
    await get_container().vector_memory.start()

    warmup_enabled = os.getenv("WARMUP_VECTOR_INDEX", "true").lower() == "true"

    if warmup_enabled:
        try:
            logger.info("🔥 Vector index warmup enabled")

            vector_index = get_container().vector_index

            if hasattr(vector_index, "load"):
                maybe = vector_index.load()
                if asyncio.iscoroutine(maybe):
                    await maybe

            if hasattr(vector_index, "ensure_ann_ready"):
                maybe = vector_index.ensure_ann_ready()
                if asyncio.iscoroutine(maybe):
                    await maybe

            logger.info("✅ Vector index ready")

        except Exception:
            logger.exception("❌ Vector index warmup failed")

    else:
        logger.info("❄️ Vector index lazy mode (no warmup)")

    # ----------------------------------------
    # discord bot (opcional)
    # ----------------------------------------
    discord_enabled = os.getenv("ENABLE_DISCORD", "true").lower() == "true"

    discord_task = None
    bot = None

    if discord_enabled:
        try:
            logger.info("🤖 Starting Discord bot")

            bot = create_bot(
                settings=get_container().settings,
                usecases=BotDependencies(
                    roll_dice=get_container().roll_dice,
                    narrative=get_container().narrative,
                    end_session=get_container().end_session,
                ),
            )

            async def run():
                await bot.start(get_container().settings.app.discord_token)

            discord_task = asyncio.create_task(run())

            app.state.discord_bot = bot
            app.state.discord_task = discord_task

            logger.info("✅ Discord bot started")

        except Exception:
            logger.exception("❌ Failed to start Discord bot")

    else:
        logger.info("🚫 Discord disabled via ENV")

    # ----------------------------------------
    # RUNNING
    # ----------------------------------------
    yield

    # ----------------------------------------
    # shutdown
    # ----------------------------------------
    logger.info("🛑 Shutting down...")

    if discord_task:
        discord_task.cancel()

        try:
            await discord_task
        except asyncio.CancelledError:
            logger.info("Discord task cancelled")

    if bot:
        try:
            await bot.close()
            logger.info("Discord bot closed")
        except Exception:
            logger.exception("Error closing Discord bot")
