import logging
import time
import uuid
from typing import Any

from rpg_narrative_server.frameworks.discord.responder import DiscordResponder

logger = logging.getLogger("rpg_narrative_server.discord")


class BaseDiscordCommandAdapter:
    """
    Adapter padrão para comandos Discord.

    Responsabilidades:
    - executar command (application layer)
    - aplicar tracing (tempo + correlation_id)
    - padronizar logs
    - delegar erro/timeout ao executor
    - enviar resposta via DiscordResponder
    """

    def __init__(self, command, executor):
        self.command = command
        self.executor = executor

    async def run(self, ctx: Any, **kwargs):
        correlation_id = str(uuid.uuid4())[:8]

        async def handler():
            start = time.perf_counter()

            user_id = getattr(ctx.author, "id", "unknown")
            channel_id = getattr(ctx.channel, "id", "unknown")

            logger.debug(
                "➡️ [COMMAND] start name=%s cid=%s user=%s channel=%s kwargs=%s",
                self.command.name,
                correlation_id,
                user_id,
                channel_id,
                kwargs,
            )

            try:
                result = await self.command.execute(ctx, **kwargs)

                duration = time.perf_counter() - start

                logger.debug(
                    "⬅️ [COMMAND] success name=%s cid=%s duration=%.4fs",
                    self.command.name,
                    correlation_id,
                    duration,
                )

                # 🔥 PROTEÇÃO CENTRAL
                if not result:
                    result = "⚠️ Nenhuma resposta gerada."

                await DiscordResponder(ctx).send(result)

                return result

            except Exception as e:
                duration = time.perf_counter() - start

                logger.exception(
                    "🔥 [COMMAND] error name=%s cid=%s duration=%.4fs error=%s",
                    self.command.name,
                    correlation_id,
                    duration,
                    str(e),
                )

                raise

        return await self.executor.run(ctx, handler)
