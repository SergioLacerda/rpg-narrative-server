import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

logger = logging.getLogger("rpg_narrative_server.discord")


class CommandExecutor:
    """
    Executa handlers com:
    - tratamento de erro
    - timeout opcional
    """

    def __init__(self, settings=None, debug: bool = False):
        self.settings = settings
        self.debug = debug

        self.timeout = getattr(settings, "command_timeout", None) if settings else None

    async def run(
        self,
        ctx: Any,
        handler: Callable[[], Awaitable[Any]],
    ) -> Any:
        try:
            # ---------------------------------------
            # EXECUTION
            # ---------------------------------------
            if self.timeout:
                return await asyncio.wait_for(handler(), timeout=self.timeout)

            return await handler()

        except TimeoutError:
            logger.warning(
                "⏳ [EXECUTOR] timeout user=%s channel=%s",
                getattr(ctx.author, "id", "unknown"),
                getattr(ctx.channel, "id", "unknown"),
            )

            await self._safe_send(ctx, "⏳ Tempo limite excedido.")

        except Exception as e:
            logger.exception(
                "🔥 [EXECUTOR] failure user=%s channel=%s error=%s",
                getattr(ctx.author, "id", "unknown"),
                getattr(ctx.channel, "id", "unknown"),
                str(e),
            )

            if self.debug:
                await self._safe_send(ctx, f"⚠️ Erro: {str(e)}")
                raise
            else:
                await self._safe_send(ctx, "⚠️ Algo deu errado.")

    # ---------------------------------------------------------
    # SAFE SEND
    # ---------------------------------------------------------

    async def _safe_send(self, ctx: Any, message: str):
        try:
            await ctx.send(message)
        except Exception:
            logger.exception("Failed to send fallback message")
