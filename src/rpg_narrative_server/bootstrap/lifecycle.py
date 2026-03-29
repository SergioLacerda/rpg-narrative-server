import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from rpg_narrative_server.bootstrap.container import Container
from rpg_narrative_server.config.paths import ensure_directories
from rpg_narrative_server.frameworks.discord.bot import create_bot
from rpg_narrative_server.frameworks.discord.dependencies import CommandDependencies

logger = logging.getLogger("rpg_narrative_server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting RPG Narrative Server")

    # --------------------------------------------------
    # container (🔥 correto)
    # --------------------------------------------------
    container = Container()
    app.state.container = container

    # --------------------------------------------------
    # filesystem
    # --------------------------------------------------
    ensure_directories()

    # --------------------------------------------------
    # vector memory start
    # --------------------------------------------------
    await container.vector_memory.start()

    # --------------------------------------------------
    # warmup opcional (mantido)
    # --------------------------------------------------
    warmup_enabled = os.getenv("WARMUP_VECTOR_INDEX", "true").lower() == "true"

    if warmup_enabled:
        try:
            logger.info("🔥 Vector index warmup")

            vi = container.vector_index

            if hasattr(vi, "load"):
                maybe = vi.load()
                if asyncio.iscoroutine(maybe):
                    await maybe

            if hasattr(vi, "ensure_ann_ready"):
                maybe = vi.ensure_ann_ready()
                if asyncio.iscoroutine(maybe):
                    await maybe

        except Exception:
            logger.exception("❌ Warmup failed")

    # --------------------------------------------------
    # discord (mantido)
    # --------------------------------------------------
    discord_enabled = os.getenv("ENABLE_DISCORD", "true").lower() == "true"

    bot = None
    task = None

    token = container.settings.app.discord_token

    if discord_enabled and token:
        try:
            logger.info("🤖 Starting Discord bot")

            bot = create_bot(
                settings=container.settings,
                deps=CommandDependencies(
                    roll_dice=container.roll_dice,
                    narrative=container.narrative,
                    end_session=container.end_session,
                    campaign_state=container.campaign_state,
                    intent_classifier=container.intent_classifier,
                ),
            )

            async def run():
                await bot.start(token)

            task = asyncio.create_task(run())

            app.state.discord_bot = bot
            app.state.discord_task = task

        except Exception:
            logger.exception("❌ Discord failed to start")

    # --------------------------------------------------
    # RUNNING
    # --------------------------------------------------
    yield

    # --------------------------------------------------
    # shutdown
    # --------------------------------------------------
    logger.info("🛑 Shutting down")

    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    if bot:
        try:
            await bot.close()
        except Exception:
            logger.exception("Error closing bot")
