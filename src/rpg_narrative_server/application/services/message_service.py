import logging

from rpg_narrative_server.application.contracts.response import Response

logger = logging.getLogger("rpg_narrative_server.discord")


class MessageService:
    def __init__(
        self,
        usecases,
        executor,
        campaign_state,
        runtime,
        intent_classifier,
        settings,
    ):
        self.usecases = usecases
        self.executor = executor
        self.campaign_state = campaign_state
        self.runtime = runtime
        self.intent = intent_classifier
        self.settings = settings

    # ---------------------------------------------------------
    # ENTRYPOINT
    # ---------------------------------------------------------
    async def handle(self, message, ctx, responder):
        # ----------------------------------
        # IGNORA BOT
        # ----------------------------------
        if message.author.bot:
            return

        content = (message.content or "").strip()

        # ----------------------------------
        # IGNORA VAZIO
        # ----------------------------------
        if not content:
            return

        channel_id = ctx.channel.id
        user_id = ctx.author.id

        # ----------------------------------
        # COOLDOWN (INFRA)
        # ----------------------------------
        if not self.runtime.check_cooldown(user_id, 3):
            logger.debug("Cooldown active, skipping message")
            return

        # ----------------------------------
        # LOCK (INFRA)
        # ----------------------------------
        lock = self.runtime.get_lock(channel_id)

        if lock.locked():
            return

        # ----------------------------------
        # INTENT (INFRA / AI)
        # ----------------------------------
        try:
            intent = await self.intent.classify(content)
        except Exception:
            logger.exception("Intent classification failed")
            intent = "ACTION"

        # ----------------------------------
        # FILTRO (INTENT)
        # ----------------------------------
        if intent == "OOC":
            return

        # ----------------------------------
        # CAMPANHA (REGRA DE NEGÓCIO)
        # ----------------------------------
        campaign_id = self.campaign_state.get(channel_id)

        if not campaign_id:
            if self.runtime.should_warn(channel_id, 30):
                await responder.send("🎲 Nenhuma campanha ativa.\nUse `/campaign switch <nome>`")
            return

        # ----------------------------------
        # EXECUÇÃO
        # ----------------------------------
        async with lock:
            await self.executor.run(
                ctx,
                lambda: self._execute_and_send(
                    responder,
                    campaign_id,
                    content,
                    user_id,
                    intent,
                ),
            )

    # ---------------------------------------------------------
    # EXECUÇÃO
    # ---------------------------------------------------------
    async def _execute_and_send(
        self,
        responder,
        campaign_id,
        content,
        user_id,
        intent,
    ):
        try:
            response = await self.usecases.narrative.execute(
                campaign_id=campaign_id,
                action=content,
                user_id=user_id,
            )
        except Exception:
            logger.exception("Narrative execution failed")
            raise

        if not response:
            return

        response = self._adapt_response_by_intent(response, intent)

        await self._send_response(responder, response)

    # ---------------------------------------------------------
    # ADAPTAÇÃO
    # ---------------------------------------------------------
    def _adapt_response_by_intent(self, response, intent):
        if isinstance(response, Response):
            return response

        return Response(
            text=response,
            type=intent.lower(),
        )

    # ---------------------------------------------------------
    # OUTPUT
    # ---------------------------------------------------------
    async def _send_response(self, responder, response):
        MAX = 1900

        # ----------------------------------
        # NORMALIZAÇÃO
        # ----------------------------------
        if isinstance(response, Response):
            content = response.text
        else:
            content = response

        if not content:
            return

        # ----------------------------------
        # ENVIO
        # ----------------------------------
        if len(content) <= MAX:
            await responder.send(content)
            return

        for i in range(0, len(content), MAX):
            await responder.send(content[i : i + MAX])
