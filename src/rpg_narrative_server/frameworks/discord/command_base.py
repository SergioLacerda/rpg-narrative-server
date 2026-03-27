import asyncio
import logging

from rpg_narrative_server.frameworks.discord.responder import send

logger = logging.getLogger("rpg_narrative_server.discord")


class CommandExecutor:

    def __init__(self, settings, debug: bool = False):
        self.settings = settings
        self.debug = debug

    async def run(self, ctx, fn):

        logger.info("[EXECUTOR] START")

        try:
            logger.info(f"⏱️ [EXECUTOR] timeout={self.settings.runtime.execution_timeout}")

            result = await self._run_with_trace(fn)

            logger.info("[EXECUTOR] COMPLETED")

            return result

        except asyncio.TimeoutError:
            logger.error("🔥 [EXECUTOR] TIMEOUT ❌")

            await send(ctx, "⏳ O modelo demorou muito para responder.")

        except asyncio.CancelledError:
            logger.error("🔥 [EXECUTOR] CANCELLED ❌")

            raise

        except Exception as e:
            logger.exception("Command execution failed")

            if self.debug:
                await send(ctx, f"Error: {str(e)}")
            else:
                await send(ctx, "⚠️ Algo deu errado")

    async def _run_with_trace(self, fn):

        logger.debug("➡️ [EXECUTOR] entering handler")

        try:
            result = await fn()
            logger.debug("⬅️ [EXECUTOR] handler finished")
            return result

        except asyncio.CancelledError:
            logger.debug("🔥 [EXECUTOR] handler CANCELLED")
            raise

        except Exception as e:
            logger.debug("🔥 [EXECUTOR] handler EXCEPTION")
            logger.debug(f"🔥 ERROR TYPE: {type(e)}")
            raise