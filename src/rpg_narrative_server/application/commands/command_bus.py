import logging
from typing import Any

logger = logging.getLogger("rpg_narrative_server.discord")


class CommandBus:

    def __init__(self, registry, executor):
        self.registry = registry
        self.executor = executor

    async def dispatch(self, ctx: Any, command_name: str | None = None, **kwargs):
        """
        Executa um comando.

        Regras:
        - se command_name não for informado:
            → usa o único comando registrado (modo teste)
        """

        command = self._resolve_command(command_name)

        async def handler():
            logger.debug(
                "➡️ [BUS] dispatch command=%s kwargs=%s",
                command.name,
                kwargs,
            )

            result = await command.execute(ctx, **kwargs)

            if not result:
                result = "⚠️ Nenhuma resposta gerada."

            if hasattr(ctx, "send"):
                await ctx.send(result)

            return result

        return await self.executor.run(ctx, handler)

    # ---------------------------------------------------------
    # INTERNAL
    # ---------------------------------------------------------

    def _resolve_command(self, command_name: str | None):
        if command_name:
            command = self.registry.get(command_name)

            if not command:
                raise ValueError(f"Command '{command_name}' não encontrado")

            return command

        commands = list(self.registry.all().values())

        if not commands:
            raise ValueError("Nenhum comando registrado")

        if len(commands) > 1:
            raise ValueError("Múltiplos comandos registrados — informe command_name")

        return commands[0]
