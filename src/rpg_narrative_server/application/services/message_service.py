import logging

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

    async def handle(self, message, ctx):

        # ----------------------------------
        # IGNORAR BOT
        # ----------------------------------
        if message.author.bot:
            return

        content = (message.content or "").strip()
        if not content:
            return

        channel_id = ctx.channel_id
        user_id = ctx.user_id

        # ----------------------------------
        # CAMPANHA
        # ----------------------------------
        campaign_id = self.campaign_state.get(channel_id)

        if not campaign_id:
            if self.runtime.should_warn(channel_id, 30):
                await ctx.send(
                    "🎲 Nenhuma campanha ativa.\n" "Use `/campaign switch <nome>`"
                )
            return

        # ----------------------------------
        # COOLDOWN
        # ----------------------------------
        if not self.runtime.check_cooldown(user_id, 3):
            logger.debug("Cooldown active, skipping message")
            return

        # ----------------------------------
        # INTENT (SOFT DECISION)
        # ----------------------------------
        try:
            intent = await self.intent.classify(content)
        except Exception:
            logger.exception("Intent classification failed")
            intent = "ACTION"  # fallback seguro

        logger.debug(
            "[INTENT] campaign=%s user=%s intent=%s text='%s'",
            campaign_id,
            user_id,
            intent,
            content,
        )

        # ----------------------------------
        # FILTRO LEVE
        # ----------------------------------
        if intent == "OOC":
            logger.debug("Ignoring OOC message")
            return

        # ----------------------------------
        # LOCK (ANTI OVERLAP)
        # ----------------------------------
        lock = self.runtime.get_lock(channel_id)

        if lock.locked():
            logger.debug("Channel busy, skipping message")
            return

        logger.debug(
            "RP AUTO: campaign=%s user=%s action=%s",
            campaign_id,
            user_id,
            content,
        )

        # ----------------------------------
        # EXECUÇÃO
        # ----------------------------------
        async with lock:
            await self.executor.run(
                ctx,
                lambda: self._execute_and_send(
                    ctx,
                    campaign_id,
                    content,
                    user_id,
                    intent,  # 🔥 agora passamos intent
                ),
            )

    # ---------------------------------------------------------
    # execução principal
    # ---------------------------------------------------------

    async def _execute_and_send(
        self,
        ctx,
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
            logger.debug("Empty narrative response")
            return

        # ----------------------------------
        # (OPCIONAL FUTURO) adaptar resposta
        # ----------------------------------
        response = self._adapt_response_by_intent(response, intent)

        await self._send_response(ctx, response)

    # ---------------------------------------------------------
    # adaptação por intent (extensível)
    # ---------------------------------------------------------

    def _adapt_response_by_intent(self, response: str, intent: str) -> str:

        if not response:
            return response

        # 🔥 hooks simples (expansível depois)

        if intent == "CHAT":
            # resposta mais leve (futuro)
            return response

        if intent == "EXPLORATION":
            return response

        if intent == "ACTION":
            return response

        return response

    # ---------------------------------------------------------
    # output
    # ---------------------------------------------------------

    async def _send_response(self, ctx, response: str):

        if len(response) <= 1900:
            await ctx.send(response)
            return

        for i in range(0, len(response), 1900):
            await ctx.send(response[i : i + 1900])
